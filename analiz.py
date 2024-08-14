import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import OneHotEncoder

# Verileri DataFrame haline getirmek
veriler = pd.read_csv('logdata3.csv')

# İlk dört sütunu almak
ilk_dort_sutun = veriler.iloc[:, :4]

# Sonucu görmek için
print(ilk_dort_sutun)


df = pd.DataFrame(veriler)

# Request Sütunu TF-IDF ile Vektörize Ediliyor
vectorizer = TfidfVectorizer()
request_vectors = vectorizer.fit_transform(df['Request'])

# StatusCode Sütunu için One-Hot Encoding
encoder = OneHotEncoder()
status_code_vectors = encoder.fit_transform(df[['StatusCode']])

# Date&Time Sütununu Ayırarak Sayısal Değerlere Dönüştürme
df['Date&Time'] = pd.to_datetime(df['Date&Time'], format='%d/%b/%Y:%H:%M:%S %z')
df['Hour'] = df['Date&Time'].dt.hour
df['DayOfWeek'] = df['Date&Time'].dt.dayofweek
df['Month'] = df['Date&Time'].dt.month

time_features = df[['Hour', 'DayOfWeek', 'Month']].values

# IP Adresini Sayısal Bir Değere Dönüştürme
df['IP_Numeric'] = df['IP'].apply(lambda x: int(''.join(x.split('.'))))

ip_features = df[['IP_Numeric']].values

# Tüm Vektörleri Birleştirme
final_vectors = np.hstack([ip_features, time_features, request_vectors.toarray(), status_code_vectors.toarray()])

import faiss


# Vektörlerin boyutunu belirleme
vektor_boyutu = final_vectors.shape[1]

# FAISS index oluşturma (L2 norm ile düz bir index)
index = faiss.IndexFlatL2(vektor_boyutu)

# Vektörleri indexe ekleme
index.add(final_vectors)

# Indexe eklenen vektörlerin sayısını kontrol etme
print(f"Indexteki toplam vektör sayısı: {index.ntotal}")

# FAISS indexi dosyaya kaydetme
faiss.write_index(index, "vektor_index.faiss")

# Index dosyasının kaydedildiğini doğrulama
print("FAISS index dosyaya kaydedildi.")


# FAISS index dosyasını yükleme
loaded_index = faiss.read_index("vektor_index.faiss")

# Bir vektör sorgulama (örneğin, ilk vektör)
query_vector = final_vectors[0].reshape(1, -1)

# En yakın 5 vektörü bulma
D, I = loaded_index.search(query_vector, k=5)

print(f"En yakın vektörlerin uzaklıkları: {D}")
print(f"En yakın vektörlerin indexleri: {I}")


# Kullanıcıdan gelen soru (örnek olarak sadece request kısmını alıyoruz)
query = "GET /usr/admin/developer"

# Soruyu vektörize etme (Daha önce kullanılan TF-IDF vektörizer)
query_vector = vectorizer.transform([query]).toarray()

# Sorgu için varsayılan (örnek) IP, tarih/zaman, ve status code bilgilerini ekleme
# Burada sorgu vektörünün boyutunu tamamlamak için örnek veriler kullanıyoruz
# Gerçek kullanımda bu bilgileri kullanıcıdan almanız gerekebilir

# IP (örnek olarak 0.0.0.0 kullanıyoruz, gerçekte bu kısım kullanıcıdan gelmeli)
default_ip_numeric = np.array([[0]])

# Tarih/zaman (örnek olarak saat, gün ve ay bilgileri)
default_time_features = np.array([[0, 0, 0]])

# Status code (örnek olarak 200, yani başarılı bir istek durumu)
default_status_code_vector = encoder.transform([[200]]).toarray()

# Tüm vektörleri birleştirme
full_query_vector = np.hstack([default_ip_numeric, default_time_features, query_vector, default_status_code_vector])

# FAISS indexine göre en yakın log kayıtlarını bulma
D, I = loaded_index.search(full_query_vector, k=5)

# Bulunan kayıtları DataFrame'den çekme
found_records = df.iloc[I[0]]

print(found_records)

from transformers import GPT2LMHeadModel, GPT2Tokenizer

# GPT2 modelini ve tokenizer'ı yükleme
model = GPT2LMHeadModel.from_pretrained("gpt2")
tokenizer = GPT2Tokenizer.from_pretrained("gpt2")

# Bulduğunuz log kayıtlarını birleştirerek modelin anlayabileceği bir metin oluşturma
input_text = " ".join(found_records['Request'].tolist())

# Model için girdi verilerini hazırlama
inputs = tokenizer.encode(input_text, return_tensors="pt", max_length=512, truncation=True)

# GPT modelinden bir cevap üretme
outputs = model.generate(inputs, max_length=150, num_beams=5, early_stopping=True)
answer = tokenizer.decode(outputs[0], skip_special_tokens=True)

print("GPT'den gelen cevap:", answer)

def cevap_olustur(query):
    # Soruyu vektörize et
    query_vector = vectorizer.transform([query]).toarray()
    
    # FAISS ile en yakın log kayıtlarını bul
    D, I = loaded_index.search(query_vector, k=5)
    found_records = df.iloc[I[0]]
    
    # Bulunan kayıtları kullanarak bir input metni oluştur
    input_text = " ".join(found_records['Request'].tolist())
    
    # GPT'den cevap üretme
    inputs = tokenizer.encode(input_text, return_tensors="pt", max_length=512, truncation=True)
    outputs = model.generate(inputs, max_length=150, num_beams=5, early_stopping=True)
    answer = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    return answer

# Kullanıcı sorusu örneği
soru = "Kullanıcı admin paneline nasıl erişmeye çalışıyor?"
cevap = cevap_olustur(soru)
print("Sistem yanıtı:", cevap)



