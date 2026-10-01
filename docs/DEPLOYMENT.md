# Phase 1: first GitHub publication and verification

This project intentionally does **not** create or change the `latex2md` repository,
install mdBook, or connect Overleaf yet. The original LaTeX files are left intact.

## 1. Local validation

Use a machine with TeX Live 2025, `latexmk`, `pdflatex`, `biber`, and the Poppler
`pdfinfo` and `pdftotext` utilities. From the repository root:

```bash
bash tools/build-pdf.sh
python3 tools/validate-pdf.py main.pdf --min-pages 100
python3 -m unittest discover -s tests -v
bash tools/stage-pages.sh
python3 tools/validate-site.py site main.pdf
```

The PDF produced from the initial supplied source has 113 pages in the reference
local TeX Live 2025 environment; output bytes may differ because of toolchain
patch levels, fonts, and PDF metadata. Compare structure and rendered pages, not
only the byte hash. Existing `fancyhdr` and some box warnings are deliberately
not fixed as part of CI setup.

## 2. Create the public repository (requires organization write permission)

In the GitHub web UI, create an **empty, public** repository named
`laughtale-lab/diabat-manual`, with **no** README, license, or `.gitignore`
initialization. These files are already prepared. Ensure the default branch is
`main`. In this extracted directory:

```bash
git init -b main
git add .
git status --short     # check: no main.pdf, site/, TeX cache files
git commit -m "Add Diabat 2.0 LaTeX manual and PDF publishing workflow"
git remote add origin https://github.com/laughtale-lab/diabat-manual.git
git push -u origin main
```

Alternatively, if GitHub CLI is installed and authenticated with organization
permissions, run `gh repo create laughtale-lab/diabat-manual --public --source .
--remote origin --push` after the initial local commit. Do not accidentally
create a second README or change the license through a web template.

## 3. Enable GitHub Pages and verify Actions

In the new repository, open **Settings -> Pages -> Build and deployment ->
Source -> GitHub Actions**. If the initial push ran before Pages was enabled,
rerun **Actions -> Build and publish the Diabat Manual -> Run workflow** on
`main`. GitHub's official Pages actions use a single staged release artifact.
No personal access token is required for ordinary builds and Pages deployment;
this workflow uses short-lived GitHub-provided credentials.

Make sure Actions are enabled for the repository/organization and that the
`github-pages` environment, if protection rules were added, permits deployments
from `main`. Pull requests compile and run tests but never publish.

Expected jobs in Actions: **Compile and validate the PDF**, then **Atomically
deploy the verified release**. If compilation, the PDF validator, or site
staging fails, there is no deployment from that run; the last successful
Pages deployment remains live. A stale run also skips deployment when `main`
has moved to a more recent commit.

## 4. Smoke test *after* the first successful deployment

Run these commands locally; replace nothing in the URLs:

```bash
curl -fIL https://laughtale-lab.github.io/diabat-manual/
curl -fIL https://laughtale-lab.github.io/diabat-manual/diabat.pdf
curl -fsSL https://laughtale-lab.github.io/diabat-manual/diabat.pdf -o /tmp/diabat-public.pdf
pdfinfo /tmp/diabat-public.pdf | grep -E '^(Pages|Page size|File size):'
```

Check that the homepage links to `./diabat.pdf`, the PDF opens in a browser,
the downloaded file is complete, and `build-info.json` reports the expected
source commit. GitHub Pages ordinarily serves `.pdf` as `application/pdf`;
the browser's own PDF-viewer preferences can still force downloads. The two
public URLs are **planned addresses**, not confirmed live until this test passes.

## 5. Link the official Diabat software README

Only after deployment and the smoke test succeed, paste the Markdown in
`docs/DIABAT-README-SNIPPET.md` into the `laughtale-lab/diabat` repository's
README (via its own change/review). Do not link to the expiring CI artifact.

## Versioning / future phases

- The only editable manual content is still the LaTeX tree (`main.tex` and its
  existing `config/`, `preamble/`, `frontmatter/`, `chapters/`, `appendices/`,
  `assets/`, `examples/`, and `.bib` dependencies).
- `tools/build-pdf.sh` remains the single PDF build command.
- In phase 2, create and release the independent `latex2md` tool. In phase 3,
  check out a **tested converter release commit**, run conversion, validate
  references/assets, install a pinned mdBook, and build HTML **before**
  invoking `tools/stage-pages.sh`. Then set `SITE_SOURCE` to the mdBook output
  folder, and set `SITE_MODE=mdbook`. Keep `diabat.pdf` at the website root.
- Do not upload Pages until **all** build and validation steps succeed. One
  stage directory means that HTML and the PDF are always deployed from the
  **same manual commit**. Never generate Markdown into tracked Overleaf files.
- Avoid checking in large/generated PDF artifacts or editing generated HTML.
  GitHub Releases may store versioned PDF snapshots once a release policy is set.
- As a further hardening step after the initial successful CI run, pin GitHub
  Actions to reviewed full commit SHAs and periodically upgrade intentionally.
