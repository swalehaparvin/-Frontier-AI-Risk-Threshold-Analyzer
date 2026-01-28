import streamlit as st
import sys
import os

# Add parent directory to path so we can import analysis module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from analysis.threshold_matcher import ThresholdMatcher
from analysis.models import ModelSpecs
import json

# Page config
st.set_page_config(page_title="Frontier AI Risk Analyzer",
                   page_icon="🤖",
                   layout="wide")

# Title
st.title("🤖 Frontier AI Risk Threshold Analyzer")
st.markdown(
    "*Map your AI model across safety frameworks and check EU compliance*")

# Sidebar
st.sidebar.header("About")
st.sidebar.info("""
This tool analyzes AI models against:
- 12+ lab safety frameworks
- EU AI Act requirements  
- Compute thresholds

Built for Technical AI Governance Challenge 2026
""")


# Initialize matcher
@st.cache_resource
def get_matcher():
    return ThresholdMatcher()


try:
    matcher = get_matcher()
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

# Main interface
tab1, tab2, tab3 = st.tabs(
    ["🎯 Risk Assessment", "📊 Framework Explorer", "📖 About"])

with tab1:
    st.header("Model Risk Assessment")

    col1, col2 = st.columns(2)

    with col1:
        model_name = st.text_input("Model Name", "GPT-5")

        # Compute input with helper
        compute_input = st.text_input(
            "Training Compute (FLOPS)",
            "1e25",
            help="Enter in scientific notation, e.g., 1e25 for 10^25")

        try:
            training_compute = float(compute_input)
        except:
            st.error(
                "Invalid compute value. Use scientific notation like 1e25")
            training_compute = 1e25

        parameters = st.number_input("Parameters (Billions)",
                                     min_value=0.0,
                                     value=100.0,
                                     step=0.1)

    with col2:
        st.markdown("**Capabilities**")
        capabilities = []

        if st.checkbox("CBRN acceleration risk"):
            capabilities.append("CBRN acceleration")
        if st.checkbox("Cyber offense capabilities"):
            capabilities.append("Cyber offense")
        if st.checkbox("Autonomous replication"):
            capabilities.append("Autonomous replication")
        if st.checkbox("Advanced persuasion"):
            capabilities.append("Advanced persuasion")

        evaluations = st.multiselect("Passed Evaluations", [
            "METR bio eval", "METR cyber eval", "ARA autonomy",
            "DeepMind safety"
        ],
                                     default=[])

    if st.button("🔍 Analyze Model", type="primary"):
        # Create model specs
        model = ModelSpecs(
            name=model_name,
            training_compute_flops=training_compute,
            parameters=parameters * 1e9,  # Convert to actual number
            passed_evaluations=evaluations,
            capabilities=capabilities)

        # Assess
        with st.spinner("Analyzing across frameworks..."):
            assessment = matcher.assess_model(model)

        # Display results
        st.success("✅ Analysis Complete!")

        # Framework assessments
        st.subheader("📋 Framework Assessments")

        if assessment.framework_assessments:
            for framework, tier in assessment.framework_assessments.items():
                if tier != "Below threshold":
                    st.warning(f"**{framework}**: {tier}")
                else:
                    st.success(f"**{framework}**: {tier}")
        else:
            st.info("No framework thresholds triggered")

        # EU Compliance
        st.subheader("🇪🇺 EU AI Act Compliance")

        if assessment.eu_compliant:
            st.success("✅ Model is below EU systemic risk threshold")
        else:
            st.error(
                "⚠️ Model exceeds EU systemic risk threshold (10^25 FLOPS)")

            if assessment.eu_requirements:
                st.markdown("**Required actions:**")
                for req in assessment.eu_requirements:
                    st.markdown(f"- {req}")

        # Gaps
        if assessment.gaps_identified:
            st.subheader("⚠️ Framework Discrepancies")
            for gap in assessment.gaps_identified:
                st.warning(gap)

with tab2:
    st.header("Framework Explorer")

    st.markdown("Explore risk thresholds across different frameworks")

    # Load and display framework data
    try:
        with open('data/processed/frameworks.json', 'r') as f:
            frameworks = json.load(f)

        if 'frameworks' in frameworks:
            for fw in frameworks['frameworks']:
                with st.expander(
                        f"🏢 {fw.get('organization')} - {fw.get('framework_name')}"
                ):
                    for tier in fw.get('risk_tiers', []):
                        st.markdown(f"**{tier.get('tier_name')}**")
                        st.markdown(
                            f"*Threshold:* {tier.get('capability_threshold')}")

                        if tier.get('compute_threshold_flops'):
                            st.markdown(
                                f"*Compute:* {tier.get('compute_threshold_flops')} FLOPS"
                            )

                        if tier.get('evaluation_requirements'):
                            st.markdown(
                                f"*Evals:* {', '.join(tier.get('evaluation_requirements'))}"
                            )

                        st.markdown("---")
        else:
            st.info("No frameworks loaded. Run extraction scripts first.")
    except FileNotFoundError:
        st.warning(
            "No framework data loaded yet. Run extraction scripts first.")

with tab3:
    st.header("About This Tool")

    st.markdown("""
    ### The Problem

    Different AI labs use different safety frameworks:
    - Anthropic has ASL levels (ASL-1, ASL-2, ASL-3)
    - Google DeepMind has CCL tiers
    - OpenAI has preparedness levels
    - The EU AI Act has its own classification

    **Nobody has mapped these together.**

    ### What We Built

    This tool:
    1. Extracts thresholds from 12+ safety frameworks using AI
    2. Maps models to appropriate risk tiers across all frameworks
    3. Checks EU AI Act compliance automatically
    4. Identifies where frameworks disagree

    ### Methodology

    - Multi-model extraction using GPT-4o
    - Consensus building across multiple extraction passes
    - Structured JSON database of all thresholds
    - Real-time risk assessment

    ### Data Sources

    - Common Elements of Frontier AI Safety Policies (METR)
    - AI Safety under EU AI Code of Practice (Georgetown CSET)
    - The Role of Compute Thresholds for AI Governance

    ### Built For

    Technical AI Governance Challenge 2026
    """)
