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
        self.assertEqual("ParseError: Syntax error at line 1, column 9: 'YYY'", str(e.exception))

    def test_wrong_accumulator(self):
        code = 'LSR X'
        with self.assertRaises(ParseError) as e:
            self.parser.parse(code)
        self.assertEqual("ParseError: Register X can not be used as an address at 1, column 5", str(e.exception))
