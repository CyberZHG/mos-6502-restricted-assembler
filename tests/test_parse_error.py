from unittest import TestCase

from asm_6502.grammar import get_parser, ParseError


class TestParseError(TestCase):

    def setUp(self) -> None:
        self.parser = get_parser()

    def test_illegal_character(self):
        code = 'ORG  $@0080'
        with self.assertRaises(ParseError) as e:
            self.parser.parse(code)
        self.assertEqual(str(e.exception), "ParseError: Illegal character '$' found at line 1, column 6")

        code = 'ORG  $0080\nORG $@0800'
        with self.assertRaises(ParseError) as e:
            self.parser.parse(code)
        self.assertEqual(repr(e.exception),
                         "ParseError(\"Illegal character '$' found at line 2, column 5\")")

    def test_parse_comma(self):
        code = 'LDA $0080,'
        with self.assertRaises(ParseError) as e:
            self.parser.parse(code)
        self.assertEqual(str(e.exception), "ParseError: Syntax error at EOF")

    def test_parse_too_many_parameters(self):
        code = 'LDA XXX,YYY,ZZZ'
        with self.assertRaises(ParseError) as e:
            self.parser.parse(code)
        self.assertEqual(str(e.exception), "ParseError: Syntax error at line 1, column 12: ','")
