import ply.lex as lex
import ply.yacc as yacc

__all__ = ['get_parser',
           'INSTANT', 'ADDRESS', 'CURRENT', 'PSEUDO', 'LABEL', 'KEYWORD']


_PARSER = None

INSTANT = 'instant'
ADDRESS = 'address'
CURRENT = 'current'
ARITHMETIC = 'arithmetic'
PSEUDO = 'pseudo'
LABEL = 'label'
KEYWORD = 'keyword'
INSTRUCTION = 'instruction'
PARAMETER = 'parameter'

KEYWORDS = {
    'ADC', 'AND', 'ASL', 'BCC', 'BCS', 'BEQ', 'BIT', 'BMI', 'BNE', 'BPL', 'BRK', 'BVC', 'BVS', 'CLC',
    'CLD', 'CLI', 'CLV', 'CMP', 'CPX', 'CPY', 'DEC', 'DEX', 'DEY', 'EOR', 'INC', 'INX', 'INY', 'JMP',
    'JSR', 'LDA', 'LDX', 'LDY', 'LSR', 'NOP', 'ORA', 'PHA', 'PHP', 'PLA', 'PLP', 'ROL', 'ROR', 'RTI',
    'RTS', 'SBC', 'SEC', 'SED', 'SEI', 'STA', 'STX', 'STY', 'TAX', 'TAY', 'TSX', 'TXA', 'TXS', 'TYA',
}

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

literals = ['+', '-', '*', '/', '#', '(', ')', ',', 'X', 'Y', '[', ']']


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
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)
    raise RuntimeError()


# Syntax
precedence = (
    ('left', '+', '-'),
    ('left', '*', '/'),
    ('right', 'UMINUS'),
)


def p_stat_with_label(p):
    """stat : LABEL LABEL stat_val
            | LABEL PSEUDO stat_val"""
    p[0] = [(INSTRUCTION, p[1], p[2], p[3])]
    return p


def p_stat_without_label(p):
    """stat : LABEL stat_val
            | PSEUDO stat_val"""
    p[0] = [(INSTRUCTION, p[1], p[2])]
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
    """stat_val : arithmetic
                | LABEL"""
    p[0] = (PARAMETER, p[1])
    return p


def p_stat_val(p):
    """stat_val : BIT LABEL
                | arithmetic ',' LABEL
                | LABEL ',' LABEL
                | '(' address ')'
                | '(' LABEL ')'
                | '(' address ',' LABEL ')'
                | '(' LABEL ',' LABEL ')'
                | '(' address ')' ',' LABEL
                | '(' LABEL ')' ',' LABEL
                |
    """
    p[0] = (PARAMETER, None)
    return p


def p_numeric(p):
    """numeric : '#' DEC
               | '#' HEX
               | '#' BIN
               | '#' CHAR
    """
    p[0] = (INSTANT, p[2])
    return p


def p_address(p):
    """address : DEC
               | HEX
               | BIN
    """
    p[0] = (ADDRESS, p[1])
    return p


def p_arithmetic_uminus(p):
    """arithmetic : '-' arithmetic %prec UMINUS"""
    p[0] = (p[2][0], -p[2][1])
    return p


def p_arithmetic_direct(p):
    """arithmetic : numeric
                  | address"""
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
                  | arithmetic '*' arithmetic
                  | arithmetic '/' arithmetic
    """
    if p[1][0] in {INSTANT, ADDRESS} and p[3][0] in {INSTANT, ADDRESS}:
        if p[2] == '+':
            p[0] = (p[1][0], p[1][1] + p[3][1])
        elif p[2] == '-':
            p[0] = (p[1][0], p[1][1] - p[3][1])
        elif p[2] == '*':
            p[0] = (p[1][0], p[1][1] * p[3][1])
        else:
            p[0] = (p[1][0], p[1][1] // p[3][1])
    else:
        p[0] = (ARITHMETIC, p[1], p[2], p[3])
    return p


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
