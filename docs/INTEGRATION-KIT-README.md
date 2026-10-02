# Pin-ready integration kit: latex2md v0.1.2

This kit is preconfigured for the reviewed converter commit:

`d61fd12be59f40969a06af7f46aa236fcb88f55a`

Read **`docs/INTEGRATE-MDBOOK.zh-CN.md`** first. It contains the exact
commands for existing sibling clones in `~/github/`.

Unpack this kit only into a clean, new Manual feature branch. It does not
replace the production `.github/workflows/publish.yml` or edit LaTeX sources.
The preview workflow builds but never deploys. After human review, compare
and conditionally adopt `docs/publish-mdbook.yml.example` as the **single**
production workflow. `tools/latex2md.sha` is the reviewed converter commit;
the workflow also checks that the checkout really matches it.

The baseline file contains the *reviewed initial manual metrics*. Deliberate
future Manual updates can change these values; review the generated book and
adjust the baseline in the same Manual PR only when appropriate.
