import sys
sys.path.append('..')

from utils.openai_client import AIExtractor
import json
import os

def extract_eu_compliance():
    """Extract EU AI Act requirements"""
    
    extractor = AIExtractor()
    
    print("🇪🇺 Extracting EU AI Act compliance data...")
    
    # Georgetown CSET document content
    eu_document = """
    The EU AI Act establishes a compute threshold of 10^25 FLOPS for identifying
    General Purpose AI (GPAI) models with systemic risk.
    
    Models exceeding this threshold must comply with Article 51 requirements:
    
    1. Model Evaluation and Testing:
       - Adversarial testing to identify systemic risks
       - Model evaluation protocols
       - Safety assessment documentation
    
    2. Systemic Risk Assessment:
       - Evaluate potential for systemic harm
       - Document risk mitigation measures
       - Ongoing monitoring requirements
    
    3. Documentation Requirements:
       - Technical documentation of model architecture
       - Training data description and provenance
       - Model card with detailed capability descriptions
       - Risk assessment reports
    
    4. Transparency Obligations:
       - Publish summary of training data sources
       - Disclose total compute used in training
       - Make model card publicly available
       - Report serious incidents
    
    5. Cybersecurity Measures:
       - Implement state-of-the-art security
       - Protection against unauthorized access
       - Incident response procedures
    
    6. Prohibited Uses:
       - Social scoring systems
       - Manipulation of human behavior
       - Exploitation of vulnerabilities
       - Real-time biometric identification in public spaces
    
    The Code of Practice sets minimum standards for appropriate risk management
    that go beyond current industry voluntary frameworks.
    """
    
    # Load prompt
    with open('prompts/eu_compliance.txt', 'r') as f:
        eu_prompt = f.read()
    
    # Extract
    result = extractor.extract_structured(eu_document, eu_prompt)
    
    if result:
        os.makedirs('../data/processed', exist_ok=True)
        with open('../data/processed/eu_compliance.json', 'w') as f:
            json.dump(result, f, indent=2)
        print("✅ EU compliance data extracted!")
        print(f"📁 Saved to data/processed/eu_compliance.json")
        
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
    extract_eu_compliance()
