# 📄 Project Report

## 📝 Introduction

### 🎯 Project Purpose and Scope
The purpose of this project is to develop an AI-supported question-answer system based on Apache web traffic logs. The system analyzes data obtained from web logs and generates responses based on this data to provide the most appropriate answers to user queries.

### ❓ Problem Definition
In today's world, a large amount of web traffic data is generated, and analyzing this data is crucial for providing better services to users. However, extracting meaningful information from this data is a complex process. This project involves analyzing web traffic logs to develop a system that can respond to specific user queries.

### 💡 Importance and Potential Impact of the Project
This project provides significant advantages by converting large volumes of web traffic data into meaningful information, improving user experience, and automating data analysis processes. Additionally, the system can be integrated into and expanded for other data analytics projects.

## 📚 Literature Review

### 🕵️‍♂️ Web Log Analysis Methods
Web log analysis is a method for understanding user behavior, system performance, and security vulnerabilities through the examination of log files obtained from web servers. Various techniques and tools for such analyses have been developed in the literature.

### 🤖 AI-Supported Question-Answer Systems
AI-supported question-answer systems are systems that can generate meaningful and accurate answers to natural language queries from users. These systems typically use natural language processing (NLP) techniques and large language models.

### 🛠️ Similar Works and Existing Technologies
Similar projects have been examined, particularly those focused on log data analysis and question-answer systems. Existing technologies include tools and methods such as FAISS, T5 model, and TF-IDF.

## 🛠️ Methodology

### 📊 Data Collection and Preprocessing
The data collection process utilized Apache web logs, from which information such as IP address, date and time, request method, URL, status code, data size, and user agent was obtained. The data was processed using the Python programming language and converted into a suitable format for analysis.

### 🧠 AI Models and Algorithms Used
The project used TF-IDF vectorization and FAISS (Facebook AI Similarity Search) for data querying. The T5 model was employed for response generation.

### 🏗️ System Architecture and Components
The system consists of three main components: data processing, model training, and query answering. In the data processing phase, web logs were processed and cleaned. In the model training phase, data was vectorized using TF-IDF, and a search index was created using FAISS. In the query answering phase, the T5 model generated the most suitable responses to user queries.

### 🛠️ Development Process and Tools Used

The following libraries and tools were used in the development process:

- **Random:** Used for random number and data selection tasks. Played a key role in simulating log data by generating random data.
- **Time:** Used for time and date operations, specifically for creating and processing timestamps in log data.
- **Faker:** Used to generate realistic but fake data, including IP addresses, dates, and times for log data.
- **OS:** Used for performing operating system-related tasks, including setting file paths and managing file operations.
- **RE (Regular Expressions):** Used to process text data and extract necessary information from log lines. Employed to capture specific patterns in log files.
- **Pandas:** Used for data processing and analysis. Facilitated the organization, processing, and saving of log data in tabular format and CSV format.
- **Scikit-learn:** Used for machine learning algorithms and vectorization processes. Effectively utilized for TF-IDF vectorization and model training.
- **FAISS:** Used for fast similarity searches on high-dimensional data. Enabled rapid retrieval of the most relevant answers from log data.
- **TfidfVectorizer:** Used to convert text data into numerical vectors. Utilized for vectorizing log content and performing similarity-based searches.
- **Transformers:** Used for natural language processing (NLP) models. Employed to generate responses using the T5 model.

## 🚀 Application

### ⚙️ System Operation
The system is designed to provide the most appropriate response to user queries. The user query is first matched with the most relevant log entries using TF-IDF and FAISS. These data are then passed to the T5 model, which generates a response to the user's query.

### 🖥️ Interface Design
No user interface was designed for this project. The system operates via the command line, and results are displayed through this interface.

### 📋 Example Queries and System Responses
For example, when the query "When did the server give an error?" is posed, the system searches through the relevant log data and produces the most suitable response. For instance, it might generate a response like "The server gave an error with status code 500 on June 15, 2023."

![Example Query](images/orneksorgu.png)
![Example Query](images/orneksorgu2.png)

## 📊 Results and Evaluation

### 🏅 System Performance Metrics
The system was evaluated based on metrics such as accuracy and speed, demonstrating the ability to provide quick and accurate responses to user queries. However, it was found to be less effective in generating responses in natural language. The use of FAISS particularly supports fast searches in large datasets.

### ⏱️ Accuracy and Response Time Analysis
Tests revealed an accuracy rate of over 90% and an average response time of around 620 ms. These results indicate that the system operates efficiently and effectively.

![Example Query](images/elapsedTime.png)
![Example Query](images/elapsedTime2.png)

### 😊 User Experience Evaluation
The command-line-based nature of the project introduces some limitations in user experience. However, the system’s ability to provide quick and accurate responses positively impacts user experience. The system could be further developed with an interface to enhance user friendliness.

## 💬 Discussion

### 👍 Strengths and Limitations of the Project
The project's strengths include fast data processing, accurate response generation, and a scalable architecture. However, limitations include reliance solely on web log data and the absence of a user interface.

### 🚧 Challenges and Solutions

1. **Data Processing Challenges:**
   - Proper processing and formatting of data proved challenging.
   - **Solution:** Data cleaning techniques were used to correct missing and erroneous data and convert data into suitable formats.

2. **AI Model Training:**
   - Training the AI model correctly posed several challenges.
   - **Solution:** Model optimization methods were applied, hyperparameters were adjusted, and model performance was improved.

3. **FAISS Data Type Mismatch:**
   - FAISS typically works with `float32` data type, making it crucial for the `all_vectors` array to be of the correct data type.
   - **Solution:** The `all_vectors` array was converted to `float32` data type to ensure compatibility with FAISS.

4. **Datetime64[ns] to int32 Conversion Error:**
   - The error "TypeError: Converting from datetime64[ns] to int32 is not supported. Do obj.astype('int64').astype(dtype) instead" occurred during data cleaning.
   - **Solution:** The `datetime64[ns]` data type was first converted to `int64`, and then to the desired `int32` data type to resolve the issue.

### 🔮 Future Development Suggestions
Future enhancements could include integrating the system with broader data sources and developing a user interface. Additionally, the model could be further developed to handle more complex and detailed queries.

## 🏁 Conclusion

### 📈 Overall Project Evaluation
This project demonstrates that it is feasible to develop a question-answer system based on web log data. The system successfully operates with the capability to generate quick and accurate responses.

### 🧠 Personal Takeaways

- **Web Traffic Logs:** Learned what web traffic logs are and how they can be utilized for an AI-supported question-answer system.
- **Data Cleaning Methods:** Gained insights into methods for cleaning web log data and the suitability of different file formats.
- **Vectorization:** Understood the need for vectorizing words in question-answer systems.
- **Vector Database:** Learned about the necessity of storing vectors in a vector database for quick access.
- **RAG Model:** Discovered how to use the Retrieval-Augmented Generation (RAG) model to provide accurate and suitable answers.
- **Information Retrieval and Response Generation:** Acquired knowledge on how to retrieve information and generate responses using the RAG model.
- **Technology Usage:** Gained understanding of which technologies are best suited for specific tasks and situations.
