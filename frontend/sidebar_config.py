# frontend/sidebar_config.py
"""
Enhanced sidebar configuration for QuestAI
Use this to create a consistent, beautiful sidebar across all pages
"""

import streamlit as st
from config import BACKEND_URL
import requests

def create_enhanced_sidebar():
    """Create an enhanced sidebar with navigation and status"""
    
    with st.sidebar:
        # Logo and branding
        st.markdown('''
        <div style="text-align: center; padding: 1rem 0 2rem;">
            <h1 style="
                font-size: 2.5rem;
                font-weight: 800;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                margin-bottom: 0.5rem;
            ">🎯 QuestAI</h1>
            <p style="
                color: #64748b;
                font-size: 0.9rem;
                font-weight: 500;
            ">AI Interview Assistant</p>
        </div>
        ''', unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Navigation section
        st.markdown('''
        <h3 style="
            color: #1e293b;
            font-size: 1.1rem;
            font-weight: 700;
            margin-bottom: 1rem;
        ">📍 Navigation</h3>
        ''', unsafe_allow_html=True)
        
        # Navigation buttons
        if st.button("🏠 Home", use_container_width=True):
            st.switch_page("Home.py")
        
        if st.button("🎓 Teach Mode", use_container_width=True):
            st.switch_page("pages/1_Teach_Mode.py")
        
        if st.button("💼 Experience Mode", use_container_width=True):
            st.switch_page("pages/2_Experience_Mode.py")
        
        if st.button("📊 Match Score", use_container_width=True):
            st.switch_page("pages/3_Match_Score.py")
        
        st.markdown("---")
        
        # System status
        st.markdown('''
        <h3 style="
            color: #1e293b;
            font-size: 1.1rem;
            font-weight: 700;
            margin-bottom: 1rem;
        ">🔧 System Status</h3>
        ''', unsafe_allow_html=True)
        
        try:
            response = requests.get(f"{BACKEND_URL}/health", timeout=3)
            
            if response.status_code == 200:
                data = response.json()
                
                # Status indicator
                st.success("✅ Backend Online")
                
                # Show provider
                provider = data.get('current_provider', 'Unknown')
                st.info(f"🤖 Provider: **{provider.title()}**")
                
                # Mock mode indicator
                if data.get("mock_mode", False):
                    st.warning("🎭 Mock Mode Active")
                else:
                    st.success("🚀 Live AI Mode")
                    
            else:
                st.error("❌ Backend Error")
                
        except:
            st.error("❌ Backend Offline")
        
        st.markdown("---")
        
        # Quick tips
        st.markdown('''
        <h3 style="
            color: #1e293b;
            font-size: 1.1rem;
            font-weight: 700;
            margin-bottom: 1rem;
        ">💡 Quick Tips</h3>
        ''', unsafe_allow_html=True)
        
        with st.expander("📝 Before You Start"):
            st.markdown('''
            - Have your resume ready (PDF/TXT)
            - Prepare the job description
            - Find a quiet environment
            - Allocate 20-30 minutes
            ''')
        
        with st.expander("🎯 Best Practices"):
            st.markdown('''
            - Answer honestly and thoroughly
            - Think before you respond
            - Use real examples (STAR method)
            - Practice regularly for improvement
            ''')
        
        with st.expander("🔍 Mode Selection"):
            st.markdown('''
            **Teach Mode**: For learning and practice  
            **Experience Mode**: For realistic simulation  
            **Match Score**: For quick resume check
            ''')

        st.markdown("---")
        
        # Footer
        st.markdown('''
        <div style="text-align: center; padding: 1rem 0;">
            <p style="color: #94a3b8; font-size: 0.8rem;">
                Made with ❤️ by QuestAI<br>
                <a href="https://github.com/sanyaprem/QuestAI" 
                   target="_blank" 
                   style="color: #667eea; text-decoration: none;">
                    ⭐ GitHub
                </a>
            </p>
        </div>
        ''', unsafe_allow_html=True)


def apply_sidebar_styling():
    """Apply custom CSS for sidebar"""
    st.markdown('''
    <style>
        /* Sidebar styling */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #f8fafc 0%, #ffffff 100%);
        }
        
        [data-testid="stSidebar"] .stButton > button {
            background: white;
            color: #1e293b;
            border: 2px solid #e2e8f0;
            border-radius: 10px;
            padding: 0.75rem 1rem;
            font-weight: 600;
            transition: all 0.3s ease;
            text-align: left;
        }
        
        [data-testid="stSidebar"] .stButton > button:hover {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-color: #667eea;
            transform: translateX(5px);
        }
        
        [data-testid="stSidebar"] hr {
            margin: 1.5rem 0;
            border: none;
            border-top: 2px solid #e2e8f0;
        }
        
        [data-testid="stSidebar"] .stExpander {
            background: white;
            border: 1px solid #e2e8f0;
            border-radius: 10px;
            margin: 0.5rem 0;
        }
    </style>
    ''', unsafe_allow_html=True)