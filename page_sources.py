import streamlit as st
import pandas as pd
import plotly.express as px

# Fonctions utilitaires

def get_mapping(df_texts, variable_name):
    if df_texts is None:
        return {}
        
    subset = df_texts[df_texts['NAME'] == variable_name].copy()
    subset = subset[subset['CODE'].notna()]
    
    mapping = {}
    for _, row in subset.iterrows():
        try:
            code = int(float(row['CODE']))
            label = str(row['FR:L'])
            mapping[code] = label
        except:
            continue
    return mapping

def plot_weighted_bar(dataframe, var_code, var_name, df_texts, manual_map=None):
    if manual_map:
        mapping = manual_map
    else:
        mapping = get_mapping(df_texts, var_code)
    
    temp_df = dataframe.copy()
    if var_code not in temp_df.columns:
        st.warning(f"La colonne {var_code} n'est pas présente dans les données.")
        return None
        
    temp_df[var_code] = pd.to_numeric(temp_df[var_code], errors='coerce').fillna(-99).astype(int)
    
    mask = temp_df[var_code] != -99
    data_clean = temp_df[mask]
    
    if data_clean.empty:
        st.warning("Pas de données valides pour cette variable.")
        return None

    ct = pd.crosstab(
        index=data_clean['Groupe'],
        columns=data_clean[var_code],
        values=data_clean['POIDS03'],
        aggfunc='sum',
        normalize='index'
    ) * 100
    
    ct_long = ct.reset_index().melt(id_vars='Groupe', var_name='Code_Reponse', value_name='Pourcentage')
    
    codes_tries = sorted(data_clean[var_code].unique())
    labels_ordonnes = [mapping.get(c, str(c)) for c in codes_tries]
    
    # Application des labels finaux
    ct_long['Réponse'] = ct_long['Code_Reponse'].map(mapping).fillna(ct_long['Code_Reponse'].astype(str))
    
    # Graphique avec gradation inversée
    fig = px.bar(
        ct_long, 
        x='Pourcentage', 
        y='Groupe', 
        color='Réponse',
        orientation='h',
        title=f"{var_name}",
        text_auto='.1f',
        color_discrete_sequence=px.colors.sequential.Blues_r,
        category_orders={"Réponse": labels_ordonnes}
    )
    
    fig.update_layout(
        xaxis_title="% (Pondéré)",
        yaxis_title="",
        legend_title="Réponse :",
        height=350,
        bargap=0.3,
        legend=dict(orientation="h", yanchor="bottom", y=-0.5, xanchor="center", x=0.5)
    )
    
    return fig

# Fonction principale

def render_page(df_filtered, df_texts):
    st.header("Sources d'information et Confiance")
    groupes_presents = sorted(df_filtered['Groupe'].unique())
    
    # Dictionnaires de libellés forcés
    map_frequence = {
        1: "Plusieurs fois par jour", 2: "Au moins 1 fois/jour", 
        3: "Au moins 1 fois/semaine", 4: "Au moins 1 fois/mois", 
        5: "Moins souvent", 6: "Jamais"
    }
    
    map_oui_non = {
        1: "Oui", 2: "Non"
    }

    # Types de médias consultés
    st.subheader("1. Fréquence d'information en fonction du support")
    st.markdown("**À quelle fréquence utilisez-vous les canaux suivants pour vous informer ?**")

    dict_news = {
        'NEWS1_R_1': 'Radio (Direct, podcasts, sites/applis des stations)',
        'NEWS1_R_2': 'Télévision (Direct, replay, sites/applis des chaînes)',
        'NEWS1_R_3': 'Presse écrite (Papier)',
        'NEWS1_R_4': 'Presse écrite (Sites internet et applications)',
        'NEWS1_R_5': 'Sites d\'information pure players (Mediapart, Brut, etc.)',
        'NEWS1_R_6': 'Agrégateurs d\'actualité (Google News, Apple News...)',
        'NEWS1_R_7': 'Réseaux sociaux (Facebook, X/Twitter, Instagram...)',
        'NEWS1_R_8': 'Plateformes vidéo (YouTube, TikTok, Twitch...)'
    }

    inv_map_news = {v: k for k, v in dict_news.items()}

    col_sel_news, col_graph_news = st.columns([1, 2])
    with col_sel_news:
        media_choisi = st.selectbox(
            "Sélectionnez un support :", 
            list(dict_news.values()),
            key="select_media"
        )
    
    code_media = inv_map_news[media_choisi]
    
    with col_graph_news:
        fig_media = plot_weighted_bar(df_filtered, code_media, media_choisi, df_texts, manual_map=map_frequence)
        if fig_media:
            st.plotly_chart(fig_media, use_container_width=True)

    st.info("""L'examen de ces huit graphiques met en évidence une corrélation positive entre le degré d'adhésion aux affirmations complotistes et la fréquence de consultation déclarée des différents canaux d'information. Contrairement à l'hypothèse d'un retrait ou d'un évitement médiatique, les données indiquent que les individus du groupe ‘Complotistes’ rapportent une information plus ‘régulière’ que le groupe ‘Non complotistes’.
    
Toutefois, l'ampleur de ces écarts varie de manière significative selon la nature du support. Concernant les médias traditionnels ou historiques (télévision, radio, presse écrite papier), la différence de consommation intensive entre les groupes reste relativement mesurée. La divergence s'accentue nettement lorsque l'on observe les plateformes numériques. Ces résultats suggèrent en effet que les profils les plus complotistes se caractérisent par une information active, plutôt orientée vers des plateformes numériques comme les réseaux sociaux, favorisant une **circulation horizontale des contenus**.""")
    
    st.markdown("---")

    # Confiance dans les sources
    st.subheader("2. Confiance envers les sources d'information")
    st.markdown("**Quel niveau de confiance accordez-vous aux informations provenant de...**")

    # Palette pour la confiance
    couleurs_echelle_map = {
        "Tout à fait confiance": "#4CAF50", "Plutôt confiance": "#8BC34A",
        "Plutôt pas confiance": "#FFC107", "Pas du tout confiance": "#F44336"
    }

    sources_confiance_map = {
        "Journalistes (presse, radio, TV)": "INF3_R_1",
        "Experts (scientifiques, médecins, etc.)": "INF3_R_2",
        "Personnalités politiques du gouvernement": "INF3_R_3",
        "Autres personnalités politiques": "INF3_R_4",
        "Célébrités (chanteurs, sportifs...)": "INF3_R_5",
        "Créateurs de contenus (Influenceurs, Youtubeurs...)": "INF3_R_6",
        "Associations et acteurs de terrain": "INF3_R_7",
        "Anonymes (internet, commentaires)": "INF3_R_8",
        "Vos proches (famille, amis)": "INF3_R_9"
    }

    col_select_inf, col_graph_inf = st.columns([1, 2])
    with col_select_inf:
        source_conf_choisie = st.radio("Sélectionnez une source :", list(sources_confiance_map.keys()), key="radio_confiance")
        col_inf = sources_confiance_map[source_conf_choisie]

    df_inf = df_filtered[df_filtered[col_inf].isin([1, 2, 3, 4])].copy()
    labels_inf = {1: "Tout à fait confiance", 2: "Plutôt confiance", 3: "Plutôt pas confiance", 4: "Pas du tout confiance"}
    df_inf['Reponse'] = df_inf[col_inf].map(labels_inf)

    chart_data_inf = df_inf.groupby(['Groupe', 'Reponse'])['POIDS03'].sum().reset_index()
    total_par_groupe_inf = chart_data_inf.groupby('Groupe')['POIDS03'].transform('sum')
    chart_data_inf['Pourcentage'] = (chart_data_inf['POIDS03'] / total_par_groupe_inf) * 100

    ordre_inf = ["Tout à fait confiance", "Plutôt confiance", "Plutôt pas confiance", "Pas du tout confiance"]

    with col_graph_inf:
        if not chart_data_inf.empty:
            fig_inf = px.bar(
                chart_data_inf, x="Groupe", y="Pourcentage", color="Reponse",
                color_discrete_map=couleurs_echelle_map,
                category_orders={"Reponse": ordre_inf, "Groupe": groupes_presents},
                labels={"Groupe": "Groupe", "Pourcentage": "%"}
            )
            fig_inf.add_hline(y=50, line_dash="dash", line_color="black", annotation_text="Majorité (50%)")
            fig_inf.update_layout(yaxis=dict(range=[0, 100]), title=f"Confiance : {source_conf_choisie}", title_font_size=14, height=350)
            st.plotly_chart(fig_inf, use_container_width=True)
        else:
            st.warning("Pas de données disponibles pour cette source.")

    st.info("""Ces graphiques montrent une vraie asymétrie entre les groupes vis-à-vis de la confiance qu’ils portent envers les sources d’informations, et ce sont peut-être les graphiques les plus intéressants de ce rapport.

D'une part, on observe chez les profils les plus complotistes une érosion marquée de la confiance accordée aux figures d'autorité traditionnelles et institutionnelles : le crédit accordé aux journalistes, aux experts scientifiques, aux politiques ainsi qu'aux associations de terrain s'affaisse nettement en comparaison avec les répondants non complotistes. 

D'autre part, cette défiance verticale semble compensée par une revalorisation des sources horizontales. En effet, le groupe complotiste se distingue par une propension plus élevée à faire confiance aux influenceurs, aux célébrités, et de manière très notable, aux anonymes sur internet. 

Enfin, la sphère familiale/amicale constitue une vraie exception : elle demeure un socle de confiance constant, quelle que soit l'appartenance au groupe.""")
    st.markdown("---")

    st.subheader("3. Propension à payer par type d'abonnement")
    st.markdown("**Avez-vous payé pour l'une de ces sources d'information au cours des 12 derniers mois ?**")

    dict_pay = {
        'PAY_R_1': 'Achat au numéro (Presse papier)',
        'PAY_R_2': 'Achat d\'articles à l\'unité sur internet',
        'PAY_R_3': 'Abonnement (Presse papier)',
        'PAY_R_4': 'Abonnement numérique à un journal/magazine',
        'PAY_R_5': 'Abonnement à un site d\'information pure player',
        'PAY_R_6': 'Don ponctuel ou régulier à un média/journaliste',
        'PAY_R_7': 'Abonnement à une plateforme de créateurs / newsletter payante'
    }
    
    inv_map_pay = {v: k for k, v in dict_pay.items()}

    col_sel_pay, col_graph_pay = st.columns([1, 2])
    with col_sel_pay:
        pay_choisi = st.selectbox(
            "Sélectionnez un type de paiement :", 
            list(dict_pay.values()),
            key="select_pay"
        )
        
    code_pay = inv_map_pay[pay_choisi]
    
    with col_graph_pay:
        fig_pay = plot_weighted_bar(df_filtered, code_pay, pay_choisi, df_texts, manual_map=map_oui_non)
        if fig_pay:
            st.plotly_chart(fig_pay, use_container_width=True)
            
    st.info("""On remarque ici que, de manière assez contre-intuitive, les personnes ‘complotistes’ **paient plus souvent pour s'informer que les ‘non-complotistes’**, mais avec des habitudes de consommation très ciblées.

Il n’y a en effet pas de différence notable sur la presse papier : les deux groupes achètent ces formats traditionnels dans les mêmes proportions. 

C’est sur les médias numériques que l’écart se montre vraiment : Les profils complotistes paient 3 à 5 fois plus que les autres pour acheter des articles en ligne, s'abonner à des médias 100% web, des newsletters ou soutenir des créateurs.

On pourrait peut-être interpréter ces résultats en supposant que cet effort financier traduit la volonté de s'affranchir des médias institutionnels (jugés peu dignes de confiance, comme vu précédemment) pour financer et pérenniser des voix indépendantes, alternatives ou dissidentes.""")