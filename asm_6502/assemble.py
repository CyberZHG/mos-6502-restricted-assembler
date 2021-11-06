from typing import Union, List, Iterable
from functools import wraps

from .grammar import (get_parser, KEYWORDS, LABEL,
                      Integer, ADDRESSING, ADDRESS, ARITHMETIC, CURRENT)


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
                 add_entry=True):
        if isinstance(instructions, str):
            parser = get_parser()
            instructions = parser.parse(instructions)
        # Preprocess and calculate offsets
        self.reset()
        for i, inst in enumerate(instructions):
            self.line_number = inst[-1]
            if inst[1][0] == LABEL:
                if inst[2][1] != 'ORG':
                    self.label_offsets[inst[1][1]] = self.code_offset
                offset = getattr(self, f'pre_{inst[2][1]}')(inst[3])
                if inst[2][1] == 'ORG':
                    self.label_offsets[inst[1][1]] = self.code_offset
                if self.code_start == -1 and inst[2][1] in KEYWORDS:
                    self.code_start = self.code_offset
            else:
                offset = getattr(self, f'pre_{inst[1][1]}')(inst[2])
                if self.code_start == -1 and inst[1][1] in KEYWORDS:
                    self.code_start = self.code_offset
            self.code_offsets.append(self.code_offset)
            self.code_offset += offset
            if self.code_offset >= self.max_memory:
                raise AssembleError(f"The assembled code will exceed the "
                                    f"max memory {hex(self.max_memory)} "
                                    f"at line {self.line_number}")
        # Generate codes
        for i, inst in enumerate(instructions):
            self.line_number = inst[-1]
            self.code_offset = self.code_offsets[i]
            if inst[1][0] == LABEL:
                getattr(self, f'gen_{inst[2][1]}')(i, inst[3])
            else:
                getattr(self, f'gen_{inst[1][1]}')(i, inst[2])
        while len(self.codes) and len(self.codes[-1][1]) == 0:
            del self.codes[-1]
        if add_entry:
            self.code_offset = 0xFFFC
            self.gen_JMP(None, (ADDRESSING.ADDRESS, (ADDRESS, Integer(is_word=True, value=self.code_start))))
        return self.codes

    def _addressing_guard(allowed: Iterable[str]):
        def deco(func):
            @wraps(func)
            def inner(self, address):
                if address[0] not in allowed:
                    keyword = func.__name__[4:]
                    raise AssembleError(f"The addressing is not allowed for `{keyword}` "
                                        f"at line {self.line_number}")
                self.fit_zero_pages.append(False)
                if address[0] in {ADDRESSING.ADDRESS, ADDRESSING.INDEXED}:
                    try:
                        resolved = self._resolve_address(address)
                        if isinstance(resolved[1], Integer) and not resolved[1].is_word and resolved[1].value <= 0xFF:
                            self.fit_zero_pages[-1] = True
                    except AssembleError as e:
                        pass
                return func(self, address)
            return inner
        return deco

    def _assemble_guard(func):
        def inner(self, index, address):
            while len(self.codes) and len(self.codes[-1][1]) == 0:
                del self.codes[-1]
            if len(self.codes) == 0 or self.code_offset != self.codes[-1][0] + len(self.codes[-1][1]):
                self.codes.append((self.code_offset, []))
            address = self._resolve_address(address)
            if address[0] in {ADDRESSING.IMMEDIATE, ADDRESSING.INDEXED_INDIRECT, ADDRESSING.INDIRECT_INDEXED} \
                    and address[1].value > 0xFF:
                raise AssembleError(f"The value {hex(address[1].value)} is too large for the addressing "
                                    f"at line {self.line_number}")
            return func(self, index, address)
        return inner

    def _resolve_address_recur(self, address):
        if isinstance(address, Integer):
            return address
        if address[0] == CURRENT:
            return Integer(is_word=True, value=self.code_offset)
        if address[0] == LABEL:
            if address[1] not in self.label_offsets:
                raise AssembleError(f"Can not resolve label '{address[1]}' at line {self.line_number}")
            return Integer(is_word=True, value=self.label_offsets[address[1]])
        if address[0] == ARITHMETIC:
            op = address[1]
            if op == '+':
                return self._resolve_address_recur(address[2]) + self._resolve_address_recur(address[3])
            if op == '-':
                return self._resolve_address_recur(address[2]) - self._resolve_address_recur(address[3])
            if op == '*':
                return self._resolve_address_recur(address[2]) * self._resolve_address_recur(address[3])
            if op == '/':
                return self._resolve_address_recur(address[2]) // self._resolve_address_recur(address[3])
            if op == 'lo':
                return self._resolve_address_recur(address[2]).low_byte()
            if op == 'hi':
                return self._resolve_address_recur(address[2]).high_byte()

    def _resolve_address(self, address):
        if address[0] == ADDRESSING.INDEXED:
            return address[0], self._resolve_address_recur(address[1][1]), address[-1][-1]
        return address[0], self._resolve_address_recur(address[1][1])

    def _extend_byte_address(self, code, address):
        self.codes[-1][1].extend([code, address[1].value])

    def _extend_word_address(self, code, address):
        self.codes[-1][1].extend([code, address[1].low_byte().value, address[1].high_byte().value])

    @_addressing_guard(allowed={ADDRESSING.ADDRESS})
    def pre_ORG(self, address):
        self.code_offset = self._resolve_address(address)[1].value
        return 0

    @_assemble_guard
    def gen_ORG(self, index, address):
        pass

    @_addressing_guard(allowed={ADDRESSING.ADDRESS, ADDRESSING.INDIRECT})
    def pre_JMP(self, address):
        return 3

    @_assemble_guard
    def gen_JMP(self, index, address):
        if address[0] == ADDRESSING.ADDRESS:
            self._extend_word_address(0x4C, address)
        elif address[0] == ADDRESSING.INDIRECT:
            self._extend_word_address(0x6C, address)

    @_addressing_guard(allowed={ADDRESSING.IMMEDIATE, ADDRESSING.ADDRESS, ADDRESSING.INDEXED,
                                ADDRESSING.INDEXED_INDIRECT, ADDRESSING.INDIRECT_INDEXED})
    def pre_LDA(self, address):
        if address[0] in {ADDRESSING.ADDRESS, ADDRESSING.INDEXED}:
            return 2 if self.fit_zero_pages[-1] else 3
        return 2

    @_assemble_guard
    def gen_LDA(self, index, address):
        if address[0] == ADDRESSING.IMMEDIATE:
            self._extend_byte_address(0xA9, address)
        elif address[0] == ADDRESSING.ADDRESS:
            if self.fit_zero_pages[index]:
                self._extend_byte_address(0xA5, address)
            else:
                self._extend_word_address(0xAD, address)
        elif address[0] == ADDRESSING.INDEXED:
            if self.fit_zero_pages[index] and address[-1] == 'X':
                self._extend_byte_address(0xB5, address)
            elif address[-1] == 'X':
                self._extend_word_address(0xBD, address)
            else:
                self._extend_word_address(0xB9, address)
        elif address[0] == ADDRESSING.INDEXED_INDIRECT:
            self._extend_byte_address(0xA1, address)
        elif address[0] == ADDRESSING.INDIRECT_INDEXED:
            self._extend_byte_address(0xB1, address)

    @_addressing_guard(allowed={ADDRESSING.IMMEDIATE, ADDRESSING.ADDRESS, ADDRESSING.INDEXED})
    def pre_LDX(self, address):
        if address[0] in {ADDRESSING.ADDRESS, ADDRESSING.INDEXED}:
            return 2 if self.fit_zero_pages[-1] else 3
        return 2

    @_assemble_guard
    def gen_LDX(self, index, address):
        if address[0] == ADDRESSING.IMMEDIATE:
            self._extend_byte_address(0xA2, address)
        elif address[0] == ADDRESSING.ADDRESS:
            if self.fit_zero_pages[index]:
                self._extend_byte_address(0xA6, address)
            else:
                self._extend_word_address(0xAE, address)
        elif address[0] == ADDRESSING.INDEXED:
            if address[-1] == 'X':
                raise AssembleError(f"Can not use X as the index register in LDX at line {self.line_number}")
            if self.fit_zero_pages[index]:
                self._extend_byte_address(0xB6, address)
            else:
                self._extend_word_address(0xBE, address)

    @_addressing_guard(allowed={ADDRESSING.IMMEDIATE, ADDRESSING.ADDRESS, ADDRESSING.INDEXED})
    def pre_LDY(self, address):
        if address[0] in {ADDRESSING.ADDRESS, ADDRESSING.INDEXED}:
            return 2 if self.fit_zero_pages[-1] else 3
        return 2

    @_assemble_guard
    def gen_LDY(self, index, address):
        if address[0] == ADDRESSING.IMMEDIATE:
            self._extend_byte_address(0xA0, address)
        elif address[0] == ADDRESSING.ADDRESS:
            if self.fit_zero_pages[index]:
                self._extend_byte_address(0xA4, address)
            else:
                self._extend_word_address(0xAC, address)
        elif address[0] == ADDRESSING.INDEXED:
            if address[-1] == 'Y':
                raise AssembleError(f"Can not use Y as the index register in LDX at line {self.line_number}")
            if self.fit_zero_pages[index]:
                self._extend_byte_address(0xB4, address)
            else:
                self._extend_word_address(0xBC, address)
