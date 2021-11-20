from unittest import TestCase

from asm_6502 import Assembler


class TestAssembleSRE(TestCase):

    def setUp(self) -> None:
        self.assembler = Assembler()

    def test_sre_zero_page(self):
        code = "SRE $00"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0x47, 0x00]),
        ], results)

    def test_sre_zero_page_x(self):
        code = "SRE $10,X"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0x57, 0x10]),
        ], results)

    def test_sre_absolute(self):
        code = "SRE $ABCD"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0x4F, 0xCD, 0xAB]),
        ], results)

    def test_sre_absolute_indexed(self):
        code = "SRE $ABCD,X\n" \
               "SRE $ABCD,Y"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0x5F, 0xCD, 0xAB, 0x5B, 0xCD, 0xAB]),
        ], results)

    def test_sre_indexed_indirect(self):
        code = "SRE ($40,X)"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0x43, 0x40]),
        ], results)

    def test_sre_indirect_indexed(self):
        code = "SRE ($40),Y"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0x53, 0x40]),
        ], results)
