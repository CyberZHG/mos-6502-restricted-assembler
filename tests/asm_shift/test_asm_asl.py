from unittest import TestCase

from asm_6502 import Assembler, AssembleError


class TestAssembleASL(TestCase):

    def setUp(self) -> None:
        self.assembler = Assembler()

    def test_asl_accumulator(self):
        code = "ASL A"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0x0A]),
        ], results)

    def test_asl_zero_page(self):
        code = "ASL $10"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0x06, 0x10]),
        ], results)

    def test_asl_zero_page_x(self):
        code = "ASL $10,X"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0x16, 0x10]),
        ], results)

    def test_asl_zero_page_y(self):
        code = "ASL $10,Y"
        with self.assertRaises(AssembleError) as e:
            self.assembler.assemble(code)
        self.assertEqual("AssembleError: Can not use Y as the index register in ASL at line 1",
                         str(e.exception))

    def test_asl_absolute(self):
        code = "ASL $ABCD"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0x0E, 0xCD, 0xAB]),
        ], results)

    def test_asl_absolute_indexed_x(self):
        code = "ASL $ABCD,X"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0x1E, 0xCD, 0xAB]),
        ], results)

    def test_asl_absolute_indexed_y(self):
        code = "ASL $ABCD,Y"
        with self.assertRaises(AssembleError) as e:
            self.assembler.assemble(code)
        self.assertEqual("AssembleError: Can not use Y as the index register in ASL at line 1",
                         str(e.exception))
