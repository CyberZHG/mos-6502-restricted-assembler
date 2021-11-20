from unittest import TestCase

from asm_6502 import Assembler


class TestAssembleBNE(TestCase):

    def setUp(self) -> None:
        self.assembler = Assembler()

    def test_bne_relative(self):
        code = "BNE *+$10"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0xD0, 0x0E]),
        ], results)
