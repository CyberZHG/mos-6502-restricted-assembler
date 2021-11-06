from unittest import TestCase

from asm_6502 import get_parser, Addressing, INSTANT, ADDRESS, Integer, REGISTER


class TestParseAddressing(TestCase):

    def setUp(self) -> None:
        self.parser = get_parser()

    def test_addressing_accumulator(self):
        code = 'LSR A'
        results = self.parser.parse(code)[0][2]
        self.assertEqual(Addressing(Addressing.ACCUMULATOR,), results)

    def test_addressing_immediate(self):
        code = 'ORA #$B2'
        results = self.parser.parse(code)[0][2]
        self.assertEqual(Addressing(Addressing.IMMEDIATE, address=(INSTANT, Integer(False, 178))), results)

    def test_addressing_implied(self):
        code = 'CLC'
        results = self.parser.parse(code)[0][2]
        self.assertEqual(Addressing(Addressing.IMPLIED,), results)

    def test_addressing_address(self):
        code = 'JMP $4032'
        results = self.parser.parse(code)[0][2]
        self.assertEqual(Addressing(Addressing.ADDRESS, address=(ADDRESS, Integer(True, 16434))), results)

        code = 'LDA $35'
        results = self.parser.parse(code)[0][2]
        self.assertEqual(Addressing(Addressing.ADDRESS, address=(ADDRESS, Integer(False, 53))), results)

    def test_addressing_indirect(self):
        code = 'JMP  ($1000)'
        results = self.parser.parse(code)[0][2]
        self.assertEqual(Addressing(Addressing.INDIRECT, address=(ADDRESS, Integer(True, 4096))), results)

    def test_addressing_indexed(self):
        code = 'STA $1000,Y'
        results = self.parser.parse(code)[0][2]
        self.assertEqual(Addressing(Addressing.INDEXED, address=(ADDRESS, Integer(True, 4096)), register='Y'), results)

        code = 'LDA $C0,X'
        results = self.parser.parse(code)[0][2]
        self.assertEqual(Addressing(Addressing.INDEXED, address=(ADDRESS, Integer(False, 192)), register='X'), results)

    def test_addressing_indexed_indirect(self):
        code = 'LDA ($20,X)'
        results = self.parser.parse(code)[0][2]
        self.assertEqual(Addressing(Addressing.INDEXED_INDIRECT,
                                    address=(ADDRESS, Integer(False, 32)), register='X'), results)

    def test_addressing_indirect_indexed(self):
        code = 'LDA ($86),Y'
        results = self.parser.parse(code)[0][2]
        self.assertEqual(Addressing(Addressing.INDIRECT_INDEXED,
                                    address=(ADDRESS, Integer(False, 134)), register='Y'), results)
