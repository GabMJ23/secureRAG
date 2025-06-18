import streamlit as st
import time
import zipfile
import tempfile
import os
from datetime import datetime
from jinja2 import Template

# Configuration de la page
st.set_page_config(
    page_title="Secure RAG Kit Generator",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS personnalisé
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

# Fonctions utilitaires
def init_session_state():
    """Initialise l'état de session"""
    if 'current_step' not in st.session_state:
        st.session_state.current_step = 1
    if 'objective' not in st.session_state:
        st.session_state.objective = ''
    if 'data_types' not in st.session_state:
        st.session_state.data_types = []
    if 'security_level' not in st.session_state:
        st.session_state.security_level = []

def render_progress_bar(current_step, total_steps):
    """Affiche une barre de progression"""
    progress_percentage = (current_step / total_steps) * 100
    
    st.markdown(f"""
    <div class="progress-container">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
            <span style="font-size: 0.9rem; color: #6b7280;">Étape {current_step} sur {total_steps}</span>
            <span style="font-size: 0.9rem; color: #6b7280;">{int(progress_percentage)}% terminé</span>
        </div>
        <div style="width: 100%; background-color: #e5e7eb; border-radius: 1rem; height: 0.5rem;">
            <div style="
                width: {progress_percentage}%; 
                background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%); 
                border-radius: 1rem; 
                height: 100%; 
                transition: width 0.3s ease;
            "></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def generate_terraform_config(config):
    """Génère la configuration Terraform"""
    template = Template("""
# Configuration Terraform pour RAG Sécurisé
# Généré automatiquement par Secure RAG Kit Generator

terraform {
  required_version = ">= 1.0"
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
  }
}

provider "azurerm" {
  features {}
}

# Resource Group
resource "azurerm_resource_group" "rag_rg" {
  name     = "rg-secure-rag-{{ objective }}"
  location = "West Europe"
  
  tags = {
    Environment = "production"
    Purpose     = "SecureRAG"
    DataTypes   = "{{ data_types_str }}"
  }
}

{% if 'encryption' in security_level %}
# Key Vault pour la gestion des clés
resource "azurerm_key_vault" "rag_kv" {
  name                = "kv-secure-rag-${random_string.suffix.result}"
  location            = azurerm_resource_group.rag_rg.location
  resource_group_name = azurerm_resource_group.rag_rg.name
  tenant_id          = data.azurerm_client_config.current.tenant_id
  sku_name           = "premium"

  enabled_for_deployment          = true
  enabled_for_disk_encryption     = true
  enabled_for_template_deployment = true
}
{% endif %}

# Azure OpenAI Service
resource "azurerm_cognitive_account" "openai" {
  name                = "openai-secure-rag-${random_string.suffix.result}"
  location            = azurerm_resource_group.rag_rg.location
  resource_group_name = azurerm_resource_group.rag_rg.name
  kind                = "OpenAI"
  sku_name           = "S0"
  
  tags = {
    Environment = "production"
    DataSensitivity = "{{ data_sensitivity }}"
  }
}

resource "random_string" "suffix" {
  length  = 8
  special = false
  upper   = false
}

data "azurerm_client_config" "current" {}

# Outputs
output "resource_group_name" {
  value = azurerm_resource_group.rag_rg.name
}

output "openai_endpoint" {
  value = azurerm_cognitive_account.openai.endpoint
  sensitive = true
}
""")
    
    data_sensitivity = "High" if any(dt in config.get('data_types', []) for dt in ['personal', 'financial', 'legal']) else "Medium"
    
    return template.render(
        objective=config.get('objective', 'general'),
        data_types_str=','.join(config.get('data_types', [])),
        security_level=config.get('security_level', []),
        data_sensitivity=data_sensitivity
    )

def generate_weaviate_config(config):
    """Génère la configuration Weaviate"""
    return f"""
# Configuration Weaviate pour RAG Sécurisé
version: '3.8'

services:
  weaviate:
    image: semitechnologies/weaviate:latest
    ports:
      - "8080:8080"
    environment:
      QUERY_DEFAULTS_LIMIT: 25
      AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED: '{"false" if "sso" in config.get("security_level", []) else "true"}'
      PERSISTENCE_DATA_PATH: '/var/lib/weaviate'
      DEFAULT_VECTORIZER_MODULE: 'text2vec-openai'
      ENABLE_MODULES: 'text2vec-openai,qna-openai'
      OPENAI_APIKEY: '${{OPENAI_API_KEY}}'
    volumes:
      - weaviate_data:/var/lib/weaviate

volumes:
  weaviate_data:
"""

def generate_readme(config):
    """Génère le README"""
    objective_labels = {
        'search': 'Moteur de recherche interne',
        'assistant': 'Assistant conversationnel',
        'synthesis': 'Génération de synthèses',
        'analysis': 'Analyse de documents'
    }
    
    data_type_labels = {
        'hr': 'RH', 'legal': 'Juridique', 'financial': 'Financier',
        'personal': 'Personnel', 'public': 'Public', 'technical': 'Technique'
    }
    
    return f"""
# 🚀 Secure RAG Kit - Configuration Personnalisée

## 📋 Vue d'ensemble

Ce kit contient une configuration complète et sécurisée pour déployer un système RAG.

### 🎯 Configuration Générée

- **Objectif** : {objective_labels.get(config.get('objective'), 'Non défini')}
- **Types de données** : {', '.join([data_type_labels.get(dt, dt) for dt in config.get('data_types', [])])}
- **Sécurité** : {', '.join(config.get('security_level', []))}

## 📦 Contenu du Kit

- 🏗️ main.tf - Infrastructure Terraform
- 🗄️ weaviate-config.yaml - Configuration base vectorielle  
- 📄 README.md - Guide d'utilisation

## 🚀 Démarrage Rapide

1. Configurer les variables d'environnement Azure
2. Déployer avec Terraform : `terraform init && terraform apply`
3. Lancer Weaviate : `docker-compose -f weaviate-config.yaml up -d`

## 🛡️ Sécurité

{'⚠️ Configuration avec données sensibles - Respectez les obligations RGPD' if any(dt in config.get('data_types', []) for dt in ['personal', 'financial']) else '✅ Configuration sécurisée standard'}

## 📞 Support

- Support technique : support@secure-rag-kit.com
- Questions sécurité : security@secure-rag-kit.com

*Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')} par Secure RAG Kit Generator*
"""

def generate_secure_kit(config):
    """Génère un kit RAG sécurisé"""
    with tempfile.TemporaryDirectory() as temp_dir:
        files_generated = []
        
        # 1. Configuration Terraform
        terraform_content = generate_terraform_config(config)
        terraform_path = os.path.join(temp_dir, "main.tf")
        with open(terraform_path, 'w', encoding='utf-8') as f:
            f.write(terraform_content)
        files_generated.append(("main.tf", terraform_path))
        
        # 2. Configuration Weaviate
        weaviate_content = generate_weaviate_config(config)
        weaviate_path = os.path.join(temp_dir, "weaviate-config.yaml")
        with open(weaviate_path, 'w', encoding='utf-8') as f:
            f.write(weaviate_content)
        files_generated.append(("weaviate-config.yaml", weaviate_path))
        
        # 3. README
        readme_content = generate_readme(config)
        readme_path = os.path.join(temp_dir, "README.md")
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        files_generated.append(("README.md", readme_path))
        
        # Créer le fichier ZIP
        zip_path = os.path.join(temp_dir, "secure-rag-kit.zip")
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for filename, filepath in files_generated:
                zipf.write(filepath, filename)
        
        # Lire le contenu du ZIP
        with open(zip_path, 'rb') as f:
            zip_content = f.read()
        
        return zip_content

def get_config_summary():
    """Génère un résumé de la configuration"""
    summary = "🎯 Configuration personnalisée :\n\n"
    
    objective_map = {
        'search': '✅ Moteur de recherche interne optimisé',
        'assistant': '✅ Assistant conversationnel intelligent',
        'synthesis': '✅ Générateur de synthèses automatique',
        'analysis': '✅ Analyseur de documents avancé'
    }
    
    if st.session_state.get('objective'):
        summary += objective_map.get(st.session_state.objective, '') + '\n'
    
    data_types = st.session_state.get('data_types', [])
    if 'personal' in data_types:
        summary += '✅ Protection données personnelles (RGPD)\n'
    if 'financial' in data_types:
        summary += '✅ Conformité financière renforcée\n'
    
    security = st.session_state.get('security_level', [])
    if 'encryption' in security:
        summary += '✅ Chiffrement bout-en-bout activé\n'
    if 'sso' in security:
        summary += '✅ Authentification SSO configurée\n'
    if 'audit' in security:
        summary += '✅ Journalisation complète des accès\n'
    
    summary += '\n✅ Configuration sécurisée prête pour déploiement'
    
    return summary

# Pages du wizard
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
    
    summary = get_config_summary()
    
    st.markdown(f"""
    <div class="config-summary">
        {summary}
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
    <div style="text-align: center; padding: 3rem;">
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
    <div style="text-align: center; padding: 3rem;">
        <div class="step-icon">🎉</div>
        <h2 style="color: #059669;">Kit généré avec succès !</h2>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style="background: #d1fae5; border: 1px solid #10b981; color: #065f46; padding: 1rem; border-radius: 0.5rem; margin: 1rem 0;">
        <h4>🎁 Votre kit personnalisé contient :</h4>
        <ul>
            <li>☁️ Configuration Terraform</li>
            <li>🗄️ Setup base vectorielle</li>
            <li>📖 Guide de déploiement</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # Génération du kit
    config = {
        'objective': st.session_state.get('objective', ''),
        'data_types': st.session_state.get('data_types', []),
        'security_level': st.session_state.get('security_level', [])
    }
    
    zip_content = generate_secure_kit(config)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.download_button(
            label="📥 Télécharger le kit",
            data=zip_content,
            file_name="secure-rag-kit.zip",
            mime="application/zip",
            use_container_width=True
        )
        
        if st.button("🔄 Créer un nouveau kit", use_container_width=True):
            # Reset de l'état
            for key in ['objective', 'data_types', 'security_level', 'current_step']:
                if key in st.session_state:
                    del st.session_state[key]
            st.session_state.current_step = 1
            st.rerun()

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

if __name__ == "__main__":
    main()
