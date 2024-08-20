# Copyright (C) 2024 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl-3.0).


def is_number(value):
    """Check if a string represents an integer or float."""
    try:
        float(value)
        return True
    except ValueError:
        return False


def inline_or(expressions):
    """
    Combine multiple expressions with 'or'.

    Args:
        expressions (list): List of expressions to combine.

    Returns:
        str: Combined expression string with 'or',
        or an empty string if input is not a list.
    """
    if not isinstance(expressions, list):
        return ""
    return " or ".join(expressions)


def inline_and(expressions):
    """
    Combine multiple expressions with 'and'.

    Args:
        expressions (list): List of expressions to combine.

    Returns:
        str: Combined expression string with 'and',
        or an empty string if input is not a list.
    """
    if not isinstance(expressions, list):
        return ""
    return " and ".join(expressions)
