import faiss
import pandas as pd

def load_faiss_index(index_file='cleaned_data_faiss.index'):
    index = faiss.read_index(index_file)
    return index

def retrieve_documents(query, vectorizer, index, documents, top_k=5):
    query_vector = vectorizer.transform([query]).toarray().astype('float32')
    distances, indices = index.search(query_vector, top_k)
    return [documents[i] for i in indices[0]]
