from unittest import TestCase

from asm_6502 import Assembler


class TestAssembleCLI(TestCase):

    def setUp(self) -> None:
        self.assembler = Assembler()

    def test_cli(self):
        code = "CLI"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0x58]),
        ], results)
