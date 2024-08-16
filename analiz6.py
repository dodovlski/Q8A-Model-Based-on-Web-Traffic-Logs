import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import StandardScaler, LabelEncoder
from scipy.sparse import hstack
import faiss
import torch
from transformers import T5ForConditionalGeneration, T5Tokenizer
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.llms import HuggingFaceHub
from langchain.chains import RetrievalQA 


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
# LangChain ile FAISS vektör deposu oluşturma
embeddings = OpenAIEmbeddings()
vectorstore = FAISS.from_dataframe(weblogs, embedding=embeddings, index_name="weblogs_index")

# T5 modeli ve tokenizer'ı yükleme (HuggingFaceHub ile)
llm = HuggingFaceHub(repo_id="t5-small", model_kwargs={"temperature":0, "max_length":150})
tokenizer = T5Tokenizer.from_pretrained("t5-small")

# RetrievalQA zinciri oluşturma
qa_chain = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=vectorstore.as_retriever())

# Sorgu yapma
test_query = "Which URLs were accessed the least?"
result = qa_chain.run(test_query)
print(f"Soru: {test_query}")
print(f"Yanıt: {result}")