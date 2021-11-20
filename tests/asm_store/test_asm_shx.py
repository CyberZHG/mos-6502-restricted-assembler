from unittest import TestCase

from asm_6502 import Assembler


class TestAssembleSHX(TestCase):

    def setUp(self) -> None:
        self.assembler = Assembler()

    def test_shx_absolute_y(self):
        code = "SHX $ABCD,Y"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0x9E, 0xCD, 0xAB]),
        ], results)
