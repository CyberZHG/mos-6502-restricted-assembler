from unittest import TestCase

from asm_6502.grammar import get_parser, ADDRESS, INSTANT, CURRENT, ARITHMETIC


class TestParseArithmetic(TestCase):

    def setUp(self) -> None:
        self.parser = get_parser()

    def test_address(self):
        code = 'ORG  $0080'
        results = self.parser.parse(code)[0][2][1]
        self.assertEqual(results, (ADDRESS, 128))

    def test_instant(self):
        code = 'TOLOWER LDY #$02'
        results = self.parser.parse(code)[0][3][1]
        self.assertEqual(results, (INSTANT, 2))

    def test_current(self):
        code = 'CMP *'
        results = self.parser.parse(code)[0][2][1]
        self.assertEqual(results, (CURRENT,))

    def test_add(self):
        code = "CMP #'Z'+1"
        results = self.parser.parse(code)[0][2][1]
        self.assertEqual(results, (INSTANT, 91))

    def test_sub(self):
        code = "ORA #%00100000"
        results = self.parser.parse(code)[0][2][1]
        self.assertEqual(results, (INSTANT, 32))

    def test_mul(self):
        code = 'CMP #2*3'
        results = self.parser.parse(code)[0][2][1]
        self.assertEqual(results, (INSTANT, 6))

        code = 'CMP #2*3+4*5'
        results = self.parser.parse(code)[0][2][1]
        self.assertEqual(results, (INSTANT, 26))

        code = 'CMP ***'
        results = self.parser.parse(code)[0][2][1]
        self.assertEqual(results, (ARITHMETIC, (CURRENT,), '*', (CURRENT,)))

    def test_div(self):
        code = 'CMP #24/3'
        results = self.parser.parse(code)[0][2][1]
        self.assertEqual(results, (INSTANT, 8))

        code = 'CMP */*'
        results = self.parser.parse(code)[0][2][1]
        self.assertEqual(results, (ARITHMETIC, (CURRENT,), '/', (CURRENT,)))

    def test_neg(self):
        code = 'CMP -#42'
        results = self.parser.parse(code)[0][2][1]
        self.assertEqual(results, (INSTANT, -42))

        code = 'CMP -**-*'
        results = self.parser.parse(code)[0][2][1]
        self.assertEqual(results, (ARITHMETIC, ((INSTANT, 0), '-', (CURRENT,)), '*', ((INSTANT, 0), '-', (CURRENT,))))

    def test_parenthesis(self):
        code = 'CMP #2*[3+4*5]'
        results = self.parser.parse(code)[0][2][1]
        self.assertEqual(results, (INSTANT, 46))
