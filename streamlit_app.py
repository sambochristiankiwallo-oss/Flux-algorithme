import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Titre de l'application
st.title("🌊 Algorithme du Flux - Recherche de Cohérence")

# Explication
st.markdown("""
Cette application illustre ton **algorithme du flux de cohérence**.  
Tu peux entrer des données, et l'algorithme va chercher les zones les plus cohérentes.
""")

# Entrée utilisateur : tableau de données
st.subheader("📥 Entrez vos données")
rows = st.number_input("Nombre de lignes :", min_value=2, max_value=20, value=5)
cols = st.number_input("Nombre de colonnes :", min_value=2, max_value=10, value=3)

# Création d’un DataFrame aléatoire
if st.button("🔄 Générer des données aléatoires"):
    data = np.random.rand(rows, cols)
    df = pd.DataFrame(data, columns=[f"Col_{i+1}" for i in range(cols)])
    st.session_state["df"] = df

# Si on a déjà un dataframe
if "df" in st.session_state:
    df = st.session_state["df"]
    st.write("### 📊 Données générées :", df)

    # Algorithme de cohérence (simplifié)
    st.subheader("⚙️ Calcul de cohérence")
    coherence = df.corr()  # matrice de corrélation comme indicateur de cohérence
    st.write("Matrice de cohérence :")
    st.dataframe(coherence)

    # Visualisation graphique dynamique
    st.subheader("📈 Visualisation")
    fig, ax = plt.subplots()
    cax = ax.matshow(coherence, cmap="coolwarm")
    fig.colorbar(cax)
    ax.set_xticks(range(len(coherence.columns)))
    ax.set_yticks(range(len(coherence.columns)))
    ax.set_xticklabels(coherence.columns)
    ax.set_yticklabels(coherence.columns)
    st.pyplot(fig)

    st.success("✅ Analyse de cohérence terminée !")
else:
    st.info("Clique sur **Générer des données aléatoires** pour commencer.")
