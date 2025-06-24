import streamlit as st
from tools import mygemini
import asyncio
import logging

st.set_page_config(
    page_title="Gemini Chatbot",
    page_icon="🙈",
    layout="wide"
)

st.title("🙈 Gemini Chatbot linked to an MCP Server")
st.caption("A Streamlit front-end for your Gemini and MCP application.")


logger = logging.getLogger(__name__)

# --- Session State Initialization ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! How can I assist you today?"}
    ]
# Initialize the Gemini chat session once and store it in the session state.
if "chat_session" not in st.session_state:
    logger.info("Starting new Gemini chat session.")
    st.session_state.chat_session = mygemini.create_gemini_model().start_chat()


# --- Display Chat History ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# This is the async function that will do the work
async def get_response_async(prompt):
    chat_session = st.session_state.chat_session
    gemini_response = chat_session.send_message(prompt)
    final_text = await mygemini.handle_gemini_response_async(chat_session, gemini_response)
    return final_text


# --- Handle User Input ---
if prompt := st.chat_input("What would you like to ask?"):
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
        
    # Get and display the assistant's response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            
            try:
                # Get the current event loop for the main thread
                loop = asyncio.get_running_loop()
            except RuntimeError:
                # If there is no running loop, create a new one
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

            # Run async function using the existing or new loop
            response = loop.run_until_complete(get_response_async(prompt))

        st.markdown(response)

    # Add the assistant's response to history
    st.session_state.messages.append({"role": "assistant", "content": response})