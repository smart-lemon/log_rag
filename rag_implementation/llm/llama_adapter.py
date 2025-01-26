import os
import configparser
import json

config = configparser.ConfigParser()
config.read('config.ini')



# Note: Not tested. Langchains embedding can be also used
def embed_text_llama(texts) -> list[list[float]]:
    """Embeds texts using LLaMA's embedding model.

    Returns:
        A list of lists containing the embedding vectors for each input text.
    """
    from langchain_ollama import OllamaEmbeddings
    import ollama

    embeddings = OllamaEmbeddings(
        model="llama3",
    )
    # Load the pre-trained LLaMA model and tokenizer
    single_vector = embeddings.embed_query(texts)
    return single_vector

def query_llama_on_device(model_name, role, query):
    import ollama
    response = ollama.chat(
        model = model_name,
        messages=[ {
                "role": role,
                "content": query,
            },
        ],
    )
    print(response["message"]["content"])
    return response


LLAMA_MODEL_33_7B = "llama3.3-70b"

def query_llama_web_api(query, model_name = LLAMA_MODEL_33_7B, role = "user", max_tokens = 1000,  temperature = 0.7):
    llama_key = config.get('keys', 'llama', fallback=None)

    from llamaapi import LlamaAPI
    if not llama_key:
        raise ValueError("LLaMA API key not found in configuration.")
    llama = LlamaAPI(llama_key)

    # Build the API request
    api_request_json = {
        "model": model_name,
        "messages": [
            {"role": role, "content": query}
        ]
    }
    # Execute the Request
    response = llama.run(api_request_json)
    return json.dumps(response.json(), indent=2)

# For your testing needs
if __name__ == "__main__":
    # Local test
    # query_llama_on_device("llama3.3")

    try:
        ret = embed_text_llama("How much wood would a woodchuck chuck if a woodchuck could chuck wood")
        # query_llama_web_api(model_name = LLAMA_MODEL_33_7B, query = "How much wood would a woodchuck chuck if a woodchuck could chuck wood")
    except:
        print("Exception")