import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import StandardScaler, LabelEncoder
from scipy.sparse import hstack
import faiss
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

# Check if 'IP' column exists
if 'IP' not in weblogs.columns:
    raise KeyError("'IP' column is missing from the DataFrame. Please check the input data.")

# Kategorik verileri sayısallaştırma
le_ip = LabelEncoder()
weblogs['IP_encoded'] = le_ip.fit_transform(weblogs['IP'])
le_method = LabelEncoder()
weblogs['RequestMethod_encoded'] = le_method.fit_transform(weblogs['RequestMethod'])

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

# FAISS indeksini yükleme
index = faiss.read_index("weblogs_index.faiss")

# T5 modelini ve tokenizer'ı yükleme
model_name = "t5-small"
tokenizer = T5Tokenizer.from_pretrained(model_name)
model = T5ForConditionalGeneration.from_pretrained(model_name)

# TF-IDF vektörizeri yeniden oluşturma
tfidf = TfidfVectorizer(max_features=100)
tfidf.fit(weblogs['URL'])

def parse_query(query):
    # Basit bir sorgu ayrıştırıcı (daha gelişmiş bir NLP modeli ile değiştirilebilir)
    query_lower = query.lower()
    
    if 'most recent' in query_lower and 'status code' in query_lower:
        try:
            # Extract the status code safely
            status_code_str = query_lower.split('status code')[-1].strip()
            status_code = int(status_code_str)
            return {
                'type': 'recent_status',
                'status_code': status_code
            }
        except ValueError:
            # Handle the case where the status code is not a valid integer
            print(f"Geçersiz durum kodu: {status_code_str}")
            return None
    
    elif 'count' in query_lower:
        if 'ip' in query_lower:
            return {'type': 'count', 'field': 'IP'}
        elif 'method' in query_lower:
            return {'type': 'count', 'field': 'RequestMethod'}
    
    # Daha fazla sorgu türü ekleyin
    return None

def retrieve_relevant_logs(query, k=5):
    query_info = parse_query(query)
    
    if query_info is None:
        return [{"Error": "Query could not be parsed or contained invalid data."}]
    
    if query_info['type'] == 'recent_status':
        relevant_logs = weblogs[weblogs['StatusCode'] == query_info['status_code']].sort_values(by='Date_numeric', ascending=False).head(k)
        return relevant_logs.to_dict('records')
    
    # Default to FAISS search for other types of queries
    query_tfidf = tfidf.transform([query]).toarray().astype('float32')
    query_vector = np.zeros((1, index.d), dtype='float32')
    query_vector[:, :query_tfidf.shape[1]] = query_tfidf
    distances, indices = index.search(query_vector, k)
    relevant_logs = weblogs.iloc[indices[0]].to_dict('records')
    return relevant_logs

def generate_response(query, relevant_logs):
    # Sorgu ve ilgili logları birleştirme
    context = "Query: " + query + "\nRelevant logs:\n"
    for log in relevant_logs:
        ip = log.get('IP', 'N/A')  # Use 'N/A' if 'IP' is missing
        method = log.get('RequestMethod', 'N/A')
        url = log.get('URL', 'N/A')
        status = log.get('StatusCode', 'N/A')
        size = log.get('Size', 'N/A')
        date = log.get('Date', 'N/A')
        time = log.get('Time', 'N/A')
        
        context += f"IP: {ip}, Method: {method}, URL: {url}, Status: {status}, Size: {size}, Date: {date}, Time: {time}\n"
    
    # T5 modelini kullanarak yanıt oluşturma
    input_ids = tokenizer.encode("summarize: " + context, return_tensors="pt", max_length=512, truncation=True)
    output = model.generate(input_ids, max_length=150, num_return_sequences=1, no_repeat_ngram_size=2)
    response = tokenizer.decode(output[0], skip_special_tokens=True)
    
    return response


def rag_query(query):
    relevant_logs = retrieve_relevant_logs(query)
    response = generate_response(query, relevant_logs)
    return response

# Test
test_query = "What is the most recent request with a 500 status code?"
result = rag_query(test_query)
print(f"\nSoru: {test_query}")
print(f"\nYanıt: {result}")

# Daha fazla test
test_query_2 = "How many requests were made from each IP?"
result_2 = rag_query(test_query_2)
print(f"\nSoru: {test_query_2}")
print(f"\nYanıt: {result_2}")
