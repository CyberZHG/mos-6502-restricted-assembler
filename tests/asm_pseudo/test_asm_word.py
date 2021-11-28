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

    def test_word_with_arithmetic(self):
        code = ".ORG $1000\n" \
               ".WORD *+3"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x1000, [0x03, 0x10]),
        ], results)

    def test_words(self):
        code = ".ORG $1000\n" \
               ".WORD $ABCD, $EF42"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x1000, [0xCD, 0xAB, 0x42, 0xEF]),
        ], results)
