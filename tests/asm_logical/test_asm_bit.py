from unittest import TestCase

from asm_6502 import Assembler


class TestAssembleBIT(TestCase):

    def setUp(self) -> None:
        self.assembler = Assembler()

    def test_bit_zero_page(self):
        code = "BIT $10"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0x24, 0x10]),
        ], results)

    def test_bit_absolute(self):
        code = "BIT $ABCD"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0x2C, 0xCD, 0xAB]),
        ], results)
