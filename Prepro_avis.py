import pandas as pd
import numpy as np
import re
from langdetect import detect, DetectorFactory, LangDetectException
import emoji
import pycountry
from sklearn.base import BaseEstimator, TransformerMixin
from prepro_entreprises import EntreprisePreprocessor  # Assurez-vous que le chemin d'importation est correct

# Pour la reproductibilité des résultats de langdetect
DetectorFactory.seed = 0

class AvisPreprocessor(BaseEstimator, TransformerMixin):
    def __init__(self, fill_value='Inconnu'):
        """
        Initialise l'AvisPreprocessor avec une valeur par défaut pour remplir les champs manquants.
        Paramètres :
            fill_value (str) : Valeur utilisée pour remplir les champs 'Pays' manquants. Par défaut à 'Inconnu'.
        """
        self.fill_value = fill_value
        self.preprocessor = EntreprisePreprocessor()

   

    def detect_language(self, text):
        """Détecte la langue du texte."""
        if len(text.strip()) < 3:
            return 'Unknown'  # Retourne 'Unknown' si le texte est trop court
        try:
            return detect(text)
        except LangDetectException as e:
            return 'Unknown'
        except Exception as e:
            return 'Unknown'

    @staticmethod
    def extract_emojis(text):
        """Extract emojis from the text."""
        emojis = emoji.emoji_list(text)  # Cette méthode retourne une liste de dictionnaires pour chaque emoji
        return ''.join(e['emoji'] for e in emojis)  # Concatène les emojis en une seule chaîne

    @staticmethod
    def convert_emojis_to_text(emojis):
        """Convert emojis to descriptive text."""
        return emoji.demojize(emojis, delimiters=("", " "))  # Convertit les emojis en texte descriptif



    @staticmethod
    def validate_language_code(code):
        """Vérifie si un code de langue est un code ISO 639-1 ou ISO 639-2 valide."""
        return pycountry.languages.get(alpha_2=code) or pycountry.languages.get(alpha_3=code) is not None

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        """Applique les transformations pour nettoyer et analyser les données d'avis."""
        X_transformed = X.copy()
        X_transformed['Nom_Entreprise'] = X_transformed['Nom_Entreprise'].apply(lambda x: self.preprocessor.clean_text(str(x)) if pd.notna(x) else x)
        X_transformed['Nom_Client'] = X_transformed['Nom_Client'].apply(lambda x: self.preprocessor.clean_text(str(x)) if pd.notna(x) else self.fill_value)
        X_transformed['Pays'] = X_transformed['Pays'].fillna(self.fill_value)
        X_transformed['Date'] = pd.to_datetime(X_transformed['Date'])

        # Extraction de caractéristiques à partir de la date
        X_transformed["year"] = X_transformed['Date'].dt.year
        X_transformed["month"] = X_transformed['Date'].dt.month
        X_transformed["weekday"] = X_transformed['Date'].dt.weekday
        X_transformed["weekend"] = np.where(X_transformed["weekday"].isin([5, 6]), 1, 0)
        X_transformed["day"] = X_transformed['Date'].dt.day
        X_transformed["hour"] = X_transformed['Date'].dt.hour

        # Extraction des emojis
        X_transformed['emojis'] = X_transformed['Contenu_avis'].apply(self.extract_emojis)
        # Conversion des emojis en texte descriptif
        X_transformed['emojis_text'] = X_transformed['emojis'].apply(self.convert_emojis_to_text)

        # Appliquez preprocess_text en s'assurant que les inputs sont des chaînes
        X_transformed['Titre_avis'] = X_transformed['Titre_avis'].apply(lambda x: self.preprocessor.clean_text(x) if pd.notna(x) else "")
        X_transformed['Contenu_avis'] = X_transformed['Contenu_avis'].apply(lambda x: self.preprocessor.clean_text(x) if pd.notna(x) else "")
        # Remplacer le contenu de 'contenu_avis' par celui de 'titre_avis' quand 'contenu_avis' contient 'non'
        X_transformed['Contenu_avis'] = np.where(X_transformed['Contenu_avis'].str.contains('non'), X_transformed['Titre_avis'], X_transformed['Contenu_avis'])
        # Supprimer les lignes où la colonne 'Contenu_avis' contient des NaN
        X_transformed = X_transformed.dropna(subset=['Contenu_avis'])
        # Détection de la langue et extraction des emojis
        X_transformed['Langue'] = X_transformed['Contenu_avis'].apply(self.detect_language)
           # Extraction des emojis
        X_transformed['extracted_emojis'] = X_transformed['Contenu_avis'].apply(self.extract_emojis)

        # Convertir les emojis en texte descriptif
        X_transformed["emojis_text"] = X_transformed['extracted_emojis'].apply(lambda text: emoji.demojize(text, delimiters=("", " ")))


        return X_transformed

if __name__ == '__main__':
    # Test des transformations
    df_test = pd.read_csv("avis.csv")
    print(df_test.head())
    print(df_test.info())
    print(df_test.isna().sum())

    preprocessor = AvisPreprocessor()
    transformed_df = preprocessor.transform(df_test)

    print("\n--- Vérifications Après Transformation ---")
    print("Noms d'entreprises nettoyés:", transformed_df['Nom_Entreprise'].tolist())
    print("Noms de clients nettoyés:", transformed_df['Nom_Client'].tolist())
    print("Pays après remplissage des valeurs manquantes:", transformed_df['Pays'].tolist())
    print("Dates converties en datetime:", transformed_df['Date'].dtypes)
    print("avis nettoi:", transformed_df['Contenu_avis'][0])
    print("Titreavis netoi:", transformed_df['Titre_avis'][0])
    print(transformed_df.head())
    print(transformed_df.info())
    print(transformed_df.isna().sum())
    transformed_df.to_csv('df_avis_Preprocessing1.csv', index=False)