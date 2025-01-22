# Reproduce Rust Licenses Action

This GitHub Action runs the [`generate-licenses.py`](./generate-licenses.py) script to produce an `UPSTREAM-LICENSES.md` file from Cargo dependencies. It:
1. Installs Python and your repo’s Python dependencies.
2. Runs `cargo-license --json`.
3. Passes the JSON to `generate-licenses.py`.
4. Writes `UPSTREAM-LICENSES.md` containing licenses for the crates you depend on.

<details>

<summary>Click to reveal a sample of the generated file...</summary>

```
This file contains licenses from the upstream software we depend on. This file
MUST be included with all distributions of the software.

This file is generated by a script during release.

---

These software packages contain the following license:

- [icu_collections](https://crates.io/crates/icu_collections)
- [zerovec](https://crates.io/crates/zerovec)

UNICODE LICENSE V3

COPYRIGHT AND PERMISSION NOTICE

Copyright © 1991-2024 Unicode, Inc.

NOTICE TO USER: Carefully read the following legal agreement. BY
DOWNLOADING, INSTALLING, COPYING OR OTHERWISE USING DATA FILES, AND/OR
SOFTWARE, YOU UNEQUIVOCALLY ACCEPT, AND AGREE TO BE BOUND BY, ALL OF THE
TERMS AND CONDITIONS OF THIS AGREEMENT. IF YOU DO NOT AGREE, DO NOT
DOWNLOAD, INSTALL, COPY, DISTRIBUTE OR USE THE DATA FILES OR SOFTWARE.

Permission is hereby granted, free of charge, to any person obtaining a
copy of data files and any associated documentation (the "Data Files") or
software and any associated documentation (the "Software") to deal in the
Data Files or Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, and/or sell
copies of the Data Files or Software, and to permit persons to whom the
Data Files or Software are furnished to do so, provided that either (a)
this copyright and permission notice appear with all copies of the Data
Files or Software, or (b) this copyright and permission notice appear in
associated Documentation.

THE DATA FILES AND SOFTWARE ARE PROVIDED "AS IS", WITHOUT WARRANTY OF ANY
KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT OF
THIRD PARTY RIGHTS.

IN NO EVENT SHALL THE COPYRIGHT HOLDER OR HOLDERS INCLUDED IN THIS NOTICE
BE LIABLE FOR ANY CLAIM, OR ANY SPECIAL INDIRECT OR CONSEQUENTIAL DAMAGES,
OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS,
WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION,
ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THE DATA
FILES OR SOFTWARE.

Except as contained in this notice, the name of a copyright holder shall
not be used in advertising or otherwise to promote the sale, use or other
dealings in these Data Files or Software without prior written
authorization of the copyright holder.

---

These software packages contain the following license:

- [addr2line](https://crates.io/crates/addr2line)
- [adler2](https://crates.io/crates/adler2)
- [aho-corasick](https://crates.io/crates/aho-corasick)

MIT LICENSE

Copyright (c) 2024

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
```

</details>

## Usage

```yaml
name: Build release images
on:
  # Run when a release is created.
  release:
    types: [ published ]

permissions:
  contents: read
  packages: write

jobs:
  licenses:
    runs-on: ubuntu-latest
    steps:
      # Checkout the upstream repository
      - uses: actions/checkout@v4

      # Setup rust
      - uses: actions-rust-lang/setup-rust-toolchain@v1
        with:
          toolchain: stable

      # **Note**: You must have `cargo-license` installed in your Rust toolchain
      # for this Action to work.
      - name: Install cargo-license
        run: cargo install cargo-license

      - name: Generate license report
        uses: element-hq/reproduce-rust-licenses@v1
        with:
          licenses: "MIT,Apache-2.0,Unicode-3.0"

      # Ensure you copy the generated `UPSTREAM-LICENSES.md` file in your Dockerfile.
      - name: Build Docker image
        run: docker build --build-arg INCLUDE_LICENSES=true -t my_project .
```

### Inputs

| Name      | Description                                     | Required | Default |
|-----------|-------------------------------------------------|----------|---------|
| `licenses`| Comma-separated list of licenses in preference order. | Yes      | None    |

### License Texts

By default, the script expects license text files in `./_licenses/<LICENSE_NAME>`. Set `LICENSE_FILE_DIR` as needed.

### Development

- Install the development requirements with `pip install -r dev-requirements.txt`.
- Run tests locally with `pytest --disable-warnings -v`.
- Publish a new version by tagging (e.g., `git tag v1 && git push origin v1`).
