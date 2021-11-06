# 6502 Restricted Assembler

[![Python application](https://github.com/CyberZHG/cpu-6502-restricted-assembler/actions/workflows/python-test.yml/badge.svg)](https://github.com/CyberZHG/cpu-6502-restricted-assembler/actions/workflows/python-test.yml)


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

Indirect addressing:

```
START ORG $0080
      .WORD $00A0
      JMP (START)    ; Set the program counter to the address that is contained in the target address,
                     ; which is $00A0 in this case
      JMP ($0080)
```
