import streamlit as st
import streamlit.components.v1 as components
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from io import BytesIO
from PIL import Image, ImageEnhance

COUNT_URL = "https://01234santhoshprabhu.github.io/count/"
TOOL_URL = "https://01234santhoshprabhu.github.io/Tool/"
WATERMARK_URL = "https://nptel-watermark.onrender.com/"

FIREBASE_CONFIG = {
    "apiKey": "AIzaSyButgD2N77doaabtGf-uzffjA5Xc4lh_sU",
    "authDomain": "nptelportalteam.firebaseapp.com",
    "projectId": "nptelportalteam",
    "storageBucket": "nptelportalteam.firebasestorage.app",
    "messagingSenderId": "574729426785",
    "appId": "1:574729426785:web:12c57aa54179167eeb1720",
}

st.set_page_config(page_title="NPTEL Watermark System", layout="wide")


def get_query_value(name):
    try:
        value = st.query_params.get(name)
    except Exception:
        params = st.experimental_get_query_params()
        value = params.get(name, [None])[0]
    if isinstance(value, list):
        return value[0] if value else None
    return value


def set_query_values(**values):
    cleaned = {key: value for key, value in values.items() if value}
    try:
        st.query_params.clear()
        for key, value in cleaned.items():
            st.query_params[key] = value
    except Exception:
        st.experimental_set_query_params(**cleaned)


def firebase_login_gate():
    signed_out = get_query_value("wm_signed_out")
    auth_email = get_query_value("wm_auth_email")
    if auth_email and not signed_out:
        return auth_email

    components.html(
        f"""
        <div style="min-height:620px;display:grid;place-items:center;background:linear-gradient(135deg,#eef4fb,#f8fbff 52%,#edf5ff);font-family:Segoe UI,Arial,sans-serif;">
          <div style="width:min(440px,calc(100% - 32px));padding:30px;border:1px solid #d9dee8;border-radius:8px;background:#fff;box-shadow:0 24px 70px rgba(15,34,65,.16);text-align:center;">
            <div style="width:50px;height:50px;margin:0 auto 14px;display:grid;place-items:center;border-radius:8px;background:linear-gradient(135deg,#1976d2,#15b97e);color:#fff;font-weight:800;">N</div>
            <div style="color:#64748b;font-size:11px;font-weight:800;letter-spacing:.12em;text-transform:uppercase;margin-bottom:8px;">NPTEL Portal Team</div>
            <h1 style="margin:0 0 8px;color:#172033;font-size:26px;">Watermark Login</h1>
            <p id="msg" style="margin:0 0 20px;color:#5f6f86;font-size:14px;line-height:1.5;">Sign in once to use Count, Tool, and Watermark.</p>
            <button id="login" class="animated-login-btn"><span>Sign in with Google</span><span class="login-scene" aria-hidden="true"></span></button>
            <div id="error" style="min-height:18px;margin-top:14px;color:#dc2626;font-size:12px;line-height:1.45;"></div>
            <div style="display:flex;gap:8px;margin-top:18px;justify-content:center;flex-wrap:wrap;">
              <a href="{COUNT_URL}" target="_top" style="color:#1769d8;font-weight:800;text-decoration:none;">Count</a>
              <a href="{TOOL_URL}" target="_top" style="color:#1769d8;font-weight:800;text-decoration:none;">Tool</a>
            </div>
          </div>
        </div>
                <style>
          .animated-login-btn {{
            position: relative;
            width: 100%;
            min-height: 46px;
            display: inline-flex;
            align-items: center;
            justify-content: space-between;
            gap: 12px;
            overflow: hidden;
            border: 0;
            border-radius: 6px;
            padding: 0 14px 0 22px;
            background: #1769d8;
            color: #fff;
            font-weight: 800;
            cursor: pointer;
            box-shadow: 0 10px 22px rgba(23,105,216,.22);
            isolation: isolate;
            transition: transform .25s ease, box-shadow .25s ease;
          }}
          .animated-login-btn::before {{
            content: "";
            position: absolute;
            inset: 0;
            z-index: -1;
            background: linear-gradient(120deg, rgba(255,255,255,.16), transparent 34%, rgba(255,255,255,.22) 52%, transparent 70%);
            transform: translateX(-110%);
            transition: transform .65s ease;
          }}
          .animated-login-btn:hover,
          .animated-login-btn:focus-visible {{
            transform: translateY(-1px);
            box-shadow: 0 16px 30px rgba(23,105,216,.28);
          }}
          .animated-login-btn:hover::before,
          .animated-login-btn:focus-visible::before {{ transform: translateX(110%); }}
          .login-scene {{
            position: relative;
            width: 58px;
            height: 30px;
            flex: 0 0 58px;
          }}
          .login-scene::before {{
            content: "";
            position: absolute;
            right: 2px;
            top: 3px;
            width: 18px;
            height: 24px;
            border-radius: 3px;
            background: #fff;
            box-shadow: inset -5px 0 0 rgba(23,105,216,.24), 0 0 0 2px rgba(255,255,255,.46);
          }}
          .login-scene::after {{
            content: "";
            position: absolute;
            left: 6px;
            top: 9px;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #fff;
            box-shadow: 0 9px 0 1px #fff, 9px 12px 0 -1px #fff, 17px 15px 0 -2px #fff;
            animation: authWalk 1.45s ease-in-out infinite;
          }}
          .animated-login-btn:hover .login-scene::after,
          .animated-login-btn:focus-visible .login-scene::after {{ animation-duration: .78s; }}
          .animated-login-btn:active .login-scene::before {{
            transform: perspective(80px) rotateY(-18deg);
            transform-origin: right center;
          }}
          @keyframes authWalk {{
            0%, 100% {{ transform: translateX(0); }}
            50% {{ transform: translateX(18px); }}
          }}
          @media (prefers-reduced-motion: reduce) {{
            .animated-login-btn,
            .animated-login-btn::before,
            .login-scene::after {{ animation: none !important; transition: none !important; }}
          }}
        </style>        <script src="https://www.gstatic.com/firebasejs/10.12.5/firebase-app-compat.js"></script>
        <script src="https://www.gstatic.com/firebasejs/10.12.5/firebase-auth-compat.js"></script>
        <script>
          const firebaseConfig = {FIREBASE_CONFIG};
          const forceSignedOut = {str(bool(get_query_value("wm_signed_out"))).lower()};
          if (!firebase.apps.length) firebase.initializeApp(firebaseConfig);
          const auth = firebase.auth();
          const login = document.getElementById('login');
          const error = document.getElementById('error');
          const msg = document.getElementById('msg');
          const loginLabel = login.querySelector('span:first-child');
          function setLoginText(text) {{ loginLabel.textContent = text; }}
          function enter(user) {{
            const email = encodeURIComponent(user.email || user.displayName || 'signed-in');
            const url = new URL(window.parent.location.href);
            url.searchParams.set('wm_auth_email', email);
            url.searchParams.delete('wm_signed_out');
            window.parent.location.href = url.toString();
          }}
          login.addEventListener('click', async () => {{
            login.disabled = true;
            setLoginText('Opening Google...');
            error.textContent = '';
            try {{
              const provider = new firebase.auth.GoogleAuthProvider();
              provider.setCustomParameters({{ prompt: 'select_account' }});
              const result = await auth.signInWithPopup(provider);
              enter(result.user);
            }} catch (err) {{
              login.disabled = false;
              setLoginText('Sign in with Google');
              error.textContent = err && err.message ? err.message : 'Google sign-in failed.';
            }}
          }});
          auth.onAuthStateChanged(async user => {{
            if (forceSignedOut && user) {{
              await auth.signOut();
              msg.textContent = 'Signed out. Choose Google sign-in to continue.';
              return;
            }}
            if (user && !forceSignedOut) {{
              msg.textContent = 'Signed in. Opening Watermark...';
              enter(user);
            }}
          }});
        </script>
        """,
        height=660,
    )
    st.stop()


signed_in_email = firebase_login_gate()

st.markdown("""
    <style>
    .main-title {
        font-size: 36px;
        font-weight: 700;
        color: #1f4e79;
        margin-bottom: 2px;
    }
    .sub-text {
        font-size: 16px;
        color: gray;
        margin-top: 0;
    }
    .portal-bar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 12px;
        flex-wrap: wrap;
        padding: 12px 14px;
        border: 1px solid #d9dee8;
        border-radius: 8px;
        background: #ffffff;
        margin-bottom: 18px;
    }
    .portal-links {
        display: flex;
        gap: 8px;
        flex-wrap: wrap;
    }
    .portal-links a, .portal-signout {
        display: inline-flex;
        align-items: center;
        min-height: 36px;
        border-radius: 999px;
        padding: 0 14px;
        background: #1769d8;
        color: #fff !important;
        font-size: 12px;
        font-weight: 800;
        text-decoration: none;
        border: 0;
    }
    .portal-links a.secondary {
        background: #0f766e;
    }
    .portal-user {
        color: #172033;
        font-size: 12px;
        font-weight: 700;
    }
    .stButton>button {
        background-color: #1f4e79;
        color: white;
        font-weight: 600;
        border-radius: 8px;
        height: 45px;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown(
    f"""
    <div class="portal-bar">
      <div class="portal-user">Signed in: {signed_in_email}</div>
      <div class="portal-links">
        <a href="{COUNT_URL}" target="_self">Count</a>
        <a class="secondary" href="{TOOL_URL}" target="_self">Tool</a>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown('<p class="main-title">NPTEL PDF Watermark System</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-text">Upload multiple PDFs and apply secure logo watermark.</p>', unsafe_allow_html=True)

if st.button("Sign out"):
    set_query_values(wm_signed_out="1")
    st.rerun()

col1, col2 = st.columns([1, 1])

with col1:
    pdf_files = st.file_uploader(
        "Upload PDF Files",
        type=["pdf"],
        accept_multiple_files=True,
    )

    logo_file = st.file_uploader(
        "Upload Logo Image",
        type=["png", "jpg", "jpeg"],
    )

with col2:
    st.subheader("Watermark Settings")

    size_percent = st.slider("Watermark Size (%)", 10, 80, 40)
    opacity = st.slider("Transparency", 0.05, 1.0, 0.3)
    rotation = st.slider("Rotation", -180, 180, 0)

    position = st.selectbox(
        "Position",
        ["Center", "Top Center", "Bottom Center"],
    )

if logo_file:
    st.markdown("---")
    st.subheader("Watermark Preview")

    preview_bg = Image.new("RGB", (600, 800), "white")
    logo = Image.open(logo_file).convert("RGBA")

    new_width = int(600 * (size_percent / 100))
    logo = logo.resize((new_width, new_width))

    alpha = logo.split()[3]
    alpha = ImageEnhance.Brightness(alpha).enhance(opacity)
    logo.putalpha(alpha)

    logo = logo.rotate(rotation, expand=True)

    if position == "Center":
        x = (600 - logo.width) // 2
        y = (800 - logo.height) // 2
    elif position == "Top Center":
        x = (600 - logo.width) // 2
        y = 50
    else:
        x = (600 - logo.width) // 2
        y = 800 - logo.height - 50

    preview_bg.paste(logo, (x, y), logo)

    st.image(preview_bg, caption="Watermark Preview (Sample Page)", width="stretch")


def add_watermark(input_pdf, watermark_image):
    reader = PdfReader(input_pdf)
    writer = PdfWriter()

    for page in reader.pages:
        packet = BytesIO()
        page_width = float(page.mediabox.width)
        page_height = float(page.mediabox.height)

        c = canvas.Canvas(packet, pagesize=(page_width, page_height))
        img = ImageReader(watermark_image)

        watermark_width = page_width * (size_percent / 100)
        watermark_height = watermark_width

        if position == "Center":
            x = (page_width - watermark_width) / 2
            y = (page_height - watermark_height) / 2
        elif position == "Top Center":
            x = (page_width - watermark_width) / 2
            y = page_height - watermark_height - 50
        else:
            x = (page_width - watermark_width) / 2
            y = 50

        c.saveState()
        c.translate(page_width / 2, page_height / 2)
        c.rotate(rotation)
        c.translate(-page_width / 2, -page_height / 2)
        c.setFillAlpha(opacity)

        c.drawImage(
            img,
            x,
            y,
            width=watermark_width,
            height=watermark_height,
            mask="auto",
        )

        c.restoreState()
        c.save()

        packet.seek(0)
        watermark_pdf = PdfReader(packet)
        page.merge_page(watermark_pdf.pages[0])
        writer.add_page(page)

    output = BytesIO()
    writer.write(output)
    output.seek(0)
    return output


if "processed_files" not in st.session_state:
    st.session_state.processed_files = {}

if pdf_files and logo_file:
    if st.button("Apply Watermark to All PDFs"):
        st.session_state.processed_files = {}

        for pdf in pdf_files:
            with st.spinner(f"Processing {pdf.name}..."):
                output_pdf = add_watermark(pdf, logo_file)
                st.session_state.processed_files[pdf.name] = output_pdf

        st.success("All PDFs processed successfully!")

if st.session_state.processed_files:
    st.markdown("---")
    st.subheader("Download Watermarked PDFs")

    for name, file in st.session_state.processed_files.items():
        st.download_button(
            label=f"Download {name}",
            data=file,
            file_name=name,
            mime="application/pdf",
            key=name,
        )
