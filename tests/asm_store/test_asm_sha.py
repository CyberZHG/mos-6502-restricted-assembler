from unittest import TestCase

from asm_6502 import Assembler, AssembleError


class TestAssembleSHA(TestCase):

    def setUp(self) -> None:
        self.assembler = Assembler()

    def test_sha_absolute_x(self):
        code = "SHA $1000,X"
        with self.assertRaises(AssembleError) as e:
            self.assembler.assemble(code)
        self.assertEqual("AssembleError: Can not use X as the index register in SHA at line 1",
                         str(e.exception))

    def test_sha_absolute_y(self):
        code = "SHA $ABCD,Y"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0x9F, 0xCD, 0xAB]),
        ], results)

    def test_sha_indirect_indexed(self):
        code = "SHA ($AB),Y"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0000, [0x93, 0xAB]),
        ], results)
