from typing import Union, List, Iterable
from functools import wraps

from .grammar import (get_parser, KEYWORDS, LABEL,
                      ADDRESSING, ADDRESS, INTEGER, ARITHMETIC, CURRENT)


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
            self.gen_JMP(None, (ADDRESSING.ADDRESS, (ADDRESS, (INTEGER, self.code_start))))
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
                        if resolved[1] <= 0xFF:
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
                    and address[1] > 0xFF:
                raise AssembleError(f"The value {hex(address[1])} is too large for the addressing "
                                    f"at line {self.line_number}")
            return func(self, index, address)
        return inner

    def _resolve_address_recur(self, address):
        if address[0] == INTEGER:
            return address[1]
        if address[0] == CURRENT:
            return self.code_offset
        if address[0] == LABEL:
            if address[1] not in self.label_offsets:
                raise AssembleError(f"Can not resolve label '{address[1]}' at line {self.line_number}")
            return self.label_offsets[address[1]]
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
                return self._low_byte(self._resolve_address_recur(address[2]))
            if op == 'hi':
                return self._high_byte(self._resolve_address_recur(address[2]))

    def _resolve_address(self, address):
        if address[0] == ADDRESSING.INDEXED:
            return address[0], self._resolve_address_recur(address[1][1]), address[-1][-1]
        return address[0], self._resolve_address_recur(address[1][1])

    @staticmethod
    def _low_byte(word):
        return word & 0xFF

    @staticmethod
    def _high_byte(word):
        return (word >> 8) & 0xFF

    @_addressing_guard(allowed={ADDRESSING.ADDRESS})
    def pre_ORG(self, address):
        self.code_offset = self._resolve_address(address)[1]
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
            self.codes[-1][1].extend([0x4C, self._low_byte(address[1]), self._high_byte(address[1])])
        elif address[0] == ADDRESSING.INDIRECT:
            self.codes[-1][1].extend([0x6C, self._low_byte(address[1]), self._high_byte(address[1])])

    @_addressing_guard(allowed={ADDRESSING.IMMEDIATE, ADDRESSING.ADDRESS, ADDRESSING.INDEXED,
                                ADDRESSING.INDEXED_INDIRECT, ADDRESSING.INDIRECT_INDEXED})
    def pre_LDA(self, address):
        if address[0] in {ADDRESSING.ADDRESS, ADDRESSING.INDEXED}:
            return 2 if self.fit_zero_pages[-1] else 3
        return 2

    @_assemble_guard
    def gen_LDA(self, index, address):
        if address[0] == ADDRESSING.IMMEDIATE:
            self.codes[-1][1].extend([0xA9, address[1]])
        elif address[0] == ADDRESSING.ADDRESS:
            if self.fit_zero_pages[index]:
                self.codes[-1][1].extend([0xA5, address[1]])
            else:
                self.codes[-1][1].extend([0xAD, self._low_byte(address[1]), self._high_byte(address[1])])
        elif address[0] == ADDRESSING.INDEXED:
            if self.fit_zero_pages[index] and address[-1] == 'X':
                self.codes[-1][1].extend([0xB5, address[1]])
            elif address[-1] == 'X':
                self.codes[-1][1].extend([0xBD, self._low_byte(address[1]), self._high_byte(address[1])])
            else:
                self.codes[-1][1].extend([0xB9, self._low_byte(address[1]), self._high_byte(address[1])])
        elif address[0] == ADDRESSING.INDEXED_INDIRECT:
            self.codes[-1][1].extend([0xA1, address[1]])
        elif address[0] == ADDRESSING.INDIRECT_INDEXED:
            self.codes[-1][1].extend([0xB1, address[1]])
