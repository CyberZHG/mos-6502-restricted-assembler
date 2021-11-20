from unittest import TestCase

from asm_6502 import Assembler


class TestAssembleANC(TestCase):

    def setUp(self) -> None:
        self.assembler = Assembler()

    def test_anc_immediate(self):
        code = "ANC #$10"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0x0B, 0x10]),
        ], results)
