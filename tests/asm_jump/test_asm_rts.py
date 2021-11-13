from unittest import TestCase

from asm_6502 import Assembler


class TestAssembleRTS(TestCase):

    def setUp(self) -> None:
        self.assembler = Assembler()

    def test_rts_absolute(self):
        code = "START ORG $0080\n" \
               "      RTS\n" \
               "      ORG $0800\n" \
               "      JSR START\n" \
               "      LDA #$10"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0080, [0x60]),
            (0x0800, [0x20, 0x80, 0x00, 0xA9, 0x10]),
        ], results)
