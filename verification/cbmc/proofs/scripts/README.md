# Running aws-c-common proof by CBMC
Running CBMC Batch jobs for aws-c-common without using CBMC-Batch.

## Installing the lastest CBMC
In order to start the CBMC Batch jobs and check results locally, you need to have installed CBMC on your local environment.

You can use `cbmc-install.sh` to install the latest CBMC.
```bash
./cbmc-install.sh
```
The default path to install `cbmc` bin file is `/usr/bin`.
[link](../../templates/template-for-repository/proofs/Makefile.common) 

## Running Locally

You can start the CBMC Batch jobs locally by running
```bash
python3 bench_table.py
```

If you wish to change the configuration of `cbmc`, please 

## Check the results

Once you done running `bench_table.py`, it will automatically generate a file named `aws-cbmc.csv`.

## Process to for each benchmark running

- Tool used
    - goto-cc
        - goto-cc reads source code, and generates a goto-binary.
        - It works for compilation and simplifies control flow
    - goto-instrument
        - goto-instrument reads a goto-binary, performs a given program transformation, and then writes the resulting program as goto-binary on disc.
    - cbmc
        - Bounded model checking for ANSI C
