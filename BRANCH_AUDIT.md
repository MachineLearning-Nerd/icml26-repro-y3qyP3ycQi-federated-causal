# Branch audit

## Before cleanup

The source repository exposed two remote branches:

| Branch | Tip before cleanup | Role |
| --- | --- | --- |
| `master` | `e39eef238865698013ae4d7cba7791dfa0663c71` | Publication surface, report, outputs, and the later marimo notebook merge |
| `orx/faithful-full-scale-baseline` | `72361e603111f8c1d3614e1cc4adf8fc1856db18` | Full-scale synthetic verifier and the recorded run lineage |

The `orx/*` tip was an ancestor of `master`, and the two trees were identical
at the cleanup snapshot. It therefore added no distinct publication content.

## After cleanup

- `master` is renamed to `main`.
- `orx/faithful-full-scale-baseline` is removed as a stale branch reference.
- `main` is the default and sole publication branch.
- The old branch role, run ID, and source commit are preserved in
  [`SOURCE_MANIFEST.md`](SOURCE_MANIFEST.md), `outputs/verdict.json`, and the
  commit history.
- Reachable commit author and committer identities are normalized to
  `MachineLearning-Nerd <MachineLearning-Nerd@users.noreply.github.com>`.

The final invariant is intentionally small: one descriptive repository, one
default branch, one documented publication surface, and explicit names for any
future audit branches.
