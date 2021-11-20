from unittest import TestCase

from asm_6502 import Assembler


class TestAssembleSEC(TestCase):

    def setUp(self) -> None:
        self.assembler = Assembler()

    def test_sec(self):
        code = "SEC"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0x38]),
        ], results)
