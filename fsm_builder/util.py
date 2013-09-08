superscript_table = str.maketrans('0123456789', '⁰¹²³⁴⁵⁶⁷⁸⁹')


underscript_table = str.maketrans('0123456789', '₀₁₂₃₄₅₆₇₈₉')


def superscripted(string):
    return string.translate(superscript_table)


def underscripted(string):
    return string.translate(underscript_table)
