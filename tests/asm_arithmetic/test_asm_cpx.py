from unittest import TestCase

from asm_6502 import Assembler


class TestAssembleCPX(TestCase):

    def setUp(self) -> None:
        self.assembler = Assembler()

    def test_cpx_immediate(self):
        code = "CPX #$10"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0xE0, 0x10]),
        ], results)

    def test_cpx_zero_page(self):
        code = "CPX $10"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0xE4, 0x10]),
        ], results)

    def test_cpx_absolute(self):
        code = "CPX $ABCD"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0xEC, 0xCD, 0xAB]),
        ], results)
