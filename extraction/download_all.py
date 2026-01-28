import requests
import os
from bs4 import BeautifulSoup
import time


def download_pdf(url, filename, subfolder=''):
    """Download PDF from URL"""
    try:
        print(f"📥 Downloading {filename}...")

        headers = {
            'User-Agent':
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        response = requests.get(url, timeout=30, headers=headers)
        response.raise_for_status()

        # Create directory
        if subfolder:
            filepath = f'../data/raw/{subfolder}/{filename}'
            os.makedirs(f'../data/raw/{subfolder}', exist_ok=True)
        else:
            filepath = f'../data/raw/{filename}'
            os.makedirs('../data/raw', exist_ok=True)

        with open(filepath, 'wb') as f:
            f.write(response.content)

        print(f"✅ Downloaded {filename}")
        return True

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            print(f"❌ {filename}: URL not found (404)")
        elif e.response.status_code == 403:
            print(f"❌ {filename}: Access forbidden (403)")
        else:
            print(f"❌ {filename}: HTTP Error {e.response.status_code}")
        return False
    except Exception as e:
        print(f"❌ {filename}: {str(e)}")
        return False


def scrape_webpage(url, filename, subfolder=''):
    """Scrape text from webpage and save as text file"""
    try:
        print(f"🌐 Scraping {filename}...")

        headers = {
            'User-Agent':
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        response = requests.get(url, timeout=30, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()

        # Get text
        text = soup.get_text(separator='\n', strip=True)

        # Create filepath
        txt_filename = filename.replace('.pdf', '.txt')
        if subfolder:
            filepath = f'../data/raw/{subfolder}/{txt_filename}'
            os.makedirs(f'../data/raw/{subfolder}', exist_ok=True)
        else:
            filepath = f'../data/raw/{txt_filename}'
            os.makedirs('../data/raw', exist_ok=True)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(text)

        print(f"✅ Scraped {filename} as text")
        return True

    except Exception as e:
        print(f"❌ {filename}: {str(e)}")
        return False


# URLs for all datasets
METR_FRAMEWORKS = {
    'anthropic_rsp.pdf':
    'https://www-cdn.anthropic.com/1adf000c8f675958c2ee23805d91aaade1cd4613/responsible-scaling-policy.pdf',
    'openai_preparedness.pdf':
    'https://cdn.openai.com/openai-preparedness-framework-beta.pdf',
    'deepmind_frontier.pdf':
    'https://deepmind.google/discover/blog/introducing-the-frontier-safety-framework/',
    'magic_agi.pdf':
    'https://magic.dev/agi-readiness-policy',
    'naver_safety.pdf':
    'https://clova.ai/en/tech-blog/en-navers-ai-safety-framework-asf',
    'meta_frontier.pdf':
    'https://ai.meta.com/static-resource/meta-frontier-ai-framework/',
    'g42_safety.pdf':
    'https://www.g42.ai/frontier-safety',
    'cohere_frontier.pdf':
    'https://cohere.com/security/the-cohere-secure-ai-frontier-model-framework-february-2025.pdf',
    'microsoft_governance.pdf':
    'https://cdn-dynmedia-1.microsoft.com/is/content/microsoftcorp/microsoft/final/en-us/microsoft-brand/documents/Microsoft-Frontier-Governance-Framework.pdf',
    'amazon_safety.pdf':
    'https://www.amazon.science/publications/amazons-frontier-model-safety-framework',
    'xai_risk.pdf':
    'https://data.x.ai/2025-08-20-xai-risk-management-framework.pdf',
    'nvidia_assessment.pdf':
    'https://images.nvidia.com/content/pdf/NVIDIA-Frontier-AI-Risk-Assessment.pdf'
}

EU_URLS = {
    'eu_code_practice.pdf':
    'https://cset.georgetown.edu/article/eu-ai-code-safety/'
}

COMPUTE_URLS = {
    'compute_thresholds.pdf':
    'https://law-ai.org/the-role-of-compute-thresholds-for-ai-governance/'
}

# These are web pages, not PDFs - need scraping
WEB_SCRAPE_LIST = [
    'deepmind_frontier.pdf', 'magic_agi.pdf', 'naver_safety.pdf',
    'meta_frontier.pdf', 'g42_safety.pdf', 'amazon_safety.pdf',
    'eu_code_practice.pdf', 'compute_thresholds.pdf'
]


def main():
    print("=" * 60)
    print("FRONTIER AI RISK ANALYZER - DATASET DOWNLOADER")
    print("=" * 60)

    success_count = 0
    fail_count = 0

    # Download METR frameworks
    print("\n📚 DOWNLOADING METR FRAMEWORKS (12 total)")
    print("-" * 60)

    for filename, url in METR_FRAMEWORKS.items():
        if filename in WEB_SCRAPE_LIST:
            # Web scraping for HTML pages
            if scrape_webpage(url, filename, 'metr'):
                success_count += 1
            else:
                fail_count += 1
        else:
            # Direct PDF download
            if download_pdf(url, filename, 'metr'):
                success_count += 1
            else:
                fail_count += 1

        time.sleep(1)  # Be nice to servers

    # Download EU documents
    print("\n🇪🇺 DOWNLOADING EU DOCUMENTS")
    print("-" * 60)

    for filename, url in EU_URLS.items():
        if filename in WEB_SCRAPE_LIST:
            if scrape_webpage(url, filename):
                success_count += 1
            else:
                fail_count += 1
        else:
            if download_pdf(url, filename):
                success_count += 1
            else:
                fail_count += 1

        time.sleep(1)

    # Download compute threshold documents
    print("\n💻 DOWNLOADING COMPUTE THRESHOLD DOCUMENTS")
    print("-" * 60)

    for filename, url in COMPUTE_URLS.items():
        if filename in WEB_SCRAPE_LIST:
            if scrape_webpage(url, filename):
                success_count += 1
            else:
                fail_count += 1
        else:
            if download_pdf(url, filename):
                success_count += 1
            else:
                fail_count += 1

        time.sleep(1)

    # Summary
    print("\n" + "=" * 60)
    print("DOWNLOAD SUMMARY")
    print("=" * 60)
    print(f"✅ Successful: {success_count}")
    print(f"❌ Failed: {fail_count}")
    print(f"📊 Total: {success_count + fail_count}")

    # Show what was downloaded
    print("\n📁 Downloaded files:")

    if os.path.exists('../data/raw/metr'):
        metr_files = os.listdir('../data/raw/metr')
        print(f"\nMETR frameworks ({len(metr_files)} files):")
        for f in sorted(metr_files):
            print(f"  - {f}")

    if os.path.exists('../data/raw'):
        other_files = [
            f for f in os.listdir('../data/raw')
            if os.path.isfile(f'../data/raw/{f}')
        ]
        if other_files:
            print(f"\nOther documents ({len(other_files)} files):")
            for f in sorted(other_files):
                print(f"  - {f}")

    print("\n✅ Download process complete!")
    print("\n📝 Next steps:")
    print("   1. Review downloaded files in data/raw/")
    print("   2. Run extraction scripts to process PDFs")
    print("   3. Check data/processed/ for extracted data")


if __name__ == "__main__":
    main()
