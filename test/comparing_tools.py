from collections import OrderedDict


def normalize_code(code):
    """
    Normalize indentation, whitespace and line breaks for comparison
    """

    replacements = OrderedDict()
    replacements['\r\n'] = '\n'
    replacements['\r\n\r\n'] = '\n'
    replacements['\r\r'] = '\n'
    replacements['\t\n'] = '\n'
    replacements['\n\n'] = '\n'
    replacements['\t'] = '    '
    replacements['\r'] = '\n'

    count = 1
    while count > 0:
        for old, new in replacements.items():
            count = code.count(old)
            code = code.replace(old, new)

    return code


def debug_dump(expected, actual, extension):
    """
    Dump the actual and expected values to 2 files
    :param extension:
    """
    with open(f"actual.{extension}", "w") as f:
        f.write(actual)

    with open(f"expected.{extension}", "w") as f:
        f.write(expected)


def normalize_lines(text):
    """
    Normalize indentation and whitespace for comparison
    """
    lines = text.splitlines()
    normalized_lines = [line.strip() for line in lines]
    return '\n'.join(normalized_lines)


def is_debug():
    """
    Dump the actual and expected values to 2 files
    """
    return True
