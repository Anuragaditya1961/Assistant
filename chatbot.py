# Importing libraries
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import os
from dotenv import load_dotenv
from ollama import Client

load_dotenv()
clientHost=os.getenv("hostName")

# App declaration
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

@app.get("/Response")
def fetch_item(Query:str=None):
    
    # PromptMaker
    def promptMaker(Query):
        content=f"""
            User Query: '{Query}'.
            Instructions for You:
            1. You are a helpful, respectful and honest assistant.
            2. Always answer as helpfully as possible, while being safe.
            3. keep your response precise while not missing any information.
            4. Please ensure that your responses are socially unbiased and positive in nature. 
            5. If you don't know the answer to a question, please don't share false information.
            """
        return content
    
    # Client calling function to get response from LLM (with streaming)
    def clientCall(clientHost, content):
        client = Client(host=clientHost)

        # Sending the Prompt to LLM and enabling stream=True
        stream = client.chat(
            model="llama3.2",
            messages=[{'role': 'user', 'content': content}],
            stream=True,  # Enabling stream
        )

        # Generator to yield each message as it comes in
        for message in stream:
            
            yield message['message']['content']
    
    
    # checking for Query whether call is for Summary or Response of User
    if Query:
        # Making Prompt
        prompt = promptMaker(Query)


        # Create a generator for streaming
        def message_generator():

            # Stream LLM response
            for message in clientCall(clientHost, prompt):
                yield message

        # Return StreamingResponse with generator
        return StreamingResponse(message_generator(), media_type="text/plain")