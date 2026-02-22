# app/pages/recommendations.py
import streamlit as st
from pathlib import Path
import json

st.title("💡 Recommandations Professionnelles")

# Charger les données JSON
try:
    with open('data/recommandations.json', 'r', encoding='utf-8') as f:
        recommendations = json.load(f)
except FileNotFoundError:
    st.error("Fichier recommandations.json introuvable!")
    st.stop()
except json.JSONDecodeError:
    st.error("Erreur de lecture du fichier JSON!")
    st.stop()

# Chemin vers le dossier contenant les images
image_dir = Path("data/screenshot_reco")

# Style CSS pour améliorer l'affichage
st.markdown("""
<style>
    .recommendation-card {
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 30px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .recommendation-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 15px;
    }
    .recommendation-name {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2a5885;
    }
    .recommendation-title {
        font-size: 1.1rem;
        color: #666;
        font-style: italic;
    }
    .recommendation-company {
        font-size: 1.1rem;
        font-weight: bold;
        color: #e74c3c;
    }
    .recommendation-content {
        line-height: 1.6;
        margin-bottom: 15px;
    }
    .recommendation-image {
        width: 100%;
        max-width: 100%;
        border-radius: 5px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-top: 15px;
    }
    .relation-badge {
        display: inline-block;
        padding: 3px 8px;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: bold;
        text-transform: uppercase;
    }
    .client {
        background-color: #e1f5fe;
        color: #0288d1;
    }
    .collègue {
        background-color: #e8f5e9;
        color: #43a047;
    }
</style>
""", unsafe_allow_html=True)

# Affichage de chaque recommandation
for reco in recommendations:
    with st.container():
        st.markdown('<div class="recommendation-card">', unsafe_allow_html=True)

        # En-tête avec nom, titre et entreprise
        st.markdown(f"""
        <div class="recommendation-header">
            <div>
                <div class="recommendation-name">{reco['nom']}</div>
                <div class="recommendation-title">{reco['titre']}</div>
            </div>
            <div class="recommendation-company">{reco['entreprise']}</div>
        </div>
        """, unsafe_allow_html=True)

        # Badge de relation
        relation_class = "client" if reco['relation'] == "client" else "collègue"
        st.markdown(f'<span class="relation-badge {relation_class}">{reco["relation"]}</span>', unsafe_allow_html=True)

        # Contenu de la recommandation
        #st.markdown(f'<div class="recommendation-content">{reco["contenu"]}</div>', unsafe_allow_html=True)

        # Image de la recommandation (si elle existe)
        if "screenshot" in reco and reco["screenshot"]:
            image_path = image_dir / Path(reco["screenshot"]).name
            if image_path.exists():
                st.image(str(image_path), width=9999)  # Pleine largeur
            else:
                st.warning(f"Image manquante: {reco['screenshot']}")

        st.markdown('</div>', unsafe_allow_html=True)
        st.divider()

# Statistiques
st.sidebar.markdown("### Statistiques")
st.sidebar.markdown(f"**Total:** {len(recommendations)} recommandations")
st.sidebar.markdown(f"**Clients:** {len([r for r in recommendations if r['relation'] == 'client'])}")
st.sidebar.markdown(f"**Collègues:** {len([r for r in recommendations if r['relation'] == 'collègue'])}")
