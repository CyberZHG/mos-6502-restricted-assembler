from unittest import TestCase

from asm_6502 import Assembler


class TestAssembleRTI(TestCase):

    def setUp(self) -> None:
        self.assembler = Assembler()

    def test_rti(self):
        code = "RTI"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0x40]),
        ], results)
