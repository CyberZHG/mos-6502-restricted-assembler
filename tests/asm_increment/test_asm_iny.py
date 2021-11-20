from unittest import TestCase

from asm_6502 import Assembler


class TestAssembleINY(TestCase):

    def setUp(self) -> None:
        self.assembler = Assembler()

    def test_iny_implied(self):
        code = "INY"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0xC8]),
        ], results)
