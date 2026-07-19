import streamlit as st

st.set_page_config(
    page_title="Identity Echo Interface",
    page_icon="🚀",
    layout="centered"
)

# ---------------- CSS ---------------- #

st.markdown("""
<style>

.stApp{
    background:linear-gradient(135deg,#0f172a,#1e3a8a,#4338ca);
}

/* Title */

.title{
    text-align:center;
    font-size:50px;
    font-weight:800;
    color:white;
}

.subtitle{
    text-align:center;
    color:#dbeafe;
    font-size:18px;
    margin-bottom:30px;
}

/* Input labels */

label{
    color:white !important;
    font-weight:bold !important;
}

/* Inputs */

.stTextInput input{
    border-radius:12px;
    border:2px solid #60A5FA;
    background:white;
    color:black;
}

.stTextArea textarea{
    border-radius:12px;
    border:2px solid #60A5FA;
    background:white;
    color:black;
}

/* Button */

.stButton>button{
    width:100%;
    border-radius:12px;
    border:none;
    padding:14px;
    background:linear-gradient(90deg,#06B6D4,#2563EB);
    color:white;
    font-size:18px;
    font-weight:bold;
}

.stButton>button:hover{
    background:linear-gradient(90deg,#0891B2,#1D4ED8);
}

</style>
""", unsafe_allow_html=True)

# ---------------- Header ---------------- #

st.markdown("<div class='title'>🚀 Identity Echo Interface</div>", unsafe_allow_html=True)

st.markdown("<div class='subtitle'>Securely transmit your identity and message.</div>", unsafe_allow_html=True)

# ---------------- Inputs ---------------- #

name = st.text_input("👤 Name")

message = st.text_area("💬 Message", height=170)

# ---------------- Button ---------------- #

if st.button("🚀 Transmit"):

    if name.strip() == "":
        st.error("Please provide your name.")

    elif message.strip() == "":
        st.warning("Please type a message to transmit.")

    else:

        st.success(
            f"Transmission successful! Greetings, {name}. We received your message: {message}"
        )

        chars = len(message)
        tokens = chars / 4

        st.info(
            f"🧠 System Check: Your message will consume approximately {tokens:.2f} tokens."
        )

        col1, col2 = st.columns(2)

        with col1:
            st.metric("Characters", chars)

        with col2:
            st.metric("Estimated Tokens", f"{tokens:.2f}")