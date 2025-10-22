# frontend/custom_styles.py
"""
Custom styling and UI components for QuestAI
Import this in your pages to maintain consistent styling

Usage:
    from custom_styles import apply_custom_theme, create_page_header
    
    apply_custom_theme()
    create_page_header("Title", "Subtitle", "🎯")
"""

import streamlit as st

def apply_custom_theme():
    """Apply consistent custom theme across all pages"""
    st.markdown('''
    <style>
        /* Import modern font */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');
        
        /* Global font */
        * {
            font-family: 'Inter', sans-serif;
        }
        
        /* Hide default Streamlit branding */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        
        /* Sidebar styling */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
        }
        
        [data-testid="stSidebar"] .css-1d391kg {
            color: #e0e7ff;
        }
        
        /* Button styling */
        .stButton > button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 10px;
            padding: 0.75rem 2rem;
            font-weight: 600;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        }
        
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 25px rgba(102, 126, 234, 0.5);
        }
        
        /* Input fields */
        .stTextInput > div > div > input,
        .stTextArea > div > div > textarea {
            border-radius: 10px;
            border: 2px solid #e2e8f0;
            padding: 0.75rem;
            transition: all 0.3s ease;
        }
        
        .stTextInput > div > div > input:focus,
        .stTextArea > div > div > textarea:focus {
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        
        /* File uploader */
        .stFileUploader {
            border-radius: 15px;
            border: 2px dashed #cbd5e1;
            padding: 2rem;
            transition: all 0.3s ease;
        }
        
        .stFileUploader:hover {
            border-color: #667eea;
            background: rgba(102, 126, 234, 0.05);
        }
        
        /* Chat messages */
        .stChatMessage {
            border-radius: 15px;
            padding: 1rem;
            margin: 0.5rem 0;
            animation: slideIn 0.3s ease;
        }
        
        /* Code editor */
        .stCodeBlock {
            border-radius: 10px;
            border: 1px solid #e2e8f0;
        }
        
        /* Expander */
        .streamlit-expanderHeader {
            background-color: #f8fafc;
            border-radius: 10px;
            font-weight: 600;
        }
        
        /* Metrics */
        [data-testid="stMetricValue"] {
            font-size: 2rem;
            font-weight: 800;
        }
        
        /* Success/Error/Warning boxes */
        .stSuccess, .stError, .stWarning, .stInfo {
            border-radius: 10px;
            padding: 1rem;
            border-left: 4px solid;
        }
        
        /* Animations */
        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateX(-20px);
            }
            to {
                opacity: 1;
                transform: translateX(0);
            }
        }
        
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        
        /* Progress bar */
        .stProgress > div > div > div {
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        }
        
        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {
            gap: 1rem;
        }
        
        .stTabs [data-baseweb="tab"] {
            border-radius: 10px;
            padding: 0.75rem 1.5rem;
            font-weight: 600;
        }
        
        /* Spinner */
        .stSpinner > div {
            border-top-color: #667eea !important;
        }
    </style>
    ''', unsafe_allow_html=True)


def create_page_header(title, subtitle, icon="🎯"):
    """Create a consistent page header"""
    st.markdown(f'''
    <div style="
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 20px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 40px rgba(102, 126, 234, 0.3);
    ">
        <h1 style="
            color: white;
            font-size: 2.5rem;
            font-weight: 800;
            margin-bottom: 0.5rem;
        ">{icon} {title}</h1>
        <p style="
            color: #e0e7ff;
            font-size: 1.2rem;
            font-weight: 300;
        ">{subtitle}</p>
    </div>
    ''', unsafe_allow_html=True)


def create_info_card(title, content, icon="ℹ️", color="#667eea"):
    """Create an info card"""
    st.markdown(f'''
    <div style="
        background: white;
        border-left: 4px solid {color};
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    ">
        <h3 style="
            color: {color};
            font-size: 1.3rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
        ">{icon} {title}</h3>
        <p style="
            color: #475569;
            line-height: 1.6;
        ">{content}</p>
    </div>
    ''', unsafe_allow_html=True)


def create_progress_tracker(current_step, total_steps, step_name):
    """Create a visual progress tracker"""
    progress = current_step / total_steps
    
    st.markdown(f'''
    <div style="
        background: white;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    ">
        <div style="
            display: flex;
            justify-content: space-between;
            margin-bottom: 0.5rem;
        ">
            <span style="font-weight: 600; color: #1e293b;">
                {step_name}
            </span>
            <span style="color: #64748b;">
                {current_step}/{total_steps}
            </span>
        </div>
        <div style="
            background: #e2e8f0;
            height: 8px;
            border-radius: 10px;
            overflow: hidden;
        ">
            <div style="
                background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
                width: {progress * 100}%;
                height: 100%;
                transition: width 0.5s ease;
            "></div>
        </div>
    </div>
    ''', unsafe_allow_html=True)


def create_stat_card(label, value, icon="📊"):
    """Create a stat card for metrics"""
    return f'''
    <div style="
        background: white;
        border-radius: 15px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        transition: transform 0.3s ease;
    " onmouseover="this.style.transform='translateY(-5px)'" 
       onmouseout="this.style.transform='translateY(0)'">
        <div style="font-size: 2rem; margin-bottom: 0.5rem;">{icon}</div>
        <div style="
            font-size: 2rem;
            font-weight: 800;
            color: #667eea;
            margin-bottom: 0.25rem;
        ">{value}</div>
        <div style="
            color: #64748b;
            font-size: 0.9rem;
            font-weight: 600;
        ">{label}</div>
    </div>
    '''


def create_timeline_step(number, title, description, is_active=False):
    """Create a timeline step indicator"""
    active_color = "#667eea" if is_active else "#cbd5e1"
    
    return f'''
    <div style="
        display: flex;
        align-items: flex-start;
        margin: 1.5rem 0;
        position: relative;
    ">
        <div style="
            min-width: 50px;
            height: 50px;
            border-radius: 50%;
            background: {active_color};
            color: white;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 800;
            font-size: 1.2rem;
            margin-right: 1rem;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        ">{number}</div>
        <div style="flex: 1;">
            <h4 style="
                color: #1e293b;
                font-weight: 700;
                margin-bottom: 0.25rem;
            ">{title}</h4>
            <p style="
                color: #64748b;
                line-height: 1.6;
            ">{description}</p>
        </div>
    </div>
    '''


def show_loading_state(message="Processing..."):
    """Show a custom loading animation"""
    st.markdown(f'''
    <div style="
        text-align: center;
        padding: 2rem;
    ">
        <div style="
            display: inline-block;
            width: 50px;
            height: 50px;
            border: 5px solid #e2e8f0;
            border-top: 5px solid #667eea;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        "></div>
        <p style="
            color: #64748b;
            margin-top: 1rem;
            font-weight: 600;
        ">{message}</p>
    </div>
    <style>
        @keyframes spin {{
            0% {{ transform: rotate(0deg); }}
            100% {{ transform: rotate(360deg); }}
        }}
    </style>
    ''', unsafe_allow_html=True)


def create_feature_badge(text, color="#667eea"):
    """Create a small feature badge"""
    return f'''
    <span style="
        display: inline-block;
        background: {color};
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        margin: 0.25rem;
    ">{text}</span>
    '''