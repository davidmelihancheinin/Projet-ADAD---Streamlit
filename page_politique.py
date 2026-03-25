import streamlit as st
import plotly.express as px

def render_page(df_filtered):
    st.header("Politique et Vision de la société")
    
    # Palettes de couleurs
    couleurs_echelle_map = {
        "Très optimiste": "#4CAF50", "Plutôt optimiste": "#8BC34A",
        "Plutôt pessimiste": "#FFC107", "Très pessimiste": "#F44336",
        "Tout à fait d'accord": "#4CAF50", "Plutôt d'accord": "#8BC34A",
        "Plutôt pas d'accord": "#FFC107", "Pas du tout d'accord": "#F44336"
    }

    # Orientation politique
    st.subheader("1. Auto-positionnement politique")
    st.markdown("On a retiré de ce graphique la valeur 5 (au milieu), car elle a massivement été choisie par tous les groupes, beaucoup de monde ne souhaitait pas se positionner. On a donc retiré cette réponse afin de rendre le graphique plus lisible. Par cette manipulation, on efface aussi un certain nombre de répondants 'centristes', mais le but du graphique étant d'exposer globalement le clivage gauche/droite au sein des groupes, on a considéré que cela n'affectait pas le message du graphique.")
   
    nou_values = [i for i in range(1, 12) if i != 6]
    df_nou = df_filtered[df_filtered['NOU1_R'].isin(nou_values)].copy()
    
    chart_data_nou = df_nou.groupby(['Groupe', 'NOU1_R'])['POIDS03'].sum().reset_index()
    
    if not chart_data_nou.empty:
        fig_bar = px.bar(
            chart_data_nou,
            x="NOU1_R",
            y="POIDS03",
            color="NOU1_R", 
            facet_col="Groupe", 
            title="Sur une échelle de 0 à 10, où 0 correspond à la gauche et 10 correspond à la droite, où diriez-vous que vous vous situez ?",
            labels={"NOU1_R": "Positionnement", "POIDS03": "Volume (Pondéré)"},
            color_continuous_scale="RdBu",
            range_color=[1, 11]
        )
        fig_bar.update_xaxes(tickvals=[1, 11], ticktext=["Gauche", "Droite"], title_text="")
        fig_bar.update_layout(coloraxis_showscale=False, height=350)
        st.plotly_chart(fig_bar, use_container_width=True)
    
    st.info("Ce graphique est assez auto-porteur. On notera que le groupe 2 a des barres plus hautes : cela est dû au fait qu'il comporte plus de personnes que les autres. L'objectif ici est surtout de repérer une tendance globale dans la répartition au sein des groupes, tendance que l'on observe surtout dans le groupe 3, avec une domination de la droite (barre bleu foncé) et un maintien résiduel de la gauche.")
    st.markdown("---")

    # Vote présidentiel 2022
    st.subheader("2. Vote à l'élection présidentielle 2022")
    st.warning("Disclaimer : la légende retenue pour ce graphique est totalement contestable, nous ne sommes nous-mêmes pas satisfaits du résultat final. L'objectif était de regrouper les candidats ensemble pour avoir un graphique lisible, tout en essayant de respecter à la fois les dénominations officielles du ministère (qui ne concernent malheureusement que les législatives et pas les présidentielles) qui datent de 2022, et en essayant d'être le plus neutre et le moins polémique possible (ce qui est en fait totalement impossible).")
    couleurs_politiques = {
        "Droite Radicale": "darkblue", "Droite Modérée": "blue", "Centre": "orange",
        "Gauche Modérée": "green", "Gauche Radicale": "red", "Blanc/Abstention/Autre": "lightgrey"
    }

    groupes_presents = sorted(df_filtered['Groupe'].unique())
    cols = st.columns(len(groupes_presents))
    
    for idx, grp in enumerate(groupes_presents):
        with cols[idx]:
            st.markdown(f"<h5 style='text-align: center;'>{grp}</h5>", unsafe_allow_html=True)
            df_grp = df_filtered[df_filtered['Groupe'] == grp]
            pie_data = df_grp.groupby('Categorie_Politique')['POIDS03'].sum().reset_index()
            
            if not pie_data.empty:
                fig_pie = px.pie(
                    pie_data, values='POIDS03', names='Categorie_Politique',
                    color='Categorie_Politique', color_discrete_map=couleurs_politiques, hole=0.3
                )
                fig_pie.update_layout(showlegend=False, margin=dict(t=0, b=0, l=0, r=0), height=250)
                fig_pie.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig_pie, use_container_width=True)

    st.success("**Légende :** 🔴 **Gauche Radicale** (Mélenchon, Roussel, Poutou, Arthaud) | 🟢 **Gauche Modérée** (Jadot, Hidalgo) | 🟠 **Centre** (Macron, Lassalle) | 🔵 **Droite Modérée** (Pécresse, Dupont-Aignan) | 🔵 **Droite Radicale** (Le Pen, Zemmour)")
    st.info("Il faut pour analyser ce graphique avoir en tête les résultats officiels de 2022, afin surtout d'analyser les écarts entre les résultats finaux de l'élection et les résultats du sondage. Notons par ailleurs que nous avons regroupé dans le bloc gris les gens préférant ne pas répondre à la question. Les résultats du sondage découlent quant à eux du graphique précédent : on trouve un groupe 1 très ancré à gauche, tandis que les groupes 2 et 3 votent plus en faveur des partis de droite. En effet, la lecture successive de ces trois camemberts montre un vrai basculement du centre de gravité politique à mesure que le 'niveau de complotisme' augmente.")
    st.markdown("---")

    # Niveau d'optimisme
    st.subheader("3. Niveau d'optimisme")
    st.markdown("**Question posée :** *Diriez-vous que vous êtes très optimiste, plutôt optimiste, plutôt pessimiste ou très pessimiste à l’égard...*")

    sujets_opti_map = {
        "De la France": "OPTI_R_2", 
        "De l’Union Européenne": "OPTI_R_3", 
        "Du climat": "OPTI_R_4",
        "Des médias et sources d'info": "OPTI_R_6"
    }
    
    col_select_opti, col_graph_opti = st.columns([1, 3])
    with col_select_opti:
        sujet_choisi = st.radio("Sélectionnez un sujet :", list(sujets_opti_map.keys()), key="radio_opti")
        col_concernee = sujets_opti_map[sujet_choisi]

    df_opti = df_filtered[df_filtered[col_concernee].isin([1, 2, 3, 4])].copy()
    labels_opti = {1: "Très optimiste", 2: "Plutôt optimiste", 3: "Plutôt pessimiste", 4: "Très pessimiste"}
    df_opti['Reponse'] = df_opti[col_concernee].map(labels_opti)
    
    chart_data_opti = df_opti.groupby(['Groupe', 'Reponse'])['POIDS03'].sum().reset_index()
    total_par_groupe_opti = chart_data_opti.groupby('Groupe')['POIDS03'].transform('sum')
    chart_data_opti['Pourcentage'] = (chart_data_opti['POIDS03'] / total_par_groupe_opti) * 100
    
    ordre_opti = ["Très optimiste", "Plutôt optimiste", "Plutôt pessimiste", "Très pessimiste"]

    with col_graph_opti:
        if not chart_data_opti.empty:
            fig_opti = px.bar(
                chart_data_opti, x="Groupe", y="Pourcentage", color="Reponse",
                color_discrete_map=couleurs_echelle_map, 
                category_orders={"Reponse": ordre_opti, "Groupe": groupes_presents},
                labels={"Groupe": "Groupe", "Pourcentage": "%"}
            )
            fig_opti.add_hline(y=50, line_dash="dash", line_color="black", annotation_text="Majorité (50%)")
            fig_opti.update_layout(yaxis=dict(range=[0, 100]), title=f"Optimisme : {sujet_choisi}", height=400)
            st.plotly_chart(fig_opti, use_container_width=True)
        else:
            st.warning("Pas de données.")
    
    st.info("La ligne en pointillé au milieu des barres représente 50% du groupe. Elle a été rajoutée pour permettre de visualiser plus rapidement de quel côté penche chaque groupe. Il est difficile de dégager une interprétation claire des graphiques, car il faut prendre en compte le fait que les groupes ne sont pas composés politiquement de la même manière. Ainsi, l'optimisme du groupe 3 vis-à-vis du climat s'explique peut-être par le fait que les partis de droite mettent souvent moins l'écologie au cœur de leur discours que les partis de gauche par exemple. L'analyse des quatre graphiques met quand même en évidence un pessimisme majoritaire, qui tend à s'aggraver avec l'adhésion aux thèses complotistes, particulièrement vis-à-vis des sphères institutionnelles. Il paraît enfin important d'observer le dernier graphique, qui montre un pessimisme vis-à-vis des médias plus marqué pour les groupes 'complotistes'.")
    st.markdown("---")

    # Opinions sur la société
    st.subheader("4. Opinions sur des questions de société")
    st.markdown("**Question posée :** *Pour chacune des affirmations suivantes, êtes-vous tout à fait d'accord, plutôt d'accord, etc. ?*")

    themes_opinions_map = {
        "Égalité Homme/Femme": {"col": "VA1_R_1", "question": "Il faut aller plus loin dans l’égalité homme/femme"},
        "Immigration": {"col": "VA1_R_2", "question": "Aujourd’hui il y a trop d’immigrés en France"},
        "Identités de genre": {"col": "VA1_R_3", "question": "Il est important de reconnaître la diversité des identités de genre"},
        "Avortement": {"col": "VA1_R_4", "question": "Aujourd’hui l’avortement est trop facile d’accès"},
        "Homoparentalité": {"col": "VA1_R_5", "question": "Il est normal que les couples homosexuels puissent avoir des enfants"},
        "Environnement": {"col": "VA1_R_6", "question": "Il faut changer nos modes de vie pour lutter contre le réchauffement climatique"},
        "Conflit Israélo-Palestinien": {"col": "VA1_R_7", "question": "Les Israéliens portent la plus grande part de responsabilité dans le conflit israélo-palestinien"},
        "Antisémitisme": {"col": "VA1_R_8", "question": "Les Français juifs ne sont pas des Français comme les autres"}
    }

    col_select_va, col_graph_va = st.columns([1, 3])
    with col_select_va:
        theme_choisi = st.selectbox("Choisissez un thème :", list(themes_opinions_map.keys()), key="select_theme")
        col_va = themes_opinions_map[theme_choisi]["col"]
        question_entiere = themes_opinions_map[theme_choisi]["question"]

    df_va = df_filtered[df_filtered[col_va].isin([1, 2, 3, 4])].copy()
    labels_va = {1: "Tout à fait d'accord", 2: "Plutôt d'accord", 3: "Plutôt pas d'accord", 4: "Pas du tout d'accord"}
    df_va['Reponse'] = df_va[col_va].map(labels_va)

    chart_data_va = df_va.groupby(['Groupe', 'Reponse'])['POIDS03'].sum().reset_index()
    total_par_groupe_va = chart_data_va.groupby('Groupe')['POIDS03'].transform('sum')
    chart_data_va['Pourcentage'] = (chart_data_va['POIDS03'] / total_par_groupe_va) * 100

    ordre_va = ["Tout à fait d'accord", "Plutôt d'accord", "Plutôt pas d'accord", "Pas du tout d'accord"]

    with col_graph_va:
        if not chart_data_va.empty:
            fig_va = px.bar(
                chart_data_va, x="Groupe", y="Pourcentage", color="Reponse",
                color_discrete_map=couleurs_echelle_map,
                category_orders={"Reponse": ordre_va, "Groupe": groupes_presents},
                labels={"Groupe": "Groupe", "Pourcentage": "%"}
            )
            fig_va.add_hline(y=50, line_dash="dash", line_color="black", annotation_text="Majorité (50%)")
            fig_va.update_layout(yaxis=dict(range=[0, 100]), title=f"Avis : {question_entiere}", title_font_size=14, height=400)
            st.plotly_chart(fig_va, use_container_width=True)
        else:
            st.warning("Pas de données.")
    
    st.info("Encore une fois, les résultats de ces graphiques montrent surtout la répartition politique des groupes, avec un groupe 1 plus en accord avec les thèmes dits 'de gauche', et des groupes 2 et 3 en accord avec les thèmes de droite. On retient surtout que l'adhésion aux thèses complotistes s'accompagne d'une adhésion à des positions sociétales plus conservatrices (voire réactionnaires). Mettons cependant de côté l'analyse de l'avant-dernière question (dont l'interprétation peut assez franchement porter à confusion, et fausser ainsi les résultats), pour nous concentrer sur les résultats de la dernière question : on note quand même que le groupe 3 soutient cet avis antisémite beaucoup plus que les deux autres groupes. Une explication possible de ce résultat pourrait être la présence d'une thèse antisémite ('Il existe un complot juif à l’échelle mondiale') parmi les thèses du complot proposées aux répondants. Il est alors possible que la majorité des répondants 'antisémites' se soient alors retrouvés dans le groupe 3, ce qui expliquerait ces résultats.")