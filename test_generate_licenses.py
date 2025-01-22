import pytest
from generate_licenses import parse_and_select_licenses

@pytest.mark.parametrize(
    "license_expr, wanted_licenses, expected_result",
    [
        # Single license, in wanted list
        ("Apache-2.0", ["Apache-2.0"], {"Apache-2.0"}),

        # Single license, not in wanted list
        ("Apache-2.0", ["MIT"], None),

        # Simple OR, pick first preference
        ("Apache-2.0 OR MIT", ["MIT", "Apache-2.0"], {"MIT"}),
        ("Apache-2.0 OR MIT", ["Apache-2.0", "MIT"], {"Apache-2.0"}),

        # Simple AND, both must be satisfied
        ("Apache-2.0 AND MIT", ["MIT", "Apache-2.0"], {"MIT", "Apache-2.0"}),
        ("Apache-2.0 AND MIT", ["MIT"], None),  # fails because Apache-2.0 isn't in wanted

        # Parentheses with OR, then AND
        ("(Apache-2.0 OR MIT) AND BSD-3-Clause",
         ["MIT", "BSD-3-Clause", "Apache-2.0"],
         {"MIT", "BSD-3-Clause"}),  # picks MIT from the OR group
        ("(Apache-2.0 OR MIT) AND BSD-3-Clause",
         ["Apache-2.0", "MIT"],
         None),  # fails because BSD-3-Clause not in wanted

        # Multiple parentheses
        ("(Apache-2.0 OR GPL-2.0) AND (MIT OR BSD-3-Clause)",
         ["GPL-2.0", "MIT", "Apache-2.0", "BSD-3-Clause"],
         {"GPL-2.0", "MIT"}),  # picks Apache-2.0 from first group, MIT from second
    ],
)
def test_parse_and_select_licenses(license_expr, wanted_licenses, expected_result):
    result = parse_and_select_licenses(license_expr, wanted_licenses)
    assert result == expected_result
