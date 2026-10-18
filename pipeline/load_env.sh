#!/bin/bash
# Export pipeline/env/common.env to the later steps of a GitHub Actions job.
# Unlike njmunicipalities-api there is no per-branch environment: dev and main
# both plan against the one layer, and only main publishes.
set -euo pipefail

grep -hv -e '^[[:space:]]*#' -e '^[[:space:]]*$' \
    pipeline/env/common.env >> "$GITHUB_ENV"
