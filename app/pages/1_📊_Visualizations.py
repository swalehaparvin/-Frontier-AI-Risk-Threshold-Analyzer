import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import json
import sys

sys.path.append('../..')

st.set_page_config(page_title="Visualizations", page_icon="📊", layout="wide")

st.title("📊 Framework Visualizations")

# Load data
try:
    with open('../data/processed/frameworks.json', 'r') as f:
        data = json.load(f)
        frameworks = data.get('frameworks', [])
except:
    st.error("No data loaded. Run extractions first.")
    st.stop()

# Risk Tier Comparison Chart
st.header("Risk Tier Comparison")

if frameworks:
    # Prepare data for visualization
    org_names = []
    tier_counts = []

    for fw in frameworks:
        org_names.append(fw.get('organization'))
        tier_counts.append(len(fw.get('risk_tiers', [])))

    fig = px.bar(x=org_names,
                 y=tier_counts,
                 labels={
                     'x': 'Organization',
                     'y': 'Number of Risk Tiers'
                 },
                 title='Risk Tier Complexity Across Frameworks')

    st.plotly_chart(fig, use_container_width=True)

# Compute Thresholds Timeline
st.header("Compute Threshold Evolution")

try:
    with open('../data/processed/compute_thresholds.json', 'r') as f:
        compute_data = json.load(f)

    thresholds = compute_data.get('compute_thresholds', [])

    if thresholds:
        fig = go.Figure()

        for threshold in thresholds:
            fig.add_trace(
                go.Scatter(x=[threshold.get('year_defined', 2024)],
                           y=[threshold.get('threshold_flops', 0)],
                           mode='markers+text',
                           name=threshold.get('scientific_notation', ''),
                           text=[threshold.get('scientific_notation', '')],
                           textposition="top center",
                           marker=dict(size=15)))

        fig.update_layout(title='FLOP Thresholds Over Time',
                          xaxis_title='Year',
                          yaxis_title='FLOPS (log scale)',
                          yaxis_type='log')

        st.plotly_chart(fig, use_container_width=True)
except:
    st.info("Compute threshold data not available")

# Framework Coverage Matrix
st.header("Framework Coverage Matrix")

coverage_matrix = []
all_capabilities = set()

for fw in frameworks:
    for tier in fw.get('risk_tiers', []):
        capabilities = tier.get('capability_threshold', '')
        # Extract key capability keywords
        if 'CBRN' in capabilities or 'bio' in capabilities:
            all_capabilities.add('CBRN')
        if 'cyber' in capabilities:
            all_capabilities.add('Cyber')
        if 'autonomy' in capabilities or 'autonomous' in capabilities:
            all_capabilities.add('Autonomy')
        if 'persuasion' in capabilities:
            all_capabilities.add('Persuasion')

st.markdown("**Capability Coverage Across Frameworks:**")

for capability in all_capabilities:
    covering_orgs = []
    for fw in frameworks:
        for tier in fw.get('risk_tiers', []):
            if capability.lower() in tier.get('capability_threshold',
                                              '').lower():
                covering_orgs.append(fw.get('organization'))
                break

    st.markdown(f"- **{capability}**: {', '.join(set(covering_orgs))}")
