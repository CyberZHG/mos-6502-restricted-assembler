from unittest import TestCase

from asm_6502 import Assembler


class TestAssembleEND(TestCase):

    def setUp(self) -> None:
        self.assembler = Assembler()

    def test_end(self):
        code = ".ORG $1000\n" \
               ".END"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x1000, [0x4C, 0x00, 0x10]),
        ], results)
