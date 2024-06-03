# CPsmell：an inter-language design smell detection toolkit

CPsmell can detect inter-language design smell  in multi-language software written in the combination of Python and C/C++.
```text

├───example // examples of design smell instances
|
├───utils // toolkit
|    |
|    ├───c_files // c/c++ files
|    |
|    ├───py_files // python files
|    |
|    ├───pybind11 // pybind11 detector and results
|    |
|    ├───python_c // python/c api detector and results
|    |
|    ├───astChecker.py // custom abstract syntax tree
|    |
|    ├───customast.py // parse python code into an abstract syntax tree
|    |
|    ├───codesmell_detection.py // check 8 inter-language design smells
|    |
|    ├───srcml_parse.py // parse c/c++ code into a xml file
|    |
|    ├───files_handler.py // divide source code files into python files and c/c++ files
|    |
|    └───configuration.py // set thresholds and sensitive words 

