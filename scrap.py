#%%
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
from bs4 import BeautifulSoup
import plotly.graph_objects as go
import pandas as pd
import plotly.express as px
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import nltk
from nltk.corpus import stopwords
import random
import time
stopwords_fr = set(stopwords.words('french'))
stopwords_fr.add("1,2,3,4,5,6,7,8,9,10,0,',,,")
import plotly.graph_objects as go
from plotly.subplots import make_subplots

#%% Mot clés souhaité par l'utilisateur + récupération des stopwords francais
#search_word = input("Écris ce que tu veux rechercher : ") 
def scrap(mot_cles):
    
    driver = webdriver.Chrome()
    driver.get("https://www.amazon.fr/")

    time.sleep(random.randint(2, 4))

    button = driver.find_element(By.XPATH, '//*[@id="sp-cc-accept"]')
    button.click()

    time.sleep(random.randint(2, 4))

    search_bar = driver.find_element(By.XPATH, '//*[@id="twotabsearchtextbox"]')
    search_bar.send_keys(mot_cles)
    search_bar.send_keys(Keys.RETURN)

    time.sleep(random.randint(3, 5))

    page_source = driver.page_source
    return BeautifulSoup(page_source, 'html.parser')

def process(soup):
    
    reviews = []
    titles = []
    prices = []
    classements = []
    

    title_divs = soup.find_all("span", {"class": "a-size-base-plus a-color-base a-text-normal"})
    price_divs = soup.find_all("span", {"class": "a-price-whole"})
    reviews_divs = soup.find_all("span", {"class": "a-size-base s-underline-text"})
    classements_div = [div['data-csa-c-pos'] for div in soup.find_all("div") if 'data-csa-c-pos' in div.attrs]


    for title_div, price_div, reviews_div, classement_div in zip(title_divs, price_divs, reviews_divs,classements_div):
        review = float(reviews_div.get_text().strip().replace('\xa0', '').replace(',', '')) if reviews_div else 'NaN'
        title = title_div.get_text().strip()
        #title = title_div.get_text().strip()
        price = price_div.get_text().strip().replace('\u202f', '').replace('€', '').replace(',', '.') if price_div else "NaN"
        price = float(price) if price != "NaN" else float('nan')
        classement = classement_div.strip()
        reviews.append(review)
        titles.append(title)
        prices.append(price)
        classements.append(classement)
    
    df = pd.DataFrame(
        {'titres' : titles,
        'prix' : prices,
        'nombres_avis_clients': reviews,
        'classements' : classements
        }
    )

    return df

#%%
def title_to_worldcloud(df):
    
    titles_segmente = []
    
    titles = list(df["titres"])
    for titre in titles:
        mots = titre.split()
        titles_segmente.extend(mots)
        
    titles_filtre = [mot for mot in titles_segmente if mot.lower() not in stopwords_fr]
    text = ' '.join(titles_filtre)
    nb_mot = len(titles_filtre)
    
    #Visualisation du nuage de mot
    wordcloud = WordCloud(width=800, 
                    height=400, 
                    background_color='white',
                    colormap='rainbow',
                    max_words=nb_mot).generate(text)
    
    image = wordcloud.to_image()

    #Vérifier comment ça fonctionne
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    
    return image, titles_filtre


def n_gram(titles_filtre):
    # Analyse fréquences des mots
    word_counts = pd.Series(titles_filtre).value_counts()
    df_word_counts = pd.DataFrame({'Mots': word_counts.index, 'Fréquences': word_counts.values})
    df_top_10 = df_word_counts.head(10)
    
    fig = go.Figure([go.Bar(x=df_top_10['Mots'], y=df_top_10['Fréquences'])])
    fig.update_layout(xaxis_title='Mots', yaxis_title='Fréquences')
    
    return fig

    
    #Analyse fréquences des mots
    # word_counts = pd.Series(titles_filtre).value_counts()
    # df_word_counts = pd.DataFrame({'Mots': word_counts.index, 'Fréquences': word_counts.values})
    # df_top_10 = df_word_counts.head(10)
    # fig = px.bar(df_top_10, x='Mots', y='Fréquences')
    
    # return fig


def compute_stats(df):
    #moyenne des longueurs des titres
    moyenne_caracteres_titres = df['titres'].apply(lambda x: len(x)).mean()
    
    #moyenne et mediane des prix au total
    moyenne_prix = df["prix"].mean()
    mediane_prix = df["prix"].median()
    
    #nettoyage des avis clients
    df['nombres_avis_clients'] = df['nombres_avis_clients'].astype(str).str.replace('\xa0', '').str.replace(',', '').astype(float)
    
    #moyenne du nombre d'avis 
    mean_nombres_avis = df['nombres_avis_clients'].mean()
    
    
    return moyenne_caracteres_titres, moyenne_prix, mediane_prix, mean_nombres_avis
    
    
#%%
def repartition_prix_moyenne_classement(df):

    #visualiser les prix 
    fig = px.histogram (
        df, 
        y="prix",
        x="classements",
        #color="nombres_avis_clients",
        title = 'Répartition des prix en fonction des classements'
    )
    
    mean_prix = df["prix"].mean()
    
    # Ajouter la ligne de la moyenne
    fig.add_shape(       
                  
        type='line',
        y0=mean_prix,
        y1=mean_prix,
        x0=0,
        x1=len(df),  # Récupérer la valeur maximale de l'histogramme
        line=dict(color='red', width=2, dash='dash')
        
    )
    
    # Modifier le label de l'axe y
    fig.update_yaxes(title_text="prix")
    
    return fig

#%%    
def quartiles_prix_boxplot(df):
    
    #analyse de la variance des prix
    fig =  px.box(df, y="prix", title="Analyse des quartiles de prix")
    return fig
    
    
#%%  
def quartiles_avis_boxplot(df):

    #analyse du nombre d'avis 
    fig = px.box(df, y="nombres_avis_clients", title="Analyse des avis clients")
    return fig

#%%
#df = process(scrap('telephone'))