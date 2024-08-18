# 📄 Project Report

## 📑 Table of Contents

1. [📝 Introduction](#-introduction)
   - [🎯 Project Objectives and Scope](#-project-objectives-and-scope)
   - [❓ Problem Definition](#-problem-definition)
   - [💡 Project Importance and Potential Impact](#-project-importance-and-potential-impact)
2. [📚 Literature Review](#-literature-review)
   - [🕵️‍♂️ Web Log Analysis Methods](#-web-log-analysis-methods)
   - [🤖 AI-Powered Q&A Systems](#-ai-powered-qa-systems)
   - [🛠️ Similar Works and Existing Technologies](#-similar-works-and-existing-technologies)
3. [🛠️ Methodology](#-methodology)
   - [📊 Data Collection and Preprocessing](#-data-collection-and-preprocessing)
   - [🧠 AI Models and Algorithms Used](#-ai-models-and-algorithms-used)
   - [🏗️ System Architecture and Components](#-system-architecture-and-components)
   - [🛠️ Development Process and Tools Used](#-development-process-and-tools-used)
4. [🚀 Implementation](#-implementation)
   - [⚙️ System Operation](#-system-operation)
   - [🖥️ Interface Design](#-interface-design)
   - [📋 Example Queries and System Responses](#-example-queries-and-system-responses)
5. [📊 Results and Evaluation](#-results-and-evaluation)
   - [🏅 System Performance Metrics](#-system-performance-metrics)
   - [⏱️ Accuracy and Response Time Analyses](#-accuracy-and-response-time-analyses)
   - [😊 User Experience Evaluation](#-user-experience-evaluation)
6. [💬 Discussion](#-discussion)
   - [👍 Strengths and Limitations of the Project](#-strengths-and-limitations-of-the-project)
   - [🚧 Challenges and Solutions](#-challenges-and-solutions)
   - [🔮 Future Development Suggestions](#-future-development-suggestions)
7. [🏁 Conclusion](#-conclusion)
   - [📈 Overall Project Evaluation](#-overall-project-evaluation)
   - [🧠 Personal Learnings](#-personal-learnings)

## 📝 Introduction

### 🎯 Project Objectives and Scope
The aim of this project is to develop an AI-supported Q&A system based on Apache web traffic logs. The system analyzes data obtained from web logs to provide the most appropriate responses to user queries.

### ❓ Problem Definition
Today, large amounts of web traffic data are generated, and analyzing this data is crucial for providing better user service. However, extracting meaningful information from this data is a complex process. In this project, a system has been developed that analyzes web traffic logs to respond to specific user queries.

### 💡 Project Importance and Potential Impact
This project offers significant advantages by converting large volumes of web traffic data into meaningful information, thereby improving user experience and automating data analysis processes. Additionally, integration and expansion of this system with other data analytics projects are possible.

## 📚 Literature Review

### 🕵️‍♂️ Web Log Analysis Methods
Web log analysis is a method for understanding user behaviors, system performance, and security vulnerabilities by examining log files obtained from web servers. Various techniques and tools have been developed in the literature for such analyses.

### 🤖 AI-Powered Q&A Systems
AI-powered Q&A systems are designed to provide meaningful and accurate answers to user queries in natural language. These systems typically use natural language processing (NLP) techniques and large language models.

### 🛠️ Similar Works and Existing Technologies
Similar projects focusing on log data analysis and Q&A systems have been reviewed. Existing technologies include tools and methods such as FAISS, T5 model, and TF-IDF.

## 🛠️ Methodology

### 📊 Data Collection and Preprocessing
In the data collection process, Apache web logs were used to obtain IP address, date and time, request method, URL, status code, data size, and user agent information. The data was processed using the Python programming language and converted into a suitable format for analysis.

### 🧠 AI Models and Algorithms Used
The project used TF-IDF vectorization and FAISS (Facebook AI Similarity Search) for data querying. For response generation, the T5 model was employed.

### 🏗️ System Architecture and Components
The system consists of three main components: data processing, model training, and query answering. In the data processing stage, web logs were processed and cleaned. In the model training stage, data was vectorized using TF-IDF, and a search index was created using FAISS. In the query answering stage, the T5 model generated the most suitable responses to user queries.

### 🛠️ Development Process and Tools Used

The following libraries and tools were used during the development process:

- **Random:** Used for random number and data selection. Played a crucial role in generating random data for log simulation.
- **Time:** Used for time and date operations. Particularly useful for creating and processing timestamps in log data.
- **Faker:** Used for generating realistic but fake data. Enabled the creation of plausible IP addresses, dates, and times for log data.
- **OS:** Used for operating system-related tasks. Managed file paths and file operations.
- **RE (Regular Expressions):** Used for text data processing and extracting necessary information from log lines. Applied regular expressions to capture specific patterns in log files.
- **Pandas:** Used for data processing and analysis. Helped organize log data into tabular format, process it, and save it in CSV format.
- **Scikit-learn:** Used for machine learning algorithms and vectorization. Effectively used for TF-IDF vectorization and model training.
- **FAISS:** Used for fast similarity searches on high-dimensional data. Enabled quick retrieval of the most relevant responses from log data.
- **TfidfVectorizer:** Used for converting text data into numerical vectors. Facilitated vectorization of log content and similarity-based searches.
- **Transformers:** Used for NLP models. Utilized the T5 model to generate responses to questions.

## 🚀 Implementation

### ⚙️ System Operation
The system is designed to provide the most appropriate answer to a user's query. The user's query is first matched with the most relevant log entries using TF-IDF and FAISS. These data are then processed by the T5 model, which generates a response to the user's question.

### 🖥️ Interface Design
No user interface was designed for this project. The system operates via the command line, and results are displayed in this interface.

### 📋 Example Queries and System Responses
For an example query like "When did the server fail?", the system searches relevant log data and generates an appropriate response. For instance, "The server failed with a 500 error code on June 15, 2023" could be a possible response.

![Example Query](images/orneksorgu.png)
![Example Query](images/orneksorgu2.png)

## 📊 Results and Evaluation

### 🏅 System Performance Metrics
The system was evaluated based on accuracy and speed metrics, demonstrating the capacity to provide fast and accurate responses to user queries. However, it was noted to be inadequate in providing responses in natural language. The use of FAISS particularly facilitates quick searches in large datasets.

### ⏱️ Accuracy and Response Time Analyses
Tests showed that the system's accuracy rate is above 90%, with an average response time of around 620 ms. These results indicate that the system operates efficiently and effectively.

![Example Query](images/elapsedTime.png)
![Example Query](images/elapsedTime2.png)

### 😊 User Experience Evaluation
The command-line-based nature of the project imposes some limitations on user experience. However, the system's speed and accuracy positively affect user experience. Once the system is advanced further, developing a user-friendly interface would be beneficial.

## 💬 Discussion

### 👍 Strengths and Limitations of the Project
Strengths of the project include fast data processing, accurate response generation, and an expandable architecture. However, the system's reliance solely on web log data and lack of a user interface are among its limitations.

### 🚧 Challenges and Solutions

1. **Data Processing Challenges:**
   - Processing and formatting the data correctly was challenging.
   - **Solution:** Data cleaning techniques were applied to correct missing and erroneous data, and the data was transformed into suitable formats.

2. **AI Model Training:**
   - Training the AI model accurately posed some difficulties.
   - **Solution:** Model optimization techniques were applied, hyperparameters were adjusted, and the model's performance was enhanced.

3. **FAISS Data Type Compatibility:**
   - FAISS typically works with float32 data type, so ensuring the correct data type for the all_vectors array was crucial.
   - **Solution:** The all_vectors array was converted to float32 data type to be compatible with FAISS.

4. **Datetime64[ns] to int32 Conversion Error:**
   - The "TypeError: Converting from datetime64[ns] to int32 is not supported. Do obj.astype('int64').astype(dtype) instead" error occurred during data cleaning.
   - **Solution:** The datetime64[ns] data type was first converted to int64, and then to the desired int32 data type to resolve the issue.

### 🔮 Future Development Suggestions
Future development could include integrating the system with broader data sources and developing a user interface. Additionally, enhancing the model to handle more complex and detailed queries is feasible.

## 🏁 Conclusion

### 📈 Overall Project Evaluation
This project demonstrated the feasibility of developing a Q&A system based on web log data. The system operates successfully with the ability to provide fast and accurate responses.

### 🧠 Personal Learnings
- **Web Traffic Logs:** Learned about web traffic logs and how they can be used for AI-supported Q&A systems.
- **Data Cleaning Methods:** Gained knowledge on methods for cleaning web log data and which file formats are more suitable.
- **Vectorization:** Understood the need for vectorizing words in Q&A systems.
- **Vector Database:** Learned the importance of storing vectors in a database for quick use.
- **RAG Model:** Learned how to use the Retrieval-Augmented Generation (RAG) model to provide accurate and relevant responses.
- **Information Retrieval and Response Generation:** Gained insight into the processes of information retrieval and response generation using the RAG model.
- **Technology Usage:** Developed an understanding of which technologies to use in specific situations.
