from unittest import TestCase

from asm_6502 import Assembler


class TestAssembleTXA(TestCase):

    def setUp(self) -> None:
        self.assembler = Assembler()

    def test_txa_implied(self):
        code = "TXA"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0x8A]),
        ], results)
