from unittest import TestCase

from asm_6502 import Assembler


class TestAssembleJAM(TestCase):

    def setUp(self) -> None:
        self.assembler = Assembler()

    def test_jam(self):
        code = "JAM"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0x02]),
        ], results)
