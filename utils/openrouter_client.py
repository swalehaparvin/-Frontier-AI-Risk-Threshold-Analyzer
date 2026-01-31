import os
import json
from openai import OpenAI

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)

AVAILABLE_MODELS = {
    "deepseek/deepseek-r1": "DeepSeek R1 (Best for reasoning)",
    "anthropic/claude-3.5-sonnet": "Claude 3.5 Sonnet",
    "openai/gpt-4o": "GPT-4o",
    "openai/gpt-4o-mini": "GPT-4o Mini (Fast & Cheap)",
    "google/gemini-2.0-flash-001": "Gemini 2.0 Flash",
    "meta-llama/llama-3.1-70b-instruct": "Llama 3.1 70B",
    "mistralai/mistral-large-2411": "Mistral Large",
    "qwen/qwen-2.5-72b-instruct": "Qwen 2.5 72B",
}

DEFAULT_MODEL = "openai/gpt-4o-mini"


def chat_completion(messages: list, model: str = DEFAULT_MODEL, temperature: float = 0.7, max_tokens: int = 4096) -> str:
    """Send a chat completion request to OpenRouter"""
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content
    except Exception as e:
        raise Exception(f"OpenRouter API error: {str(e)}")


def extract_framework_data(document_text: str, model: str = DEFAULT_MODEL) -> dict:
    """Extract structured framework data from document text using AI"""
    
    system_prompt = """You are an expert AI safety researcher. Extract structured data about AI safety frameworks from the provided document.

Return a JSON object with this structure:
{
    "organization": "Name of the organization",
    "framework_name": "Name of the safety framework",
    "publication_date": "Date if mentioned",
    "risk_tiers": [
        {
            "tier_name": "Name of the risk tier (e.g., ASL-3, CCL-2)",
            "tier_level": 1-5 (integer, higher = more dangerous),
            "capability_threshold": "Description of capabilities that trigger this tier",
            "compute_threshold_flops": "Compute threshold if mentioned (as number, e.g., 1e25)",
            "evaluation_requirements": ["List of required evaluations"],
            "required_safeguards": ["List of required safeguards"]
        }
    ],
    "key_capabilities_assessed": ["List of dangerous capabilities assessed"],
    "governance_requirements": ["List of governance/oversight requirements"]
}

Be precise and only include information explicitly stated in the document. Use null for missing values."""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Extract the AI safety framework data from this document:\n\n{document_text[:15000]}"}
    ]
    
    response = chat_completion(messages, model=model, temperature=0.2)
    
    try:
        start = response.find('{')
        end = response.rfind('}') + 1
        if start != -1 and end > start:
            return json.loads(response[start:end])
    except json.JSONDecodeError:
        pass
    
    return {"error": "Failed to parse extraction", "raw_response": response}


def analyze_risk_gaps(model_specs: dict, framework_assessments: dict, model: str = DEFAULT_MODEL) -> dict:
    """Analyze gaps and inconsistencies across framework assessments"""
    
    system_prompt = """You are an expert AI governance analyst. Analyze the risk assessments across multiple frameworks and identify:
1. Key discrepancies between frameworks
2. Most concerning risk areas
3. Recommended actions for compliance
4. Overall risk summary

Return a JSON object with:
{
    "risk_summary": "2-3 sentence overall assessment",
    "key_discrepancies": ["List of notable differences between frameworks"],
    "primary_concerns": ["Top 3-5 risk concerns"],
    "recommended_actions": ["Prioritized list of recommended actions"],
    "compliance_gaps": ["Specific compliance gaps identified"],
    "confidence_score": 0-100 (your confidence in this assessment)
}"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"""Analyze these risk assessments:

Model Specifications:
{json.dumps(model_specs, indent=2)}

Framework Assessments:
{json.dumps(framework_assessments, indent=2)}

Provide a comprehensive gap analysis."""}
    ]
    
    response = chat_completion(messages, model=model, temperature=0.3)
    
    try:
        start = response.find('{')
        end = response.rfind('}') + 1
        if start != -1 and end > start:
            return json.loads(response[start:end])
    except json.JSONDecodeError:
        pass
    
    return {"risk_summary": response, "error": "Failed to parse structured response"}


def generate_compliance_report(model_name: str, assessments: dict, model: str = DEFAULT_MODEL) -> str:
    """Generate a detailed compliance report in markdown format"""
    
    system_prompt = """You are an AI governance compliance officer. Generate a professional compliance report for the given AI model assessment.

The report should include:
1. Executive Summary
2. Model Overview
3. Framework-by-Framework Assessment
4. EU AI Act Compliance Status
5. Risk Mitigation Recommendations
6. Conclusion

Format the report in clean markdown with proper headings."""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"""Generate a compliance report for:

Model: {model_name}

Assessment Data:
{json.dumps(assessments, indent=2)}"""}
    ]
    
    return chat_completion(messages, model=model, temperature=0.4, max_tokens=6000)


def explain_risk_tier(tier_name: str, framework_name: str, model: str = DEFAULT_MODEL) -> str:
    """Get an AI explanation of what a specific risk tier means"""
    
    messages = [
        {"role": "system", "content": "You are an AI safety expert. Provide clear, concise explanations of AI safety framework risk tiers. Be factual and helpful."},
        {"role": "user", "content": f"Explain what {tier_name} means in the {framework_name} framework. Include what capabilities trigger this tier, what safeguards are required, and real-world implications. Keep it under 200 words."}
    ]
    
    return chat_completion(messages, model=model, temperature=0.5, max_tokens=500)
