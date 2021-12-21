import pytest
from ..common import validate_problem_test


@pytest.mark.parametrize("part", ["a", "b"])
@pytest.mark.parametrize("test", [1])
def test_day04(part, test):
    result, expected = validate_problem_test("2021", "04", part, str(test))
    assert result == expected
