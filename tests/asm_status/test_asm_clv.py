from unittest import TestCase

from asm_6502 import Assembler


class TestAssembleCLV(TestCase):

    def setUp(self) -> None:
        self.assembler = Assembler()

    def test_clv(self):
        code = "CLV"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0xB8]),
        ], results)
