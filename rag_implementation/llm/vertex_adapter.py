import vertexai
import configparser
config = configparser.ConfigParser()
config.read('config.ini')

EMBEDDING_MODEL_NAME = "text-embedding-005"
DIMENSIONALITY = 256
VERTEX_MODEL = 'gemini-pro'


def embed_text_vertex(texts) -> list[list[float]]:
    from vertexai.language_models import TextEmbeddingInput, TextEmbeddingModel

    """Embeds texts with a pre-trained, foundational model.

    Returns:
        A list of lists containing the embedding vectors for each input text
    """

    # A list of texts to be embedded.
    # The dimensionality of the output embeddings.
    dimensionality = 384
    # The task type for embedding. Check the available tasks in the model's documentation.
    task = "RETRIEVAL_DOCUMENT"
    embedding_name = config.get('llm_in_use', 'embedding')
    model = TextEmbeddingModel.from_pretrained(embedding_name)
    inputs = [TextEmbeddingInput(text, task) for text in texts]
    kwargs = dict(output_dimensionality=dimensionality) if dimensionality else {}
    embeddings = model.get_embeddings(inputs, **kwargs)

    # print(embeddings)
    return [embedding.values for embedding in embeddings]

def query_vertex_web_api(query, model_name = VERTEX_MODEL, max_length = 1000, temperature = 0.2, role=None):
    from vertexai.preview.generative_models import GenerativeModel
    location = 'us-central1'
    project_id = config.get('keys', 'vertex_project_id')

    vertexai.init(project=project_id, location=location)

    model = GenerativeModel(model_name)
    response = model.generate_content(query)
    return response.text

def langchain_vertex_get_model():
    from langchain_google_vertexai import VertexAI

    # To use model
    model = VertexAI(model_name="gemini-pro")
    return model

def lanchain_vertex_embedding():

    from langchain_google_vertexai import VertexAIEmbeddings
    embedding_name = config.get('llm_in_use', 'embedding')
    embeddings = VertexAIEmbeddings(model= embedding_name) # "text-embedding-004")
    return embeddings

if __name__ == "__main__":
    query = "How much wood would a woodchuck chuck if a woodchuck could chuck wood"
    model_name = VERTEX_MODEL
    result = query_vertex_web_api(query, model_name=model_name, max_length = 600)
    print(result)