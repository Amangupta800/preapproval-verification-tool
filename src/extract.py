import sys
import json
import yaml
from pypdf import PdfReader
from openai import OpenAI

client = OpenAI()


def read_pdf_text(pdf_path):
    reader = PdfReader(pdf_path)
    full_text = ""
    for page in reader.pages:
        full_text += page.extract_text() + "\n"
    return full_text


def load_category_config(category_key):
    with open(f"config/categories/{category_key}.yaml") as f:
        return yaml.safe_load(f)


def extract_fields(pdf_text, category_config):
    field_list = category_config["fields"]

    system_prompt = f"""You are extracting structured data from a completed pre-approval application form.
The form belongs to the category: {category_config['display_name']}

Extract ONLY the following fields from the text below. Return STRICT JSON only,
no markdown, no commentary, no code fences.

Fields to extract: {json.dumps(field_list)}

Rules:
- If a field is not present or unclear in the text, set its value to null. Do NOT guess or invent values.
- For YES/NO checklist answers, extract them as a dict called "checklist_answers" mapping
  a short description of each question to "YES", "NO", or null if unclear.
- Preserve exact numbers, URLs, and names as written in the text.
"""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": pdf_text},
        ],
        response_format={"type": "json_object"},
    )

    return json.loads(response.choices[0].message.content)


def main():
    if len(sys.argv) < 3:
        print("Usage: python3 src/extract.py <pdf_path> <category_key>")
        print("Example: python3 src/extract.py samples/Sample-01---Community-Class-GallopNYC.pdf community_classes")
        sys.exit(1)

    pdf_path = sys.argv[1]
    category_key = sys.argv[2]

    pdf_text = read_pdf_text(pdf_path)
    config = load_category_config(category_key)
    extracted = extract_fields(pdf_text, config)

    print(json.dumps(extracted, indent=2))


if __name__ == "__main__":
    main()
