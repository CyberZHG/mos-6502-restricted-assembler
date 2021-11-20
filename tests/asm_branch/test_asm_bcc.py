from unittest import TestCase

from asm_6502 import Assembler, AssembleError


class TestAssembleBCC(TestCase):

    def setUp(self) -> None:
        self.assembler = Assembler()

    def test_bcc_relative(self):
        code = "BCC *+$10"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0x90, 0x0E]),
        ], results)

    def test_bcc_relative_neg(self):
        code = "ORG $0800\n" \
               "BCC *-$7E"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0800, [0x90, 0x80]),
        ], results)

    def test_bcc_relative_neg_invalid(self):
        code = "ORG $0800\n" \
               "BCC *-$7F"
        with self.assertRaises(AssembleError) as e:
            self.assembler.assemble(code)
        self.assertEqual("AssembleError: The offset -0x81 is out of range for relative addressing at line 2",
                         str(e.exception))

    def test_bcc_relative_pos(self):
        code = "ORG $0800\n" \
               "BCC *+$81"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0800, [0x90, 0x7F]),
        ], results)

    def test_bcc_relative_pos_invalid(self):
        code = "ORG $0800\n" \
               "BCC *+$82"
        with self.assertRaises(AssembleError) as e:
            self.assembler.assemble(code)
        self.assertEqual("AssembleError: The offset 0x80 is out of range for relative addressing at line 2",
                         str(e.exception))
