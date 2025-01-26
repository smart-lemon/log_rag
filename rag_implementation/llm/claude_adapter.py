import anthropic
import configparser

# Load API keys from configuration file
config = configparser.ConfigParser()
config.read('config.ini')

MODEL_NAME = "claude-3-5-sonnet-20241022"

# It needs to use the environment variable VOYAGE_API_KEY. https://docs.anthropic.com/en/docs/build-with-claude/embeddings
def embed_text_claude(texts):
    import voyageai
    vo = voyageai.Client()
    result = vo.embed(texts, model="voyage-3", input_type="document")
    return result.embeddings[:]

# API call to Claude LLM
def query_claude_web_api(query, model_name = MODEL_NAME, max_tokens = 1000, temperature = 0.7, role="user"):
    key = config.get('keys', 'claude')
    client = anthropic.Anthropic(
        api_key=key,
    )
    message = client.messages.create(
        model=model_name,
        max_tokens=max_tokens,
        messages=[
            {"role": role, "content": query}
        ]
    )
    return message.content

# For your testing needs
if __name__ == "__main__":
    query = "How much wood would a woodchuck chuck if a woodchuck could chuck wood"
    model_name = MODEL_NAME
    result = query_claude_web_api(query, model_name=model_name, max_tokens = 1000)
    print(result)