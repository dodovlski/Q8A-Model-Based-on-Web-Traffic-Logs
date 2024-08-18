from transformers import T5Tokenizer, T5ForConditionalGeneration

tokenizer = T5Tokenizer.from_pretrained('t5-base')
model = T5ForConditionalGeneration.from_pretrained('t5-base')

def generate_answer(query, context):
    
    input_text = f"question: {query} context: {context} </s>"
    input_ids = tokenizer.encode(input_text, return_tensors="pt")
    output = model.generate(input_ids)
    
    answer = tokenizer.decode(output[0], skip_special_tokens=True)
    
    return answer
