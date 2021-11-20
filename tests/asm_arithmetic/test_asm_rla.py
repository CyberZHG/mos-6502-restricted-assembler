from unittest import TestCase

from asm_6502 import Assembler


class TestAssembleRLA(TestCase):

    def setUp(self) -> None:
        self.assembler = Assembler()

    def test_rla_zero_page(self):
        code = "RLA $00"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0x27, 0x00]),
        ], results)

    def test_rla_zero_page_x(self):
        code = "RLA $10,X"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0x37, 0x10]),
        ], results)

    def test_rla_absolute(self):
        code = "RLA $ABCD"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0x2F, 0xCD, 0xAB]),
        ], results)

    def test_rla_absolute_indexed(self):
        code = "RLA $ABCD,X\n" \
               "RLA $ABCD,Y"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0x3F, 0xCD, 0xAB, 0x3B, 0xCD, 0xAB]),
        ], results)

    def test_rla_indexed_indirect(self):
        code = "RLA ($40,X)"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0x23, 0x40]),
        ], results)

    def test_rla_indirect_indexed(self):
        code = "RLA ($40),Y"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0x33, 0x40]),
        ], results)
