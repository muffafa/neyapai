import streamlit as st
import requests
import os

# Constants
API_URL = "http://localhost:8000/llm/completions"

st.title("Antalya İli Öğretmen Analiz Asistanı")

# Sidebar with example questions
with st.sidebar:
    st.header("Örnek Sorular")
    st.markdown("""
    - En çok hangi branşta öğretmen ihtiyacı var?
    - Hangi ilçede en fazla norm fazlası öğretmen var?
    - Özel eğitim branşında kaç öğretmen ihtiyacı var?
    - Muratpaşa'da hangi branşlarda norm fazlası var?
    """)

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Sormak istediğiniz soruyu yazın..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get AI response
    with st.chat_message("assistant"):
        with st.spinner("Yanıt hazırlanıyor..."):
            try:
                response = requests.post(
                    API_URL,
                    json={"input": prompt}
                )
                response.raise_for_status()
                data = response.json()
                
                # Ana yanıtı göster
                st.markdown(data["output"])
                
                # Düşünme sürecini göster
                if data.get("thought_process"):
                    with st.expander("Düşünme Süreci 🤔"):
                        for step in data["thought_process"]:
                            st.markdown(f"### {step['step']}")
                            if step.get("thought"):
                                st.markdown(f"**Düşünce:** {step['thought']}")
                            if step.get("action"):
                                st.markdown(f"**İşlem:** ```python\n{step['action']}\n```")
                            if step.get("observation"):
                                st.markdown(f"**Sonuç:** {step['observation']}")
                            st.markdown("---")
                
                # Mesajı kaydet
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": data["output"],
                    "thought_process": data.get("thought_process", [])
                })
                
            except Exception as e:
                error_msg = f"Bir hata oluştu: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
