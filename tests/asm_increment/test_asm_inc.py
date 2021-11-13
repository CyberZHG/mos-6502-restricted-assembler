from unittest import TestCase

from asm_6502 import Assembler, AssembleError


class TestAssembleINC(TestCase):

    def setUp(self) -> None:
        self.assembler = Assembler()

    def test_inc_zero_page(self):
        code = "INC $10"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0xE6, 0x10]),
        ], results)

    def test_inc_zero_page_x(self):
        code = "INC $10,X"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0xF6, 0x10]),
        ], results)

    def test_inc_zero_page_y(self):
        code = "INC $10,Y"
        with self.assertRaises(AssembleError) as e:
            self.assembler.assemble(code)
        self.assertEqual("AssembleError: Can not use Y as the index register in INC at line 1",
                         str(e.exception))

    def test_inc_absolute(self):
        code = "INC $ABCD"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0xEE, 0xCD, 0xAB]),
        ], results)

    def test_inc_absolute_indexed_x(self):
        code = "INC $ABCD,X"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0xFE, 0xCD, 0xAB]),
        ], results)

    def test_inc_absolute_indexed_y(self):
        code = "INC $ABCD,Y"
        with self.assertRaises(AssembleError) as e:
            self.assembler.assemble(code)
        self.assertEqual("AssembleError: Can not use Y as the index register in INC at line 1",
                         str(e.exception))
