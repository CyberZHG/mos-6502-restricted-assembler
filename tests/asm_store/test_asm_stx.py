from unittest import TestCase

from asm_6502 import Assembler, AssembleError


class TestAssembleSTX(TestCase):

    def setUp(self) -> None:
        self.assembler = Assembler()

    def test_stx_zero_page(self):
        code = "STX $10"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0x86, 0x10]),
        ], results)

    def test_stx_zero_page_x(self):
        code = "STX $10,X"
        with self.assertRaises(AssembleError) as e:
            self.assembler.assemble(code)
        self.assertEqual("AssembleError: Can not use X as the index register in STX at line 1",
                         str(e.exception))

    def test_stx_zero_page_y(self):
        code = "STX $10,Y"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0x96, 0x10]),
        ], results)

    def test_stx_absolute(self):
        code = "STX $ABCD"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0x8E, 0xCD, 0xAB]),
        ], results)

    def test_stx_absolute_indexed(self):
        code = "STX $ABCD,Y"
        with self.assertRaises(AssembleError) as e:
            self.assembler.assemble(code)
        self.assertEqual("AssembleError: Absolute indexed addressing is not allowed for STX at line 1",
                         str(e.exception))
