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
@SCREEN  // a points to memory word mapped to 16 leftmost 
         // pixels of top row
D=A      // d = a
@i       // m represents new var i
M=D      // i = address of 16 leftmost pixels of first row

// figures out how large the screen is and stores it in a var
@KBD     // a points to address of keyboard
D=A      // d = a
@i       // m represents i
M=M-D    // i=i-address of keyboard
D=M      // d = i
@screensize
M=D

@SCREEN  // a points to memory word mapped to 16 leftmost 
         // pixels of top row
D=A      // d = a
@i       // m represents new var i
M=D      // i = address of 16 leftmost pixels of first row

// begin loop, end loop if screen is full
(LOOP)   // loop starts here
@i
D=A
@screensize
D=D-M
D;JEQ

// check if kbd pressed
@KBD     // a points to address of keyboard
D=A      // d = a
@i       // m represents i
M=M+D    // i=i+address of keyboard
@KBD     // m represents keyboard mem word
D=M      // d = whichever key is being pressed
@FILL    // sets up jump
D;JGT    // if kbd pressed jump to filling teh screen
@CLEAR   // sets up jump
D;JEQ    // if kbd not pressed jump to clearing the screen

// fill 16 pixels of screen represented by i
(FILL)
@i       // a points to i, m represents i
A=M      // a = contents of i
M=-1     // sets 16 pixels represented by i to black 

// clear 16 pixels of screen represented by i
// (CLEAR)
// @i       // a points to i, m represents i
// A=M      // a = contents of i
// M=0      // sets 16 pixels represented by i to white

// increments i and restarts loop
@i       // m represents i
M=M+1    // i+=1
@LOOP    // sets up jump
0;JMP    // jumps back to beginning of loop

// infinite end loop
(END)    
@END
0;JMP
