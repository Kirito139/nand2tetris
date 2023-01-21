#!/usr/bin/env python3

import re
import sys

inputfilename = sys.argv[1]
outputfilename = inputfilename.rsplit('.', 1)[0] + '.hack'
are = re.compile(r'^\s*@(.*)')
# first part allows whitespace, second part allows 1-3 letters(the dest field),
# after that an = sign, the comp field, the rest allows for a comment
cre = re.compile(r'^\s*(?:(\w{0,3})=)?([0-9A-Z+\|&\-!]{1,3})(?:;(\w{0,3}))?')
lre = re.compile(r'^\s*\((.*)\)')
adre = re.compile(r'^\d*$')
addressymboltable = {'SP': 0,
                     'LCL': 1,
                     'ARG': 2,
                     'THIS': 3,
                     'THAT': 4,
                     'R0': 0,
                     'R1': 1,
                     'R2': 2,
                     'R3': 3,
                     'R4': 4,
                     'R5': 5,
                     'R6': 6,
                     'R7': 7,
                     'R8': 8,
                     'R9': 9,
                     'R10': 10,
                     'R11': 11,
                     'R12': 12,
                     'R13': 13,
                     'R14': 14,
                     'R15': 15,
                     'SCREEN': 16384,
                     'KBD': 24676}
compdict = {'0': '0101010',
            '1': '0111111',
            '-1': '0111010',
            'D': '0001100',
            'A': '0110000',
            'M': '1110000',
            '!D': '1001101',
            '!A': '0110001',
            'r!M': '1110001',
            '-D': '0001111',
            '-A': '0110011',
            '-M': '1110011',
            'D+1': '0011111',
            'A+1': '0110111',
            'M+1': '1110111',
            'D-1': '0001110',
            'A-1': '0110010',
            'M-1': '1110010',
            'D+A': '0000010',
            'D+M': '1000010',
            'D-A': '0010011',
            'D-M': '1010011',
            'A-D': '0000111',
            'M-D': '1000111',
            'D&A': '0000000',
            'D&M': '1000000',
            'D|A': '0010101',
            'D|M': '1010101'}
destdict = {None: '000',
            'M': '001',
            'D': '010',
            'MD': '011',
            'A': '100',
            'AM': '101',
            'AD': '110',
            'AMD': '111'}
jumpdict = {None: '000',
            'JGT': '001',
            'JEQ': '010',
            'JGE': '011',
            'JLT': '100',
            'JNE': '101',
            'JLE': '110',
            'JMP': '111'}

undefinedsymboltable = []
labelsymboltable = {}
nextvar = 16
# TODO: finish symboltable()
# TODO: create list of commands and symboltable simultaneosly, then transcribe
# to .hack file


# Encapsulates access to teh input code. Reads an assembly language command,
# parses it, and provides convenient access to teh command's components (fields
# and symbols). In addition, skips all white space and comments.
def parser(line):
    global undefinedsymboltable
    global addressymboltable
    global nextvar
    global labelsymboltable

    # differentiates between a, l and c instructions
    # if c instruction, find comp, dest and jump
    m = cre.match(line)
    if m:
        comp = m.group(2)
        dest = m.group(1)
        jump = m.group(3)
        output = "111"

        output += compdict[comp]
        output += destdict[dest]
        output += jumpdict[jump]
        output += '\n'
        return output
    m = are.match(line)
    if m:
        address = m.group(1)
        output = '0'
        if adre.match(address):
            output += format(int(address), 'b')
        elif address not in undefinedsymboltable:
            undefinedsymboltable += address
        filler = ''
        for i in range(16-len(output)):
            filler += '0'
        filler += output
        filler += '\n'
        return filler
    m = lre.match(line)
    if m:
        symbol = m.group(1)
        if symbol not in labelsymboltable:
            labelsymboltable[symbol] = linecounter
        if symbol in undefinedsymboltable:
            undefinedsymboltable -= symbol
        return 'l'
    else:
        return 'w'


with open(inputfilename, "r") as fileToTranslate:
    cmdlist = []
    linecounter = 0
    for line in fileToTranslate:
        parsout = parser(line)
        if parsout != 'w' and parsout != 'l':
            cmdlist.append(parsout)
            linecounter += 1
with open(outputfilename, "w") as outputFile:
    for symbol in undefinedsymboltable:
        addressymboltable[symbol] = nextvar
        nextvar += 1
    for cmd in cmdlist:
        print(cmd)
        outputFile.write(cmd)
