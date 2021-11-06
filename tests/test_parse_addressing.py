from unittest import TestCase

from asm_6502.grammar import get_parser, ADDRESSING, INSTANT, ADDRESS, INTEGER


class TestParseAddressing(TestCase):

    def setUp(self) -> None:
        self.parser = get_parser()

    def test_addressing_accumulator(self):
        code = 'LSR A'
        results = self.parser.parse(code)[0][2]
        self.assertEqual((ADDRESSING.ACCUMULATOR,), results)

    def test_addressing_immediate(self):
        code = 'ORA #$B2'
        results = self.parser.parse(code)[0][2]
        self.assertEqual((ADDRESSING.IMMEDIATE, (INSTANT, (INTEGER, 178))), results)
