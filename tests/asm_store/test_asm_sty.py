from unittest import TestCase

from asm_6502 import Assembler, AssembleError


class TestAssembleSTY(TestCase):

    def setUp(self) -> None:
        self.assembler = Assembler()

    def test_sty_zero_page(self):
        code = "STY $10"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0x84, 0x10]),
        ], results)

    def test_sty_zero_page_x(self):
        code = "STY $10,X"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0x94, 0x10]),
        ], results)

    def test_sty_zero_page_y(self):
        code = "STY $10,Y"
        with self.assertRaises(AssembleError) as e:
            self.assembler.assemble(code)
        self.assertEqual("AssembleError: Can not use Y as the index register in STY at line 1",
                         str(e.exception))

    def test_sty_absolute(self):
        code = "STY $ABCD"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0x8C, 0xCD, 0xAB]),
        ], results)

    def test_sty_absolute_indexed(self):
        code = "STY $ABCD,X"
        with self.assertRaises(AssembleError) as e:
            self.assembler.assemble(code)
        self.assertEqual("AssembleError: Absolute indexed addressing is not allowed for STY at line 1",
                         str(e.exception))
