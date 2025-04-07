import streamlit as st
import requests
import json

st.title("💬 Chatbot")
st.write(
    "This is a bhikhmanga using [Groq](https://console.groq.com/) to chat with high-performance models like **Mixtral** or **LLaMA 3**.\n\n"
)

groq_api_key = st.secrets.get("GROQ_API_KEY")

if not groq_api_key:
    st.error("Missing Groq API key. Please add it to .streamlit/secrets.toml.")
    st.stop()

model_catalog = {
    "🦙 LLaMA 3.3 70B (Versatile)": "llama-3.3-70b-versatile",
    "🦙 LLaMA 3.1 8B (Instant)": "llama-3.1-8b-instant",
    "🦙 LLaMA 3 70B": "llama3-70b-8192",
    "🦙 LLaMA 3 8B": "llama3-8b-8192",
    "🔸 Gemma 2 9B IT": "gemma2-9b-it",
    "🌠 Qwen QWQ 32B": "qwen-qwq-32b",
    "💡 DeepSeek (LLaMA 70B Distilled)": "deepseek-r1-distill-llama-70b",
    "🔧 Allam 2 7B": "allam-2-7b",
}

st.subheader("🧠 Model Selection")
friendly_model = st.selectbox("Choose a model:", list(model_catalog.keys()))
model = model_catalog[friendly_model]
st.caption(f"Model ID: `{model}`")

st.subheader("🎛️ Generation Settings")

temperature = st.slider("Temperature", 0.0, 1.5, 0.7, 0.05)
top_p = st.slider("Top-p (nucleus sampling)", 0.0, 1.0, 1.0, 0.05)
max_tokens = st.slider("Max tokens in response", 256, 8192, 1024, step=64)

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": "You are a helpful assistant."}]

for message in st.session_state.messages[1:]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What would you like to ask?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    headers = {
        "Authorization": f"Bearer {groq_api_key}",
        "Content-Type": "application/json"
    }
    payload = {
    "model": model,
    "messages": st.session_state.messages,
    "temperature": temperature,
    "top_p": top_p,
    "max_tokens": max_tokens,
    "stream": True
}

    assistant_response = ""
    with st.chat_message("assistant"):
        response_container = st.empty()
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json=payload,
            stream=True
        )

        for line in response.iter_lines():
            if line:
                if line.startswith(b"data: "):
                    line = line[6:]
                if line == b"[DONE]":
                    break
                try:
                    data = json.loads(line.decode("utf-8"))
                    delta = data["choices"][0]["delta"].get("content", "")
                    assistant_response += delta
                    response_container.markdown(assistant_response + "▌")
                except Exception as e:
                    continue
        response_container.markdown(assistant_response)

    st.session_state.messages.append({"role": "assistant", "content": assistant_response})
