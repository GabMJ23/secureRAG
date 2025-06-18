import streamlit as st
import time
from components.wizard_state import init_session_state, get_progress
from components.ui_components import render_progress_bar, render_card, render_step_navigation
from components.generator import generate_secure_kit

# Configuration de la page
st.set_page_config(
    page_title="Secure RAG Kit Generator",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS personnalisé pour reproduire l'interface React
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 1rem;
        margin-bottom: 2rem;
    }
    
    .step-card {
        background: white;
        padding: 2rem;
        border-radius: 1rem;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        border: 1px solid #e5e7eb;
        margin: 1rem 0;
    }
    
    .step-icon {
        font-size: 3rem;
        text-align: center;
        margin-bottom: 1rem;
    }
    
    .option-card {
        border: 2px solid #e5e7eb;
        border-radius: 0.75rem;
        padding: 1rem;
        margin: 0.5rem 0;
        cursor: pointer;
        transition: all 0.3s;
        background: white;
    }
    
    .option-card:hover {
        border-color: #3b82f6;
        background: #f8fafc;
    }
    
    .option-card.selected {
        border-color: #3b82f6;
        background: #eff6ff;
    }
    
    .progress-container {
        background: white;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    
    .alert-warning {
        background: #fef3c7;
        border: 1px solid #f59e0b;
        color: #92400e;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    
    .alert-success {
        background: #d1fae5;
        border: 1px solid #10b981;
        color: #065f46;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    
    .generation-container {
        text-align: center;
        padding: 3rem;
    }
    
    .config-summary {
        background: linear-gradient(135deg, #ddd6fe 0%, #e0e7ff 100%);
        padding: 1.5rem;
        border-radius: 0.75rem;
        margin: 1rem 0;
        white-space: pre-line;
        font-family: monospace;
    }
    
    /* Masquer le menu Streamlit */
    #MainMenu {visibility: hidden;}
    .stDeployButton {display:none;}
    footer {visibility: hidden;}
    
    /* Style des boutons */
    .stButton > button {
        background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
        color: white;
        border: none;
        border-radius: 0.5rem;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 25px rgba(0,0,0,0.2);
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Initialisation de l'état
    init_session_state()
    
    # En-tête principal
    st.markdown("""
    <div class="main-header">
        <h1>🚀 Secure RAG Kit Generator</h1>
        <p>Configurez votre moteur RAG sécurisé en quelques étapes</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Navigation par onglets (simulation des étapes)
    if 'current_step' not in st.session_state:
        st.session_state.current_step = 1
    
    # Affichage selon l'étape
    if st.session_state.current_step == 1:
        render_welcome()
    elif st.session_state.current_step == 2:
        render_objective()
    elif st.session_state.current_step == 3:
        render_data_types()
    elif st.session_state.current_step == 4:
        render_security()
    elif st.session_state.current_step == 5:
        render_summary()
    elif st.session_state.current_step == 6:
        render_generating()
    elif st.session_state.current_step == 7:
        render_complete()

def render_welcome():
    st.markdown("""
    <div class="step-card">
        <div class="step-icon">✨</div>
        <h2 style="text-align: center;">Bonjour ! 👋</h2>
        <p style="text-align: center; font-size: 1.2rem; color: #6b7280;">
            Je vais vous aider à générer un environnement IA sécurisé,<br>
            adapté à votre contexte.
        </p>
        <div style="text-align: center; margin: 2rem 0;">
            <span style="background: #dbeafe; color: #1d4ed8; padding: 0.5rem 1rem; border-radius: 2rem; font-size: 0.9rem;">
                ⏱️ Cela prendra environ 3 minutes
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Commencer mon kit personnalisé", use_container_width=True):
            st.session_state.current_step = 2
            st.rerun()

def render_objective():
    # Barre de progression
    render_progress_bar(1, 4)
    
    st.markdown("""
    <div class="step-card">
        <div class="step-icon">🎯</div>
        <h2 style="text-align: center;">Quel est votre objectif avec cette IA ?</h2>
        <p style="text-align: center; color: #6b7280;">Sélectionnez ce que vous cherchez à construire</p>
    </div>
    """, unsafe_allow_html=True)
    
    objectives = [
        {"value": "search", "label": "🔍 Moteur de recherche interne", "desc": "Rechercher dans documents et bases de connaissances"},
        {"value": "assistant", "label": "🤖 Assistant conversationnel métier", "desc": "RH, finance, support client..."},
        {"value": "synthesis", "label": "📝 Génération de synthèses", "desc": "Résumés, rapports, documentation"},
        {"value": "analysis", "label": "📊 Analyse de documents", "desc": "Contrats, PDF, données non-structurées"}
    ]
    
    for obj in objectives:
        selected = st.session_state.get('objective') == obj['value']
        css_class = "option-card selected" if selected else "option-card"
        
        if st.button(f"{obj['label']}\n{obj['desc']}", key=obj['value'], use_container_width=True):
            st.session_state.objective = obj['value']
            st.rerun()
    
    # Navigation
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("← Précédent"):
            st.session_state.current_step = 1
            st.rerun()
    with col3:
        if st.button("Suivant →", disabled=not st.session_state.get('objective')):
            st.session_state.current_step = 3
            st.rerun()

def render_data_types():
    render_progress_bar(2, 4)
    
    st.markdown("""
    <div class="step-card">
        <div class="step-icon">📊</div>
        <h2 style="text-align: center;">Quelles données allez-vous utiliser ?</h2>
        <p style="text-align: center; color: #6b7280;">Cochez les types de données que vous comptez intégrer</p>
    </div>
    """, unsafe_allow_html=True)
    
    if 'data_types' not in st.session_state:
        st.session_state.data_types = []
    
    data_types = [
        {"value": "hr", "label": "👥 RH", "desc": "Fiches de poste, CV, entretiens", "risk": "medium"},
        {"value": "legal", "label": "⚖️ Juridique", "desc": "Contrats, politiques internes", "risk": "high"},
        {"value": "financial", "label": "💰 Financier", "desc": "Budgets, bilans, projections", "risk": "high"},
        {"value": "personal", "label": "🔒 Données personnelles", "desc": "Emails, noms, adresses...", "risk": "high"},
        {"value": "public", "label": "🌐 Données publiques", "desc": "Documentation, FAQ, guides", "risk": "low"},
        {"value": "technical", "label": "⚙️ Technique", "desc": "Code, configurations, logs", "risk": "medium"}
    ]
    
    col1, col2 = st.columns(2)
    
    for i, dtype in enumerate(data_types):
        with col1 if i % 2 == 0 else col2:
            is_selected = dtype['value'] in st.session_state.data_types
            
            risk_color = {"high": "🔴", "medium": "🟡", "low": "🟢"}[dtype['risk']]
            risk_text = {"high": "Sensible", "medium": "Modéré", "low": "Public"}[dtype['risk']]
            
            if st.checkbox(f"{dtype['label']} {risk_color}", value=is_selected, key=f"data_{dtype['value']}"):
                if dtype['value'] not in st.session_state.data_types:
                    st.session_state.data_types.append(dtype['value'])
            else:
                if dtype['value'] in st.session_state.data_types:
                    st.session_state.data_types.remove(dtype['value'])
            
            st.caption(f"{dtype['desc']} - {risk_text}")
    
    # Alerte données sensibles
    if any(dt in st.session_state.data_types for dt in ['personal', 'hr', 'legal']):
        st.markdown("""
        <div class="alert-warning">
            🛡️ <strong>Données sensibles détectées</strong><br>
            Nous activerons automatiquement les mesures de conformité RGPD et de sécurité renforcée.
        </div>
        """, unsafe_allow_html=True)
    
    # Navigation
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("← Précédent", key="back_data"):
            st.session_state.current_step = 2
            st.rerun()
    with col3:
        if st.button("Suivant →", key="next_data", disabled=len(st.session_state.data_types) == 0):
            st.session_state.current_step = 4
            st.rerun()

def render_security():
    render_progress_bar(3, 4)
    
    st.markdown("""
    <div class="step-card">
        <div class="step-icon">🔒</div>
        <h2 style="text-align: center;">Sécurité et conformité</h2>
        <p style="text-align: center; color: #6b7280;">Cochez les mesures que vous jugez nécessaires</p>
    </div>
    """, unsafe_allow_html=True)
    
    if 'security_level' not in st.session_state:
        st.session_state.security_level = []
    
    security_options = [
        {"value": "sso", "label": "🔑 Authentification SSO", "desc": "Azure AD, Google, SAML", "priority": "high"},
        {"value": "audit", "label": "📋 Journalisation des accès", "desc": "Logs auditables et traçabilité", "priority": "high"},
        {"value": "encryption", "label": "🔒 Chiffrement au repos", "desc": "KMS, Vault, clés rotatives", "priority": "high"},
        {"value": "rbac", "label": "👥 Contrôle d'accès par rôle", "desc": "RBAC, politiques granulaires", "priority": "medium"},
        {"value": "gdpr", "label": "🇪🇺 Conformité RGPD complète", "desc": "DPO, registres, procédures", "priority": "high"},
        {"value": "minimal", "label": "⚡ Configuration minimale", "desc": "Pour test rapide", "priority": "low"}
    ]
    
    col1, col2 = st.columns(2)
    
    for i, sec in enumerate(security_options):
        with col1 if i % 2 == 0 else col2:
            is_selected = sec['value'] in st.session_state.security_level
            
            priority_color = {"high": "🔴", "medium": "🟡", "low": "🟢"}[sec['priority']]
            priority_text = {"high": "Essentiel", "medium": "Recommandé", "low": "Optionnel"}[sec['priority']]
            
            if st.checkbox(f"{sec['label']} {priority_color}", value=is_selected, key=f"sec_{sec['value']}"):
                if sec['value'] not in st.session_state.security_level:
                    st.session_state.security_level.append(sec['value'])
            else:
                if sec['value'] in st.session_state.security_level:
                    st.session_state.security_level.remove(sec['value'])
            
            st.caption(f"{sec['desc']} - {priority_text}")
    
    # Navigation
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("← Précédent", key="back_security"):
            st.session_state.current_step = 3
            st.rerun()
    with col3:
        if st.button("Suivant →", key="next_security", disabled=len(st.session_state.security_level) == 0):
            st.session_state.current_step = 5
            st.rerun()

def render_summary():
    render_progress_bar(4, 4)
    
    st.markdown("""
    <div class="step-card">
        <div class="step-icon">📋</div>
        <h2 style="text-align: center;">Récapitulatif de votre configuration</h2>
        <p style="text-align: center; color: #6b7280;">Voici ce que je vais générer pour vous</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Générer le résumé
    summary = "🎯 Configuration personnalisée :\n\n"
    
    if st.session_state.get('objective') == 'search':
        summary += "✅ Moteur de recherche interne optimisé\n"
    elif st.session_state.get('objective') == 'assistant':
        summary += "✅ Assistant conversationnel intelligent\n"
    elif st.session_state.get('objective') == 'analysis':
        summary += "✅ Analyseur de documents avancé\n"
    
    if 'personal' in st.session_state.get('data_types', []):
        summary += "✅ Protection données personnelles (RGPD)\n"
    if 'encryption' in st.session_state.get('security_level', []):
        summary += "✅ Chiffrement bout-en-bout activé\n"
    if 'sso' in st.session_state.get('security_level', []):
        summary += "✅ Authentification SSO configurée\n"
    
    summary += "✅ Configuration sécurisée prête pour déploiement\n"
    
    st.markdown(f"""
    <div class="config-summary">
        {summary}
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style="text-align: center; margin: 2rem 0;">
        <p style="color: #6b7280;">✨ Configuration intelligente prête pour génération</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Générer mon kit sécurisé personnalisé", use_container_width=True):
            st.session_state.current_step = 6
            st.rerun()
    
    # Navigation
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("← Précédent", key="back_summary"):
            st.session_state.current_step = 4
            st.rerun()

def render_generating():
    st.markdown("""
    <div class="generation-container">
        <div class="step-icon">⚡</div>
        <h2>Génération de votre kit intelligent...</h2>
        <p style="color: #6b7280;">Notre IA analyse vos exigences et génère une configuration sur-mesure</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Barre de progression animée
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    steps = [
        "Analyse de vos besoins...",
        "Configuration cloud optimale...",
        "Paramètres de sécurité...",
        "Génération des fichiers...",
        "Validation finale..."
    ]
    
    for i, step in enumerate(steps):
        status_text.text(step)
        progress_bar.progress((i + 1) / len(steps))
        time.sleep(1)
    
    st.session_state.current_step = 7
    st.rerun()

def render_complete():
    st.markdown("""
    <div class="generation-container">
        <div class="step-icon">🎉</div>
        <h2 style="color: #059669;">Kit généré avec succès !</h2>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="alert-success">
        <h4>🎁 Votre kit personnalisé contient :</h4>
        <ul>
            <li>☁️ Configuration Terraform</li>
            <li>🗄️ Setup base vectorielle</li>
            <li>🛡️ Checklist sécurité</li>
            <li>📖 Guide de déploiement</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if st.button("📥 Télécharger le kit", use_container_width=True):
            # Ici vous pouvez déclencher le téléchargement réel
            st.success("Kit téléchargé ! 🎉")
        
        if st.button("🔄 Créer un nouveau kit", use_container_width=True):
            # Reset de l'état
            for key in ['objective', 'data_types', 'security_level', 'current_step']:
                if key in st.session_state:
                    del st.session_state[key]
            st.session_state.current_step = 1
            st.rerun()

if __name__ == "__main__":
    main()
