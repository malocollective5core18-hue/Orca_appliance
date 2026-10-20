# Django application boundary

Phase 1 creates only `accounts`. Add domain apps only in their separately approved phase. Keep
cross-app writes in services and query composition in selectors; do not add placeholder apps that
look implemented when they are not.
