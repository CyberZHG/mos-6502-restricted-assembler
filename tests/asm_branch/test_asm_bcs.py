from unittest import TestCase

from asm_6502 import Assembler


class TestAssembleBCS(TestCase):

    def setUp(self) -> None:
        self.assembler = Assembler()

    def test_bcs_relative(self):
        code = "BCS *+$10"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0xB0, 0x0E]),
        ], results)
