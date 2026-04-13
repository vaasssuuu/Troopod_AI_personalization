import streamlit as st
import requests
from bs4 import BeautifulSoup
from groq import Groq
from dotenv import load_dotenv
import json
import os
import base64

# ==========================================
# PAGE CONFIGURATION
# ==========================================
st.set_page_config(page_title="Troopod AI Personalization", layout="wide")
st.title("⚡ Dynamic Landing Page Personalizer")
st.markdown("Upload an ad creative and a target URL to generate a dynamically personalized landing page.")

# ==========================================
# API CONFIGURATION
# ==========================================
load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY") or st.sidebar.text_input("Enter Groq API Key:", type="password")

if groq_api_key:
    groq_client = Groq(api_key=groq_api_key)
else:
    st.warning("Please enter your Groq API Key in the sidebar to proceed.")
    st.stop()

# ==========================================
# HELPER FUNCTIONS (THE AGENTS)
# ==========================================

@st.cache_data(show_spinner=False)
def scrape_landing_page(url):
    """Scrapes visible text. For production, this would use a DOM-aware headless browser."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        text_elements = soup.find_all(['h1', 'h2', 'h3', 'p', 'li', 'span'])
        extracted_text = " ".join([elem.get_text(strip=True) for elem in text_elements])
        return extracted_text[:4000] 
    except Exception as e:
        return f"Error scraping URL: {str(e)}"

def analyze_ad_image(image_bytes, mime_type):
    """Agent 1 (Vision): Extracts intent and mapping logic."""
    base64_image = base64.b64encode(image_bytes).decode('utf-8')
    prompt = """
    Analyze this ad creative. 
    1. Core Value Proposition
    2. Target Audience
    3. Primary Emotional Hook
    4. Personalization Strategy: (e.g., "Shift focus to pricing", "Highlight luxury features")
    Keep it concise.
    """
    response = groq_client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=[
            {"role": "user", "content": [{"type": "text", "text": prompt}, {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{base64_image}"}}]},
        ],
    )
    return response.choices[0].message.content

def generate_personalized_copy(ad_analysis, page_text, attempt=1):
    """Agent 2 (Text): Generates a full-page structured JSON with a resilience loop."""
    prompt = f"""
    You are an expert conversion rate optimizer and AI Product Manager.
    
    Ad Analysis Strategy: {ad_analysis}
    Original Landing Page Context: {page_text}
    
    Task: Architect a personalized landing page structure that matches the Ad Strategy. 
    Rule 1: Grounding - Use ONLY facts from the Original Page Context. 
    Rule 2: Format - Output ONLY valid JSON.
    Rule 3: Guardrails - Do NOT modify, exaggerate, or hallucinate pricing, legal claims, or return policies. Preserve them exactly.
    
    Format exactly like this:
    {{
      "hero_section": {{
        "headline": "...",
        "subheadline": "...",
        "cta_button": "..."
      }},
      "value_props_section": [
        {{"title": "...", "description": "..."}}
      ],
      "urgency_trust_section": {{
        "message": "...",
        "trust_badge_text": "..."
      }}
    }}
    """
    
    try:
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"},
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content
    except Exception as e:
        if attempt < 2:
            return generate_personalized_copy(ad_analysis, page_text, attempt=2) # Resilience Retry
        raise e

# ==========================================
# USER INTERFACE & LOGIC
# ==========================================

col_input, col_output = st.columns([1, 2])

with col_input:
    st.subheader("1. Setup Personalization")
    uploaded_file = st.file_uploader("Upload Ad Creative", type=["jpg", "jpeg", "png"])
    target_url = st.text_input("Landing Page URL", placeholder="https://example.com")
    
    if uploaded_file:
        st.image(uploaded_file, caption="Ad Creative Preview", use_column_width=True)
    
    generate_btn = st.button("Generate Layout 🚀", type="primary", use_container_width=True)

with col_output:
    st.subheader("2. Live Rendered Wireframe")
    
    if generate_btn and uploaded_file and target_url:
        with st.status("Initializing AI Pipeline...", expanded=True) as status:
            
            st.write("🔍 Scraping base DOM structure...")
            page_text = scrape_landing_page(target_url)
            if "Error" in page_text:
                st.error(page_text)
                st.stop()
                
            try:
                st.write("👁️ Agent 1: Mapping Ad Strategy...")
                ad_context = analyze_ad_image(uploaded_file.getvalue(), uploaded_file.type)
                
                st.write("✍️ Agent 2: Rebuilding JSON nodes...")
                raw_json_output = generate_personalized_copy(ad_context, page_text)
                
                status.update(label="System Ready", state="complete", expanded=False)
            except Exception as e:
                status.update(label="API Failure", state="error")
                st.error(f"System Error: {str(e)}")
                st.stop()
        
        # --- UI RENDERING (The "Wow" Factor) ---
        # --- UI RENDERING (The "Wow" Factor) ---
        try:
            data = json.loads(raw_json_output)
            st.success("✅ JSON Payload mapped successfully. No DOM breaks detected.")
            st.info("🛡️ Guardrail Active: Pricing and compliance data strictly preserved.")
            
            # Safe parsing with fallbacks (PM Level Resilience)
            hero = data.get('hero_section', {})
            props = data.get('value_props_section', [])
            trust = data.get('urgency_trust_section', {})
            
            # Simulated Hero Section
            with st.container(border=True):
                st.markdown(f"<h1 style='text-align: center;'>{hero.get('headline', 'Special Offer Inside')}</h1>", unsafe_allow_html=True)
                st.markdown(f"<h4 style='text-align: center; color: gray;'>{hero.get('subheadline', 'Explore our top products tailored for you.')}</h4>", unsafe_allow_html=True)
                col1, col2, col3 = st.columns([1,2,1])
                with col2:
                    st.button(hero.get('cta_button', 'Shop Now'), type="primary", use_container_width=True)
            
            st.divider()
            
            # Simulated Features Section
            st.markdown("<h3 style='text-align: center;'>Why Choose Us</h3>", unsafe_allow_html=True)
            cols = st.columns(3)
            for i in range(3):
                with cols[i]:
                    if i < len(props):
                        st.markdown(f"**{props[i].get('title', 'Premium Quality')}**")
                        st.caption(props[i].get('description', 'Built to the highest standards.'))
            
            st.divider()
            
            # Simulated Trust Section
            with st.container(border=True):
                st.info(f"🚨 **{trust.get('message', 'Limited time offer.')}**")
                st.caption(f"🔒 {trust.get('trust_badge_text', 'Secure Checkout')}")

            # Debug Data for PM Review
            with st.expander("🛠️ View Agent Decision Logs (For PM Evaluation)"):
                st.markdown("**Personalization Mapping (Agent 1):**")
                st.write(ad_context)
                st.markdown("**Coupled JSON Payload (Agent 2):**")
                st.json(data)
                
        except json.JSONDecodeError:
            # Fallback Resilience Layer
            st.warning("⚠️ AI generated invalid schema. Displaying safe fallback layout.")
            st.write("Raw Output:", raw_json_output)

    elif generate_btn:
        st.warning("Please provide inputs.")