# Running aws-c-common proof by CBMC
Running CBMC Batch jobs for aws-c-common without using CBMC-Batch.

## Installing the lastest CBMC
In order to start the CBMC Batch jobs and check results locally, you need to have installed CBMC on your local environment.

You can use `cbmc-install.sh` to install the latest CBMC.
```bash
./cbmc-install.sh
```
The default path to install `cbmc` bin file is `/usr/bin`.

## Running Locally

You can start the CBMC Batch jobs locally by running
```bash
python3 bench_table.py
```

If you wish to change any configurations of `goto-cc`, `goto-instrument`, `cbmc`, please open and modify [Makefile.common](../../templates/template-for-repository/proofs/Makefile.common).

For each benchmark, the logging output is summarized by an `log` file. You can also check logging file during each step at `logs` folder.

## Check the results

Once you done running `bench_table.py`, it will automatically generate a file named `aws-cbmc.csv`.

## Process to for each benchmark running

- Tools used
    - `goto-cc`
        - `goto-cc` reads the source code, and generates a goto-binary file as an output.
        - It works for compilation and simplifies the program. E.g. remove program side effect (j = i++), control flow made explicit (continue, break -> goto), loops simplify to one form (while loop)
    - `goto-instrument`
        - `goto-instrument` reads a goto-binary, performs a given program transformation, and then writes the resulting program as goto-binary.
    - `cbmc`
        - Bounded model checking for ANSI C
        - CBMC detects all possible failed properties as default. It will terminate until all those violations determined.
- Project and source file structure
    - Project source files included are loacted inside `aws-c-common/source` directory
    - Proof source files included are loacted inside `proof` directory and `cbmc/sources` directory
    - Those files are specified for each benchmark inside each `../<bench_name>/makefile`
- Steps
    1. Compile (with link) the harness code into goto file via `goto-cc`
        - Example
            - Inputs
                - <benchmark_name>_harness.c
                - sources/make_common_data_structures.c
                - stubs/error.c
                - ...
            - Output: proof1.goto
    2. Remove function body if neccesary 
        - If not, copy proof1.goto into proof2.goto
        - Otherwise, use `goto-instrument` to perform remove function body
    2. Compile the project source files into goto file via goto-cc
        - Example
            - Inputs: source/common.c
            - Output: project1.goto
    2. Use goto-instrument to perform program transformation (use flag --remove-function-body)
        - Remove function such as `aws_default_allocator`, …
            - Input project1.goto
            - Output project2.goto
    2. Invoke goto-cc to set the entry point (--funtion aws_add_size_checked_harness)
        - Link project and proof sources into the proof harness
            - Input
                - proof2.goto
                - project2.goto
            - Output
                - <benchmark_name>_harness.c1.goto
    2. Optionally fill static variable with unconstrained values
        - The --nondet-static flag causes CBMC to initialize static variables with unconstrained value (ignoring initializers and default zero-initialization).
        - If not, goto-instrument with --nondet-static <benchmark_name>.c1.goto as <benchmark_name>.c2.goto
    2. Use goto-instrument to omit unused functions (sharpens coverage calculations)
        - Flag used `-drop-unused-functions`
            - Function Pointer Removal
            - Virtual function removal
            - Cleaning inline assembler statements
            - Removing unused functions
        - Input: <benchmark_name>_harness.c2.goto
        - Output: <benchmark_name>_harness.c3.goto
    2. Use goto-instrument to omit initialization of unused global variables (reduces problem size)
        - Flag used --slice-global-inits
        - Input: <benchmark_name>.c3.goto
        - Output: <benchmark_name>.c4.goto
    2. Copy <benchmark_name>.c4.goto into goto file as the final result
