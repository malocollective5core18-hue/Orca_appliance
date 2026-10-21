"""Staff-upload image validation and privacy-safe WebP variant generation."""

import hashlib
import io
import warnings
from dataclasses import dataclass

from django.conf import settings
from PIL import Image, ImageOps, UnidentifiedImageError


class ImageAssetValidationError(ValueError):
    pass


@dataclass(frozen=True)
class ProcessedImage:
    original_sha256: str
    original_bytes: int
    original_content_type: str
    original_width: int
    original_height: int
    variants: dict[str, bytes]


FORMAT_TYPES = {"JPEG": "image/jpeg", "PNG": "image/png", "WEBP": "image/webp"}
VARIANT_SIZES = {"thumbnail": 320, "medium": 960, "large": 1920}


def validate_and_process_image(data: bytes) -> ProcessedImage:
    """Inspect actual bytes, reject oversized/unsafe images, strip metadata, emit WebP sizes."""
    max_bytes = settings.IMAGE_MAX_BYTES
    max_dimension = settings.IMAGE_MAX_DIMENSION
    max_pixels = settings.IMAGE_MAX_PIXELS
    if not data or len(data) > max_bytes:
        raise ImageAssetValidationError("Image is empty or exceeds the configured byte limit")
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            source = Image.open(io.BytesIO(data))
            detected_format = source.format
            if detected_format not in FORMAT_TYPES:
                raise ImageAssetValidationError("Only JPEG, PNG, and WebP images are allowed")
            source.verify()
            source = Image.open(io.BytesIO(data))
            source.load()
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError, Image.DecompressionBombWarning) as exc:
        raise ImageAssetValidationError("Image bytes are invalid or unsafe") from exc

    width, height = source.size
    if width < 1 or height < 1 or width > max_dimension or height > max_dimension or width * height > max_pixels:
        raise ImageAssetValidationError("Image dimensions exceed the configured limit")
    oriented = ImageOps.exif_transpose(source)
    if oriented.mode not in {"RGB", "RGBA"}:
        oriented = oriented.convert("RGBA" if "transparency" in oriented.info else "RGB")

    # Recreating from pixel data omits EXIF, XMP, GPS, comments, and source metadata.
    clean = Image.new(oriented.mode, oriented.size)
    clean.paste(oriented)
    normalized_width, normalized_height = clean.size
    variants = {}
    for name, max_size in VARIANT_SIZES.items():
        image = clean.copy()
        image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
        output = io.BytesIO()
        image.save(output, format="WEBP", quality=86, method=6)
        variants[name] = output.getvalue()
    return ProcessedImage(
        original_sha256=hashlib.sha256(data).hexdigest(),
        original_bytes=len(data),
        original_content_type=FORMAT_TYPES[detected_format],
        original_width=normalized_width,
        original_height=normalized_height,
        variants=variants,
    )
