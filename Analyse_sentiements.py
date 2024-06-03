import pandas as pd
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer
from nltk.stem.snowball import FrenchStemmer
from nltk.stem import WordNetLemmatizer 
from sklearn.feature_extraction.text import TfidfVectorizer
from gensim import corpora, models
import emoji
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import collections

# Téléchargement des ressources nécessaires pour NLTK
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

# Importation de la classe externe
from Text_Pocesseur import TextMiningProcessus

class Analayse_Sentiment_Processus:
    def __init__(self, data_frame, column_name, language='french', max_features=100, min_df=5, max_df=0.9):
        if column_name not in data_frame.columns:
            raise ValueError(f"Le DataFrame ne contient pas la colonne spécifiée: {column_name}")
        
        self.df = data_frame.copy()
        self.column = column_name
        self.language = language
        self.lemmatizer = WordNetLemmatizer()
        self.stemmer = FrenchStemmer()
        self.vectorizer = TfidfVectorizer(max_features=max_features, min_df=min_df, max_df=max_df)
        self.stop_words = set(stopwords.words(language))
        self.tokenize = RegexpTokenizer(r'\w{4,}')



    def preprocess_and_vectorize(self, use_stemming=False):
         # Initialisation des données emoji et ponctuation
        self.initialize_emoji_and_punctuation_columns()
        self.update_stop_words()
        # Preprocess text and vectorize
        print("Starting tokenization...")
        self.token()
        print("Tokens processed:", self.df['tokens'].head())

        print("Reconstructing sentences...")
        self.reconstruct_sentences()
        print("Sentences reconstructed:", self.df['reconstructed'].head())
        self.apply_stem_or_lemma(use_stemming)
        self.vectorize_text()

        return self.df




    
     # Vérifier et initialiser les colonnes emojis et punctuations
    def initialize_emoji_and_punctuation_columns(self):
        # Assurer que les colonnes emoji et ponctuation sont des listes (même vides)
        text_processor = TextMiningProcessus(self.df, self.column)
        if 'emojis' not in self.df.columns:
            self.df['emojis'] = self.df[self.column].apply(text_processor.extract_emojis)
        if 'punctuations' not in self.df.columns:
            self.df['punctuations'] = self.df[self.column].apply(text_processor.extract_punctuations)
        
        # Convertir NaN en listes vides pour éviter les erreurs lors de l'itération
        self.df['emojis'] = self.df['emojis'].apply(lambda x: x if isinstance(x, list) else [])
        self.df['punctuations'] = self.df['punctuations'].apply(lambda x: x if isinstance(x, list) else [])


    def update_stop_words(self):
        # Extraction des emojis et ponctuations uniques
        emojis_unique = set(emoji for sublist in self.df['emojis'] for emoji in sublist)
        punctuations_unique = set(punc for sublist in self.df['punctuations'] for punc in sublist)

        # Extraction des chiffres uniques
        digits = set(re.findall(r'\d', ' '.join(self.df[self.column].astype(str))))

        # Ajout aux stop words
        additional_stop_words = {"@", "*", "(", ")", ">", "<", "/", "=", "--", "©", "~", "\\", "\\\\"}
        self.stop_words.update(emojis_unique, punctuations_unique, digits, additional_stop_words)


    def token(self):
        # Tokenize text considering stopwords, emojis, and punctuations
        self.df['tokens'] = self.df[self.column].apply(lambda text: [word for word in self.tokenize.tokenize(text.lower()) if word not in self.stop_words])
    
    def reconstruct_sentences(self):
        # Reconstruct sentences from tokens
        self.df['reconstructed'] = self.df['tokens'].apply(lambda tokens: ' '.join(tokens))
    
    def apply_stem_or_lemma(self, use_stemming):
        if use_stemming:
            self.df['stemmed'] = self.df['tokens'].apply(lambda tokens: [self.stemmer.stem(token) for token in tokens])
        else:
            self.df['lemmatized'] = self.df['tokens'].apply(lambda tokens: [self.lemmatizer.lemmatize(token) for token in tokens])

    def vectorize_text(self):
        # Convert text data into numerical format using TF-IDF vectorization
        text_data = self.df['tokens'] if 'tokens' in self.df.columns else self.df['stemmed']
        self.df['vectorized'] = list(self.vectorizer.fit_transform([' '.join(tokens) for tokens in text_data]).toarray())

# Exemple d'utilisation
if __name__ == '__main__':
    df_avis = pd.read_csv("Df_aviscoliweb_TexteMining.csv")
    print(df_avis.head())
    sentiment_analyzer = Analayse_Sentiment_Processus(df_avis, 'Contenu_avis')
    df_modified =sentiment_analyzer.preprocess_and_vectorize(use_stemming=True)
    
    print(df_modified.head())
    df_modified.to_csv('Df_aviscoliweb_TexteMining_AnalyseSentiment.csv', index=False)

