import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import StandardScaler, LabelEncoder
from scipy.sparse import hstack
import faiss
import torch
from transformers import T5ForConditionalGeneration, T5Tokenizer

# CSV dosyasını okuma
weblogs = pd.read_csv("logdata3.csv")
weblogs = weblogs.drop(columns=["UserAgent", "RandomLogNumber"])

# Tarih ve zaman damgalarını uygun bir formata dönüştürün
weblogs['Date&Time'] = pd.to_datetime(weblogs['Date&Time'], format='%d/%b/%Y:%H:%M:%S %z')

# 'Date' ve 'Time' olarak ayır
weblogs['Date'] = weblogs['Date&Time'].dt.date
weblogs['Time'] = weblogs['Date&Time'].dt.time

# Eski 'Date&Time' sütununu kaldır
weblogs = weblogs.drop(columns=["Date&Time"])

weblogs_checkpoint = weblogs

# Kategorik verileri sayısallaştırma
le = LabelEncoder()
weblogs['IP_encoded'] = le.fit_transform(weblogs['IP'])
weblogs['RequestMethod_encoded'] = le.fit_transform(weblogs['RequestMethod'])

# URL'leri TF-IDF vektörlerine dönüştürme
tfidf = TfidfVectorizer(max_features=100)  # max_features'ı veri setinize göre ayarlayın
url_vectors = tfidf.fit_transform(weblogs['URL'])

# Sayısal verileri ölçeklendirme
scaler = StandardScaler()
numeric_features = ['StatusCode', 'Size']
numeric_vectors = scaler.fit_transform(weblogs[numeric_features])

# Tarih ve zaman verilerini sayısallaştırma
weblogs['Date_numeric'] = pd.to_datetime(weblogs['Date']).astype('int64') // 10**9  # int64 dönüşümü
weblogs['Time_numeric'] = weblogs['Time'].apply(lambda x: x.hour * 3600 + x.minute * 60 + x.second)

# Tüm vektörleri birleştirme
encoded_features = ['IP_encoded', 'RequestMethod_encoded', 'Date_numeric', 'Time_numeric']
all_features = hstack([
    weblogs[encoded_features].values,
    url_vectors,
    numeric_vectors
]).tocsr()

# Sonuç
print("Vektör boyutu:", all_features.shape)
print("Örnek vektör:", all_features[0].toarray())



# Vektörleri numpy array'ine dönüştürme
vectors = all_features.toarray().astype('float32')

# Vektör boyutunu alma
dimension = vectors.shape[1]

# FAISS indeksi oluşturma
index = faiss.IndexFlatL2(dimension)

# Vektörleri indekse ekleme
index.add(vectors)

# İndeksin boyutunu kontrol etme
print(f"Toplam {index.ntotal} vektör indekse eklendi.")

# İndeksi dosyaya kaydetme
faiss.write_index(index, "weblogs_index.faiss")

print("FAISS indeksi başarıyla kaydedildi.")

# İsteğe bağlı: Kaydedilen indeksi test etme
test_index = faiss.read_index("weblogs_index.faiss")
print(f"Kaydedilen indeksteki vektör sayısı: {test_index.ntotal}")

# Örnek bir sorgu yapma
k = 5  # En yakın 5 sonucu al
query_vector = vectors[0].reshape(1, -1)  # İlk vektörü sorgu olarak kullan
distances, indices = test_index.search(query_vector, k)

print(f"\nEn yakın {k} sonuç:")
for i, (d, idx) in enumerate(zip(distances[0], indices[0])):
    print(f"{i+1}. Vektör indeksi: {idx}, Uzaklık: {d}")
    
    
# FAISS indeksini yükleme
index = faiss.read_index("weblogs_index.faiss")

# T5 modelini ve tokenizer'ı yükleme
model_name = "t5-small"
tokenizer = T5Tokenizer.from_pretrained(model_name)
model = T5ForConditionalGeneration.from_pretrained(model_name)

# TF-IDF vektörizeri yeniden oluşturma
# Not: Gerçek uygulamada, bunu kaydetmiş ve yüklüyor olmalısınız
tfidf = TfidfVectorizer(max_features=100)
tfidf.fit(weblogs['URL'])

def retrieve_relevant_logs(query, k=5):
    # Sorguyu vektöre dönüştürme
    query_tfidf = tfidf.transform([query]).toarray().astype('float32')
    
    # Sorgu vektörünü FAISS indeksindeki vektörlerle aynı boyuta getirme
    query_vector = np.zeros((1, index.d), dtype='float32')
    query_vector[:, :query_tfidf.shape[1]] = query_tfidf
    
    # FAISS ile en yakın k vektörü bulma
    distances, indices = index.search(query_vector, k)
    
    # Bulunan indekslere karşılık gelen log kayıtlarını döndürme
    relevant_logs = weblogs.iloc[indices[0]].to_dict('records')
    return relevant_logs

def generate_response(query, relevant_logs):
    # Sorgu ve ilgili logları birleştirme
    context = "Query: " + query + "\nRelevant logs:\n"
    for log in relevant_logs:
        context += f"IP: {log['IP']}, Method: {log['RequestMethod']}, URL: {log['URL']}, Status: {log['StatusCode']}, Size: {log['Size']}, Date: {log['Date']}, Time: {log['Time']}\n"
    
    # T5 modelini kullanarak yanıt oluşturma
    input_ids = tokenizer.encode("summarize: " + context, return_tensors="pt", max_length=512, truncation=True)
    output = model.generate(input_ids, max_length=150, num_return_sequences=1, no_repeat_ngram_size=2)
    response = tokenizer.decode(output[0], skip_special_tokens=True)
    
    return response

def rag_query(query):
    # İlgili logları getirme
    relevant_logs = retrieve_relevant_logs(query)
    
    # Yanıt oluşturma
    response = generate_response(query, relevant_logs)
    
    return response

# Test
test_query = "Which URLs were accessed the least?"
result = rag_query(test_query)
print(f"Soru: {test_query}")
print(f"Yanıt: {result}")






























"""
#Vektörize etme
from sklearn.feature_extraction.text import TfidfVectorizer

vectorizer_url = TfidfVectorizer()
vectorizer_method = TfidfVectorizer()

url_vectors = vectorizer_url.fit_transform(weblogs['URL']).toarray()
method_vectors = vectorizer_method.fit_transform(weblogs['RequestMethod']).toarray()

url_vector_df = pd.DataFrame(url_vectors, columns=[f"URL_{i}" for i in range(url_vectors.shape[1])])
method_vector_df = pd.DataFrame(method_vectors, columns=[f"RequestMethod_{i}" for i in range(method_vectors.shape[1])])

weblogs = pd.concat([weblogs, url_vector_df, method_vector_df], axis=1)

weblogs = weblogs.drop(columns=["URL", "RequestMethod"])


#Standartize 
from sklearn.preprocessing import StandardScaler
scaler = StandardScaler()
weblogs[['StatusCode', 'Size']] = scaler.fit_transform(weblogs[['StatusCode', 'Size']])"""












