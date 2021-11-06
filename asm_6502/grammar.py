import ply.lex as lex
import ply.yacc as yacc

__all__ = ['get_parser']


_PARSER = None


tokens = (
    'PSEUDO',
    'LABEL',
    'BIT',
    'ACC',
    'RX',
    'RY',
    'HEX',
    'BIN',
    'DEC',
    'CHAR',
    'CUR',
    'NEWLINE',
)

literals = ['+', '-', '*', '/', '#', '(', ')', ',', 'X', 'Y', '[', ']']

# Tokens


def t_PSEUDO(t):
    r"""\.[a-zA-Z_][a-zA-Z0-9_]*"""
    return t


def t_ACC(t):
    r"""A"""
    return t


def t_RX(t):
    r"""X"""
    return t


def t_RY(t):
    r"""Y"""
    return t


def t_LABEL(t):
    r"""[a-zA-Z_][a-zA-Z0-9_]*"""
    return t


t_BIT = r'\#LO|\#HI'


def t_HEX(t):
    r"""\$[0-9a-fA-F]+"""
    t.value = int(t.value[1:], 16)
    return t


def t_BIN(t):
    r"""%[01]+"""
    t.value = int(t.value[1:], 2)
    return t


def t_DEC(t):
    r"""[0-9]+"""
    t.value = int(t.value, 10)
    return t


def t_CHAR(t):
    r"""\'[^\'\n\r]\'"""
    t.value = ord(t.value[1])
    return t


t_CUR = r'\*'

t_ignore = " \t"
t_ignore_COMMENT = r';.*'


def t_NEWLINE(t):
    r"""[\n\r]+"""
    t.lexer.lineno += t.value.count("\n")
    return t


def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)
    raise RuntimeError()


# Syntax
precedence = (
    ('left', '+', '-'),
    ('left', '*', '/'),
    ('right', 'UMINUS'),
)


def p_stat(p):
    """stat : LABEL LABEL stat_val
            | LABEL stat_val
            | LABEL PSEUDO stat_val
            | PSEUDO stat_val
            | stat NEWLINE stat
            |
    """


def p_stat_val(p):
    """stat_val : ACC
                | arithmetic
                | LABEL
                | BIT LABEL
                | arithmetic ',' RX
                | LABEL ',' RX
                | arithmetic ',' RY
                | LABEL ',' RY
                | '(' address ')'
                | '(' LABEL ')'
                | '(' address ',' RX ')'
                | '(' LABEL ',' RX ')'
                | '(' address ')' ',' RY
                | '(' LABEL ')' ',' RY
                |
    """


def p_numeric(p):
    """numeric : '#' DEC
               | '#' HEX
               | '#' BIN
               | '#' CHAR
    """


def p_address(p):
    """address : DEC
               | HEX
               | BIN
    """


def p_arithmetic_uminus(p):
    """arithmetic : '-' arithmetic %prec UMINUS"""


def p_arithmetic(p):
    """arithmetic : numeric
                  | address
                  | CUR
                  | '[' arithmetic ']'
                  | arithmetic '+' arithmetic
                  | arithmetic '-' arithmetic
                  | arithmetic '*' arithmetic
                  | arithmetic '/' arithmetic
    """


def p_error(p):
    if p:
        print("Syntax error at '%s'" % p.value)
        raise RuntimeError()
    else:
        print("Syntax error at EOF")


def get_parser():
    global _PARSER
    if _PARSER is None:
        lex.lex()
        _PARSER = yacc.yacc()
    return _PARSER
