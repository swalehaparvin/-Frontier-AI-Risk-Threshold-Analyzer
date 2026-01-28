import sys

sys.path.append('..')

from utils.openai_client import AIExtractor
from utils.pdf_reader import get_all_documents, read_document
import json
import os


def extract_compute_from_pdfs():
    """Extract compute threshold data from downloaded documents"""

    extractor = AIExtractor()

    print("=" * 60)
    print("EXTRACTING COMPUTE THRESHOLD DOCUMENTS")
    print("=" * 60)

    # Look for compute-related files
    compute_files = []
    raw_dir = '../data/raw'

    if os.path.exists(raw_dir):
        for filename in os.listdir(raw_dir):
            if 'compute' in filename.lower() or 'threshold' in filename.lower(
            ):
                compute_files.append(os.path.join(raw_dir, filename))

    if not compute_files:
        print("⚠️ No compute threshold documents found")
        return None

    for filepath in compute_files:
        print(f"\n📄 Reading {os.path.basename(filepath)}...")
        content = read_document(filepath)

        if not content:
            continue

        if len(content) > 100000:
            content = content[:100000]

        print(f"📊 Extracting compute data ({len(content)} chars)...")

        with open('prompts/compute_thresholds.txt', 'r') as f:
            compute_prompt = f.read()

        try:
            result = extractor.extract_structured(content, compute_prompt)

            if result:
                os.makedirs('../data/processed', exist_ok=True)
                with open('../data/processed/compute_thresholds.json',
                          'w') as f:
                    json.dump(result, f, indent=2)

                print("✅ Compute threshold data extracted!")
                print(f"📁 Saved to: data/processed/compute_thresholds.json")
                return result

        except Exception as e:
            print(f"❌ Error: {e}")
            continue

    return None


if __name__ == "__main__":
    extract_compute_from_pdfs()
