#!/usr/bin/env python3

import re
import sys

# TODO: translate from vmcode to hack

inputfilename = sys.argv[1]
outputfilename = inputfilename.rsplit('.', 1)[0] + '.asm'
cmd = re.compile(r'^\s*([a-z]{2,4})(?:\s([a-z]{4,8})\s([0-9]*))?')
cmddict = {}


def parser(line):
    pass


with open(inputfilename, 'r') as fileToTranslate:
    cmdlist = []
    linecounter = 0
    for line in fileToTranslate:
        parsout = parser(line)


def test_answer():
    tsts = [('push constant 1', ('push', 'constant', '1')),
            ('eq', ('eq', None, None)),
            ('not   // asddsdf', ('not', None, None))]
    for test in tsts:
        output = cmd.match(test[0])
        assert output is not None, test[0]
        for group in range(1, 3):
            assert output.group(group+1) == test[1][group]
