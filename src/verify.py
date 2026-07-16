import sys
import json
import yaml
import os
from datetime import datetime
from playwright.sync_api import sync_playwright
from openai import OpenAI

client = OpenAI()

BOT_BLOCK_SIGNALS = [
    "click the button below to continue shopping",
    "to discuss automated access",
    "enter the characters you see below",
    "are you a human",
    "verify you are a human",
    "robot check",
    "sorry we couldn't find that page",
    "page not found",
    "404 not found",
]


def load_category_config(category_key):
    with open(f"config/categories/{category_key}.yaml") as f:
        return yaml.safe_load(f)


def add_timestamp_overlay(page, url, timestamp):
    page.evaluate(
        """
        ([text]) => {
            const banner = document.createElement('div');
            banner.textContent = text;
            banner.style.position = 'fixed';
            banner.style.top = '0';
            banner.style.left = '0';
            banner.style.width = '100%';
            banner.style.background = 'red';
            banner.style.color = 'white';
            banner.style.fontSize = '14px';
            banner.style.fontFamily = 'monospace';
            banner.style.padding = '6px';
            banner.style.zIndex = '999999';
            banner.style.textAlign = 'center';
            document.body.appendChild(banner);
        }
        """,
        [f"Captured: {timestamp} | URL: {url}"],
    )


def add_label_banner(page, label_text):
    page.evaluate(
        """
        ([text]) => {
            const label = document.createElement('div');
            label.textContent = text;
            label.style.position = 'fixed';
            label.style.top = '32px';
            label.style.left = '0';
            label.style.width = '100%';
            label.style.background = 'darkgreen';
            label.style.color = 'white';
            label.style.fontSize = '14px';
            label.style.fontFamily = 'monospace';
            label.style.padding = '6px';
            label.style.zIndex = '999999';
            label.style.textAlign = 'center';
            document.body.appendChild(label);
        }
        """,
        [label_text],
    )


def highlight_text(page, snippet):
    page.evaluate(
        """
        ([snippet]) => {
            const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
            let node;
            while (node = walker.nextNode()) {
                if (node.textContent.includes(snippet)) {
                    const span = document.createElement('span');
                    span.style.backgroundColor = 'yellow';
                    span.style.border = '2px solid red';
                    const range = document.createRange();
                    range.selectNodeContents(node);
                    try { range.surroundContents(span); } catch(e) {}
                    break;
                }
            }
        }
        """,
        [snippet],
    )


def new_context(browser):
    return browser.new_context(
        user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        viewport={"width": 1440, "height": 900},
        locale="en-US",
    )


def looks_bot_blocked(page_text):
    lowered = page_text.lower()
    return any(signal in lowered for signal in BOT_BLOCK_SIGNALS)


def capture_website(url, output_dir="output/evidence"):
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    screenshot_path = f"{output_dir}/full_page_{timestamp}.png"

    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = new_context(browser)
        page = context.new_page()
        page.goto(url, timeout=30000, wait_until="networkidle")
        page_text = page.inner_text("body")

        add_timestamp_overlay(page, url, timestamp)
        page.screenshot(path=screenshot_path, full_page=True)

        browser.close()

    return {
        "url": url,
        "timestamp": timestamp,
        "screenshot_path": screenshot_path,
        "page_text": page_text[:15000],
        "bot_blocked": looks_bot_blocked(page_text),
    }


def capture_targeted_evidence(url, item_id, item_label, search_text, output_dir="output/evidence"):
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    safe_id = item_id.replace(" ", "_")
    screenshot_path = f"{output_dir}/evidence_{safe_id}_{timestamp}.png"

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            context = new_context(browser)
            page = context.new_page()
            page.goto(url, timeout=30000, wait_until="networkidle")

            if search_text:
                snippet = search_text.strip()[:40]
                try:
                    locator = page.get_by_text(snippet, exact=False).first
                    locator.scroll_into_view_if_needed(timeout=5000)
                    highlight_text(page, snippet)
                except Exception:
                    pass

            add_timestamp_overlay(page, url, timestamp)
            add_label_banner(page, f"Evidence: {item_label}")

            page.screenshot(path=screenshot_path, full_page=False)
            browser.close()

        return screenshot_path
    except Exception as e:
        print(f"  (targeted capture failed for {item_id}: {e})")
        return None


def check_exclusion_list(extracted_fields, category_config):
    """Deterministic, code-level check: does the form's stated item name
    match anything on the category's exclusion list? Does not depend on
    the website loading at all."""
    exclusion_list = category_config.get("exclusion_list", [])
    if not exclusion_list:
        return None

    item_text = " ".join(
        str(extracted_fields.get(f, "") or "")
        for f in ["item_name", "class_name", "course_name", "organization_name", "program_name", "subject_area"]
    ).lower()

    matched = [term for term in exclusion_list if term.lower() in item_text]

    if matched:
        return {
            "status": "Not Met",
            "note": f"Item description on the form ('{item_text.strip()}') matches excluded category: {', '.join(matched)}. This item plausibly falls under the program's exclusion list.",
        }
    return {
        "status": "Needs Review",
        "note": f"No exact exclusion-list keyword match found in the form's item description ('{item_text.strip()}'). Reviewer should confirm the item does not fall under an excluded category.",
    }


def verify_checklist_items(page_text, extracted_fields, category_config, capture_meta):
    website_items = [c for c in category_config["checklist"] if c["verifiable"] == "website"]

    bot_blocked = capture_meta.get("bot_blocked", False)

    items_description = "\n".join(
        f"- id: {item['id']} | {item['label']}" + (f" | NOTE: {item['note']}" if "note" in item else "")
        for item in website_items
    )

    block_notice = ""
    if bot_blocked:
        block_notice = (
            "\nIMPORTANT: The captured page appears to be an anti-bot / verification challenge page, "
            "NOT the real product/site content. Do NOT infer anything about the actual item from this text. "
            "Mark every item as 'Needs Review' with a note explaining the site blocked automated access.\n"
        )

    system_prompt = f"""You are verifying pre-approval checklist items against real website content.
Captured on: {capture_meta['timestamp']} from URL: {capture_meta['url']}
{block_notice}
Application details extracted from the form:
{json.dumps(extracted_fields, indent=2)}

Website page text (what was actually captured):
\"\"\"
{page_text}
\"\"\"

For EACH checklist item below, determine status based ONLY on what appears in the website text above.
Do NOT guess or invent information not present in the page text.

Checklist items:
{items_description}

Return STRICT JSON only, in this exact shape:
{{
  "results": [
    {{
      "id": "<item id>",
      "status": "Met" | "Not Met" | "Needs Review",
      "note": "<plain language note>",
      "supporting_quote": "<the exact short snippet of page text that supports this, or null if Needs Review>"
    }}
  ]
}}

Rules:
- "Met" = the page text clearly confirms this.
- "Not Met" = the page text clearly contradicts this.
- "Needs Review" = the page doesn't address it clearly, or it's the kind of thing a website can't prove/disprove with certainty, or the page is a bot-block/challenge page.
- Never fabricate evidence. If unsure, use "Needs Review".
- supporting_quote must be an exact substring copied from the page text above (for locating it later), under 15 words.
"""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "system", "content": system_prompt}],
        response_format={"type": "json_object"},
    )

    return json.loads(response.choices[0].message.content), website_items


def main():
    if len(sys.argv) < 3:
        print("Usage: python3 src/verify.py <extracted_json_path> <category_key>")
        sys.exit(1)

    extracted_json_path = sys.argv[1]
    category_key = sys.argv[2]

    with open(extracted_json_path) as f:
        extracted_fields = json.load(f)

    config = load_category_config(category_key)
    url = extracted_fields.get("website_url")

    if not url:
        print(json.dumps({"error": "No website_url found in extracted fields. Needs Review — ask reviewer for the link."}))
        sys.exit(0)

    print(f"Capturing website: {url}")
    capture_meta = capture_website(url)

    if capture_meta.get("bot_blocked"):
        print("WARNING: Captured page appears to be a bot-detection/challenge page, not real site content.")

    print("Verifying checklist items against captured content...")
    verification, website_items = verify_checklist_items(capture_meta["page_text"], extracted_fields, config, capture_meta)

    # Deterministic code-level exclusion-list override (independent of website content)
    exclusion_check = check_exclusion_list(extracted_fields, config)
    if exclusion_check:
        for result in verification["results"]:
            if result["id"] == "not_excluded":
                result["status"] = exclusion_check["status"]
                result["note"] = exclusion_check["note"]
                result["supporting_quote"] = None
                break

    label_map = {item["id"]: item["label"] for item in website_items}

    print("Capturing targeted evidence for confirmed items...")
    for result in verification["results"]:
        if result["status"] == "Met":
            label = label_map.get(result["id"], result["id"])
            quote = result.get("supporting_quote")
            path = capture_targeted_evidence(url, result["id"], label, quote)
            result["evidence_screenshot"] = path
        else:
            result["evidence_screenshot"] = None

    output = {
        "url": url,
        "capture_timestamp": capture_meta["timestamp"],
        "full_page_screenshot": capture_meta["screenshot_path"],
        "bot_blocked": capture_meta.get("bot_blocked", False),
        "verification_results": verification["results"],
    }

    output_path = f"output/verification_{capture_meta['timestamp']}.json"
    with open(output_path, "w") as f:
        json.dump(output, f, indent=2)

    print(f"\nSaved verification output to: {output_path}")
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
