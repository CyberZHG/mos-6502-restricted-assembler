from unittest import TestCase

from asm_6502 import get_parser


class TestParseWikiSample(TestCase):

    def test_wiki_sample(self):
        sample = """
; TOLOWER:
;
;   Convert a null-terminated character string to all lower case.
;   Maximum string length is 255 characters, plus the null term-
;   inator.
;
; Parameters:
;
;   SRC - Source string address
;   DST - Destination string address
;
        ORG  $0080
;
SRC     .WORD $0400     ;source string pointer
DST     .WORD $0500     ;destination string pointer
;
        ORG $0600       ;execution start address
;
TOLOWER LDY #$00        ;starting index
;
LOOP    LDA (SRC),Y     ;get from source string
        BEQ DONE        ;end of string
;
        CMP #'A'        ;if lower than UC alphabet...
        BCC SKIP        ;copy unchanged
;
        CMP #'Z'+1      ;if greater than UC alphabet...
        BCS SKIP        ;copy unchanged
;
        ORA #%00100000  ;convert to lower case
;
SKIP    STA (DST),Y     ;store to destination string
        INY             ;bump index
        BNE LOOP        ;next character
;
; NOTE: If Y wraps the destination string will be left in an undefined
;  state.  We set carry to indicate this to the calling function.
;
        SEC             ;report string too long error &...
        RTS             ;return to caller
;
DONE    STA (DST),Y     ;terminate destination string
        CLC             ;report conversion completed &...
        RTS             ;return to caller
;
        .END
"""
        parser = get_parser(debug=False)
        parser.parse(sample)
