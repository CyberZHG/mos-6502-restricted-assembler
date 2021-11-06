from unittest import TestCase

from asm_6502.grammar import get_parser, ADDRESS, INSTANT, CURRENT, ARITHMETIC, INTEGER


class TestParseArithmetic(TestCase):

    def setUp(self) -> None:
        self.parser = get_parser()

    def test_address(self):
        code = 'ORG  $0080'
        results = self.parser.parse(code)[0][2][1]
        self.assertEqual((ADDRESS, (INTEGER, 128)), results)

    def test_instant(self):
        code = 'TOLOWER LDY #$02'
        results = self.parser.parse(code)[0][3][1]
        self.assertEqual((INSTANT, (INTEGER, 2)), results)

    def test_current(self):
        code = 'CMP *'
        results = self.parser.parse(code)[0][2][1]
        self.assertEqual((ADDRESS, (CURRENT,)), results)

    def test_add(self):
        code = "CMP #'Z'+1"
        results = self.parser.parse(code)[0][2][1]
        self.assertEqual((INSTANT, (INTEGER, 91)), results)

    def test_sub(self):
        code = "ORA #%00100000-1"
        results = self.parser.parse(code)[0][2][1]
        self.assertEqual((INSTANT, (INTEGER, 31)), results)

    def test_mul(self):
        code = 'CMP #2*3'
        results = self.parser.parse(code)[0][2][1]
        self.assertEqual((INSTANT, (INTEGER, 6)), results)

        code = 'CMP #2*3+4*5'
        results = self.parser.parse(code)[0][2][1]
        self.assertEqual((INSTANT, (INTEGER, 26)), results)

        code = 'CMP ***'
        results = self.parser.parse(code)[0][2][1]
        self.assertEqual((ADDRESS, (ARITHMETIC, (CURRENT,), '*', (CURRENT,))), results)

    def test_div(self):
        code = 'CMP #24/3'
        results = self.parser.parse(code)[0][2][1]
        self.assertEqual((INSTANT, (INTEGER, 8)), results)

        code = 'CMP */*'
        results = self.parser.parse(code)[0][2][1]
        self.assertEqual((ADDRESS, (ARITHMETIC, (CURRENT,), '/', (CURRENT,))), results)

    def test_neg(self):
        code = 'CMP #-42'
        results = self.parser.parse(code)[0][2][1]
        self.assertEqual((INSTANT, (INTEGER, -42)), results)

        code = 'CMP -**-*'
        results = self.parser.parse(code)[0][2][1]
        self.assertEqual((ADDRESS, (ARITHMETIC, ((INTEGER, 0), '-', (CURRENT,)), '*', ((INTEGER, 0), '-', (CURRENT,)))),
                         results)

    def test_parenthesis(self):
        code = 'CMP #2*[3+4*5]'
        results = self.parser.parse(code)[0][2][1]
        self.assertEqual((INSTANT, (INTEGER, 46)), results)
