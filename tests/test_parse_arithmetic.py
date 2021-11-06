from unittest import TestCase

from asm_6502 import get_parser, Arithmetic, Integer


class TestParseArithmetic(TestCase):

    def setUp(self) -> None:
        self.parser = get_parser()

    def test_address(self):
        code = 'ORG  $0080'
        results = self.parser.parse(code)[0].addressing.address
        self.assertEqual(Integer(True, 128), results)

    def test_instant(self):
        code = 'TOLOWER LDY #$02'
        results = self.parser.parse(code)[0].addressing.address
        self.assertEqual(Integer(False, 2), results)

    def test_current(self):
        code = 'CMP *'
        results = self.parser.parse(code)[0].addressing.address
        self.assertEqual(Arithmetic(Arithmetic.CURRENT,), results)

    def test_add(self):
        code = "CMP #'Z'+1"
        results = self.parser.parse(code)[0].addressing.address
        self.assertEqual(Integer(False, 91), results)

    def test_sub(self):
        code = "ORA #%00100000-1"
        results = self.parser.parse(code)[0].addressing.address
        self.assertEqual(Integer(False, 31), results)

    def test_mul(self):
        code = 'CMP #2*3'
        results = self.parser.parse(code)[0].addressing.address
        self.assertEqual(Integer(False, 6), results)

        code = 'CMP #2*3+4*5'
        results = self.parser.parse(code)[0].addressing.address
        self.assertEqual(Integer(False, 26), results)

        code = 'CMP ***'
        results = self.parser.parse(code)[0].addressing.address
        self.assertEqual(Arithmetic(Arithmetic.MUL, (Arithmetic(Arithmetic.CURRENT), Arithmetic(Arithmetic.CURRENT))),
                         results)

    def test_div(self):
        code = 'CMP #24/3'
        results = self.parser.parse(code)[0].addressing.address
        self.assertEqual(Integer(False, 8), results)

        code = 'CMP */*'
        results = self.parser.parse(code)[0].addressing.address
        self.assertEqual(Arithmetic(Arithmetic.DIV, (Arithmetic(Arithmetic.CURRENT), Arithmetic(Arithmetic.CURRENT))),
                         results)

    def test_neg(self):
        code = 'CMP #-42'
        results = self.parser.parse(code)[0].addressing.address
        self.assertEqual(Integer(False, -42), results)

        code = 'CMP -**-*'
        results = self.parser.parse(code)[0].addressing.address
        self.assertEqual(Arithmetic(Arithmetic.MUL,
                                    (Arithmetic(Arithmetic.NEG, Arithmetic(Arithmetic.CURRENT)),
                                     Arithmetic(Arithmetic.NEG, Arithmetic(Arithmetic.CURRENT)))),
                         results)

    def test_parenthesis(self):
        code = 'CMP #2*[3+4*5]'
        results = self.parser.parse(code)[0].addressing.address
        self.assertEqual(Integer(False, 46), results)

    def test_low_and_high(self):
        code = 'LDA #LO $00AB+$CD00'
        results = self.parser.parse(code)[0].addressing.address
        self.assertEqual(Integer(False, 0xAB), results)

        code = 'LDA #HI $00AB+$CD00'
        results = self.parser.parse(code)[0].addressing.address
        self.assertEqual(Integer(False, 0xCD), results)

        code = 'LDA #LO *+1'
        results = self.parser.parse(code)[0].addressing.address
        self.assertEqual(Arithmetic(Arithmetic.LOW_BYTE,
                                    Arithmetic(Arithmetic.ADD, (Arithmetic(Arithmetic.CURRENT), Integer(False, 1)))),
                         results)

        code = 'LDA #HI *+1'
        results = self.parser.parse(code)[0].addressing.address
        self.assertEqual(Arithmetic(Arithmetic.HIGH_BYTE,
                                    Arithmetic(Arithmetic.ADD, (Arithmetic(Arithmetic.CURRENT), Integer(False, 1)))),
                         results)
