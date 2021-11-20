from unittest import TestCase

from asm_6502 import Assembler


class TestAssembleDEX(TestCase):

    def setUp(self) -> None:
        self.assembler = Assembler()

    def test_dex_implied(self):
        code = "DEX"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0xCA]),
        ], results)
