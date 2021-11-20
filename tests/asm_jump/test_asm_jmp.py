from unittest import TestCase

from asm_6502 import Assembler, AssembleError


class TestAssembleJMP(TestCase):

    def setUp(self) -> None:
        self.assembler = Assembler()

    def test_jmp_absolute(self):
        code = "ORG $0080\n" \
               "JMP $0080"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0080, [0x4C, 0x80, 0x00]),
        ], results)

        code = "START ORG $0080\n" \
               "      JMP START"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0080, [0x4C, 0x80, 0x00]),
        ], results)

    def test_jmp_indirect(self):
        code = "START ORG $0080\n" \
               "      JMP (START)\n" \
               "      ORG $FFFF"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0080, [0x6C, 0x80, 0x00]),
        ], results)

    def test_jmp_error_addressing(self):
        code = "JMP ($0080),Y"
        with self.assertRaises(AssembleError) as e:
            self.assembler.assemble(code)
        self.assertEqual("AssembleError: Indirect indexed addressing is not allowed for `JMP` at line 1",
                         str(e.exception))

    def test_jmp_unknown_label(self):
        code = "JMP START"
        with self.assertRaises(AssembleError) as e:
            self.assembler.assemble(code)
        self.assertEqual("AssembleError(\"Can not resolve label 'START' at line 1\")",
                         repr(e.exception))

    def test_jmp_out_of_memory(self):
        code = "START ORG $FFFF\n" \
               "      JMP (START)"
        with self.assertRaises(AssembleError) as e:
            self.assembler.assemble(code)
        self.assertEqual("AssembleError: The assembled code will exceed the max memory 0x10000 at line 2",
                         str(e.exception))

    def test_jmp_with_entry(self):
        code = "ORG $0080\n" \
               "JMP $abcd"
        results = self.assembler.assemble(code)
        self.assertEqual([
            (0x0080, [0x4C, 0xcd, 0xab]),
            (0xFFFC, [0x80, 0x00]),
        ], results)

        code = "START ORG $0080\n" \
               "NEXT  JMP $abcd"
        results = self.assembler.assemble(code)
        self.assertEqual([
            (0x0080, [0x4C, 0xcd, 0xab]),
            (0xFFFC, [0x80, 0x00]),
        ], results)

    def test_jmp_dead_loop(self):
        code = "ORG $0080\n" \
               "JMP *"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0080, [0x4C, 0x80, 0x00]),
        ], results)

    def test_jmp_add(self):
        code = "ORG $0080\n" \
               "JMP *+3"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0080, [0x4C, 0x83, 0x00]),
        ], results)

    def test_jmp_sub(self):
        code = "ORG $0080\n" \
               "JMP *-3"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0080, [0x4C, 0x7D, 0x00]),
        ], results)

    def test_jmp_mul(self):
        code = "ORG $0080\n" \
               "JMP ***"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0080, [0x4C, 0x00, 0x40]),
        ], results)

    def test_jmp_div(self):
        code = "START ORG $0080\n" \
               "      JMP */START"
        results = self.assembler.assemble(code, add_entry=False)
        self.assertEqual([
            (0x0080, [0x4C, 0x01, 0x00]),
        ], results)
