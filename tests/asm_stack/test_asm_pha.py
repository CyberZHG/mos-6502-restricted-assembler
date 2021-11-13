from unittest import TestCase

from asm_6502 import Assembler


class TestAssemblePHA(TestCase):

    def setUp(self) -> None:
        self.assembler = Assembler()

    def test_pha_implied(self):
        code = "PHA"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0x48]),
        ], results)
