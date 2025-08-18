# ui/login.py
import urllib.parse as _url
import streamlit as st
from auth_config import EASY_AUTH


# =========================
# BASIC CONFIG
# =========================
REDIRECT_AFTER_LOGIN = "/"      # where to send user after login
APP_NAME = "AskMyDocs"

st.set_page_config(
    page_title=f"Sign In • {APP_NAME}", page_icon="🔐", layout="centered")

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

      /* Provider buttons - Dark theme */
      .microsoft { 
        background: #2b2b2b; 
        color: #ffffff; 
        border: 1px solid #404040;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
      }
      .microsoft:hover { background: #383838; }
      
      .google { 
        background: #2b2b2b; 
        color: #ffffff; 
        border: 1px solid #404040;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
      }
      .google:hover { background: #383838; }
      
      .github { 
        background: #2b2b2b; 
        color: #ffffff; 
        border: 1px solid #404040;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
      }
      .github:hover { background: #383838; }

      .sep { text-align:center; color:#cccccc; margin:14px 0 8px; font-size:.85rem;}
      .tiny { color:#cccccc; font-size:.8rem; margin-top:14px; text-align:center;}
      .tiny a { color:#4fc3f7; text-decoration:none; }
      .tiny a:hover { text-decoration:underline; }
    </style>
    """,
    unsafe_allow_html=True,
)

# =========================
# AUTO REDIRECT IF ALREADY LOGGED IN
# (check /.auth/me on client and redirect)
# =========================
st.markdown(
    f"""
    <script>
      (function() {{
        fetch('/.auth/me', {{credentials:'include'}})
          .then(r => r.ok ? r.json() : null)
          .then(d => {{
            if (Array.isArray(d) && d.length > 0) {{
              const target = "{_url.quote(REDIRECT_AFTER_LOGIN)}";
              if (window.location.pathname !== target) {{
                window.location.href = target;
              }}
            }}
          }})
          .catch(() => {{ /* silencioso */ }});
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
            <span style="font-size:1.4rem">🔐</span>
            <h1>Welcome to <strong>{APP_NAME}</strong></h1>
          </div>
          <p class="muted">Sign in to continue. Your data is protected via Azure App Service Authentication.</p>

          <a class="btn microsoft" href="/.auth/login/microsoft?post_login_redirect_url={_url.quote(REDIRECT_AFTER_LOGIN)}">
            <svg width="20" height="20" viewBox="0 0 23 23" fill="currentColor">
              <path d="M1 1h10v10H1V1zm11 0h10v10H12V1zM1 12h10v10H1V12zm11 0h10v10H12V12z"/>
            </svg>
            Sign in with Microsoft
          </a>
          <a class="btn google" href="/.auth/login/google?post_login_redirect_url={_url.quote(REDIRECT_AFTER_LOGIN)}">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
              <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
              <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
              <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
              <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
            </svg>
            Sign in with Google
          </a>
          <a class="btn github" href="/.auth/login/github?post_login_redirect_url={_url.quote(REDIRECT_AFTER_LOGIN)}">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
            </svg>
            Sign in with GitHub
          </a>

          <div class="sep">—</div>
          <p class="tiny">
            <a href="/.auth/logout?post_logout_redirect_uri=/ui/login" style="color:#ff6b6b;">Sign out</a> if you're already logged in
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
            <h1>Welcome to <strong>{APP_NAME}</strong></h1>
          </div>
          <p class="muted">Public mode enabled - no authentication required.</p>

          <a class="btn microsoft" href="{REDIRECT_AFTER_LOGIN}" style="background: #28a745; border-color: #28a745;">
            Continue as Guest
          </a>

          <div class="sep">—</div>
          <p class="tiny">
            Running in public mode. Authentication is disabled.
          </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

# Footer
st.caption("Made with 💙 to accelerate your work with documents.")


# =========================
# TIP: LOGOUT BUTTON (if you want to reuse in the main app)
# href = '/.auth/logout?post_logout_redirect_uri=/ui/login'
# =========================
