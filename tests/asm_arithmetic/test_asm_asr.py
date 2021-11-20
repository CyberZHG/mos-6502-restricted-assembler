from unittest import TestCase

from asm_6502 import Assembler


class TestAssembleASR(TestCase):

    def setUp(self) -> None:
        self.assembler = Assembler()

    def test_asr_immediate(self):
        code = "ASR #$10"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0x4B, 0x10]),
        ], results)
