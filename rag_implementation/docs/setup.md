## Project setup 

Unfortunately there are two packages which dont like each other 
```commandline
chromadb==0.5.23
transformers==4.48.1
```
Resolution between them is impossible as of today. That can be checked by 
```commandline
pip-compile req.in
pip-sync
```

Solution: Create two environments 
```
python3 -m venv raptorenv
python3 -m venv venv 
source raptorenv/bin/activate
```
The raptor impementation requirement is in raptor-requirement.in
```commandline
python -m ensurepip --upgrade or python -m pip install --upgrade pip
python -m pip install --upgrade setuptools
pip3 install -r requirements.txt 
pip3 install -e .
```
To save the requirements use 
```commandLine 
pip3 freeze > raptor-requirement.in
```

## Install model 

#### LLama 
Llama takes about 42GB diskspace and needs a 64GB of RAM for decent performance. To install Llama locally use 

```commandline
ollama run llama3.3
ollama serve 
```

Or you need to buy credits to use the web API 

#### Mistral 
The model used here is Nemo because of its long context window of 128K 
Download the model using the utility script. You will need a token from hugging face  

```commandline
huggingface-cli login
```
By default the model is saved in a cache directory /Users/username/.cache/huggingface

#### Vertex 
To setup the vertex credentials, locally use a credential which can be generated from Google cloud console
```commandline
export GOOGLE_APPLICATION_CREDENTIALS="/home/user/Downloads/my-key.json"
```

It also needs a project id, which can be generated using Google Cloud console 

#### Open AI
Need to purchase credits 


### To generate output PDFs 
On macOS 
https://wkhtmltopdf.org/downloads.html
```commandline
where wkhtmltopdf 
```
MacOS does not trust
Linux 
```commandline
apt-get install wkhtmltopdf
```
Windows 
Download from the website 

### plantuml

```commandline
java -jar res/plantuml.jar -picoweb:9000:127.0.0.1
```

The config looks like 
```commandline
[tools]
wkhtmltopdf_path=/usr/local/bin/wkhtmltopdf
plant_uml_server=127.0.0.1:9000
```

http://wkhtmltopdf.org/downloads.html
```
Add the path to the config.ini 

```commandline
export OPENAI_API_KEY="your_api_key_here"
```
and verify that it is set by 
```commandline
echo $OPENAI_API_KEY
```

# Neo4J 
Install Neo4J desktop app from https://neo4j.com 
Create a database. Hit start and setup config.ini


## Log to file 
main.py | tee logs/the_script.log

### important note 
Tree sitter version HAS to be 0.21.3 