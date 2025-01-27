from utility.utils import *
import re
from pathlib import Path
from typing import List, Dict, Any
import pprint
from llm.vertex_adapter import *
from pre_processor.longcontext_preprocessor import *
from pre_processor.graphrag_preprocessor import add_code_chunks_to_graph_db, clear_neo4j_database


def execute_project_feed_logs_longcontext(project, project_path, project_name, project_description):
    invocation_dir = str(Path(project_path).parents[0])

    script_dir = str(Path(project_path).parents[0]) + str(os.sep) + "scripts"
    files = os.listdir(script_dir)

    main_scripts = [f for f in files if f.startswith("main") and f.endswith(".py")]

    if not main_scripts:
        print("No files starting with 'main' found in the folder.")

    # Troubleshooting
    # pprint.pprint(main_scripts)

    context = embed_code_into_clusters_long_context(project_path, project, project_description)
    main_scripts.sort()

    for file in main_scripts:
        logs = []
        query_file = os.path.basename(file).split(".")[0] + ".txt"
        query_file_path = invocation_dir + str(os.sep) + "scripts" + str(os.sep) + query_file

        res = run_script_and_capture_logs(invocation_dir, file)
        if res is not None:
            logs.extend(res)

        with open(query_file_path, "r") as f:
            query = f.read()

        print(Fore.CYAN + Style.DIM  +"Query " + str(query) + " Read from " + query_file_path + Style.RESET_ALL)

        if query is None or query.strip() == "":
            query = "Here are logs of the project, analyse them and make a plantuml sequence diagram of the code flow"

        # Format prompt for LLM
        final_prompt = f"You are an expert developer analyzing code and logs to troubleshoot errors.\n\nContext:\n{context}\n\nQuestion:\n{query}"

        if logs:
            final_prompt += f"\nLogs:\n{logs}"

        count_tokens(final_prompt)

        # Get response from Gemini Pro
        print(Fore.CYAN + Style.DIM + "Prompt" + Style.RESET_ALL)
        pprint_color(final_prompt)
        response = query_llm(final_prompt)

        print(response)

        render_to_pdf(location=str(Path(project_path).parents[0]) + str(os.sep) + "scripts", content=response,
                      filename=os.path.basename(file).split(".")[0], prefix = "long_context", logs=logs)
