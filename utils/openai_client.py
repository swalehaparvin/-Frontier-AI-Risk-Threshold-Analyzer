import os
from openai import OpenAI
from dotenv import load_dotenv
import json
import time

load_dotenv()


class AIExtractor:

    def __init__(self):
        api_key = os.getenv('OPENAI_API_KEY')

        # Check if API key exists
        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY not found in environment variables!")

        # Simple client initialization (no proxies argument)
        self.client = OpenAI(api_key=api_key)

    def extract_structured(self,
                           document_text,
                           extraction_prompt,
                           model="gpt-4o-mini"):
        """Extract structured data from documents"""
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[{
                    "role":
                    "system",
                    "content":
                    "You are a policy analysis expert. Extract information accurately in JSON format."
                }, {
                    "role":
                    "user",
                    "content":
                    f"{extraction_prompt}\n\nDocument:\n{document_text}"
                }],
                response_format={"type": "json_object"},
                temperature=0.1)
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"❌ Error in extraction: {e}")
            return None

    def deep_reasoning(self, question, context, model="gpt-4o-mini"):
        """Use GPT-4 for complex reasoning (o1 models don't support some features)"""
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[{
                    "role":
                    "user",
                    "content":
                    f"Context: {context}\n\nQuestion: {question}"
                }],
                temperature=0.3)
            return response.choices[0].message.content
        except Exception as e:
            print(f"❌ Error in reasoning: {e}")
            return None

    def multi_pass_extraction(self, document_text, prompts_list):
        """Extract with multiple prompts and reconcile"""
        extractions = []

        print("🔄 Running multi-pass extraction...")

        # Multiple extraction passes
        for i, prompt in enumerate(prompts_list, 1):
            print(f"   Pass {i}/{len(prompts_list)}...")
            result = self.extract_structured(document_text, prompt)
            if result:
                extractions.append(result)
            time.sleep(1)  # Rate limit protection

        print(f"✅ Completed {len(extractions)} extraction passes")

        # Reconcile using another GPT call
        if len(extractions) > 1:
            print("🔄 Reconciling extractions...")
            reconciliation_prompt = f"""
            I have {len(extractions)} different extractions of the same document.
            Please reconcile them into a single, accurate extraction.
            Only include information that appears in at least 2 extractions.

            Extractions:
            {json.dumps(extractions, indent=2)}

            Return the reconciled version as JSON.
            """
            final = self.extract_structured(reconciliation_prompt,
                                            "Reconcile these extractions")
            return final

        return extractions[0] if extractions else None
