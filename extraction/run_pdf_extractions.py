from extract_all_frameworks import extract_from_all_pdfs
from extract_all_eu import extract_eu_from_pdfs
from extract_all_compute import extract_compute_from_pdfs
import time

def main():
    print("\n" + "=" * 60)
    print("FRONTIER AI RISK ANALYZER - PDF EXTRACTION")
    print("=" * 60)

    print("\n⚠️ NOTE: This will use OpenAI API credits")
    print("Estimated cost: ~$2-5 depending on PDF sizes\n")

    input("Press Enter to continue or Ctrl+C to cancel...")

    # Extract frameworks
    print("\n\n" + "🏢" * 30)
    print("STEP 1: EXTRACTING FRAMEWORKS FROM ALL PDFS")
    print("🏢" * 30)
    frameworks = extract_from_all_pdfs()
    time.sleep(2)

    # Extract EU
    print("\n\n" + "🇪🇺" * 30)
    print("STEP 2: EXTRACTING EU COMPLIANCE DATA")
    print("🇪🇺" * 30)
    eu = extract_eu_from_pdfs()
    time.sleep(2)

    # Extract compute
    print("\n\n" + "💻" * 30)
    print("STEP 3: EXTRACTING COMPUTE THRESHOLDS")
    print("💻" * 30)
    compute = extract_compute_from_pdfs()

    # Summary
    print("\n\n" + "=" * 60)
    print("EXTRACTION SUMMARY")
    print("=" * 60)

    if frameworks:
        print(
            f"✅ Frameworks: {len(frameworks.get('frameworks', []))} extracted")
    else:
        print("❌ Frameworks: Extraction failed")

    if eu:
        print("✅ EU Compliance: Extracted")
    else:
        print("❌ EU Compliance: Extraction failed")

    if compute:
        print("✅ Compute Thresholds: Extracted")
    else:
        print("❌ Compute Thresholds: Extraction failed")

    print("\n📁 Check data/processed/ for results")
    print("\n🚀 Ready to launch Streamlit app!")
    print("\nRun: streamlit run app/main.py")


if __name__ == "__main__":
    main()
