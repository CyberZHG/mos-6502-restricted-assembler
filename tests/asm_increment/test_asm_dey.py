from unittest import TestCase

from asm_6502 import Assembler


class TestAssembleDEY(TestCase):

    def setUp(self) -> None:
        self.assembler = Assembler()

    def test_dey_implied(self):
        code = "DEY"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0x88]),
        ], results)
