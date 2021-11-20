from unittest import TestCase

from asm_6502 import Assembler


class TestAssembleSEI(TestCase):

    def setUp(self) -> None:
        self.assembler = Assembler()

    def test_sei(self):
        code = "SEI"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0x78]),
        ], results)
