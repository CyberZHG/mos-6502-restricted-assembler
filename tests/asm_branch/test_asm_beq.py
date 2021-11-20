from unittest import TestCase

from asm_6502 import Assembler


class TestAssembleBEQ(TestCase):

    def setUp(self) -> None:
        self.assembler = Assembler()

    def test_beq_relative(self):
        code = "BEQ *+$10"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0xF0, 0x0E]),
        ], results)
