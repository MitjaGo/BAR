# generate_hash.py
import os, hashlib, binascii, base64

def generate_password_hash(password: str, iterations: int = 200_000):
    salt = os.urandom(16)                # 16 bytes salt
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, iterations)
    b64_hash = base64.b64encode(dk).decode()
    hex_salt = binascii.hexlify(salt).decode()
    return b64_hash, hex_salt, iterations

if __name__ == "__main__":
    pw = input("New password: ")
    b64_hash, hex_salt, iter_count = generate_password_hash(pw)
    print("Put these in your secrets.toml under [app]:")
    print("password_hash = {!r}".format(b64_hash))
    print("password_salt = {!r}".format(hex_salt))
    print("iterations = {}".format(iter_count))
# app.py
import streamlit as st
import hashlib, binascii, base64

# Helper — verify password using PBKDF2
def verify_password(plain_password: str, stored_b64_hash: str, stored_hex_salt: str, iterations: int = 200_000) -> bool:
    salt = binascii.unhexlify(stored_hex_salt)
    dk = hashlib.pbkdf2_hmac("sha256", plain_password.encode(), salt, iterations)
    b64 = base64.b64encode(dk).decode()
    return b64 == stored_b64_hash

# ---- UI ----
st.set_page_config(page_title="Protected Streamlit App")

# Read secrets (from secrets.toml locally, or from cloud provider)
app_secrets = st.secrets.get("app", {})
postgres_secrets = st.secrets.get("postgres", {})

# Basic session-state login persistence
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

st.title("My Streamlit App — Login required")

if not st.session_state.authenticated:
    with st.form("login_form"):
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Log in")
    if submitted:
        stored_hash = app_secrets.get("password_hash")
        stored_salt = app_secrets.get("password_salt")
        iterations = int(app_secrets.get("iterations", 200_000))
        if not stored_hash or not stored_salt:
            st.error("No password configured in st.secrets['app']. Please set it.")
        else:
            if verify_password(password, stored_hash, stored_salt, iterations):
                st.session_state.authenticated = True
                st.success("Logged in!")
            else:
                st.error("Incorrect password.")
else:
    st.success("You are authenticated — welcome!")
    # Protected content
    st.write("Here is the secret data only shown after login.")
    st.write("Example: fetch DB credentials from secrets (but don't print them in production!)")
    if postgres_secrets:
        st.write("DB host:", postgres_secrets.get("host"))
        # NEVER show db password in a real app. This is just demo.
    else:
        st.info("No postgres credentials found in st.secrets['postgres']")

    # Add a logout button
    if st.button("Log out"):
        st.session_state.authenticated = False
        st.experimental_rerun()

