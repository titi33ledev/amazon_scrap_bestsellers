#%%
import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_plotly_events import plotly_events
from st_aggrid import AgGrid
from scrap import  scrap, quartiles_avis_boxplot, quartiles_prix_boxplot, repartition_prix_moyenne_classement,compute_stats, process,n_gram,title_to_worldcloud

st.title('Product Finder Amazon')
st.header("Bienvenue dans l'outil : Product Finder Amazon :sunglasses:")
st.markdown(body=f"Vous allez pouvoir avoir les données produits qu'ils vous faut pour atteindre les offres de 1er page sur votre mot clés")

mot_cles = st.text_input('Écris ce que tu veux rechercher', '...')
if mot_cles != '...':
    st.write('Le mot clés choisi est : ', mot_cles)
    soup = scrap(mot_cles)
    df = process(soup)
    

    # Vérifier si df a été définie
    if 'df' in locals():
        # Continuer avec le reste du code utilisant df
        moyenne_caracteres_titres, moyenne_prix, mediane_prix, mean_nombres_avis = compute_stats(df)

        # Affichage des métriques avec Streamlit
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Moy. longueurs titres", f"{moyenne_caracteres_titres:.2f}")
        col2.metric("Moyenne des prix", f"{moyenne_prix:.2f} €")
        col3.metric("Médiane des prix", f"{mediane_prix:.2f} €")
        col4.metric("Moyenne des avis", f"{mean_nombres_avis:.2f}")
        
        
        st.subheader("Partie 1 : Analyse des prix produits :moneybag:")
        
        # Afficher la répartition des prix
        fig_repartition = repartition_prix_moyenne_classement(df)
        st.plotly_chart(fig_repartition)
        
        
        # Afficher le boxplot des prix
        fig_quartiles = quartiles_prix_boxplot(df)
        st.plotly_chart(fig_quartiles)

        st.markdown("La boîte à moustaches (quartiles_prix_boxplot) est un outil mathématique et graphique qui permet d'analyser la répartition des prix dans un ensemble de données. Elle fournit des informations sur les quartiles, la médiane, les valeurs aberrantes et l'étendue des prix. Ces mesures statistiques permettent d'évaluer la dispersion et la distribution des prix, ce qui est utile pour la comparaison des données, la détection des valeurs aberrantes et la prise de décision éclairée.")
        

        st.subheader("Partie 2 : Analyse des caractères produits :abc:")
        
        #Afficher nuages de mots les plus fréquents
        image_wordcloud, titles_filtre = title_to_worldcloud(df)
        st.image(image_wordcloud)
        
        st.markdown("Le WordCloud est une représentation graphique des mots les plus fréquents dans les titres des produits. Il permet une visualisation rapide des mots clés pertinents et des tendances. Les mots sont affichés en fonction de leur fréquence, avec une taille plus grande pour les mots les plus fréquents.")

        # Afficher le classement des caractères les plus donnés
        fig_classement_caracteres = n_gram(titles_filtre)
        st.plotly_chart(fig_classement_caracteres)