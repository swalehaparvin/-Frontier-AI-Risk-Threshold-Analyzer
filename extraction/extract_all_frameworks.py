import sys

sys.path.append('..')

from utils.openai_client import AIExtractor
from utils.pdf_reader import get_all_documents
import json
import os


def load_prompt(filename):
    """Load extraction prompt from file"""
    with open(f'prompts/{filename}', 'r') as f:
        return f.read()


def extract_from_all_pdfs():
    """Extract framework data from all downloaded PDFs"""

    extractor = AIExtractor()

    print("=" * 60)
    print("EXTRACTING ALL FRAMEWORK DOCUMENTS")
    print("=" * 60)

    # Read all documents from METR folder
    print("\n📚 Loading METR framework documents...")
    metr_docs = get_all_documents('../data/raw/metr')

    if not metr_docs:
        print("⚠️ No documents found in data/raw/metr/")
        return None

    print(f"\n✅ Loaded {len(metr_docs)} documents")

    # Combine all documents (or process individually)
    all_frameworks = []

    framework_prompt = load_prompt('framework_extraction.txt')

    for filename, content in metr_docs.items():
        print(f"\n{'='*60}")
        print(f"Processing: {filename}")
        print(f"{'='*60}")

        # Truncate if too long (GPT-4o context limit)
        max_chars = 100000
        if len(content) > max_chars:
            print(
                f"⚠️ Document too long ({len(content)} chars), truncating to {max_chars}"
            )
            content = content[:max_chars]

        print(f"📊 Extracting from {filename} ({len(content)} chars)...")

        try:
            result = extractor.extract_structured(content, framework_prompt)

            if result and 'frameworks' in result:
                frameworks = result['frameworks']
                all_frameworks.extend(frameworks)
                print(
                    f"✅ Extracted {len(frameworks)} framework(s) from {filename}"
                )
            else:
                print(f"⚠️ No frameworks extracted from {filename}")

        except Exception as e:
            print(f"❌ Error processing {filename}: {e}")
            continue

    # Save combined results
    if all_frameworks:
        final_result = {'frameworks': all_frameworks}

        os.makedirs('../data/processed', exist_ok=True)
        with open('../data/processed/frameworks.json', 'w') as f:
            json.dump(final_result, f, indent=2)

        print("\n" + "=" * 60)
        print("EXTRACTION COMPLETE")
        print("=" * 60)
        print(f"✅ Total frameworks extracted: {len(all_frameworks)}")
        print(f"📁 Saved to: data/processed/frameworks.json")

        # Show summary
        print("\n📊 Framework Summary:")
        for fw in all_frameworks:
            org = fw.get('organization', 'Unknown')
            name = fw.get('framework_name', 'Unknown')
            tiers = len(fw.get('risk_tiers', []))
            print(f"  - {org}: {name} ({tiers} tiers)")

        return final_result
    else:
        print("❌ No frameworks extracted from any documents")
        return None


if __name__ == "__main__":
    extract_from_all_pdfs()
