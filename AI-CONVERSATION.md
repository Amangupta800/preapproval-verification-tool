# Tools & Models Used

- Claude (Claude Sonnet, via claude.ai chat interface) — main planning, code generation, debugging assistant throughout the build
- OpenAI GPT-4o (via API, `gpt-4o` model) — used at runtime by the tool itself for PDF field extraction and website checklist verification
- Playwright (Chromium) — headless browser automation for website capture and evidence screenshots

---

# The Conversation

[Paste the full conversation below this line]
Claude finished the response

Orchestrated data parsing and structured JSON conversion strategy
Orchestrated data parsing and structured JSON conversion strategy
This is excellent — genuinely great result. Look at what you got for free:

Every field extracted cleanly (name, age, provider, URL, fee, duration)
The checkbox marks (☑ = checked, ☐ = unchecked) came through as actual text, which means you can parse YES/NO answers programmatically without any image analysis
Two pages, both readable
This confirms: plain pypdf text extraction is enough for this whole project. No OCR, no image parsing needed. That simplifies your build a lot.

Next: build the category config files
Now we lock in the checklist logic per §5 of the brief, starting with Community Classes since you already have real sample text to validate it against.

Create the config folder and first file:

bash
mkdir -p config/categories
nano config/categories/community_classes.yaml
Paste this in (this is transcribed directly from §5 of the brief, cross-checked against what you just extracted from Sample-01):

yaml
category: community_classes
display_name: "Community Class"
fields:
  - participant_name
  - participant_age
  - fi_coordinator_name
  - broker_name
  - class_name
  - provider_name
  - website_url
  - subject_area
  - fee_per_session
  - duration_per_session

checklist:
  - id: open_to_public
    label: "Class is open to and attended by the broader public"
    verifiable: website

  - id: published_fees
    label: "Class has published fees"
    verifiable: website

  - id: identical_pricing
    label: "Fees are identical for OPWDD and non-OPWDD individuals"
    verifiable: website
    note: "Website can rarely prove this positively — mark 'Needs Review' unless site shows explicit two-tier pricing that contradicts it"

  - id: subject_based
    label: "Class is subject-based (Art, Dance, Martial Arts, Cooking, etc.)"
    verifiable: website

  - id: no_college_credit
    label: "Class does not provide college credits"
    verifiable: website

  - id: not_clinical
    label: "Class is not clinical/therapy in nature"
    verifiable: website

  - id: schedule_published
    label: "A published schedule of the class exists"
    verifiable: website

  - id: fee_match
    label: "Published fee matches Fee per Session stated on form"
    verifiable: website

  # Internal items — website cannot verify these, must be flagged not guessed
  - id: budget_approved
    label: "Community classes currently approved in the budget"
    verifiable: internal

  - id: community_inclusion
    label: "Class provides opportunity for community inclusion"
    verifiable: internal

  - id: health_safety
    label: "Class accommodates individual's health/safety needs"
    verifiable: internal

  - id: independence
    label: "Class increases independence or substitutes for human assistance"
    verifiable: internal

  - id: exclusive_benefit
    label: "Class is NOT provided exclusively for the participant's benefit"
    verifiable: internal

  - id: dd_only_setting
    label: "Class is NOT in a setting accessed only by people with DD"
    verifiable: internal

  - id: staff_run
    label: "Class is NOT run by OPWDD/provider-agency staff in official capacity"
    verifiable: internal

  - id: opwdd_grounds
    label: "Class is NOT located on grounds where OPWDD services are normally provided"
    verifiable: internal

  - id: medicaid_duplicate
    label: "Class does NOT duplicate Medicaid state plan/HCBS waiver services"
    verifiable: internal

  - id: education_duplicate
    label: "Class does NOT duplicate Board of Education services"
    verifiable: internal

  - id: direct_reimbursement
    label: "Class is NOT being reimbursed directly (or W9 attached)"
    verifiable: internal

invoice_rule: ">2 sessions/day (≤60 min each) or >7 sessions/week at one provider requires prior approval"
Save (Ctrl+O, Enter, Ctrl+X).

Notice I included all the YES/NO checklist items from the actual form (not just the 8 website-verifiable ones from §5) — this matters because your report needs to show the reviewer the full picture, with internal ones clearly separated per §6's requirement.

Once you save this, run:

bash
cat config/categories/community_classes.yaml
Paste that back to me so we confirm it saved right, then we do the same for the other 6 categories (Coaching, Memberships, HRI, OTPS, Transition, Appeals) — I'll give you each one ready to paste.

nano config/categories/community_classes.yaml
blinkdigital@Blinks-MacBook-Air preapproval-verification-tool % cat config/categories/community_classes.yaml
category: community_classes
display_name: "Community Class"
fields:
  - participant_name
  - participant_age
  - fi_coordinator_name
  - broker_name
  - class_name
  - provider_name
  - website_url
  - subject_area
  - fee_per_session
  - duration_per_session

checklist:
  - id: open_to_public
    label: "Class is open to and attended by the broader public"
    verifiable: website

id: published_fees
label: "Class has published fees"
verifiable: website

id: identical_pricing
label: "Fees are identical for OPWDD and non-OPWDD individuals"
verifiable: website
note: "Website can rarely prove this positively — mark 'Needs Review' unless site shows explicit two-tier pricing that contradicts it"

id: subject_based
label: "Class is subject-based (Art, Dance, Martial Arts, Cooking, etc.)"
verifiable: website

id: no_college_credit
label: "Class does not provide college credits"
verifiable: website

id: not_clinical
label: "Class is not clinical/therapy in nature"
verifiable: website

id: schedule_published
label: "A published schedule of the class exists"
verifiable: website

id: fee_match
label: "Published fee matches Fee per Session stated on form"
verifiable: website

# Internal items — website cannot verify these, must be flagged not guessed

id: budget_approved
label: "Community classes currently approved in the budget"
verifiable: internal

id: community_inclusion
label: "Class provides opportunity for community inclusion"
verifiable: internal

id: health_safety
label: "Class accommodates individual's health/safety needs"
verifiable: internal

id: independence
label: "Class increases independence or substitutes for human assistance"
verifiable: internal

id: exclusive_benefit
label: "Class is NOT provided exclusively for the participant's benefit"
verifiable: internal

id: dd_only_setting
label: "Class is NOT in a setting accessed only by people with DD"
verifiable: internal

id: staff_run
label: "Class is NOT run by OPWDD/provider-agency staff in official capacity"
verifiable: internal

id: opwdd_grounds
label: "Class is NOT located on grounds where OPWDD services are normally provided"
verifiable: internal

id: medicaid_duplicate
label: "Class does NOT duplicate Medicaid state plan/HCBS waiver services"
verifiable: internal

id: education_duplicate
label: "Class does NOT duplicate Board of Education services"
verifiable: internal

id: direct_reimbursement
label: "Class is NOT being reimbursed directly (or W9 attached)"
verifiable: internal

invoice_rule: ">2 sessions/day (≤60 min each) or >7 sessions/week at one provider requires prior approval"
blinkdigital@Blinks-MacBook-Air preapproval-verification-tool %

Show more
Saved correctly. Now let's do the remaining 6 category configs. I'll give you each one ready to paste — same pattern as before.

1. Coaching
bash
nano config/categories/coaching.yaml
yaml
category: coaching
display_name: "Coaching (for Parents/Spouse)"
fields:
  - participant_name
  - participant_age
  - fi_coordinator_name
  - broker_name
  - course_name
  - provider_name
  - website_url
  - fee_per_class
  - class_type   # group or private

checklist:
  - id: published_fees
    label: "Published fees exist for the course/class"
    verifiable: website

  - id: fee_sanity_check
    label: "Fee is within program cap (≤$55/group class or ≤$111/private class, $500/year total)"
    verifiable: website

  - id: genuine_education
    label: "Content is a genuine educational/coaching opportunity (not lodging/travel)"
    verifiable: website

  - id: adult_participant
    label: "Participant is 18+ (adults-only category)"
    verifiable: internal

  - id: budget_approved
    label: "Coaching currently approved in the budget"
    verifiable: internal

  - id: life_plan_match
    label: "Matches a valued outcome in the participant's Life Plan"
    verifiable: internal

program_caps:
  group_class: 55
  private_class: 111
  annual_cap: 500
2. Memberships
bash
nano config/categories/memberships.yaml
yaml
category: memberships
display_name: "Health-Club / Organizational Membership"
fields:
  - participant_name
  - participant_age
  - fi_coordinator_name
  - broker_name
  - organization_name
  - website_url
  - membership_fee
  - fee_frequency   # yearly or monthly

checklist:
  - id: open_to_public
    label: "Organization is open to the public — not a private/invitation-only club"
    verifiable: website

  - id: published_fee
    label: "Membership fee is published"
    verifiable: website

  - id: fee_match
    label: "Published fee amount matches form's stated fee (yearly/monthly)"
    verifiable: website

  - id: budget_approved
    label: "Memberships currently approved in the budget"
    verifiable: internal

  - id: life_plan_match
    label: "Matches a valued outcome in the participant's Life Plan"
    verifiable: internal
3. HRI (Household Related Items)
bash
nano config/categories/hri.yaml
yaml
category: hri
display_name: "Household Related Items"
fields:
  - participant_name
  - participant_age
  - fi_coordinator_name
  - broker_name
  - item_name
  - provider_name
  - website_url   # product link
  - item_price
  - safety_features_described

checklist:
  - id: item_exists
    label: "Item exists at the linked page, with a visible price"
    verifiable: website

  - id: not_excluded
    label: "Item is plausibly NOT on the exclusion list (cell phone, computer, vehicle, medical device, pill dispenser)"
    verifiable: website

  - id: safety_match
    label: "Safety features described on the form are supported by the product page"
    verifiable: website

  - id: budget_approved
    label: "HRI currently approved in the budget"
    verifiable: internal

  - id: life_plan_match
    label: "Matches a valued outcome in the participant's Life Plan"
    verifiable: internal

program_caps:
  annual_cap: 1500
  approval_validity_months: 3

exclusion_list:
  - cell phone
  - computer
  - vehicle
  - medical device
  - pill dispenser
4. OTPS
bash
nano config/categories/otps.yaml
yaml
category: otps
display_name: "Other Than Personal Services (OTPS)"
fields:
  - participant_name
  - participant_age
  - fi_coordinator_name
  - broker_name
  - item_name
  - provider_name
  - website_url
  - item_price

checklist:
  - id: item_exists
    label: "Item exists at the linked page, with a visible price"
    verifiable: website

  - id: not_excluded
    label: "Item is plausibly NOT on the OTPS exclusion list (cable TV, common household supplies, rental cars, legal fees, co-pays, experimental therapies)"
    verifiable: website

  - id: budget_approved
    label: "OTPS currently approved in the budget"
    verifiable: internal

  - id: life_plan_match
    label: "Matches a valued outcome in the participant's Life Plan"
    verifiable: internal

program_caps:
  annual_cap: 3000

exclusion_list:
  - cable tv
  - common household supplies
  - rental cars
  - legal fees
  - co-pays
  - experimental therapies
5. Transition Program
bash
nano config/categories/transition_program.yaml
yaml
category: transition_program
display_name: "Transition Program"
fields:
  - participant_name
  - participant_age
  - fi_coordinator_name
  - broker_name
  - program_name
  - provider_name
  - website_url
  - fee_per_course
  - fee_per_month

checklist:
  - id: published_fees
    label: "Published fees exist"
    verifiable: website

  - id: fee_sanity_check
    label: "Fee within program cap (≤$350/course or ≤$800/month)"
    verifiable: website

  - id: noncredit_skill_building
    label: "Program is noncredit-bearing and oriented to skill-building/employment outcomes"
    verifiable: website

  - id: not_opwdd_location
    label: "Program is NOT in an OPWDD-certified location"
    verifiable: website

  - id: staff_background_check
    label: "Staff background-screening proven by letter"
    verifiable: internal
    note: "Proven by a letter, not the website — flag as 'needs document' regardless of website findings"

  - id: budget_approved
    label: "Transition Program currently approved in the budget"
    verifiable: internal

  - id: life_plan_match
    label: "Matches a valued outcome in the participant's Life Plan"
    verifiable: internal

program_caps:
  per_course: 350
  per_month: 800
6. Appeals
bash
nano config/categories/appeals.yaml
yaml
category: appeals
display_name: "Pre-Approval Appeal"
fields:
  - participant_name
  - participant_age
  - fi_coordinator_name
  - broker_name
  - original_category   # category of the original denied request
  - denial_reason
  - appeal_justification
  - provider_name
  - website_url
  - fee

checklist:
  - id: rerun_original_checklist
    label: "Re-run the website-verifiable checks for the original category (e.g. Community Classes)"
    verifiable: website
    note: "Load the original_category's config and re-execute its website-verifiable items"

  - id: addresses_denial_reason
    label: "Evidence specifically supports or refutes the stated denial reason"
    verifiable: website

  - id: budget_approved
    label: "Category currently approved in the budget"
    verifiable: internal

  - id: life_plan_match
    label: "Matches a valued outcome in the participant's Life Plan"
    verifiable: internal
After creating all 6, verify everything's there:

bash
ls config/categories/
Paste me that output — should show all 7 files (including community_classes.yaml from before). Once confirmed, we move to writing the actual extraction script that reads any sample PDF and pulls out structured fields using the OpenAI API.

1784162230690_image.png
This looks correct and matches what I gave you. Now save and exit:

Press Ctrl+O, then Enter (to confirm filename), then Ctrl+X (to exit).

Then create the next file:

bash
nano config/categories/memberships.yaml
Paste in the Memberships config from my previous message, save/exit the same way, then move on to hri.yaml, otps.yaml, transition_program.yaml, and appeals.yaml — same pattern each time.

Once all 6 new files are created, run:

bash
ls config/categories/
Paste me that output so we confirm all 7 files exist (6 new + community_classes.yaml from earlier), then we move to writing the extraction script.


Validated test results and orchestrated project completion workflow
Validated test results and orchestrated project completion workflow
This ran successfully and, importantly, behaved honestly given the current simplification — it said "Needs Review" for the re-run check (correctly reflecting that the original category's full checklist isn't wired in yet) rather than making something up. Exactly the "no guessing" behavior the brief demands.

You now have 3 complete end-to-end samples committed to output/:

Sample-01 (Community Class — GallopNYC) — clean case, most items Met
Sample-07 (HRI — Laptop) — exclusion-list catch working correctly
Sample-10 (Appeal — Gracie Barra) — appeal category, with an honest limitation surfaced
This satisfies the "run on at least 3 samples" requirement from both §8 and the deliverables list. Time to wrap up.

Next: README.md
Let's write this now, since it's an explicit deliverable requirement (run instructions, how to add a checklist, limitations). Run this:

bash
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
MDEOF
echo "README.md written."
Run that, then confirm:

bash
cat README.md | head -20
Once confirmed, we move to the AI-CONVERSATION.md export, then commit and push. Want me to walk you through exporting this whole conversation next?

1784164063711_image.png
README.md wrote correctly and reads well — clear run instructions, honest limitations, sample outputs listed. This is a strong deliverable.

Next: AI-CONVERSATION.md
Since you're using this chat (Claude, in the Claude app) as your main AI assistant for this build, here's how to export it:

Look for the conversation options — usually a "..." or menu icon near the top of this chat, or an export option.
Since you're on the Claude web/app interface, the reliable way is: select all the text in this conversation (your messages + my responses) and copy it, since Claude.ai doesn't have a single-click /export like Claude Code does.
Given the length of this conversation, here's the most efficient approach:

Step 1: Replace the placeholder file
bash
nano AI-CONVERSATION.md
Step 2: At the very top, add the required tools/models list:
markdown
# Tools & Models Used

- Claude (Claude Sonnet, via claude.ai chat interface) — main planning, code generation, debugging assistant throughout the build
- OpenAI GPT-4o (via API, `gpt-4o` model) — used at runtime by the tool itself for PDF field extraction and website checklist verification
- Playwright (Chromium) — headless browser automation for website capture and evidence screenshots

---
