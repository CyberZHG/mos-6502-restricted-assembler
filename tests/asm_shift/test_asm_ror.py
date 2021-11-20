from unittest import TestCase

from asm_6502 import Assembler


class TestAssembleROR(TestCase):

    def setUp(self) -> None:
        self.assembler = Assembler()

    def test_ror_accumulator(self):
        code = "ROR A"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0x6A]),
        ], results)

    def test_ror_zero_page(self):
        code = "ROR $10"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0x66, 0x10]),
        ], results)

    def test_ror_zero_page_x(self):
        code = "ROR $10,X"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0x76, 0x10]),
        ], results)

    def test_ror_absolute(self):
        code = "ROR $ABCD"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0x6E, 0xCD, 0xAB]),
        ], results)

    def test_ror_absolute_indexed_x(self):
        code = "ROR $ABCD,X"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0x7E, 0xCD, 0xAB]),
        ], results)
