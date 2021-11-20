from unittest import TestCase

from asm_6502 import Assembler


class TestAssembleISC(TestCase):

    def setUp(self) -> None:
        self.assembler = Assembler()

    def test_isc_zero_page(self):
        code = "ISC $00"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0xE7, 0x00]),
        ], results)

    def test_isc_zero_page_x(self):
        code = "ISC $10,X"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0xF7, 0x10]),
        ], results)

    def test_isc_absolute(self):
        code = "ISC $ABCD"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0xEF, 0xCD, 0xAB]),
        ], results)

    def test_isc_absolute_indexed(self):
        code = "ISC $ABCD,X\n" \
               "ISC $ABCD,Y"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0xFF, 0xCD, 0xAB, 0xFB, 0xCD, 0xAB]),
        ], results)

    def test_isc_indexed_indirect(self):
        code = "ISC ($40,X)"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0xE3, 0x40]),
        ], results)

    def test_isc_indirect_indexed(self):
        code = "ISC ($40),Y"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0xF3, 0x40]),
        ], results)
