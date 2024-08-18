import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
import faiss

def create_faiss_index(file_path='data/cleaned_data.csv', index_file='data/cleaned_data_faiss.index'):
    
    log_data = pd.read_csv(file_path)
    
    vectorizer = TfidfVectorizer()
    tfidf_vectors = vectorizer.fit_transform(log_data['LOG_CONTENT'])
    dense_vectors = tfidf_vectors.toarray().astype('float32')
    
    index = faiss.IndexFlatL2(dense_vectors.shape[1])
    index.add(dense_vectors)
    
    faiss.write_index(index, index_file)
    
    print("FAISS index successfully created and saved.")
    
    return vectorizer
