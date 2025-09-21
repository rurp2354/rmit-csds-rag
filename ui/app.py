import streamlit as st
import requests

st.title("RMIT CSDS RAG Chatbot")

query = st.text_input("Enter your question:")

if st.button("Search") and query:
    try:
        response = requests.post(
            "http://localhost:8000/query",   # ✅ FIXED ENDPOINT
            json={"query": query}
        )
        if response.status_code == 200:
            data = response.json()
            st.subheader("Answer")
            st.write(data["answer"])

            st.subheader("Sources")
            for s in data["sources"]:
                st.markdown(f"- **{s['file']}** (page {s['page']})")
        else:
            st.error(f"Error: {response.status_code}")
    except Exception as e:
        st.error(f"Request failed: {e}")
