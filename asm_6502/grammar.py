import ply.lex as lex
import ply.yacc as yacc

__all__ = ['get_parser', 'ParseError',
           'INTEGER', 'INSTANT', 'ADDRESS', 'CURRENT', 'ARITHMETIC', 'PSEUDO', 'LABEL', 'KEYWORD', 'INSTRUCTION',
           'PARAMETER', 'REGISTER', 'ADDRESSING']


_PARSER = None
_LEXER = None

INTEGER = 'integer'
INSTANT = 'instant'
ADDRESS = 'address'
CURRENT = 'current'
ARITHMETIC = 'arithmetic'
PSEUDO = 'pseudo'
LABEL = 'label'
KEYWORD = 'keyword'
INSTRUCTION = 'instruction'
PARAMETER = 'parameter'
REGISTER = 'register'


class ADDRESSING(object):

    ACCUMULATOR = 'addressing_accumulator'
    IMMEDIATE = 'addressing_immediate'
    IMPLIED = 'addressing_implied'
    RELATIVE = 'addressing_relative'
    ABSOLUTE = 'addressing_absolute'
    ZERO_PAGE = 'addressing_zero_page'
    INDIRECT = 'addressing_indirect'
    ABSOLUTE_INDEXED = 'addressing_absolute_indexed'
    ZERO_PAGE_INDEXED = 'addressing_zero_page_indexed'
    INDEXED_INDIRECT = 'addressing_indexed_indirect'
    INDIRECT_INDEXED = 'addressing_indirect_indexed'


KEYWORDS = {
    'ADC', 'AND', 'ASL', 'BCC', 'BCS', 'BEQ', 'BIT', 'BMI', 'BNE', 'BPL', 'BRK', 'BVC', 'BVS', 'CLC',
    'CLD', 'CLI', 'CLV', 'CMP', 'CPX', 'CPY', 'DEC', 'DEX', 'DEY', 'EOR', 'INC', 'INX', 'INY', 'JMP',
    'JSR', 'LDA', 'LDX', 'LDY', 'LSR', 'NOP', 'ORA', 'PHA', 'PHP', 'PLA', 'PLP', 'ROL', 'ROR', 'RTI',
    'RTS', 'SBC', 'SEC', 'SED', 'SEI', 'STA', 'STX', 'STY', 'TAX', 'TAY', 'TSX', 'TXA', 'TXS', 'TYA',
}

PSEUDOS = {
    'ORG', '.ORG', '.BYTE', '.WORD', '.END'
}


class ParseError(Exception):

    def __init__(self, info, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.info = info

    def __str__(self):
        return f'ParseError: {self.info}'

    def __repr__(self):
        return f'ParseError("{self.info}")'


def get_column(p, index=None):
    column = 1
    if index is None:
        pos = p.lexpos
    else:
        pos = p.lexpos(index)
    while pos - column >= 0:
        if p.lexer.lexdata[pos - column] in {'\n', '\r'}:
            break
        column += 1
    return column


# Tokens
tokens = (
    'PSEUDO',
    'LABEL',
    'BIT',
    'HEX',
    'BIN',
    'DEC',
    'CHAR',
    'CUR',
    'NEWLINE',
)

literals = ['+', '-', '/', '#', '(', ')', ',', 'X', 'Y', '[', ']']


def t_PSEUDO(t):
    r"""\.[a-zA-Z_][a-zA-Z0-9_]*"""
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
    raise ParseError(f"Illegal character '{t.value[0]}' found at line {t.lineno}, column {get_column(t)}")


# Syntax
precedence = (
    ('left', '+', '-'),
    ('left', 'CUR', '/'),
    ('right', 'UMINUS'),
)


def _get_keyword(p, label, index=None):
    if label in KEYWORDS:
        op = (KEYWORD, label)
    elif label in PSEUDOS:
        op = (PSEUDOS, label)
    else:
        raise ParseError(f"Unknown keyword at line {p.lineno(index)}, column {get_column(p, index=index)}: '{label}'")
    return op


def p_stat_with_label(p):
    """stat : LABEL LABEL stat_val
            | LABEL PSEUDO stat_val"""
    p[0] = [(INSTRUCTION, (LABEL, p[1]), _get_keyword(p, p[2], index=2), p[3])]
    return p


def p_stat_without_label(p):
    """stat : LABEL stat_val
            | PSEUDO stat_val"""
    p[0] = [(INSTRUCTION, _get_keyword(p, p[1], index=1), p[2])]
    return p


def p_stat_repeat(p):
    """stat : stat NEWLINE stat"""
    p[0] = p[1] + p[3]
    return p


def p_stat_empty(p):
    """stat :"""
    p[0] = []
    return p


def p_stat_val_direct(p):
    """stat_val : numeric
                | LABEL"""
    if p[1] == 'A':
        p[0] = (ADDRESSING.ACCUMULATOR,)
    elif isinstance(p[1], tuple) and p[1][0] == INSTANT:
        p[0] = (ADDRESSING.IMMEDIATE, p[1])
    else:
        p[0] = (PARAMETER, p[1])
    return p


def p_stat_val(p):
    """stat_val : BIT LABEL
                | numeric ',' LABEL
                | LABEL ',' LABEL
                | '(' numeric ')'
                | '(' LABEL ')'
                | '(' numeric ',' LABEL ')'
                | '(' LABEL ',' LABEL ')'
                | '(' numeric ')' ',' LABEL
                | '(' LABEL ')' ',' LABEL
                |
    """
    p[0] = (PARAMETER, None)
    return p


def p_numeric(p):
    """numeric : arithmetic
               | '#' arithmetic"""
    if p[1] == '#':
        p[0] = (INSTANT, p[2])
    else:
        p[0] = (ADDRESS, p[1])
    return p


def p_arithmetic_uminus(p):
    """arithmetic : '-' arithmetic %prec UMINUS"""
    if p[2][0] == INTEGER:
        p[0] = (p[2][0], -p[2][1])
    else:
        p[0] = ((INTEGER, 0), '-', p[2])
    return p


def p_arithmetic_direct(p):
    """arithmetic : integer"""
    p[0] = p[1]
    return p


def p_arithmetic_cur(p):
    """arithmetic : CUR"""
    p[0] = (CURRENT,)
    return p


def p_arithmetic_paren(p):
    """arithmetic : '[' arithmetic ']'"""
    p[0] = p[2]
    return p


def p_arithmetic_binary_op(p):
    """arithmetic : arithmetic '+' arithmetic
                  | arithmetic '-' arithmetic
                  | arithmetic CUR arithmetic
                  | arithmetic '/' arithmetic
    """
    if p[1][0] == INTEGER and p[3][0] == INTEGER:
        if p[2] == '+':
            p[0] = (p[1][0], p[1][1] + p[3][1])
        elif p[2] == '-':
            p[0] = (p[1][0], p[1][1] - p[3][1])
        elif p[2] == '/':
            p[0] = (p[1][0], p[1][1] // p[3][1])
        else:
            p[0] = (p[1][0], p[1][1] * p[3][1])
    else:
        p[0] = (ARITHMETIC, p[1], p[2], p[3])
    return p


def p_integer(p):
    """integer : DEC
              | HEX
              | BIN
              | CHAR
    """
    p[0] = (INTEGER, p[1])
    return p


def p_error(p):
    if p:
        raise ParseError(f"Syntax error at line {p.lineno}, column {get_column(p)}: {repr(p.value)}")
    else:
        raise ParseError(f"Syntax error at EOF")


def get_parser(debug=False):
    global _PARSER, _LEXER
    if _PARSER is None:
        _LEXER = lex.lex(debug=debug)
        _PARSER = yacc.yacc(debug=debug)
    _LEXER.lineno = 1
    return _PARSER
