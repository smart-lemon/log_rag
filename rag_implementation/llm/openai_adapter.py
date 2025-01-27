OPEN_AI_MODEL = 'gpt-4o'

import configparser
import openai
config = configparser.ConfigParser()
config.read('config.ini')

from openai import OpenAI
import openai

config = configparser.ConfigParser()
config.read('config.ini')
llm_config = config.get('llm_in_use', 'llm')

# Set the embedding in config.ini e.g - "text-embedding-ada-002"
embedding_name = config.get('llm_in_use', 'embedding')


def embed_text_openai(texts) -> list[list[float]]:
    """Embeds texts using OpenAI's embedding model.

    Returns:
        A list of lists containing the embedding vectors for each input text.
    """

    # Define the OpenAI embedding model (e.g., text-embedding-ada-002)
    embedding_model = embedding_name

    # Call the OpenAI API to generate embeddings
    response = openai.Embedding.create(input=texts, model=embedding_model)

    # Extract and return the embeddings
    return [data["embedding"] for data in response["data"]]


def query_openai_web_api(query, model_name = OPEN_AI_MODEL, max_tokens = 1000, temperature = 0.7,
                         role="user", llm_self_description = "You are a helpful assistant."):

    client = OpenAI()

    completion = client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "system", "content": llm_self_description},
            {
                "role": role,
                "content": query
            }
        ] )

    return completion.choices[0].text.strip()


# For your testing needs
if __name__ == "__main__":
    query = "How much wood would a woodchuck chuck if a woodchuck could chuck wood"
    model_name = OPEN_AI_MODEL
    result = query_openai_web_api(query, model_name=model_name, max_tokens = 600)
    print(result)