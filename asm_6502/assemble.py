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


CODE_MAP_IMPLIED = {
    'CLC': 0x18, 'CLD': 0xD8, 'CLI': 0x58, 'CLV': 0xB8, 'DEX': 0xCA,
    'DEY': 0x88, 'INX': 0xE8, 'INY': 0xC8, 'PHA': 0x48, 'PHP': 0x08,
    'PLA': 0x68, 'PLP': 0x28, 'RTI': 0x40, 'RTS': 0x60, 'SEC': 0x38,
    'SED': 0xF8, 'SEI': 0x78, 'TAX': 0xAA, 'TAY': 0xA8, 'TSX': 0xBA,
    'TXA': 0x8A, 'TXS': 0x9A, 'TYA': 0x98, 'JAM': 0x02,
}

CODE_MAP_RELATIVE = {
    'BCC': 0x90, 'BCS': 0xB0, 'BEQ': 0xF0, 'BMI': 0x30, 'BNE': 0xD0,
    'BPL': 0x10, 'BVC': 0x50, 'BVS': 0x70,
}

CODE_MAP_IMMEDIATE = {
    'ANC': 0x0B, 'ARR': 0x6B, 'ASR': 0x4B, 'SBX': 0xCB, 'XAA': 0x8B,
}

CODE_MAP_ABSOLUTE_Y = {
    'LAS': 0xBB, 'SHS': 0x9B, 'SHX': 0x9E,
}

CODE_MAPS_LOAD_A = {
    'ADC': {
        Addressing.IMMEDIATE: 0x69,
        Addressing.ZERO_PAGE: 0x65,
        Addressing.ZERO_PAGE_X: 0x75,
        Addressing.ABSOLUTE: 0x6D,
        Addressing.ABSOLUTE_X: 0x7D,
        Addressing.ABSOLUTE_Y: 0x79,
        Addressing.INDEXED_INDIRECT: 0x61,
        Addressing.INDIRECT_INDEXED: 0x71,
    },
    'AND': {
        Addressing.IMMEDIATE: 0x29,
        Addressing.ZERO_PAGE: 0x25,
        Addressing.ZERO_PAGE_X: 0x35,
        Addressing.ABSOLUTE: 0x2D,
        Addressing.ABSOLUTE_X: 0x3D,
        Addressing.ABSOLUTE_Y: 0x39,
        Addressing.INDEXED_INDIRECT: 0x21,
        Addressing.INDIRECT_INDEXED: 0x31,
    },
    'CMP': {
        Addressing.IMMEDIATE: 0xC9,
        Addressing.ZERO_PAGE: 0xC5,
        Addressing.ZERO_PAGE_X: 0xD5,
        Addressing.ABSOLUTE: 0xCD,
        Addressing.ABSOLUTE_X: 0xDD,
        Addressing.ABSOLUTE_Y: 0xD9,
        Addressing.INDEXED_INDIRECT: 0xC1,
        Addressing.INDIRECT_INDEXED: 0xD1,
    },
    'EOR': {
        Addressing.IMMEDIATE: 0x49,
        Addressing.ZERO_PAGE: 0x45,
        Addressing.ZERO_PAGE_X: 0x55,
        Addressing.ABSOLUTE: 0x4D,
        Addressing.ABSOLUTE_X: 0x5D,
        Addressing.ABSOLUTE_Y: 0x59,
        Addressing.INDEXED_INDIRECT: 0x41,
        Addressing.INDIRECT_INDEXED: 0x51,
    },
    'LDA': {
        Addressing.IMMEDIATE: 0xA9,
        Addressing.ZERO_PAGE: 0xA5,
        Addressing.ZERO_PAGE_X: 0xB5,
        Addressing.ABSOLUTE: 0xAD,
        Addressing.ABSOLUTE_X: 0xBD,
        Addressing.ABSOLUTE_Y: 0xB9,
        Addressing.INDEXED_INDIRECT: 0xA1,
        Addressing.INDIRECT_INDEXED: 0xB1,
    },
    'ORA': {
        Addressing.IMMEDIATE: 0x09,
        Addressing.ZERO_PAGE: 0x05,
        Addressing.ZERO_PAGE_X: 0x15,
        Addressing.ABSOLUTE: 0x0D,
        Addressing.ABSOLUTE_X: 0x1D,
        Addressing.ABSOLUTE_Y: 0x19,
        Addressing.INDEXED_INDIRECT: 0x01,
        Addressing.INDIRECT_INDEXED: 0x11,
    },
    'SBC': {
        Addressing.IMMEDIATE: 0xE9,
        Addressing.ZERO_PAGE: 0xE5,
        Addressing.ZERO_PAGE_X: 0xF5,
        Addressing.ABSOLUTE: 0xED,
        Addressing.ABSOLUTE_X: 0xFD,
        Addressing.ABSOLUTE_Y: 0xF9,
        Addressing.INDEXED_INDIRECT: 0xE1,
        Addressing.INDIRECT_INDEXED: 0xF1,
    },
}

CODE_MAPS_STORE_A = {
    'STA': {
        Addressing.ZERO_PAGE: 0x85,
        Addressing.ZERO_PAGE_X: 0x95,
        Addressing.ABSOLUTE: 0x8D,
        Addressing.ABSOLUTE_X: 0x9D,
        Addressing.ABSOLUTE_Y: 0x99,
        Addressing.INDEXED_INDIRECT: 0x81,
        Addressing.INDIRECT_INDEXED: 0x91,
    },
    'DCP': {
        Addressing.ZERO_PAGE: 0xC7,
        Addressing.ZERO_PAGE_X: 0xD7,
        Addressing.ABSOLUTE: 0xCF,
        Addressing.ABSOLUTE_X: 0xDF,
        Addressing.ABSOLUTE_Y: 0xDB,
        Addressing.INDEXED_INDIRECT: 0xC3,
        Addressing.INDIRECT_INDEXED: 0xD3,
    },
    'ISC': {
        Addressing.ZERO_PAGE: 0xE7,
        Addressing.ZERO_PAGE_X: 0xF7,
        Addressing.ABSOLUTE: 0xEF,
        Addressing.ABSOLUTE_X: 0xFF,
        Addressing.ABSOLUTE_Y: 0xFB,
        Addressing.INDEXED_INDIRECT: 0xE3,
        Addressing.INDIRECT_INDEXED: 0xF3,
    },
    'RLA': {
        Addressing.ZERO_PAGE: 0x27,
        Addressing.ZERO_PAGE_X: 0x37,
        Addressing.ABSOLUTE: 0x2F,
        Addressing.ABSOLUTE_X: 0x3F,
        Addressing.ABSOLUTE_Y: 0x3B,
        Addressing.INDEXED_INDIRECT: 0x23,
        Addressing.INDIRECT_INDEXED: 0x33,
    },
    'RRA': {
        Addressing.ZERO_PAGE: 0x67,
        Addressing.ZERO_PAGE_X: 0x77,
        Addressing.ABSOLUTE: 0x6F,
        Addressing.ABSOLUTE_X: 0x7F,
        Addressing.ABSOLUTE_Y: 0x7B,
        Addressing.INDEXED_INDIRECT: 0x63,
        Addressing.INDIRECT_INDEXED: 0x73,
    },
    'SLO': {
        Addressing.ZERO_PAGE: 0x07,
        Addressing.ZERO_PAGE_X: 0x17,
        Addressing.ABSOLUTE: 0x0F,
        Addressing.ABSOLUTE_X: 0x1F,
        Addressing.ABSOLUTE_Y: 0x1B,
        Addressing.INDEXED_INDIRECT: 0x03,
        Addressing.INDIRECT_INDEXED: 0x13,
    },
    'SRE': {
        Addressing.ZERO_PAGE: 0x47,
        Addressing.ZERO_PAGE_X: 0x57,
        Addressing.ABSOLUTE: 0x4F,
        Addressing.ABSOLUTE_X: 0x5F,
        Addressing.ABSOLUTE_Y: 0x5B,
        Addressing.INDEXED_INDIRECT: 0x43,
        Addressing.INDIRECT_INDEXED: 0x53,
    },
}


CODE_MAPS_A_M = {
    'ASL': {
        Addressing.ACCUMULATOR: 0x0A,
        Addressing.ZERO_PAGE: 0x06,
        Addressing.ZERO_PAGE_X: 0x16,
        Addressing.ABSOLUTE: 0x0E,
        Addressing.ABSOLUTE_X: 0x1E,
    },
    'LSR': {
        Addressing.ACCUMULATOR: 0x4A,
        Addressing.ZERO_PAGE: 0x46,
        Addressing.ZERO_PAGE_X: 0x56,
        Addressing.ABSOLUTE: 0x4E,
        Addressing.ABSOLUTE_X: 0x5E,
    },
    'ROL': {
        Addressing.ACCUMULATOR: 0x2A,
        Addressing.ZERO_PAGE: 0x26,
        Addressing.ZERO_PAGE_X: 0x36,
        Addressing.ABSOLUTE: 0x2E,
        Addressing.ABSOLUTE_X: 0x3E,
    },
    'ROR': {
        Addressing.ACCUMULATOR: 0x6A,
        Addressing.ZERO_PAGE: 0x66,
        Addressing.ZERO_PAGE_X: 0x76,
        Addressing.ABSOLUTE: 0x6E,
        Addressing.ABSOLUTE_X: 0x7E,
    },
}


class Assembler(object):

    def __init__(self,
                 max_memory=0x10000,
                 program_entry=0xfffc,
                 brk_size=2):
        self.max_memory = max_memory
        self.program_entry = program_entry
        self.brk_size = brk_size
        assert brk_size in {1, 2}, 'The size of BRK should be in {1, 2}'

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
            if inst.label is not None and not inst.op.endswith('ORG'):
                self.label_offsets[inst.label] = self.code_offset
            op_name = inst.op.lower()
            if op_name.startswith('.'):
                op_name = op_name[1:]
            if inst.op in CODE_MAP_IMPLIED:
                offset = self._get_num_bytes_type_implied(inst.addressing, op_name)
            elif inst.op in CODE_MAP_IMMEDIATE:
                offset = self._get_num_bytes_type_immediate(inst.addressing, op_name)
            elif inst.op in CODE_MAP_RELATIVE:
                offset = self._get_num_bytes_type_relative(inst.addressing, op_name)
            elif inst.op in CODE_MAP_ABSOLUTE_Y:
                offset = self._get_num_bytes_type_absolute_y(inst.addressing, op_name)
            elif inst.op in CODE_MAPS_LOAD_A:
                offset = self._get_num_bytes_type_load_a(inst.addressing, op_name)
            elif inst.op in CODE_MAPS_STORE_A:
                offset = self._get_num_bytes_type_store_a(inst.addressing, op_name)
            elif inst.op in CODE_MAPS_A_M:
                offset = self._get_num_bytes_type_a_m(inst.addressing, op_name)
            else:
                offset = getattr(self, f'pre_{op_name}')(inst.addressing, op_name)
            if inst.label is not None and inst.op.endswith('ORG'):
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
            if inst.op in CODE_MAP_IMPLIED:
                self._extend_address_type_implied(i, inst.addressing, inst.op)
            elif inst.op in CODE_MAP_IMMEDIATE:
                self._extend_address_type_immediate(i, inst.addressing, inst.op)
            elif inst.op in CODE_MAP_RELATIVE:
                self._extend_address_type_relative(i, inst.addressing, inst.op)
            elif inst.op in CODE_MAP_ABSOLUTE_Y:
                self._extend_address_type_absolute_y(i, inst.addressing, inst.op)
            elif inst.op in CODE_MAPS_LOAD_A:
                self._extend_address_type_load_a(i, inst.addressing, inst.op)
            elif inst.op in CODE_MAPS_STORE_A:
                self._extend_address_type_store_a(i, inst.addressing, inst.op)
            elif inst.op in CODE_MAPS_A_M:
                self._extend_address_type_a_m(i, inst.addressing, inst.op)
            else:
                op_name = inst.op.lower()
                if op_name.startswith('.'):
                    op_name = op_name[1:]
                getattr(self, f'gen_{op_name}')(i, inst.addressing)
        while len(self.codes) and len(self.codes[-1][1]) == 0:
            del self.codes[-1]
        if add_entry:
            self.code_offset = 0xFFFC
            self.gen_entry(None, Addressing(Addressing.ADDRESS, address=Integer(is_word=True, value=self.code_start)))
        return self.codes

    def _addressing_guard(allowed: Iterable[str]):
        def deco(func):
            @wraps(func)
            def inner(self, addressing, op_name):
                if addressing.mode not in allowed:
                    raise AssembleError(f"{addressing.mode.capitalize()} addressing is not allowed"
                                        f" for `{op_name.upper()}` at line {self.line_number}")
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
        def inner(self, index, addressing, *args, **kwargs):
            while len(self.codes) and len(self.codes[-1][1]) == 0:
                del self.codes[-1]
            if len(self.codes) == 0 or self.code_offset != self.codes[-1][0] + len(self.codes[-1][1]):
                self.codes.append((self.code_offset, []))
            addressing = self._resolve_address(addressing)
            if addressing.mode in {Addressing.IMMEDIATE, Addressing.INDEXED_INDIRECT, Addressing.INDIRECT_INDEXED} \
                    and addressing.address.value > 0xFF:
                raise AssembleError(f"The value {hex(addressing.address.value)} is too large for the addressing "
                                    f"at line {self.line_number}")
            return func(self, index, addressing, *args, **kwargs)
        return inner

    def _resolve_address_recur(self, arithmetic: Union[Integer, Arithmetic]) -> Union[Integer, List[Integer]]:
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
        if arithmetic.mode == Arithmetic.LIST:
            return [self._resolve_address_recur(p) for p in arithmetic.param]

    def _resolve_address(self, addressing: Addressing) -> Addressing:
        return Addressing(mode=addressing.mode,
                          address=self._resolve_address_recur(addressing.address),
                          register=addressing.register)

    def _extend_byte(self, code):
        self.codes[-1][1].append(code)

    def _extend_byte_address(self, code, addressing: Addressing):
        self.codes[-1][1].extend([code, addressing.address.value])

    def _extend_word_address(self, code, addressing: Addressing):
        self.codes[-1][1].extend([code, addressing.address.low_byte().value, addressing.address.high_byte().value])

    @_addressing_guard(allowed={Addressing.IMPLIED})
    def _get_num_bytes_type_implied(self, addressing: Addressing):
        return 1

    @_assemble_guard
    def _extend_address_type_implied(self, index, addressing: Addressing, op: str):
        self._extend_byte(CODE_MAP_IMPLIED[op])

    @_addressing_guard(allowed={Addressing.IMMEDIATE})
    def _get_num_bytes_type_immediate(self, addressing: Addressing):
        return 2

    @_assemble_guard
    def _extend_address_type_immediate(self, index, addressing: Addressing, op: str):
        self._extend_byte_address(CODE_MAP_IMMEDIATE[op], addressing)

    @_addressing_guard(allowed={Addressing.ADDRESS})
    def _get_num_bytes_type_relative(self, addressing: Addressing):
        return 2

    @_assemble_guard
    def _extend_address_type_relative(self, index, addressing: Addressing, op: str):
        address = addressing.address.value - (self.codes[-1][0] + 2)
        if address < -0x80 or 0x7F < address:
            raise AssembleError(f"The offset {hex(address)} is out of range for relative addressing "
                                f"at line {self.line_number}")
        if address < 0:
            address += 0x100
        self.codes[-1][1].extend([CODE_MAP_RELATIVE[op], address])

    @_addressing_guard(allowed={Addressing.INDEXED})
    def _get_num_bytes_type_absolute_y(self, addressing: Addressing):
        return 3

    @_assemble_guard
    def _extend_address_type_absolute_y(self, index, addressing: Addressing, op: str):
        self._extend_word_address(CODE_MAP_ABSOLUTE_Y[op], addressing)

    @_addressing_guard(allowed={Addressing.IMMEDIATE, Addressing.ADDRESS, Addressing.INDEXED,
                                Addressing.INDEXED_INDIRECT, Addressing.INDIRECT_INDEXED})
    def _get_num_bytes_type_load_a(self, addressing: Addressing):
        if addressing.mode in {Addressing.ADDRESS, Addressing.INDEXED}:
            return 2 if self.fit_zero_pages[-1] else 3
        return 2

    @_assemble_guard
    def _extend_address_type_load_a(self, index, addressing: Addressing, op: str):
        code_map = CODE_MAPS_LOAD_A[op]
        if addressing.mode == Addressing.IMMEDIATE:
            self._extend_byte_address(code_map[Addressing.IMMEDIATE], addressing)
        elif addressing.mode == Addressing.ADDRESS:
            if self.fit_zero_pages[index]:
                self._extend_byte_address(code_map[Addressing.ZERO_PAGE], addressing)
            else:
                self._extend_word_address(code_map[Addressing.ABSOLUTE], addressing)
        elif addressing.mode == Addressing.INDEXED:
            if self.fit_zero_pages[index] and addressing.register == 'X':
                self._extend_byte_address(code_map[Addressing.ZERO_PAGE_X], addressing)
            elif addressing.register == 'X':
                self._extend_word_address(code_map[Addressing.ABSOLUTE_X], addressing)
            else:
                self._extend_word_address(code_map[Addressing.ABSOLUTE_Y], addressing)
        elif addressing.mode == Addressing.INDEXED_INDIRECT:
            self._extend_byte_address(code_map[Addressing.INDEXED_INDIRECT], addressing)
        elif addressing.mode == Addressing.INDIRECT_INDEXED:
            self._extend_byte_address(code_map[Addressing.INDIRECT_INDEXED], addressing)

    @_addressing_guard(allowed={Addressing.ADDRESS, Addressing.INDEXED,
                                Addressing.INDEXED_INDIRECT, Addressing.INDIRECT_INDEXED})
    def _get_num_bytes_type_store_a(self, addressing: Addressing):
        if addressing.mode in {Addressing.ADDRESS, Addressing.INDEXED}:
            return 2 if self.fit_zero_pages[-1] else 3
        return 2

    @_assemble_guard
    def _extend_address_type_store_a(self, index, addressing: Addressing, op: str):
        code_map = CODE_MAPS_STORE_A[op]
        if addressing.mode == Addressing.ADDRESS:
            if self.fit_zero_pages[index]:
                self._extend_byte_address(code_map[Addressing.ZERO_PAGE], addressing)
            else:
                self._extend_word_address(code_map[Addressing.ABSOLUTE], addressing)
        elif addressing.mode == Addressing.INDEXED:
            if self.fit_zero_pages[index] and addressing.register == 'X':
                self._extend_byte_address(code_map[Addressing.ZERO_PAGE_X], addressing)
            elif addressing.register == 'X':
                self._extend_word_address(code_map[Addressing.ABSOLUTE_X], addressing)
            else:
                self._extend_word_address(code_map[Addressing.ABSOLUTE_Y], addressing)
        elif addressing.mode == Addressing.INDEXED_INDIRECT:
            self._extend_byte_address(code_map[Addressing.INDEXED_INDIRECT], addressing)
        elif addressing.mode == Addressing.INDIRECT_INDEXED:
            self._extend_byte_address(code_map[Addressing.INDIRECT_INDEXED], addressing)

    @_addressing_guard(allowed={Addressing.ACCUMULATOR, Addressing.ADDRESS, Addressing.INDEXED})
    def _get_num_bytes_type_a_m(self, addressing: Addressing):
        if addressing.mode == Addressing.ACCUMULATOR:
            return 1
        return 2 if self.fit_zero_pages[-1] else 3

    @_assemble_guard
    def _extend_address_type_a_m(self, index, addressing: Addressing, op: str):
        code_map = CODE_MAPS_A_M[op]
        if addressing.mode == Addressing.ACCUMULATOR:
            self._extend_byte(code_map[Addressing.ACCUMULATOR])
        elif addressing.mode == Addressing.ADDRESS:
            if self.fit_zero_pages[index]:
                self._extend_byte_address(code_map[Addressing.ZERO_PAGE], addressing)
            else:
                self._extend_word_address(code_map[Addressing.ABSOLUTE], addressing)
        elif addressing.mode == Addressing.INDEXED:
            if addressing.register == 'Y':
                raise AssembleError(f"Can not use Y as the index register in {op} at line {self.line_number}")
            if self.fit_zero_pages[index]:
                self._extend_byte_address(code_map[Addressing.ZERO_PAGE_X], addressing)
            else:
                self._extend_word_address(code_map[Addressing.ABSOLUTE_X], addressing)

    @_assemble_guard
    def gen_entry(self, index, addressing: Addressing):
        self.codes[-1][1].extend([addressing.address.low_byte().value, addressing.address.high_byte().value])

    @_addressing_guard(allowed={Addressing.ADDRESS})
    def pre_org(self, addressing: Addressing):
        self.code_offset = self._resolve_address(addressing).address.value
        return 0

    @_assemble_guard
    def gen_org(self, index, addressing: Addressing):
        pass

    @_addressing_guard(allowed={Addressing.IMPLIED})
    def pre_end(self, addressing: Addressing):
        return 3

    @_assemble_guard
    def gen_end(self, index, addressing: Addressing):
        address = Integer(is_word=True, value=self.codes[-1][0])
        self.codes[-1][1].extend([0x4C, address.low_byte().value, address.high_byte().value])

    @_addressing_guard(allowed={Addressing.ADDRESS, Addressing.LIST})
    def pre_byte(self, addressing: Addressing):
        if addressing.mode == Addressing.LIST:
            return len(addressing.address.param)
        return 1

    @_assemble_guard
    def gen_byte(self, index, addressing: Addressing):
        if addressing.mode == Addressing.LIST:
            for byte in addressing.address:
                if byte.value > 0xFF:
                    raise AssembleError(f"{hex(byte.value)} can not fit in a byte "
                                        f"at line {self.line_number}")
                self._extend_byte(byte.value)
        else:
            if addressing.address.value > 0xFF:
                raise AssembleError(f"{hex(addressing.address.value)} can not fit in a byte "
                                    f"at line {self.line_number}")
            self._extend_byte(addressing.address.value)

    @_addressing_guard(allowed={Addressing.ADDRESS, Addressing.LIST})
    def pre_word(self, addressing: Addressing):
        if addressing.mode == Addressing.LIST:
            return len(addressing.address.param) * 2
        return 2

    @_assemble_guard
    def gen_word(self, index, addressing: Addressing):
        if addressing.mode == Addressing.LIST:
            for word in addressing.address:
                self.codes[-1][1].extend([word.low_byte().value, word.high_byte().value])
        else:
            self.codes[-1][1].extend([addressing.address.low_byte().value, addressing.address.high_byte().value])

    @_addressing_guard(allowed={Addressing.IMPLIED})
    def pre_brk(self, addressing: Addressing):
        return self.brk_size

    @_assemble_guard
    def gen_brk(self, index, addressing: Addressing):
        for i in range(self.brk_size):
            self._extend_byte(0x00)

    @_addressing_guard(allowed={Addressing.IMPLIED, Addressing.IMMEDIATE, Addressing.ADDRESS, Addressing.INDEXED})
    def pre_nop(self, addressing: Addressing):
        if addressing.mode == Addressing.IMPLIED:
            return 1
        if addressing.mode in {Addressing.ADDRESS, Addressing.INDEXED}:
            return 2 if self.fit_zero_pages[-1] else 3
        return 2

    @_assemble_guard
    def gen_nop(self, index, addressing: Addressing):
        if addressing.mode == Addressing.IMPLIED:
            self._extend_byte(0xEA)
        elif addressing.mode == Addressing.IMMEDIATE:
            self._extend_byte_address(0x80, addressing)
        elif addressing.mode == Addressing.ADDRESS:
            if self.fit_zero_pages[index]:
                self._extend_byte_address(0x04, addressing)
            else:
                self._extend_word_address(0x0C, addressing)
        elif addressing.mode == Addressing.INDEXED:
            if addressing.register == 'Y':
                raise AssembleError(f"Can not use Y as the index register in NOP at line {self.line_number}")
            if self.fit_zero_pages[index]:
                self._extend_byte_address(0x14, addressing)
            else:
                self._extend_word_address(0x1C, addressing)

    @_addressing_guard(allowed={Addressing.ADDRESS, Addressing.INDIRECT})
    def pre_jmp(self, addressing: Addressing):
        return 3

    @_assemble_guard
    def gen_jmp(self, index, addressing: Addressing):
        if addressing.mode == Addressing.ADDRESS:
            self._extend_word_address(0x4C, addressing)
        elif addressing.mode == Addressing.INDIRECT:
            self._extend_word_address(0x6C, addressing)

    @_addressing_guard(allowed={Addressing.ADDRESS})
    def pre_jsr(self, addressing: Addressing):
        return 3

    @_assemble_guard
    def gen_jsr(self, index, addressing: Addressing):
        self._extend_word_address(0x20, addressing)

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

    @_addressing_guard(allowed={Addressing.IMMEDIATE, Addressing.ADDRESS, Addressing.INDEXED,
                                Addressing.INDIRECT_INDEXED, Addressing.INDEXED_INDIRECT})
    def pre_lax(self, addressing: Addressing):
        if addressing.mode in {Addressing.ADDRESS, Addressing.INDEXED}:
            return 2 if self.fit_zero_pages[-1] else 3
        return 2

    @_assemble_guard
    def gen_lax(self, index, addressing: Addressing):
        if addressing.mode == Addressing.IMMEDIATE:
            self._extend_byte_address(0xAB, addressing)
        elif addressing.mode == Addressing.ADDRESS:
            if self.fit_zero_pages[index]:
                self._extend_byte_address(0xA7, addressing)
            else:
                self._extend_word_address(0xAF, addressing)
        elif addressing.mode == Addressing.INDEXED:
            if addressing.register == 'X':
                raise AssembleError(f"Can not use X as the index register in LAX at line {self.line_number}")
            if self.fit_zero_pages[index]:
                self._extend_byte_address(0xB7, addressing)
            else:
                self._extend_word_address(0xBF, addressing)
        elif addressing.mode == Addressing.INDEXED_INDIRECT:
            self._extend_byte_address(0xA3, addressing)
        elif addressing.mode == Addressing.INDIRECT_INDEXED:
            self._extend_byte_address(0xB3, addressing)

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

    @_addressing_guard(allowed={Addressing.ADDRESS, Addressing.INDEXED, Addressing.INDEXED_INDIRECT})
    def pre_sax(self, addressing: Addressing):
        if addressing.mode in {Addressing.ADDRESS, Addressing.INDEXED}:
            return 2 if self.fit_zero_pages[-1] else 3
        return 2

    @_assemble_guard
    def gen_sax(self, index, addressing: Addressing):
        if addressing.mode == Addressing.ADDRESS:
            if self.fit_zero_pages[index]:
                self._extend_byte_address(0x87, addressing)
            else:
                self._extend_word_address(0x8F, addressing)
        elif addressing.mode == Addressing.INDEXED:
            if addressing.register == 'X':
                raise AssembleError(f"Can not use X as the index register in SAX at line {self.line_number}")
            if addressing.address.value > 0xFF:
                raise AssembleError(f"Absolute indexed addressing is not allowed for SAX "
                                    f"at line {self.line_number}")
            self._extend_byte_address(0x97, addressing)
        elif addressing.mode == Addressing.INDEXED_INDIRECT:
            self._extend_byte_address(0x83, addressing)

    @_addressing_guard(allowed={Addressing.INDEXED, Addressing.INDIRECT_INDEXED})
    def pre_sha(self, addressing: Addressing):
        return 3 if addressing.mode == Addressing.INDEXED else 2

    @_assemble_guard
    def gen_sha(self, index, addressing: Addressing):
        if addressing.mode == Addressing.INDEXED:
            if addressing.register == 'X':
                raise AssembleError(f"Can not use X as the index register in SHA at line {self.line_number}")
            self._extend_word_address(0x9F, addressing)
        elif addressing.mode == Addressing.INDIRECT_INDEXED:
            self._extend_byte_address(0x93, addressing)

    @_addressing_guard(allowed={Addressing.INDEXED})
    def pre_shy(self, addressing: Addressing):
        return 3 if addressing.mode == Addressing.INDEXED else 2

    @_assemble_guard
    def gen_shy(self, index, addressing: Addressing):
        if addressing.mode == Addressing.INDEXED:
            if addressing.register == 'Y':
                raise AssembleError(f"Can not use Y as the index register in SHY at line {self.line_number}")
            self._extend_word_address(0x9C, addressing)

    @_addressing_guard(allowed={Addressing.ADDRESS})
    def pre_bit(self, addressing: Addressing):
        return 2 if self.fit_zero_pages[-1] else 3

    @_assemble_guard
    def gen_bit(self, index, addressing: Addressing):
        if self.fit_zero_pages[index]:
            self._extend_byte_address(0x24, addressing)
        else:
            self._extend_word_address(0x2C, addressing)

    @_addressing_guard(allowed={Addressing.IMMEDIATE, Addressing.ADDRESS})
    def pre_cpx(self, addressing: Addressing):
        if addressing.mode in {Addressing.ADDRESS}:
            return 2 if self.fit_zero_pages[-1] else 3
        return 2

    @_assemble_guard
    def gen_cpx(self, index, addressing: Addressing):
        if addressing.mode == Addressing.IMMEDIATE:
            self._extend_byte_address(0xE0, addressing)
        elif addressing.mode == Addressing.ADDRESS:
            if self.fit_zero_pages[index]:
                self._extend_byte_address(0xE4, addressing)
            else:
                self._extend_word_address(0xEC, addressing)

    @_addressing_guard(allowed={Addressing.IMMEDIATE, Addressing.ADDRESS})
    def pre_cpy(self, addressing: Addressing):
        if addressing.mode in {Addressing.ADDRESS}:
            return 2 if self.fit_zero_pages[-1] else 3
        return 2

    @_assemble_guard
    def gen_cpy(self, index, addressing: Addressing):
        if addressing.mode == Addressing.IMMEDIATE:
            self._extend_byte_address(0xC0, addressing)
        elif addressing.mode == Addressing.ADDRESS:
            if self.fit_zero_pages[index]:
                self._extend_byte_address(0xC4, addressing)
            else:
                self._extend_word_address(0xCC, addressing)

    @_addressing_guard(allowed={Addressing.ADDRESS, Addressing.INDEXED})
    def pre_inc(self, addressing: Addressing):
        return 2 if self.fit_zero_pages[-1] else 3

    @_assemble_guard
    def gen_inc(self, index, addressing: Addressing):
        if addressing.mode == Addressing.ADDRESS:
            if self.fit_zero_pages[index]:
                self._extend_byte_address(0xE6, addressing)
            else:
                self._extend_word_address(0xEE, addressing)
        elif addressing.mode == Addressing.INDEXED:
            if addressing.register == 'Y':
                raise AssembleError(f"Can not use Y as the index register in INC at line {self.line_number}")
            if self.fit_zero_pages[index]:
                self._extend_byte_address(0xF6, addressing)
            else:
                self._extend_word_address(0xFE, addressing)

    @_addressing_guard(allowed={Addressing.ADDRESS, Addressing.INDEXED})
    def pre_dec(self, addressing: Addressing):
        return 2 if self.fit_zero_pages[-1] else 3

    @_assemble_guard
    def gen_dec(self, index, addressing: Addressing):
        if addressing.mode == Addressing.ADDRESS:
            if self.fit_zero_pages[index]:
                self._extend_byte_address(0xC6, addressing)
            else:
                self._extend_word_address(0xCE, addressing)
        elif addressing.mode == Addressing.INDEXED:
            if addressing.register == 'Y':
                raise AssembleError(f"Can not use Y as the index register in DEC at line {self.line_number}")
            if self.fit_zero_pages[index]:
                self._extend_byte_address(0xD6, addressing)
            else:
                self._extend_word_address(0xDE, addressing)
