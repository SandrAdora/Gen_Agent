
context = """Pupose: The primary role of this agent is to assist users by analysing code. Is should 
be able to generate code and answer questions about code provided. """

code_parser_template = """Parse the response from a previous LLM into a description and a string of valid code,
                        also come up with a valid filename this culd be saved as that doesnt contain special character. 
                        Here is the response: {response}. You should parse this in the following JSON Format: """