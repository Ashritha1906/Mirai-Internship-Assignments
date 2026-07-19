import os
import random
import io
from urllib.parse import quote

import requests
import streamlit as st
from PIL import Image
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# -----------------------------
# Session state initialization
# -----------------------------
if "prompt_input" not in st.session_state:
    st.session_state.prompt_input = ""

if "current_image" not in st.session_state:
    st.session_state.current_image = None

if "current_image_bytes" not in st.session_state:
    st.session_state.current_image_bytes = None

if "current_prompt" not in st.session_state:
    st.session_state.current_prompt = ""

if "generated_style" not in st.session_state:
    st.session_state.generated_style = ""

if "generated_width" not in st.session_state:
    st.session_state.generated_width = 0

if "generated_height" not in st.session_state:
    st.session_state.generated_height = 0

if "generated_magic_enhance" not in st.session_state:
    st.session_state.generated_magic_enhance = False


# -----------------------------
# Helpers
# -----------------------------
def pil_to_png_bytes(img: Image.Image) -> bytes:
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()


def generate_image(prompt: str, width: int, height: int, art_style: str, magic_enhance: bool):
    full_prompt = f"{prompt}, {art_style} style"

    if magic_enhance:
        full_prompt += ", masterpiece, 8k resolution, highly detailed, trending on art station, unreal engine 5 render"

    encoded_prompt = quote(full_prompt)
    url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={width}&height={height}"

    try:
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            return Image.open(io.BytesIO(response.content))
        st.error(f"Error generating image: {response.status_code}")
        return None
    except Exception as e:
        st.error(f"Error generating image: {e}")
        return None


def enhance_user_prompt(user_prompt: str) -> str:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        st.error("GROQ_API_KEY not found. Please set it in your .env file.")
        return user_prompt

    try:
        client = OpenAI(
            api_key=api_key,
            base_url="https://api.groq.com/openai/v1",
        )

        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {
                    "role": "system",
                    "content": "You are a Creative Agent that enhances image prompts for AI generation. Return only the enhanced prompt within 20-25 words."
                },
                {
                    "role": "user",
                    "content": f"Enhance this prompt: '{user_prompt}'"
                }
            ],
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        st.error(f"Error enhancing prompt: {e}")
        return user_prompt


def handle_surprise():
    surprise_prompts = [
        "An astronaut riding a horse on Mars with a neon sunset",
        "A cyberpunk street food vendor in Tokyo with holographic signs",
        "A dragon made of galaxies flying through a nebula",
        "A steampunk city floating in the clouds with airships",
        "An underwater civilization with bio-luminescent buildings"
    ]
    st.session_state.prompt_input = random.choice(surprise_prompts)


def handle_enhance():
    prompt = st.session_state.prompt_input.strip()
    if prompt:
        st.session_state.prompt_input = enhance_user_prompt(prompt)


# -----------------------------
# UI
# -----------------------------
if not os.getenv("GROQ_API_KEY"):
    st.warning("GROQ_API_KEY not found in environment variables. Prompt enhancement will not work until you set it.")  # noqa

st.title("AI Image Studio")
st.markdown("Generate stunning AI images with custom settings!")

with st.sidebar:
    st.title("-- Configurations --")
    st.divider()

    art_style = st.selectbox(
        "Art-Style",
        ["Realistic", "Anime", "CyberPunk", "Fantasy", "Watercolor"]
    )

    width = st.slider("Width", min_value=256, max_value=1024, value=512, step=64)
    height = st.slider("Height", min_value=256, max_value=1024, value=512, step=64)

    magic_enhance = st.checkbox("Enable Magic Enhance")

    st.divider()
    st.caption("Made with 💖 using Pollinations.ai")

col1, col2 = st.columns([2, 1])

with col1:
    st.text_area(
        "Enter your image description:",
        placeholder="eg. Beautiful sunset over mountains",
        height=150,
        key="prompt_input"
    )

    st.button("Surprise Me!!", use_container_width=True, on_click=handle_surprise)
    st.button("Enhance your prompt", use_container_width=True, on_click=handle_enhance)
    generate = st.button("Generate Image", type="primary",  use_container_width=True)

with col2:
    st.subheader("PREVIEW")
    image_placeholder = st.empty()


# -----------------------------
# Generation logic
# -----------------------------
if generate:
    prompt = st.session_state.prompt_input.strip()

    if not prompt:
        st.warning("Please enter a prompt first.")
    else:
        with st.spinner("Creating your masterpiece..."):
            img = generate_image(prompt, width, height, art_style, magic_enhance)

            if img is not None:
                img_bytes = pil_to_png_bytes(img)

                st.session_state.current_image = img
                st.session_state.current_image_bytes = img_bytes
                st.session_state.current_prompt = prompt
                st.session_state.generated_style = art_style
                st.session_state.generated_width = width
                st.session_state.generated_height = height
                st.session_state.generated_magic_enhance = magic_enhance


# -----------------------------
# Persistent preview
# -----------------------------
if st.session_state.current_image is not None:
    image_placeholder.image(
        st.session_state.current_image,
        caption=st.session_state.current_prompt,
        use_container_width=True
    )


# -----------------------------
# Download + info
# -----------------------------
with col1:
    if st.session_state.current_image_bytes is not None:
        clean_style = st.session_state.generated_style.lower().replace(" ", "_")
        file_name = f"{clean_style}_image.png"

        st.download_button(
            label="Download Image",
            data=st.session_state.current_image_bytes,
            file_name=file_name,
            mime="image/png",
            type="secondary",
            use_container_width=True,
            on_click="ignore"
        )

        with st.expander("Image Info"):
            st.write(f"**Prompt:** {st.session_state.current_prompt}")
            st.write(f"**Style:** {st.session_state.generated_style}")
            st.write(f"**Dimensions:** {st.session_state.generated_width} x {st.session_state.generated_height}")
            st.write(
                f"**Magic Enhance:** {'Active' if st.session_state.generated_magic_enhance else 'Inactive'}"
            )
            st.write(f"**File name:** {file_name}")
    else:
        st.download_button(
            label="Download Image (Generate an image first)",
            data=b"",
            file_name="image.png",
            mime="image/png",
            type="secondary",
            use_container_width=True,
            disabled=True
        )

st.markdown(
    """
    <div style='text-align: center; color: #666; margin-top: 30px;'>
        <p>Built with 💖 using Streamlit & Pollinations.ai</p>
        <p style='font-size: 12px;'>MirAI School of Technology - AI Builder Track 2026</p>
    </div>
    """,
    unsafe_allow_html=True
)