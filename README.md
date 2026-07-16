# Pre-Approval Website-Verification Tool

An AI-assisted tool that reads completed pre-approval application forms (PDF), verifies the request against the provider's public website, captures date-stamped evidence, and produces a review-ready report — for a human Pre-Approvals Reviewer to make the final decision.

**This tool does not approve or deny anything.** It gathers evidence and flags items for review.

## How it works

1. **Extract** — reads a PDF application, pulls structured fields (participant, provider, item, fee, checklist answers) using an LLM.
2. **Verify** — visits the provider's website, checks each website-verifiable checklist item, and captures evidence (whole-page screenshot + a labeled, highlighted screenshot per confirmed item), each burned with a visible timestamp and URL.
3. **Report** — generates a markdown report: request summary, rate comparison, per-criterion findings table, internal (non-website-verifiable) items, and the evidence appendix.

## Requirements

- Python 3.12+
- An OpenAI API key set as `OPENAI_API_KEY`
- Playwright with Chromium installed (`pip3 install playwright && playwright install`)

## Setup

```bash
pip3 install openai pyyaml pypdf playwright
playwright install
export OPENAI_API_KEY="your-key-here"
```

## Running the tool

Run the full pipeline (extract → verify → report) on a sample:

```bash
python3 src/run_pipeline.py "samples/Sample-01---Community-Class-GallopNYC.pdf" community_classes
```

Category keys match the filenames in `config/categories/`:
`community_classes`, `coaching`, `memberships`, `hri`, `otps`, `transition_program`, `appeals`

Output is saved to:
- `output/<name>_extracted.json` — structured fields pulled from the form
- `output/verification_<timestamp>.json` — per-item verification results
- `output/evidence/` — all screenshots (whole-page + targeted)
- `output/reports/report_<participant>_<timestamp>.md` — the final report

## How to add a new form/checklist

1. Create a new file in `config/categories/<new_category>.yaml`
2. List the fields to extract from that form under `fields:`
3. List each checklist item under `checklist:`, marking each `verifiable: website` or `verifiable: internal`
4. Run the pipeline with your new category key — no code changes needed

## Limitations & assumptions

- **Website access is not guaranteed.** Some provider sites (notably Amazon)
cat README.md | head -20
cat README.md | head -20
cat > README.md << 'MDEOF'
# Pre-Approval Website-Verification Tool

An AI-assisted tool that reads completed pre-approval application forms (PDF), verifies the request against the provider's public website, captures date-stamped evidence, and produces a review-ready report — for a human Pre-Approvals Reviewer to make the final decision.

**This tool does not approve or deny anything.** It gathers evidence and flags items for review.

## How it works

1. **Extract** — reads a PDF application, pulls structured fields (participant, provider, item, fee, checklist answers) using an LLM.
2. **Verify** — visits the provider's website, checks each website-verifiable checklist item, and captures evidence (whole-page screenshot + a labeled, highlighted screenshot per confirmed item), each burned with a visible timestamp and URL.
3. **Report** — generates a markdown report: request summary, rate comparison, per-criterion findings table, internal (non-website-verifiable) items, and the evidence appendix.

## Requirements

- Python 3.12+
- An OpenAI API key set as `OPENAI_API_KEY`
- Playwright with Chromium installed (`pip3 install playwright && playwright install`)

## Setup

```bash
pip3 install openai pyyaml pypdf playwright
playwright install
export OPENAI_API_KEY="your-key-here"
```

## Running the tool

Run the full pipeline (extract → verify → report) on a sample:

```bash
python3 src/run_pipeline.py "samples/Sample-01---Community-Class-GallopNYC.pdf" community_classes
```

Category keys match the filenames in `config/categories/`:
`community_classes`, `coaching`, `memberships`, `hri`, `otps`, `transition_program`, `appeals`

Output is saved to:
- `output/<name>_extracted.json` — structured fields pulled from the form
- `output/verification_<timestamp>.json` — per-item verification results
- `output/evidence/` — all screenshots (whole-page + targeted)
- `output/reports/report_<participant>_<timestamp>.md` — the final report

## How to add a new form/checklist

1. Create a new file in `config/categories/<new_category>.yaml`
2. List the fields to extract from that form under `fields:`
3. List each checklist item under `checklist:`, marking each `verifiable: website` or `verifiable: internal`
4. Run the pipeline with your new category key — no code changes needed

## Limitations & assumptions

- **Website access is not guaranteed.** Some provider sites (notably Amazon) serve anti-bot challenge pages or 404s to automated browsers. The tool detects these cases and degrades to "Needs Review" rather than fabricating findings. The `exclusion_list` check for HRI/OTPS runs as a deterministic code check against the form's stated item text, so it works even when the live page can't be read.
- **"Fees identical for OPWDD/non-OPWDD"** and similar negative claims are rarely provable from a public website (a site can fail to show a special price, but can't prove one doesn't exist elsewhere) — these are intentionally marked "Needs Review" rather than "Met" in most cases.
- **Appeals** currently re-run only a small appeal-specific checklist rather than dynamically loading the original category's full checklist. A production version would load both configs and merge them.
- **No OCR** — this version assumes forms are text-based PDFs (all 10 samples are). Scanned/image-only forms would need an OCR step added to `extract.py`.
- **No internal system integration** — budget approval, Life Plan matching, and other "internal" items are always flagged for the human reviewer, never inferred.
- **This is a take-home evaluation build**, not production software: no authentication, no queuing/retry logic for flaky sites, no test suite, and evidence storage is local disk rather than an audit-grade document store.

## Sample outputs

Three fully-run examples are committed under `output/`:
- Sample-01 (Community Class, GallopNYC) — clean case, most items Met
- Sample-07 (HRI, Laptop) — demonstrates the exclusion-list catch
- Sample-10 (Appeal, Gracie Barra) — demonstrates the appeals category

## Human-in-the-loop

A human Pre-Approvals Reviewer always makes the final approve/deny decision. Every report ends with an explicit statement to that effect.
