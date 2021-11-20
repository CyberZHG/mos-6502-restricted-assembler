from unittest import TestCase

from asm_6502 import Assembler


class TestAssembleSBC(TestCase):

    def setUp(self) -> None:
        self.assembler = Assembler()

    def test_sbc_immediate(self):
        code = "SBC #$10"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0xE9, 0x10]),
        ], results)

    def test_sbc_zero_page(self):
        code = "SBC $10"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0xE5, 0x10]),
        ], results)

    def test_sbc_zero_page_x(self):
        code = "SBC $10,X"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0xF5, 0x10]),
        ], results)

    def test_sbc_absolute(self):
        code = "SBC $ABCD"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0xED, 0xCD, 0xAB]),
        ], results)

    def test_sbc_absolute_indexed(self):
        code = "SBC $ABCD,X\n" \
               "SBC $ABCD,Y"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0xFD, 0xCD, 0xAB, 0xF9, 0xCD, 0xAB]),
        ], results)

    def test_sbc_indexed_indirect(self):
        code = "SBC ($10,X)"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0xE1, 0x10]),
        ], results)

    def test_sbc_indirect_indexed(self):
        code = "SBC ($10),Y"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0xF1, 0x10]),
        ], results)
