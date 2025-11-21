import streamlit as st
from ultralytics import YOLO
import tempfile
from PIL import Image
import os
import time
import datetime

# Configuration de la page
st.set_page_config(
    page_title="Détection Poubelle Pleine/Vide",
    page_icon="🗑️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé avec thème bleu et blanc
def local_css():
    st.markdown("""
    <style>
    /* Votre CSS existant */
    .main {
        background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 100%);
        color: white;
    }
    
    .stApp {
        background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 100%);
    }
    
    .main-header {
        font-size: 3rem;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .sub-header {
        font-size: 1.5rem;
        color: white;
        margin-bottom: 1rem;
        font-weight: 600;
    }
    
    .stButton>button {
        background: linear-gradient(135deg, #FFFFFF 0%, #E2E8F0 100%);
        color: #1E3A8A;
        border-radius: 25px;
        padding: 0.75rem 2rem;
        border: none;
        font-weight: bold;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        width: 100%;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.2);
        background: linear-gradient(135deg, #FFFFFF 0%, #F7FAFC 100%);
    }
    
    .card {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 20px;
        padding: 25px;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
        margin: 15px 0;
        border: 1px solid rgba(255, 255, 255, 0.2);
        backdrop-filter: blur(10px);
    }
    
    .success-box {
        background: linear-gradient(135deg, #DCFCE7 0%, #BBF7D0 100%);
        border: 1px solid #22C55E;
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
        color: #166534;
    }
    
    .warning-box {
        background: linear-gradient(135deg, #FEF3C7 0%, #FDE68A 100%);
        border: 1px solid #F59E0B;
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
        color: #92400E;
    }
    
    .info-box {
        background: linear-gradient(135deg, #DBEAFE 0%, #BFDBFE 100%);
        border: 1px solid #3B82F6;
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
        color: #1E40AF;
    }
    
    @media (max-width: 768px) {
        .main-header {
            font-size: 2rem;
        }
        .sub-header {
            font-size: 1.2rem;
        }
        .card {
            padding: 15px;
            margin: 10px 0;
        }
    }
    
    /* Style spécial pour le file_uploader */
    .stFileUploader > div > div {
        border: 2px dashed #3B82F6 !important;
        border-radius: 15px !important;
        background: rgba(255, 255, 255, 0.9) !important;
        padding: 20px !important;
    }
    
    .stFileUploader > div > div:hover {
        border-color: #1E40AF !important;
        background: rgba(255, 255, 255, 1) !important;
    }
    </style>
    """, unsafe_allow_html=True)

local_css()

# Cache le modèle pour améliorer les performances
@st.cache_resource
def load_model(model_path):
    """Charge et cache le modèle YOLO"""
    try:
        model = YOLO(model_path)
        return model
    except Exception as e:
        st.error(f"Erreur lors du chargement du modèle: {str(e)}")
        return None

# === SOLUTION SIMPLIFIÉE POUR L'UPLOAD ===
def check_app_ready():
    """Vérifie si l'application est prête"""
    if 'app_ready' not in st.session_state:
        st.session_state.app_ready = False
        # Petit délai initial pour le démarrage
        time.sleep(2)
        st.session_state.app_ready = True
    return st.session_state.app_ready

# Header principal
st.markdown('<h1 class="main-header">🗑️ Détection Intelligente de Poubelles</h1>', unsafe_allow_html=True)
st.markdown('<h3 style="text-align: center; color: white; margin-bottom: 3rem;">🔍 Analyse automatique : Poubelle Pleine ou Vide</h3>', unsafe_allow_html=True)

# Vérification du statut de l'app
if not check_app_ready():
    st.warning("""
    ⏳ **Initialisation de l'application en cours...**
    
    *Veuillez patienter quelques secondes que le backend se initialise complètement.*
    """)
    st.stop()

# Introduction
with st.container():
    st.markdown("""
    <div class="card">
    <h4 style="color: #1E3A8A; margin-bottom: 1rem;">📋 Comment utiliser cette application :</h4>
    <div style="color: #4B5563;">
    <ol>
        <li style="margin-bottom: 0.5rem;"><strong>Étape 1 :</strong> Téléchargez votre modèle YOLO (optionnel)</li>
        <li style="margin-bottom: 0.5rem;"><strong>Étape 2 :</strong> Importez une image</li>
        <li style="margin-bottom: 0.5rem;"><strong>Étape 3 :</strong> Lancez la détection</li>
    </ol>
    </div>
    </div>
    """, unsafe_allow_html=True)

# Layout en colonnes
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<h3 class="sub-header" style="color: #1E3A8A;">📦 Modèle de Détection</h3>', unsafe_allow_html=True)
    
    # Upload du modèle
    uploaded_model = st.file_uploader(
        "**Téléchargez votre modèle YOLO (.pt)**", 
        type=["pt"],
        help="Importez un modèle YOLO entraîné personnalisé. Si aucun modèle n'est fourni, le modèle par défaut sera utilisé."
    )
    
    model_path = None
    if uploaded_model:
        # Sauvegarder temporairement
        temp_model_path = tempfile.NamedTemporaryFile(delete=False, suffix=".pt").name
        with open(temp_model_path, "wb") as f:
            f.write(uploaded_model.getbuffer())
        model_path = temp_model_path
        st.markdown(f'<div class="success-box">✅ <strong>Modèle personnalisé chargé avec succès !</strong></div>', unsafe_allow_html=True)
    else:
        # Utiliser le modèle par défaut
        DEFAULT_MODEL = "best.pt"
        if os.path.exists(DEFAULT_MODEL):
            model_path = DEFAULT_MODEL
            st.markdown(f'<div class="info-box">ℹ️ <strong>Utilisation du modèle par défaut: {DEFAULT_MODEL}</strong></div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="warning-box">⚠️ <strong>Aucun modèle par défaut trouvé. Veuillez uploader un modèle.</strong></div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<h3 class="sub-header" style="color: #1E3A8A;">🖼️ Image à Analyser</h3>', unsafe_allow_html=True)
    
    # ZONE UPLOAD AMÉLIORÉE
    st.markdown("""
    <div style="text-align: center; margin: 20px 0;">
        <p style="color: #4B5563; font-size: 16px;">
        📁 <strong>Glissez-déposez votre image ici OU cliquez pour parcourir</strong>
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_image = st.file_uploader(
        "**Sélectionner une image**", 
        type=["jpg", "jpeg", "png"],
        help="Formats supportés: JPG, JPEG, PNG. Taille maximale recommandée: 10MB",
        label_visibility="collapsed",
        key="image_uploader"
    )
    
    if uploaded_image is not None:
        try:
            # Vérification que le fichier est valide
            if uploaded_image.size == 0:
                st.error("❌ Le fichier est vide")
            else:
                with st.spinner("🔄 Chargement de l'image en cours..."):
                    time.sleep(0.5)  # Petit délai pour stabilité
                    
                    image = Image.open(uploaded_image)
                    
                    # Redimensionnement pour optimisation
                    max_size = (800, 800)
                    image.thumbnail(max_size, Image.Resampling.LANCZOS)
                    
                    # Affichage de l'image
                    st.image(image, caption="📸 Image importée avec succès", use_column_width=True)
                    
                    # Sauvegarde temporaire
                    temp_image_path = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg").name
                    image.save(temp_image_path, "JPEG", quality=90)
                    
                    st.success(f"✅ Image chargée : {uploaded_image.name} ({uploaded_image.size // 1024} KB)")
                    
        except Exception as e:
            st.error(f"❌ Erreur lors du chargement : {str(e)}")
            st.info("💡 Essayez une autre image ou un format différent")
    
    # Bouton de prédiction
    if uploaded_image and model_path:
        predict_btn = st.button("🚀 Lancer l'Analyse", use_container_width=True, type="primary")
        
        if predict_btn:
            with st.spinner("🔍 Analyse en cours... Cela peut prendre quelques secondes"):
                try:
                    # Charger le modèle
                    model = load_model(model_path)
                    
                    if model is not None:
                        # Effectuer la prédiction
                        results = model(temp_image_path)
                        
                        # Afficher les résultats
                        result_image = results[0].plot()
                        
                        st.markdown('<h3 style="color: #1E3A8A;">📊 Résultats de l\'Analyse</h3>', unsafe_allow_html=True)
                        
                        # Afficher l'image avec détections
                        st.image(result_image, caption="🖼️ Image avec détections", use_column_width=True)
                        
                        # Afficher les informations de détection
                        boxes = results[0].boxes
                        
                        if len(boxes) > 0:
                            cls_id = int(boxes[0].cls[0])
                            cls_name = model.names[cls_id]
                            
                            if "pleine" in cls_name.lower() or "full" in cls_name.lower():
                                st.markdown(f"""
                                <div class="warning-box">
                                <h3 style="color: #92400E; margin-bottom: 1rem;">⚠️ Poubelle Pleine Détectée</h3>
                                <p><strong>Statut :</strong> {cls_name}</p>
                                <p><strong>Recommandation :</strong> Il est temps de vider la poubelle !</p>
                                </div>
                                """, unsafe_allow_html=True)
                            else:
                                st.markdown(f"""
                                <div class="success-box">
                                <h3 style="color: #166534; margin-bottom: 1rem;">✅ Poubelle Vide Détectée</h3>
                                <p><strong>Statut :</strong> {cls_name}</p>
                                <p><strong>Recommandation :</strong> La poubelle peut continuer à être utilisée.</p>
                                </div>
                                """, unsafe_allow_html=True)
                            
                            # Statistiques
                            st.markdown('<h3 style="color: #1E3A8A;">📈 Statistiques de Détection</h3>', unsafe_allow_html=True)
                            col_stat1, col_stat2, col_stat3 = st.columns(3)
                            with col_stat1:
                                st.metric("Objets détectés", len(boxes))
                            with col_stat2:
                                st.metric("Confiance moyenne", f"{boxes.conf.mean():.2f}" if len(boxes.conf) > 0 else "N/A")
                            with col_stat3:
                                st.metric("Classe", cls_name)
                                
                        else:
                            st.markdown(f"""
                            <div class="info-box">
                            <h3 style="color: #1E40AF; margin-bottom: 1rem;">❌ Aucune Poubelle Détectée</h3>
                            <p>Aucune poubelle détectée. Suggestions :</p>
                            <ul>
                                <li>Image plus claire</li>
                                <li>Poubelle bien visible</li>
                                <li>Angle différent</li>
                            </ul>
                            </div>
                            """, unsafe_allow_html=True)
                    
                    # Nettoyage
                    try:
                        os.unlink(temp_image_path)
                        if uploaded_model:
                            os.unlink(temp_model_path)
                    except:
                        pass
                        
                except Exception as e:
                    st.error(f"❌ Erreur lors de l'analyse : {str(e)}")
    
    elif uploaded_image and not model_path:
        st.warning("⚠️ Veuillez d'abord charger un modèle YOLO.")
    
    # Bouton de secours
    st.markdown("---")
    if st.button("🔄 Réinitialiser l'upload", key="reset_upload"):
        st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

# Section information
st.markdown("---")
st.markdown("### 💡 À propos de cette application")
st.markdown("""
<div class="card">
<h4 style="color: #1E3A8A; margin-bottom: 1rem;">Technologie de Détection Intelligente</h4>
<div style="color: #4B5563;">
<p>Cette application utilise l'IA pour détecter automatiquement si une poubelle est pleine ou vide.</p>
<p><strong>Technologies :</strong> YOLO pour la détection d'objets en temps réel.</p>
<p><strong>Usage :</strong> Optimisation de la collecte des déchets.</p>
</div>
</div>
""", unsafe_allow_html=True)