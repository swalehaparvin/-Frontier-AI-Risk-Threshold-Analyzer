import sys
sys.path.append('..')

from utils.openai_client import AIExtractor
import json
import os

def extract_compute_thresholds():
    """Extract compute threshold data"""
    
    extractor = AIExtractor()
    
    print("💻 Extracting compute threshold data...")
    
    # Institute for Law & AI document
    compute_document = """
    Compute thresholds serve as regulatory triggers in AI governance frameworks.
    
    Key Thresholds:
    
    1. 10^25 FLOPS (EU AI Act Systemic Risk Threshold)
       - Defined in: EU AI Act Article 51
       - Year: 2024
       - Triggers: Systemic risk designation, enhanced monitoring, mandatory evaluations
       - Rationale: Models at this scale show emergent capabilities that pose societal risks
    
    2. 10^26 FLOPS (Proposed International Threshold)
       - Defined in: IAEA-style international framework proposals
       - Year: 2025
       - Triggers: Extreme risk category, international coordination, export controls
       - Rationale: Models at this scale could pose catastrophic risks
    
    3. 10^24 FLOPS (Moderate Risk Threshold)
       - Defined in: Various national frameworks
       - Year: 2023
       - Triggers: Enhanced documentation, basic safety testing
       - Rationale: First indication of advanced capabilities
    
    Algorithmic Efficiency Considerations:
    
    Algorithmic improvements reduce the effective compute needed for equivalent capabilities
    at approximately 30% per year (based on historical trends).
    
    This means:
    - A model requiring 10^25 FLOPS in 2024 might need only 7×10^24 FLOPS in 2025
    - Thresholds may need periodic adjustment to account for efficiency gains
    - Post-training enhancements (RLHF, fine-tuning) can add capabilities without
      proportional compute increases
    
    Verification Mechanisms:
    
    1. On-chip governance mechanisms
       - Hardware-level compute tracking
       - Cryptographic attestation of training runs
       - Tamper-resistant logging
    
    2. Datacenter monitoring
       - Third-party audits of training infrastructure
       - Energy consumption tracking as proxy
       - Network traffic analysis
    
    3. Self-reporting with verification
       - Labs report compute usage
       - Spot checks by regulatory bodies
       - Penalties for misreporting
    
    Limitations:
    
    - Algorithmic progress can reduce compute requirements over time
    - Post-training enhancements hard to track
    - Distributed training complicates monitoring
    - Energy-efficient hardware shifts goalposts
    """
    
    # Load prompt
    with open('prompts/compute_thresholds.txt', 'r') as f:
        compute_prompt = f.read()
    
    result = extractor.extract_structured(compute_document, compute_prompt)
    
    if result:
        os.makedirs('../data/processed', exist_ok=True)
        with open('../data/processed/compute_thresholds.json', 'w') as f:
            json.dump(result, f, indent=2)
        print("✅ Compute threshold data extracted!")
        print(f"📁 Saved to data/processed/compute_thresholds.json")
        
        # Show preview
        preview = json.dumps(result, indent=2)
        if len(preview) > 500:
            preview = preview[:500] + "..."
        print(f"\n📄 Preview:\n{preview}")
        return result
    else:
        print("❌ Extraction failed")
        return None

if __name__ == "__main__":
    extract_compute_thresholds()
