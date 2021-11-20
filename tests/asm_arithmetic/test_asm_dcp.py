from unittest import TestCase

from asm_6502 import Assembler


class TestAssembleDCP(TestCase):

    def setUp(self) -> None:
        self.assembler = Assembler()

    def test_dcp_zero_page(self):
        code = "DCP $00"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0xC7, 0x00]),
        ], results)

    def test_dcp_zero_page_x(self):
        code = "DCP $10,X"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0xD7, 0x10]),
        ], results)

    def test_dcp_absolute(self):
        code = "DCP $ABCD"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0xCF, 0xCD, 0xAB]),
        ], results)

    def test_dcp_absolute_indexed(self):
        code = "DCP $ABCD,X\n" \
               "DCP $ABCD,Y"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0xDF, 0xCD, 0xAB, 0xDB, 0xCD, 0xAB]),
        ], results)

    def test_dcp_indexed_indirect(self):
        code = "DCP ($40,X)"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0xC3, 0x40]),
        ], results)

    def test_dcp_indirect_indexed(self):
        code = "DCP ($40),Y"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0xD3, 0x40]),
        ], results)
