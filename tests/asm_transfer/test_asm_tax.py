from unittest import TestCase

from asm_6502 import Assembler


class TestAssembleTAX(TestCase):

    def setUp(self) -> None:
        self.assembler = Assembler()

    def test_tax_implied(self):
        code = "TAX"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0xAA]),
        ], results)
