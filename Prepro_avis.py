import pandas as pd
import numpy as np
import re
from sklearn.base import BaseEstimator, TransformerMixin
from prepro_entreprises import EntreprisePreprocessor  # Assurez-vous que le chemin d'importation est correct
from langdetect import detect, LangDetectException
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer


nltk.download('vader_lexicon')  # Télécharger le lexique de VADER une seule fois


class AvisPreprocessor(BaseEstimator, TransformerMixin):
    def __init__(self, fill_value='Inconnu'):
        """
        Initialise l'AvisPreprocessor avec une valeur par défaut pour remplir les champs manquants.
        Paramètres :
            fill_value (str) : Valeur utilisée pour remplir les champs 'Pays' manquants. Par défaut à 'Inconnu'.
        """
        self.fill_value = fill_value
        self.preprocessor = EntreprisePreprocessor()

   

    
    
    def transform(self, X):
        """Applique les transformations pour nettoyer et analyser les données d'avis."""
        #s'assurer que les colonnes attendues sont présentes avant de tenter des opérations dessus.
        required_columns = ['Nom_Entreprise', 'Nom_Client', 'Pays', 'Date', 'Titre_avis', 'Contenu_avis']
        if not all(col in X.columns for col in required_columns):
            missing = list(set(required_columns) - set(X.columns))
            raise ValueError(f"Missing columns in input data: {missing}")
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

        # Appliquez preprocess_text en s'assurant que les inputs sont des chaînes
        X_transformed['Titre_avis'] = X_transformed['Titre_avis'].apply(lambda x: self.preprocessor.clean_text(x) if pd.notna(x) else "")
        X_transformed['Contenu_avis'] = X_transformed['Contenu_avis'].apply(lambda x: self.preprocessor.clean_text(x) if pd.notna(x) else "")
        # Remplacer le contenu de 'contenu_avis' par celui de 'titre_avis' quand 'contenu_avis' contient 'non'
        X_transformed['Contenu_avis'] = np.where(X_transformed['Contenu_avis'].str.contains('non'), X_transformed['Titre_avis'], X_transformed['Contenu_avis'])
        
        # Supprimer les lignes où la colonne 'Contenu_avis' contient des NaN
        X_transformed = X_transformed.dropna(subset=['Contenu_avis'])
        # Détection de la langue et extraction des emojis
        X_transformed['Langue'] = X_transformed['Contenu_avis'].apply(self.detect_language)
        # garder la langue france
        X_transformed=X_transformed[X_transformed['Langue']=='fr']
        return X_transformed
    

    
    def detect_language(self,text):
    
        """
        Detect the language of the text, handling non-string types and NaN values.
        """
        if not isinstance(text, str) or pd.isna(text):
            return 'Unknown'
        try:
            return detect(text) if len(text.strip()) > 3 else 'Unknown'
        except LangDetectException:
            return 'Unknown'





if __name__ == '__main__':
    # Test des transformations
    df_test = pd.read_csv("avis.csv")
    print(df_test.head())
    print(df_test.info())
    print(df_test.isna().sum())

    preprocessor = AvisPreprocessor()
    transformed_df = preprocessor.transform(df_test)

    print("\n--- Vérifications Après Transformation ---")

    print(transformed_df.head())
    print(transformed_df.info())
    print(transformed_df.isna().sum())
    transformed_df.to_csv('df_avis_Preprocessing1.csv', index=False)