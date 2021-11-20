from unittest import TestCase

from asm_6502 import Assembler, AssembleError


class TestAssembleSAX(TestCase):

    def setUp(self) -> None:
        self.assembler = Assembler()

    def test_sax_zero_page(self):
        code = "SAX $10"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0x87, 0x10]),
        ], results)

    def test_sax_zero_page_x(self):
        code = "SAX $10,X"
        with self.assertRaises(AssembleError) as e:
            self.assembler.assemble(code)
        self.assertEqual("AssembleError: Can not use X as the index register in SAX at line 1",
                         str(e.exception))

    def test_sax_zero_page_y(self):
        code = "SAX $10,Y"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0x97, 0x10]),
        ], results)

    def test_sax_absolute(self):
        code = "SAX $ABCD"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0x8F, 0xCD, 0xAB]),
        ], results)

    def test_sax_absolute_indexed(self):
        code = "SAX $ABCD,Y"
        with self.assertRaises(AssembleError) as e:
            self.assembler.assemble(code)
        self.assertEqual("AssembleError: Absolute indexed addressing is not allowed for SAX at line 1",
                         str(e.exception))

    def test_sax_indexed_indirect(self):
        code = "SAX ($AB,X)"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0x83, 0xAB]),
        ], results)
