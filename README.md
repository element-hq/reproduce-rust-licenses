# Reproduce Rust Licenses Action

This GitHub Action runs the [`generate-licenses.py`](./generate-licenses.py) script to produce an `UPSTREAM-LICENSES.md` file from Cargo dependencies. It:
1. Installs Python and your repo’s Python dependencies.
2. Runs `cargo-license --json`.
3. Passes the JSON to `generate-licenses.py`.
4. Writes `UPSTREAM-LICENSES.md` containing licenses for the crates you depend on.

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
