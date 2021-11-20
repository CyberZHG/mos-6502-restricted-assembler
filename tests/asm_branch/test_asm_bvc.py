from unittest import TestCase

from asm_6502 import Assembler


class TestAssembleBVC(TestCase):

    def setUp(self) -> None:
        self.assembler = Assembler()

    def test_bvc_accumulator(self):
        code = "BVC *+$10"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0x50, 0x10]),
        ], results)
