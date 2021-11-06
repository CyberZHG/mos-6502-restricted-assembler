from unittest import TestCase

from asm_6502 import Assembler, AssembleError


class TestAssembleLDA(TestCase):

    def setUp(self) -> None:
        self.assembler = Assembler()

    def test_lda_immediate(self):
        code = "ORG $0080\n" \
               "LDA #10"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0080, [0xA9, 0x0A]),
        ], results)

    def test_lda_immediate_too_large(self):
        code = "ORG $0080\n" \
               "LDA #$ABCD"
        with self.assertRaises(AssembleError) as e:
            self.assembler.assemble(code)
        self.assertEqual("AssembleError: The value 0xabcd is too large for the addressing at line 2",
                         str(e.exception))

    def test_lda_immediate_low(self):
        code = "START ORG $ABCD\n" \
               "      LDA #LO START"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0xABCD, [0xA9, 0xCD]),
        ], results)

        code = "LDA #LO $ABCD"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0xA9, 0xCD]),
        ], results)

    def test_lda_immediate_high(self):
        code = "START ORG $ABCD\n" \
               "      LDA #HI START"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0xABCD, [0xA9, 0xAB]),
        ], results)

    def test_lda_zero_page(self):
        code = "LDA $00\n" \
               "LDA $00"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0xA5, 0x00, 0xA5, 0x00]),
        ], results)

        code = "START LDA START"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0xAD, 0x00, 0x00]),
        ], results)

        code = "ORG $ABCD\n" \
               "LDA *-*"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0xABCD, [0xAD, 0x00, 0x00]),
        ], results)

        code = "ORG $ABCD\n" \
               "LDA -*--*"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0xABCD, [0xAD, 0x00, 0x00]),
        ], results)

        code = "LDA *+255"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0xAD, 0xFF, 0x00]),
        ], results)

    def test_lda_zero_page_x(self):
        code = "LDA $10,X\n" \
               "LDA $10,X"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0xB5, 0x10, 0xB5, 0x10]),
        ], results)

    def test_lda_absolute(self):
        code = "LDA $ABCD\n" \
               "LDA $ABCD"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0xAD, 0xCD, 0xAB, 0xAD, 0xCD, 0xAB]),
        ], results)

        code = "LDA $00CD\n" \
               "LDA $00CD"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0xAD, 0xCD, 0x00, 0xAD, 0xCD, 0x00]),
        ], results)

        code = "LDA $FF+10-10"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0xAD, 0xFF, 0x00]),
        ], results)

    def test_lda_absolute_indexed(self):
        code = "LDA $ABCD,X\n" \
               "LDA $ABCD,Y"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0xBD, 0xCD, 0xAB, 0xB9, 0xCD, 0xAB]),
        ], results)

        code = "LDA $10,X\n" \
               "LDA $10,Y"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0xB5, 0x10, 0xB9, 0x10, 0x00]),
        ], results)

        code = "LDA $0010,X\n" \
               "LDA $0010,Y"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0xBD, 0x10, 0x00, 0xB9, 0x10, 0x00]),
        ], results)

    def test_lda_indexed_indirect(self):
        code = "LDA ($40,X)"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0xA1, 0x40]),
        ], results)

    def test_lda_indirect_indexed(self):
        code = "LDA ($40),Y"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0xB1, 0x40]),
        ], results)
