from unittest import TestCase

from asm_6502 import Assembler


class TestAssembleBPL(TestCase):

    def setUp(self) -> None:
        self.assembler = Assembler()

    def test_bpl_relative(self):
        code = "BPL *+$10"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0x10, 0x0E]),
        ], results)
