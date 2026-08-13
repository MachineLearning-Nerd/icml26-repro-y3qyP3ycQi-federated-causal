# Output artifacts

The checked-in `claim*.json` files and `verdict.json` are the authoritative
machine-readable snapshot from run `ea6fbba7`.

The verifier also generates `sim_raw.csv` and `.openresearch/artifacts/` on a
fresh run. Those files are intentionally ignored because they are generated
intermediate data, not the publication gate. The old `verify_run.log` was a
historical toy-proxy log and has been removed to avoid confusing it with the
authoritative full verifier.
