# 6502 Restricted Assembler

[![Python application](https://github.com/CyberZHG/cpu-6502-restricted-assembler/actions/workflows/python-test.yml/badge.svg)](https://github.com/CyberZHG/cpu-6502-restricted-assembler/actions/workflows/python-test.yml)

A 6502 assembler with restricted functions.

## Install

```bash
pip install git+https://github.com/CyberZHG/cpu-6502-restricted-assembler@main
```

## Usage

```python
from asm_6502 import Assembler

code = """
START ORG $0080
      JMP START
"""
assembler = Assembler()
results = assembler.assemble(code, add_entry=False)
# Results will be `[(0x0080, [0x4C, 0x80, 0x00])]`
#     0x0080 is the offset of the codes, the following are the bytes generated by the assembler.

code = """
ORG $0080
JMP $abcd
"""
results = assembler.assemble(code)
# Results will be `[
#     (0x0080, [0x4C, 0xcd, 0xab]),
#     (0xFFFC, [0x4C, 0x80, 0x00]),
# ]`
# By default, the assembler will add a JMP instruction that 
# points to the first line of code that can be executed.
```

## Instructions

### ORG

```
ORG $0080    ; The following codes will be generated from this offset
```

### JMP

Absolute addressing:

```
JMP $0080    ; Set the program counter to $0080
```

```
START ORG $0080
      JMP START    ; Set the program counter to $0080
```

```
JMP *    ; A dead loop
```

Indirect addressing:

```
START ORG $0080
      .WORD $00A0
      JMP (START)    ; Set the program counter to the address that is contained in the target address,
                     ; which is $00A0 in this case
      JMP ($0080)
```

### LDA

```
LDA #10             ; Load $0A into the accumulator
LDA #LO $ABCD       ; Load $CD into the accumulator
LDA #HI $ABCD       ; Load $AB into the accumulator
LDA $00             ; Load accumulator from zero-page address $00
LDA $10,X           ; Load accumulator from zero-page address ($10 + X) % $0100
LDA $ABCD           ; Load accumulator from address $ABCD
LDA $ABCD,X         ; Load accumulator from address $ABCD + X
LDA $ABCD,Y         ; Load accumulator from address $ABCD + Y
LDA ($40,X)         ; Load accumulator from the 2-byte address contained in ($40 + X) % $0100
LDA ($40),Y         ; Load accumulator from (the 2-byte address contained in $40) + Y
```
