#!/usr/bin/env python3

import sys
import os
import json
import argparse
import re

def split_top_level_and(expr: str) -> list[str]:
    """
    Splits a license expression on top-level 'AND' tokens
    respecting parentheses. Returns a list of sub-expressions.
    E.g. '(Apache-2.0 OR MIT) AND BSD-3-Clause' -> ['(Apache-2.0 OR MIT)', 'BSD-3-Clause']
    """
    parts = []
    bracket_depth = 0
    current = []

    tokens = re.split(r'(\(|\)|\s+AND\s+|\s+OR\s+)', expr)
    # tokens includes possible parentheses, 'AND', 'OR' markers, or whitespace.

    for i, token in enumerate(tokens):
        if token is None or token.strip() == "":
            continue
        token_stripped = token.strip()

        # Track parentheses depth
        if token_stripped == "(":
            bracket_depth += 1
            current.append(token)
        elif token_stripped == ")":
            bracket_depth -= 1
            current.append(token)
        elif token_stripped == "AND" and bracket_depth == 0:
            # Split point on top-level AND
            part = "".join(current).strip()
            if part:
                parts.append(part)
            current = []
        else:
            current.append(token)

    if current:
        part = "".join(current).strip()
        if part:
            parts.append(part)
    return parts


def split_top_level_or(expr: str) -> list[str]:
    """
    Splits a sub-expression on top-level 'OR' tokens
    respecting parentheses. Returns a list of sub-expressions.
    E.g. '(Apache-2.0 OR MIT)' -> ['Apache-2.0', 'MIT']
    """
    parts = []
    bracket_depth = 0
    current = []

    # Strip leading and trailing parantheses if the expression is wrapped in
    # them, as they're logically meaningless and break the below.
    if expr.startswith("(") and expr.endswith(")"):
        expr = expr[1:-1]

    tokens = re.split(r'(\(|\)|\s+AND\s+|\s+OR\s+)', expr)
    for i, token in enumerate(tokens):
        if token is None or token.strip() == "":
            continue
        token_stripped = token.strip()

        # Track parentheses depth
        if token_stripped == "(":
            bracket_depth += 1
            current.append(token)
        elif token_stripped == ")":
            bracket_depth -= 1
            current.append(token)
        elif token_stripped == "OR" and bracket_depth == 0:
            part = "".join(current).strip("() \t\n\r")
            if part:
                parts.append(part)
            current = []
        else:
            current.append(token)

    if current:
        part = "".join(current).strip("() \t\n\r")
        if part:
            parts.append(part)

    return parts


def parse_and_select_licenses(license_expr: str, wanted_licenses: list[str]) -> set[str] | None:
    """
    For a given license_expr (string) like "(Apache-2.0 OR MIT) AND BSD-3-Clause",
    split on top-level AND, then for each sub-expression split on top-level OR.
    For each OR set, pick the first license in the user's preference order
    that appears. If any AND part fails, return None. Otherwise return
    a set of all picked licenses.
    """
    chosen_licenses = set()

    # Split into sub-expressions around top-level AND
    and_parts = split_top_level_and(license_expr)

    for part in and_parts:
        # Each part might be something like "(Apache-2.0 OR MIT)"
        # Now split on top-level OR
        or_parts = split_top_level_or(part)

        # or_parts might be ['Apache-2.0', 'MIT'] for example
        # We pick the first in the user’s preference that’s also in or_parts
        selected = None
        for pref_license in wanted_licenses:
            for candidate in or_parts:
                candidate_str = candidate.strip("() \t\n\r")
                if candidate_str == pref_license:
                    selected = candidate_str
                    break
            if selected:
                break

        # If we didn't find a suitable license in that OR part, entire expression fails
        if not selected:
            return None

        # Add to the final set of chosen licenses
        chosen_licenses.add(selected)

    return chosen_licenses


def main():
    parser = argparse.ArgumentParser(
        description="Generate UPSTREAM-LICENSES.md from cargo-license --json output."
    )
    parser.add_argument(
        "--licenses",
        required=True,
        help="Comma-separated list of license names to include in the final output, in order of preference."
    )
    args = parser.parse_args()

    wanted_licenses = [l.strip() for l in args.licenses.split(",")]

    # Read JSON data from stdin
    data = json.load(sys.stdin)

    # Env var or default for license file directory
    license_dir = os.environ.get("LICENSE_FILE_DIR", "./_licenses")

    # Prepare a place to store crates by each final license we choose.
    # If a crate has an "AND" expression that picks multiple, we'll list it under each.
    crates_by_license = {}

    for dep in data:
        license_expr = dep.get("license")
        if not license_expr:
            print(f"warning: {dep} crate did not specify its license")
            continue

        # Attempt to select from the expression
        chosen = parse_and_select_licenses(license_expr, wanted_licenses)
        if chosen is None:
            # Means we can't or won't comply with it based on the user’s preferences
            continue

        # Each license in 'chosen' is something we must comply with for that crate
        for lic in chosen:
            crates_by_license.setdefault(lic, []).append(dep["name"])

    # Build UPSTREAM-LICENSES.md
    with open("UPSTREAM-LICENSES.md", "w", encoding="utf-8") as out:
        out.write(
            "This file contains licenses from the upstream software we depend on. "
            "This file\nMUST be included with all distributions of the software.\n\n"
            "This file is generated by a script during release.\n\n"
        )

        # Output in the order of wanted_licenses
        for lic in wanted_licenses:
            if lic not in crates_by_license:
                continue

            crate_list = crates_by_license[lic]
            if not crate_list:
                continue

            out.write("---\n\nThese software packages contain the following license:\n\n")
            for crate_name in crate_list:
                out.write(f"- [{crate_name}](https://crates.io/crates/{crate_name})\n")
            out.write("\n")

            # Read and write license text
            license_path = os.path.join(license_dir, f"{lic}")
            if not os.path.isfile(license_path):
                print(f"error: could not find license file at '{license_path}'")
                sys.exit(1)
            else:
                with open(license_path, "r", encoding="utf-8") as lf:
                    out.write("```\n")
                    out.write(lf.read())
                    out.write("\n```")
                    out.write("\n\n")
    
    print("File generated successfully!")

if __name__ == "__main__":
    main()
