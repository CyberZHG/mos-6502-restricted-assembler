from unittest import TestCase

from asm_6502 import Assembler, AssembleError


class TestAssembleLDX(TestCase):

    def setUp(self) -> None:
        self.assembler = Assembler()

    def test_ldx_immediate(self):
        code = "LDX #10"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0xA2, 0x0A]),
        ], results)

    def test_ldx_zero_page(self):
        code = "LDX $10"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0xA6, 0x10]),
        ], results)

    def test_ldx_zero_page_x(self):
        code = "LDX $10,X"
        with self.assertRaises(AssembleError) as e:
            self.assembler.assemble(code)
        self.assertEqual("AssembleError: Can not use X as the index register in LDX at line 1",
                         str(e.exception))

    def test_ldx_zero_page_y(self):
        code = "LDX $10,Y"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0xB6, 0x10]),
        ], results)

    def test_ldx_absolute(self):
        code = "LDX $ABCD"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0xAE, 0xCD, 0xAB]),
        ], results)

    def test_ldx_absolute_indexed(self):
        code = "LDX $ABCD,Y"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0xBE, 0xCD, 0xAB]),
        ], results)
