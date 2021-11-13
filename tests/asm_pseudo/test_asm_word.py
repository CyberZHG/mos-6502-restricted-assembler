from unittest import TestCase

from asm_6502 import Assembler, AssembleError


class TestAssembleWORD(TestCase):

    def setUp(self) -> None:
        self.assembler = Assembler()

    def test_word(self):
        code = ".ORG $1000\n" \
               ".WORD $ABCD"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x1000, [0xCD, 0xAB]),
        ], results)
