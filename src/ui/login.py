# ui/login.py
import urllib.parse as _url
import streamlit as st
from auth_config import EASY_AUTH

if EASY_AUTH:
    st.markdown("""... your /.auth login buttons ...""", unsafe_allow_html=True)
else:
    st.info("🔓 Public mode: no login required here")

# =========================
# CONFIG BÁSICA
# =========================
REDIRECT_AFTER_LOGIN = "/"      # para onde mandar o usuário depois do login
APP_NAME = "AskMyDocs"

st.set_page_config(
    page_title=f"Entrar • {APP_NAME}", page_icon="🔐", layout="centered")

# =========================
# ESTILO (dark caprichado)
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
        font-size: 1.35rem; margin: 0; letter-spacing:.2px;
      }
      .muted { color:#bdbdbd; font-size:.92rem; margin: 4px 0 20px; text-align:center;}
      .btn {
        display:block; width:100%; text-align:center; padding:12px 14px; margin:10px 0;
        border-radius:10px; font-weight:700; border:1px solid transparent; text-decoration:none;
        transition: transform .04s ease-in-out, opacity .15s;
      }
      .btn:hover { transform: translateY(-1px); opacity:.96; }
      .btn:active { transform: translateY(0); }

      /* Botões por provedor */
      .microsoft { background: linear-gradient(90deg,#0a84ff,#1ac8d6); color:#fff; }
      .google    { background: #202124; color:#fff; border-color:#303134; }
      .github    { background: #0d1117; color:#fff; border-color:#30363d; }
      .twitter   { background: #15202b; color:#e6f1f8; border-color:#253341; }

      .sep { text-align:center; color:#9b9b9b; margin:14px 0 8px; font-size:.85rem;}
      .tiny { color:#8e8e8e; font-size:.8rem; margin-top:14px; text-align:center;}
      .tiny a { color:#b9e4ff; text-decoration:none; }
      .tiny a:hover { text-decoration:underline; }
    </style>
    """,
    unsafe_allow_html=True,
)

# =========================
# REDIRECT AUTOMÁTICO SE JÁ ESTIVER LOGADO
# (consulta /.auth/me no client e redireciona)
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
# CONTEÚDO
# =========================
st.markdown(
    f"""
    <div class="login-wrap">
      <div class="brand">
        <span style="font-size:1.4rem">🔐</span>
        <h1>Bem-vindo ao <strong>{APP_NAME}</strong></h1>
      </div>
      <p class="muted">Faça login para continuar. Seus dados são protegidos via Azure App Service Authentication.</p>

      <a class="btn microsoft" href="/.auth/login/microsoft?post_login_redirect_url={_url.quote(REDIRECT_AFTER_LOGIN)}">
        Entrar com Microsoft
      </a>
      <a class="btn google" href="/.auth/login/google?post_login_redirect_url={_url.quote(REDIRECT_AFTER_LOGIN)}">
        Entrar com Google
      </a>
      <a class="btn github" href="/.auth/login/github?post_login_redirect_url={_url.quote(REDIRECT_AFTER_LOGIN)}">
        Entrar com GitHub
      </a>
      <a class="btn twitter" href="/.auth/login/twitter?post_login_redirect_url={_url.quote(REDIRECT_AFTER_LOGIN)}">
        Entrar com X (Twitter)
      </a>

      <div class="sep">—</div>
      <p class="tiny">
        Ao continuar, você concorda com nossos
        <a href="/terms" target="_self">Termos de Uso</a> e
        <a href="/privacy" target="_self">Política de Privacidade</a>.
      </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# Rodapé discreto
st.caption("Feito com 💙 para acelerar seu trabalho com documentos.")


# =========================
# DICA: BOTÃO DE SAIR (se quiser reaproveitar no app principal)
# href = '/.auth/logout?post_logout_redirect_uri=/ui/login'
# =========================
