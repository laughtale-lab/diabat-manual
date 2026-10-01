# Diabat 2.0 User Manual — source and publishing

This repository is the single source of truth for the **LaTeX** Manual. PDF
compilation and GitHub Pages publication are automated; do not edit generated
PDF/HTML files or introduce a separately maintained Markdown copy.

**Planned permanent links (only live after the first successful GitHub Pages deployment):**

- **Online docs / initial PDF landing page:** https://laughtale-lab.github.io/diabat-manual/
- **Latest PDF (direct file):** https://laughtale-lab.github.io/diabat-manual/diabat.pdf

**Local build:** `bash tools/build-pdf.sh`, followed by
`python3 tools/validate-pdf.py main.pdf` (requires Poppler utilities).
Every push to `main` compiles the PDF and, once Pages is enabled, publishes the
PDF together with the current website. Pull requests compile and test without
publishing. See [Phase 1 deployment instructions](docs/DEPLOYMENT.md) and the
[official Diabat README snippet](docs/DIABAT-README-SNIPPET.md).

The `web/landing/` directory is a small temporary site; a later **independent**
`latex2md` release and mdBook build will replace its content. The original
LaTeX tree is not reorganized for these tools. Only LaTeX sources are edited.

---

## Original supplied-source notes

This edition revises the uploaded legacy LaTeX Manual. The original document's
12-point book class, page geometry, line spacing, Times-family prose, title
formatting, page headers and footers, keyword-description table macro, and
Example/Script counters and basic code-listing design are retained. The listing
language extends the original syntax coloring to double-quoted red strings and
actual v2.0 job/block names. Only the explicitly requested cover, seven chapter
organization, appendices, and technical corrections have been changed.

## Contents

- `main.tex` is the canonical LaTeX entry point. `main-public.tex` is a convenience
  wrapper for editors that expect the previous filename.
- `preamble/`, `frontmatter/`, `config/`, `chapters/`, and `assets/` contain all
  editable document sources and provided images.
- `examples/templates/` contains the published source-tree templates with
  double-quoted string literals.
- `examples/release/` contains selected examples from the *public* binary
  distribution with the same string-delimiter normalization.
- `examples/tutorials/` contains the original input files for the four named
  article applications, together with selected published Hamiltonians. The
  Diabat scripts have only their string delimiters normalized. No quantum
  chemistry output or absent orbital intermediates have been invented.
- `references-diabat.bib` contains the complete bibliography supplied by the
  author, with only the manuscript and dataset bibliographic records appended.
- `references-build.bib` is derived solely from the cited records in that file,
  excluding damaged Zotero attachments and unrelated export fields. Biblatex
  reads this clean selection to avoid malformed encoding from attachment paths;
  when adding a new citation, copy its canonical bibliographic fields from the
  original supplied bibliography into the build selection.

## Compiling

Run from the top-level project directory:

```sh
latexmk -pdf -pdflatex='pdflatex -interaction=nonstopmode %O %S' main.tex
```

The supplied preamble uses `biblatex` with the `biber` backend, because this
build environment does not provide the original BibTeX executable. The
reference-list appearance follows the legacy biblatex defaults. Compile
with pdfLaTeX and Biber, both available in Overleaf's standard TeX Live
installations. The source bundle is self-contained with respect to TeX assets;
Diabat and external quantum-chemistry data are not required to render the PDF.

## Source and verification boundaries

The example Diabat files are copied from public v2.0 release templates, public
binary-package examples, and the uploaded paper dataset; their input content has been preserved where required. The accompanying
QC input originals are copied unchanged from the uploaded paper dataset.

The paper-data archive supplied for this work has SHA-256:
`39a5ff755d8a03e7a4946166ccfc942a864933b369f699ac7027023cbcf4b115`.
The original paper dataset is CC BY 4.0 (copyright 2026 Yu-Chen Wang).
Its full archive remains available at https://doi.org/10.5281/zenodo.23025244.

**Execution limitations:** The released binary requires Intel MKL, Intel MPI,
Intel OpenMP, and Intel Fortran shared libraries. The current editing machine
lacks those runtimes. The paper dataset also does not include all intermediate
GBW, Molden, formatted-checkpoint, or original external-program log files for
independent reruns. No Diabat or external QC numerical recalculation is claimed.
The manual's examples are source-checked and should be tested in a supported
runtime before using their numerical results as new benchmarks.

## Licensing

Manual text: CC BY 4.0, see LICENSE. Dataset inputs reproduced from the
paper-data archive: CC BY 4.0 with the original author credited. Software
and third-party quantum chemistry programs retain their own licenses.

The `examples/display/` files are LaTeX-only listings with generated, linked grey first-line captions. Use executable inputs from `examples/release/` or `examples/tutorials/`, never the display wrappers.

## Refined edition notes

This refinement preserves the original typography and keyword-table/listing macros.
The cover banner image has been cropped only around its transparent margins;
its original pixel artwork remains in `assets/banner_bold.png`. The interior
cover uses the unmodified supplied `assets/inner_cover_bold.png` artwork on white.
An explicit source path precedes every displayed binary-distribution example.
The displayed `.lst` examples contain LaTeX markup used only for caption and
comment colors; use the corresponding `.inp` files from the binary distribution
for actual calculations. The `prefix` keyword is intentionally not documented.

A complete PDF build uses pdfLaTeX and Biber. Example:

```sh
latexmk -pdf -pdflatex='pdflatex -interaction=nonstopmode %O %S' main.tex
```

Documentation consistency was checked against the supplied public examples and
the relevant public-module implementation. No new quantum-chemistry or numerical
Diabat benchmark execution is claimed by this documentation-only revision.

## Output-file and Phasefix refinement

The output-file entries use a same-size bold monospaced filename with a numbered label and an aligned description. Example headings have no terminal period or extra distribution label. The Phasefix background and optional output descriptions have been checked directly against the v2.0 public Phasefix registry, base wave-function routines, and Phasefix job implementation. No numerical Phasefix calculations were executed for this documentation update.
