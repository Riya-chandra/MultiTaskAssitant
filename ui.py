import os
from pathlib import Path
from dotenv import dotenv_values, load_dotenv, set_key
import streamlit as st

from src.agents.personal_assistant import PersonalAssistant
from src.utils import get_current_date_time, get_credentials


load_dotenv()


def get_env_path() -> str:
    return os.path.join(os.getcwd(), ".env")


def save_env_value(key: str, value: str) -> None:
    env_path = get_env_path()
    if not os.path.exists(env_path):
        with open(env_path, "w", encoding="utf-8"):
            pass
    set_key(env_path, key, value)
    os.environ[key] = value


def read_env_values() -> dict:
    env_path = get_env_path()
    if not os.path.exists(env_path):
        return {}
    return dotenv_values(env_path)


def create_assistant() -> PersonalAssistant:
    return PersonalAssistant(None)


def apply_session_env(key: str, value: str) -> None:
    if value:
        os.environ[key] = value.strip()


def save_uploaded_google_credentials(uploaded_file) -> str:
    session_id = st.session_state.get("session_id")
    if not session_id:
        session_id = str(abs(hash(str(st.session_state))))
        st.session_state["session_id"] = session_id

    session_dir = Path(".session_credentials") / session_id
    session_dir.mkdir(parents=True, exist_ok=True)

    credentials_file = session_dir / "credentials.json"
    token_file = session_dir / "token.json"

    credentials_file.write_bytes(uploaded_file.getvalue())

    os.environ["GOOGLE_OAUTH_CREDENTIALS_FILE"] = str(credentials_file)
    os.environ["GOOGLE_OAUTH_TOKEN_FILE"] = str(token_file)

    return str(credentials_file)


st.set_page_config(page_title="MultiTask Assistant Dashboard", page_icon="🤖", layout="wide")

st.title("MultiTask Assistant Dashboard")
st.caption("Users can add their own credentials and test commands instantly")

if "history" not in st.session_state:
    st.session_state["history"] = []

if "assistant" not in st.session_state:
    st.session_state["assistant"] = None

with st.sidebar:
    st.subheader("Status")
    active_credentials_file = os.getenv("GOOGLE_OAUTH_CREDENTIALS_FILE", "credentials.json")
    active_token_file = os.getenv("GOOGLE_OAUTH_TOKEN_FILE", "token.json")
    credentials_exists = os.path.exists(active_credentials_file)
    token_exists = os.path.exists(active_token_file)
    groq_key_exists = bool(os.getenv("GROQ_API_KEY"))
    tavily_key_exists = bool(os.getenv("TAVILY_API_KEY"))
    st.write(f"Google OAuth file: {'✅' if credentials_exists else '❌'}")
    st.write(f"Google token file: {'✅' if token_exists else '❌'}")
    st.write(f"Groq API key: {'✅' if groq_key_exists else '❌'}")
    st.write(f"Tavily API key: {'✅' if tavily_key_exists else '❌'}")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Validate Google"):
            try:
                get_credentials()
                st.success("Google OK")
            except Exception as exc:
                st.error(f"Google failed: {exc}")
    
    with col2:
        if st.button("Test Groq"):
            try:
                from langchain_groq import ChatGroq
                llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.1)
                llm.invoke("Hi")
                st.success("Groq OK")
            except Exception as exc:
                st.error(f"Groq failed: {exc}")


st.subheader("1) User Credentials (Test Right Now)")
env_values = read_env_values()

with st.form("session_credentials_form"):
    st.caption("These credentials are used for this session only (safe for demos/interviews).")
    groq_api_key = st.text_input(
        "Groq API Key",
        value="",
        type="password",
        help="Required for assistant reasoning",
        placeholder="gsk_...",
    )
    tavily_api_key = st.text_input(
        "Tavily API Key (optional, for research commands)",
        value="",
        type="password",
        placeholder="tvly-...",
    )
    google_api_key = st.text_input(
        "Google API Key (optional)",
        value="",
        type="password",
        placeholder="AIza...",
    )
    uploaded_google_oauth = st.file_uploader(
        "Upload Google OAuth credentials.json (for calendar/email)",
        type=["json"],
        accept_multiple_files=False,
    )
    apply_session = st.form_submit_button("Apply Session Credentials")

if apply_session:
    try:
        if groq_api_key:
            apply_session_env("GROQ_API_KEY", groq_api_key)
        if tavily_api_key:
            apply_session_env("TAVILY_API_KEY", tavily_api_key)
        if google_api_key:
            apply_session_env("GOOGLE_API_KEY", google_api_key)
        if uploaded_google_oauth:
            saved_path = save_uploaded_google_credentials(uploaded_google_oauth)
            st.success(f"Google OAuth file loaded for this session: {saved_path}")

        st.session_state["assistant"] = create_assistant()
        st.success("Session credentials applied. You can test commands now.")
    except Exception as exc:
        st.error(f"Could not apply credentials: {exc}")


with st.expander("Owner-only: Save default keys to .env"):
    st.caption("Use only for your own machine defaults. Not recommended for public demos.")
    with st.form("owner_credentials_form"):
        owner_groq = st.text_input("GROQ_API_KEY", value=env_values.get("GROQ_API_KEY", ""), type="password")
        owner_google = st.text_input("GOOGLE_API_KEY", value=env_values.get("GOOGLE_API_KEY", ""), type="password")
        owner_tavily = st.text_input("TAVILY_API_KEY", value=env_values.get("TAVILY_API_KEY", ""), type="password")
        save_defaults = st.form_submit_button("Save to .env")

    if save_defaults:
        try:
            if owner_groq:
                save_env_value("GROQ_API_KEY", owner_groq)
            if owner_google:
                save_env_value("GOOGLE_API_KEY", owner_google)
            if owner_tavily:
                save_env_value("TAVILY_API_KEY", owner_tavily)
            st.success("Default credentials saved to .env")
        except Exception as exc:
            st.error(f"Could not save .env values: {exc}")


st.subheader("2) Google OAuth Files")
st.write("Either upload OAuth credentials above, or place `credentials.json` in project root for default flow.")

if not credentials_exists:
    st.warning("Google OAuth credentials are missing for current session. Calendar and Gmail actions will fail.")


st.subheader("3) Test Assistant Command")
st.write("Example: Please set up my calendar meeting on 24th March at 4 PM with title Team Sync")
st.caption("Tip: write exact event name. The assistant will save the same name in calendar.")

command_text = st.text_area(
    "Enter your command",
    placeholder="Please set up my calendar meeting on 24th March at 4 PM with title Team Sync",
    height=120,
)

if st.button("Run Command", type="primary"):
    if not command_text.strip():
        st.warning("Please enter a command first.")
    else:
        if not os.getenv("GROQ_API_KEY"):
            st.error("⚠️ GROQ_API_KEY is not set. Please add it in the credentials section above and reload the page.")
        else:
            with st.spinner("Running assistant..."):
                try:
                    if st.session_state["assistant"] is None:
                        st.session_state["assistant"] = create_assistant()
                    assistant = st.session_state["assistant"]
                    message = (
                        f"Message: {command_text.strip()}\n"
                        f"Current Date/time: {get_current_date_time()}"
                    )
                    answer = assistant.invoke(message)
                    st.session_state["history"].append(
                        {
                            "command": command_text.strip(),
                            "response": answer,
                        }
                    )
                    st.success("Command executed")
                except Exception as exc:
                    error_message = str(exc)
                    if "401" in error_message or "invalid_api_key" in error_message.lower():
                        st.error("🔑 **Groq API Key Invalid**\n\nYour GROQ_API_KEY is either wrong, expired, or inactive. Get a valid key from https://console.groq.com/keys and update it in the credentials form above, then refresh this page.")
                    elif "deleted_client" in error_message.lower():
                        st.error("🔐 **Google OAuth Client Deleted**\n\nUpload a fresh OAuth `credentials.json` in section 1 (or replace root credentials.json), then validate again.")
                    elif "credentials.json" in error_message.lower() or "token.json" in error_message.lower():
                        st.error(f"🔐 **Google OAuth Issue**: {error_message}\n\nEnsure credentials.json is present and click 'Validate Google' in the sidebar.")
                    else:
                        st.error(f"❌ **Execution failed**: {error_message}")


if st.session_state["history"]:
    st.subheader("Recent Tests")
    for item in reversed(st.session_state["history"][-5:]):
        with st.expander(item["command"]):
            st.write(item["response"])