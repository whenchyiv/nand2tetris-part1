# Hack VM Parser Project 1

## TODO

- [ ] write automated tests for the parser.py
- [ ] write automated tests for the codewriter.py
- [ ] write automated tests for full script (interpres.py)
- [ ] codewriter module
    - [x] fix codewriter poppush module based on spec on p. 186; not currently right
    - [x] fix push pop logic to use the values at the pointer addresses and not overwrite the pointers (duh).
    - [x] fix push pop logic so that it handles different segments correctly.
    - [x] arithmetic asm generation
        - [x] fix sub logic.
        - [ ] add comparison commands
        - [ ] add logical commands
        - [ ] test with StackTest.vm
- [x] Create main script that calls into the codewriter and runs the whole thing (interpres.py)
