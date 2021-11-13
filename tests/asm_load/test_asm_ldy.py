from unittest import TestCase

from asm_6502 import Assembler, AssembleError


class TestAssembleLDY(TestCase):

    def setUp(self) -> None:
        self.assembler = Assembler()

    def test_ldy_immediate(self):
        code = "LDY #10"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0xA0, 0x0A]),
        ], results)

    def test_ldy_zero_page(self):
        code = "LDY $10"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0xA4, 0x10]),
        ], results)

    def test_ldy_zero_page_x(self):
        code = "LDY $10,X"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0xB4, 0x10]),
        ], results)

    def test_ldy_zero_page_y(self):
        code = "LDY $10,Y"
        with self.assertRaises(AssembleError) as e:
            self.assembler.assemble(code)
        self.assertEqual("AssembleError: Can not use Y as the index register in LDY at line 1",
                         str(e.exception))

    def test_ldy_absolute(self):
        code = "LDY $ABCD"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0xAC, 0xCD, 0xAB]),
        ], results)

    def test_ldy_absolute_indexed(self):
        code = "LDY $ABCD,X"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0xBC, 0xCD, 0xAB]),
        ], results)
