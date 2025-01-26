import pprint
import configparser
import requests

# Load API keys from configuration file
config = configparser.ConfigParser()
config.read('config.ini')

# local
MISTRAL_7B = "mistralai/Mistral-7B-v0.3"
MISTRAL_NEMO = "mistralai/Mistral-Nemo-Base-2407"
MISTRAL_LARGE = "mistral-large-latest"

def embed_text_mistral(texts):
    from langchain_mistralai import MistralAIEmbeddings

    embeddings = MistralAIEmbeddings(model="mistral-embed")
    result = embeddings.embed_query(texts)
    return result


def query_mistral_on_device(query, model_name, max_length = 1000, temperature = 0.7, role=None, max_tokens = 1000):
    from transformers import AutoModelForCausalLM, AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name)

    # Tokenize the input
    inputs = tokenizer(query, return_tensors="pt")

    # Generate response
    outputs = model.generate(inputs["input_ids"], max_length=max_length, num_return_sequences=1)

    # Decode and print the result
    generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)

    return generated_text

def query_mistral_web_api(query, role = "user", model_name = "mistral-large-latest", max_tokens = 1000, temperature = 0.2):
    """
    Calls the Mistral API with a given prompt.
    """
    mistral_key = config.get('keys', 'mistral')
    from mistralai import Mistral

    client = Mistral(api_key=mistral_key)

    chat_response = client.chat.complete(
        model=model_name,
        messages=[
            {
                "role": role,
                "content": query,
            },
        ]
    )
    return chat_response.choices[0].message.content

# For your testing needs
if __name__ == "__main__":
    query = "How much wood would a woodchuck chuck if a woodchuck could chuck wood"
    model_name = MISTRAL_LARGE

    # Local test
    # result = query_mistral_on_device(query, model_name=model_name, max_length = 600)

    # Web API test
    result = query_mistral_web_api(query, model_name=model_name, max_tokens=600)
    print(result)