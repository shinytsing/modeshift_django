# Manual utilities

These scripts are intentionally separate from `qa/` and from the default pytest collection.
They support local diagnostics or data preparation and may require an explicitly configured local
environment. Do not run them against production targets.

- `create_test_qr.py`: creates a local QR fixture under `media/qr_codes/`.
- `generate_qr.py`: opens an external login page to capture a QR image; use only with permission.

Credential-bearing historical diagnostics live in the ignored `scripts/manual/legacy/` directory
and are not part of the repository.
