import faiss
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from transformers import GPT2LMHeadModel, GPT2Tokenizer
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

def retrieve_logs(user_query, top_k=5):
    # Sorguyu vektörize et
    query_vec = vectorizer.transform([user_query]).toarray().astype('float32')
    
    # FAISS'ten en yakın log kayıtlarını al
    _, I = index.search(query_vec, top_k)
    
    # En yakın log kayıtlarını al
    similar_logs = weblogs.iloc[I[0]]
    return similar_logs

def generate_response(logs, user_query):
    if "oldest" in user_query.lower() and "delete" in user_query.lower():
        # DELETE isteklerini filtrele
        delete_logs = logs[logs['RequestMethod'] == 'DELETE']
        
        if not delete_logs.empty:
            # En eski tarihe sahip kaydı bul
            oldest_log = delete_logs.loc[delete_logs['Date'].idxmin()]
            
            response = f"""Based on the relevant logs retrieved, the oldest DELETE request in the dataset occurred on:

Date: {oldest_log['Date']}
Time: {oldest_log['Time']}

This request had the following details:
- IP: {oldest_log['IP']}
- Status Code: {oldest_log['StatusCode']}
- Request Method: {oldest_log['RequestMethod']}
- URL: {oldest_log['URL']}
- Size: {oldest_log['Size']}

It's important to note that this is the oldest DELETE request among the logs provided in the sample. The actual oldest request in the entire dataset may be different if there are earlier entries not shown in this sample."""
        else:
            response = "No DELETE requests were found in the retrieved logs."
    else:
        response = "I'm sorry, but I couldn't find a specific answer to your query in the logs."
    
    return response

def rag_response(user_query):
    # İlgili log kayıtlarını al
    logs = retrieve_logs(user_query)
    
    # Yanıt oluştur
    response = generate_response(logs, user_query)
    
    return response

# Kullanıcı sorgusu
user_query = "When is the oldest DELETE request?"
response = rag_response(user_query)
print("Kullanıcı Sorgusu:", user_query)
print("\nRAG Yanıtı:", response)


