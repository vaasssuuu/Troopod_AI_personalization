# ⚡ Dynamic Landing Page Personalizer (AI PM Assignment)

**Candidate:** Vatsalya Soni
**Role:** AI Product Manager Intern - Troopod

🔗 **Live Demo:** [Troopod AI Personalization App](https://troopodaipersonalization.streamlit.app/)
## 📖 Overview
This repository contains a functional prototype for a dynamic landing page personalization engine. The product goal is to solve the conversion drop-off that occurs when highly targeted ad creatives drive traffic to generic, unpersonalized landing pages. 

By utilizing a sequential multi-agent AI pipeline, this system ingests an ad creative and a target URL, synthesizes the core marketing strategy, and dynamically re-renders the landing page copy to match the ad's hook—without breaking the underlying UI.

## 🏗️ System Architecture & Logic
Rather than relying on a single LLM call, the system utilizes a **Decoupled Multi-Agent Pipeline** powered by Groq's high-speed inference engine to ensure low latency and high reliability.

1. **DOM Scraper:** Uses `BeautifulSoup` to extract factual text nodes from the target URL, stripping out visual noise.
2. **Agent 1 (Vision/Strategy):** Uses `meta-llama/llama-4-scout-17b-16e-instruct` to act as a Growth Marketer. It analyzes the ad image to identify the Core Value Proposition, Target Audience, and outputs a strategic "Personalization Directive."
3. **Agent 2 (Execution):** Uses `llama-3.3-70b-versatile` to rewrite the DOM facts based on Agent 1's directive. It is strictly constrained to output a structured JSON payload mapped to specific UI nodes.
4. **Rendering Client:** The Streamlit frontend maps the JSON payload to isolated UI containers, simulating a real-world frontend framework.

## 🛡️ Risk Mitigation & Edge Case Handling
This system was architected with strict product guardrails to handle the inherent non-determinism of generative AI:

* **Preventing "Broken UI" & Random Layout Changes:** The AI is physically walled off from manipulating HTML/CSS. By forcing a strict JSON schema output, the AI acts purely as a content API. The frontend safely maps these JSON values to rigid containers using `.get()` fallbacks.
* **Neutralizing Hallucinations:** The copywriter agent is explicitly sandboxed to synthesize features *only* from the scraped BeautifulSoup text. Furthermore, a strict prompt guardrail prohibits the modification of pricing or compliance claims.
* **Inconsistent Output Resilience:** If the LLM generates a malformed JSON string, the application catches the `JSONDecodeError` and automatically triggers a recursive retry loop. If it fails twice, it triggers a Graceful Degradation state, serving a safe default wireframe.

## 💻 Local Setup Instructions
If you wish to run this application locally:

1. Clone this repository.
2. Create a virtual environment and run `pip install -r requirements.txt`.
3. Create a `.env` file in the root directory and add your Groq API key: `GROQ_API_KEY="your_key_here"`
4. Run the application: `streamlit run app.py`

## 🚀 Future Roadmap
A production-grade iteration of this MVP would replace the live DOM scraper with a Retrieval-Augmented Generation (RAG) pipeline connected to a Headless CMS. This would act as a single source of truth for approved brand messaging, entirely eliminating structural hallucinations and enabling real-time compliance checks.
