# Hack VM Parser Project 1

## TODO

- [x] Fix handling of arg1 and arg2 properties on the Parser class. Currently cannot be used to check if e.g. the command has no arg2 because it will throw an error. Need to first check if the tokens even exist.
- [x] strip out blank lines from the file
- [x] add comment handling
- [ ] complete main loop file parsing and handling.
- [ ] write automated tests for the parser.py
- [ ] Add an iterator that lets us iterate over the lines as a python for loop? Rather than having to do a while or similar?
    1.  Define a class property using `@property`.
    2.  Implement the `__iter__` method in the class. This method should return an iterator object.
    3.  Optionally, implement the `__len__` method to return the number of items in the iterable.

    ```python
    class MyClass:
        def __init__(self):
            self._my_list = [1, 2, 3]

        @property
        def my_prop(self):
            return self._my_list

        def __iter__(self):
            return iter(self._my_list)

        def __len__(self):
            return len(self._my_list)
