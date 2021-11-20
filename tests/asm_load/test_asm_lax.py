from unittest import TestCase

from asm_6502 import Assembler, AssembleError


class TestAssembleLAX(TestCase):

    def setUp(self) -> None:
        self.assembler = Assembler()

    def test_lax_immediate(self):
        code = "ORG $0080\n" \
               "LAX #10"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0080, [0xAB, 0x0A]),
        ], results)

    def test_lax_zero_page(self):
        code = "LAX $00"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0xA7, 0x00]),
        ], results)

    def test_ldx_zero_page_x(self):
        code = "LAX $10,X"
        with self.assertRaises(AssembleError) as e:
            self.assembler.assemble(code)
        self.assertEqual("AssembleError: Can not use X as the index register in LAX at line 1",
                         str(e.exception))

    def test_lax_zero_page_y(self):
        code = "LAX $10,Y"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0xB7, 0x10]),
        ], results)

    def test_lax_absolute(self):
        code = "LAX $ABCD"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0xAF, 0xCD, 0xAB]),
        ], results)

    def test_lax_absolute_y(self):
        code = "LAX $ABCD,Y"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0xBF, 0xCD, 0xAB]),
        ], results)

    def test_lax_indexed_indirect(self):
        code = "LAX ($40,X)"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0xA3, 0x40]),
        ], results)

    def test_lax_indirect_indexed(self):
        code = "LAX ($40),Y"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0xB3, 0x40]),
        ], results)
