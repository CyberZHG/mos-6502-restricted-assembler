from unittest import TestCase

from asm_6502 import Assembler


class TestAssembleJSR(TestCase):

    def setUp(self) -> None:
        self.assembler = Assembler()

    def test_jsr_absolute(self):
        code = "START ORG $0080\n" \
               "START ORG $0800\n" \
               "      JSR START"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0800, [0x20, 0x00, 0x08]),
        ], results)
