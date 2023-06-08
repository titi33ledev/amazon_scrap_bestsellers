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

#%% Mot clés souhaité par l'utilisateur + récupération des stopwords francais
search_word = input("Écris ce que tu veux rechercher : ") 
stopwords_fr = set(stopwords.words('french'))
stopwords_fr.add("1,2,3,4,5,6,7,8,9,10,0,',,,")

driver = webdriver.Chrome()
driver.get("https://www.amazon.fr/")

time.sleep(random.randint(4, 7))

button = driver.find_element(By.XPATH, '//*[@id="sp-cc-accept"]')
button.click()

time.sleep(random.randint(3, 6))

search_bar = driver.find_element(By.XPATH, '//*[@id="twotabsearchtextbox"]')
search_bar.send_keys(search_word)
search_bar.send_keys(Keys.RETURN)

time.sleep(random.randint(4, 7))

page_source = driver.page_source
soup = BeautifulSoup(page_source, 'html.parser')

#%%
reviews = []
titles = []
prices = []
titles_segmente = []
classements = []


title_divs = soup.find_all("span", {"class": "a-size-base-plus a-color-base a-text-normal"})
price_divs = soup.find_all("span", {"class": "a-price-whole"})
reviews_divs = soup.find_all("span", {"class": "a-size-base s-underline-text"})
classements_div = [div['data-csa-c-pos'] for div in soup.find_all("div") if 'data-csa-c-pos' in div.attrs]

for title_div, price_div, reviews_div, classement_div in zip(title_divs, price_divs, reviews_divs,classements_div):
    review = float(reviews_div.get_text().strip().replace('\xa0', '').replace(',', '')) if reviews_div else 'NaN'
    title = title_div.get_text().strip()
    title = title_div.get_text().strip()
    price = price_div.get_text().strip().replace('\u202f', '').replace('€', '').replace(',', '.') if price_div else "NaN"
    price = float(price) if price != "NaN" else float('nan')
    classement = classement_div.strip()
    reviews.append(review)
    titles.append(title)
    prices.append(price)
    classements.append(classement)


#%%
for titre in titles:
    mots = titre.split()
    titles_segmente.extend(mots)
   
df = pd.DataFrame(
     {'titres' : titles,
      'prix' : prices,
      'nombres_avis_clients': reviews, 
      'classements' : classements
     }
)

#%% Analyse statistiques des données

moyenne_caracteres_titres = df['titres'].apply(lambda x: len(x)).mean()
moyenne_prix = df["prix"].mean()
df['nombres_avis_clients'] = df['nombres_avis_clients'].astype(str).str.replace('\xa0', '').str.replace(',', '').astype(float)
mean_nombres_avis = df['nombres_avis_clients'].mean()
mediane_prix = df["prix"].median()

print(f"Moyenne des prix = {moyenne_prix}")
print(f"Médiane des prix = {mediane_prix}")
print(f"Moyenne du nombre de caractères pour l'ensemble des titres : {moyenne_caracteres_titres}")

mean_prix = df['prix'].mean()
prix_trace = go.Scatter(x=df.index, y=df['prix'], name='Prix')
mean_trace = go.Scatter(x=[df.index[0], df.index[-1]], y=[mean_prix, mean_prix], name='Moyenne', 
                        line=dict(color='red', width=3, dash='dash'))

visualisation_prix_mc = go.Figure(data=[prix_trace, mean_trace], layout=go.Layout(title=f'Visualisation des prix sur le mot clé "{search_word}"'))
visualisation_prix_mc.update_layout(legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01))
#visualisation_prix_mc.show()


analyse_variance_prix = px.box(df, y="prix", title="Analyse des variances de prix")
#analyse_variance_prix.show()


# %% Analyse des mots utilisés dans les produits de la première page

titles_filtre = [mot for mot in titles_segmente if mot.lower() not in stopwords_fr]
text = ' '.join(titles_filtre)
nb_mot = len(titles_filtre)

wordcloud = WordCloud(width=800, 
                      height=400, 
                      background_color='white',
                      colormap='rainbow',
                      max_words=nb_mot).generate(text)

plt.figure(figsize=(100, 5))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off')
#plt.show()


word_counts = pd.Series(titles_filtre).value_counts()
df_word_counts = pd.DataFrame({'Mots': word_counts.index, 'Fréquences': word_counts.values})
print(f'Voici le top 10 des mots clés les plus utilisés sur la requête : "{search_word}"')
print(df_word_counts.head(10))

df_top_10 = df_word_counts.head(10)
top_mot_cles = px.bar(df_top_10, x='Mots', y='Fréquences')
#top_mot_cles.show()

#%% Analyse du nombre d'avis et la répartition

avis_client = px.box(df, y="nombres_avis_clients", title="Analyse des avis clients")
#avis_client.show()