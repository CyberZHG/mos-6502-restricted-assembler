from unittest import TestCase

from asm_6502 import Assembler


class TestAssemblePLA(TestCase):

    def setUp(self) -> None:
        self.assembler = Assembler()

    def test_pla_implied(self):
        code = "PLA"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0x68]),
        ], results)
