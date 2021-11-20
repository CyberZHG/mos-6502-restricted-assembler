from unittest import TestCase

from asm_6502 import Assembler


class TestAssembleSED(TestCase):

    def setUp(self) -> None:
        self.assembler = Assembler()

    def test_sed(self):
        code = "SED"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0xF8]),
        ], results)
