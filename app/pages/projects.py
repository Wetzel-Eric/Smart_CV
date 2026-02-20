# app/pages/projects.py
import streamlit as st
from pathlib import Path
import json

st.title("🚀 Projets Professionnels")

# Charger les données JSON
try:
    with open('data/projects.json', 'r', encoding='utf-8') as f:
        projects = json.load(f)["projets"]
except FileNotFoundError:
    st.error("Fichier projects.json introuvable!")
    st.stop()
except json.JSONDecodeError:
    st.error("Erreur de lecture du fichier JSON!")
    st.stop()
except KeyError:
    st.error("Format de fichier JSON invalide!")
    st.stop()

# Chemin vers le dossier contenant les images
image_dir = Path("data/screenshot_projects")

# Style CSS pour améliorer l'affichage
st.markdown("""
<style>
    .project-card {
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 30px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .project-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 15px;
    }
    .project-title {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2a5885;
    }
    .project-role {
        font-size: 1.1rem;
        color: #666;
        font-style: italic;
    }
    .project-description {
        line-height: 1.6;
        margin-bottom: 15px;
    }
    .project-image {
        width: 100%;
        max-width: 100%;
        border-radius: 5px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-top: 15px;
    }
    .tech-badge {
        display: inline-block;
        padding: 3px 8px;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: bold;
        margin-right: 8px;
        margin-bottom: 8px;
        background-color: #e3f2fd;
        color: #1976d2;
    }
    .competence-badge {
        display: inline-block;
        padding: 3px 8px;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: bold;
        margin-right: 8px;
        margin-bottom: 8px;
        background-color: #e8f5e9;
        color: #43a047;
    }
</style>
""", unsafe_allow_html=True)

# Affichage de chaque projet dans l'ordre du JSON
for project in projects:
    with st.container():
        st.markdown('<div class="project-card">', unsafe_allow_html=True)

        # En-tête avec titre et rôle
        st.markdown(f"""
        <div class="project-header">
            <div class="project-title">{project['titre'].replace('_', ' ').title()}</div>
            <div class="project-role">{project['role']}</div>
        </div>
        """, unsafe_allow_html=True)

        # Description courte
        st.markdown(f'<div class="project-description">{project["description_courte"]}</div>', unsafe_allow_html=True)

        # Solution (si disponible)
        if "solution" in project and project["solution"] and project["solution"] != "solutions TBD":
            st.markdown(f"**Solution:** {project['solution']}")

        # Technologies utilisées (en ligne horizontale)
        if "technos" in project and project["technos"]:
            st.markdown("**Technologies:**")
            techs_html = " ".join([f'<span class="tech-badge">{tech}</span>' for tech in project["technos"]])
            st.markdown(techs_html, unsafe_allow_html=True)

        # Compétences mises en œuvre (en ligne horizontale)
        if "competences" in project and project["competences"]:
            st.markdown("**Compétences:**")
            comps_html = " ".join([f'<span class="competence-badge">{comp}</span>' for comp in project["competences"]])
            st.markdown(comps_html, unsafe_allow_html=True)

        # Image du projet (si elle existe)
        if "image" in project and project["image"]:
            image_path = image_dir / Path(project["image"]).name
            if image_path.exists():
                st.image(str(image_path), width=9999)  # Pleine largeur
            else:
                st.warning(f"Image manquante: {project['image']}")

        st.markdown('</div>', unsafe_allow_html=True)
        st.divider()

"""
# Statistiques
st.sidebar.markdown("### Statistiques")
st.sidebar.markdown(f"**Total:** {len(projects)} projets")

# Compter les technologies les plus utilisées
tech_counts = {}
for project in projects:
    if "technos" in project:
        for tech in project["technos"]:
            tech_counts[tech] = tech_counts.get(tech, 0) + 1

if tech_counts:
    st.sidebar.markdown("**Technologies les plus utilisées:**")
    for tech, count in sorted(tech_counts.items(), key=lambda x: x[1], reverse=True):
        st.sidebar.markdown(f"- {tech}: {count} projet(s)")

# Compter les rôles
role_counts = {}
for project in projects:
    role = project.get("role", "Non spécifié")
    role_counts[role] = role_counts.get(role, 0) + 1

if role_counts:
    st.sidebar.markdown("**Rôles occupés:**")
    for role, count in role_counts.items():
        st.sidebar.markdown(f"- {role}: {count} projet(s)")
"""