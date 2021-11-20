from unittest import TestCase

from asm_6502 import Assembler


class TestAssembleLSR(TestCase):

    def setUp(self) -> None:
        self.assembler = Assembler()

    def test_lsr_accumulator(self):
        code = "LSR A"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0x4A]),
        ], results)

    def test_lsr_zero_page(self):
        code = "LSR $10"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0x46, 0x10]),
        ], results)

    def test_lsr_zero_page_x(self):
        code = "LSR $10,X"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0x56, 0x10]),
        ], results)

    def test_lsr_absolute(self):
        code = "LSR $ABCD"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0x4E, 0xCD, 0xAB]),
        ], results)

    def test_lsr_absolute_indexed_x(self):
        code = "LSR $ABCD,X"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0x5E, 0xCD, 0xAB]),
        ], results)
