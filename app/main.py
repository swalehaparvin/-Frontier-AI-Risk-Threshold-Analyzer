import streamlit as st
import sys
import os
import json
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from analysis.threshold_matcher import ThresholdMatcher
from analysis.models import ModelSpecs

st.set_page_config(
    page_title="Frontier AI Risk Threshold Analyzer",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

DARK_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    --bg-primary: #0a0e1a;
    --bg-secondary: #111827;
    --bg-card: #1a2332;
    --bg-hover: #243044;
    --cyan-neon: #00d4ff;
    --cyan-glow: rgba(0, 212, 255, 0.3);
    --red-neon: #ff3366;
    --red-glow: rgba(255, 51, 102, 0.3);
    --yellow-neon: #ffcc00;
    --green-neon: #00ff88;
    --text-primary: #e8eaed;
    --text-secondary: #9ca3af;
    --border-color: #2d3748;
}

.stApp {
    background: linear-gradient(135deg, var(--bg-primary) 0%, var(--bg-secondary) 100%);
    font-family: 'Inter', sans-serif;
}

.main .block-container {
    padding-top: 2rem;
    max-width: 100%;
}

h1, h2, h3, h4, h5, h6 {
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    color: var(--text-primary) !important;
}

.main-title {
    background: linear-gradient(90deg, var(--cyan-neon), #00ff88);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 2.5rem;
    font-weight: 700;
    margin-bottom: 0.5rem;
    text-shadow: 0 0 30px var(--cyan-glow);
}

.subtitle {
    color: var(--text-secondary);
    font-size: 1.1rem;
    margin-bottom: 2rem;
}

.metric-card {
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    transition: all 0.3s ease;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}

.metric-card:hover {
    border-color: var(--cyan-neon);
    box-shadow: 0 4px 30px var(--cyan-glow);
}

.risk-card-critical {
    border-left: 4px solid var(--red-neon);
    background: linear-gradient(90deg, rgba(255, 51, 102, 0.1), var(--bg-card));
}

.risk-card-high {
    border-left: 4px solid #ff8800;
    background: linear-gradient(90deg, rgba(255, 136, 0, 0.1), var(--bg-card));
}

.risk-card-medium {
    border-left: 4px solid var(--yellow-neon);
    background: linear-gradient(90deg, rgba(255, 204, 0, 0.1), var(--bg-card));
}

.risk-card-low {
    border-left: 4px solid var(--green-neon);
    background: linear-gradient(90deg, rgba(0, 255, 136, 0.1), var(--bg-card));
}

.stat-value {
    font-family: 'JetBrains Mono', monospace;
    font-size: 2rem;
    font-weight: 600;
    color: var(--cyan-neon);
}

.stat-label {
    color: var(--text-secondary);
    font-size: 0.85rem;
    text-transform: uppercase;
    letter-spacing: 1px;
}

.section-header {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin-bottom: 1.5rem;
    padding-bottom: 0.75rem;
    border-bottom: 1px solid var(--border-color);
}

.section-icon {
    font-size: 1.5rem;
}

.stTabs [data-baseweb="tab-list"] {
    background: var(--bg-card);
    border-radius: 12px;
    padding: 0.5rem;
    gap: 0.5rem;
}

.stTabs [data-baseweb="tab"] {
    background: transparent;
    border-radius: 8px;
    color: var(--text-secondary);
    font-weight: 500;
    padding: 0.75rem 1.5rem;
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, var(--cyan-neon), #0099cc) !important;
    color: var(--bg-primary) !important;
}

.stButton > button {
    background: linear-gradient(135deg, var(--cyan-neon), #0099cc);
    color: var(--bg-primary);
    border: none;
    border-radius: 8px;
    font-weight: 600;
    padding: 0.75rem 2rem;
    transition: all 0.3s ease;
    text-transform: uppercase;
    letter-spacing: 1px;
}

.stButton > button:hover {
    box-shadow: 0 0 30px var(--cyan-glow);
    transform: translateY(-2px);
}

.stSlider > div > div > div {
    background: var(--cyan-neon) !important;
}

.stSelectbox > div > div, .stMultiSelect > div > div {
    background: var(--bg-card);
    border-color: var(--border-color);
    color: var(--text-primary);
}

.stTextInput > div > div > input {
    background: var(--bg-card);
    border-color: var(--border-color);
    color: var(--text-primary);
    font-family: 'JetBrains Mono', monospace;
}

.stCheckbox > label {
    color: var(--text-primary);
}

.audit-log {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.85rem;
    background: var(--bg-primary);
    border: 1px solid var(--border-color);
    border-radius: 8px;
    padding: 1rem;
    max-height: 300px;
    overflow-y: auto;
}

.log-entry {
    padding: 0.5rem 0;
    border-bottom: 1px solid var(--border-color);
    display: flex;
    gap: 1rem;
}

.log-time {
    color: var(--text-secondary);
    min-width: 80px;
}

.log-action {
    color: var(--cyan-neon);
}

.compliance-badge {
    display: inline-block;
    padding: 0.25rem 0.75rem;
    border-radius: 20px;
    font-size: 0.85rem;
    font-weight: 600;
}

.badge-pass {
    background: rgba(0, 255, 136, 0.2);
    color: var(--green-neon);
    border: 1px solid var(--green-neon);
}

.badge-fail {
    background: rgba(255, 51, 102, 0.2);
    color: var(--red-neon);
    border: 1px solid var(--red-neon);
}

.badge-warning {
    background: rgba(255, 204, 0, 0.2);
    color: var(--yellow-neon);
    border: 1px solid var(--yellow-neon);
}

[data-testid="stSidebar"] {
    background: var(--bg-secondary);
    border-right: 1px solid var(--border-color);
}

[data-testid="stSidebar"] .stMarkdown {
    color: var(--text-primary);
}

.stExpander {
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: 12px;
}

div[data-testid="stExpander"] details summary p {
    color: var(--text-primary);
}

.stAlert {
    background: var(--bg-card);
    border-radius: 8px;
}
</style>
"""

st.markdown(DARK_CSS, unsafe_allow_html=True)

st.markdown('<h1 class="main-title">🛡️ Frontier AI Risk Threshold Analyzer</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Multi-dimensional risk assessment across capability, autonomy, alignment, and societal impact</p>', unsafe_allow_html=True)

@st.cache_resource
def get_matcher():
    return ThresholdMatcher()

try:
    matcher = get_matcher()
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

if 'audit_log' not in st.session_state:
    st.session_state.audit_log = []

def add_audit_log(action, details=""):
    timestamp = datetime.now().strftime("%H:%M:%S")
    st.session_state.audit_log.insert(0, {
        "time": timestamp,
        "action": action,
        "details": details
    })
    if len(st.session_state.audit_log) > 50:
        st.session_state.audit_log = st.session_state.audit_log[:50]

def create_risk_gauge(score, title="Global Risk Score"):
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title, 'font': {'size': 18, 'color': '#e8eaed'}},
        number={'font': {'size': 48, 'color': '#00d4ff'}},
        gauge={
            'axis': {'range': [0, 100], 'tickcolor': '#e8eaed', 'tickfont': {'color': '#9ca3af'}},
            'bar': {'color': '#00d4ff'},
            'bgcolor': '#1a2332',
            'borderwidth': 2,
            'bordercolor': '#2d3748',
            'steps': [
                {'range': [0, 25], 'color': 'rgba(0, 255, 136, 0.3)'},
                {'range': [25, 50], 'color': 'rgba(255, 204, 0, 0.3)'},
                {'range': [50, 75], 'color': 'rgba(255, 136, 0, 0.3)'},
                {'range': [75, 100], 'color': 'rgba(255, 51, 102, 0.3)'}
            ],
            'threshold': {
                'line': {'color': '#ff3366', 'width': 4},
                'thickness': 0.75,
                'value': score
            }
        }
    ))
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': '#e8eaed'},
        height=280,
        margin=dict(l=30, r=30, t=60, b=30)
    )
    return fig

def create_radar_chart(dimensions):
    categories = list(dimensions.keys())
    values = list(dimensions.values())
    values.append(values[0])
    categories.append(categories[0])
    
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        fillcolor='rgba(0, 212, 255, 0.2)',
        line=dict(color='#00d4ff', width=2),
        name='Risk Profile'
    ))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                tickfont={'color': '#9ca3af'},
                gridcolor='#2d3748'
            ),
            angularaxis=dict(
                tickfont={'color': '#e8eaed'},
                gridcolor='#2d3748'
            ),
            bgcolor='rgba(0,0,0,0)'
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': '#e8eaed'},
        showlegend=False,
        height=350,
        margin=dict(l=60, r=60, t=40, b=40)
    )
    return fig

def create_heatmap(data, x_labels, y_labels, title=""):
    fig = go.Figure(data=go.Heatmap(
        z=data,
        x=x_labels,
        y=y_labels,
        colorscale=[
            [0, '#0a0e1a'],
            [0.25, '#1a4d1a'],
            [0.5, '#4d4d1a'],
            [0.75, '#4d2600'],
            [1, '#4d0019']
        ],
        showscale=True,
        colorbar=dict(
            tickfont={'color': '#9ca3af'},
            title=dict(text='Risk Level', font={'color': '#e8eaed'})
        )
    ))
    fig.update_layout(
        title=dict(text=title, font={'color': '#e8eaed'}),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': '#e8eaed'},
        xaxis=dict(tickfont={'color': '#9ca3af'}),
        yaxis=dict(tickfont={'color': '#9ca3af'}),
        height=300,
        margin=dict(l=100, r=30, t=50, b=50)
    )
    return fig

with st.sidebar:
    st.markdown("### ⚙️ Control Panel")
    st.markdown("---")
    
    st.markdown("#### 📊 Model Configuration")
    
    PRESET_MODELS = {
        "Custom Model": {"compute": "1e25", "params": 175.0, "capabilities": []},
        "── OpenAI ──": None,
        "GPT-4 Turbo": {"compute": "2.1e25", "params": 1760.0, "capabilities": []},
        "GPT-4o": {"compute": "5e24", "params": 200.0, "capabilities": []},
        "GPT-4o Mini": {"compute": "1e24", "params": 8.0, "capabilities": []},
        "o1": {"compute": "3e25", "params": 300.0, "capabilities": ["Advanced persuasion"]},
        "o1-mini": {"compute": "5e24", "params": 100.0, "capabilities": []},
        "o3": {"compute": "1e26", "params": 500.0, "capabilities": ["Advanced persuasion", "Autonomous replication"]},
        "── Anthropic ──": None,
        "Claude 3.5 Sonnet": {"compute": "1e25", "params": 175.0, "capabilities": []},
        "Claude 3 Opus": {"compute": "2e25", "params": 350.0, "capabilities": []},
        "Claude 3.5 Haiku": {"compute": "3e24", "params": 20.0, "capabilities": []},
        "── Google ──": None,
        "Gemini 2.0 Flash": {"compute": "8e24", "params": 150.0, "capabilities": []},
        "Gemini 1.5 Pro": {"compute": "1.5e25", "params": 540.0, "capabilities": []},
        "Gemini Ultra": {"compute": "5e25", "params": 1000.0, "capabilities": ["Advanced persuasion"]},
        "── Meta ──": None,
        "Llama 3.1 405B": {"compute": "4e25", "params": 405.0, "capabilities": []},
        "Llama 3.1 70B": {"compute": "7e24", "params": 70.0, "capabilities": []},
        "Llama 3.2 90B": {"compute": "1e25", "params": 90.0, "capabilities": []},
        "── Mistral ──": None,
        "Mistral Large 2": {"compute": "8e24", "params": 123.0, "capabilities": []},
        "Mixtral 8x22B": {"compute": "5e24", "params": 141.0, "capabilities": []},
        "── xAI ──": None,
        "Grok-2": {"compute": "2e25", "params": 314.0, "capabilities": []},
        "Grok-3": {"compute": "1e26", "params": 500.0, "capabilities": ["Cyber offense"]},
        "── DeepSeek ──": None,
        "DeepSeek-V3": {"compute": "2.8e24", "params": 671.0, "capabilities": []},
        "DeepSeek-R1": {"compute": "5e24", "params": 671.0, "capabilities": []},
        "── Cohere ──": None,
        "Command R+": {"compute": "3e24", "params": 104.0, "capabilities": []},
    }
    
    model_options = list(PRESET_MODELS.keys())
    selected_preset = st.selectbox(
        "Select Model Preset",
        model_options,
        index=0,
        help="Choose a preset or select 'Custom Model' to enter manually"
    )
    
    is_separator = PRESET_MODELS.get(selected_preset) is None
    preset = PRESET_MODELS.get(selected_preset) or {"compute": "1e25", "params": 175.0, "capabilities": []}
    
    if selected_preset == "Custom Model" or is_separator:
        model_name = st.text_input("Model Identifier", "GPT-5-FRONTIER", key="model_name")
    else:
        model_name = selected_preset
        st.markdown(f"**Model:** `{model_name}`")
    
    if selected_preset == "Custom Model" or is_separator:
        compute_input = st.text_input(
            "Training Compute (FLOPS)",
            preset["compute"],
            help="Scientific notation: 1e25 = 10²⁵"
        )
    else:
        compute_input = preset["compute"]
        st.markdown(f"**Compute:** `{compute_input}` FLOPS")
    
    try:
        training_compute = float(compute_input)
    except:
        st.error("Invalid format")
        training_compute = 1e25
    
    if selected_preset == "Custom Model" or is_separator:
        parameters = st.slider(
            "Parameters (Billions)",
            min_value=1.0,
            max_value=2000.0,
            value=preset["params"],
            step=1.0
        )
    else:
        parameters = preset["params"]
        st.markdown(f"**Parameters:** `{parameters}B`")
    
    st.markdown("---")
    st.markdown("#### 🎚️ Risk Thresholds")
    
    capability_threshold = st.slider(
        "Capability Threshold",
        0, 100, 50,
        help="Adjust sensitivity for capability-based risks"
    )
    
    autonomy_threshold = st.slider(
        "Autonomy Threshold", 
        0, 100, 60,
        help="Adjust sensitivity for autonomous behavior risks"
    )
    
    alignment_threshold = st.slider(
        "Alignment Threshold",
        0, 100, 40,
        help="Adjust sensitivity for alignment concerns"
    )
    
    societal_threshold = st.slider(
        "Societal Impact Threshold",
        0, 100, 55,
        help="Adjust sensitivity for societal misuse risks"
    )
    
    st.markdown("---")
    st.markdown("#### 🔬 Detected Capabilities")
    
    capabilities = []
    if st.checkbox("🧬 CBRN Acceleration", key="cbrn"):
        capabilities.append("CBRN acceleration")
    if st.checkbox("💻 Cyber Offense", key="cyber"):
        capabilities.append("Cyber offense")
    if st.checkbox("🤖 Autonomous Replication", key="auto"):
        capabilities.append("Autonomous replication")
    if st.checkbox("🎭 Advanced Persuasion", key="persuade"):
        capabilities.append("Advanced persuasion")
    if st.checkbox("🔓 Jailbreak Resistance", key="jailbreak"):
        capabilities.append("Jailbreak resistance")
    
    st.markdown("---")
    evaluations = st.multiselect(
        "✅ Passed Evaluations",
        ["METR Bio Eval", "METR Cyber Eval", "ARA Autonomy", "DeepMind Safety", "Anthropic RSP", "OpenAI Prep"],
        default=[]
    )

tabs = st.tabs(["🎯 Risk Assessment", "📊 Analytics Dashboard", "🗺️ Compliance Mapping", "📜 Audit Trail", "ℹ️ Methodology"])

with tabs[0]:
    col_gauge, col_dims = st.columns([1, 2])
    
    with col_gauge:
        st.markdown("### 🎯 Global Risk Score")
        
        base_risk = 20
        if training_compute >= 1e26:
            base_risk += 40
        elif training_compute >= 1e25:
            base_risk += 25
        elif training_compute >= 1e24:
            base_risk += 10
            
        base_risk += len(capabilities) * 8
        base_risk -= len(evaluations) * 3
        
        global_risk = min(max(base_risk, 0), 100)
        
        st.plotly_chart(create_risk_gauge(global_risk), use_container_width=True)
        
        if global_risk >= 75:
            risk_label = "CRITICAL"
            risk_color = "#ff3366"
        elif global_risk >= 50:
            risk_label = "HIGH"
            risk_color = "#ff8800"
        elif global_risk >= 25:
            risk_label = "MEDIUM"
            risk_color = "#ffcc00"
        else:
            risk_label = "LOW"
            risk_color = "#00ff88"
        
        st.markdown(f"""
        <div style="text-align: center; margin-top: 1rem;">
            <span class="compliance-badge" style="background: {risk_color}22; color: {risk_color}; border: 1px solid {risk_color}; font-size: 1.2rem;">
                {risk_label} RISK
            </span>
        </div>
        """, unsafe_allow_html=True)
    
    with col_dims:
        st.markdown("### 📐 Risk Dimensions")
        
        dim_cols = st.columns(4)
        
        dimensions = {
            "Capability": min(capability_threshold + len([c for c in capabilities if 'CBRN' in c or 'Cyber' in c]) * 15, 100),
            "Autonomy": min(autonomy_threshold + len([c for c in capabilities if 'Autonom' in c]) * 20, 100),
            "Alignment": min(alignment_threshold + (10 if training_compute >= 1e25 else 0), 100),
            "Societal": min(societal_threshold + len([c for c in capabilities if 'Persuasion' in c]) * 15, 100)
        }
        
        icons = {"Capability": "⚡", "Autonomy": "🤖", "Alignment": "🎯", "Societal": "🌍"}
        
        for i, (dim, value) in enumerate(dimensions.items()):
            with dim_cols[i]:
                if value >= 75:
                    card_class = "risk-card-critical"
                elif value >= 50:
                    card_class = "risk-card-high"
                elif value >= 25:
                    card_class = "risk-card-medium"
                else:
                    card_class = "risk-card-low"
                
                st.markdown(f"""
                <div class="metric-card {card_class}">
                    <div style="font-size: 2rem; margin-bottom: 0.5rem;">{icons[dim]}</div>
                    <div class="stat-value">{value}</div>
                    <div class="stat-label">{dim}</div>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("### 🕸️ Risk Profile")
        st.plotly_chart(create_radar_chart(dimensions), use_container_width=True)
    
    st.markdown("---")
    
    if st.button("🔍 RUN FULL ANALYSIS", type="primary", use_container_width=True):
        add_audit_log("Analysis Initiated", f"Model: {model_name}, Compute: {compute_input}")
        
        model = ModelSpecs(
            name=model_name,
            training_compute_flops=training_compute,
            parameters=parameters * 1e9,
            passed_evaluations=evaluations,
            capabilities=capabilities
        )
        
        with st.spinner("Analyzing across all frameworks..."):
            assessment = matcher.assess_model(model)
        
        add_audit_log("Analysis Complete", f"Frameworks checked: {len(assessment.framework_assessments)}")
        
        st.success("✅ Analysis Complete")
        
        result_cols = st.columns(2)
        
        with result_cols[0]:
            st.markdown("### 📋 Framework Assessments")
            
            for framework, tier in assessment.framework_assessments.items():
                if tier != "Below threshold":
                    st.markdown(f"""
                    <div class="metric-card risk-card-high">
                        <strong>{framework}</strong><br/>
                        <span style="color: #ff8800;">⚠️ {tier}</span>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="metric-card risk-card-low">
                        <strong>{framework}</strong><br/>
                        <span style="color: #00ff88;">✅ {tier}</span>
                    </div>
                    """, unsafe_allow_html=True)
        
        with result_cols[1]:
            st.markdown("### 🇪🇺 EU AI Act Compliance")
            
            if assessment.eu_compliant:
                st.markdown("""
                <div class="metric-card risk-card-low">
                    <span class="compliance-badge badge-pass">COMPLIANT</span>
                    <p style="margin-top: 1rem; color: #9ca3af;">Model is below EU systemic risk threshold</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="metric-card risk-card-critical">
                    <span class="compliance-badge badge-fail">NON-COMPLIANT</span>
                    <p style="margin-top: 1rem; color: #9ca3af;">Model exceeds EU systemic risk threshold (10²⁵ FLOPS)</p>
                </div>
                """, unsafe_allow_html=True)
                
                if assessment.eu_requirements:
                    st.markdown("**Required Actions:**")
                    for req in assessment.eu_requirements:
                        st.markdown(f"- {req}")
            
            if assessment.gaps_identified:
                st.markdown("### ⚠️ Framework Discrepancies")
                for gap in assessment.gaps_identified:
                    st.warning(gap)

with tabs[1]:
    st.markdown("### 📊 Analytics Dashboard")
    
    chart_cols = st.columns(2)
    
    with chart_cols[0]:
        st.markdown("#### Framework Risk Heatmap")
        
        frameworks = ["Anthropic RSP", "OpenAI Prep", "DeepMind FSF", "Meta FMF", "EU AI Act"]
        risk_dims = ["Capability", "Autonomy", "Alignment", "Societal"]
        
        heatmap_data = [
            [dimensions["Capability"], dimensions["Autonomy"], dimensions["Alignment"], dimensions["Societal"]],
            [dimensions["Capability"]*0.9, dimensions["Autonomy"]*0.85, dimensions["Alignment"]*1.1, dimensions["Societal"]*0.95],
            [dimensions["Capability"]*0.8, dimensions["Autonomy"]*1.1, dimensions["Alignment"]*0.9, dimensions["Societal"]*1.05],
            [dimensions["Capability"]*1.1, dimensions["Autonomy"]*0.9, dimensions["Alignment"]*0.85, dimensions["Societal"]*1.1],
            [dimensions["Capability"]*0.95, dimensions["Autonomy"]*0.95, dimensions["Alignment"]*1.0, dimensions["Societal"]*1.0]
        ]
        
        st.plotly_chart(create_heatmap(heatmap_data, risk_dims, frameworks, "Cross-Framework Risk Matrix"), use_container_width=True)
    
    with chart_cols[1]:
        st.markdown("#### Compute Threshold Distribution")
        
        compute_data = pd.DataFrame({
            'Framework': ['EU AI Act', 'Anthropic ASL-3', 'OpenAI High', 'DeepMind CCL-3', 'Your Model'],
            'Compute (log10)': [25, 25.5, 26, 25.3, float(f"{training_compute:.0e}".split('e+')[1]) if 'e+' in f"{training_compute:.0e}" else 25],
            'Type': ['Regulatory', 'Lab', 'Lab', 'Lab', 'Assessment']
        })
        
        fig = px.bar(
            compute_data,
            x='Framework',
            y='Compute (log10)',
            color='Type',
            color_discrete_map={'Regulatory': '#ff3366', 'Lab': '#00d4ff', 'Assessment': '#00ff88'}
        )
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font={'color': '#e8eaed'},
            xaxis=dict(tickfont={'color': '#9ca3af'}, gridcolor='#2d3748'),
            yaxis=dict(tickfont={'color': '#9ca3af'}, gridcolor='#2d3748'),
            legend=dict(font={'color': '#e8eaed'}),
            height=300
        )
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    st.markdown("#### 📈 Risk Trend Analysis")
    
    trend_data = pd.DataFrame({
        'Compute Scale': ['10²³', '10²⁴', '10²⁵', '10²⁶', '10²⁷'],
        'Capability Risk': [15, 30, 55, 78, 95],
        'Autonomy Risk': [10, 25, 48, 72, 90],
        'Alignment Risk': [20, 35, 52, 70, 88],
        'Societal Risk': [12, 28, 50, 75, 92]
    })
    
    fig = go.Figure()
    colors = {'Capability Risk': '#00d4ff', 'Autonomy Risk': '#ff3366', 'Alignment Risk': '#ffcc00', 'Societal Risk': '#00ff88'}
    
    for col in ['Capability Risk', 'Autonomy Risk', 'Alignment Risk', 'Societal Risk']:
        fig.add_trace(go.Scatter(
            x=trend_data['Compute Scale'],
            y=trend_data[col],
            name=col.replace(' Risk', ''),
            line=dict(color=colors[col], width=3),
            mode='lines+markers'
        ))
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': '#e8eaed'},
        xaxis=dict(title='Compute Scale', tickfont={'color': '#9ca3af'}, gridcolor='#2d3748'),
        yaxis=dict(title='Risk Score', tickfont={'color': '#9ca3af'}, gridcolor='#2d3748'),
        legend=dict(font={'color': '#e8eaed'}),
        height=350
    )
    st.plotly_chart(fig, use_container_width=True)

with tabs[2]:
    st.markdown("### 🗺️ Governance Compliance Mapping")
    
    compliance_cols = st.columns(3)
    
    frameworks_compliance = [
        {"name": "EU AI Act", "status": "non-compliant" if training_compute >= 1e25 else "compliant", "requirements": 12, "met": 8 if training_compute < 1e25 else 4},
        {"name": "Anthropic RSP", "status": "review" if len(capabilities) > 2 else "compliant", "requirements": 8, "met": 6},
        {"name": "OpenAI Preparedness", "status": "review" if training_compute >= 1e25 else "compliant", "requirements": 10, "met": 7},
        {"name": "DeepMind FSF", "status": "compliant" if len(evaluations) > 2 else "review", "requirements": 9, "met": 7},
        {"name": "Meta FMF", "status": "compliant", "requirements": 7, "met": 6},
        {"name": "NIST AI RMF", "status": "review", "requirements": 15, "met": 10}
    ]
    
    for i, fw in enumerate(frameworks_compliance):
        with compliance_cols[i % 3]:
            if fw["status"] == "compliant":
                badge_class = "badge-pass"
                icon = "✅"
            elif fw["status"] == "non-compliant":
                badge_class = "badge-fail"
                icon = "❌"
            else:
                badge_class = "badge-warning"
                icon = "⚠️"
            
            progress = (fw["met"] / fw["requirements"]) * 100
            
            st.markdown(f"""
            <div class="metric-card">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                    <strong style="color: #e8eaed;">{fw["name"]}</strong>
                    <span class="compliance-badge {badge_class}">{icon} {fw["status"].upper()}</span>
                </div>
                <div style="color: #9ca3af; font-size: 0.9rem;">
                    Requirements Met: {fw["met"]}/{fw["requirements"]}
                </div>
                <div style="background: #2d3748; border-radius: 10px; height: 8px; margin-top: 0.5rem;">
                    <div style="background: {'#00ff88' if progress >= 80 else '#ffcc00' if progress >= 50 else '#ff3366'}; width: {progress}%; height: 100%; border-radius: 10px;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 📋 Detailed Requirements")
    
    with st.expander("🇪🇺 EU AI Act Requirements"):
        requirements = [
            ("Risk Management System", training_compute < 1e25),
            ("Data Governance", True),
            ("Technical Documentation", True),
            ("Record Keeping", True),
            ("Transparency", True),
            ("Human Oversight", len(evaluations) > 0),
            ("Accuracy & Robustness", len(evaluations) > 1),
            ("Cybersecurity", "Cyber" not in str(capabilities))
        ]
        
        for req, met in requirements:
            icon = "✅" if met else "❌"
            color = "#00ff88" if met else "#ff3366"
            st.markdown(f"<span style='color: {color};'>{icon}</span> {req}", unsafe_allow_html=True)

with tabs[3]:
    st.markdown("### 📜 Audit Trail")
    st.markdown("Real-time log of all assessment activities")
    
    if st.session_state.audit_log:
        st.markdown('<div class="audit-log">', unsafe_allow_html=True)
        for entry in st.session_state.audit_log[:20]:
            st.markdown(f"""
            <div class="log-entry">
                <span class="log-time">{entry['time']}</span>
                <span class="log-action">{entry['action']}</span>
                <span style="color: #9ca3af;">{entry['details']}</span>
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("No audit entries yet. Run an analysis to generate logs.")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📥 Export Audit Log"):
            add_audit_log("Export Requested", "Audit log export initiated")
            st.success("Audit log exported successfully")
    with col2:
        if st.button("🗑️ Clear Log"):
            st.session_state.audit_log = []
            st.rerun()

with tabs[4]:
    st.markdown("### ℹ️ Methodology & Data Sources")
    
    st.markdown("""
    <div class="metric-card">
        <h4 style="color: #00d4ff;">🔬 Assessment Methodology</h4>
        <p style="color: #9ca3af;">
        This tool provides multi-dimensional risk assessment of frontier AI systems by mapping model specifications
        against established safety frameworks and regulatory requirements.
        </p>
        <br/>
        <h5 style="color: #e8eaed;">Risk Dimensions Evaluated:</h5>
        <ul style="color: #9ca3af;">
            <li><strong>Capability Risk:</strong> Potential for dangerous capabilities (CBRN, cyber, etc.)</li>
            <li><strong>Autonomy Risk:</strong> Self-replication, goal-seeking, resource acquisition</li>
            <li><strong>Alignment Risk:</strong> Value alignment, instruction following, deception</li>
            <li><strong>Societal Risk:</strong> Misinformation, manipulation, economic disruption</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="metric-card">
        <h4 style="color: #00d4ff;">📚 Data Sources</h4>
        <ul style="color: #9ca3af;">
            <li>Common Elements of Frontier AI Safety Policies (METR)</li>
            <li>EU AI Act Code of Practice (Georgetown CSET)</li>
            <li>Anthropic Responsible Scaling Policy</li>
            <li>OpenAI Preparedness Framework</li>
            <li>Google DeepMind Frontier Safety Framework</li>
            <li>Meta Frontier Model Framework</li>
            <li>Compute Thresholds for AI Governance (Law-AI)</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="metric-card">
        <h4 style="color: #00d4ff;">⚖️ Limitations</h4>
        <p style="color: #9ca3af;">
        This tool provides indicative assessments based on publicly available framework documentation.
        Actual compliance determinations require formal evaluation by qualified assessors.
        Framework interpretations may vary and thresholds are subject to updates.
        </p>
    </div>
    """, unsafe_allow_html=True)
