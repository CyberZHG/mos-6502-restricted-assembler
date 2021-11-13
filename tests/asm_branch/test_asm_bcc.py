from unittest import TestCase

from asm_6502 import Assembler


class TestAssembleBCC(TestCase):

    def setUp(self) -> None:
        self.assembler = Assembler()

    def test_bcc_accumulator(self):
        code = "BCC *+$10"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0x90, 0x10]),
        ], results)
