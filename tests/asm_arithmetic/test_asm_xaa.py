from unittest import TestCase

from asm_6502 import Assembler


class TestAssembleXAA(TestCase):

    def setUp(self) -> None:
        self.assembler = Assembler()

    def test_xaa_immediate(self):
        code = "XAA #$10"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0x8B, 0x10]),
        ], results)
