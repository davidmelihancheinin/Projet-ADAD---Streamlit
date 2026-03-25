import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import seaborn as sns

# Fonctions utilitaires

def get_mapping(df_texts, variable_name):
    """Récupère le dictionnaire {code: label} depuis l'onglet TEXTS."""
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
    """Génère un graphique Plotly horizontal pondéré."""
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
    
    ct_long['Réponse'] = ct_long['Code_Reponse'].map(mapping).fillna(ct_long['Code_Reponse'].astype(str))
    
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
    st.header("Rapport à l'information")
    st.markdown("Cette page concerne le rapport à l'information des 3 groupes : est-ce qu'elle les intéresse, sur quels sujets ? Enfin, sont-ils prêts à payer pour y avoir accès ? On notera qu'il faut prendre les résultats avec des pincettes, car on demande avant tout aux répondants un 'sentiment', un 'intérêt global' : il ne faut pas forcément conclure que cela se répercute dans la consommation réelle de l'information. Pour finir, on retient globalement de cette page que le groupe 3 est assez polarisé, car il contient à la fois une base de répondants peu intéressés par l'information, et à la fois une base très engagée et intéressée par une variété de sujets.")
    
    map_interet = {
        1: "Très intéressé·e", 2: "Assez intéressé·e", 
        3: "Peu intéressé·e", 4: "Pas du tout intéressé·e"
    }
    
    map_sentiment = {
        1: "Oui, tout à fait", 2: "Oui, plutôt", 
        3: "Non, pas vraiment", 4: "Non, pas du tout"
    }
    
    map_frequence = {
        1: "Plusieurs fois par jour", 2: "Au moins 1 fois/jour", 
        3: "Au moins 1 fois/semaine", 4: "Au moins 1 fois/mois", 
        5: "Moins souvent", 6: "Jamais"
    }

    st.subheader("1. Intérêt pour l'information")

    fig_interet = plot_weighted_bar(df_filtered, 'INT1_R', "Quel est votre niveau d’intérêt pour l’information en général, qu’elle porte sur la politique, l’international, la société, le sport, la culture ... ?", df_texts, manual_map=map_interet)
    if fig_interet:
        st.plotly_chart(fig_interet, use_container_width=True, key="chart_interet_global")
    
    st.info("Ce graphique illustre bien les réponses parfois paradoxales du sondage, et dont l'interprétation est compliquée. On trouve ici que le groupe 1 est plus intéressé par l'actualité en général, alors même que ce n'est pas le groupe qui en consomme le plus. On note toutefois qu'il y a un groupe très intéressé par l'information dans le groupe 1, que l'on retrouvera dans le graphique ci-dessous.")
    st.markdown("---")
    
    st.subheader("2. Sentiment d'être informé selon les thèmes")
    st.markdown("**Avez-vous le sentiment d'être bien informé sur les sujets suivants ?**")
    
    dict_sentiment = {
        "Actualité Internationale": "INT3_R_1",
        "Actualité nationale": "INT3_R_2",
        "Actualité locale / régionale": "INT3_R_3",
        "Politique": "INT3_R_4",
        "Économie": "INT3_R_5",
        "Société (justice, emploi, faits divers…)": "INT3_R_6",
        "Environnement, climat, écologie": "INT3_R_7",
        "Santé, mode de vie, bien-être": "INT3_R_8",
        "Culture et divertissement": "INT3_R_9",
        "Sport": "INT3_R_10",
        "People, vie des stars, interviews des célébrités": "INT3_R_11",
        "Sciences et technologies": "INT3_R_12"
    }
    
    col_sel, col_graph = st.columns([1, 2])
    
    with col_sel:
        theme_choisi = st.selectbox(
            "Sélectionnez un thème :", 
            list(dict_sentiment.keys()),
            key="select_sentiment_habitudes"
        )
        
    code_sentiment = dict_sentiment[theme_choisi]
    
    with col_graph:
        fig_sentiment = plot_weighted_bar(df_filtered, code_sentiment, f"Sentiment d'être informé : {theme_choisi}", df_texts, manual_map=map_sentiment)
        if fig_sentiment:
            st.plotly_chart(fig_sentiment, use_container_width=True, key=f"chart_sentiment_{code_sentiment}")
            
    st.info("La principale information du sondage est la composition du groupe 3. On y trouve à la fois une part importante de personnes qui n'ont pas le sentiment d'être bien informées, mais aussi une part qui au contraire est très sûre de ses connaissances. Le groupe est donc très polarisé entre ceux qui se jugent 'très informés', et ceux qui se jugent 'pas du tout informés'. Les autres groupes sont plus homogènes, même si on note encore la présence d'un groupe 'très informé' parmi le groupe 1. Enfin, on ne remarque pas de différences majeures entre les thèmes, à part le sport qui transcende les groupes et reste un sujet très apprécié.")
    st.markdown("---")
    
    st.subheader("3. Propension à payer pour l'information")
    st.markdown("Analyse du nombre moyen de sources payantes et de la part d'individus payant pour au moins une source d'information.")
    
    cols_pay = [f'PAY_R_{i}' for i in range(1, 8)]
    temp_pay = df_filtered.copy()
    
    colonnes_existantes = [col for col in cols_pay if col in temp_pay.columns]
    
    if colonnes_existantes:
        for col in colonnes_existantes:
            temp_pay[col] = pd.to_numeric(temp_pay[col], errors='coerce').fillna(0)
        
        temp_pay['Score_Paye'] = temp_pay[colonnes_existantes].eq(1).sum(axis=1)
        
        results = []
        for grp in temp_pay['Groupe'].unique():
            sub = temp_pay[temp_pay['Groupe'] == grp]
            if sub['POIDS03'].sum() > 0:
                avg = np.average(sub['Score_Paye'], weights=sub['POIDS03'])
                rate = np.average(sub['Score_Paye'] > 0, weights=sub['POIDS03']) * 100
                results.append({'Groupe': grp, 'Moyenne': avg, 'Taux_Paiement': rate})
                
        if results:
            df_stats = pd.DataFrame(results).sort_values('Groupe')
            
            fig_pay = go.Figure()
            
            fig_pay.add_trace(go.Bar(
                x=df_stats['Groupe'], 
                y=df_stats['Moyenne'],
                name='Nb moyen sources payantes',
                marker_color='#3498db', 
                text=df_stats['Moyenne'].round(2),
                textposition='auto'
            ))
            
            fig_pay.add_trace(go.Scatter(
                x=df_stats['Groupe'], 
                y=df_stats['Taux_Paiement'] / 100, 
                name='% de payeurs (échelle droite)',
                yaxis='y2',
                mode='lines+markers+text',
                line=dict(color='#08306b', width=3), 
                text=df_stats['Taux_Paiement'].round(1).astype(str) + '%',
                textposition='top center'
            ))
            
            fig_pay.update_layout(
                title="Comportement d'achat par groupe",
                yaxis=dict(title="Nombre moyen de sources payantes", range=[0, df_stats['Moyenne'].max() * 1.5]),
                yaxis2=dict(title="Taux de payeurs (%)", overlaying='y', side='right', range=[0, 1]),
                legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
                height=500,
                margin=dict(t=50, b=50)
            )
            
            st.plotly_chart(fig_pay, use_container_width=True, key="chart_propension_payer")
    else:
        st.warning("Les données sur la propension à payer (PAY_R_...) ne sont pas disponibles dans ce fichier.")
        
    st.info("Contrairement aux idées reçues, l'adhésion aux thèses complotistes semble corrélée à un investissement financier plus important dans l'accès à l'information. Le groupe des complotistes (3+) présente à la fois le taux de payeurs le plus élevé (41,1 %) et le nombre moyen de sources payantes le plus important (1,07), signe d'une démarche active et volontaire pour obtenir des contenus spécifiques.")

    st.header("4. Analyse des profils")
    st.write("Ce graphique compare le sentiment d'être bien informé, aux performances à un quiz sur l'actualité qui était posé à la fin du sondage. Ce quiz comportait 4 questions à choix multiples sur l'actualité, et les performances à ce quiz ont ensuite été transformées en un score entre 0 et 1.")

    data = df_filtered
    colonnes_info = ["INT3_R_1", "INT3_R_4", "INT3_R_5"]
    data["Info_moyenne"] = data[colonnes_info].mean(axis=1)

    Scores = {}
    for k in range(len(data)):
        score = 0
        for i in range(1,5):
            question = f"QUIZZ{i}_R"
            if data[question].iloc[k] == 1:
                score += 1
        Scores[k] = score/4

    data[f"Score_quizz"] = data.index.map(Scores)

    sns.set_theme(style="ticks")

    labels_groupes = {1: "Pas complotistes", 2: "Peu Complotistes", 3: "Complotistes"}
    palette = {1: "#8BC6A8", 2: "#F2C879", 3: "#E89A9A"}
    marqueurs_px = {1: "square", 2: "triangle-up", 3: "circle"}

    z_80 = 1.2816

    stats = (
        data
        .groupby("Groupe")
        .agg(
            score_mean=("Score_quizz", "mean"),
            score_std=("Score_quizz", "std"),
            score_n=("Score_quizz", "count"),

            info_mean=("Info_moyenne", "mean"),
            info_std=("Info_moyenne", "std"),
            info_n=("Info_moyenne", "count"),
        )
    )

    stats["score_ci80"] = z_80 * stats["score_std"] / np.sqrt(stats["score_n"])
    stats["info_ci80"] = z_80 * stats["info_std"] / np.sqrt(stats["info_n"])

    stats_plot = stats.reset_index()

    fig = px.scatter(
        stats_plot,
        x="score_mean",
        y="info_mean",
        color="Groupe",
        symbol="Groupe",
        color_discrete_map={labels_groupes[k]: v for k, v in palette.items()},
        symbol_sequence=[marqueurs_px[k] for k in sorted(marqueurs_px.keys())],
        error_x="score_std",
        error_y="info_std",
        labels={
            "score_mean": "Performance au quiz (score entre 0 et 1)",
            "info_mean": '"Vous sentez-vous bien informé ?"',
            "Groupe": "Groupes"
        },
        title="Sentiment d'information perçu et bonne connaissance de l'actualité par groupe de complotisme"
    )

    fig.update_layout(
        plot_bgcolor="white",
        xaxis=dict(
            range=[0, 1],
            gridcolor="lightgrey",
            linecolor="black",
            ticks="outside"
        ),
        yaxis=dict(
            tickmode="array",
            tickvals=[1, 2, 3, 4],
            ticktext=["Pas du tout", "Plutôt non", "Plutôt oui", "Tout à fait"],
            gridcolor="lightgrey",
            linecolor="black",
            ticks="outside"
        ),
        legend=dict(
            bordercolor="black",
            borderwidth=1,
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=1.02
        ),
        margin=dict(l=50, r=150, t=80, b=50)
    )

    fig.update_traces(
        marker=dict(size=12, line=dict(width=1, color="black")),
        error_x=dict(thickness=2, width=10),
        error_y=dict(thickness=2, width=10)
    )

    st.plotly_chart(fig, use_container_width=True, key="chart_analyse_profils_final")
    st.info("On observe que, même si tous les répondants se déclarent le plus souvent comme plutôt mal informés sur l’actualité, les plus 'complotistes' semblent avoir plus de confiance dans leur accès à l’information, tandis que les moins complotistes ont tendance à être plus réalistes ou plus modestes. Cependant, les complotistes ont des scores sensiblement plus bas sur les questions du quiz, marquant une moins bonne connaissance de l’actualité. Ceci est un résultat intéressant et peut peut-être se lire ainsi : les personnes les plus perméables aux théories du complot ont tendance à s’isoler dans des bulles informationnelles, ayant le sentiment d’être bien informées sur l’état du monde, ayant eu accès à des “vérités qu’on nous cache”. Mais cet isolement fait qu’on a plus de ressentiment envers les médias traditionnels et l’information 'mainstream', manquant ainsi l’occasion d’accéder à de vrais savoirs sur l’actualité.")