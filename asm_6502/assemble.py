from typing import Union, List, Iterable
from functools import wraps

from .grammar import get_parser, Integer, Addressing, Arithmetic, Instruction


__all__ = ['Assembler', 'AssembleError']


class AssembleError(Exception):

    def __init__(self, info, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.info = info

    def __str__(self):
        return f'AssembleError: {self.info}'

    def __repr__(self):
        return f'AssembleError("{self.info}")'


class Assembler(object):

    def __init__(self, max_memory=0x10000, program_entry=0xfffc):
        self.max_memory = max_memory
        self.program_entry = program_entry

        self.code_start = -1  # The offset of the first instruction that can be executed
        self.code_offset = 0  # Current offset
        self.line_number = -1  # Current line number
        self.code_offsets = []  # The offsets of all the instructions
        self.fit_zero_pages = []  # Whether the addresses fit zero-page
        self.label_offsets = {}  # The resolved labels
        self.codes = []  # The generated codes

    def reset(self):
        self.code_start = -1
        self.code_offset = 0
        self.line_number = -1
        self.code_offsets = []
        self.fit_zero_pages = []
        self.label_offsets = {}
        self.codes = []

    def assemble(self,
                 instructions: Union[str, List],
                 add_entry: bool = True):
        if isinstance(instructions, str):
            parser = get_parser()
            instructions = parser.parse(instructions)
        # Preprocess and calculate offsets
        self.reset()
        for i, inst in enumerate(instructions):
            self.line_number = inst.line_num
            if inst.label is not None and inst.op != 'ORG':
                self.label_offsets[inst.label] = self.code_offset
            offset = getattr(self, f'pre_{inst.op.lower()}')(inst.addressing)
            if inst.label is not None and inst.op == 'ORG':
                self.label_offsets[inst.label] = self.code_offset
            if self.code_start == -1 and inst.op in Instruction.KEYWORDS:
                self.code_start = self.code_offset
            self.code_offsets.append(self.code_offset)
            self.code_offset += offset
            if self.code_offset >= self.max_memory:
                raise AssembleError(f"The assembled code will exceed the "
                                    f"max memory {hex(self.max_memory)} "
                                    f"at line {self.line_number}")
        # Generate codes
        for i, inst in enumerate(instructions):
            self.line_number = inst.line_num
            self.code_offset = self.code_offsets[i]
            getattr(self, f'gen_{inst.op.lower()}')(i, inst.addressing)
        while len(self.codes) and len(self.codes[-1][1]) == 0:
            del self.codes[-1]
        if add_entry:
            self.code_offset = 0xFFFC
            self.gen_jmp(None, Addressing(Addressing.ADDRESS, address=Integer(is_word=True, value=self.code_start)))
        return self.codes

    def _addressing_guard(allowed: Iterable[str]):
        def deco(func):
            @wraps(func)
            def inner(self, addressing):
                if addressing.mode not in allowed:
                    keyword = func.__name__[4:].upper()
                    raise AssembleError(f"{addressing.mode.capitalize()} addressing is not allowed for `{keyword}` "
                                        f"at line {self.line_number}")
                self.fit_zero_pages.append(False)
                if addressing.mode in {Addressing.ADDRESS, Addressing.INDEXED}:
                    try:
                        resolved = self._resolve_address(addressing)
                        if isinstance(resolved.address, Integer) and \
                           not resolved.address.is_word and resolved.address.value <= 0xFF:
                            self.fit_zero_pages[-1] = True
                    except AssembleError as e:
                        pass
                return func(self, addressing)
            return inner
        return deco

    def _assemble_guard(func):
        def inner(self, index, addressing):
            while len(self.codes) and len(self.codes[-1][1]) == 0:
                del self.codes[-1]
            if len(self.codes) == 0 or self.code_offset != self.codes[-1][0] + len(self.codes[-1][1]):
                self.codes.append((self.code_offset, []))
            addressing = self._resolve_address(addressing)
            if addressing.mode in {Addressing.IMMEDIATE, Addressing.INDEXED_INDIRECT, Addressing.INDIRECT_INDEXED} \
                    and addressing.address.value > 0xFF:
                raise AssembleError(f"The value {hex(addressing.address.value)} is too large for the addressing "
                                    f"at line {self.line_number}")
            return func(self, index, addressing)
        return inner

    def _resolve_address_recur(self, arithmetic: Union[Integer, Arithmetic]) -> Integer:
        if arithmetic is None:
            return None
        if isinstance(arithmetic, Integer):
            return arithmetic
        if arithmetic.mode == Arithmetic.CURRENT:
            return Integer(is_word=True, value=self.code_offset)
        if arithmetic.mode == Arithmetic.LABEL:
            if arithmetic.param not in self.label_offsets:
                raise AssembleError(f"Can not resolve label '{arithmetic.param}' at line {self.line_number}")
            return Integer(is_word=True, value=self.label_offsets[arithmetic.param])
        if arithmetic.mode == Arithmetic.ADD:
            return self._resolve_address_recur(arithmetic.param[0]) + self._resolve_address_recur(arithmetic.param[1])
        if arithmetic.mode == Arithmetic.SUB:
            return self._resolve_address_recur(arithmetic.param[0]) - self._resolve_address_recur(arithmetic.param[1])
        if arithmetic.mode == Arithmetic.MUL:
            return self._resolve_address_recur(arithmetic.param[0]) * self._resolve_address_recur(arithmetic.param[1])
        if arithmetic.mode == Arithmetic.DIV:
            return self._resolve_address_recur(arithmetic.param[0]) // self._resolve_address_recur(arithmetic.param[1])
        if arithmetic.mode == Arithmetic.NEG:
            return -self._resolve_address_recur(arithmetic.param)
        if arithmetic.mode == Arithmetic.LOW_BYTE:
            return self._resolve_address_recur(arithmetic.param).low_byte()
        if arithmetic.mode == Arithmetic.HIGH_BYTE:
            return self._resolve_address_recur(arithmetic.param).high_byte()

    def _resolve_address(self, addressing: Addressing) -> Addressing:
        return Addressing(mode=addressing.mode,
                          address=self._resolve_address_recur(addressing.address),
                          register=addressing.register)

    def _extend_byte_address(self, code, addressing: Addressing):
        self.codes[-1][1].extend([code, addressing.address.value])

    def _extend_word_address(self, code, addressing: Addressing):
        self.codes[-1][1].extend([code, addressing.address.low_byte().value, addressing.address.high_byte().value])

    @_addressing_guard(allowed={Addressing.ADDRESS})
    def pre_org(self, addressing: Addressing):
        self.code_offset = self._resolve_address(addressing).address.value
        return 0

    @_assemble_guard
    def gen_org(self, index, addressing: Addressing):
        pass

    @_addressing_guard(allowed={Addressing.ADDRESS, Addressing.INDIRECT})
    def pre_jmp(self, addressing: Addressing):
        return 3

    @_assemble_guard
    def gen_jmp(self, index, addressing: Addressing):
        if addressing.mode == Addressing.ADDRESS:
            self._extend_word_address(0x4C, addressing)
        elif addressing.mode == Addressing.INDIRECT:
            self._extend_word_address(0x6C, addressing)

    @_addressing_guard(allowed={Addressing.IMMEDIATE, Addressing.ADDRESS, Addressing.INDEXED,
                                Addressing.INDEXED_INDIRECT, Addressing.INDIRECT_INDEXED})
    def pre_lda(self, addressing: Addressing):
        if addressing.mode in {Addressing.ADDRESS, Addressing.INDEXED}:
            return 2 if self.fit_zero_pages[-1] else 3
        return 2

    @_assemble_guard
    def gen_lda(self, index, addressing: Addressing):
        if addressing.mode == Addressing.IMMEDIATE:
            self._extend_byte_address(0xA9, addressing)
        elif addressing.mode == Addressing.ADDRESS:
            if self.fit_zero_pages[index]:
                self._extend_byte_address(0xA5, addressing)
            else:
                self._extend_word_address(0xAD, addressing)
        elif addressing.mode == Addressing.INDEXED:
            if self.fit_zero_pages[index] and addressing.register == 'X':
                self._extend_byte_address(0xB5, addressing)
            elif addressing.register == 'X':
                self._extend_word_address(0xBD, addressing)
            else:
                self._extend_word_address(0xB9, addressing)
        elif addressing.mode == Addressing.INDEXED_INDIRECT:
            self._extend_byte_address(0xA1, addressing)
        elif addressing.mode == Addressing.INDIRECT_INDEXED:
            self._extend_byte_address(0xB1, addressing)

    @_addressing_guard(allowed={Addressing.IMMEDIATE, Addressing.ADDRESS, Addressing.INDEXED})
    def pre_ldx(self, addressing: Addressing):
        if addressing.mode in {Addressing.ADDRESS, Addressing.INDEXED}:
            return 2 if self.fit_zero_pages[-1] else 3
        return 2

    @_assemble_guard
    def gen_ldx(self, index, addressing: Addressing):
        if addressing.mode == Addressing.IMMEDIATE:
            self._extend_byte_address(0xA2, addressing)
        elif addressing.mode == Addressing.ADDRESS:
            if self.fit_zero_pages[index]:
                self._extend_byte_address(0xA6, addressing)
            else:
                self._extend_word_address(0xAE, addressing)
        elif addressing.mode == Addressing.INDEXED:
            if addressing.register == 'X':
                raise AssembleError(f"Can not use X as the index register in LDX at line {self.line_number}")
            if self.fit_zero_pages[index]:
                self._extend_byte_address(0xB6, addressing)
            else:
                self._extend_word_address(0xBE, addressing)

    @_addressing_guard(allowed={Addressing.IMMEDIATE, Addressing.ADDRESS, Addressing.INDEXED})
    def pre_ldy(self, addressing: Addressing):
        if addressing.mode in {Addressing.ADDRESS, Addressing.INDEXED}:
            return 2 if self.fit_zero_pages[-1] else 3
        return 2

    @_assemble_guard
    def gen_ldy(self, index, addressing: Addressing):
        if addressing.mode == Addressing.IMMEDIATE:
            self._extend_byte_address(0xA0, addressing)
        elif addressing.mode == Addressing.ADDRESS:
            if self.fit_zero_pages[index]:
                self._extend_byte_address(0xA4, addressing)
            else:
                self._extend_word_address(0xAC, addressing)
        elif addressing.mode == Addressing.INDEXED:
            if addressing.register == 'Y':
                raise AssembleError(f"Can not use Y as the index register in LDY at line {self.line_number}")
            if self.fit_zero_pages[index]:
                self._extend_byte_address(0xB4, addressing)
            else:
                self._extend_word_address(0xBC, addressing)

    @_addressing_guard(allowed={Addressing.IMPLIED})
    def pre_nop(self, addressing: Addressing):
        return 1

    @_assemble_guard
    def gen_nop(self, index, addressing: Addressing):
        self.codes[-1][1].append(0xEA)

    @_addressing_guard(allowed={Addressing.ADDRESS, Addressing.INDEXED,
                                Addressing.INDEXED_INDIRECT, Addressing.INDIRECT_INDEXED})
    def pre_sta(self, addressing: Addressing):
        if addressing.mode in {Addressing.ADDRESS, Addressing.INDEXED}:
            return 2 if self.fit_zero_pages[-1] else 3
        return 2

    @_assemble_guard
    def gen_sta(self, index, addressing: Addressing):
        if addressing.mode == Addressing.ADDRESS:
            if self.fit_zero_pages[index]:
                self._extend_byte_address(0x85, addressing)
            else:
                self._extend_word_address(0x8D, addressing)
        elif addressing.mode == Addressing.INDEXED:
            if self.fit_zero_pages[index] and addressing.register == 'X':
                self._extend_byte_address(0x95, addressing)
            elif addressing.register == 'X':
                self._extend_word_address(0x9D, addressing)
            else:
                self._extend_word_address(0x99, addressing)
        elif addressing.mode == Addressing.INDEXED_INDIRECT:
            self._extend_byte_address(0x81, addressing)
        elif addressing.mode == Addressing.INDIRECT_INDEXED:
            self._extend_byte_address(0x91, addressing)

    @_addressing_guard(allowed={Addressing.ADDRESS, Addressing.INDEXED})
    def pre_stx(self, addressing: Addressing):
        return 2 if self.fit_zero_pages[-1] else 3

    @_assemble_guard
    def gen_stx(self, index, addressing: Addressing):
        if addressing.mode == Addressing.ADDRESS:
            if self.fit_zero_pages[index]:
                self._extend_byte_address(0x86, addressing)
            else:
                self._extend_word_address(0x8E, addressing)
        elif addressing.mode == Addressing.INDEXED:
            if addressing.register == 'X':
                raise AssembleError(f"Can not use X as the index register in STX at line {self.line_number}")
            if addressing.address.value > 0xFF:
                raise AssembleError(f"Absolute indexed addressing is not allowed for STX "
                                    f"at line {self.line_number}")
            self._extend_byte_address(0x96, addressing)

    @_addressing_guard(allowed={Addressing.ADDRESS, Addressing.INDEXED})
    def pre_sty(self, addressing: Addressing):
        return 2 if self.fit_zero_pages[-1] else 3

    @_assemble_guard
    def gen_sty(self, index, addressing: Addressing):
        if addressing.mode == Addressing.ADDRESS:
            if self.fit_zero_pages[index]:
                self._extend_byte_address(0x84, addressing)
            else:
                self._extend_word_address(0x8C, addressing)
        elif addressing.mode == Addressing.INDEXED:
            if addressing.register == 'Y':
                raise AssembleError(f"Can not use Y as the index register in STY at line {self.line_number}")
            if addressing.address.value > 0xFF:
                raise AssembleError(f"Absolute indexed addressing is not allowed for STY "
                                    f"at line {self.line_number}")
            self._extend_byte_address(0x94, addressing)
