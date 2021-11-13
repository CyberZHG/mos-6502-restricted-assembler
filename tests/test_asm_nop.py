from unittest import TestCase

from asm_6502 import Assembler, AssembleError


class TestAssembleNOP(TestCase):

    def setUp(self) -> None:
        self.assembler = Assembler()

    def test_nop(self):
        code = "NOP"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0xEA]),
        ], results)
