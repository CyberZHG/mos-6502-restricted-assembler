from unittest import TestCase

from asm_6502 import Assembler


class TestAssembleSLO(TestCase):

    def setUp(self) -> None:
        self.assembler = Assembler()

    def test_slo_zero_page(self):
        code = "SLO $00"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0x07, 0x00]),
        ], results)

    def test_slo_zero_page_x(self):
        code = "SLO $10,X"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0x17, 0x10]),
        ], results)

    def test_slo_absolute(self):
        code = "SLO $ABCD"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0x0F, 0xCD, 0xAB]),
        ], results)

    def test_slo_absolute_indexed(self):
        code = "SLO $ABCD,X\n" \
               "SLO $ABCD,Y"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0x1F, 0xCD, 0xAB, 0x1B, 0xCD, 0xAB]),
        ], results)

    def test_slo_indexed_indirect(self):
        code = "SLO ($40,X)"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0x03, 0x40]),
        ], results)

    def test_slo_indirect_indexed(self):
        code = "SLO ($40),Y"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0x13, 0x40]),
        ], results)
