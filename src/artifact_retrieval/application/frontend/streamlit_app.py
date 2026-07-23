from dns import query
import requests
import streamlit as st
from artifact_retrieval.application.backend.api.schemas.basic_schemas import ChatRequest, ChatResponse
import pandas as pd
import numpy as np

FASTAPI_URL = "http://localhost:8000"
START_URL = f"{FASTAPI_URL}/home"
CHAT_URL = f"{FASTAPI_URL}/chat"

st.set_page_config(page_title="AI-Assistant", page_icon=":robot_face:")

if "clicked" not in st.session_state:
    st.session_state.clicked = False

def start_chat():
    st.session_state.clicked = True

def send_message(query: str):
    try:
        query_model = ChatRequest(content=query)
        http_response = requests.post(CHAT_URL, json=query_model.model_dump(), timeout=30) # http transport object
        http_response.raise_for_status()
        response = ChatResponse.model_validate(http_response.json()) # model object of application, validates against expected schema
        return response.content
    except Exception as e:
        st.error(f"Could not reach backend: {e}")
        return e
    

if not st.session_state.clicked:
    st.title("Retrieval of Test Artifacts using a Chatbot")
    st.button("Start Chat!", on_click=start_chat)
else:
    st.title("AI Assistant — Chat")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


    query = st.chat_input("How can I assist you?")
    if query:
        st.session_state.messages.append({"role": "user", "content": query})
        with st.chat_message("user"):
            st.markdown(query)


        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = send_message(query)
                if isinstance(response, Exception) or response is None:
                    st.error(f"Backend error: {response}")
                    response_text = str(response)
                else:
                    response_text = response
                st.markdown(response_text)

        st.session_state.messages.append({"role": "assistant", "content": response_text})
            