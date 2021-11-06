#!/usr/bin/env bash
pycodestyle --max-line-length=120 --exclude parsetab.py asm_6502 tests && \
    nosetests --nocapture --with-coverage --cover-erase --cover-html --cover-html-dir=htmlcov --cover-package=asm_6502 --with-doctest