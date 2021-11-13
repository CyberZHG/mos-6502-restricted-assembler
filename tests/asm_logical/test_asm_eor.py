from unittest import TestCase

from asm_6502 import Assembler


class TestAssembleEOR(TestCase):

    def setUp(self) -> None:
        self.assembler = Assembler()

    def test_eor_immediate(self):
        code = "EOR #$10"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0x49, 0x10]),
        ], results)

    def test_eor_zero_page(self):
        code = "EOR $10"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0x45, 0x10]),
        ], results)

    def test_eor_zero_page_x(self):
        code = "EOR $10,X"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0x55, 0x10]),
        ], results)

    def test_eor_absolute(self):
        code = "EOR $ABCD"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0x4D, 0xCD, 0xAB]),
        ], results)

    def test_eor_absolute_indexed(self):
        code = "EOR $ABCD,X\n" \
               "EOR $ABCD,Y"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0x5D, 0xCD, 0xAB, 0x59, 0xCD, 0xAB]),
        ], results)

    def test_eor_indexed_indirect(self):
        code = "EOR ($10,X)"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0x41, 0x10]),
        ], results)

    def test_eor_indirect_indexed(self):
        code = "EOR ($10),Y"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0x51, 0x10]),
        ], results)
