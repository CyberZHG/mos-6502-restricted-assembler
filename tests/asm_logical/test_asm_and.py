from unittest import TestCase

from asm_6502 import Assembler


class TestAssembleAND(TestCase):

    def setUp(self) -> None:
        self.assembler = Assembler()

    def test_and_immediate(self):
        code = "AND #$10"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0x29, 0x10]),
        ], results)

    def test_and_zero_page(self):
        code = "AND $10"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0x25, 0x10]),
        ], results)

    def test_and_zero_page_x(self):
        code = "AND $10,X"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0x35, 0x10]),
        ], results)

    def test_and_absolute(self):
        code = "AND $ABCD"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0x2D, 0xCD, 0xAB]),
        ], results)

    def test_and_absolute_indexed(self):
        code = "AND $ABCD,X\n" \
               "AND $ABCD,Y"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0x3D, 0xCD, 0xAB, 0x39, 0xCD, 0xAB]),
        ], results)

    def test_and_indexed_indirect(self):
        code = "AND ($10,X)"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0x21, 0x10]),
        ], results)

    def test_and_indirect_indexed(self):
        code = "AND ($10),Y"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0x31, 0x10]),
        ], results)
