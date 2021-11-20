from unittest import TestCase

from asm_6502 import Assembler, AssembleError


class TestAssembleSHY(TestCase):

    def setUp(self) -> None:
        self.assembler = Assembler()

    def test_shy_absolute_x(self):
        code = "SHY $ABCD,X"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0x9C, 0xCD, 0xAB]),
        ], results)

    def test_shy_absolute_y(self):
        code = "SHY $1000,Y"
        with self.assertRaises(AssembleError) as e:
            self.assembler.assemble(code)
        self.assertEqual("AssembleError: Can not use Y as the index register in SHY at line 1",
                         str(e.exception))
