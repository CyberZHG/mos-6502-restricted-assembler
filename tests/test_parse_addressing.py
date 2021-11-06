from unittest import TestCase

from asm_6502 import get_parser, ADDRESSING, INSTANT, ADDRESS, INTEGER, REGISTER


class TestParseAddressing(TestCase):

    def setUp(self) -> None:
        self.parser = get_parser()

    def test_addressing_accumulator(self):
        code = 'LSR A'
        results = self.parser.parse(code)[0][2]
        self.assertEqual((ADDRESSING.ACCUMULATOR,), results)

    def test_addressing_immediate(self):
        code = 'ORA #$B2'
        results = self.parser.parse(code)[0][2]
        self.assertEqual((ADDRESSING.IMMEDIATE, (INSTANT, (INTEGER, 178))), results)

    def test_addressing_implied(self):
        code = 'CLC'
        results = self.parser.parse(code)[0][2]
        self.assertEqual((ADDRESSING.IMPLIED,), results)

    def test_addressing_address(self):
        code = 'JMP $4032'
        results = self.parser.parse(code)[0][2]
        self.assertEqual((ADDRESSING.ADDRESS, (ADDRESS, (INTEGER, 16434))), results)

        code = 'LDA $35'
        results = self.parser.parse(code)[0][2]
        self.assertEqual((ADDRESSING.ADDRESS, (ADDRESS, (INTEGER, 53))), results)

    def test_addressing_indirect(self):
        code = 'JMP  ($1000)'
        results = self.parser.parse(code)[0][2]
        self.assertEqual((ADDRESSING.INDIRECT, (ADDRESS, (INTEGER, 4096))), results)

    def test_addressing_indexed(self):
        code = 'STA $1000,Y'
        results = self.parser.parse(code)[0][2]
        self.assertEqual((ADDRESSING.INDEXED, (ADDRESS, (INTEGER, 4096)), (REGISTER, 'Y')), results)

        code = 'LDA $C0,X'
        results = self.parser.parse(code)[0][2]
        self.assertEqual((ADDRESSING.INDEXED, (ADDRESS, (INTEGER, 192)), (REGISTER, 'X')), results)

    def test_addressing_indexed_indirect(self):
        code = 'LDA ($20,X)'
        results = self.parser.parse(code)[0][2]
        self.assertEqual((ADDRESSING.INDEXED_INDIRECT, (ADDRESS, (INTEGER, 32)), (REGISTER, 'X')), results)

    def test_addressing_indirect_indexed(self):
        code = 'LDA ($86),Y'
        results = self.parser.parse(code)[0][2]
        self.assertEqual((ADDRESSING.INDEXED_INDIRECT, (ADDRESS, (INTEGER, 134)), (REGISTER, 'Y')), results)
