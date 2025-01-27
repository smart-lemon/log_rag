import os

from pre_processor.repo_chunker import *
from raptor_retriever import *
from graph_retriever import *
from longcontext_retriever import *
from colorama import Fore, Style

# ====================== Set before the test ========================

config = configparser.ConfigParser()
config.read('config.ini')
llm = config.get('llm_in_use', 'llm')
embedding_name = config.get('llm_in_use', 'embedding')


# ==================== # ==================== # ====================
from enum import Enum

class Method(Enum):
    LONG_CONTEXT, RAPTOR, GRAPH_RAG = 1, 2, 3

def execute(method, project, project_path, project_name, project_description):
    if method == Method.GRAPH_RAG:
        print(Fore.YELLOW + Style.BRIGHT + "Executing project: " + project + " - " + project_description
              + Fore.YELLOW + "Using Graph RAG" + Style.RESET_ALL)
        execute_project_feed_logs_to_graphrag(project, project_path, project_name, project_description)
    if method == Method.RAPTOR:
        print(Fore.YELLOW + Style.BRIGHT + "Executing project: " + project + " - " + project_description
              + Fore.YELLOW + "Using Raptor" + Style.RESET_ALL)
        execute_project_feed_logs_to_raptor(project, project_path, project_name, project_description)
    if method == Method.LONG_CONTEXT:
        print(Fore.YELLOW + Style.BRIGHT + "Executing project: " + project + " - " + project_description
              + Fore.YELLOW + "Using Long context" + Style.RESET_ALL)
        execute_project_feed_logs_longcontext(project, project_path, project_name, project_description)

def print_config():

    config = configparser.ConfigParser()
    config.read('config.ini')

    for section in config.sections():
        print(f"Section: {section}")
        for key in config[section]:
            print(f"  Key: {key}, Value: {config[section][key]}")

def parse_info_ini(file_path):
    config = configparser.ConfigParser()
    config.read(file_path)
    project_info = {}
    for section in config.sections():
        if section == 'project_info':
            project_info['project'] = config.get(section, 'project')
            project_info['project_name'] = config.get(section, 'project_name')
            project_info['project_description'] = config.get(section, 'project_description')
            project_info['project_code'] = config.get(section, 'project_code')
    return project_info

def find_and_parse_info_ini(root_directory):
    project_infos = []
    for dirpath, dirnames, filenames in os.walk(root_directory):
        if 'info.ini' in filenames:
            file_path = os.path.join(dirpath, 'info.ini')
            project_info = parse_info_ini(file_path)
            project_info['project_dir'] =  dirpath
            project_infos.append(project_info)
    return project_infos

def select_project(project_infos):
    counter = 1
    project_list = {}

    for info in project_infos:
        print(Fore.YELLOW + Style.BRIGHT + "Option " + str(counter) + Style.RESET_ALL)
        print(f"Project: {info['project']}")
        print(f"Project Name: {info['project_name']}")
        print(f"Project Description: {info['project_description']}")
        # print(f"Project Code: {info['project_code']}")
        print(Fore.YELLOW + Style.BRIGHT + "-" * 40 + Style.RESET_ALL)
        project_list[counter] = info
        counter += 1

    print(Fore.YELLOW + Style.BRIGHT + "Choose one project (enter the option number): " + Style.RESET_ALL, end='')
    choice = int(input())

    if choice in project_list:
        selected_project = project_list[choice]
        print(Fore.GREEN + Style.BRIGHT + "Selected Project:" + Style.RESET_ALL)
        print(f"Project: {selected_project['project']}")
        print(f"Project Name: {selected_project['project_name']}")
        print(f"Project Description: {selected_project['project_description']}")
        # print(f"Project Code: {selected_project['project_code']}")
        return selected_project
    else:
        print(Fore.RED + Style.BRIGHT + "Invalid choice. Please try again." + Style.RESET_ALL)
        return None

if __name__ == "__main__":
    from llm.common import *
    query_llm("Hello world")

    config = configparser.ConfigParser()
    config.read('config.ini')

    # Troubleshooting
    # print_config(config)

    print(Fore.GREEN + "Retrieval augmented generation for Logs - " + Style.BRIGHT +
          " Version 1.0 " +  Style.DIM + " Author: SS" +  Style.RESET_ALL)
    root_directory = config.get('projects', 'project_directory')

    project_infos = find_and_parse_info_ini(root_directory)
    selected_project = select_project(project_infos)

    if selected_project:
        # You can now use the selected_project information as needed
        print("Code location: " +  str(selected_project['project_dir']) + "/" + selected_project['project_code'])

    print(Fore.YELLOW + Style.BRIGHT + "Choose one RAG methods: 1. Raptor, 2. GraphRAG, 3. Long context " + Style.RESET_ALL, end='')
    choice = int(input())
    method = 0
    if choice == 1:
        method = Method.RAPTOR
    if choice == 2:
        method = Method.GRAPH_RAG
    if choice == 3:
        method = Method.LONG_CONTEXT

    execute( method, project=selected_project['project'],
             project_path=str(selected_project['project_dir']) + str(os.sep)+ selected_project['project_code'],
             project_name=selected_project['project'], project_description=selected_project['project_description'])



