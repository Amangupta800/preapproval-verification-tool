import sys
import subprocess
import json
import os
from datetime import datetime

def run(cmd):
    print(f">>> {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=False)
    if result.returncode != 0:
        print("Command failed.")
        sys.exit(1)

def main():
    if len(sys.argv) < 3:
        print("Usage: python3 src/run_pipeline.py <pdf_path> <category_key>")
        print("Example: python3 src/run_pipeline.py samples/Sample-07---HRI-Laptop---exclusion-test.pdf hri")
        sys.exit(1)

    pdf_path = sys.argv[1]
    category_key = sys.argv[2]

    os.makedirs("output", exist_ok=True)

    base_name = os.path.splitext(os.path.basename(pdf_path))[0].replace(" ", "_")
    extracted_path = f"output/{base_name}_extracted.json"

    print(f"\n=== STEP 1: Extracting fields from {pdf_path} ===\n")
    with open(extracted_path, "w") as f:
        subprocess.run(["python3", "src/extract.py", pdf_path, category_key], stdout=f, check=True)
    print(f"Saved extraction to: {extracted_path}")

    print(f"\n=== STEP 2: Verifying against website ===\n")
    result = subprocess.run(["python3", "src/verify.py", extracted_path, category_key], capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        print(result.stderr)
        sys.exit(1)

    # Find the verification output path from stdout
    verification_path = None
    for line in result.stdout.splitlines():
        if "Saved verification output to:" in line:
            verification_path = line.split("Saved verification output to:")[1].strip()
            break

    if not verification_path:
        print("Could not find verification output path in verify.py output.")
        sys.exit(1)

    print(f"\n=== STEP 3: Generating report ===\n")
    run(["python3", "src/generate_report.py", extracted_path, verification_path, category_key])

    print(f"\n=== DONE: Pipeline complete for {pdf_path} ===\n")

if __name__ == "__main__":
    main()
