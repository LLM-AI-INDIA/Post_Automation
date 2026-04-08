import streamlit as st
import requests
import json
import time
import base64
import os

# ── Encode LinkedIn logo as base64 for embedding ───────────────────────
def get_logo_base64():
    logo_path = os.path.join(os.path.dirname(__file__), "Logo", "Linkedin.png")
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

LOGO_B64 = get_logo_base64()

# Set page config for a premium, clean look
st.set_page_config(
    page_title="LinkedIn Post Generator",
    page_icon="💼",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── Load External CSS ──────────────────────────────────────────────────
def load_css(file_name):
    if os.path.exists(file_name):
        with open(file_name, "r") as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

load_css("style.css")

# ── Header with LinkedIn Logo ───────────────────────────────────────────
logo_html = ""
if LOGO_B64:
    logo_html = f'<img src="data:image/png;base64,{LOGO_B64}" style="width:34px; height:34px; border-radius:6px; object-fit:contain; box-shadow: 0 2px 8px rgba(10,102,194,0.15);" />'
else:
    logo_html = '<span style="font-size:1.6rem;">💼</span>'

st.markdown(f"""
<div style="text-align:center; margin-bottom:2rem; animation: fadeUp 0.6s ease;">
  <div style="display:inline-flex; align-items:center; gap:0.6rem; margin-bottom:0.3rem;">
    {logo_html}
    <h1 style="margin:0; color:#1a1a2e; font-family:'Inter',sans-serif; font-weight:700; font-size:1.8rem;">
      Post Generator
    </h1>
  </div>
  <p style="color:#6b7280; font-size:0.95rem; font-family:'Inter',sans-serif; margin-top:0.3rem;">
    AI-powered LinkedIn content — create &amp; publish in one click
  </p>
</div>
""", unsafe_allow_html=True)

WEBHOOK_URL = 'https://yokesh01.app.n8n.cloud/webhook/e1e9a75e-172b-4b25-93ba-e1f27744a78c'

# ── Form Inputs ─────────────────────────────────────────────────────────
user_prompt = st.text_input("Topic *", placeholder="Enter the content topic")
post_type = st.selectbox("Post Type *", ["Select Post Type", "image", "article"])

article_data = ""
if post_type == "image":
    article_data = st.text_input("Image URL (Optional)", placeholder="https://example.com/image.png")
elif post_type == "article":
    article_data = st.text_input("Article URL (Optional)", placeholder="https://example.com/article")

def validate_inputs():
    if not user_prompt.strip():
        return False
    if post_type == "Select Post Type":
        return False
    return True

# ── Loading Step HTML Generator ─────────────────────────────────────────
def build_loading_html(active_step=0):
    steps_data = [
        ("⚡", "Connecting to n8n..."),
        ("🤖", "AI generating content..."),
        ("📝", "Formatting post..."),
        ("🚀", "Publishing to LinkedIn..."),
    ]
    status_messages = [
        "Connecting to n8n...",
        "AI is generating your content...",
        "Formatting your post...",
        "Publishing to LinkedIn...",
    ]
    steps_html = ""
    for i, (icon, label) in enumerate(steps_data):
        if i < active_step:
            cls = "wf-step done"
            icon_display = "✓"
        elif i == active_step:
            cls = "wf-step active"
            icon_display = icon
        else:
            cls = "wf-step"
            icon_display = icon
        steps_html += f'<div class="{cls}"><span class="wf-icon">{icon_display}</span><span>{label}</span></div>'

    status_text = status_messages[min(active_step, len(status_messages) - 1)]
    return f"""
<div class="loading-overlay">
  <div class="loading-container">
    <div class="orbs"><div class="orb"></div><div class="orb"></div><div class="orb"></div></div>
    <div class="loading-text">{status_text}</div>
    <div class="loading-progress-track"><div class="loading-progress-fill"></div></div>
    <div class="workflow-steps">{steps_html}</div>
    <div class="loading-sub">This may take a moment</div>
  </div>
</div>
"""

# ── Submit Button ───────────────────────────────────────────────────────
submitted = st.button("Generate & Publish", use_container_width=True)

if submitted:
    if not validate_inputs():
        st.error("Please fill out all required fields marked with *.")
    else:
        payload = {
            "user_prompt": user_prompt.strip(),
            "post_type": post_type.strip(),
            "article": article_data.strip()
        }

        # Show step-by-step loading overlay
        loader = st.empty()

        # Step 0: Connecting
        loader.markdown(build_loading_html(0), unsafe_allow_html=True)
        time.sleep(1)

        # Step 1: AI Generating (runs during actual API call)
        loader.markdown(build_loading_html(1), unsafe_allow_html=True)

        try:
            response = requests.post(WEBHOOK_URL, json=payload, headers={"Content-Type": "application/json"})

            # Step 2: Formatting
            loader.markdown(build_loading_html(2), unsafe_allow_html=True)
            time.sleep(0.8)

            # Step 3: Publishing
            loader.markdown(build_loading_html(3), unsafe_allow_html=True)
            time.sleep(0.6)

            # Clear overlay
            loader.empty()

            if not response.ok:
                if response.status_code == 524:
                    st.error("⌛ **N8N Connection Timeout**")
                    st.info("The workflow started but took too long to respond. Please check your n8n dashboard to see if the process finished correctly.")
                else:
                    st.error(f"⚠️ Server Error — Status {response.status_code}")
                
                with st.expander("Show Technical Details"):
                    st.code(response.text[:1000] + ("..." if len(response.text) > 1000 else ""), language="html")
            else:
                try:
                    data = response.json()
                    if isinstance(data, dict):
                        if data.get("success") is False or "error" in data:
                            st.error("❌ Workflow failed in n8n!")
                            st.json(data)
                        else:
                            st.success("✅ Published to LinkedIn successfully!")
                    else:
                        st.success("✅ Published to LinkedIn successfully!")
                except ValueError:
                    st.success("✅ Published to LinkedIn successfully!")

        except Exception as e:
            loader.empty()
            st.error("❌ An error occurred while connecting to the webhook.")
            st.error(str(e))
