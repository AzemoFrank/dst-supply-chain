from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer, PorterStemmer
from sklearn.feature_extraction.text import TfidfVectorizer
import nltk
import pandas as pd

# Assurez-vous de télécharger les ressources nécessaires
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

class TextMiningProcessus:
    def __init__(self, data_frame, column_name, language='french'):
        self.df = data_frame
        self.column = column_name
        self.language = language
        self.lemmatizer = WordNetLemmatizer()
        self.stemmer = PorterStemmer()
        self.vectorizer = TfidfVectorizer(max_features=100, min_df=5, max_df=0.9)
        self.stop_words = set(stopwords.words(language))

    def tokenize(self):
        """Tokenize the text."""
        self.df['tokens'] = self.df[self.column].apply(lambda x: word_tokenize(str(x).lower()) if x is not None else [])

    def remove_stopwords(self):
        """Remove stopwords from tokens."""
        self.df['tokens_no_stop'] = self.df['tokens'].apply(
            lambda tokens: [word for word in tokens if word not in self.stop_words]
        )

    def lemmatize(self):
        """Lemmatize the tokens."""
        self.df['lemmatized'] = self.df['tokens_no_stop'].apply(
            lambda x: [self.lemmatizer.lemmatize(word) for word in x]
        )

    def stem(self):
        """Stem the tokens."""
        self.df['stemmed'] = self.df['tokens_no_stop'].apply(
            lambda x: [self.stemmer.stem(word) for word in x]
        )

    def vectorize_text(self):
        """Vectorize the text."""
        if 'lemmatized' in self.df:
            self.df['vectorized'] = list(self.vectorizer.fit_transform(self.df['lemmatized'].apply(lambda x: ' '.join(x))).toarray())
        else:
            self.df['vectorized'] = list(self.vectorizer.fit_transform(self.df['stemmed'].apply(lambda x: ' '.join(x))).toarray())

    def preprocess_and_vectorize(self, use_stemming=False):
        """Run all preprocessing steps and vectorize."""
        self.tokenize()
        self.remove_stopwords()
        if use_stemming:
            self.stem()
        else:
            self.lemmatize()
        self.vectorize_text()

# Test de la classe
if __name__ == '__main__':
    df_avis_class_test = pd.read_csv("df_avis_transformedprepro.csv")
    text_processor = TextMiningProcessus(df_avis_class_test, 'Contenu_avis', 'french')
    text_processor.preprocess_and_vectorize()
    print(df_avis_class_test.head())
    df_avis_class_test.to_csv('df_avis_TexteMininge.csv', index=False)