from unittest import TestCase

from asm_6502 import get_parser, ParseError


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
        code = 'LDA XXX,YYY,ZZZ ZZZ'
        with self.assertRaises(ParseError) as e:
            self.parser.parse(code)
        self.assertEqual("ParseError: Syntax error at line 1, column 17: 'ZZZ'", str(e.exception))

    def test_wrong_accumulator(self):
        code = 'LSR X'
        with self.assertRaises(ParseError) as e:
            self.parser.parse(code)
        self.assertEqual("ParseError: Register X can not be used as an address at 1, column 5", str(e.exception))

    def test_wrong_register_in_indexed_addressing(self):
        code = 'STA $1000,A'
        with self.assertRaises(ParseError) as e:
            self.parser.parse(code)
        self.assertEqual("ParseError: Only registers X and Y can be used for indexing, found A at 1, column 11",
                         str(e.exception))

    def test_wrong_register_in_indexed_indirect_addressing(self):
        code = 'LDA ($20,Y)'
        with self.assertRaises(ParseError) as e:
            self.parser.parse(code)
        self.assertEqual("ParseError: Only register X can be used for indexed indirect addressing, "
                         "found Y at 1, column 10",
                         str(e.exception))

    def test_wrong_register_in_indirect_indexed_addressing(self):
        code = 'LDA ($86),X'
        with self.assertRaises(ParseError) as e:
            self.parser.parse(code)
        self.assertEqual("ParseError: Only register Y can be used for indexed indirect addressing, "
                         "found X at 1, column 11",
                         str(e.exception))
