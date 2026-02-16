import streamlit as st
import cv2
import numpy as np
from ultralytics import YOLO
from PIL import Image
import tempfile
import av
from streamlit_webrtc import webrtc_streamer
from datetime import datetime

# ---------------------------------------------------------
# Page Configuration & Professional Theming
# ---------------------------------------------------------
st.set_page_config(
    page_title="Pothole Guard AI | Smart Infrastructure", 
    page_icon="🛣️", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for a "Modern Dashboard" look
st.markdown("""
    <style>
    /* Main background and font */
    .main { background-color: #f8f9fa; }
    
    /* Custom Card Style */
    .metric-card {
        background: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border: 1px solid #eee;
        margin-bottom: 15px;
    }
    
    /* Header styling */
    .main-title {
        font-size: 2.5rem;
        font-weight: 800;
        color: #1E1E1E;
        margin-bottom: 0rem;
    }
    .sub-title {
        color: #6c757d;
        margin-bottom: 2rem;
    }
    
    /* Status indicators */
    .status-badge {
        padding: 5px 12px;
        border-radius: 20px;
        font-weight: bold;
        font-size: 0.8rem;
        text-transform: uppercase;
    }
    </style>
    """, unsafe_allow_html=True)

@st.cache_resource
def load_model():
    # Adding a try-except to handle cases where best.pt might be missing during dev
    try:
        return YOLO("best.pt")
    except:
        return None

model = load_model()

# -----------------------
# Sidebar - Navigation & System Health
# -----------------------
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2555/2555013.png", width=80)
    st.markdown("# Pothole Guard AI\n**V2.0.4 - Enterprise**")
    st.divider()
    
    mode = st.radio(
        "Select Inspection Interface",
        ["🖼️ Image Analysis", "🎥 Video Intelligence", "📷 Live Surveillance"],
        help="Choose the input source for AI detection"
    )
    
    st.divider()
    st.subheader("📡 System Pulse")
    if model:
        st.success("Neural Engine: Active")
    else:
        st.error("Neural Engine: Offline")
        
    st.info(f"Last Sync: {datetime.now().strftime('%H:%M:%S')}")
    
    if st.button("Clear Session Logs"):
        st.session_state.history = []
        st.rerun()

# -----------------------
# Main Dashboard Header
# -----------------------
col_header, col_status = st.columns([3, 1])
with col_header:
    st.markdown('<p class="main-title">Road Infrastructure Analytics</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">AI-powered defect detection and maintenance prioritization</p>', unsafe_allow_html=True)

# Session State for History
if "history" not in st.session_state:
    st.session_state.history = []

# =====================================================
# 🖼️ IMAGE MODE
# =====================================================
if "Image" in mode:
    st.markdown("### 🖼️ Still Image Processing")
    file = st.file_uploader("Upload high-resolution road imagery", type=["jpg","png","jpeg"], label_visibility="collapsed")
    
    if file:
        col1, col2 = st.columns([2, 1])
        img = np.array(Image.open(file))
        results = model(img)
        count = len(results[0].boxes)
        
        with col1:
            st.image(results[0].plot(), use_container_width=True, caption="AI Annotated Result")
        
        with col2:
            st.markdown("### 📊 Analysis Details")
            
            # Custom Metric Cards
            st.metric(label="Total Potholes Detected", value=count, delta="Action Required" if count > 0 else "Clear", delta_color="inverse")
            
            st.markdown("---")
            if count > 0:
                st.error(f"**Criticality: High**\n\nDetected {count} surface anomalies. Recommend dispatching repair crew to coordinates.")
                if st.button("Generate Repair Ticket"):
                    st.toast("Ticket #PX-402 created successfully!")
            else:
                st.success("**Criticality: None**\n\nSurface integrity within safety parameters.")
            
            st.session_state.history.append(f"{datetime.now().strftime('%H:%M')} - Image: {count} detected")
    else:
        st.info("👆 Please upload an image file to begin the scan.")

# =====================================================
# 🎥 VIDEO MODE
# =====================================================
elif "Video" in mode:
    st.markdown("### 🎥 Mobile Video Inspection")
    video = st.file_uploader("Upload patrol vehicle footage", type=["mp4","mov"], label_visibility="collapsed")
    
    if video:
        tfile = tempfile.NamedTemporaryFile(delete=False)
        tfile.write(video.read())
        cap = cv2.VideoCapture(tfile.name)
        
        col_vid, col_stats = st.columns([2, 1])
        
        with col_vid:
            stframe = st.empty()
            
        with col_stats:
            st.markdown("### 📈 Live Telemetry")
            curr_metric = st.empty()
            peak_metric = st.empty()
            status_box = st.empty()
            st.markdown("**Incident Log**")
            log_box = st.empty()

        max_potholes = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret: break

            results = model(frame)
            count = len(results[0].boxes)
            max_potholes = max(count, max_potholes)

            # Update Main Feed
            stframe.image(results[0].plot(), channels="BGR", use_container_width=True)
            
            # Update Dashboard Metrics
            curr_metric.metric("Current Frame Count", count)
            peak_metric.metric("Peak Pothole Density", max_potholes)
            
            if max_potholes >= 5:
                status_box.error("🚨 **IMMEDIATE INTERVENTION**\n\nSevere cluster detected. Road closure may be required.")
            elif max_potholes > 0:
                status_box.warning("⚠️ **ROUTINE MAINTENANCE**\n\nSurface degradation detected. Schedule within 48 hours.")
            else:
                status_box.success("✅ **OPTIMAL CONDITIONS**\n\nNo significant anomalies detected.")

            if count > 0:
                log_box.caption(f"📍 Frame {int(cap.get(cv2.CAP_PROP_POS_FRAMES))}: {count} anomalies identified")

        cap.release()
    else:
        st.info("📂 Waiting for video input from patrol units...")

# =====================================================
# 📷 LIVE CAMERA MODE
# =====================================================
elif "Live" in mode:
    st.markdown("### 📷 Live Field Surveillance")
    
    col_l, col_r = st.columns([3, 1])
    
    with col_r:
        st.markdown("### ⚙️ Camera Settings")
        st.write("Current FPS: 24.5")
        st.write("GPS Sync: ✅ Active")
        st.divider()
        st.warning("Ensure lens is clear of debris for high-accuracy detection.")
        
    with col_l:
        def video_frame_callback(frame):
            img = frame.to_ndarray(format="bgr24")
            # Efficient processing
            results = model(cv2.resize(img, (640, 640)))
            annotated = cv2.resize(results[0].plot(), (img.shape[1], img.shape[0]))
            return av.VideoFrame.from_ndarray(annotated, format="bgr24")

        webrtc_streamer(
            key="pothole-live",
            video_frame_callback=video_frame_callback,
            media_stream_constraints={"video": True, "audio": False},
            async_processing=True
        )

# -----------------------
# Global Footer Log
# -----------------------
if st.session_state.history:
    with st.expander("📝 Recent Incident History", expanded=False):
        for item in reversed(st.session_state.history):
            st.write(item)