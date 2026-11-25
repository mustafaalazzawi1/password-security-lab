#!/usr/bin/env bash
set -euo pipefail
# Tested on Linux x86_64. This setup downloads the official core source only.
project_dir="$(cd -- "$(dirname -- "$0")/.." && pwd)"
tool_dir="$project_dir/tools"
mkdir -p "$tool_dir"
source_archive="$tool_dir/john-1.9.0.tar.xz"
curl --fail --location --connect-timeout 15 --max-time 180 \
  https://download.openwall.net/pub/projects/john/1.9.0/john-1.9.0.tar.xz \
  --output "$source_archive"
python3 - "$source_archive" <<'PY'
import hashlib, sys
from pathlib import Path
expected = '0b266adcfef8c11eed690187e71494baea539efbd632fe221181063ba09508df'
assert hashlib.sha256(Path(sys.argv[1]).read_bytes()).hexdigest() == expected, 'Source checksum mismatch'
PY
tar -xJf "$source_archive" -C "$tool_dir"
make -C "$tool_dir/john-1.9.0/src" -j2 linux-x86-64
printf 'John core built. Run the commands in README.md.\n'
