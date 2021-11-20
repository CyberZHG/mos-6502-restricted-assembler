from unittest import TestCase

from asm_6502 import Assembler


class TestAssembleCLD(TestCase):

    def setUp(self) -> None:
        self.assembler = Assembler()

    def test_cld(self):
        code = "CLD"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0xD8]),
        ], results)
