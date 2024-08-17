import faiss
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from transformers import GPT2LMHeadModel, GPT2Tokenizer, GPTNeoForCausalLM, GPT2Tokenizer

import torch

# "logdata3.csv" dosyasını "weblogs" DataFrame'ine aktar
weblogs = pd.read_csv("logdata3.csv", delimiter=",") 


# "UserAgent" ve "RandomLogNumber" sütunlarını at
weblogs.drop(["UserAgent", "RandomLogNumber"], axis=1, inplace=True)


# "Date&Time" sütununu uygun formatta "Date" ve "Time" sütunları olarak ikiye ayır
weblogs['Date&Time'] = pd.to_datetime(weblogs['Date&Time'], format='%d/%b/%Y:%H:%M:%S %z')
weblogs['Date'] = weblogs['Date&Time'].dt.date
weblogs['Time'] = weblogs['Date&Time'].dt.time

# "Date&Time" sütununu at
weblogs.drop(["Date&Time"], axis=1, inplace=True)

# Belirtilen sütunları virgülle ayırarak birleştir ve yeni bir "TEXT" sütunu oluştur
weblogs['TEXT'] = (weblogs['Date'].astype(str) + ', ' + 
                  weblogs['Time'].astype(str) + ', ' + 
                  weblogs['IP'] + ', ' + 
                  weblogs['StatusCode'].astype(str) + ', ' + 
                  weblogs['RequestMethod'] + ', ' + 
                  weblogs['URL'] + ', ' + 
                  weblogs['Size'].astype(str))


vectorizer = TfidfVectorizer()

# TEXT sütununu TF-IDF kullanarak vektörize et
tfidf_matrix = vectorizer.fit_transform(weblogs['TEXT'])

# Vektörize edilen veriyi DataFrame'e dönüştür
tfidf_df = pd.DataFrame(tfidf_matrix.toarray(), columns=vectorizer.get_feature_names_out())

# Sonucu görüntüle
# print(tfidf_df.head())

vectors = tfidf_matrix.toarray().astype('float32')

# Vektörlerin boyutunu al
d = vectors.shape[1]  # vektör boyutu

# FAISS index'i oluştur (L2 normu ile)
index = faiss.IndexFlatL2(d)

# Vektörleri FAISS index'ine ekle
index.add(vectors)

# FAISS index'ini diske kaydet
faiss.write_index(index, "faiss_index.index")

# GPT modelini ve tokenizer'ı yükle
tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
model = GPT2LMHeadModel.from_pretrained("gpt2")

# Modeli değerlendirilecek moda al (GPU kullanılıyorsa CUDA'ya taşı)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)
model.eval()

model = GPTNeoForCausalLM.from_pretrained("EleutherAI/gpt-neo-1.3B")
tokenizer = GPT2Tokenizer.from_pretrained("EleutherAI/gpt-neo-1.3B")

def retrieve_logs(user_query, top_k=5):
    # Sorguyu vektörize et
    query_vec = vectorizer.transform([user_query]).toarray().astype('float32')
    
    # FAISS'ten en yakın log kayıtlarını al
    _, I = index.search(query_vec, top_k)
    
    # En yakın log kayıtlarını al
    similar_logs = weblogs.iloc[I[0]]
    return similar_logs

def generate_response(logs, user_query):
    # Log kayıtlarını özetle
    log_summary = logs['TEXT'].head().to_string(index=False)
    
    # Daha iyi bir prompt oluştur
    context = f"""
    Analyze these web server logs and answer the user's question accurately:

    {log_summary}

    User Question: {user_query}

    Provide a concise and relevant answer based only on the information in the logs:
    """
    
    input_ids = tokenizer.encode(context, return_tensors="pt").to(device)
    
    with torch.no_grad():
        output = model.generate(
            input_ids, 
            max_length=200, 
            num_return_sequences=1, 
            no_repeat_ngram_size=2, 
            temperature=0.7,
            top_k=50,
            top_p=0.95
        )
    
    response = tokenizer.decode(output[0], skip_special_tokens=True)
    
    # Cevabı temizle ve düzenle
    response = response.split("Provide a concise and relevant answer based only on the information in the logs:")[-1].strip()
    
    return response

def rag_response(user_query):
    logs = retrieve_logs(user_query)
    response = generate_response(logs, user_query)
    return response

# Test et
user_query = "When is the oldest DELETE request?"
response = rag_response(user_query)
print("User Query:", user_query)
print("RAG Response:", response)


