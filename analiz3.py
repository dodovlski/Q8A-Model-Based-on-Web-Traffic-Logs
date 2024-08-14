import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import StandardScaler

# CSV dosyasını okuma
weblogs = pd.read_csv("logdata3.csv")

new_weblogs = weblogs.iloc[:,:6]

# Tarih ve zaman damgalarını uygun bir formata dönüştürün
new_weblogs['Date&Time'] = pd.to_datetime(new_weblogs['Date&Time'], format='%d/%b/%Y:%H:%M:%S %z')


# Vektör haline getirmek
from sklearn.feature_extraction.text import TfidfVectorizer

vectorizer = TfidfVectorizer()
req_vectors = vectorizer.fit_transform(new_weblogs['RequestMethod'])
url_vectors = vectorizer.fit_transform(new_weblogs['URL'])


# Sayısal sütunları alıp numpy array'e çevirin
ip_vectors = new_weblogs['IP'].apply(lambda x: hash(x) % 10**8).values.reshape(-1, 1)
datetime_vectors = np.array([new_weblogs['Date&Time'].dt.year, new_weblogs['Date&Time'].dt.month, 
                             new_weblogs['Date&Time'].dt.day, new_weblogs['Date&Time'].dt.hour]).T
status_code_vectors = new_weblogs['StatusCode'].values.reshape(-1, 1)
size_vectors = new_weblogs['Size'].values.reshape(-1, 1)

# Tüm vektörleri birleştirin
combined_vectors = np.hstack([ip_vectors, datetime_vectors, status_code_vectors, size_vectors, 
                             url_vectors.toarray()])

import faiss
