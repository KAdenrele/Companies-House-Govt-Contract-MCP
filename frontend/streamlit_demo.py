import streamlit as st
import time
import random

# --- Page Configuration ---
# Set the page title and icon for the browser tab.
st.set_page_config(
    page_title="Gemini Chatbot",
    page_icon="🤖",
    layout="centered" # "centered" or "wide"
)

# --- App Title ---
# Display a main title and a subtitle for the app.
st.title("🤖 Gemini Chatbot Template")
st.caption("A simple Streamlit template to get you started.")


# --- Session State Initialization ---
# This is crucial for maintaining the chat history across reruns.
# 'messages' will be a list of dictionaries, e.g., [{"role": "user", "content": "Hello!"}]
if "messages" not in st.session_state:
    # Start with a welcome message from the assistant.
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello there! How can I help you today?"}
    ]


# --- Display Chat History ---
# Iterate through the existing messages in the session state and display them.
for message in st.session_state.messages:
    # Use st.chat_message to display messages in a chat-like format.
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# --- Placeholder for Gemini API Call ---
# Replace this function with your actual logic to call the Gemini API.
def get_gemini_response(user_query: str) -> str:
    """
    Simulates a call to the Gemini API.
    In a real application, this is where you would:
    1. Initialize your Gemini client.
    2. Send the user_query and chat history.
    3. Handle function calls if your model uses tools.
    4. Return the model's text response.
    """
    # For demonstration, we'll just echo the user's query with a delay.
    time.sleep(1) # Simulate network latency
    
    # Simple canned responses for the demo
    responses = [
        f"I received your message: '{user_query}'. I'm just a template, so I can't process this yet.",
        f"Thanks for asking about '{user_query}'. You'll need to connect me to the real Gemini API to get a proper answer!",
        f"Ah, '{user_query}' is an interesting topic. I look forward to discussing it once I'm fully configured."
    ]
    return random.choice(responses)


# --- Handle User Input ---
# st.chat_input creates a text input field at the bottom of the page.
# The 'if prompt := ...' syntax assigns the input to 'prompt' and checks if it's not empty.
if prompt := st.chat_input("What would you like to ask?"):
    
    # 1. Add the user's message to the session state.
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # 2. Display the user's message in the chat.
    with st.chat_message("user"):
        st.markdown(prompt)
        
    # 3. Get and display the assistant's response.
    with st.chat_message("assistant"):
        # Use a "thinking" placeholder while waiting for the response.
        with st.spinner("Thinking..."):
            response = get_gemini_response(prompt)
        
        # Display the response from the model.
        st.markdown(response)

    # 4. Add the assistant's response to the session state.
    st.session_state.messages.append({"role": "assistant", "content": response})

# --- To Run This App ---
# 1. Save the code as a Python file (e.g., `app.py`).
# 2. Make sure you have streamlit installed: `pip install streamlit`
# 3. Run from your terminal: `streamlit run app.py`
