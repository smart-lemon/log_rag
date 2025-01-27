import configparser
# from llm.mistral_adapter import *
from llm.openai_adapter import *
from llm.claude_adapter import *
from llm.vertex_adapter import *
from llm.llama_adapter import *
from llm.mistral_adapter import *
from colorama import Fore, Style

config = configparser.ConfigParser()
config.read('config.ini')
llm_config = config.get('llm_in_use', 'llm')


def eval_llm_token_count(prompt):
    import tiktoken
    for encoding_name in ["cl100k_base"]:
        encoding = tiktoken.get_encoding(encoding_name)
        token_integers = encoding.encode(prompt)
        num_tokens = len(token_integers)
        print(Fore.CYAN + Style.DIM +  "Approximate number of tokens used are " + str(num_tokens) + Style.RESET_ALL)

def embed_text(txt):
    results = None
    if llm_config == 'vertex':
        results = embed_text_vertex(txt)
    elif llm_config == 'openai':
        results = embed_text_openai(txt)
    elif llm_config == 'mistral':
        results = embed_text_mistral(txt)
    elif llm_config == 'llama':
       results = embed_text_llama(txt)
    elif llm_config == 'claude':
       results = embed_text_claude(txt)
    else: # Corner case only - no response
        results = []
    return results

def query_llm(txt):
    print("Querying LLM " + llm_config)
    response = ""
    if llm_config == 'vertex':
        response = query_vertex_web_api(txt)
    elif llm_config == 'openai':
        response = query_openai_web_api(txt)
    elif llm_config == 'llama':
        response = query_llama_web_api(txt)
    elif llm_config == 'mistral':
        response = query_mistral_web_api(txt)
    elif llm_config == 'claude':
        response = query_claude_web_api(txt)
    else: # Corner case only - no response
        response = "No response - please check LLM configuration"
    return response


if __name__ == "__main__":
    eval_llm_token_count("Hello world")