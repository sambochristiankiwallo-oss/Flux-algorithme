import streamlit as st
import itertools
from pyvis.network import Network
import networkx as nx
import tempfile
import os
import base64

# ----------------------------- Structures -----------------------------

class Constraint:
    def __init__(self, name: str, weight: float = 1.0):
        self.name = name
        self.weight = weight

def compatibility(a: Constraint, b: Constraint) -> float:
    overlap = len(set(a.name.lower()) & set(b.name.lower()))
    return overlap / (max(len(a.name), len(b.name)))

OPPOSITES = {
    ("vite", "lentement"): 1.0,
    ("vite", "coût"): 0.7,
    ("coût", "qualité"): 0.5,
    ("écologie", "pollution"): 1.0,
    ("écologie", "rentabilité"): 0.6,
    ("innovation", "tradition"): 0.8,
    ("simplicité", "richesse"): 0.6,
    ("ergonomie", "esthétique"): 0.5,
    ("flexibilité", "rigidité"): 0.9,
    ("stock", "disponibilité"): 0.7
}

def contradiction(a: Constraint, b: Constraint) -> float:
    for (x, y), strength in OPPOSITES.items():
        if (x in a.name.lower() and y in b.name.lower()) or (y in a.name.lower() and x in b.name.lower()):
            return strength
    return 0.0

def synthesis(a: Constraint, b: Constraint, strength: float) -> str:
    return (f"Compromis ({strength:.1f}) : équilibrer « {a.name} » et « {b.name} » "
            f"pour conserver partiellement les deux bénéfices.")

def flux_score(constraints, alpha=1.0, beta=1.0, gamma=0.7):
    comp_total = 0.0
    contra_total = 0.0
    syntheses = []
    pairs = list(itertools.combinations(constraints, 2))

    for a, b in pairs:
        comp_total += compatibility(a, b) * (a.weight + b.weight) / 2
        c = contradiction(a, b)
        contra_total += c * (a.weight + b.weight) / 2
        if c > 0:
            syntheses.append(synthesis(a, b, c))

    score = alpha * comp_total - beta * contra_total + gamma * len(syntheses)
    return score, comp_total, contra_total, syntheses, pairs

# ----------------------------- Interface Streamlit -----------------------------

st.title("🌊 Algorithme du Flux – Analyse et Visualisation Dynamique")
st.write("Entrez vos contraintes (planification, logistique, design...).")

constraints = []
n = st.number_input("Nombre de contraintes", min_value=2, max_value=10, value=3)

for i in range(n):
    col1, col2 = st.columns([3,1])
    with col1:
        name = st.text_input(f"Contrainte {i+1}", key=f"name_{i}")
    with col2:
        weight = st.slider(f"Poids {i+1}", 0.1, 1.0, 1.0, 0.1, key=f"weight_{i}")
    if name:
        constraints.append(Constraint(name, weight))

if st.button("Analyser avec le Flux"):
    if len(constraints) < 2:
        st.warning("⚠️ Veuillez entrer au moins deux contraintes.")
    else:
        score, comp, contra, synths, pairs = flux_score(constraints)

        st.subheader("📊 Résultats du Flux")
        st.metric("Score global", f"{score:.3f}")
        st.write(f"Compatibilité totale : **{comp:.3f}**")
        st.write(f"Contradictions détectées : **{contra:.3f}**")

        if synths:
            st.subheader("🔄 Synthèses proposées")
            for s in synths:
                st.write("•", s)
        else:
            st.info("Aucune contradiction explicite détectée. Cohérence déjà bonne ✅")

        # ----------------------------- Graphe PyVis -----------------------------
        st.subheader("📈 Visualisation interactive des contraintes")

        G = nx.Graph()

        for c in constraints:
            G.add_node(c.name, size=25 + 40*c.weight)

        for a, b in pairs:
            c_val = compatibility(a, b)
            contra_val = contradiction(a, b)
            if contra_val > 0:
                G.add_edge(a.name, b.name, color="red", value=5*contra_val, title=f"Contradiction {contra_val:.2f}")
            elif c_val > 0:
                G.add_edge(a.name, b.name, color="green", value=3*c_val, title=f"Compatibilité {c_val:.2f}")

        net = Network(height="600px", width="100%", notebook=False)
        net.from_nx(G)

        # Fichier temporaire HTML
        with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tmp_file:
            net.save_graph(tmp_file.name)
            tmp_path = tmp_file.name

        # Lecture et affichage dans Streamlit
        with open(tmp_path, "r", encoding="utf-8") as f:
            html = f.read()
        st.components.v1.html(html, height=600, scrolling=True)

        # ----------------------------- Export téléchargeable -----------------------------
        with open(tmp_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
            href = f'<a href="data:text/html;base64,{b64}" download="flux_graph.html">📥 Télécharger le graphe interactif (HTML)</a>'
            st.markdown(href, unsafe_allow_html=True)

        # Nettoyage du fichier temporaire
        os.remove(tmp_path)
