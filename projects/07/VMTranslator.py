#!/usr/bin/env python3

import re
import sys
from pathlib import Path

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
    // add
@SP     // Set A-register to SP
A=M-1   // M is the location of the 1st empty stack location, so this sets A to
        // the location of the top-most stack item.
D=M     // Save the top-most stack value
A=A-1   // Sets A to the new top of the stack (back 1).
M=M+D   // Add the saved former top-most stack value to the new top-most stack
        // value.
@SP
M=M-1
"""
SUB = """\
    // sub
@SP     // Set A-register to SP
A=M-1   // M is the location of the 1st empty stack location, so this sets A to
        // the location of the top-most stack item.
D=M     // Save the top-most stack value
A=A-1   // Sets A to the new top of the stack (back 1).
M=M-D   // Subtract the saved former top-most stack value to the new top-most
        // stack value.
@SP
M=M-1
"""
NEG = '''\
    // neg
@SP     // Set A-register to SP
A=M-1   // M is the location of the 1st empty stack location, so this sets A to
        // the location of the top-most stack item.
M=-M    // Negate the value of the topmost value of the stack
'''
EQ = '''\
    // eq
@SP     // set a-reg to SP
A=M-1   // set a to topmost item in stack
D=M     // save topmost stack item
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
    // and
@SP     // goes to stack pointer pointer
A=M-1   // goes to top of stack
D=M     // saves top of stack
A=A-1   // moves to second topmost stack location
M=M&D   // ands contents of secondmost and topmost stack locations
@SP
M=M-1   // decrements stack pointer
'''
OR = '''\
    // or
@SP
A=M-1   // goes to top of stack
D=M     // saves top of stack
A=A-1   // goes to second topmost location in stack
M=M|D   // ors together topmost and second topmost
@SP
M=M-1
'''
NOT = '''\
    // not
@SP
A=M-1
M=!M    // nots the topmost stack location
'''
GT = '''\
    // greater than
@SP     // set a-reg to SP
A=M-1   // set a to topmost item in stack
D=M     // save topmost stack item
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
    // less than
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
    // push constant {0}
@{0}     // given the command push constant [num], goes to the given [num]
D=A     // saves this number
@SP     // goes to stack pointer pointer
A=M     // goes to stack pointer
M=D     // adds the saved number to the stack
@SP     // goes to stack pointer pointer
M=M+1   // increments stack pointer
'''
END = '''\
    // end loop
(END)
@END
0;JMP
'''
PUPOI = '''\
    // push {0} {1}
@{0}    // sets A to the pointer of the register it will read from (local,
        // argument, etc.)
D=A     // saves this location
@{1}    // goes to the address part of the code, for example given push local
        // 5, it will go to the memory location 5
A=A+D   // adds together the register and adress to get to the address it
        // should be at
D=M     // saves the contents of this memory location
@SP     // goes to memory location that points to stack pointer
A=M     // goes to stack pointer
M=D     // sets register to saved value
@SP     // goes to memory location that points to stack pointer
M=M+1   // incrememts stack pointer
'''
PUSH = '''\
    // push {0} {1}
@{0}    // sets A to the pointer of the register it will read from (local,
        // argument, etc.)
D=M     // saves the location stored in this pointer
@{1}    // goes to the address part of the code, for example given push local
        // 5, it will go to the memory location 5
A=A+D   // adds together the register and adress to get to the address it
        // should be at
D=M     // saves the contents of this memory location
@SP     // goes to memory location that points to stack pointer
A=M     // goes to stack pointer
M=D     // sets register to saved value
@SP     // goes to memory location that points to stack pointer
M=M+1   // incrememts stack pointer
'''

PUSTAT = '''\
    // push static {1}
@{0}.{1}    // creates variable [filename].[num]
D=M     // sets d to contents of m
@SP     // goes to stack pointer pointer
A=M     // goes to stack pointer
M=D     // pushes contents of variable to stack
@SP     // goes to stack pointer pointer
M=M+1   // increments
'''
POP = '''\
    // pop {0} {1}
@SP     // goes to register that points to stack pointer
A=M-1   // goes to top of stack
D=M     // saves top of stack
@popval // creates variable
M=D     // stores top value of stack in variable
@SP     // goes to stack pointer pointer
M=M-1   // decrements stack pointer
@{0}    // given pop [register] [address], goes to pointer of beginning of
        // given register
D=M     // saves location
@{1}    // goes to [address]
A=A+D   // goes to [address] + [register]
D=A     // saves location
@location   // creates variable
M=D     // saves location in variable
@popval // goes to variable that contains popped value
D=M     // retrieves popped value
@location   // goes to variable that holds location where popped value should
        // be stored
A=M     // goes to location where popped value should be stored
M=D     // sets location to popped value
'''
POSTAT = '''\
    // pop static {1}
@SP     // goes to register that points to stack pointer
A=M-1   // goes to top of stack
D=M     // saves top of stack
@{0}.{1}    // goes to variable [filename].[number]
M=D     // saves location in variable
@SP     // goes to stack pointer pointer
M=M-1   // decrements stack pointer
'''
POPOI = '''\
    // pop {0} {1}
@SP     // goes to register that points to stack pointer
A=M-1   // goes to top of stack
D=M     // saves top of stack
@popval // creates variable
M=D     // stores top value of stack in variable
@SP     // goes to stack pointer pointer
M=M-1   // decrements stack pointer
@{0}    // given pop [register] [address], goes to pointer of beginning of
        // given register
D=A     // saves location
@{1}    // goes to [address]
A=A+D   // goes to [address] + [register]
D=A     // saves location
@location   // creates variable
M=D     // saves location in variable
@popval // goes to variable that contains popped value
D=M     // retrieves popped value
@location   // goes to variable that holds location where popped value should
        // be stored
A=M     // goes to location where popped value should be stored
M=D     // sets location to popped value
'''

# dictionary of commands
cmddict = {
    'add': ADD,
    'sub': SUB,
    'neg': NEG,
    'eq': EQ,
    'gt': GT,
    'lt': LT,
    'and': AND,
    'or': OR,
    'not': NOT,
    'push constant': PCONST,
    'push static': PUSTAT,
    'pop static': POSTAT,
    'pop pointer': POPOI,
    'push pointer': PUPOI,
    'push': PUSH,
    'pop': POP,
    'end': END
}


def parser(line):
    '''parses each line and returns what kind of command it is, along with the
    arguments that kind of command needs.'''
    matchCmd = cmd.match(line)
    if matchCmd:
        command = matchCmd.group(1)
        register = matchCmd.group(2)
        address = matchCmd.group(3)
        if register is None and address is None:
            return 'arithmetic', command
        elif command == 'pop':
            if register == 'static':
                return 'popStatic', inputfilename, address
            elif register == 'pointer' or register == 'temp':
                return 'popPointer', register, address
            else:
                return 'pop', register, address
        elif command == 'push':
            if register == 'constant':
                return 'pushConstant', address
            elif register == 'static':
                return 'pushStatic', inputfilename, address
            elif register == 'pointer' or register == 'temp':
                return 'pushPointer', register, address
            else:
                return 'push', register, address
    else:
        return 'o'


def arithmetic(command):
    global num
    cmdlist.append(cmddict[command].format(num))
    num += 1


def pushConstant(address):
    cmdlist.append(cmddict['push constant'].format(address))


def pushStatic(filename, address):
    cmdlist.append(cmddict['push static'].format(Path(filename).stem, address))


def push(register, address):
    '''figures out which register to push to before writing the command'''
    if register == 'local':
        reg = 'LCL'
    elif register == 'argument':
        reg = 'ARG'
    elif register == 'this':
        reg = 'THIS'
    elif register == 'that':
        reg = 'THAT'
    cmdlist.append(cmddict['push'].format(reg, address))


def pushPointer(register, address):
    if register == 'temp':
        reg = '5'
    elif register == 'pointer':
        reg = '3'
    cmdlist.append(cmddict['push pointer'].format(reg, address))


def pop(register, address):
    if register == 'local':
        reg = 'LCL'
    elif register == 'argument':
        reg = 'ARG'
    elif register == 'this':
        reg = 'THIS'
    elif register == 'that':
        reg = 'THAT'
    cmdlist.append(cmddict['pop'].format(reg, address))


def popStatic(filename, address):
    cmdlist.append(cmddict['pop static'].format(Path(filename).stem, address))


def popPointer(register, address):
    if register == 'temp':
        reg = '5'
    elif register == 'pointer':
        reg = '3'
    cmdlist.append(cmddict['pop pointer'].format(reg, address))


def other():
    '''whitespace, comments, etc. isn't added to the hack code'''
    pass


# each function in this list other than 'other' writes the corresponding code
# to the output file
funcs = {
    'arithmetic': arithmetic,
    'pushConstant': pushConstant,
    'pushPointer': pushPointer,
    'push': push,
    'pop': pop,
    'popPointer': popPointer,
    'popStatic': popStatic,
    'pushStatic': pushStatic,
    'o': other
}

# reads inputfile and sends each line to the parser, then uses the parser's
# output to send the right arguments to the right function which then returns
# the correct translated code, which is then written to the outputfile. after
# the entire program has been translated, an infinite loop is added to the end
# of the file to terminate the code and prevent any other code from being run.
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
# just a nice touch to make it more user friendly
print('''
      =================================================================
                            Translation Complete!
      =================================================================
      ''')


# pytest for regex.
def test_answer():
    tsts = [('push constant 1', ('push', 'constant', '1')),
            ('    eq', ('eq', None, None)),
            ('not   // asddsdf', ('not', None, None))]
    for test in tsts:
        output = cmd.match(test[0])
        assert output is not None, test[0]
        for group in range(1, 3):
            assert output.group(group+1) == test[1][group]
