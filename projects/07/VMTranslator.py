#!/usr/bin/env python3

import re
import sys

# TODO: translate from vmcode to hack

global num
inputfilename = sys.argv[1]
outputfilename = inputfilename.rsplit('.', 1)[0] + '.asm'
# regex matches a sequence of [whitespace*, (command) lowercase characters
# {2,4}, (register and address, optional) whitespace ?,(register) lowercase
# letters {4,8},
# whitespace?, (register address) numbers *]
cmd = re.compile(r'^\s*([a-z]{2,4})(?:\s([a-z]{4,8})\s([0-9]*))?')
ADD = """\
@SP     // Set A-register to SP
A=M-1   // M is the location of the 1st empty stack location, so this sets A to
        // the location of the top-most stack item.
D=M     // Save the top-most stack value
M=0     // Clears the top-most stack value
A=A-1   // Sets A to the new top of the stack (back 1).
M=M+D   // Add the saved former top-most stack value to the new top-most stack
        // value.
@SP
M=M-1
"""
SUB = """\
@SP     // Set A-register to SP
A=M-1   // M is the location of the 1st empty stack location, so this sets A to
        // the location of the top-most stack item.
D=M     // Save the top-most stack value
M=0     // Clears the top-most stack value
A=A-1   // Sets A to the new top of the stack (back 1).
M=M-D   // Subtract the saved former top-most stack value to the new top-most
        // stack value.
@SP
M=M-1
"""
NEG = '''\
@SP     // Set A-register to SP
A=M-1   // M is the location of the 1st empty stack location, so this sets A to
        // the location of the top-most stack item.
M=-M    // Negate the value of the topmost value of the stack
'''
EQ = '''\
@SP     // set a-reg to SP
A=M-1   // set a to topmost item in stack
D=M     // save topmost stack item
M=0     // clear topmost stack item
A=A-1   // de-index a to new topmost stack item
M=M-D   // subtract saved value from current topmost stack value
D=M     // sets saves topmost stack value
@SP
M=M-1
@TRUE{0} // sets a to continue point
D;JEQ   // jump if d is zero
@SP     // sets a to stack pointer
A=M-1   // go to topmost stack value
M=0    // sets m to false
@FALSE{0} // sets a to skip point
0;JMP   // unconditional jump
(TRUE{0})    // continue point
@SP     // sets a to stack pointer
A=M-1   // sets a to topmost stack falue
M=-1     // sets m to true
(FALSE{0})
'''
AND = '''\
@SP
A=M-1
D=M
M=0
A=A-1
M=M&D
@SP
M=M-1
'''
OR = '''\
@SP
A=M-1
D=M
M=0
A=A-1
M=M|D
@SP
M=M-1
'''
NOT = '''\
@SP
A=M-1
M=!M
'''
GT = '''\
@SP     // set a-reg to SP
A=M-1   // set a to topmost item in stack
D=M     // save topmost stack item
M=0     // clear topmost stack item
A=A-1   // de-index a to new topmost stack item
M=M-D   // subtract saved value from current topmost stack value
D=M     // sets saves topmost stack value
@SP
M=M-1
@TRUE{0} // sets a to continue point
D;JGT   // jump if d is zero
@SP     // sets a to stack pointer
A=M-1   // go to topmost stack value
M=0    // sets m to false
@FALSE{0} // sets a to skip point
0;JMP   // unconditional jump
(TRUE{0})    // continue point
@SP     // sets a to stack pointer
A=M-1   // sets a to topmost stack falue
M=-1     // sets m to true
(FALSE{0})
'''
LT = '''\
@SP     // set a-reg to SP
A=M-1   // set a to topmost item in stack
D=M     // save topmost stack item
M=0     // clear topmost stack item
A=A-1   // de-index a to new topmost stack item
M=M-D   // subtract saved value from current topmost stack value
D=M     // sets saves topmost stack value
@SP
M=M-1
@TRUE{0} // sets a to continue point
D;JLT   // jump if d is zero
@SP     // sets a to stack pointer
A=M-1   // go to topmost stack value
M=0    // sets m to false
@FALSE{0} // sets a to skip point
0;JMP   // unconditional jump
(TRUE{0})    // continue point
@SP     // sets a to stack pointer
A=M-1   // sets a to topmost stack falue
M=-1     // sets m to true
(FALSE{0})
'''
PCONST = '''\
@{}
D=A
@SP
A=M
M=D
@SP
M=M+1
'''
END = '''\
(END)
@END
0;JMP
'''
cmddict = {'add': ADD,
           'sub': SUB,
           'neg': NEG,
           'eq': EQ,
           'gt': GT,
           'lt': LT,
           'and': AND,
           'or': OR,
           'not': NOT,
           'push constant': PCONST,
           'end': END}


def parser(line):
    '''parses each line and returns what kind of command it is.'''
    matchCmd = cmd.match(line)
    if matchCmd:
        command = matchCmd.group(1)
        register = matchCmd.group(2)
        address = matchCmd.group(3)
        if register is None and address is None:
            return "arithmetic", command
        else:
            return "push", command, register, address
    else:
        return 'o'


def arithmetic(command):
    global num
    cmdlist.append(cmddict[command].format(num))
    num += 1


def push(command, register, address):
    cmdlist.append(cmddict[command+' '+register].format(address))


def other():
    pass


funcs = {'arithmetic': arithmetic, 'push': push, 'o': other}

with open(inputfilename, 'r') as fileToTranslate:
    cmdlist = []
    num = 0
    for line in fileToTranslate:
        parsout = parser(line)
        funcs[parsout[0]](*parsout[1:])
with open(outputfilename, 'w') as outputFile:
    for cmd in cmdlist:
        outputFile.write(cmd)
    outputFile.write(cmddict['end'])
print('Translation complete!')


def test_answer():
    tsts = [('push constant 1', ('push', 'constant', '1')),
            ('    eq', ('eq', None, None)),
            ('not   // asddsdf', ('not', None, None))]
    for test in tsts:
        output = cmd.match(test[0])
        assert output is not None, test[0]
        for group in range(1, 3):
            assert output.group(group+1) == test[1][group]
