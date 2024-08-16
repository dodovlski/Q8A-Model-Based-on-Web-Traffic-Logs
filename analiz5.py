import pandas as pd

# CSV dosyasını oku ve DataFrame'e dönüştür
weblogs = pd.read_csv('logdata3.csv')

# "UserAgent" ve "RandomLogNumber" sütunlarını çıkar
weblogs = weblogs.drop(['UserAgent', 'RandomLogNumber'], axis=1)

# Date&Time sütununu belirtilen formata dönüştür
weblogs['Date&Time'] = pd.to_datetime(weblogs['Date&Time'], format='%d/%b/%Y:%H:%M:%S %z')

# Date&Time sütununu Date ve Time olarak ayır
weblogs['Date'] = weblogs['Date&Time'].dt.date
weblogs['Time'] = weblogs['Date&Time'].dt.time

# Date&Time sütununu kaldır
weblogs = weblogs.drop('Date&Time', axis=1)

# DataFrame'i göster
print(weblogs.head())

from sklearn.preprocessing import LabelEncoder
from sklearn.feature_extraction.text import TfidfVectorizer
import ipaddress
import numpy as np

# IP adreslerini sayısal temsillere dönüştür
def convert_ip_to_int(ip_str):
    return int(ipaddress.ip_address(ip_str))

weblogs['IP'] = weblogs['IP'].apply(convert_ip_to_int)

# RequestMethod sütununu LabelEncoder ile dönüştür
le = LabelEncoder()
weblogs['RequestMethod'] = le.fit_transform(weblogs['RequestMethod'])

# URL sütununu TF-IDF Vectorizer ile dönüştür
tfidf_vectorizer = TfidfVectorizer()
url_vectors = tfidf_vectorizer.fit_transform(weblogs['URL'])

# Date ve Time sütunlarını Unix zaman damgasına dönüştür
weblogs['DateTime'] = pd.to_datetime(weblogs['Date'].astype(str) + ' ' + weblogs['Time'].astype(str))
weblogs['UnixTimestamp'] = (weblogs['DateTime'].astype('int64') // 10**9).astype('int32') # Nanoseconds to seconds, then to int32

# Date, Time ve DateTime sütunlarını kaldır
weblogs = weblogs.drop(['Date', 'Time', 'DateTime'], axis=1)

# Sayısal sütunları seç
numeric_columns = ['IP', 'RequestMethod', 'StatusCode', 'Size', 'UnixTimestamp']
numeric_data = weblogs[numeric_columns].values

# URL vektörlerini numpy dizisine dönüştür
url_vectors = url_vectors.toarray()

# Tüm vektörleri birleştir
all_vectors = np.hstack((numeric_data, url_vectors))

# Sonuçları göster
print(all_vectors.shape)  # Vektörlerin boyutunu kontrol edin
print(all_vectors[:5])  # İlk birkaç vektörü göstererek doğrulama yapabilirsiniz

import faiss

# FAISS indeksini oluştur
dimension = all_vectors.shape[1]  # Vektörlerin boyutunu al
index = faiss.IndexFlatL2(dimension)  # L2 mesafesi kullanan düz indeks oluştur

# Verileri indeksle
index.add(all_vectors.astype('float32'))  # FAISS genellikle float32 veri tipiyle çalışır

# İndeksi kaydet (isteğe bağlı)
faiss.write_index(index, 'weblog_index.faiss')

from transformers import T5Tokenizer, T5ForConditionalGeneration

# T5 tokenizer ve modeli yükle
tokenizer = T5Tokenizer.from_pretrained("t5-small")
model = T5ForConditionalGeneration.from_pretrained("t5-small")

def retrieve_info(query):
    # Kullanıcı sorgusunu vektörleştir (URL sütunu için)
    query_vector = tfidf_vectorizer.transform([query]).toarray()

    # Diğer sayısal özellikler için vektörler ekle (örneğin, null veya ortalama değerler kullanılabilir)
    # Burada sadece URL vektörüne odaklandığımız için, diğer sayısal vektörlerin yerini 0 veya ortalama ile doldurabilirsiniz.
    numeric_part = np.zeros((1, len(numeric_columns)))  # Null values for the numeric part

    # URL vektörlerini ve sayısal verileri birleştir
    combined_query_vector = np.hstack((numeric_part, query_vector))

    # FAISS ile en yakın vektörleri bul
    k = 5  # En yakın 5 vektörü al
    distances, indices = index.search(combined_query_vector.astype('float32'), k)

    # En yakın vektörlere karşılık gelen log kayıtlarını al
    retrieved_logs = weblogs.iloc[indices[0]]

    # Log kayıtlarını metne dönüştür
    retrieved_text = retrieved_logs.to_string(index=False)
    # En yakın vektörlere karşılık gelen log kayıtlarını al
    retrieved_logs = weblogs.iloc[indices[0]]

    # Eğer sorgu sayısal bir cevap gerektiriyorsa, log verilerinden hesapla
    if "how many" in query.lower() and "404 errors" in query.lower():
        count = (retrieved_logs['StatusCode'] == 404).sum()
        retrieved_text = f"404 hatalarının sayısı: {count}"
    else:
        # Diğer sorular için log kayıtlarını metne dönüştür
        retrieved_text = retrieved_logs.to_string(index=False)

    return retrieved_text

    return retrieved_text


def generate_answer(query, retrieved_info):
    # T5 modeli için girdi metnini oluştur
    input_text = f"question: {query} context: {retrieved_info}"

    # Girdi metnini tokenize et
    input_ids = tokenizer.encode(input_text, return_tensors="pt", max_length=512, truncation=True)

    # T5 modeli ile yanıt üret
    outputs = model.generate(input_ids, max_length=150, num_beams=4, early_stopping=True)

    # Yanıtı decode et
    answer = tokenizer.decode(outputs[0], skip_special_tokens=True)

    return answer

# Örnek bir sorgu ile sistemi test et
query = "How many 404 errors occurred?"
retrieved_info = retrieve_info(query)
answer = generate_answer(query, retrieved_info)

print("Kullanıcı Sorusu:", query)
print("Alınan Log Kayıtları:\n", retrieved_info)
print("Oluşturulan Yanıt:", answer)

