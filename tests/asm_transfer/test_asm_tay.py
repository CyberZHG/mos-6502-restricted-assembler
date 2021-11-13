from unittest import TestCase

from asm_6502 import Assembler


class TestAssembleTAY(TestCase):

    def setUp(self) -> None:
        self.assembler = Assembler()

    def test_tay_implied(self):
        code = "TAY"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0xA8]),
        ], results)
