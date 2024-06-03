from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.preprocessing import MultiLabelBinarizer
from ast import literal_eval
import re
import pandas as pd
from spellchecker import SpellChecker

class EntreprisePreprocessor(BaseEstimator, TransformerMixin):
    """
    Un préprocesseur pour nettoyer et transformer les données des entreprises, adapté pour être utilisé dans des pipelines de prétraitement de données.

    Attributs :
        lower_case (bool): Si True, convertit les noms d'entreprise en minuscules.
        mlb (MultiLabelBinarizer): Utilisé pour appliquer l'encodage one-hot aux services proposés par les entreprises.
    """
    
    def __init__(self, lower_case=True):
        """
        Initialise l'EntreprisePreprocessor avec la possibilité de spécifier si les noms doivent être convertis en minuscules.

        Paramètres :
            lower_case (bool): Si True (défaut), les noms d'entreprises sont convertis en minuscules.
        """
        self.lower_case = lower_case
        self.mlb = MultiLabelBinarizer()  # Initialiser ici pour utiliser dans transform

    def fit(self, X, y=None):
        """
        Prépare le préprocesseur avec les données nécessaires, spécifiquement en adaptant le MultiLabelBinarizer avec tous les services proposés.

        Paramètres :
            X (DataFrame): Le DataFrame contenant les données à prétraiter.
            y : Ignoré, présent pour compatibilité avec l'API de scikit-learn.

        Retour :
            self (EntreprisePreprocessor): L'instance de préprocesseur configurée.
        """
        if 'ServicesProposes' in X:
            services = X['ServicesProposes'].apply(literal_eval).apply(lambda x: [s.lower().strip() for s in x])
            self.mlb.fit(services)
        return self

    def clean_location(self, location):
        """
        Nettoie et normalise la colonne de localisation.

        Paramètres :
            location (str): La chaîne de caractères de localisation à nettoyer.

        Retour :
            (str): La localisation nettoyée.
        """
        location = location.title().strip()
        location = location.replace('St.', 'St. ')
        words = location.split()
        for i, word in enumerate(words):
            if word.lower() in ['de', 'du', 'le', 'la', 'les', 'et']:
                words[i] = word.lower()
        return ' '.join(words)

   
    def clean_text(self,text):
        """Nettoie le texte en supprimant les URL, les balises HTML, et en normalisant le texte pour divers usages, y compris la vérification orthographique."""
        if not isinstance(text, str):
            text = str(text) if text is not None else ""
        
        text = text.lower()
        text = re.sub(r'http\S+', '', text)  # Remove URLs
        text = re.sub(r'<[^>]+>', '', text)  # Remove HTML tags
        text = re.sub(r'\bwww\.\S+\.\S+', '', text)  # Remove web addresses
        text = re.sub(r'\.\S+', '', text)  # Careful with removing all post-dot text
        text = re.sub(r'home\s*\|\s*', '', text)  # Example of specific removal
        #text = re.sub(r'[^a-zA-Z\s]', '', text)  # Remove non-alphabetic characters for general text
        text = re.sub(r'\s+', ' ', text).strip()  # Normalize whitespace

        # Vérifier l'orthographe
        #spell = SpellChecker()
       # words = text.split()
        #misspelled = spell.unknown(words)
        #corrected_text = ' '.join([spell.correction(word) if word in misspelled and spell.correction(word) is not None else word for word in words])

        return text #corrected_text

    def transform(self, X):
        """
        Applique les transformations de nettoyage sur le DataFrame fourni.

        Paramètres :
            X (DataFrame): Les données à transformer.

        Retour :
            (DataFrame): Le DataFrame transformé avec les noms d'entreprises et localisations nettoyés, et avec les services encodés.
        """
        X_transformed = X.copy()
        X_transformed['Entreprise'] = X_transformed['Entreprise'].apply(self.clean_text)
        X_transformed['Location'] = X_transformed['Location'].apply(self.clean_location)
        #Rechercher et éliminer les enregistrements en double pour éviter la redondance.
        X_transformed = X_transformed.drop_duplicates(subset=['Entreprise'], keep='last')
        X_transformed['ServicesProposes'] = X_transformed['ServicesProposes'].apply(literal_eval)
        """ 
       if 'ServicesProposes' in X_transformed:
            X_transformed['ServicesProposes'] = X_transformed['ServicesProposes'].apply(literal_eval)
            X_transformed['ServicesProposes'] = X_transformed['ServicesProposes'].apply(
                lambda x: [s.lower().strip() for s in x])
            # Apply one-hot encoding
            services_encoded = pd.DataFrame(self.mlb.transform(X_transformed['ServicesProposes']),
                                            columns=self.mlb.classes_,
                                            index=X_transformed.index)
            X_transformed = X_transformed.join(services_encoded)
            #X_transformed.drop('ServicesProposes', axis=1, inplace=True)  # Optional: remove original column
        """

        return X_transformed


# auto testing
if __name__ == '__main__':
    df = pd.read_csv("entreprises.csv")
    
    # Création de l'instance du préprocesseur
    preprocessor = EntreprisePreprocessor()
    
    # Adapter le préprocesseur
    preprocessor.fit(df)
    
    # Transformer les données
    transformed_df = preprocessor.transform(df)
    
    # Afficher le DataFrame transformé
    print(transformed_df)





