from pre_processor.raptor_preprocessor import *
import pdfkit
from plantuml import *
import datetime
import plantuml
from collections import defaultdict
import os
import re
from pygments import highlight
from pygments.formatters import Terminal256Formatter
from pygments.lexers import PythonLexer
from typing import Any
import subprocess
from pprint import pformat
from pathlib import Path


#====================== Set before the test ========================
config = configparser.ConfigParser()
config.read('config.ini')
llm = config.get('llm_in_use', 'llm')
def run_script_and_capture_logs(script_path, file_name):
    """
    Runs the script as a subprocess and captures its logs.
    :param script_path: Path to the Python script to run.
    :return: List of log lines from the script.
    """
    print(Fore.CYAN + "Running script " + str(script_path))

    commands = [
        "cd " + script_path,
        "source venv/bin/activate",
        "PYTHONPATH=$(pwd) python3 scripts/" + file_name
    ]

    # Combine the commands into a single shell execution
    command = " && ".join(commands)
    log_lines = []
    # Run the commands
    try:
        result = subprocess.run(
            command,
            shell=True,  # Required for combining multiple commands
            check=True,  # Raise an exception if the command fails
            stdout=subprocess.PIPE,  # Capture standard output
            stderr=subprocess.PIPE  # Capture error output
        )

        log_lines = [line.strip() for line in result.stderr.decode().split('\n') if line.strip()]

        print(Fore.CYAN + "Cleaning project ")

        commands = [
            "cd " + script_path,
            "source venv/bin/activate",
            "PYTHONPATH=$(pwd) python3 scripts/" + "clean.py"
        ]

        command = " && ".join(commands)

        subprocess.run(
            command,
            shell=True,  # Required for combining multiple commands
            check=True,  # Raise an exception if the command fails
            stdout=subprocess.PIPE,  # Capture standard output
            stderr=subprocess.PIPE  # Capture error output
        )

        for log in log_lines:
            print(Fore.YELLOW + log)

        if len(log_lines) > 0:
            return log_lines

        # Check if the script ran successfully
        if result.returncode != 0:
            print(f"Script failed with return code {result.returncode}")
            print(f"Error output: {result.stderr}")
            return []


    except subprocess.CalledProcessError as e:
        print(Fore.RED + f"Command failed with return code {e.returncode}")
        print(Fore.RED + "Output:\n", e.stdout.decode())
        print(Fore.RED + "Errors:\n", e.stderr.decode())
        return log_lines

    except Exception as e:
        print(f"Error running script: {e}")
        return []


def extract_plantuml(text):
    """
    Extracts the PlantUML code block from a given text.

    Parameters:
    - text (str): The response text containing a PlantUML diagram.

    Returns:
    - str: Extracted PlantUML code.
    """
    match = re.search(r"```plantuml\n(.*?)\n```", text, re.DOTALL)
    return match.group(1) if match else None

def remove_plantuml(text):
    """
    Removes the PlantUML code block from a given text.

    Parameters:
    - text (str): The response text containing a PlantUML diagram.

    Returns:
    - str: The text without the PlantUML section.
    """
    return re.sub(r"```plantuml\n.*?\n```", "", text, flags=re.DOTALL).strip()

def try_plant_uml_backup(plantuml_file):
    try:
        plant_tool_server = config.get('tools', 'backup_plant_uml_server')
        print(Fore.MAGENTA + "Plant UML server is " + plant_tool_server + "/plantuml/img/")
        uml = plantuml.PlantUML(url=plant_tool_server + "/plantuml/img/")
        uml.processes_file(plantuml_file)  # Generates `diagram.png`
    except PlantUMLHTTPError as e:
        print(Fore.RED + Style.BRIGHT + f"HTTP Error while communicating with PlantUML server: {e}"+ Style.RESET_ALL)
        return False
    except PlantUMLConnectionError as e:
        print(Fore.RED + Style.BRIGHT + f"Connection error with PlantUML server: {e}"+ Style.RESET_ALL)
        return False
    except PlantUMLError as e:
        print(Fore.RED + Style.BRIGHT + f"General PlantUML processing error: {e}"+ Style.RESET_ALL)
        return False
    except Exception as e:
        print(Fore.RED + Style.BRIGHT + f"An unexpected error occurred: {e}"+ Style.RESET_ALL)
        print(Fore.RED + "Plant UML server not available "+ Style.RESET_ALL)
        return False
    return True


def get_plant_uml_image(plantuml_file):
    try:
        plant_tool_server = config.get('tools', 'plant_uml_server')
        print(Fore.MAGENTA + "Plant UML server is " + plant_tool_server + "/plantuml/png/")
        uml = plantuml.PlantUML(url=plant_tool_server + "/plantuml/png/")
        uml.processes_file(plantuml_file)  # Generates `diagram.png`
    except PlantUMLHTTPError as e:
        print(Fore.RED + Style.BRIGHT + f"HTTP Error while communicating with PlantUML server: {e} ... Retrying"+ Style.RESET_ALL)
        if not try_plant_uml_backup(plantuml_file):
            return False
    except PlantUMLConnectionError as e:
        print(Fore.RED + Style.BRIGHT + f"Connection error with PlantUML server: {e} ... Retrying"+ Style.RESET_ALL)
        if not try_plant_uml_backup(plantuml_file):
            return False
    except PlantUMLError as e:
        print(Fore.RED + Style.BRIGHT + f"General PlantUML processing error: {e}  ... Retrying"+ Style.RESET_ALL)
        if not try_plant_uml_backup(plantuml_file):
            return False
    except Exception as e:
        print(Fore.RED + Style.BRIGHT + f"An unexpected error occurred: {e}"+ Style.RESET_ALL)
        print(Fore.RED + "Plant UML server not available  ... Retrying"+ Style.RESET_ALL)
        if not try_plant_uml_backup(plantuml_file):
            return False
    return True

def create_pdf_with_plantuml_from_response(directory, text, filename, prefix, logs = None, plantuml_txt = None):
    image_path = directory + str(os.sep) + "diagram.png"
    plantuml_file = directory + str(os.sep) + "diagram.puml"

    # If false, PlantUML is flaky
    plantuml_ret = False

    if plantuml_txt is not None:
        with open(plantuml_file, "w") as f:
            f.write(plantuml_txt)
        plantuml_ret = get_plant_uml_image(plantuml_file)

    now = datetime.datetime.now()
    section = "This report was generated on " + now.strftime("%I:%M%p on %B %d, %Y")
    footer_text = "This is an LLM generated report - please be aware of hallucinations <br>  (Esp if you provide an incorrect prompt/insufficient data)"
    header_text = ""

    md_extensions = ['codehilite', 'fenced_code']
    import markdown
    html_content = markdown.markdown(text, extensions=md_extensions)

    html = f"""
    <!DOCTYPE html>
    <html>
     <div class="container-fluid report-header">
        <div class="row">
               <div class="col-xs-12">
                   <h2 style="text-align:center;"> {header_text}</h2>
                   <h4 style="text-align:center;"> {section}</h4>
               </div>
           </div>
        </div>
    <head>
        <meta charset="utf-8">
        <title></title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            img {{ max-width: 100%; height: auto; }}
            .log-container {{ background-color: #1e1e1e; /* Dark background */
                        color: #dcdcdc; /* Light text */
                        font-family: "Courier New", Courier, monospace; /* Monospace font */
                        padding: 15px;
                        border-radius: 5px;
                        overflow-x: auto; /* Horizontal scroll for long lines */
                        white-space: pre-wrap; /* Preserve line breaks */
                        word-wrap: break-word; /* Wrap long words */ }}
        </style>
    </head>
     <body>
       <div>{html_content}</div>
    """
    if os.path.isfile(image_path):
        add_image_html = f"""
        <img src="file://{image_path}" alt="PlantUML Diagram"> </img>
        """
        html = html + add_image_html
    else:
        if plantuml_txt is not None:
            html += f"""<h3> Plant UML image was not generated due to server error - use planttext.com </h3> <div class="log-container">"""
            html += plantuml_txt
            html += "</div>"
    log_text = ""
    if logs is not None and len(logs) > 0:
        log_text = f"""<h4> Logs: </h4> <div class="log-container">"""

        for log in logs:
            log_text += "" + log + " <br>"
        log_text += "</div>"

    if log_text.strip() != "":
        html = html + log_text

    html = html + f"""
    <div class="container-fluid report-header">
           <div class="row">
               <div class="col-xs-12">
                   <h2 style="text-align:center;"> {footer_text}</h2>
               </div>
             </div>
            </div>
       </body>
    </html>"""

    html_file = directory + str(os.sep)  + "output.html"
    os.makedirs(directory + str(os.sep) , exist_ok=True)

    with open(html_file, "w") as f:
        f.write(html)

    pdf_path = str(Path(directory).parents[0])+ str(os.sep) + "outputs" + str(os.sep)  + filename + "_" + prefix + ".pdf"

    # Configure pdfkit with the path to wkhtmltopdf
    pdf_tool_path = config.get('tools', 'wkhtmltopdf_path')
    pdfkit_config = pdfkit.configuration(wkhtmltopdf=pdf_tool_path)

    options = {
        '--enable-local-file-access': '',
    }

    # Convert HTML to PDF
    pdfkit.from_file(html_file, pdf_path, options=options, configuration=pdfkit_config)

    # Clean up
    if os.path.isfile(html_file):
        os.remove(html_file)
    if os.path.isfile(plantuml_file):
        os.remove(plantuml_file)
    if os.path.isfile(image_path):
        os.remove(image_path)

def render_to_pdf(location, content, filename, prefix, logs = None):
    plant_text = None
    if "@startuml" in content:
        plant_text = extract_plantuml(content)
        content = remove_plantuml(content)

    create_pdf_with_plantuml_from_response(directory = location, text = content, plantuml_txt = plant_text, filename=filename, logs = logs, prefix=prefix)




def pprint_color(obj: Any) -> None:
    """Pretty-print in color."""
    print(highlight(pformat(obj), PythonLexer(), Terminal256Formatter()), end="")