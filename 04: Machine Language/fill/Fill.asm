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

(KEYBOARD)
    @KBD
    D=M
    @FILL_WHITE
    D;JEQ
    @FILL_BLACK
    D;JNE

(FILL_BLACK)
    @COLOR
    M=-1 // -1 = 1111111111111111
    @FILL
    0;JMP

(FILL_WHITE)
    @COLOR
    M=0
    @FILL
    0;JMP

(FILL)
    @8192
    D=A
    @MAXROW
    M=D
    @INDEX
    M=0
    @CURRENTROW
    M=0

(FILL_LOOP)
    @INDEX
    D=M
    @MAXROW
    D=M-D
    @KEYBOARD
    D;JEQ
    @SCREEN
    D=A
    @INDEX
    D=D+M
    @CURRENTROW
    M=D
    @COLOR
    D=M
    @CURRENTROW
    A=M
    M=D
    @INDEX
    M=M+1
    @FILL_LOOP
    0;JMP
