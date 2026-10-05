# **Peut-on identifier des profils sociologiques plus perméables aux théories du complot ?**

Un dashboard interactif sur les Français, l'information et les théories du complot.

**Le dashboard est accessible à l'adresse suivante :** https://projet-adad---app-imdbedki75azuwwnzdtv5r.streamlit.app

_Ce projet a été réalisé par David MELIHAN, Hamza ZAHRAOUI et Swann ROBERT, dans le cadre de l'Open Data University, programme créé par Latitudes._

## **En une phrase**

Ce dashboard explore l'enquête « Les Français et l'information » (ARCOM, 2024) et pose une question simple : les personnes qui adhèrent aux théories du complot ne s'informent-elles pas, ou s'informent-elles autrement ?


## **L'idée de départ**

On parle beaucoup de désinformation, mais rarement des personnes concernées : qui sont-elles, que pensent-elles des médias, où consultent-elles l'actualité, pour qui votent-elles ?
Plutôt que de raisonner à partir d'idées reçues, ce projet part des données d'une grande enquête nationale et les met en scène de manière visuelle et interactive. Chacun peut explorer les chiffres à son rythme, changer de variable, filtrer les groupes, et se faire sa propre idée.

## **Le principe : trois groupes à comparer**

Les répondants de l'enquête ont été interrogés sur 8 affirmations, dont certaines sont avérées et d'autres fausses (alunissage, origine du Covid, 11 septembre, vaccins, climat, élections américaines, etc.).

Le score va de 0 à 8, selon le nombre de réponses qui s'écartent de la réalité. Il permet de former trois groupes :

🟢 **Groupe 1**, les « **non complotistes** » : les personnes dont le score est de 0, qui ne se trompent sur aucune des 8 affirmations.

🟠 **Groupe 2**, les « **peu complotistes** » : les personnes dont le score est de 1 ou 2.

🔴 **Groupe 3**, les « **complotistes** » : les personnes dont le score est de 3 ou plus.

Tout le dashboard consiste ensuite à comparer ces trois groupes sur des dimensions très différentes de la vie quotidienne.

## **Organisation du dashboard**

Le dashboard est découpé en 5 onglets, comme cinq angles pour regarder la même question.

🏠 **Accueil : comprendre la méthode**
Le point d'entrée : comment les trois groupes ont été construits, avec la liste des 8 affirmations soumises aux répondants (vraies ou fausses). Près de trois quarts des personnes interrogées adhèrent à au moins l'une d'elles.

👥 **Socio-démographie : qui sont-ils ?**
Âge, diplôme, profession, revenus, région, genre… à explorer variable par variable. Ce sont surtout le diplôme et les revenus qui distinguent les groupes, bien plus que le lieu de vie.

📰 **Rapport à l'information : s'estiment-ils informés ?**
Intérêt pour l'actualité, sentiment d'être bien informé, propension à payer, et un quiz d'actualité pour confronter ce que l'on croit savoir à ce que l'on sait vraiment. Le résultat est contre-intuitif.

🗳️ **Politique : quelles opinions ?**
Positionnement gauche/droite, vote en 2022, optimisme et opinions sur huit sujets de société. On y voit comment le centre de gravité politique se déplace d'un groupe à l'autre, et ce que l'on peut en conclure ou non.

📱 **Sources d'information : à qui fait-on confiance ?**
Fréquence d'usage de chaque média et confiance accordée aux journalistes, experts, influenceurs, anonymes ou proches. La confiance se déplace des figures d'autorité vers des sources plus « horizontales », mais celle accordée aux proches reste stable dans tous les groupes.


## **Les données**

**Source :** enquête Les Français et l'information, ARCOM, 2024 (base anonymisée, issue de l'open data).

**Contenu :** les réponses individuelles de milliers de répondants, accompagnées d'un dictionnaire de variables.

**Thèmes couverts :** profil sociodémographique, intérêt et sentiment d'information, usages des médias, confiance, paiement, opinions politiques et sociétales, croyance aux théories du complot.

Le dashboard est développé en **Python** avec **Streamlit** pour l'interface,**pandas** et **NumPy** pour le traitement des données, et **Plotly** pour les graphiques interactifs.

## **Contexte du projet**

Ce projet a été réalisé à Centrale Marseille dans le cadre de l'Open Data University, un programme créé par Latitudes qui invite des étudiants à s'emparer de données ouvertes pour en tirer des analyses utiles et accessibles.

**Auteurs :**  David MELIHAN, Hamza ZAHRAOUI et Swann ROBERT

