from llama_index.llms.ollama import Ollama
import llama_index.llms.openai as AI
from llama_parse import LlamaParse
from llama_index.core.tools import QueryEngineTool, ToolMetadata
#used to load in the data
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, PromptTemplate
from llama_index.core.embeddings import resolve_embed_model
from llama_index.core.agent import ReActAgent
from prompts import context, code_parser_template
from code_reader import code_reader
import ast

#output parser for testing whic
from pydantic import BaseModel
from llama_index.core.output_parsers import PydanticOutputParser
from llama_index.core.query_pipeline import QueryPipeline
import os

#importing the api key from env
from dotenv import load_dotenv



# Loading the  LLama cloud Api key
load_dotenv()


#initializing the model
llm = Ollama(model="mitral", request_timeout=3600.0)

parser = LlamaParse(result_type="markdown")

# Extract files that end with pdf
file_extractor = {".pdf": parser}
# Use the Simplediretory reader to search for a folder and give the files found in the folder into a json document
# You need to create a folder called data in your ide. In that folder insert the files readme.pdf and test.py
documents = SimpleDirectoryReader("./data", file_extractor=file_extractor).load_data()
#check if documents were loaded
print(documents)


embed_model = resolve_embed_model("local:BAAI/bge-m3")
vector_index = VectorStoreIndex.from_documents(documents, embed_model=embed_model)
query_engine = vector_index.as_query_engine(llm=llm)

# creating a tool
tools = [
    QueryEngineTool(
        query_engine= query_engine, 
        metadata=ToolMetadata(
                    name="api_doumentation", 
        description="this gives documentaion about code for an API. Use this for reading docs for APIs"

        ), 
    ),
    # Reader tool to read in code files like python files
    code_reader,


]
code_llm = Ollama(model="codellama", request_timeout=3600.0)
#creating an ageint
agent = ReActAgent.from_tools(tools, llm=code_llm, verbose=False, context=context)


class CodeOutput(BaseModel):
    code: str
    desription: str
    filename: str

parser = PydanticOutputParser(CodeOutput)
json_prompt_str = parser.format(code_parser_template)
json_prompt_templae = PromptTemplate(json_prompt_str)
output_pipline = QueryPipeline(chain=[json_prompt_templae, llm])


while (prompt := input("Enter a prompt (q to quit): ")) != "q":
    retries = 0

    while retries < 3:
        try: 
            """Handling exception """
            result = agent.query(prompt)
            next_result = output_pipline.run(response=result)
            cleaned_json = ast.literal_eval(str(next_result).replace("assistant: ", " "))
            break
        except Exception as e:
            retries += 1
            print(f"Error occured, retry# {retries}:", e)
    if retries >= 3:
        print("Unable to process request, try again...")
        continue
    

    print('Code generated')
    print(cleaned_json("code"))
    
    print("\n\nDescription: ", cleaned_json("description"))
    filename = cleaned_json["filename"]

    try:
        # In your ide you would need to create a folder called output
        with open(os.path.join("output" ,filename), "w") as f: #TO avoid overriting the file we already have
            f.write(cleaned_json["code"])
        print("Saved file", filename)
    except:
        print("Error saving file...")

