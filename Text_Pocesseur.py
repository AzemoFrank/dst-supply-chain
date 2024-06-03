import pandas as pd
import re
from gensim import corpora, models
import emoji
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import collections


class TextMiningProcessus:
    """
    Classe pour le prétraitement et la vectorisation de texte dans un DataFrame.
    Utilise des techniques NLP pour transformer le texte en vecteurs numériques.
    """
    def __init__(self, data_frame, column_name, language='french'):
        """
        Initialise la classe avec le DataFrame et les paramètres de traitement du texte.
        """
        if column_name not in data_frame.columns:
            raise ValueError(f"Le DataFrame ne contient pas la colonne spécifiée: {column_name}")
        
        self.df = data_frame.copy()
        self.column = column_name
        self.language = language
       

    def preprocess_Data_Extraction(self, use_lda=True):
        """
        Exécute toutes les étapes de prétraitement et vectorise le texte.
        """
        self.df['text_sentiment'] = self.df[self.column].apply(self.analyze_text_sentiment)
        self.process_emojis()
        self.extract_text_features()

        if use_lda:
            lda_model = self.perform_lda()
            return self.df, lda_model
        return self.df


    
    
    def analyze_text_sentiment(self,text):
        """
        Analyze the sentiment of text using the VADER sentiment analysis tool.
        - VADER est un outil populaire pour l'analyse de sentiment des textes écrits en langage naturel,
        - efficace pour les textes des réseaux sociaux. 
        - Il est inclus dans la bibliothèque NLTK
        - et peut être utilisé pour obtenir rapidement une mesure du sentiment.
        """
        analyzer = SentimentIntensityAnalyzer()
        # Appliquer l'analyseur sur la colonne de contenu d'avis
        return analyzer.polarity_scores(text)['compound']
    


    def process_emojis(self):
        """
        Processes emojis by extracting them and converting to text, then analyzing sentiment.
        """
        self.df['emojis'] = self.df[self.column].apply(self.extract_emojis)
        self.df['emoji_text'] = self.df['emojis'].apply(self.convert_emojis_to_text)
        self.df['emoji_sentiment'] = self.df['emoji_text'].apply(self.process_emoji_sentiments)
        self.df['emoji_counts'] = self.df['emojis'].apply(self.count_emojis)
        self.df['emoji_ratio'] = self.df['emojis'].apply(lambda x: len(x) if isinstance(x, str) else 0) / self.df[self.column].str.split().apply(len).replace(0, 1)
        #df_avis['emoji_ratio'] = df_avis['emojis'].apply(lambda x: len(x) if isinstance(x, str) else 0) / df_avis['Contenu_avis'].str.split().apply(len).replace(0, 1)

        self.df['emoji_diversity'] = self.df['emoji_counts'].apply(len)




    @staticmethod
    def extract_emojis(text):
        """
        Extract emojis from the text.
        """
        if text is None:
            return ''
        return ''.join(e['emoji'] for e in emoji.emoji_list(text))

    @staticmethod
    def convert_emojis_to_text(emojis):
        """
        Convert emojis to descriptive text.
        """
        return emoji.demojize(emojis, delimiters=("", " "))

    def process_emoji_sentiments(self, emoji_text):
        """
        Analyze the sentiment of emojis converted to text using the VADER sentiment analysis tool.
        """
        analyzer = SentimentIntensityAnalyzer()
        return analyzer.polarity_scores(emoji_text)['compound']
    

    @staticmethod
    def count_emojis(emojis):
        """
        Count the occurrences of each emoji.
        """
        if isinstance(emojis, str):  # S'assurer que l'entrée est une chaîne
            return collections.Counter(emojis)
        return collections.Counter()  # Retourner un compteur vide pour les entrées non valides

   



    def extract_text_features(self):
        """
        Extracts text features like punctuations, counts of uppercase and lowercase words.
        """
        self.df['punctuations'] = self.df[self.column].apply(self.extract_punctuations)
        self.df['exclamation_marks'] = self.df[self.column].apply(self.count_exclamation_marks)
        self.df['question_marks'] = self.df[self.column].apply(self.count_question_marks)
        self.df['exclamation_ratio'] = self.df['exclamation_marks'] / self.df[self.column].str.split().apply(len).replace(0, 1) # éviter la division par zéro,
        self.df['question_ratio'] = self.df['question_marks'] / self.df[self.column].str.split().apply(len).replace(0, 1)
        self.df['ellipsis'] = self.df[self.column].apply(self.count_ellipsis)
        self.df['exclamation_series'] = self.df[self.column].apply(self.count_exclamation_series)
        self.df['quotes'] = self.df[self.column].apply(self.count_quotes)
        self.df['parentheses'] = self.df[self.column].apply(self.count_parentheses)
        self.df['combined_punctuation'] = self.df[self.column].apply(self.count_combined_punctuation)
        self.df['uppercase_words'] = self.df[self.column].apply(self.count_uppercase_words)
        self.df['lowercase_words'] = self.df[self.column].apply(self.count_lowercase_words)
        self.df['uppercase_ratio'] = self.df['uppercase_words'] / self.df[self.column].str.split().apply(len).replace(0, 1)
        self.df['lowercase_ratio'] = self.df['lowercase_words'] / self.df[self.column].str.split().apply(len).replace(0, 1)



    def count_exclamation_marks(self, text):
        return text.count('!')

    def count_question_marks(self, text):
        return text.count('?')
    
    def count_ellipsis(self, text):
        return text.count('...')

    def count_exclamation_series(self, text):
        import re
        return len(re.findall(r'!{2,}', text))

    def count_quotes(self, text):
        return text.count('"') + text.count("'")  # Compte tous les guillemets simples et doubles

    def count_parentheses(self, text):
        return text.count('(') + text.count(')')  # Compte toutes les parenthèses ouvrantes et fermantes

    def count_combined_punctuation(self, text):
        return len(re.findall(r'\?\!|\!\?', text))
        
    def extract_punctuations(self, text):
        """
        Extract strictly punctuations from the text.
        """
        return ''.join(re.findall(r'[\.\,\;\:\!\?\(\)\[\]\{\}\'\"\\\/\-\—\–]', text))

    @staticmethod
    def count_uppercase_words(text):
        """
        Count uppercase words in the text.
        """
        return sum(1 for word in text.split() if word.isupper())

    @staticmethod
    def count_lowercase_words(text):
        """
        Count lowercase words in the text.
        """
        return sum(1 for word in text.split() if word.islower())



    
    def perform_lda(self, num_topics=5):
        # Préparation des données pour LDA
        processed_docs = [doc.split() for doc in self.df[self.column]]
        dictionary = corpora.Dictionary(processed_docs)
        corpus = [dictionary.doc2bow(doc) for doc in processed_docs]
        lda_model = models.LdaModel(corpus, num_topics=num_topics, id2word=dictionary, passes=15, random_state=100)
        self.df['topics'] = [lda_model.get_document_topics(bow) for bow in corpus]
        topic_keywords = self.get_topic_keywords(lda_model)
        lda_model.save('lda_model.model')
        self.label_avises_with_topics(topic_keywords)
        return lda_model

    def get_topic_keywords(self, lda_model, num_words=10):
        topics = lda_model.show_topics(num_topics=-1, num_words=num_words, formatted=False)
        topic_keywords = {}
        for topic_id, topic in topics:
            topic_keywords[topic_id] = [word for word, prob in topic]
            print(f"Topic {topic_id}: {', '.join(topic_keywords[topic_id])}")
        return topic_keywords

    def label_avises_with_topics(self, topic_keywords):
        def map_topic_to_service(topic_id):
            keywords = topic_keywords[topic_id]
            services_count = {service: sum(keyword in service for keyword in keywords) for service in self.df['ServicesProposes'].unique()}
            return max(services_count, key=services_count.get, default="Général")

        self.df['dominant_topic_id'] = self.df['topics'].apply(lambda topics: max(topics, key=lambda x: x[1])[0])
        self.df['dominant_service_topic'] = self.df['dominant_topic_id'].apply(map_topic_to_service)




# Exemple d'utilisation
if __name__ == '__main__':
    df_avis_class_test = pd.read_csv("df_avis_jointure.csv")
    
    text_processor = TextMiningProcessus(df_avis_class_test, 'Contenu_avis')
    results = text_processor.preprocess_Data_Extraction(use_lda=False)
    if isinstance(results, tuple):
        processed_df, lda_model = results  # Séparer le DataFrame et le modèle LDA
    else:
        processed_df = results  # Aucun modèle LDA retourné, seul le DataFrame est retourné

    # Maintenant vous pouvez utiliser la méthode head() sur le DataFrame correctement
    print(processed_df.head())
    processed_df.to_csv('df_avis_TexteMining.csv', index=False)












































