from unittest import TestCase

from asm_6502 import Assembler


class TestAssembleBMI(TestCase):

    def setUp(self) -> None:
        self.assembler = Assembler()

    def test_bmi_relative(self):
        code = "BMI *+$10"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0x30, 0x0E]),
        ], results)
