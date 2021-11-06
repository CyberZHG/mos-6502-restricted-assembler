from unittest import TestCase

from asm_6502.grammar import get_parser, ParseError


class TestParseError(TestCase):

    def setUp(self) -> None:
        self.parser = get_parser()

    def test_illegal_character(self):
        code = 'ORG  $@0080'
        with self.assertRaises(ParseError) as e:
            self.parser.parse(code)
        self.assertEqual("ParseError: Illegal character '$' found at line 1, column 6", str(e.exception))

        code = 'ORG  $0080\nORG $@0800'
        with self.assertRaises(ParseError) as e:
            self.parser.parse(code)
        self.assertEqual("ParseError(\"Illegal character '$' found at line 2, column 5\")", repr(e.exception))

    def test_parse_comma(self):
        code = 'LDA $0080,'
        with self.assertRaises(ParseError) as e:
            self.parser.parse(code)
        self.assertEqual("ParseError: Syntax error at EOF", str(e.exception))

    def test_parse_too_many_parameters(self):
        code = 'LDA XXX,YYY,ZZZ'
        with self.assertRaises(ParseError) as e:
            self.parser.parse(code)
        self.assertEqual("ParseError: Syntax error at line 1, column 12: ','", str(e.exception))

    def test_invalid_keyword(self):
        code = 'LDK #$00'
        with self.assertRaises(ParseError) as e:
            self.parser.parse(code)
        self.assertEqual("ParseError: Unknown keyword at line 1, column 1: 'LDK'", str(e.exception))

        code = '  LDK #$00'
        with self.assertRaises(ParseError) as e:
            self.parser.parse(code)
        self.assertEqual("ParseError: Unknown keyword at line 1, column 3: 'LDK'", str(e.exception))

        code = 'LDK LDK #$00'
        with self.assertRaises(ParseError) as e:
            self.parser.parse(code)
        self.assertEqual("ParseError: Unknown keyword at line 1, column 5: 'LDK'", str(e.exception))
