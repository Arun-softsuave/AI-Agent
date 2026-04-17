import streamlit as st
import requests
import uuid

# ---------------------------------------------------
# Page Config
# ---------------------------------------------------
st.set_page_config(
    page_title="AI Agent",
    page_icon="🤖",
    layout="centered"
)

st.title("🤖 AI Agent Chatbot")

# ---------------------------------------------------
# Session State
# ---------------------------------------------------
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []

# ---------------------------------------------------
# Show Chat History
# ---------------------------------------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# ---------------------------------------------------
# User Input
# ---------------------------------------------------
prompt = st.chat_input("Ask about sales data...")

if prompt:

    # Save User Message
    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt
        }
    )

    # Show User Message
    with st.chat_message("user"):
        st.write(prompt)

    # ---------------------------------------------------
    # Call Backend API
    # ---------------------------------------------------
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):

            try:
                response = requests.post(
                    "http://localhost:8000/chat",
                    json={
                        "thread_id": st.session_state.thread_id,
                        "message": prompt
                    },
                    timeout=300
                )

                # Check HTTP Status
                if response.status_code == 200:

                    try:
                        data = response.json()
                        answer = data.get(
                            "answer",
                            "No answer returned."
                        )

                    except Exception:
                        answer = (
                            "Backend returned invalid JSON:\n\n"
                            + response.text
                        )

                else:
                    answer = (
                        f"Backend Error {response.status_code}:\n\n"
                        + response.text
                    )

            except requests.exceptions.ConnectionError:
                answer = (
                    "Cannot connect to backend.\n\n"
                    "Make sure FastAPI server is running:\n"
                    "uvicorn backend.main:app --reload"
                )

            except requests.exceptions.Timeout:
                answer = (
                    "Request timed out. "
                    "Backend took too long to respond."
                )

            except Exception as e:
                answer = f"Unexpected Error: {str(e)}"

        # Show Assistant Reply
        st.write(answer)

    # Save Assistant Message
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer
        }
    )