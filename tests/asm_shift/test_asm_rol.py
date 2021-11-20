from unittest import TestCase

from asm_6502 import Assembler


class TestAssembleROL(TestCase):

    def setUp(self) -> None:
        self.assembler = Assembler()

    def test_rol_accumulator(self):
        code = "ROL A"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0x2A]),
        ], results)

    def test_rol_zero_page(self):
        code = "ROL $10"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0x26, 0x10]),
        ], results)

    def test_rol_zero_page_x(self):
        code = "ROL $10,X"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0x36, 0x10]),
        ], results)

    def test_rol_absolute(self):
        code = "ROL $ABCD"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0x2E, 0xCD, 0xAB]),
        ], results)

    def test_rol_absolute_indexed_x(self):
        code = "ROL $ABCD,X"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0x3E, 0xCD, 0xAB]),
        ], results)
