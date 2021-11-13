from unittest import TestCase

from asm_6502 import Assembler


class TestAssembleTXS(TestCase):

    def setUp(self) -> None:
        self.assembler = Assembler()

    def test_txs_implied(self):
        code = "TXS"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0x9A]),
        ], results)
