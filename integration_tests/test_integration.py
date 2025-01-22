import os
import shutil
import subprocess
import tempfile
import pytest

TEST_JSON = r"""
[
  {
    "name": "somecrate",
    "version": "0.1.0",
    "license": "Apache-2.0 OR MIT"
  },
  {
    "name": "othercrate",
    "version": "0.2.0",
    "license": "BSD-3-Clause"
  },
  {
    "name": "ignoredcrate",
    "version": "0.3.0",
    "license": "GPL-2.0"
  }
]
"""

@pytest.mark.integration
def test_end_to_end():
    """
    End-to-end test that:
    1. Writes dummy cargo-license JSON.
    2. Copies dummy license files into a temp dir.
    3. Runs generate-licenses.py with wanted licenses = "MIT,Apache-2.0".
    4. Verifies the resulting UPSTREAM-LICENSES.md.
    """
    # Locate the root of the repo (adjust if needed).
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    # Path to the generate-licenses.py script (adjust if needed).
    script_path = os.path.join(repo_root, "generate_licenses.py")

    # Path to our local _licenses directory with dummy license texts:
    local_licenses_dir = os.path.join(os.path.dirname(__file__), "_licenses")

    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a subdir for licenses in the temp directory.
        tmp_licenses_dir = os.path.join(tmpdir, "_licenses")
        shutil.copytree(local_licenses_dir, tmp_licenses_dir)

        # Run the script, piping in the JSON
        # We'll also set LICENSE_FILE_DIR to point to our temp _licenses folder
        cmd = [
            "python",
            script_path,
            "--licenses", "MIT,Apache-2.0"  # user preference order
        ]

        subprocess.run(
            cmd,
            cwd=tmpdir,
            env={
                **os.environ,
                "LICENSE_FILE_DIR": tmp_licenses_dir
            },
            input=TEST_JSON.encode("utf-8"),
            check=True
        )

        # Now verify UPSTREAM-LICENSES.md exists
        upstream_path = os.path.join(tmpdir, "UPSTREAM-LICENSES.md")
        assert os.path.isfile(upstream_path), "UPSTREAM-LICENSES.md was not generated."

        with open(upstream_path, "r", encoding="utf-8") as f:
            content = f.read()

        # "somecrate" should appear (picks MIT from "Apache-2.0 OR MIT")
        assert "somecrate" in content
        # "othercrate" should be ignored because BSD-3-Clause wasn't in wanted list
        assert "othercrate" not in content
        # "ignoredcrate" has GPL-2.0, also not in wanted list, so it should be excluded
        assert "ignoredcrate" not in content

        # Check that the MIT license text got included
        # (assuming _licenses/MIT.txt is something like "MIT LICENSE...")
        assert "MIT LICENSE DUMMY CONTENT" in content

        # The user chose MIT over Apache-2.0 for "somecrate," so only "MIT" text should appear.
        # However, if your script includes *all* chosen licenses for OR logic, adjust accordingly.
        # If you only pick the first matched preference, we won't see the Apache text.
        assert "APACHE LICENSE DUMMY CONTENT" not in content
