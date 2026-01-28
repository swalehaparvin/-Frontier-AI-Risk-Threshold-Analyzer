import sys

sys.path.append('..')

from utils.openai_client import AIExtractor
from utils.pdf_reader import get_all_documents
import json
import os


def extract_eu_from_pdfs():
    """Extract EU compliance data from downloaded documents"""

    extractor = AIExtractor()

    print("=" * 60)
    print("EXTRACTING EU COMPLIANCE DOCUMENTS")
    print("=" * 60)

    # Read EU documents
    print("\n📚 Loading EU documents...")
    eu_files = []

    # Check for EU-related files
    raw_dir = '../data/raw'
    if os.path.exists(raw_dir):
        for filename in os.listdir(raw_dir):
            if 'eu' in filename.lower():
                eu_files.append(os.path.join(raw_dir, filename))

    if not eu_files:
        print("⚠️ No EU documents found, using default data")
        return None

    # Read first EU document
    from utils.pdf_reader import read_document

    for filepath in eu_files:
        print(f"\n📄 Reading {os.path.basename(filepath)}...")
        content = read_document(filepath)

        if not content:
            continue

        # Truncate if needed
        if len(content) > 100000:
            content = content[:100000]

        print(f"📊 Extracting EU compliance data ({len(content)} chars)...")

        with open('prompts/eu_compliance.txt', 'r') as f:
            eu_prompt = f.read()

        try:
            result = extractor.extract_structured(content, eu_prompt)

            if result:
                os.makedirs('../data/processed', exist_ok=True)
                with open('../data/processed/eu_compliance.json', 'w') as f:
                    json.dump(result, f, indent=2)

                print("✅ EU compliance data extracted!")
                print(f"📁 Saved to: data/processed/eu_compliance.json")
                return result

        except Exception as e:
            print(f"❌ Error: {e}")
            continue

    return None


if __name__ == "__main__":
    extract_eu_from_pdfs()
