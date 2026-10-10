# Part 1 Experiments

These scripts are written to import the project-root modules:
`bruteforce.py`, `bsgs.py`, `pollard_rho.py`, `pohlig_hellman.py`,
`index_calculus.py`, `linear_sieve.py`, `common.py`, and
`assignment_data.py`. They do not duplicate or modify the solvers.

## Run

From the Part 1 project root:

```bash
python experiments/exp_bruteforce_extrapolate.py --max-seconds 15
python experiments/exp_bsgs_memory.py --generated
python experiments/exp_bsgs_memory.py --include-c
python experiments/exp_rho_runs.py --runs 10
python experiments/exp_ic_B.py --instances F --bounds 100,140,180
python experiments/exp_ic_B.py --instances G --bounds 180,220 --run-heavy
python experiments/exp_ls_vs_ic.py --instance G --run-heavy
python experiments/run_experiments.py --quick
python experiments/run_experiments.py --full
```

## Outputs

All scripts create `results/` at the project root and write CSVs there:
- `exp_bruteforce.csv`
- `exp_bsgs_memory.csv`
- `exp_rho_runs.csv`
- `exp_ic_B.csv`
- `exp_ls_vs_ic.csv`

Rows include seeds, parameters, verification status, wall-clock time and
solver-reported statistics where available. Exceptions are recorded in the
CSV rather than silently discarded. The generated BSGS cases are reproducible
and are labelled `generated_*`; they do not replace assignment instances.

## Experimental care

- Brute-force D is an extrapolation, never an actual solve.
- BSGS time and `tracemalloc` memory are measured in separate executions,
  because allocation tracing affects timing.
- Pollard-rho reports every seeded run; the mean/SD summary uses successful
  runs only and reports the success count so failures remain visible.
- Index-calculus/linear-sieve runs use dense modular Gaussian elimination in
  the current solver modules. Larger bounds can consume substantial time and
  memory; heavy runs are opt-in and print progress.
- `group_ops` is the solver's own counter. The experiment also records
  independently measured wall time; counters from different algorithms should
  be interpreted according to each implementation's counting convention.
- The data file in this project labels these as reference/self-generated
  instances. Replace with instructor-provided instances if those differ.
