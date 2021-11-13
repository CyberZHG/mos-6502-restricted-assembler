from unittest import TestCase

from asm_6502 import Assembler


class TestAssembleTSX(TestCase):

    def setUp(self) -> None:
        self.assembler = Assembler()

    def test_tsx_implied(self):
        code = "TSX"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0xBA]),
        ], results)
