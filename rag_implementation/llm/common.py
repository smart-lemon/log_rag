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
llm = config.get('llm_in_use', 'llm')

def embed_text(txt):
    results = None
    if llm == 'vertex':
        results = embed_text_vertex(txt)
    elif llm == 'openai':
        results = embed_text_openai(txt)
    elif llm == 'mistral':
        results = embed_text_mistral(txt)
    elif llm == 'llama':
       results = embed_text_llama(txt)
    elif llm == 'claude':
       results = embed_text_claude(txt)
    else: # Corner case only - no response
        results = []
    return results

def query_llm(txt):
    response = ""
    if llm == 'vertex':
        response = query_vertex_web_api(txt)
    elif llm == 'openai':
        response = query_openai_web_api(txt)
    elif llm == 'llama':
        response = query_llama_web_api(txt)
    elif llm == 'mistral':
        response = query_mistral_web_api(txt)
    elif llm == 'claude':
        response = query_claude_web_api(txt)
    else: # Corner case only - no response
        response = "No response - please check LLM configuration"
    return response

def count_tokens(prompt):
    import tiktoken
    for encoding_name in ["cl100k_base"]:
        encoding = tiktoken.get_encoding(encoding_name)
        token_integers = encoding.encode(final_prompt)
        num_tokens = len(token_integers)
        print(Fore.CYAN + Style.DIM "Approximate number of tokens used are " + str(num_tokens) + Style.RESET_ALL)

