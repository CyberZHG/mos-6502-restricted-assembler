from collections import namedtuple

import ply.lex as lex
import ply.yacc as yacc

__all__ = ['get_parser', 'ParseError', 'Integer', 'Addressing', 'Arithmetic', 'Instruction']


_PARSER = None
_LEXER = None


class Integer(namedtuple('Integer', ['is_word', 'value'])):

    __slots__ = ()

    def __add__(self, other):
        value = self.value + other.value
        return Integer(
            is_word=self.is_word or other.is_word or value > 0xFF,
            value=value,
        )

    def __sub__(self, other):
        return Integer(
            is_word=self.is_word or other.is_word,
            value=self.value - other.value,
        )

    def __mul__(self, other):
        value = self.value * other.value
        return Integer(
            is_word=self.is_word or other.is_word or value > 0xFF,
            value=value,
        )

    def __floordiv__(self, other):
        return Integer(
            is_word=self.is_word or other.is_word,
            value=self.value // other.value,
        )

    def __neg__(self):
        return Integer(is_word=self.is_word, value=-self.value)

    def low_byte(self):
        return Integer(is_word=False, value=self.value & 0xFF)

    def high_byte(self):
        return Integer(is_word=False, value=(self.value >> 8) & 0xFF)


class Addressing(namedtuple('Addressing', ['mode', 'address', 'register'], defaults=[None, None, None])):

    ACCUMULATOR = 'accumulator'
    IMMEDIATE = 'immediate'
    IMPLIED = 'implied'
    ADDRESS = 'address'
    ZERO_PAGE = 'zero page'
    ZERO_PAGE_X = 'zero page X'
    ZERO_PAGE_Y = 'zero page Y'
    ABSOLUTE = 'absolute'
    ABSOLUTE_X = 'absolute X'
    ABSOLUTE_Y = 'absolute Y'
    INDIRECT = 'indirect'
    INDEXED = 'indexed'
    INDEXED_INDIRECT = 'indexed indirect'
    INDIRECT_INDEXED = 'indirect indexed'

    LIST = 'list'


class Arithmetic(namedtuple('Arithmetic', ['mode', 'param'], defaults=[None, None])):

    CURRENT = 'current'
    LABEL = 'label'

    ADD = 'add'
    SUB = 'sub'
    MUL = 'mul'
    DIV = 'div'
    NEG = 'neg'

    LOW_BYTE = 'low_byte'
    HIGH_BYTE = 'high_byte'

    LIST = 'list'


class Instruction(namedtuple('Instruction', ['label', 'op', 'addressing', 'line_num'])):

    KEYWORDS = {
        'ADC', 'AND', 'ASL', 'BCC', 'BCS', 'BEQ', 'BIT', 'BMI', 'BNE', 'BPL', 'BRK', 'BVC', 'BVS', 'CLC',
        'CLD', 'CLI', 'CLV', 'CMP', 'CPX', 'CPY', 'DEC', 'DEX', 'DEY', 'EOR', 'INC', 'INX', 'INY', 'JMP',
        'JSR', 'LDA', 'LDX', 'LDY', 'LSR', 'NOP', 'ORA', 'PHA', 'PHP', 'PLA', 'PLP', 'ROL', 'ROR', 'RTI',
        'RTS', 'SBC', 'SEC', 'SED', 'SEI', 'STA', 'STX', 'STY', 'TAX', 'TAY', 'TSX', 'TXA', 'TXS', 'TYA',

        'ANC', 'ARR', 'ASR', 'DCP', 'ISC', 'JAM', 'LAS', 'LAX', 'RLA', 'RRA', 'SAX', 'SBX', 'SHA', 'SHS',
        'SHX', 'SHY', 'SLO', 'SRE', 'XAA'
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


def _get_column(p, index=None):
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
    'REGISTER',
    'KEYWORD',
    'LABEL',
    'BIT',
    'HEX',
    'BIN',
    'DEC',
    'CHAR',
    'CUR',
    'NEWLINE',
)

literals = ['+', '-', '/', '#', '(', ')', ',', '[', ']']


def t_PSEUDO(t):
    r"""\.[a-zA-Z_][a-zA-Z0-9_]*"""
    t.type = 'KEYWORD'
    return t


def t_LABEL(t):
    r"""[a-zA-Z_][a-zA-Z0-9_]*"""
    if t.value in {'A', 'X', 'Y'}:
        t.type = 'REGISTER'
    elif t.value in Instruction.KEYWORDS or t.value in Instruction.PSEUDOS:
        t.type = 'KEYWORD'
    return t


t_BIT = r'\#LO|\#HI'


def t_HEX(t):
    r"""\$[0-9a-fA-F]+"""
    t.value = Integer(
        is_word=len(t.value) > 2 + 1,
        value=int(t.value[1:], 16),
    )
    return t


def t_BIN(t):
    r"""%[01]+"""
    t.value = Integer(
        is_word=len(t.value) > 8 + 1,
        value=int(t.value[1:], 2),
    )
    return t


def t_DEC(t):
    r"""[0-9]+"""
    value = int(t.value, 10)
    t.value = Integer(
        is_word=value > 0xFF,
        value=value,
    )
    return t


def t_CHAR(t):
    r"""\'[^\'\n\r]\'"""
    t.value = Integer(is_word=False, value=ord(t.value[1]))
    return t


t_CUR = r'\*'

t_ignore = " \t"
t_ignore_COMMENT = r';.*'


def t_NEWLINE(t):
    r"""[\n\r]+"""
    t.lexer.lineno += t.value.count("\n")
    return t


def t_error(t):
    raise ParseError(f"Illegal character '{t.value[0]}' found at line {t.lineno}, column {_get_column(t)}")


# Syntax
precedence = (
    ('left', '+', '-'),
    ('left', 'CUR', '/'),
    ('right', 'UMINUS'),
)


def p_stat_with_label(p):
    """stat : LABEL KEYWORD stat_val"""
    p[0] = [Instruction(label=p[1], op=p[2], addressing=p[3], line_num=p.lineno(1))]
    return p


def p_stat_without_label(p):
    """stat : KEYWORD stat_val"""
    p[0] = [Instruction(label=None, op=p[1], addressing=p[2], line_num=p.lineno(1))]
    return p


def p_stat_repeat(p):
    """stat : stat NEWLINE stat"""
    p[0] = p[1] + p[3]
    return p


def p_stat_empty(p):
    """stat :"""
    p[0] = []
    return p


def p_stat_val_accumulator(p):
    """stat_val : REGISTER"""
    if p[1] == 'A':
        p[0] = Addressing(Addressing.ACCUMULATOR)
    else:
        raise ParseError(f"Register {p[1]} can not be used as an address at "
                         f"{p.lineno(1)}, column {_get_column(p, index=1)}")
    return p


def p_stat_val_direct(p):
    """stat_val : arithmetic"""
    p[0] = Addressing(Addressing.ADDRESS, address=p[1])
    return p


def p_stat_val_empty(p):
    """stat_val :"""
    p[0] = Addressing(Addressing.IMPLIED,)
    return p


def p_stat_val_indirect(p):
    """stat_val : '(' arithmetic ')'"""
    p[0] = Addressing(Addressing.INDIRECT, address=p[2])
    return p


def p_stat_val_indexed(p):
    """stat_val : arithmetic ',' REGISTER"""
    if p[3][0] not in {'X', 'Y'}:
        raise ParseError(f"Only registers X and Y can be used for indexing, found {p[3][0]} at "
                         f"{p.lineno(3)}, column {_get_column(p, index=3)}")
    p[0] = Addressing(Addressing.INDEXED, address=p[1], register=p[3])
    return p


def p_stat_val_indexed_indirect(p):
    """stat_val : '(' arithmetic ',' REGISTER ')'"""
    if p[4][0] != 'X':
        raise ParseError(f"Only register X can be used for indexed indirect addressing, found {p[4][0]} at "
                         f"{p.lineno(4)}, column {_get_column(p, index=4)}")
    p[0] = Addressing(Addressing.INDEXED_INDIRECT, address=p[2], register=p[4])
    return p


def p_stat_val_indirect_indexed(p):
    """stat_val : '(' arithmetic ')' ',' REGISTER"""
    if p[5][0] != 'Y':
        raise ParseError(f"Only register Y can be used for indexed indirect addressing, found {p[5][0]} at "
                         f"{p.lineno(5)}, column {_get_column(p, index=5)}")
    p[0] = Addressing(Addressing.INDIRECT_INDEXED, address=p[2], register=p[5])
    return p


def p_stat_val_immediate_bit(p):
    """stat_val : BIT arithmetic"""
    if p[1] == '#LO':
        if isinstance(p[2], Integer):
            p[0] = Addressing(Addressing.IMMEDIATE, address=p[2].low_byte())
        else:
            p[0] = Addressing(Addressing.IMMEDIATE, address=Arithmetic(Arithmetic.LOW_BYTE, p[2]))
    else:
        if isinstance(p[2], Integer):
            p[0] = Addressing(Addressing.IMMEDIATE, address=p[2].high_byte())
        else:
            p[0] = Addressing(Addressing.IMMEDIATE, address=Arithmetic(Arithmetic.HIGH_BYTE, p[2]))
    return p


def p_stat_val_immediate(p):
    """stat_val : '#' arithmetic"""
    p[0] = Addressing(Addressing.IMMEDIATE, address=p[2])
    return p


def p_stat_val_list(p):
    """stat_val : arithmetic_list"""
    p[0] = Addressing(Addressing.LIST, address=p[1])
    return p


def p_arithmetic_list(p):
    """arithmetic_list : arithmetic ',' arithmetic_list
                       | arithmetic"""
    if len(p) == 2:
        p[0] = Arithmetic(Arithmetic.LIST, [p[1]])
    else:
        p[0] = Arithmetic(Arithmetic.LIST, [p[1]] + p[3].param)
    return p


def p_arithmetic_uminus(p):
    """arithmetic : '-' arithmetic %prec UMINUS"""
    if isinstance(p[2], Integer):
        p[0] = -p[2]
    else:
        p[0] = Arithmetic(Arithmetic.NEG, p[2])
    return p


def p_arithmetic_direct(p):
    """arithmetic : integer"""
    p[0] = p[1]
    return p


def p_arithmetic_label(p):
    """arithmetic : LABEL"""
    p[0] = Arithmetic(Arithmetic.LABEL, p[1])
    return p


def p_arithmetic_cur(p):
    """arithmetic : CUR"""
    p[0] = Arithmetic(Arithmetic.CURRENT)
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
    if isinstance(p[1], Integer) and isinstance(p[3], Integer):
        if p[2] == '+':
            p[0] = p[1] + p[3]
        elif p[2] == '-':
            p[0] = p[1] - p[3]
        elif p[2] == '/':
            p[0] = p[1] // p[3]
        else:
            p[0] = p[1] * p[3]
    else:
        if p[2] == '+':
            p[0] = Arithmetic(Arithmetic.ADD, (p[1], p[3]))
        elif p[2] == '-':
            p[0] = Arithmetic(Arithmetic.SUB, (p[1], p[3]))
        elif p[2] == '/':
            p[0] = Arithmetic(Arithmetic.DIV, (p[1], p[3]))
        else:
            p[0] = Arithmetic(Arithmetic.MUL, (p[1], p[3]))
    return p


def p_integer(p):
    """integer : DEC
              | HEX
              | BIN
              | CHAR
    """
    p[0] = p[1]
    return p


def p_error(p):
    if p:
        raise ParseError(f"Syntax error at line {p.lineno}, column {_get_column(p)}: {repr(p.value)}")
    else:
        raise ParseError(f"Syntax error at EOF")


def get_parser(debug=False):
    global _PARSER, _LEXER
    if _PARSER is None:
        _LEXER = lex.lex(debug=debug)
        _PARSER = yacc.yacc(debug=debug)
    _LEXER.lineno = 1
    return _PARSER
