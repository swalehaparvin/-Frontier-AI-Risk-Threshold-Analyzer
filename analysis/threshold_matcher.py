import json
import os
from analysis.models import Framework, ModelSpecs, RiskAssessment, RiskTier


class ThresholdMatcher:

    def __init__(self):
        self.frameworks = self.load_frameworks()
        self.eu_requirements = self.load_eu_requirements()
        self.compute_thresholds = self.load_compute_thresholds()

    def load_frameworks(self):
        """Load extracted framework data"""
        try:
            with open('data/processed/frameworks.json', 'r') as f:
                data = json.load(f)
                return data.get('frameworks', [])
        except FileNotFoundError:
            print("⚠️ frameworks.json not found, using empty list")
            return []

    def load_eu_requirements(self):
        """Load EU compliance data"""
        try:
            with open('data/processed/eu_compliance.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print("⚠️ eu_compliance.json not found, using defaults")
            return {
                "eu_ai_act": {
                    "compute_threshold_flops":
                    1e25,
                    "required_evaluations":
                    ["Model evaluation", "Adversarial testing"],
                    "documentation_requirements": ["Technical documentation"]
                }
            }

    def load_compute_thresholds(self):
        """Load compute threshold data"""
        try:
            with open('data/processed/compute_thresholds.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print("⚠️ compute_thresholds.json not found, using defaults")
            return {
                "compute_thresholds": [{
                    "threshold_flops": 1e25,
                    "scientific_notation": "10^25",
                    "triggers": ["EU AI Act systemic risk"]
                }]
            }

    def assess_model(self, model_specs: ModelSpecs) -> RiskAssessment:
        """Assess a model against all frameworks"""

        assessments = {}

        # Check each framework
        for framework in self.frameworks:
            tier = self._match_to_framework(model_specs, framework)
            if tier:
                framework_name = framework.get(
                    'framework_name', framework.get('organization', 'Unknown'))
                assessments[framework_name] = tier

        # Check EU compliance
        eu_compliant, eu_reqs = self._check_eu_compliance(model_specs)

        # Identify gaps
        gaps = self._identify_gaps(assessments)

        return RiskAssessment(model_name=model_specs.name,
                              framework_assessments=assessments,
                              eu_compliant=eu_compliant,
                              eu_requirements=eu_reqs,
                              gaps_identified=gaps)

    def _match_to_framework(self, model_specs, framework):
        """Match model to appropriate tier in a framework"""

        # Sort tiers by level (highest first)
        tiers = sorted(framework.get('risk_tiers', []),
                       key=lambda x: x.get('tier_level', 0),
                       reverse=True)

        for tier in tiers:
            # Check compute threshold
            compute_threshold = tier.get('compute_threshold_flops')
            if compute_threshold and model_specs.training_compute_flops >= compute_threshold:
                return tier.get('tier_name')

            # Check capability matches
            capability_threshold = tier.get('capability_threshold', '').lower()
            for capability in model_specs.capabilities:
                if capability.lower() in capability_threshold or \
                   'cbrn' in capability.lower() and 'cbrn' in capability_threshold or \
                   'cyber' in capability.lower() and 'cyber' in capability_threshold or \
                   'autonom' in capability.lower() and 'autonom' in capability_threshold or \
                   'persuasion' in capability.lower() and 'persuasion' in capability_threshold:
                    return tier.get('tier_name')

        return "Below threshold"

    def _check_eu_compliance(self, model_specs):
        """Check if model needs EU AI Act compliance"""

        eu_data = self.eu_requirements.get('eu_ai_act', {})
        threshold = eu_data.get('compute_threshold_flops', 1e25)

        if model_specs.training_compute_flops >= threshold:
            # Model exceeds threshold - NOT compliant (needs to take actions)
            return False, eu_data.get('required_evaluations', [])

        # Model below threshold - compliant
        return True, []

    def _identify_gaps(self, assessments):
        """Identify where frameworks disagree"""

        gaps = []

        # Check if different frameworks give different risk levels
        unique_tiers = set(assessments.values())

        if len(unique_tiers) > 1:
            # Check if disagreement is meaningful (not just "Below threshold" vs actual tier)
            actual_tiers = [t for t in unique_tiers if t != "Below threshold"]
            if len(actual_tiers) > 1:
                gaps.append(
                    f"Frameworks disagree on risk level: {', '.join(actual_tiers)}"
                )

        # Check if some frameworks trigger but others don't
        triggered = [
            k for k, v in assessments.items() if v != "Below threshold"
        ]
        not_triggered = [
            k for k, v in assessments.items() if v == "Below threshold"
        ]

        if triggered and not_triggered:
            gaps.append(
                f"Triggered in {len(triggered)} frameworks but not in {len(not_triggered)} others"
            )

        return gaps
