from unittest import TestCase

from asm_6502 import Assembler


class TestAssembleADC(TestCase):

    def setUp(self) -> None:
        self.assembler = Assembler()

    def test_adc_immediate(self):
        code = "ADC #$10"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0x69, 0x10]),
        ], results)

    def test_adc_zero_page(self):
        code = "ADC $10"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0x65, 0x10]),
        ], results)

    def test_adc_zero_page_x(self):
        code = "ADC $10,X"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0x75, 0x10]),
        ], results)

    def test_adc_absolute(self):
        code = "ADC $ABCD"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0x6D, 0xCD, 0xAB]),
        ], results)

    def test_adc_absolute_indexed(self):
        code = "ADC $ABCD,X\n" \
               "ADC $ABCD,Y"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0x7D, 0xCD, 0xAB, 0x79, 0xCD, 0xAB]),
        ], results)

    def test_adc_indexed_indirect(self):
        code = "ADC ($10,X)"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0x61, 0x10]),
        ], results)

    def test_adc_indirect_indexed(self):
        code = "ADC ($10),Y"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0x71, 0x10]),
        ], results)
