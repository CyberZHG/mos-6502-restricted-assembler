from unittest import TestCase

from asm_6502 import Assembler


class TestAssembleARR(TestCase):

    def setUp(self) -> None:
        self.assembler = Assembler()

    def test_arr_immediate(self):
        code = "ARR #$10"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0x6B, 0x10]),
        ], results)
