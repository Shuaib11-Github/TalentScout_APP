import streamlit as st
import asyncio
from chatbot import CandidateChatbot
from googletrans import Translator

# Optional custom CSS for styling the app
st.markdown(
    """
    <style>
    .chat-title {
        text-align: center;
        font-size: 2.5em;
        color: #ffffff;
        margin-bottom: 10px;
    }
    .chat-subtitle {
        text-align: center;
        font-size: 1.2em;
        color: #e0e0e0;
        margin-bottom: 30px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Initialize session state variables if they don't exist already.
if "chatbot" not in st.session_state:
    st.session_state["chatbot"] = CandidateChatbot()
    st.session_state["messages"] = []
    st.session_state["language_selected"] = False
    st.session_state["selected_language"] = "en"
    st.session_state["translator"] = Translator(service_urls=['translate.google.com'])

# Display the main title of the chat application with a custom style.
st.markdown("<div class='chat-title'>🎓 Candidate Screening Chatbot</div>", unsafe_allow_html=True)

# Display a subtitle or welcome text (optional).
st.markdown(
    "<div class='chat-subtitle'>Welcome! Let's get started with your screening process. "
    "Feel free to ask any questions.</div>",
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# Language Selection Phase
# -----------------------------------------------------------------------------
if not st.session_state["language_selected"]:
    # Prompt user to select a language
    st.markdown(
        "<div style='background-color: #ede7f6; color: #4527a0; padding: 15px; "
        "border-radius: 10px; font-size: 1.1em; font-weight: bold; margin-bottom: 20px; "
        "text-align: center;'>Please select your preferred language (default is English). "
        "For example, type 'en' for English, 'es' for Spanish, etc.:</div>",
        unsafe_allow_html=True,
    )

    # Use Streamlit's chat_input to capture the user’s language code
    if user_input := st.chat_input("Type your language code here...", key="language_input"):
        # If user input is empty, default to 'en'; otherwise use the input language code
        st.session_state["selected_language"] = user_input if user_input else "en"
        st.session_state["language_selected"] = True

        # Provide an initial greeting to the user
        greeting = "Hello! Welcome to the Candidate Screening Chatbot. Let's start with your name."

        # If the user has selected a non-English language, translate the greeting
        if st.session_state["selected_language"] != "en":
            greeting = st.session_state["translator"].translate(
                greeting, dest=st.session_state["selected_language"]
            ).text

        # Display the greeting in the chat
        st.session_state["messages"].append({"role": "assistant", "content": greeting})
        with st.chat_message("assistant"):
            st.write(greeting)

        # Pass the user input (the language code) to the chatbot for further processing
        response = asyncio.run(st.session_state["chatbot"].handle_input(user_input))

        # Translate the chatbot's response if a non-English language is selected
        if st.session_state["selected_language"] != "en":
            response = st.session_state["translator"].translate(
                response, dest=st.session_state["selected_language"]
            ).text

        # Display the chatbot's response
        st.session_state["messages"].append({"role": "assistant", "content": response})
        with st.chat_message("assistant"):
            st.write(response)

        # Force the script to rerun so we skip the language selection prompt next time
        st.rerun()

# -----------------------------------------------------------------------------
# Main Chat Flow Phase
# -----------------------------------------------------------------------------
else:
    # Display all previous messages (both user and assistant) in the chat
    for message in st.session_state["messages"]:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # Capture new user input using chat_input
    if user_input := st.chat_input("Type your response here..."):
        # Display the user's message
        st.session_state["messages"].append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)

        # Process the user's input using the CandidateChatbot
        response = asyncio.run(st.session_state["chatbot"].handle_input(user_input))

        # If the user selected a different language, translate the chatbot's response
        if st.session_state["selected_language"] != "en":
            response = st.session_state["translator"].translate(
                response, dest=st.session_state["selected_language"]
            ).text

        # Display the chatbot's response
        st.session_state["messages"].append({"role": "assistant", "content": response})
        with st.chat_message("assistant"):
            st.write(response)