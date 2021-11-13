from unittest import TestCase

from asm_6502 import Assembler


class TestAssemblePHP(TestCase):

    def setUp(self) -> None:
        self.assembler = Assembler()

    def test_php_implied(self):
        code = "PHP"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0x08]),
        ], results)
