import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import StandardScaler

# CSV dosyasını okuma
df = pd.read_csv("logdata3.csv")

# İlk dört sütunu seçme
df_selected = df.loc[:, ['IP', 'Date&Time', 'Request', 'StatusCode']]

# IP adresini sayısal değerlere çevirme
df_selected.loc[:, 'IP'] = df_selected['IP'].apply(lambda x: [int(i) for i in x.split('.')])

# Tarih ve zaman damgasını Unix zamanına dönüştürme
df_selected.loc[:, 'Date&Time'] = pd.to_datetime(df_selected['Date&Time'], format='%d/%b/%Y:%H:%M:%S %z')

# Unix zamanına dönüştürme
df_selected.loc[:, 'Date&Time'] = df_selected['Date&Time'].apply(lambda x: int(x.timestamp()))

# TF-IDF vektörleştirme
tfidf_vectorizer = TfidfVectorizer()
request_vectors = tfidf_vectorizer.fit_transform(df_selected['Request'])

# Durum kodunu normalleştirme
scaler = StandardScaler()
status_code_scaled = scaler.fit_transform(df_selected[['StatusCode']])

# IP vektörleri
ip_vectors = np.array(df_selected['IP'].to_list())

# Tarih ve Zaman damgası vektörleri
datetime_vectors = df_selected[['Date&Time']].values

# Tüm vektörleri birleştirme
final_vectors = np.hstack((ip_vectors, datetime_vectors, request_vectors.toarray(), status_code_scaled))

# final_vectors değişkeni şimdi her satır için bir vektördür.

import faiss

# Vektör boyutunu alalım
d = final_vectors.shape[1]

# FAISS dizini oluşturma
index = faiss.IndexFlatL2(d)

# Vektörleri FAISS dizinine ekleme
index.add(final_vectors)

# Kullanıcı sorusuna en yakın k vektörü bulmak için sorgu yapma (örneğin, en yakın 5 vektör)
def retrieve_similar_logs(query_vector, k=5):
    D, I = index.search(query_vector, k)  # D: Mesafeler, I: İndisler
    return D, I

from transformers import T5ForConditionalGeneration, T5Tokenizer

# T5 modelini ve tokenizer'ı yükleyelim
model_name = "t5-small"  # Daha büyük bir model isterseniz "t5-base" veya "t5-large" kullanabilirsiniz
tokenizer = T5Tokenizer.from_pretrained(model_name)
model = T5ForConditionalGeneration.from_pretrained(model_name)

# Bulduğumuz en iyi log kayıtlarını metin haline getirme
def generate_response(retrieved_logs):
    input_text = " ".join(retrieved_logs)
    input_ids = tokenizer.encode("generate question: " + input_text, return_tensors="pt", max_length=512, truncation=True)
    
    outputs = model.generate(input_ids, max_length=150, num_beams=5, early_stopping=True)
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    return response


def answer_question(query):
    # Sorguyu vektörleştirme
    query_vector = tfidf_vectorizer.transform([query]).toarray()
    
    # En benzer log kayıtlarını bulma
    _, indices = retrieve_similar_logs(query_vector)
    
    # Logları metin haline getirme
    retrieved_logs = df_selected.iloc[indices[0]]['Request'].values
    
    # Jeneratif modeli kullanarak yanıt oluşturma
    answer = generate_response(retrieved_logs)
    
    return answer

