import streamlit as st
import pandas as pd
import plotly.express as px

#Configuration globale
st.set_page_config(page_title="Dashboard Arcom 2024", layout="wide")
st.title("Les Français et l'Information - ARCOM 2024")

#Chargement et traitement des données locales
@st.cache_data
def load_and_process_data(file_path):
    try:
        df = pd.read_excel(file_path, sheet_name="Résultats")
        try:
            df_texts = pd.read_excel(file_path, sheet_name="TEXTS")
        except ValueError:
            df_texts = None 
            
        #  NETTOYAGE POIDS 
        if 'POIDS03' in df.columns:
            df['POIDS03'] = df['POIDS03'].astype(str).str.replace(',', '.', regex=False)
            df['POIDS03'] = pd.to_numeric(df['POIDS03'], errors='coerce').fillna(1.0)
        
        # LOGIQUE GROUPE COMPLOT 
        BonnesReponses = [2, 1, 2, 2, 2, 1, 2, 2]
        scores_complot = []
        
        for index, row in df.iterrows():
            score = 0
            for i in range(1, 9):
                col_name = f"COMPLOT2_R_{i}"
                if col_name in df.columns and pd.notna(row[col_name]):
                    if int(row[col_name]) != BonnesReponses[i-1]:
                        score += 1
            scores_complot.append(score)
            
        df['Score_Complot'] = scores_complot
        
        groupes_int = []  
        groupes_str = []  
        
        for score in scores_complot:
            if score == 0:
                groupes_int.append(1)
                groupes_str.append("1. Non complotistes (0)")
            elif 0 < score <= 2: 
                groupes_int.append(2)
                groupes_str.append("2. Peu complotistes (1,2)")
            else:
                groupes_int.append(3)
                groupes_str.append("3. Complotistes (3+)")
                
        df['Groupe_Complot'] = groupes_int
        df['Groupe'] = groupes_str
        
        # MAPPING POLITIQUE
        def categoriser_candidat(val):
            try: val = int(val)
            except: return "Blanc/Abstention/Autre"
            if val in [3, 4]: return "Droite Radicale"
            if val in [2, 12]: return "Droite Modérée"
            if val in [1, 8]: return "Centre"
            if val in [5, 11]: return "Gauche Modérée"
            if val in [6, 9, 7, 10, 18]: return "Gauche Radicale"
            return "Blanc/Abstention/Autre"

        if 'PP3_R' in df.columns:
            df['Categorie_Politique'] = df['PP3_R'].apply(categoriser_candidat)

        return df, df_texts

    except FileNotFoundError:
        st.error(f"Le fichier '{file_path}' est introuvable.")
        return None, None

# 3. Initialisation
file_path = 'les-francais-et-l-information-arcom-2024-datamap.xlsx'
df, df_texts = load_and_process_data(file_path)

if df is not None:
    #  BARRE LATÉRALE : FILTRE GLOBAL
    st.sidebar.header("Paramètres")
    groupes_selectionnes = st.sidebar.multiselect(
        "Afficher les groupes pour les analyses :", 
        options=[1, 2, 3], 
        default=[1, 2, 3],
        format_func=lambda x: {1: "1. Non complotistes", 2: "2. Peu complotistes", 3: "3. Complotistes"}[x]
    )
    
    df_filtered = df[df['Groupe_Complot'].isin(groupes_selectionnes)].copy()

    # STRUCTURE DES ONGLETS
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Accueil", 
        "Socio-démographie", 
        "Rapport à l'information", 
        "Politique", 
        "Sources d'information",
    ])
    
    # ==========================================
    # ONGLET 1 : ACCUEIL
    # ==========================================
    with tab1:
        st.header("Méthodologie : L'adhésion aux théories du complot")
        st.write("Ce graphique montre la distribution de l'adhésion aux thèses complotistes au sein de la population. Selon nos données, près de 75% des Français interrogés adhèrent à au moins une thèse complotiste. En divisant l'échantillon en trois groupes distincts (Score 0, 1 à 2, et 3 ou plus), on observe qu'une majorité se tient à l'écart de ces théories ou n'y adhère que faiblement, mais qu'un noyau dur et significatif y adhère fortement. Cette segmentation permet de comprendre que la désinformation ne touche pas la population de manière homogène.")
        compte_scores = df.groupby('Score_Complot')['POIDS03'].sum().reindex(range(9), fill_value=0).reset_index()
        compte_scores.columns = ['Score', 'Effectif']
        
        colors_list = ["green"] + ["orange"]*2 + ["red"]*6
        
        total_grp1 = df[df['Groupe_Complot'] == 1]['POIDS03'].sum()
        total_grp2 = df[df['Groupe_Complot'] == 2]['POIDS03'].sum()
        total_grp3 = df[df['Groupe_Complot'] == 3]['POIDS03'].sum()
        
        fig_global = px.bar(
            compte_scores, 
            x='Score', 
            y='Effectif',
            title="Répartition des participants selon le nombre de théories du complot crues",
            labels={'Score': "Nombre de théories crues", 'Effectif': "Effectif (pondéré)"}
        )
        fig_global.update_traces(marker_color=colors_list)
        fig_global.update_layout(xaxis=dict(tickmode='linear', tick0=0, dtick=1))
        
        st.plotly_chart(fig_global, use_container_width=True)
        
        st.markdown(f"""
        <div style="background-color: #f0f2f6; padding: 15px; border-radius: 10px; margin-bottom: 25px;">
            <strong>Légende et Effectifs :</strong><br>
            <span style="color: green;">⬤</span> <strong>Non complotistes (Groupe 1)</strong> : Score 0 — <em>{int(total_grp1):,} personnes</em><br>
            <span style="color: orange;">⬤</span> <strong>Peu complotistes (Groupe 2)</strong> : Score 1 à 2 — <em>{int(total_grp2):,} personnes</em><br>
            <span style="color: red;">⬤</span> <strong>Complotistes (Groupe 3)</strong> : Score 3 à 8 — <em>{int(total_grp3):,} personnes</em>
        </div>
        """, unsafe_allow_html=True)

        st.warning("Concernant la répartition des groupes, nous avons décidé d’en créer 3 afin d’avoir une différence marquée entre les groupes. **La dénomination des groupes (“Complotistes”, “Pas complotistes”...) n’est pas à prendre au pied de la lettre.** Elle a été choisie pour un souci de compréhension et de lisibilité du rapport, mais nous n’affirmons aucunement que nous sommes légitimes pour mettre définitivement des gens dans des groupes. **Il s’agit donc de prendre ce rapport avec du recul et de l’esprit critique, d’autant plus que nous ne sommes pas statisticiens et que nous ne pouvons pas affirmer que nos résultats soient tous statistiquement significatifs.**")
        st.write("Voici la liste des théories du complot proposées aux répondants. L'Arcom a ensuite pris le parti de les catégoriser en Vraies (vert) ou Fausses (rouge) :")
        
        theories = [
    ("1. Les Américains n’ont jamais marché sur la lune", False),
    ("2. L’épidémie Covid s’est répandue accidentellement depuis la ville de Wuhan en Chine", True),
    ("3. Il existe un complot juif à l’échelle mondiale", False),
    ("4. C’est la CIA qui a abattu les tours jumelles à New York le 11 septembre", False),
    ("5. Le gouvernement est de mèche avec l’industrie pharmaceutique pour cacher la nocivité des vaccins", False),
    ("6. Lady Diana est décédée dans un accident de voiture sous le Pont de l’Alma", True),
    ("7. Le réchauffement climatique actuel n’est pas causé par l’homme", False),
    ("8. Donald Trump est le véritable vainqueur des dernières élections américaines", False),
]

        for texte, verite in theories:
            if verite:
                st.markdown(f"<p style='color:green'>{texte}</p>", unsafe_allow_html=True)
            else:
                st.markdown(f"<p style='color:red'>{texte}</p>", unsafe_allow_html=True)
        
    # ==========================================
    # APPEL DES AUTRES ONGLETS
    # ==========================================
    if not df_filtered.empty:
        with tab2:
            import page_sociodemo
            page_sociodemo.render_page(df_filtered, df_texts)
            
        with tab3:
            import page_habitudes
            page_habitudes.render_page(df_filtered, df_texts)
            
        with tab4:
            import page_politique
            page_politique.render_page(df_filtered)
            
        with tab5:
            import page_sources
            page_sources.render_page(df_filtered, df_texts)
    else:
        for t in [tab2, tab3, tab4, tab5]:
            with t:
                st.warning("⚠️ Aucun groupe sélectionné. Veuillez sélectionner au moins un groupe dans la barre latérale.")