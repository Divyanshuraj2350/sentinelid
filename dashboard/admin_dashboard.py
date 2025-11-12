
import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import json
from datetime import datetime

st.set_page_config(page_title="SentinelID Admin Dashboard", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    .main { padding: 20px; }
    h1 { color: #667eea; text-align: center; }
</style>
""", unsafe_allow_html=True)

st.title("🛡️ SentinelID Admin Dashboard")
st.subheader("Real-time Behavioral Authentication Monitoring")

API_URL = "http://127.0.0.1:5000/api"

col1, col2, col3 = st.columns(3)

try:
    active_sessions = requests.get(f"{API_URL}/admin/active-sessions").json()
    alerts = requests.get(f"{API_URL}/admin/alerts").json()
    
    with col1:
        st.metric("Active Sessions", active_sessions.get('total_active', 0))
    
    with col2:
        st.metric("Active Alerts", alerts.get('total_alerts', 0))
    
    with col3:
        st.metric("System Status", "✅ Online")
    
    st.divider()
    
    tab1, tab2, tab3 = st.tabs(["👥 Active Sessions", "⚠️ Anomaly Alerts", "📊 Analytics"])
    
    with tab1:
        st.subheader("Active User Sessions")
        if active_sessions.get('sessions'):
            df_sessions = pd.DataFrame(active_sessions['sessions'])
            st.dataframe(df_sessions, use_container_width=True)
            
            st.subheader("Session Confidence Distribution")
            if not df_sessions.empty:
                fig = px.bar(df_sessions, x='user_id', y='current_confidence', title="User Confidence Scores")
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No active sessions")
    
    with tab2:
        st.subheader("Recent Anomaly Alerts")
        if alerts.get('alerts'):
            df_alerts = pd.DataFrame(alerts['alerts'])
            st.dataframe(df_alerts, use_container_width=True)
            
            st.subheader("Alert Severity Distribution")
            severity_counts = df_alerts['severity'].value_counts()
            fig = px.pie(values=severity_counts.values, names=severity_counts.index, title="Alerts by Severity")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No active alerts")
    
    with tab3:
        st.subheader("System Analytics")
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Total Sessions", active_sessions.get('total_active', 0))
        
        with col2:
            st.metric("Total Alerts", alerts.get('total_alerts', 0))
        
        st.info("Dashboard updates in real-time. Refresh to see latest data.")

except requests.exceptions.ConnectionError:
    st.error("❌ Cannot connect to SentinelID Backend. Make sure it's running on http://127.0.0.1:5000")
except Exception as e:
    st.error(f"Error: {str(e)}")

st.divider()
st.caption("SentinelID Admin Dashboard | Real-time Behavioral Authentication Monitoring")
EOF
pip install streamlit plotly

cd ~/Desktop/SentinelID/dashboard

streamlit run admin_dashboard.py

cd ~/Desktop/SentinelID

mkdir -p dashboard

cd dashboard

cat > admin_dashboard.py << 'DASHEOF'

import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import json
from datetime import datetime

st.set_page_config(page_title="SentinelID Admin Dashboard", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    .main { padding: 20px; }
    h1 { color: #667eea; text-align: center; }
</style>
""", unsafe_allow_html=True)

st.title("🛡️ SentinelID Admin Dashboard")
st.subheader("Real-time Behavioral Authentication Monitoring")

API_URL = "http://127.0.0.1:5000/api"

col1, col2, col3 = st.columns(3)

try:
    active_sessions = requests.get(f"{API_URL}/admin/active-sessions").json()
    alerts = requests.get(f"{API_URL}/admin/alerts").json()
    
    with col1:
        st.metric("Active Sessions", active_sessions.get('total_active', 0))
    
    with col2:
        st.metric("Active Alerts", alerts.get('total_alerts', 0))
    
    with col3:
        st.metric("System Status", "✅ Online")
    
    st.divider()
    
    tab1, tab2, tab3 = st.tabs(["👥 Active Sessions", "⚠️ Anomaly Alerts", "📊 Analytics"])
    
    with tab1:
        st.subheader("Active User Sessions")
        if active_sessions.get('sessions'):
            df_sessions = pd.DataFrame(active_sessions['sessions'])
            st.dataframe(df_sessions, use_container_width=True)
            
            st.subheader("Session Confidence Distribution")
            if not df_sessions.empty:
                fig = px.bar(df_sessions, x='user_id', y='current_confidence', title="User Confidence Scores")
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No active sessions")
    
    with tab2:
        st.subheader("Recent Anomaly Alerts")
        if alerts.get('alerts'):
            df_alerts = pd.DataFrame(alerts['alerts'])
            st.dataframe(df_alerts, use_container_width=True)
            
            st.subheader("Alert Severity Distribution")
            severity_counts = df_alerts['severity'].value_counts()
            fig = px.pie(values=severity_counts.values, names=severity_counts.index, title="Alerts by Severity")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No active alerts")
    
    with tab3:
        st.subheader("System Analytics")
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Total Sessions", active_sessions.get('total_active', 0))
        
        with col2:
            st.metric("Total Alerts", alerts.get('total_alerts', 0))
        
        st.info("Dashboard updates in real-time. Refresh to see latest data.")

except requests.exceptions.ConnectionError:
    st.error("❌ Cannot connect to SentinelID Backend. Make sure it's running on http://127.0.0.1:5000")
except Exception as e:
    st.error(f"Error: {str(e)}")

st.divider()
st.caption("SentinelID Admin Dashboard | Real-time Behavioral Authentication Monitoring")
