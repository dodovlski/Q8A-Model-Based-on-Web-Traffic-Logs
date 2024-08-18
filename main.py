from 4_qa_system import answer_question

if __name__ == "__main__":
    user_query = input("Enter Question: ")
    answer = answer_question(user_query)
    print(f"Question: {user_query}")
    print(f"Answer: {answer}")

