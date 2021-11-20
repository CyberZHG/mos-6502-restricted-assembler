from unittest import TestCase

from asm_6502 import Assembler


class TestAssembleBRK(TestCase):

    def setUp(self) -> None:
        self.assembler = Assembler()

    def test_brk(self):
        code = "BRK"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0x00, 0x00]),
        ], results)
