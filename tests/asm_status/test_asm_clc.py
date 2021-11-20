from unittest import TestCase

from asm_6502 import Assembler


class TestAssembleCLC(TestCase):

    def setUp(self) -> None:
        self.assembler = Assembler()

    def test_clc(self):
        code = "CLC"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0x18]),
        ], results)
