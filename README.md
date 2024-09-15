# Introduction
This is my attempt on implementing a Brainfuck interpreter in Python with some addtional features.

# Features
- Standard Brainfuck interpreter
- A compiler or how you might call it. It removes unnessesary text and converts the brainfuck commands to index the right methode in an array
- a variable size cap for the individual cells which allows one to use custom cell sizes with no limits even in the negatives
- a varable array size with no limit even in the negatives

And some more not so relavent features

# Usage
The Interpreter can easily be used via the commandline in the format

**python interpreter.py [Brainfuck file] [parameters]**

for help with the interpreter consult the messy help menu accessed with -h or --help