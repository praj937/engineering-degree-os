"""Save feedback to Supabase using a separate client for each browser session.""" 
import logging 
import streamlit as st 
from supabase import create_client 

logger = logging.getLogger(__name__) 

st.set_page_config(page_title="Supabase feedback", page_icon="📝") 
st.title("Feedback") 

# Read configuration from .streamlit/secrets.toml or the host's Secrets settings. 
try: 
    url = st.secrets["SUPABASE_URL"] 
    key = st.secrets["SUPABASE_PUBLISHABLE_KEY"] 
except (FileNotFoundError, KeyError): 
    st.error("Add the Supabase URL and publishable key to Streamlit Secrets.") 
    st.stop() 

# Auth changes the client. Do not share this client through a global cache. 
try: 
    if "_supabase" not in st.session_state: 
        st.session_state["_supabase"] = create_client(url, key) 
    db = st.session_state["_supabase"] 
    session = db.auth.get_session() 
except Exception: 
    logger.exception("Supabase connection or session failed") 
    st.error("Could not connect. Check your settings and Supabase project.") 
    st.stop() 

if session is None: 
    st.subheader("Sign in") 
    with st.form("sign_in", clear_on_submit=True): 
        email = st.text_input("Email") 
        password = st.text_input("Password", type="password") 
        sign_in = st.form_submit_button("Sign in") 
    if sign_in: 
        if not email.strip() or not password: 
            st.warning("Enter your email and password.") 
        else: 
            try: 
                result = db.auth.sign_in_with_password( 
                    {"email": email.strip(), "password": password} 
                ) 
            except Exception: 
                logger.exception("Supabase sign in failed") 
                st.error("Sign in failed. Check your credentials and account status.") 
            else: 
                if result.session is not None: 
                    st.rerun() 
                st.error("No session was created. Check your account status.") 
    st.stop() 

st.caption(f"Signed in as {session.user.email}") 
if st.button("Sign out"): 
    try: 
        db.auth.sign_out({"scope": "local"}) 
    except Exception: 
        logger.exception("Remote sign out failed; clearing local session") 
    st.session_state.pop("_supabase", None) 
    st.rerun() 

st.subheader("Add feedback") 
with st.form("feedback"): 
    name = st.text_input("Your name", max_chars=100) 
    message = st.text_area("Message", max_chars=2000) 
    save = st.form_submit_button("Save", type="primary") 

if save: 
    name, message = name.strip(), message.strip() 
    if not name or not message: 
        st.warning("Enter both your name and a message.") 
    else: 
        try: 
            # user_id, id and created_at are assigned by the database. 
            result = ( 
                db.table("app_feedback") 
                .insert({"name": name, "message": message}) 
                .execute() 
            ) 
        except Exception: 
            logger.exception("Supabase insert failed") 
            st.error("Save could not be confirmed. Refresh records before retrying.") 
        else: 
            st.success("Saved in Supabase.") 
            if result.data: 
                st.caption(f"Record ID: {result.data[0]['id']}") 

st.subheader("Your saved feedback") 
st.button("Refresh records") 
try: 
    result = ( 
        db.table("app_feedback") 
        .select("id, name, message, created_at") 
        .order("created_at", desc=True) 
        .limit(50) 
        .execute() 
    ) 
except Exception: 
    logger.exception("Supabase read failed") 
    st.error("Could not load records. Check the table, permissions and session.") 
else: 
    if result.data: 
        st.dataframe(result.data, hide_index=True, width="stretch") 
    else: 
        st.info("No feedback saved for this account yet.") 
