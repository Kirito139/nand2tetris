// TODO: Create loop for filling screen
// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.

// Put your code here.

@SCREEN     // a points to screen(16 leftmost pixels of top row)
D=A         // d = a
@i          // m represents new var i
M=D         // i = screen

// check if kbd pressed
(KBDCHECK)
@KBD        // m represents keyboard mem word
D=M         // d = whichever key is being pressed
@FILLCHECK  // sets up jump
D;JGT       // if kbd pressed check if screen full
@CLEARCHECK // sets up jump
D;JEQ       // if kbd not pressed check if screen empty


// if screen full check if kbd pressed, else fill screen
(FILLCHECK)
@KBD        // a points to keyboard
D=A         // d=address of kbd
@i          // m represents i
D=D-M       // d=address of kbd-i
@KBDCHECK
D;JEQ
@FILL
0;JMP

// if screen empty check if kbd pressed, else clear screen
(CLEARCHECK)
@SCREEN     // a points to SCREEN
D=A
@i          // m=i
D=D-M       // d=a-i
@KBDCHECK
D;JEQ
@CLEAR
0;JMP

// fill 16 pixels of screen represented by i
(FILL)
@i       // a points to i, m represents i
A=M      // a = contents of i
M=-1     // sets 16 pixels represented by i to black 
@i       // incrementation
M=M+1
@KBDCHECK
0;JMP

// clear 16 pixels of screen represented by i
(CLEAR)
@i       // a points to i, m represents i
M=M-1
A=M      // a = contents of i
M=0      // sets 16 pixels represented by i to white
@KBDCHECK
0;JMP
