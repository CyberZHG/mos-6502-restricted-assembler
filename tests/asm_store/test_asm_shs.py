from unittest import TestCase

from asm_6502 import Assembler


class TestAssembleSHS(TestCase):

    def setUp(self) -> None:
        self.assembler = Assembler()

    def test_shs_absolute_y(self):
        code = "SHS $ABCD,Y"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0x9B, 0xCD, 0xAB]),
        ], results)
