from unittest import TestCase

from asm_6502 import Assembler


class TestAssembleCMP(TestCase):

    def setUp(self) -> None:
        self.assembler = Assembler()

    def test_cmp_immediate(self):
        code = "CMP #$10"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0xC9, 0x10]),
        ], results)

    def test_cmp_zero_page(self):
        code = "CMP $10"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0xC5, 0x10]),
        ], results)

    def test_cmp_zero_page_x(self):
        code = "CMP $10,X"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0xD5, 0x10]),
        ], results)

    def test_cmp_absolute(self):
        code = "CMP $ABCD"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0xCD, 0xCD, 0xAB]),
        ], results)

    def test_cmp_absolute_indexed(self):
        code = "CMP $ABCD,X\n" \
               "CMP $ABCD,Y"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0xDD, 0xCD, 0xAB, 0xD9, 0xCD, 0xAB]),
        ], results)

    def test_cmp_indexed_indirect(self):
        code = "CMP ($10,X)"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0xC1, 0x10]),
        ], results)

    def test_cmp_indirect_indexed(self):
        code = "CMP ($10),Y"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0xD1, 0x10]),
        ], results)
