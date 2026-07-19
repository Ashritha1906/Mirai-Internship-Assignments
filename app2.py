import os
import random
from pathlib import Path
from dotenv import load_dotenv
import streamlit as st
from google import genai
from google.oauth2.credentials import Credentials as OAuthCredentials

# Set up the page before anything else
st.set_page_config(
    page_title="The Multiverse of Chatbots",
    page_icon="🌌",
    layout="centered"
)

# Custom styling to make the app look premium, beautiful and cosmic
st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@400;600;700;800&display=swap" rel="stylesheet">

<style>
/* CSS VARIABLES FOR UNIFIED COLOR SCHEME (Purples, indigos, cosmic blues) */
:root {
    --cosmic-bg-start: #090514;
    --cosmic-bg-mid: #120b29;
    --cosmic-bg-end: #080d26;
    --primary-g1: #8b5cf6;
    --primary-g2: #6366f1;
    --primary-g3: #3b82f6;
    --text-primary: #f1f1f1;
    --text-secondary: #a5b4fc;
    --glass-bg: rgba(255, 255, 255, 0.03);
    --glass-border: rgba(255, 255, 255, 0.08);
    --glass-border-glow: rgba(139, 92, 246, 0.2);
}

/* Background animated gradient */
@keyframes gradient-bg {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

.stApp {
    background: linear-gradient(-45deg, var(--cosmic-bg-start), var(--cosmic-bg-mid), var(--cosmic-bg-end), #03040c) !important;
    background-size: 400% 400% !important;
    animation: gradient-bg 15s ease infinite !important;
    color: var(--text-primary) !important;
    font-family: 'Inter', sans-serif !important;
}

/* Make headings use Outfit */
h1, h2, h3, h4, h5, h6 {
    font-family: 'Outfit', sans-serif !important;
    font-weight: 700 !important;
    color: #ffffff !important;
}

/* Sidebar glassmorphic container */
section[data-testid="stSidebar"] {
    background-color: rgba(9, 6, 20, 0.85) !important;
    border-right: 1px solid var(--glass-border-glow) !important;
    backdrop-filter: blur(12px) !important;
}

/* Custom styled character select and elements inside sidebar */
div[data-testid="stSidebarCollapseButton"] {
    color: white !important;
}

/* Sidebar selectbox and slider styling */
.stSelectbox, .stSlider {
    background: var(--glass-bg);
    border: 1px solid var(--glass-border);
    border-radius: 12px;
    padding: 12px;
    margin-bottom: 15px;
    transition: all 0.3s ease;
}
.stSelectbox:hover, .stSlider:hover {
    border-color: rgba(139, 92, 246, 0.4);
}

/* Glowing text for main Title */
.cosmic-title-container {
    text-align: center !important;
    margin-top: -20px !important;
    margin-bottom: 5px !important;
    display: flex !important;
    justify-content: center !important;
    align-items: center !important;
    gap: 12px !important;
}

.cosmic-emoji {
    font-size: 2.8rem !important;
    filter: drop-shadow(0 2px 10px rgba(168, 85, 247, 0.3)) !important;
}

.cosmic-title-text {
    font-family: 'Outfit', sans-serif !important;
    font-size: 2.8rem !important;
    font-weight: 800 !important;
    background: linear-gradient(45deg, #a855f7, #6366f1, #3b82f6) !important;
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    filter: drop-shadow(0 2px 10px rgba(168, 85, 247, 0.3)) !important;
    letter-spacing: -0.5px !important;
}

.cosmic-subtitle {
    font-family: 'Inter', sans-serif !important;
    font-size: 1.05rem !important;
    color: var(--text-secondary) !important;
    text-align: center !important;
    margin-bottom: 25px !important;
    font-weight: 400 !important;
}

/* Active Character Card in Main View */
.active-character-card {
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.03) 0%, rgba(255, 255, 255, 0.01) 100%);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-left: 4px solid #8b5cf6;
    border-radius: 16px;
    padding: 16px 20px;
    margin-bottom: 20px;
    display: flex;
    align-items: center;
    gap: 16px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
    backdrop-filter: blur(10px);
}

.character-avatar-large {
    font-size: 2.5rem;
    line-height: 1;
}

.character-details h3 {
    margin: 0 0 4px 0 !important;
    font-size: 1.3rem !important;
    color: #ffffff !important;
}

.character-details p {
    margin: 0 !important;
    color: var(--text-secondary) !important;
    font-size: 0.95rem !important;
}

/* Welcome Banner */
.welcome-banner {
    background: linear-gradient(90deg, rgba(139, 92, 246, 0.15) 0%, rgba(99, 102, 241, 0.15) 100%);
    border: 1px solid rgba(139, 92, 246, 0.25);
    border-radius: 12px;
    padding: 12px 20px;
    text-align: center;
    margin-bottom: 20px;
    font-size: 1.05rem;
    font-weight: 500;
    color: #e0e7ff;
    box-shadow: 0 4px 15px rgba(139, 92, 246, 0.05);
}

/* Chat bubble overrides */
div[data-testid="stChatMessage"] {
    border-radius: 16px !important;
    margin-bottom: 12px !important;
    padding: 14px 18px !important;
    transition: all 0.3s ease !important;
}

div[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"],
div[data-testid="stChatMessage"] p,
div[data-testid="stChatMessage"] span,
div[data-testid="stChatMessage"] li,
div[data-testid="stChatMessage"] code {
    color: var(--text-primary) !important;
}

div[data-testid="stChatMessage"]:has(.user-message-hook) {
    background: linear-gradient(135deg, rgba(99, 102, 241, 0.15) 0%, rgba(168, 85, 247, 0.15) 100%) !important;
    border: 1px solid rgba(168, 85, 247, 0.25) !important;
    box-shadow: 0 4px 15px rgba(168, 85, 247, 0.05) !important;
}

div[data-testid="stChatMessage"]:has(.assistant-message-hook) {
    background: rgba(255, 255, 255, 0.04) !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    backdrop-filter: blur(10px) !important;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1) !important;
}

/* Sleek Copy Response Button (expander styling) */
.stExpander {
    background: transparent !important;
    border: 1px solid rgba(255, 255, 255, 0.05) !important;
    border-radius: 10px !important;
    margin-top: 5px !important;
}

/* Buttons in general */
.stButton>button {
    background: linear-gradient(45deg, #8b5cf6, #6366f1) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 8px 20px !important;
    font-weight: 600 !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    width: 100% !important;
}

.stButton>button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 5px 15px rgba(139, 92, 246, 0.4) !important;
}

.stButton>button:active {
    transform: translateY(0px) !important;
}

/* Chat Input Styling */
div[data-testid="stChatInput"] {
    border-radius: 24px !important;
    border: 1px solid var(--glass-border-glow) !important;
    background-color: rgba(9, 6, 20, 0.75) !important;
    backdrop-filter: blur(12px) !important;
    padding: 6px !important;
    box-shadow: 0 -4px 20px rgba(0, 0, 0, 0.2) !important;
    transition: border-color 0.3s ease !important;
}

div[data-testid="stChatInput"],
div[data-testid="stChatInput"] * {
    color-scheme: dark !important;
}

div[data-testid="stChatInput"]:focus-within {
    border-color: rgba(139, 92, 246, 0.6) !important;
}

div[data-testid="stChatInput"] textarea {
    color: #f8fafc !important;
}

div[data-testid="stChatInput"] textarea,
div[data-testid="stChatInput"] input,
div[data-testid="stChatInput"] [contenteditable="true"] {
    color: #f8fafc !important;
    -webkit-text-fill-color: #f8fafc !important;
    caret-color: #f8fafc !important;
    background: rgba(15, 23, 42, 0.96) !important;
    border: 1px solid rgba(139, 92, 246, 0.22) !important;
    border-radius: 18px !important;
    box-shadow: inset 0 0 0 1000px rgba(15, 23, 42, 0.96) !important;
    opacity: 1 !important;
    -webkit-appearance: none !important;
    appearance: none !important;
}

div[data-testid="stChatInput"] textarea::placeholder,
div[data-testid="stChatInput"] input::placeholder,
div[data-testid="stChatInput"] [contenteditable="true"]::placeholder {
    color: rgba(248, 250, 252, 0.62) !important;
}

/* Scrollbar customization */
::-webkit-scrollbar {
    width: 8px;
    height: 8px;
}
::-webkit-scrollbar-track {
    background: rgba(0, 0, 0, 0.1);
}
::-webkit-scrollbar-thumb {
    background: rgba(139, 92, 246, 0.3);
    border-radius: 10px;
}
::-webkit-scrollbar-thumb:hover {
    background: rgba(139, 92, 246, 0.5);
}
</style>
""", unsafe_allow_html=True)

# Load the API key from the .env file or Streamlit secrets
load_dotenv(dotenv_path=Path(__file__).with_name(".env"))


def load_api_key():
    for key_name in ("GEMINI_API_KEY", "GOOGLE_API_KEY"):
        value = os.getenv(key_name)
        if value:
            return value.strip().strip('"').strip("'")

    try:
        for key_name in ("GEMINI_API_KEY", "GOOGLE_API_KEY"):
            value = st.secrets.get(key_name)
            if value:
                return str(value).strip().strip('"').strip("'")
    except Exception:
        pass

    return None


api_key = load_api_key()

if not api_key:
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
    except Exception:
        pass

if not api_key:
    st.error("🔑 **GEMINI_API_KEY not found!**")
    st.info("""
    To run this app on Streamlit Cloud, you need to configure your Google Gemini API Key in the Secrets manager:
    1. In the lower right of your Streamlit app, click **Manage app** (or go to your Streamlit dashboard).
    2. Click the three dots icon next to your app and select **Settings**.
    3. Go to **Secrets** and paste the following:
    ```toml
    GEMINI_API_KEY = "your_actual_api_key_here"
    ```
    4. Click **Save** and wait for the app to restart.
    """)
    st.stop()

def create_gemini_client(secret: str):
    cleaned_secret = secret.strip().strip('"').strip("'")

    if cleaned_secret.startswith("AIza"):
        return genai.Client(api_key=cleaned_secret)

    return genai.Client(credentials=OAuthCredentials(token=cleaned_secret))


# Create the Gemini client
client = create_gemini_client(api_key)

MODEL_CANDIDATES = [
    "gemini-2.5-flash-lite",
    "gemini-2.5-flash",
    "gemini-2.0-flash",
]


def generate_reply(prompt: str):
    last_error = None

    for model_name in MODEL_CANDIDATES:
        try:
            return client.models.generate_content(
                model=model_name,
                contents=prompt,
            )
        except Exception as exc:
            last_error = exc

    raise last_error

# Create chat history only once
if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar configuration
with st.sidebar:
    st.header("⚙️ Chat Settings")

    # Let the user choose who they want to chat with
    personality = st.selectbox(
        "Choose a Character",
        [
            "🛡 Captain America",
            "🧛 A Pookie Vampire",
            "🏏 Angry Ravi Shastri",
            "🤖 Jarvis",
            "⚡ Iron Man",
            "🕷 Spider-Man",
            "🃏 Joker",
            "🦇 Batman",
            "🧙 Harry Potter",
            "🧠 Sherlock Holmes",
            "🐼 Po",
            "🧙 Gandalf"
        ]
    )

    # Short descriptions for every character
    descriptions = {
        "🛡 Captain America": "Brave, disciplined and inspiring leader.",
        "🧛 A Pookie Vampire": "Cute, dramatic and hopeless romantic vampire.",
        "🏏 Angry Ravi Shastri": "Loud, energetic cricket commentator with high intensity.",
        "🤖 Jarvis": "Highly professional, intelligent AI assistant.",
        "⚡ Iron Man": "Sarcastic, witty, billionaire genius philanthropist.",
        "🕷 Spider-Man": "Funny, friendly, talkative neighborhood superhero.",
        "🃏 Joker": "Chaotic, mysterious, insane and highly unpredictable.",
        "🦇 Batman": "Serious, dark, logical protector and detective of Gotham.",
        "🧙 Harry Potter": "Kind-hearted, courageous young wizard.",
        "🧠 Sherlock Holmes": "Master detective utilizing brilliant logical deduction.",
        "🐼 Po": "Funny, enthusiastic kung-fu warrior panda.",
        "🧙 Gandalf": "Wise, deep and powerful guide wizard."
    }

    # Show a short description of the selected character
    st.info(descriptions.get(personality, ""))

    # Let the user decide how detailed the reply should be
    response_length = st.select_slider(
        "Response Length",
        options=["Short", "Medium", "Long"],
        value="Medium"
    )

    st.markdown("---")

    # Clear the conversation and start fresh
    if st.button("🗑 Clear Chat"):
        st.session_state.messages = []
        st.rerun()

# Extract character name and emoji
emoji = personality.split()[0]
char_name = " ".join(personality.split()[1:])

# Main page headings
st.markdown('<h1 class="cosmic-title-container"><span class="cosmic-emoji">🌌</span><span class="cosmic-title-text">THE MULTIVERSE OF CHATBOTS</span></h1>', unsafe_allow_html=True)
st.markdown('<p class="cosmic-subtitle">Step into another dimension and chat with your favorite characters</p>', unsafe_allow_html=True)

# Active Character Card in Main Area
st.markdown(f"""
<div class="active-character-card">
    <div class="character-avatar-large">{emoji}</div>
    <div class="character-details">
        <h3>{char_name}</h3>
        <p>{descriptions.get(personality, "")}</p>
    </div>
</div>
""", unsafe_allow_html=True)

# Display a welcome message if the conversation is empty
if len(st.session_state.messages) == 0:
    welcome = random.choice([
        f"🌟 Welcome! Click the input box below to start chatting with {char_name}.",
        f"🚀 Enter the portal and speak with {char_name}!",
        f"🌀 You are now connected to the universe of {char_name}!",
        f"🎭 {char_name} is waiting for you. Say hello!"
    ])
    st.markdown(f'<div class="welcome-banner">{welcome}</div>', unsafe_allow_html=True)

# Render the full chat history before waiting for the next prompt.
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input box
if prompt := st.chat_input("Say something..."):
    # Save and display the user's message immediately so it survives reruns.
    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt
        }
    )

    with st.chat_message("user"):
        st.markdown(prompt)

    # Combine all previous messages into one conversation
    conversation = ""
    for msg in st.session_state.messages:
        conversation += f"{msg['role']}: {msg['content']}\n"

    # Tell Gemini how it should behave
    ai_instructions = f"""
You are {personality}.

Rules:
- Stay completely in character.
- Never say you are an AI.
- Talk exactly like {personality}.
- Be engaging and entertaining.
- Use emojis whenever they fit naturally.
- Remember the previous conversation.
- Reply in {response_length.lower()} length.

Conversation:

{conversation}

User:
{prompt}
"""

    with st.chat_message("assistant"):

        # Show a typing animation while waiting for the reply
        with st.spinner(f"{char_name} is thinking..."):
            try:
                # Ask Gemini to generate a response
                response = generate_reply(ai_instructions)

                # Display and persist the assistant reply so the chat remains stateful.
                reply = response.text
                st.markdown(reply)
                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": reply
                    }
                )

                # Make it easy to copy the response
                with st.expander("📋 Copy Response"):
                    st.code(reply)

            # Show any errors if something goes wrong
            except Exception as e:
                st.error(f"Error: {e}")

# A simple footer for the app
st.markdown("---")
st.markdown(
    '<p style="text-align: center; color: var(--text-secondary); font-size: 0.85rem;">🌌 Made with ❤️ using Streamlit and Gemini</p>', 
    unsafe_allow_html=True
)