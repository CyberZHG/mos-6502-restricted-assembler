from unittest import TestCase

from asm_6502 import Assembler


class TestAssembleINX(TestCase):

    def setUp(self) -> None:
        self.assembler = Assembler()

    def test_inx_implied(self):
        code = "INX"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0xE8]),
        ], results)
