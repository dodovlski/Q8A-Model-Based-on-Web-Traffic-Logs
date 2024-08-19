import time
from ivvv_qa_system import answer_question

if __name__ == "__main__":
    
    while(True):
    
        user_query = input("Enter Question: ")
        
        start_time = time.time()
        answer = answer_question(user_query)
        end_time = time.time()
        
        elapsed_time = end_time - start_time
        
        print(f"Question: {user_query}")
        print(f"Answer: {answer}")
        print(f"Elapsed Time: {elapsed_time:.4f} seconds")
    