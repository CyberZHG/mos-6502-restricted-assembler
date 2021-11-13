from unittest import TestCase

from asm_6502 import Assembler


class TestAssembleORA(TestCase):

    def setUp(self) -> None:
        self.assembler = Assembler()

    def test_ora_immediate(self):
        code = "ORA #$10"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0x09, 0x10]),
        ], results)

    def test_ora_zero_page(self):
        code = "ORA $10"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0x05, 0x10]),
        ], results)

    def test_ora_zero_page_x(self):
        code = "ORA $10,X"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0x15, 0x10]),
        ], results)

    def test_ora_absolute(self):
        code = "ORA $ABCD"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0x0D, 0xCD, 0xAB]),
        ], results)

    def test_ora_absolute_indexed(self):
        code = "ORA $ABCD,X\n" \
               "ORA $ABCD,Y"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0x1D, 0xCD, 0xAB, 0x19, 0xCD, 0xAB]),
        ], results)

    def test_ora_indexed_indirect(self):
        code = "ORA ($10,X)"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0x01, 0x10]),
        ], results)

    def test_ora_indirect_indexed(self):
        code = "ORA ($10),Y"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0x11, 0x10]),
        ], results)
