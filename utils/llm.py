from ctransformers import AutoModelForCausalLM

# Set gpu_layers to the number of layers to offload to GPU. Set to 0 if no GPU acceleration is available on your system.
llm = AutoModelForCausalLM.from_pretrained("TheBloke/Mistral-7B-Instruct-v0.1-GGUF", model_file="mistral-7b-instruct-v0.1.Q4_K_M.gguf", model_type="mistral",gpu_layers=50)

def generate_lecture(topic):
    prompt = f"""
        <s>[INST] You are a helpful, authoritative and knowledgable teacher. Your name is Miss Emily. You must generate a small lecture on topic: {topic}. Generate a lecture of maximum 500 characters.[/INST] </s>"""
    
    output=''
    for word in llm(prompt):
        output += word

    return output


def generation_model(question, topic):
    prompt = f"""
        <s>[INST] You are a helpful, authoritative and strict teacher. Answer in few words without any non verbal ques.
        Answer the question below from topic: {topic}
        Do not answer the question if it is not relevant to the topic. Say something a teacher would say.
        Answer the Question: {question} 
        [/INST] </s>"""
    
    output=''
    for word in llm(prompt):
        print(word,end='')
        output += word

    return output