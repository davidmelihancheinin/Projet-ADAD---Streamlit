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

def plot_weighted_bar(dataframe, var_code, var_name, df_texts):
    mapping = get_mapping(df_texts, var_code)
    
    temp_df = dataframe.copy()
    if var_code not in temp_df.columns:
        st.warning(f"La colonne {var_code} n'est pas présente dans les données.")
        return None
        
    temp_df[var_code] = pd.to_numeric(temp_df[var_code], errors='coerce').fillna(-99).astype(int)
    
    mask = temp_df[var_code] != -99
    data_clean = temp_df[mask]
    
    if data_clean.empty:
        st.warning(f"Pas de données valides pour {var_name}")
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
    
    if var_code == 'RS5_R':
        cap_label = next((l for l in labels_ordonnes if 'CAP' in str(l).upper()), None)
        bac_label = next((l for l in labels_ordonnes if 'BAC' in str(l).upper()), None)
        
        if cap_label and bac_label:
            labels_ordonnes.remove(cap_label)
            idx_bac = labels_ordonnes.index(bac_label)
            labels_ordonnes.insert(idx_bac + 1, cap_label)
            

    ct_long['Réponse'] = ct_long['Code_Reponse'].map(mapping).fillna(ct_long['Code_Reponse'].astype(str))
    
    # Graphique avec gradation et ordre forcé
    fig = px.bar(
        ct_long, 
        x='Pourcentage', 
        y='Groupe', 
        color='Réponse',
        orientation='h',
        title=f"Répartition : {var_name}",
        text_auto='.1f',
        color_discrete_sequence=px.colors.sequential.Blues,
        category_orders={"Réponse": labels_ordonnes}
    )
    
    fig.update_layout(
        xaxis_title="% (Pondéré)",
        yaxis_title="",
        legend_title="Catégories :",
        height=450,
        bargap=0.3,
        legend=dict(orientation="h", yanchor="bottom", y=-0.5, xanchor="center", x=0.5)
    )
    
    return fig

# Fonction principale

def render_page(df_filtered, df_texts):
    st.header("Profil Sociodémographique")
    st.markdown("L'analyse croisée des variables socio-démographiques démontre que l'adhésion aux thèses complotistes est fondamentalement structurée par le **capital culturel et économique**, reléguant au second plan les déterminants géographiques ou le genre. Le profil dit 'Non Complotiste' (Groupe 1) se distingue par une forte dotation en capital scolaire (diplômes du supérieur) et financier, regroupant majoritairement des cadres et des professions intellectuelles supérieures. À l'inverse, la porosité aux récits alternatifs (Groupe 3) s'enracine au sein des classes populaires et moyennes (ouvriers, employés), disposant de revenus et de diplômes intermédiaires.")
    
    dict_socio = {
        'RS2C_RECODE_AG_R': 'Âge',
        'RS5_R': 'Niveau d\'étude',
        'RS3_R': 'Situation professionnelle', 
        'CSPIND_R': 'Catégorie socio-professionnelle (Profession)',
        'RS14_R': 'Revenu mensuel du foyer',
        'CC_R': 'Taille d\'agglomération (Urbain/Rural)',
        'UDA9_R': 'Région',
        'RS7_R': 'Nombre de personnes dans le foyer', 
        'RS1_R': 'Genre'
    }

    # Dictionnaire des descriptions
    dict_descriptions = {
        'Âge': "Les personnes âgées de plus de 70 ans sont plus représentées parmi les personnes adhérentes aux théories du complot : elles passent de 13,9% du groupe 1 à 16,2% du groupe 2 et 19,4% du groupe 3. Le schéma inverse est observable pour les plus jeunes (15-17 ans) qui représentent 5,6% des non complotistes contre 4,8% des peu complotistes et 3,3% des “très” complotistes.",
        'Niveau d\'étude': "L'analyse du niveau d'étude confirme une corrélation classique : plus le diplôme s'élève, plus l'adhésion au complotisme recule. Le Groupe 3 concentre une forte proportion de diplômes intermédiaires (CAP, BEP, Baccalauréat), tandis que les diplômés de l'enseignement supérieur (Bac+3, Bac+5 et au-delà) sont largement majoritaires dans le Groupe 1.",
        'Situation professionnelle': "Le profil professionnel s'inscrit dans la continuité de l'âge. Le Groupe 3 est fortement représenté par des inactifs retraités (près de 33%). Le Groupe 3, en revanche, est un groupe résolument \"actif\" (près de 58% de personnes en emploi).",
        'Catégorie socio-professionnelle (Profession)': "Le clivage social est net sur ce graphique. Les catégories populaires (CSP-) constituent le cœur du Groupe 3, témoignant d'une perméabilité plus forte de ces milieux aux récits alternatifs. À l'autre extrémité, les Cadres et professions intellectuelles supérieures (CSP+) sont plus étanches à ces thèses et se retrouvent principalement dans le Groupe 1.",
        'Revenu mensuel du foyer': "Le gradient économique suit bien le gradient éducatif et professionnel. Les foyers disposant de revenus modestes à intermédiaires (moins de 3000€ net par mois) sont surreprésentés parmi les profils très complotistes. À l'inverse, la part des revenus les plus confortables (plus de 3000€ net par mois) grimpe de façon significative dans le Groupe 1.",
        'Taille d\'agglomération (Urbain/Rural)': "Contrairement aux indicateurs économiques, la géographie urbaine joue un rôle marginal. Que l'on vive en zone rurale, dans une ville moyenne ou dans une grande métropole, l'adhésion aux thèses complotistes reste relativement stable. On note tout au plus une légère \"résistance\" en agglomération parisienne, surreprésentée dans le Groupe 1, probablement liée à la concentration des cadres et hauts diplômés.",
        'Région': "L'analyse régionale ne fait ressortir aucun \"bastion\" géographique de la désinformation. La distribution des trois groupes est relativement homogène sur l'ensemble du territoire national, confirmant que le complotisme est un phénomène sociologique et économique plutôt que territorial.",
        'Nombre de personnes dans le foyer': "Il ne ressort pas de tendance particulière de l’analyse des trois groupes selon le nombre de personnes dans le foyer hormis une légère surreprésentation des foyers de 5 personnes et plus chez le groupe 3.",
        'Genre': "L'analyse des résultats pondérés révèle une légère différence de genre face à la désinformation. Les hommes apparaissent très légèrement majoritaires au sein du Groupe 1 (non complotistes) avec 51,6 % (chiffres INSEE 2019). À l'inverse, on observe une surreprésentation féminine dans les profils plus poreux à ces thèses : les femmes constituent 53,7 % du Groupe 2 et 53,3 % du Groupe 3. Toutefois, ce constat doit être nuancé : ces chiffres intègrent un redressement statistique (POIDS03) visant à reproduire la structure démographique réelle de la population française, naturellement majoritairement féminine. Ainsi, bien que le glissement soit visible après pondération, la fracture de genre reste modérée et est probablement accentuée par le croisement avec d'autres variables socio-économiques lors du lissage statistique, plutôt que par un clivage massif dans les réponses brutes."
    }

    inv_map = {v: k for k, v in dict_socio.items()}

    # Menu déroulantz
    choix_graphe = st.selectbox(
        "**Choisissez la variable à afficher :**", 
        list(dict_socio.values())
    )

    st.markdown("---")

    code_var = inv_map[choix_graphe]
    fig = plot_weighted_bar(df_filtered, code_var, choix_graphe, df_texts)
    
    if fig:
        st.plotly_chart(fig, use_container_width=True)
        

        if choix_graphe in dict_descriptions:
            st.info(dict_descriptions[choix_graphe])