from unittest import TestCase

from asm_6502 import Assembler


class TestAssembleSBX(TestCase):

    def setUp(self) -> None:
        self.assembler = Assembler()

    def test_sbx_immediate(self):
        code = "SBX #$10"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0xCB, 0x10]),
        ], results)
