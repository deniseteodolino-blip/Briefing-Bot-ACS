"""
Briefing Bot ACS - Web Interface Premium
Automação de pacote de validação CSI
"""

import os
import sys
import tempfile
import streamlit as st
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv

load_dotenv()

# CSI Pipefy link
CSI_LINK = "https://app.pipefy.com/organizations/330500/interfaces/741579fb-df99-4642-9b5a-d8e290b6f6ce/pages/00e630fb-4c13-45b0-b114-98271b58d36f?form=f3ffaa88-74d0-42a1-ad76-7e19886d95c6&origin=public%20form"

# Supabase config
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# ============================================
# CUSTOM CSS - Premium SaaS Design
# ============================================
st.set_page_config(
    page_title="Briefing Bot",
    page_icon="🔷",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Premium CSS
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* Root Variables */
    :root {
        --primary: #2563EB;
        --primary-dark: #1D4ED8;
        --primary-light: #3B82F6;
        --success: #10B981;
        --warning: #F59E0B;
        --error: #EF4444;
        --bg-primary: #FAFBFC;
        --bg-secondary: #FFFFFF;
        --bg-tertiary: #F3F4F6;
        --text-primary: #111827;
        --text-secondary: #6B7280;
        --text-muted: #9CA3AF;
        --border: #E5E7EB;
        --border-light: #F3F4F6;
        --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
        --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        --radius-sm: 8px;
        --radius-md: 12px;
        --radius-lg: 16px;
        --transition: all 0.2s ease;
    }

    /* Base Styles */
    .stApp {
        background: var(--bg-primary);
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Typography */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        color: var(--text-primary);
    }

    /* Main Container */
    .main-container {
        max-width: 1200px;
        margin: 0 auto;
        padding: 40px 24px;
    }

    /* Header */
    .header {
        text-align: center;
        margin-bottom: 48px;
    }

    .header h1 {
        font-size: 32px;
        font-weight: 700;
        color: var(--text-primary);
        margin-bottom: 8px;
        letter-spacing: -0.02em;
    }

    .header p {
        font-size: 16px;
        color: var(--text-secondary);
        font-weight: 400;
    }

    /* Card Styles */
    .card {
        background: var(--bg-secondary);
        border-radius: var(--radius-lg);
        border: 1px solid var(--border);
        padding: 24px;
        margin-bottom: 24px;
        box-shadow: var(--shadow-sm);
        transition: var(--transition);
    }

    .card:hover {
        box-shadow: var(--shadow-md);
    }

    .card-title {
        font-size: 18px;
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        gap: 12px;
    }

    .card-title span {
        width: 32px;
        height: 32px;
        background: var(--primary);
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 14px;
        font-weight: 600;
    }

    /* Tab Navigation */
    .tabs {
        display: flex;
        gap: 8px;
        margin-bottom: 32px;
        background: var(--bg-secondary);
        padding: 6px;
        border-radius: var(--radius-md);
        border: 1px solid var(--border);
    }

    .tab {
        flex: 1;
        padding: 14px 24px;
        border-radius: var(--radius-sm);
        background: transparent;
        border: none;
        cursor: pointer;
        font-size: 14px;
        font-weight: 500;
        color: var(--text-secondary);
        transition: var(--transition);
    }

    .tab:hover {
        background: var(--bg-tertiary);
        color: var(--text-primary);
    }

    .tab.active {
        background: var(--primary);
        color: white;
    }

    /* File Upload */
    .upload-area {
        border: 2px dashed var(--border);
        border-radius: var(--radius-lg);
        padding: 48px;
        text-align: center;
        background: var(--bg-tertiary);
        transition: var(--transition);
        cursor: pointer;
    }

    .upload-area:hover {
        border-color: var(--primary);
        background: white;
    }

    /* File uploader overlay */
    .upload-overlay {
        position: relative;
    }

    .upload-overlay .stFileUploader {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        opacity: 0;
        cursor: pointer;
    }

    .upload-overlay .stFileUploader > div {
        width: 100%;
    }

    .upload-overlay .stFileUploader label {
        cursor: pointer;
        padding: 32px;
        display: block;
    }

    /* Input Styles */
    .stTextInput > div > div {
        background: var(--bg-secondary);
        border: 1px solid var(--border);
        border-radius: var(--radius-sm);
        padding: 4px;
        transition: var(--transition);
    }

    .stTextInput input {
        padding: 12px 14px !important;
        font-size: 14px !important;
        border: none !important;
    }

    .stTextInput > div > div:focus-within {
        border-color: var(--primary);
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
    }

    /* Form labels */
    .stTextInput label, .stCheckbox label {
        font-size: 13px !important;
        font-weight: 500 !important;
        color: var(--text-secondary) !important;
        margin-bottom: 6px !important;
    }

    /* Button Styles */
    .stButton > button {
        background: var(--primary);
        color: white;
        border: none;
        border-radius: var(--radius-sm);
        padding: 12px 24px;
        font-size: 14px;
        font-weight: 500;
        cursor: pointer;
        transition: var(--transition);
        width: 100%;
    }

    .stButton > button:hover {
        background: var(--primary-dark);
        transform: translateY(-1px);
    }

    .btn-secondary {
        background: var(--bg-secondary) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border) !important;
    }

    .btn-secondary:hover {
        background: var(--bg-tertiary) !important;
    }

    /* Metrics Grid */
    .metrics-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 16px;
        margin: 24px 0;
    }

    .metric-card {
        background: var(--bg-tertiary);
        border-radius: var(--radius-md);
        padding: 20px;
        text-align: center;
        transition: var(--transition);
    }

    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-md);
    }

    .metric-value {
        font-size: 28px;
        font-weight: 700;
        color: var(--text-primary);
        margin-bottom: 4px;
    }

    .metric-label {
        font-size: 12px;
        color: var(--text-secondary);
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    /* Message Box */
    .message-box {
        background: var(--bg-secondary);
        border: 1px solid var(--border);
        border-radius: var(--radius-md);
        padding: 20px;
        font-family: 'Monaco', 'Consolas', monospace;
        font-size: 13px;
        line-height: 1.6;
        white-space: pre-wrap;
        max-height: 400px;
        overflow-y: auto;
    }

    /* History Card */
    .history-card {
        background: var(--bg-secondary);
        border: 1px solid var(--border);
        border-radius: var(--radius-md);
        padding: 20px;
        margin-bottom: 16px;
        transition: var(--transition);
    }

    .history-card:hover {
        border-color: var(--primary-light);
        box-shadow: var(--shadow-md);
    }

    .history-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 16px;
    }

    .history-title {
        font-size: 15px;
        font-weight: 600;
        color: var(--text-primary);
    }

    .history-date {
        font-size: 13px;
        color: var(--text-muted);
    }

    .history-actions {
        display: flex;
        gap: 8px;
        margin-top: 16px;
    }

    .history-actions button {
        padding: 8px 16px;
        border-radius: var(--radius-sm);
        font-size: 13px;
        font-weight: 500;
        cursor: pointer;
        border: 1px solid var(--border);
        background: white;
        color: var(--text-primary);
        transition: var(--transition);
    }

    .history-actions button:hover {
        background: var(--bg-tertiary);
    }

    .btn-csi {
        background: var(--primary) !important;
        color: white !important;
        border: none !important;
    }

    .btn-csi:hover {
        background: var(--primary-dark) !important;
    }

    .btn-download {
        background: var(--bg-secondary) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border) !important;
    }

    .btn-download:hover {
        background: var(--bg-tertiary) !important;
    }

    .btn-delete {
        background: transparent !important;
        color: var(--error) !important;
        border: 1px solid var(--error) !important;
    }

    .btn-delete:hover {
        background: var(--error) !important;
        color: white !important;
    }

    /* Success State */
    .success-message {
        background: linear-gradient(135deg, #10B981 0%, #059669 100%);
        color: white;
        padding: 16px 24px;
        border-radius: var(--radius-md);
        text-align: center;
        margin: 24px 0;
    }

    /* Error State */
    .error-message {
        background: linear-gradient(135deg, #EF4444 0%, #DC2626 100%);
        color: white;
        padding: 16px 24px;
        border-radius: var(--radius-md);
        text-align: center;
        margin: 24px 0;
    }

    /* Sidebar adjustment */
    .css-1d391kg {
        background: var(--bg-secondary);
    }

    /* Expander styling */
    .streamlit-expanderHeader {
        background: var(--bg-secondary);
        border: 1px solid var(--border);
        border-radius: var(--radius-md);
        padding: 16px 20px;
    }

    .streamlit-expanderHeader:hover {
        background: var(--bg-tertiary);
    }

    /* Form styling */
    .stForm {
        background: var(--bg-secondary);
        border-radius: var(--radius-lg);
        padding: 24px;
        border: 1px solid var(--border);
    }

    /* Checkbox styling */
    .stCheckbox > label {
        color: var(--text-secondary);
        font-size: 14px;
    }

    /* Link button */
    .link-btn {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
        background: var(--success);
        color: white;
        padding: 12px 24px;
        border-radius: var(--radius-sm);
        text-decoration: none;
        font-weight: 500;
        font-size: 14px;
        transition: var(--transition);
    }

    .link-btn:hover {
        background: #059669;
        transform: translateY(-1px);
    }

    /* Login page */
    .login-container {
        max-width: 400px;
        margin: 80px auto;
        padding: 48px;
        background: var(--bg-secondary);
        border-radius: var(--radius-lg);
        border: 1px solid var(--border);
        box-shadow: var(--shadow-lg);
    }

    .login-input {
        background: var(--bg-secondary) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius-sm) !important;
        padding: 14px 16px !important;
        font-size: 15px !important;
        transition: var(--transition) !important;
    }

    .login-input:focus {
        border-color: var(--primary) !important;
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1) !important;
    }

    .login-btn {
        background: var(--primary) !important;
        color: white !important;
        border: none !important;
        border-radius: var(--radius-sm) !important;
        padding: 14px 24px !important;
        font-size: 15px !important;
        font-weight: 500 !important;
        cursor: pointer !important;
        transition: var(--transition) !important;
        width: 100% !important;
    }

    .login-btn:hover {
        background: var(--primary-dark) !important;
        transform: translateY(-1px);
    }

    .login-divider {
        text-align: center;
        margin: 24px 0;
        color: var(--text-muted);
        font-size: 13px;
    }

    .login-demo-btn {
        background: var(--bg-tertiary) !important;
        color: var(--text-secondary) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius-sm) !important;
        padding: 14px 24px !important;
        font-size: 14px !important;
        cursor: pointer !important;
        transition: var(--transition) !important;
        width: 100% !important;
    }

    .login-demo-btn:hover {
        background: var(--bg-secondary) !important;
        color: var(--text-primary) !important;
        border-color: var(--text-muted) !important;
    }

    /* Input container spacing */
    .stTextInput {
        margin-bottom: 16px !important;
    }

    .stTextInput label {
        font-size: 13px !important;
        font-weight: 500 !important;
        color: var(--text-secondary) !important;
        margin-bottom: 8px !important;
        display: block !important;
    }

    /* Divider */
    .divider {
        height: 1px;
        background: var(--border);
        margin: 24px 0;
    }

    /* Responsive */
    @media (max-width: 768px) {
        .metrics-grid {
            grid-template-columns: repeat(2, 1fr);
        }

        .main-container {
            padding: 24px 16px;
        }

        .header h1 {
            font-size: 24px;
        }

        .card {
            padding: 16px;
        }
    }

    /* Animation keyframes */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }

    .fade-in {
        animation: fadeIn 0.3s ease forwards;
    }

    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }

    ::-webkit-scrollbar-track {
        background: var(--bg-tertiary);
        border-radius: 4px;
    }

    ::-webkit-scrollbar-thumb {
        background: var(--text-muted);
        border-radius: 4px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: var(--text-secondary);
    }
</style>
""", unsafe_allow_html=True)


def init_session():
    """Initialize session state - checks for existing session on every page load"""
    # Check Supabase for existing session
    existing_user = check_supabase_session()
    if existing_user:
        st.session_state.user = existing_user
        st.session_state.logged_in = True
        return

    # Check query params for persisted login
    if st.query_params.get("logged_in") == "true":
        email = st.query_params.get("email")
        user_id = st.query_params.get("user_id")
        if email:
            st.session_state.user = {"email": email, "id": user_id}
            st.session_state.logged_in = True
            return

    # Check session state
    if not st.session_state.get('logged_in'):
        st.session_state.user = None
        st.session_state.logged_in = False


def check_supabase_session():
    """Check if there's an active Supabase session."""
    if SUPABASE_URL and SUPABASE_KEY:
        try:
            from supabase import create_client
            supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
            user = supabase.auth.get_user()
            if user and hasattr(user, 'email'):
                return {"email": user.email, "id": getattr(user, 'id', 'unknown')}
            session = supabase.auth.get_session()
            if session and hasattr(session, 'user') and session.user:
                st.session_state.access_token = session.access_token
                st.session_state.refresh_token = session.refresh_token
                return {"email": session.user.email, "id": session.user.id}
        except:
            pass
    return None


def persist_login(email: str, user_id: str):
    """Persist login"""
    st.query_params["logged_in"] = "true"
    st.query_params["email"] = email
    st.query_params["user_id"] = user_id


# ============================================
# MAIN APP
# ============================================
def main():
    init_session()

    if not st.session_state.get('logged_in'):
        # Show login page
        col1, col2, col3 = st.columns([1, 2, 1])

        with col2:
            st.markdown("""
            <div style="text-align:center; margin-bottom:40px;">
                <div style="width:56px; height:56px; background:linear-gradient(135deg, #2563EB, #1D4ED8); border-radius:14px; display:flex; align-items:center; justify-content:center; margin:0 auto 20px;">
                    <span style="font-size:28px; color:white; font-weight:700;">B</span>
                </div>
                <h1 style="font-size:22px; margin-bottom:6px;">Briefing Bot</h1>
                <p style="color:#6B7280; font-size:14px;">Automação de pacote de validação CSI</p>
            </div>
            """, unsafe_allow_html=True)

            if SUPABASE_URL and SUPABASE_KEY:
                from supabase import create_client
                supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

                email = st.text_input("Email", placeholder="seu.email@seazone.com.br")
                password = st.text_input("Senha", placeholder="Sua senha", type="password")

                if st.button("Entrar", type="primary", use_container_width=True):
                    if email and password:
                        try:
                            response = supabase.auth.sign_in_with_password(
                                credentials={"email": email, "password": password}
                            )
                            if response.user:
                                st.session_state.user = {"email": response.user.email, "id": response.user.id}
                                st.session_state.access_token = response.session.access_token
                                st.session_state.refresh_token = response.session.refresh_token
                                st.session_state.logged_in = True
                                persist_login(response.user.email, response.user.id)
                                st.rerun()
                        except Exception as e:
                            st.error(f"Erro ao fazer login: {str(e)}")

                st.markdown('<div style="text-align:center; margin:20px 0; color:#9CA3AF; font-size:13px;">ou</div>', unsafe_allow_html=True)

                if st.button("Continuar em modo demo", use_container_width=True):
                    st.session_state.user = {"email": "demo@seazone.com.br", "id": "demo"}
                    st.session_state.logged_in = True
                    st.rerun()
            else:
                st.info("Configure SUPABASE_URL e SUPABASE_KEY no arquivo .env")

                if st.button("Continuar em modo demo", type="primary", use_container_width=True):
                    st.session_state.user = {"email": "demo@seazone.com.br", "id": "demo"}
                    st.session_state.logged_in = True
                    st.rerun()
    else:
        show_main_app()


def show_main_app():
    """Main application interface"""

    # Top bar with Logout
    col_logo, col_space, col_logout = st.columns([2, 5, 1])
    with col_logout:
        if st.button("🚪 Sair", use_container_width=True):
            if SUPABASE_URL and SUPABASE_KEY:
                from supabase import create_client
                supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
                supabase.auth.sign_out()
            st.session_state.user = None
            st.session_state.logged_in = False
            st.query_params.clear()
            st.rerun()

    # Header
    st.markdown("""
    <div class="header" style="margin-top:-20px;">
        <div style="display:flex; align-items:center; justify-content:center; gap:16px; margin-bottom:16px;">
            <div style="width:48px; height:48px; background:linear-gradient(135deg, #2563EB, #1D4ED8); border-radius:12px; display:flex; align-items:center; justify-content:center;">
                <span style="font-size:24px; color:white; font-weight:700;">B</span>
            </div>
            <div style="text-align:left;">
                <h1 style="font-size:28px; margin:0;">Briefing Bot</h1>
                <p style="font-size:14px; color:#6B7280; margin:0;">Automação de pacote de validação CSI</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Navigation tabs
    tab1, tab2 = st.columns([1, 1])

    with tab1:
        if st.button("Processar Minuta", use_container_width=True):
            st.session_state['active_tab'] = 'processar'

    with tab2:
        if st.button("Historico", use_container_width=True):
            st.session_state['active_tab'] = 'historico'

    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

    active_tab = st.session_state.get('active_tab', 'processar')

    if active_tab == 'processar':
        show_process_tab()
    else:
        show_history_tab()


def show_process_tab():
    """Process minuta tab"""

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h3 style='font-size:16px; font-weight:600; margin-bottom:16px; text-align:center;'>Upload da Minuta ACS</h3>", unsafe_allow_html=True)
        uploaded_file = st.file_uploader(
            "Upload da Minuta",
            type=["pdf", "docx"],
            label_visibility="collapsed"
        )

    if uploaded_file:
        col1, col2 = st.columns(2)
        with col1:
            planilha = st.text_input("Link da Planilha de Assinaturas", placeholder="https://docs.google.com/...")
        with col2:
            force_refresh = st.checkbox("Forçar reconsulta de CNPJs")

        st.markdown("<div style='margin:24px 0;'></div>", unsafe_allow_html=True)

        if st.button("Processar Minuta", type="primary", use_container_width=True):
            with st.spinner("Processando..."):
                try:
                    mensagem, spe, acs_num, data_corte, classificacao = process_minuta(
                        uploaded_file, planilha, force_refresh
                    )

                    from history import save_processamento
                    save_processamento(
                        filename=uploaded_file.name,
                        spe=spe, acs_num=acs_num, data_corte=data_corte,
                        classificacao=classificacao, mensagem=mensagem,
                        user_id=st.session_state.get('user', {}).get('id')
                    )

                    st.markdown("""
                    <div class="success-message">
                        Mensagem gerada com sucesso!
                    </div>
                    """, unsafe_allow_html=True)

                    # Metrics
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Estrangeiros", len(classificacao['estrangeiros']))
                    with col2:
                        st.metric("Simples Nacional", len(classificacao['simples_nacional']))
                    with col3:
                        st.metric("ME/EPP", len(classificacao['me_epp']))
                    with col4:
                        st.metric("Erros API", len(classificacao.get('erros', [])))

                    # Message
                    st.markdown("""
                    <div style="margin:24px 0;">
                        <h3 style="font-size:16px; font-weight:600; margin-bottom:12px;">Mensagem Gerada</h3>
                        <div class="message-box">{}</div>
                    </div>
                    """.format(mensagem), unsafe_allow_html=True)

                    # Actions
                    col1, col2 = st.columns([1, 1])
                    with col1:
                        st.download_button(
                            "Baixar mensagem",
                            data=mensagem,
                            file_name=f"briefing_{spe}_{acs_num}acs.txt",
                            mime="text/plain",
                            key=f"dl_msg_{acs_num}",
                            use_container_width=True
                        )
                    with col2:
                        st.link_button(
                            "Enviar para CSI",
                            CSI_LINK,
                            type="primary",
                            use_container_width=True
                        )

                    # Errors
                    true_erros = [e for e in classificacao.get('erros', []) if e.get('bucket') != 'me_epp']
                    if true_erros:
                        st.markdown("<div style='margin-top:24px;'></div>", unsafe_allow_html=True)
                        for erro in true_erros:
                            st.warning(f"{erro.get('nome')}: {erro.get('erro')}")

                except Exception as e:
                    st.markdown(f"""
                    <div class="error-message">
                        Erro ao processar: {str(e)}
                    </div>
                    """, unsafe_allow_html=True)


def show_history_tab():
    """History tab"""
    from history import get_all_processamentos, delete_processamento

    st.markdown("""
    <div style="background:var(--bg-secondary); border:1px solid var(--border); border-radius:12px; padding:20px 24px; margin-bottom:24px;">
        <h3 style="font-size:16px; font-weight:600; color:var(--text-primary); margin:0;">Historico de Processamentos</h3>
    </div>
    """, unsafe_allow_html=True)

    user_id = st.session_state.get('user', {}).get('id') if st.session_state.get('logged_in') else None
    registros = get_all_processamentos(user_id=user_id)

    if not registros:
        st.info("Nenhum processamento encontrado.")
        return

    for registro in registros:
        processed_dt = registro['processed_at']
        try:
            if 'T' in processed_dt:
                dt_obj = datetime.fromisoformat(processed_dt.replace('Z', ''))
                brasilia_offset = timedelta(hours=-3)
                dt_brasilia = dt_obj.replace(tzinfo=timezone.utc).astimezone(timezone(brasilia_offset))
                date_str = dt_brasilia.strftime("%d/%m/%Y")
                time_str = dt_brasilia.strftime("%H:%M")
            else:
                date_str = processed_dt[:10]
                time_str = processed_dt[11:16] if len(processed_dt) > 10 else ''
        except:
            date_str = processed_dt[:10] if processed_dt else ''
            time_str = ''

        classif = registro.get('classificacao', {})

        with st.container():
            col_header = st.columns([3, 1])
            with col_header[0]:
                st.markdown(f"**{registro['filename']}**")
                st.caption(f"{registro['spe']} - {registro['acs_num']}a ACS")
            with col_header[1]:
                st.caption(f"{date_str} as {time_str}")

            cols = st.columns(4)
            with cols[0]:
                st.metric("Estrangeiros", len(classif.get('estrangeiros', [])))
            with cols[1]:
                st.metric("ME/EPP", len(classif.get('me_epp', [])))
            with cols[2]:
                st.metric("Simples", len(classif.get('simples_nacional', [])))
            with cols[3]:
                st.metric("Erros", len(classif.get('erros', [])))

            col_btn = st.columns([1, 1, 1])
            with col_btn[0]:
                st.link_button("Enviar para CSI", CSI_LINK, key=f"csi_{registro['id']}", use_container_width=True)
            with col_btn[1]:
                st.download_button(
                    "Baixar",
                    data=registro.get('mensagem', ''),
                    file_name=f"briefing_{registro['spe']}_{registro['acs_num']}acs.txt",
                    mime="text/plain",
                    key=f"dl_{registro['id']}",
                    use_container_width=True
                )
            with col_btn[2]:
                if st.button("Excluir", key=f"del_{registro['id']}"):
                    delete_processamento(registro['id'])
                    st.rerun()

            st.divider()

    # Stats
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total", len(registros))
    with col2:
        total_est = sum(len(r.get('classificacao', {}).get('estrangeiros', [])) for r in registros)
        st.metric("Estrangeiros", total_est)
    with col3:
        total_me = sum(len(r.get('classificacao', {}).get('me_epp', [])) for r in registros)
        st.metric("ME/EPP", total_me)


def process_minuta(uploaded_file, planilha_url, force_refresh):
    """Process uploaded minuta"""
    from minuta_reader import extract_pendencias_with_retry
    from cnpj_classifier import classify_pj
    from briefing_composer import compose_briefing

    with tempfile.NamedTemporaryFile(delete=False, suffix=uploaded_file.name) as tmp:
        tmp.write(uploaded_file.getvalue())
        tmp_path = tmp.name

    try:
        pendencias = extract_pendencias_with_retry(tmp_path)

        spe = pendencias.get('spe') or "SPE"
        acs_num = pendencias.get('acs_num') or 1
        data_corte = pendencias.get('data_corte') or "dd/mm/aaaa"

        classificacao = {
            "estrangeiros": pendencias.get('estrangeiros', []),
            "simples_nacional": [],
            "me_epp": [],
            "erros": []
        }

        for empresa in pendencias.get('me_epp', []):
            cnpj = empresa.get('cnpj')
            if cnpj:
                cnpj_clean = ''.join(c for c in cnpj if c.isdigit())
                result = classify_pj(cnpj_clean, force_refresh)
                result['nome'] = empresa['nome']
                if result['bucket'] == 'me_epp':
                    classificacao['me_epp'].append(result)
                elif result['bucket'] == 'erro':
                    classificacao['erros'].append(result)

        for empresa in pendencias.get('simples_nacional', []):
            cnpj = empresa.get('cnpj')
            if cnpj:
                cnpj_clean = ''.join(c for c in cnpj if c.isdigit())
                result = classify_pj(cnpj_clean, force_refresh)
                result['nome'] = empresa['nome']
                if result['bucket'] == 'simples_nacional':
                    classificacao['simples_nacional'].append(result)
                elif result['bucket'] == 'me_epp':
                    classificacao['me_epp'].append(result)
                elif result['bucket'] == 'erro':
                    classificacao['erros'].append(result)

        mensagem = compose_briefing(
            spe=spe, acs_num=acs_num, data_corte=data_corte,
            classificacao=classificacao,
            planilha_assinaturas=planilha_url if planilha_url else None
        )

        return mensagem, spe, acs_num, data_corte, classificacao

    finally:
        os.unlink(tmp_path)


if __name__ == "__main__":
    main()