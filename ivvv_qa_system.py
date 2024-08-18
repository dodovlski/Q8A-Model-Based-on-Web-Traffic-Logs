from iii_vectorization import create_faiss_index
from iv_retrieval import load_faiss_index, retrieve_documents
from ivv_generation import generate_answer
import pandas as pd

def answer_question(query):
    data_file = 'data/cleaned_data.csv'
    index_file = 'data/cleaned_data_faiss.index'
    
    vectorizer = create_faiss_index(data_file, index_file)
    index = load_faiss_index(index_file)
    
    log_data = pd.read_csv(data_file)
    documents = log_data['LOG_CONTENT'].tolist()
    
    retrieved_docs = retrieve_documents(query, vectorizer, index, documents)
    context = " ".join(retrieved_docs)
    
    answer = generate_answer(query, context)
    return answer
