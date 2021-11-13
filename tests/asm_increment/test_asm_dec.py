from unittest import TestCase

from asm_6502 import Assembler, AssembleError


class TestAssembleDEC(TestCase):

    def setUp(self) -> None:
        self.assembler = Assembler()

    def test_dec_zero_page(self):
        code = "DEC $10"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0xC6, 0x10]),
        ], results)

    def test_dec_zero_page_x(self):
        code = "DEC $10,X"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0xD6, 0x10]),
        ], results)

    def test_dec_zero_page_y(self):
        code = "DEC $10,Y"
        with self.assertRaises(AssembleError) as e:
            self.assembler.assemble(code)
        self.assertEqual("AssembleError: Can not use Y as the index register in DEC at line 1",
                         str(e.exception))

    def test_dec_absolute(self):
        code = "DEC $ABCD"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0xCE, 0xCD, 0xAB]),
        ], results)

    def test_dec_absolute_indexed_x(self):
        code = "DEC $ABCD,X"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0xDE, 0xCD, 0xAB]),
        ], results)

    def test_dec_absolute_indexed_y(self):
        code = "DEC $ABCD,Y"
        with self.assertRaises(AssembleError) as e:
            self.assembler.assemble(code)
        self.assertEqual("AssembleError: Can not use Y as the index register in DEC at line 1",
                         str(e.exception))
