import os
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


@st.cache_resource
def get_assistant() -> PersonalAssistant:
    return PersonalAssistant(None)


st.set_page_config(page_title="MultiTask Assistant Dashboard", page_icon="🤖", layout="wide")

st.title("MultiTask Assistant Dashboard")
st.caption("Set credentials and test natural-language commands for Calendar, Email, and Research")

with st.sidebar:
    st.subheader("Status")
    credentials_exists = os.path.exists("credentials.json")
    token_exists = os.path.exists("token.json")
    groq_key_exists = bool(os.getenv("GROQ_API_KEY"))
    st.write(f"Google OAuth credentials.json: {'✅' if credentials_exists else '❌'}")
    st.write(f"Google OAuth token.json: {'✅' if token_exists else '❌'}")
    st.write(f"Groq API key: {'✅' if groq_key_exists else '❌'}")

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


st.subheader("1) Setup API Keys")
env_values = read_env_values()

with st.form("credentials_form"):
    groq_api_key = st.text_input(
        "GROQ_API_KEY",
        value=env_values.get("GROQ_API_KEY", ""),
        type="password",
        help="Required by current agents (model: groq/llama-3.3-70b-versatile)",
    )
    google_api_key = st.text_input(
        "GOOGLE_API_KEY",
        value=env_values.get("GOOGLE_API_KEY", ""),
        type="password",
        help="Used for Gemini via langchain-google-genai",
    )
    tavily_api_key = st.text_input(
        "TAVILY_API_KEY",
        value=env_values.get("TAVILY_API_KEY", ""),
        type="password",
        help="Used by web research tools",
    )
    save_keys = st.form_submit_button("Save Keys to .env")

if save_keys:
    try:
        if groq_api_key:
            save_env_value("GROQ_API_KEY", groq_api_key)
        if google_api_key:
            save_env_value("GOOGLE_API_KEY", google_api_key)
        if tavily_api_key:
            save_env_value("TAVILY_API_KEY", tavily_api_key)
        st.success("Credentials saved to .env")
    except Exception as exc:
        st.error(f"Could not save .env values: {exc}")


st.subheader("2) Google OAuth Files")
st.write("Place `credentials.json` in the project root. Then click validate to generate/refresh `token.json`.")

if not credentials_exists:
    st.warning("`credentials.json` is missing. Calendar and Gmail actions will fail until you add it.")


st.subheader("3) Test Assistant Command")
st.write("Example: Please set up my calendar meeting on 24th March at 4 PM with title Team Sync")

if "history" not in st.session_state:
    st.session_state["history"] = []

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
        elif not os.path.exists("credentials.json"):
            st.warning("⚠️ credentials.json is missing. Calendar/Email operations may fail.")
        else:
            with st.spinner("Running assistant..."):
                try:
                    assistant = get_assistant()
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
                    elif "credentials.json" in error_message.lower() or "token.json" in error_message.lower():
                        st.error(f"🔐 **Google OAuth Issue**: {error_message}\n\nEnsure credentials.json is present and click 'Validate Google' in the sidebar.")
                    else:
                        st.error(f"❌ **Execution failed**: {error_message}")


if st.session_state["history"]:
    st.subheader("Recent Tests")
    for item in reversed(st.session_state["history"][-5:]):
        with st.expander(item["command"]):
            st.write(item["response"])