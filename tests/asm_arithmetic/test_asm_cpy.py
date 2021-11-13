from unittest import TestCase

from asm_6502 import Assembler


class TestAssembleCPY(TestCase):

    def setUp(self) -> None:
        self.assembler = Assembler()

    def test_cpy_immediate(self):
        code = "CPY #$10"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0xC0, 0x10]),
        ], results)

    def test_cpy_zero_page(self):
        code = "CPY $10"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0xC4, 0x10]),
        ], results)

    def test_cpy_absolute(self):
        code = "CPY $ABCD"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0xCC, 0xCD, 0xAB]),
        ], results)
