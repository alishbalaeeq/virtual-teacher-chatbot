from ctransformers import AutoModelForCausalLM

# Set gpu_layers to the number of layers to offload to GPU. Set to 0 if no GPU acceleration is available on your system.
llm = AutoModelForCausalLM.from_pretrained("TheBloke/Mistral-7B-Instruct-v0.1-GGUF", model_file="mistral-7b-instruct-v0.1.Q4_K_M.gguf", model_type="mistral",gpu_layers=50)

def generation_model(question):
    prompt = f"""
        <s>[INST] You are a helpful, authoritative and strict teacher.Answer in few words without any non verbal ques.
        Answer the question below from context below :
        Topic is about Climate change.
        Do not answer the question if it is not relevant to the topic.
        Answer the Question: {question} if it is relevant to the topic: Climate change or related to climate.
        or else say 'Question not relevant, we will study this later on.'
        [/INST] </s>"""
    
    output=''
    for word in llm(prompt):
        print(word,end='')
        output += word

    return output