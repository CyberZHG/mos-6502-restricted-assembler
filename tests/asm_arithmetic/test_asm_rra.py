from unittest import TestCase

from asm_6502 import Assembler


class TestAssembleRRA(TestCase):

    def setUp(self) -> None:
        self.assembler = Assembler()

    def test_rra_zero_page(self):
        code = "RRA $00"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0x67, 0x00]),
        ], results)

    def test_rra_zero_page_x(self):
        code = "RRA $10,X"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0x77, 0x10]),
        ], results)

    def test_rra_absolute(self):
        code = "RRA $ABCD"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0x6F, 0xCD, 0xAB]),
        ], results)

    def test_rra_absolute_indexed(self):
        code = "RRA $ABCD,X\n" \
               "RRA $ABCD,Y"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0x7F, 0xCD, 0xAB, 0x7B, 0xCD, 0xAB]),
        ], results)

    def test_rra_indexed_indirect(self):
        code = "RRA ($40,X)"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0x63, 0x40]),
        ], results)

    def test_rra_indirect_indexed(self):
        code = "RRA ($40),Y"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0x73, 0x40]),
        ], results)
