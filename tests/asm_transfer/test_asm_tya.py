from unittest import TestCase

from asm_6502 import Assembler


class TestAssembleTYA(TestCase):

    def setUp(self) -> None:
        self.assembler = Assembler()

    def test_tya_implied(self):
        code = "TYA"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0x98]),
        ], results)
