# Appliance image storage design

**Phase 2:** image metadata, byte validation and safe local/test adapters only. No upload endpoint,
cloud bucket, signed upload, or production storage integration is implemented.

## Storage and visibility decision

Appliance/product images are product marketing content and are recommended to be **public CDN assets
only after staff approval and successful processing**. This is an ADR recommendation, not owner
approval. Keep original/quarantine objects private during validation. Do not publish `UPLOADED`,
`PROCESSING`, or `REJECTED` assets. `READY` assets can receive a public CDN URL in a later phase.
Customer, payment, agreement, and device documents are not product images; keep those private and
serve them with short-lived signed URLs after authorization.

PostgreSQL stores an `ImageAsset` row only: partner/product, storage key, content type, byte size,
width, height, SHA-256, alt text, primary flag, sort order, processing status, uploader, and
timestamps. Never store file bytes or base64 data in Postgres. One non-deleted primary image per
product is enforced by a partial unique constraint. Soft deletion changes status to `DELETED`; a
later cleanup task deletes remote variants after a retention window. Do not make customer flows
depend on Render's ephemeral local disk.

Recommended key layout: `appliances/<product_id>/<image_id>/<variant>.webp`, with variants `thumbnail`
(320 px), `medium` (960 px), and `large` (1920 px). Store UUID-like IDs, not customer-supplied file
names. `ImageAsset.storage_key` is the base/large key; variants share its directory and asset ID.

## Validation implemented

`apps/domain/images.py::validate_and_process_image` accepts JPEG, PNG, and WebP by inspecting actual
file bytes, not file names. It enforces configured byte, dimension, and pixel limits, verifies and
decodes the image with Pillow, applies EXIF orientation, recreates pixels without EXIF/XMP/GPS
metadata, and emits WebP thumbnail/medium/large variants. Current defaults are 10 MiB, 8,000 px per
dimension, and 40 million pixels. Override with `IMAGE_MAX_BYTES`, `IMAGE_MAX_DIMENSION`, and
`IMAGE_MAX_PIXELS`; all must be positive. Pillow is a direct dependency because standard-library
code cannot reliably decode/verify these image formats, strip metadata while preserving pixels, and
generate consistent WebP variants.

Never trust MIME headers, extensions, dimensions reported by the browser, or uploaded names. Treat
Pillow decode errors and decompression-bomb warnings as rejection. Only staff may upload in a future
endpoint; customers and devices never upload.

## Phase 3 upload flow design

Preferred first implementation: authenticated staff server upload to a private quarantine key;
validate and transform in a bounded worker; write variants; transactionally create/update the
`ImageAsset`; set `READY` only after all objects exist; publish only the approved public variant.
This is simpler to secure and test first, but the server handles the upload bytes and needs memory
limits/timeouts.

Alternative: staff obtains a short-lived signed upload URL to a private quarantine prefix. This
reduces app-server bandwidth but requires strict key/content-size constraints, private bucket
policy, untrusted upload completion handling, and a server-side validation/finalize step before
public promotion. Never let a browser choose a final public key or claim an asset is ready.

Use the StorageBackend conformance suite for local and in-memory adapters now. A later S3-compatible
adapter can use django-storages with R2, Supabase Storage, or AWS S3 after provider choice and explicit
approval. No bucket credentials, provider dependency, endpoint, or upload flow is enabled here.

## Tests

The Phase 2 tests create image bytes in memory and assert byte-format detection, size rejection,
three WebP variants, and absence of EXIF from output. They do not access a network or persist files.
