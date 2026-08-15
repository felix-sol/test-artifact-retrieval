import requests
import streamlit as st
from artifact_retrieval.application.backend.api.schemas.basic_schemas import ChatRequest, ChatResponse, ChatHistory

FASTAPI_URL = "http://localhost:8000"
START_URL = f"{FASTAPI_URL}/home"
CHAT_URL = f"{FASTAPI_URL}/chat"

st.set_page_config(page_title="AI-Assistant", page_icon=":robot_face:")

if "clicked" not in st.session_state:
    st.session_state.clicked = False

if "messages" not in st.session_state:
        st.session_state.messages = []    

def start_chat():
    st.session_state.clicked = True

def send_message(query: str) -> tuple[str, list[dict]]:
    try:
        query_model = ChatRequest(content=query)
        http_response = requests.post(CHAT_URL, json=query_model.model_dump(), timeout=30) # http transport object
        http_response.raise_for_status()
        response = ChatResponse.model_validate(http_response.json()) # model object of application, validates against expected schema
        return response.content, response.sources
    except Exception as e:
        st.error(f"Could not reach backend: {e}")
        return str(e), []

def display_sources(sources: list[dict]) -> None:
    if not sources:
        return

    with st.expander(f"Sources ({len(sources)})"):
        for source in sources:
            filename = source.get("filename") or "Unknown file"
            repo_name = source.get("repo_name") or "Unknown repository"
            rel_path = source.get("rel_path") or "Unknown path"
            source_type = source.get("source_type") or "Unknown type"
            chunk_count = source.get("chunk_count", 0)
    
            st.markdown(
                f"**{filename}** \n"
                f"**Repository:** `{repo_name}`\n"
                f"**Path:** `{rel_path}`\n"
                f"**Type:** `{source_type}`\n"
                f"**Chunks used:** `{chunk_count}`"
            )
            
    
if not st.session_state.clicked:
    st.title("Retrieval of Test Artifacts using a Chatbot")
    st.button("Start Chat!", on_click=start_chat)
else:
    st.title("AI Assistant — Chat")

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

            if message["role"] == "assistant":
                display_sources(message.get("sources", []))

    query = st.chat_input("How can I assist you?")
    if query:
        st.session_state.messages.append({"role": "user", "content": query})
        with st.chat_message("user"):
            st.markdown(query)


        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response, sources = send_message(query)
                if isinstance(response, Exception) or response is None:
                    st.error(f"Backend error: {response}")
                    response_text = str(response)
                else:
                    response_text = response
                st.markdown(response_text)
                display_sources(sources)

        st.session_state.messages.append({"role": "assistant", "content": response_text, "sources": sources})

    chat_history = ChatHistory.model_validate(
            {"messages": st.session_state.messages}
        )   

    st.download_button(
            label="Download Chat",
            data=chat_history.model_dump_json(indent=2),
            file_name="chat_history.json",
            mime="application/json",
            disabled=not st.session_state.messages, 
        )
            