from extract_frameworks import extract_all_frameworks
from extract_eu_requirements import extract_eu_compliance
from extract_compute import extract_compute_thresholds
import time


def main():
    print("🚀 Starting all extractions...\n")

    # Extract frameworks
    frameworks = extract_all_frameworks()
    time.sleep(2)

    # Extract EU compliance
    eu = extract_eu_compliance()
    time.sleep(2)

    # Extract compute thresholds
    compute = extract_compute_thresholds()

    print("\n✅ All extractions complete!")
    print("📁 Check data/processed/ for results")


if __name__ == "__main__":
    main()
