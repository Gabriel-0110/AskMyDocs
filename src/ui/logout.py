# ui/logout.py
import urllib.parse as _url
import streamlit as st
from auth_config import EASY_AUTH

# =========================
# BASIC CONFIG
# =========================
REDIRECT_AFTER_LOGOUT = "/ui/login"  # where to send user after logout
APP_NAME = "AskMyDocs"

st.set_page_config(
    page_title=f"Sign Out • {APP_NAME}", page_icon="🔐", layout="centered")

# =========================
# STYLING (dark theme)
# =========================
st.markdown(
    """
    <style>
      html, body, [data-testid="stAppViewContainer"] {
        background: radial-gradient(60% 60% at 20% 20%, #222 0%, #111 40%, #0b0b0b 100%) !important;
      }
      .login-wrap {
        max-width: 440px;
        margin: 6vh auto 8vh;
        padding: 28px 26px;
        background: rgba(25,25,25,0.85);
        border: 1px solid #2c2c2c;
        border-radius: 14px;
        box-shadow: 0 10px 40px rgba(0,0,0,.35);
      }
      .brand {
        display:flex; align-items:center; gap:10px; justify-content:center;
        margin-bottom: 10px;
      }
      .brand h1{
        font-size: 1.35rem; margin: 0; letter-spacing:.2px; color: #ffffff;
      }
      .muted { color:#e0e0e0; font-size:.92rem; margin: 4px 0 20px; text-align:center;}
      .btn {
        display:block; width:100%; text-align:center; padding:12px 14px; margin:10px 0;
        border-radius:10px; font-weight:700; border:1px solid transparent; text-decoration:none;
        transition: transform .04s ease-in-out, opacity .15s;
      }
      .btn:hover { transform: translateY(-1px); opacity:.96; }
      .btn:active { transform: translateY(0); }

      /* Logout button styling - same as login buttons */
      .logout-btn { 
        background: #2b2b2b; 
        color: #ffffff; 
        border: 1px solid #404040;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
      }
      .logout-btn:hover { background: #383838; }
      
      .back-btn { 
        background: #2b2b2b; 
        color: #ffffff; 
        border: 1px solid #404040;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
      }
      .back-btn:hover { background: #383838; }

      .sep { text-align:center; color:#cccccc; margin:14px 0 8px; font-size:.85rem;}
      .tiny { color:#cccccc; font-size:.8rem; margin-top:14px; text-align:center;}
      .tiny a { color:#4fc3f7; text-decoration:none; }
      .tiny a:hover { text-decoration:underline; }
    </style>
    """,
    unsafe_allow_html=True,
)

# =========================
# AUTO LOGOUT LOGIC
# =========================
st.markdown(
    f"""
    <script>
      (function() {{
        // Check if user wants to logout (via URL parameter)
        const urlParams = new URLSearchParams(window.location.search);
        if (urlParams.get('confirm') === 'true') {{
          // Show loading message and perform logout
          document.body.innerHTML = '<div style="display:flex;justify-content:center;align-items:center;height:100vh;color:white;font-family:system-ui;"><div style="text-align:center;"><div style="font-size:2rem;margin-bottom:1rem;">🔐</div><div>Signing you out...</div></div></div>';
          setTimeout(() => {{
            window.location.href = '/.auth/logout?post_logout_redirect_uri={_url.quote(REDIRECT_AFTER_LOGOUT)}';
          }}, 1000);
        }}
      }})();
    </script>
    """,
    unsafe_allow_html=True,
)

# =========================
# CONTENT
# =========================
if EASY_AUTH:
    st.markdown(
        f"""
        <div class="login-wrap">
          <div class="brand">
            <span style="font-size:1.4rem">🚪</span>
            <h1>Sign out of <strong>{APP_NAME}</strong></h1>
          </div>
          <p class="muted">Are you sure you want to sign out? You'll need to sign in again to access your documents.</p>

          <a class="btn logout-btn" href="/ui/logout?confirm=true">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
              <path d="M17 7l-1.41 1.41L18.17 11H8v2h10.17l-2.58 2.59L17 17l5-5zM4 5h8V3H4c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h8v-2H4V5z"/>
            </svg>
            Yes, Sign Out
          </a>
          
          <a class="btn back-btn" href="#" onclick="window.location.href='/'; return false;">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
              <path d="M20 11H7.83l5.59-5.59L12 4l-8 8 8 8 1.41-1.41L7.83 13H20v-2z"/>
            </svg>
            Cancel, Go Back
          </a>

          <div class="sep">—</div>
          <p class="tiny">
            Your session will be securely terminated and you'll be redirected to the login page.
          </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        f"""
        <div class="login-wrap">
          <div class="brand">
            <span style="font-size:1.4rem">🔓</span>
            <h1>Logout from <strong>{APP_NAME}</strong></h1>
          </div>
          <p class="muted">You're in public mode. No authentication session to terminate.</p>

          <a class="btn back-btn" href="#" onclick="window.location.href='/'; return false;">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
              <path d="M20 11H7.83l5.59-5.59L12 4l-8 8 8 8 1.41-1.41L7.83 13H20v-2z"/>
            </svg>
            Return to App
          </a>

          <div class="sep">—</div>
          <p class="tiny">
            Running in public mode. No authentication required.
          </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

# Footer
st.caption("Made with 💙 to accelerate your work with documents.")