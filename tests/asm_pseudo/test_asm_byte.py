from unittest import TestCase

from asm_6502 import Assembler, AssembleError


class TestAssembleBYTE(TestCase):

    def setUp(self) -> None:
        self.assembler = Assembler()

    def test_byte(self):
        code = ".ORG $1000\n" \
               ".BYTE $AB"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x1000, [0xAB]),
        ], results)

    def test_byte_too_large(self):
        code = ".ORG $1000\n" \
               ".BYTE $ABCD"
        with self.assertRaises(AssembleError) as e:
            self.assembler.assemble(code)
        self.assertEqual("AssembleError: 0xabcd can not fit in a byte at line 2", str(e.exception))

    def test_bytes(self):
        code = ".ORG $1000\n" \
               ".BYTE $AB,$CD+1"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x1000, [0xAB, 0xCD + 1]),
        ], results)

        code = ".ORG $1000\n" \
               ".BYTE $AB,$CD+1,$EF"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x1000, [0xAB, 0xCD + 1, 0xEF]),
        ], results)

    def test_bytes_too_large(self):
        code = ".ORG $1000\n" \
               ".BYTE $AB,$CD+$EF"
        with self.assertRaises(AssembleError) as e:
            self.assembler.assemble(code)
        self.assertEqual("AssembleError: 0x1bc can not fit in a byte at line 2", str(e.exception))
