from unittest import TestCase

from asm_6502 import Assembler, AssembleError


class TestAssembleSTA(TestCase):

    def setUp(self) -> None:
        self.assembler = Assembler()

    def test_sta_error_immediate(self):
        code = "STA #$00"
        with self.assertRaises(AssembleError) as e:
            self.assembler.assemble(code)
        self.assertEqual("AssembleError: Immediate addressing is not allowed for `STA` at line 1",
                         str(e.exception))

    def test_sta_zero_page(self):
        code = "STA $00"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0x85, 0x00]),
        ], results)

    def test_sta_zero_page_x(self):
        code = "STA $10,X"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0x95, 0x10]),
        ], results)

    def test_sta_absolute(self):
        code = "STA $ABCD"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0x8D, 0xCD, 0xAB]),
        ], results)

    def test_sta_absolute_indexed(self):
        code = "STA $ABCD,X\n" \
               "STA $ABCD,Y"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0x9D, 0xCD, 0xAB, 0x99, 0xCD, 0xAB]),
        ], results)

    def test_sta_indexed_indirect(self):
        code = "STA ($40,X)"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0x81, 0x40]),
        ], results)

    def test_sta_indirect_indexed(self):
        code = "STA ($40),Y"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0x91, 0x40]),
        ], results)
