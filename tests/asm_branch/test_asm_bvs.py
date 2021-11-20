from unittest import TestCase

from asm_6502 import Assembler


class TestAssembleBVS(TestCase):

    def setUp(self) -> None:
        self.assembler = Assembler()

    def test_bvs_relative(self):
        code = "BVS *+$10"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0x70, 0x0E]),
        ], results)
