from unittest import TestCase

from asm_6502 import Assembler, AssembleError


class TestAssembleNOP(TestCase):

    def setUp(self) -> None:
        self.assembler = Assembler()

    def test_nop_implied(self):
        code = "NOP"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0xEA]),
        ], results)

    def test_nop_immediate_undocumented(self):
        code = "NOP #$10"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0x80, 0x10]),
        ], results)

    def test_nop_zero_page_undocumented(self):
        code = "NOP $10"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0x04, 0x10]),
        ], results)

    def test_nop_zero_page_x_undocumented(self):
        code = "NOP $10,X"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0x14, 0x10]),
        ], results)

    def test_nop_absolute_undocumented(self):
        code = "NOP $ABCD"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0x0C, 0xCD, 0xAB]),
        ], results)

    def test_nop_absolute_x_undocumented(self):
        code = "NOP $ABCD,X"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0x1C, 0xCD, 0xAB]),
        ], results)

    def test_nop_absolute_y_undocumented(self):
        code = "NOP $ABCD,Y"
        with self.assertRaises(AssembleError) as e:
            self.assembler.assemble(code)
        self.assertEqual("AssembleError: Can not use Y as the index register in NOP at line 1",
                         str(e.exception))
