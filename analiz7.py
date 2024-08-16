import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import StandardScaler, LabelEncoder
from scipy.sparse import hstack, save_npz, load_npz
import faiss
from transformers import T5ForConditionalGeneration, T5Tokenizer
import joblib
import torch

# CSV dosyasını okuma
weblogs = pd.read_csv("logdata3.csv")
weblogs = weblogs.drop(columns=["UserAgent", "RandomLogNumber"])

# Tarih ve zaman damgalarını uygun bir formata dönüştürme
weblogs['Date&Time'] = pd.to_datetime(weblogs['Date&Time'], format='%d/%b/%Y:%H:%M:%S %z')
weblogs['Date'] = weblogs['Date&Time'].dt.date
weblogs['Time'] = weblogs['Date&Time'].dt.time
weblogs = weblogs.drop(columns=["Date&Time"])

# Kategorik verileri sayısallaştırma
le = LabelEncoder()
weblogs['IP_encoded'] = le.fit_transform(weblogs['IP'])
weblogs['RequestMethod_encoded'] = le.fit_transform(weblogs['RequestMethod'])

# URL'leri TF-IDF vektörlerine dönüştürme
tfidf = TfidfVectorizer(max_features=100)
url_vectors = tfidf.fit_transform(weblogs['URL'])

# Sayısal verileri ölçeklendirme
scaler = StandardScaler()
numeric_features = ['StatusCode', 'Size']
numeric_vectors = scaler.fit_transform(weblogs[numeric_features])

# Tarih ve zaman verilerini sayısallaştırma
weblogs['Date_numeric'] = pd.to_datetime(weblogs['Date']).astype('int64') // 10**9
weblogs['Time_numeric'] = weblogs['Time'].apply(lambda x: x.hour * 3600 + x.minute * 60 + x.second)

# Tüm vektörleri birleştirme
encoded_features = ['IP_encoded', 'RequestMethod_encoded', 'Date_numeric', 'Time_numeric']
all_features = hstack([
    weblogs[encoded_features].values,
    url_vectors,
    numeric_vectors
]).tocsr()

# Vektörleri numpy array'ine dönüştürme
vectors = all_features.toarray().astype('float32')

# FAISS indeksi oluşturma ve vektörleri ekleme
dimension = vectors.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(vectors)

# İndeksi dosyaya kaydetme
faiss.write_index(index, "weblogs_index.faiss")

# Diğer modelleri kaydetme
joblib.dump(le, 'label_encoder.joblib')
joblib.dump(scaler, 'scaler.joblib')
joblib.dump(tfidf, 'tfidf_vectorizer.joblib')
save_npz('all_features.npz', all_features)

# T5 modelini ve tokenizer'ı yükleme
model_name = "t5-base"  # Daha büyük bir model kullanıyoruz
tokenizer = T5Tokenizer.from_pretrained(model_name)
model = T5ForConditionalGeneration.from_pretrained(model_name)

# GPU kullanımı için
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

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
    context = "Query: " + query + "\nRelevant logs:\n"
    for log in relevant_logs:
        context += f"IP: {log['IP']}, Method: {log['RequestMethod']}, URL: {log['URL']}, Status: {log['StatusCode']}, Size: {log['Size']}, Date: {log['Date']}, Time: {log['Time']}\n"
    
    input_ids = tokenizer.encode("summarize: " + context, return_tensors="pt", max_length=512, truncation=True).to(device)
    
    # Beam search ve daha uzun çıktı için ayarlar
    output = model.generate(
        input_ids,
        max_length=200,
        num_beams=5,
        no_repeat_ngram_size=2,
        num_return_sequences=1,
        early_stopping=True
    )
    
    response = tokenizer.decode(output[0], skip_special_tokens=True)
    return response

def rag_query(query):
    relevant_logs = retrieve_relevant_logs(query)
    response = generate_response(query, relevant_logs)
    return response

# Test
test_queries = [
    "What is the most common HTTP status code?",
    "Are there any suspicious activities in the logs?",
]

for query in test_queries:
    result = rag_query(query)
    print(f"Soru: {query}")
    print(f"Yanıt: {result}\n")