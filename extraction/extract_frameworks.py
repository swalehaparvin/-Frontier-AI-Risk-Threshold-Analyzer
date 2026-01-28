import sys
sys.path.append('..')

from utils.openai_client import AIExtractor
import json
import os

def load_prompt(filename):
    """Load extraction prompt from file"""
    # Fix: Use correct path when running from extraction directory
    prompt_path = f'prompts/{filename}'
    with open(prompt_path, 'r') as f:
        return f.read()

def extract_all_frameworks():
    """Extract framework data from METR dataset"""
    
    extractor = AIExtractor()
    
    print("📊 Extracting framework data...")
    
    # Sample document for testing (replace with actual METR content later)
    metr_document = """
    Anthropic's Responsible Scaling Policy defines ASL-3 as the threshold where models
    could meaningfully accelerate CBRN (chemical, biological, radiological, nuclear) threats
    or demonstrate autonomous replication capabilities. 
    
    ASL-3 triggers require:
    - METR biological risk evaluations
    - METR cyber offense evaluations  
    - Autonomous replication testing
    - Enhanced security controls
    - Deployment restrictions including no open-source release
    
    ASL-2 represents models with early signs of dangerous capabilities but cannot yet 
    cause catastrophic harm. ASL-2 requires standard safety evaluations and basic security controls.
    
    Google DeepMind's Frontier Safety Framework uses Critical Capability Levels (CCL).
    CCL-3 represents models with dangerous capabilities requiring:
    - External red teaming
    - Enhanced access controls
    - Restricted deployment
    
    CCL-2 covers early capability concerns with internal safety testing and standard controls.
    
    The EU AI Act defines systemic risk GPAI models as those trained with compute 
    exceeding 10^25 FLOPS. These models must comply with Article 51 requirements:
    - Model evaluation and adversarial testing
    - Systemic risk assessment
    - Technical documentation
    - Cybersecurity measures
    - Incident reporting
    
    OpenAI's Preparedness Framework defines "High" risk as models that could enable
    creation of novel biological threats or autonomous systems. High-risk models require:
    - External red team assessments
    - Board-level approval for deployment
    - Enhanced security measures
    """
    
    # Load prompts
    framework_prompt = load_prompt('framework_extraction.txt')
    
    # Create multiple extraction prompts for multi-pass
    prompts = [
        framework_prompt,
        "Extract risk tier definitions and thresholds from this AI safety policy analysis. Focus on capability thresholds and compute limits. Return as structured JSON with 'frameworks' array.",
        "Identify all mentions of risk levels (ASL, CCL, preparedness levels) and their associated thresholds. Include evaluation requirements. Return as JSON."
    ]
    
    # Multi-pass extraction
    print("🔄 Running multi-pass extraction...")
    result = extractor.multi_pass_extraction(metr_document, prompts)
    
    if result:
        # Save to processed data
        os.makedirs('../data/processed', exist_ok=True)
        with open('../data/processed/frameworks.json', 'w') as f:
            json.dump(result, f, indent=2)
        print("✅ Framework data extracted successfully!")
        print(f"📁 Saved to data/processed/frameworks.json")
        
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
    extract_all_frameworks()
