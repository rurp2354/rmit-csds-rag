import streamlit as st
import requests
import os
from streamlit.components.v1 import html as st_html
import base64
from streamlit import session_state as ss

# --- Page Config ---
st.set_page_config(
    page_title="RMIT CSDS RAG Chatbot",
    page_icon="📘",
    layout="centered"
)

# --- Custom CSS ---
st.markdown("""
    <style>
        /* Background */
        .stApp {
            background-color: #ffffff;
        }
        /* Card container */

        /* Title */
        .rmit-title {
            display: flex; 
            align-items: center; 
            justify-content: center; 
            gap: 15px;
            color: #070758;
            text-align: center;
            font-size: 2.2em;
            font-weight: bold;
            font-family: "Sans Forgetica";
            background-color: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            width: 90%;
            margin: auto;
        }
        .rmit-title img {
            width: 200px;              
            display: inline-block;
        }
        /* Subtitle */
        .rmit-subheader {
            color: #E60028;
            font-size: 1.2em;
            margin-top: 25px;
            margin-bottom: 10px;
            font-weight: bold;
        }
        /* Buttons */
        div.stButton > button {
            background-color: #E60028;
            color: white;
            border-radius: 8px;
            padding: 0.6em 1.2em;
            border: none;
            font-weight: bold;
        }
        div.stButton > button:hover {
            background-color: #b81a23;
        }
        /* Chat bubbles */
        .answer-bubble {
            background-color: #ffffff;
            color: #070758;
            padding: 15px;
            border-radius: 12px;
            margin-top: 10px;
            font-size: 16px;
            line-height: 1.6;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            font-weight: bold;
        }

        .source-card {
            color: #006400;  /* Dark green */
            font-weight: bold;
            font-size: 15px;
            margin-top: 8px;
            padding: 15px;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }
        /* File uploader container */
        div.stFileUploader {
            background-color: #ffffff;   
            padding: 15px;               /* inner spacing */
            border-radius: 12px;         /* rounded corners */
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            text-align: center;          /* center content */
            max-width: 800px;
            margin: auto;
            color: #070758;
        }

         
        /* Browse button */
        div.stFileUploader button {
            background-color: #E60028;
            color: white !important;
            border-radius: 8px;
            padding: 0.5em 1em;
            border: none;
            font-weight: bold;
        }

        div.stFileUploader button:hover {
            background-color: #b81a23;
        }
            
        div.stFileUploader *{
            background-color: #ffffff;
            color: #070758;
        }
            
        div.stFileUploader [data-testid="stFileUploaderDeleteBtn"] {
            display: none;
        }

        [data-testid="stTextInput"] {
            height: 120px;
            padding: 15px;               /* inner spacing */
            border-radius: 12px;         /* rounded corners */
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            text-align: center;          /* center content */
            max-width: 800px;
            margin: auto;
        }
            
        [data-testid="stTextInput"] input[type="text"] {
            background-color: #ffffff;
            color: #070758;
            border-radius: 12px;
            padding: 15px;
        }
  
    </style>
""", unsafe_allow_html=True)



# --- Main Card Layout ---
with st.container():

    # Logo & Title

    with open("rmitlogo.png", "rb") as f:
        img_bytes = f.read()
        img_base64 = base64.b64encode(img_bytes).decode()

        # Use base64 in HTML
        st.markdown(f"""
        <div class="rmit-title">
            <img src="data:image/png;base64,{img_base64}"/>
            <span>| Course Chatbot</span>
        </div>
        """, unsafe_allow_html=True)


    # --- Query Section ---
    st.markdown('<div class="rmit-subheader">Ask a Question</div>', unsafe_allow_html=True)

    # Initialize session state
    if "query" not in st.session_state:
        st.session_state.query = ""
    if "answer_data" not in st.session_state:
        st.session_state.answer_data = None

    # Function to execute the query
    def execute_query():
        query = st.session_state.query
        if not query:
            return
        try:
            response = requests.post(
                "http://localhost:8000/query",
                json={"query": query}
            )
            if response.status_code == 200:
                st.session_state.answer_data = response.json()
            else:
                st.session_state.answer_data = {"error": f"Error: {response.status_code}"}
        except Exception as e:
            st.session_state.answer_data = {"error": f"Request failed: {e}"}

    # Input box with Enter key trigger
    st.text_input(
        "",
        key="query",
        on_change=execute_query
    )

    # Optional Search button
    if st.button("Search") and st.session_state.query:
        execute_query()

    # --- Display the answer in the proper location ---
    if st.session_state.answer_data:
        data = st.session_state.answer_data
        if "error" in data:
            st.error(data["error"])
        else:
            st.markdown('<div class="rmit-subheader">Answer</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="answer-bubble">{data["answer"]}</div>', unsafe_allow_html=True)

            st.markdown('<div class="rmit-subheader">Sources</div>', unsafe_allow_html=True)
            for s in data["sources"]:
                st.markdown(
                    f'<div class="source-card">📄 <b>{s["file"]}</b> (page {s["page"]})</div>',
                    unsafe_allow_html=True
                )



# --- File Upload Section ---
# Base directory
    st.markdown('<div class="rmit-subheader">Upload Files</div>', unsafe_allow_html=True)
    if "file_uploader_key" not in st.session_state:
        st.session_state["file_uploader_key"] = 0

    if "uploaded_files" not in st.session_state:
        st.session_state["uploaded_files"] = []
    uploaded_files = st.file_uploader("", type=["pdf", "docx", "txt"], accept_multiple_files=True, key = st.session_state["file_uploader_key"])

    if uploaded_files:
        st.session_state["uploaded_files"] = uploaded_files
        BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
        os.makedirs(BASE_DIR, exist_ok=True)

        if uploaded_files:
            for uploaded_file in uploaded_files:
                file_path = os.path.join(BASE_DIR, uploaded_file.name)
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())

    if st.button("Clear uploaded files"):
        st.session_state["file_uploader_key"] += 1
        file_path = os.path.join(BASE_DIR, uploaded_file.name)
        if os.path.exists(file_path):
                os.remove(file_path)
        st.rerun()

      

    # Use absolute path
    # Always resolve to <project_root>/rmit-csds-rag/data
    

    st.markdown('</div>', unsafe_allow_html=True)  # close card