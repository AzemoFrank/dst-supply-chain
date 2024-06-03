import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import folium
import geopandas as gpd
from wordcloud import WordCloud
from collections import Counter
from nltk.corpus import stopwords

class VisualisationGeneral:
    """
    Fournit des outils de visualisation pour des données spécifiques ou des colonnes de DataFrame.
    """

    @staticmethod
    def plot_bar_chart(data, rotation=45):
        """
        Trace un diagramme en barres pour les données fournies.

        Paramètres:
        data (Series): Données pandas Series contenant les valeurs à tracer.
        rotation (int): Rotation des étiquettes de l'axe X.
        """
        plt.figure(figsize=(10, 6))
        data.plot(kind='bar', color='skyblue')
        plt.title("Nombre d'entreprises par Ville")
        plt.xlabel("Ville")
        plt.ylabel("Nombre d'entreprises")
        plt.xticks(rotation=rotation)
        plt.show()

    @staticmethod
    def plot_map(data, popup_column):
        """
        Crée une carte avec des marqueurs basés sur les colonnes de latitude et longitude fournies.
        """
        if 'Latitude' not in data.columns or 'Longitude' not in data.columns or popup_column not in data.columns:
            print("Les colonnes nécessaires sont manquantes.")
            return None

        valid_data = data.dropna(subset=['Latitude', 'Longitude', popup_column])
        if valid_data.empty:
            print("Aucune donnée valide pour tracer la carte.")
            return None

        map = folium.Map(location=[valid_data['Latitude'].mean(), valid_data['Longitude'].mean()], zoom_start=6)
        for _, row in valid_data.iterrows():
            folium.Marker([row['Latitude'], row['Longitude']], popup=str(row[popup_column])).add_to(map)
        return map

    @staticmethod
    def plot_bar_chart_services(dataframe, top_n):
        """
        Trace un diagramme en barres des top_n services les plus utilisés par les entreprises.
        """
        cols_to_exclude = ['Entreprise', 'Url', 'Location', 'TrustScore', 'NombreAvis', 'ServicesProposes', 'Latitude', 'Longitude']
        cols_for_sum = [col for col in dataframe.columns if col not in cols_to_exclude]
        service_counts = dataframe[cols_for_sum].sum().sort_values(ascending=False)
        top_services = service_counts.head(top_n)
        plt.figure(figsize=(10, 8))
        top_services.plot(kind='bar', color='skyblue')
        plt.title('Nombre d\'entreprises par Service Proposé')
        plt.xlabel('Service')
        plt.ylabel('Nombre d\'entreprises')
        plt.xticks(rotation=45)
        plt.show()  # Correction: ajout des parenthèses

    @staticmethod
    def histogramme_trustScore(TrustScore):
        """
        Trace un histogramme de la distribution des scores de confiance.
        """
        plt.figure(figsize=(8, 4))
        sns.histplot(TrustScore, kde=True, color='blue')
        plt.title('Distribution de TrustScore')
        plt.xlabel('TrustScore')
        plt.ylabel('Fréquence')
        plt.show()



    @staticmethod
    def diagramme_Pays(Pays,top_n):
     # Préparation des données
        data_counts = Pays.value_counts().head(top_n)  # Top 10 pour simplifier la vue

        # Création du diagramme
        plt.figure(figsize=(10, 8))
        sns.barplot(x=data_counts.index, y=data_counts.values)
        plt.title('Répartition des Pays dans les Données')
        plt.xlabel('Pays')
        plt.ylabel('Nombre d\'Occurrences')
        plt.xticks(rotation=90)  # Rotation des étiquettes pour une meilleure lisibilité
        plt.show()


    @staticmethod
    def Pie_Chart_Pays(Pays,top_n):
        # Filtrage et préparation des données
        pie_data = Pays.value_counts().head(top_n)  # Top 10 pour simplifier la vue
        
        # Création du pie chart
        plt.figure(figsize=(8, 8))
        plt.pie(pie_data, labels=pie_data.index, autopct='%1.1f%%', startangle=140)
        plt.title('Top dans les données')
        plt.show()
     

    @staticmethod
    def countplo_notsClients(Note):
        sns.countplot(x=Note)
        plt.show()


    @staticmethod
    def plot_distributionDate(data, column, rotation=0):
        """
        Génère un graphique de distribution pour la colonne spécifiée du DataFrame.
        :param data: DataFrame contenant les données à visualiser.
        :param column: Nom de la colonne pour laquelle générer le graphique.
        :param rotation: Rotation des labels de l'axe des x, par défaut 0.
        """
        # Nettoyer et préparer le nom de la colonne pour l'affichage
        NomG = column.replace('_', ' ').capitalize()

        plt.figure(figsize=(10, 6))
        sns.countplot(x=column, data=data, palette='viridis')
        plt.title(f"Distribution des avis par {NomG}")
        plt.xlabel(NomG)
        plt.ylabel('Nombre d\'avis')
        plt.xticks(rotation=rotation)
        plt.show()




    @staticmethod
    def plot_word_cloud(data_frame, column):

        # Combinez tous les textes de la colonne spécifiée
        text = " ".join(review for review in data_frame[column].dropna())
        
        # Créer l'objet WordCloud
        wordcloud = WordCloud(background_color="black",width=800, height=400, max_words=50, stopwords=set(stopwords.words('french')), max_font_size=50, random_state=42).generate(text)
    

        # Afficher le nuage de mots
        plt.figure(figsize=(10, 5))
        plt.imshow(wordcloud)
        plt.show()


    @staticmethod
    def plot_word_frequency(data_frame, column, num_words=50):
        # Assurez-vous que la colonne est correctement spécifiée et que les données sont déjà tokenizées
        words = []
        for tokens_list in data_frame[column].dropna():  # Élimine les valeurs nulles
            if tokens_list:  # Vérifie que la liste n'est pas vide
                words.extend(tokens_list)  # Ajoute chaque mot dans la liste globale

        # Compter les fréquences des mots
        word_counts = Counter(words)
        
        # Sélectionner les mots les plus fréquents
        if word_counts:
            common_words = word_counts.most_common(num_words)
            words, counts = zip(*common_words)  # Dézippe les mots et leurs comptages

            # Créer l'histogramme
            plt.figure(figsize=(10, 5))
            plt.bar(words, counts)
            plt.xlabel('Mots')
            plt.ylabel('Fréquences')
            plt.title(f'Top {num_words} des mots les plus fréquents')
            plt.xticks(rotation=45)
            plt.show()
        else:
            print("Pas de mots à afficher. La liste des mots est vide.")
    

if __name__ == '__main__':
    """
    df = pd.read_csv("df_Intreprise_transformed_testeClasser.csv")
    print(df.head())
    # Histogramme pour TrustScore
    VisualisationGeneral.histogramme_trustScore(df['TrustScore'])

    # Diagramme en barres pour la localisation
    location_counts = df['Location'].value_counts()
    VisualisationGeneral.plot_bar_chart(location_counts)

    # Diagramme en barres des services
    VisualisationGeneral.plot_bar_chart_services(df, 20)

    # Carte pour les localisations
    valid_data = df.dropna(subset=['Latitude', 'Longitude'])
    map_obj = VisualisationGeneral.plot_map(valid_data, popup_column='Location')
    if map_obj:
        map_obj.save('map.html')
        print("Carte sauvegardée en tant que map.html.")
    else:
        print("Aucune donnée valide pour créer la carte.")
    """

    dfavis = pd.read_csv("df_avis_TexteMininge.csv")
    print(dfavis.head())
        # Histogramme pour pays
    VisualisationGeneral.diagramme_Pays(dfavis['Pays'],10)

        # Pie_Chart_Pays
    VisualisationGeneral.Pie_Chart_Pays(dfavis['Pays'],10)
    VisualisationGeneral.countplo_notsClients(dfavis['Note'])

    VisualisationGeneral.plot_distributionDate(dfavis, 'month', rotation=45)
    VisualisationGeneral.plot_distributionDate(dfavis, 'weekday', rotation=45)
    VisualisationGeneral.plot_distributionDate(dfavis, 'day', rotation=45)
    VisualisationGeneral.plot_distributionDate(dfavis, 'hour', rotation=45)
    VisualisationGeneral.plot_word_cloud(dfavis, 'tokens_no_stop')
    VisualisationGeneral.plot_word_frequency(dfavis, 'tokens_no_stop')
