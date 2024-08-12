from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
from dotenv import load_dotenv
load_dotenv()
import httpx
from fastapi import FastAPI, HTTPException, File, UploadFile,Form
from pydantic import BaseModel
from typing import List, Dict,Optional
import uvicorn
import shutil
import atexit
from metrics_functions import compute_bleu, compute_rouge, improved_semantic_coherence
from fastapi.middleware.cors import CORSMiddleware
import logging

logging.basicConfig(level=logging.INFO)

app = FastAPI()
origins = ["http://localhost.tiangolo.com","https://localhost.tiangolo.com","http://localhost:3000","http://localhost:8080"]
app.add_middleware(CORSMiddleware,allow_origins=origins,allow_credentials=True,allow_methods=["*"],allow_headers=["*"])

api_key = os.getenv('OPENAI_API_KEY')
base_url = os.getenv('API_URL')
max_output_tokens = 250
streaming = False
http_client = httpx.Client(verify=False)
available_models = [
    "mixtral-8x7b-instruct-v01", 
    "gemma-7b-it", 
    "mistral-7b-instruct-v02", 
    "llama-2-70b-chat", 
    "phi-3-mini-128k-instruct", 
    "llama-3-8b-instruct"]
embedding_models = [
    "all-MiniLM-L6-v2",
    "paraphrase-multilingual-MiniLM-L12-v2",
    "all-mpnet-base-v2",
    "multi-qa-mpnet-base-dot-v1",
    "distiluse-base-multilingual-cased-v2"
]
model_selected = available_models[5]
global_texts = None
langchain_llm = ChatOpenAI(
    base_url=base_url,
    model=model_selected,
    http_client=http_client,
    api_key=api_key
)
embeddings = [HuggingFaceEmbeddings(model_name=model) for model in embedding_models]

def load_document(file_path):
    _, file_extension = os.path.splitext(file_path)
    
    if file_extension.lower() == '.pdf':
        loader = PyPDFLoader(file_path)
    elif file_extension.lower() == '.txt':
        print("Here")
        loader = TextLoader(file_path ,encoding = 'UTF-8')
        print("Loaded Successfully")
    else:
        raise ValueError(f"Unsupported file type: {file_extension}")
    print(loader)
    try:
        documents = loader.load()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    print(documents)
    # Split the document into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    texts = text_splitter.split_documents(documents)
    print("Here1")
    return [doc.page_content for doc in texts]

def create_vector_stores(texts, embeddings):
    vector_stores = []
    for embedding in embeddings:
        vector_store = FAISS.from_texts(texts, embedding)
        vector_stores.append(vector_store)
    return vector_stores

def query_vector_stores(query, vector_stores, llm):
    results = []
    for i, vector_store in enumerate(vector_stores):
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=vector_store.as_retriever()
        )
        result = qa_chain.run(query)
        results.append(f"Model {i+1} result: {result}")
    return "/n/n".join(results)

def calculate_rank(ground_truth, responses):
    ranks = []
    if isinstance(ground_truth, list):
        ground_truth = " ".join(ground_truth)
    for response in responses:
        ranks.append(compute_bleu(ground_truth, response))
    
    for i, response in enumerate(responses):
        ranks[i] += compute_rouge(ground_truth, response)
        ranks[i] = ranks[i] / 2

    min_tuple = tuple()
    min_sem_coh = 10  # contains the minimum semantic coherence value and the index of the response
    for i, response in enumerate(responses):
        sem_coh = improved_semantic_coherence(response)
        min_sem_coh = min(min_sem_coh, sem_coh)
        if min_sem_coh == sem_coh:
            min_tuple = (sem_coh, i)
    ranks[min_tuple[1]] = 0
    
    # Return the ranks along with their indices
    return [(rank, i) for i, rank in enumerate(ranks)]

class QueryRequest(BaseModel):
    query: str
    models: Optional[List[str]] = None

class QueryResponse(BaseModel):
    results: List[Dict[str, str]]


@app.post("/upload-and-query")
async def upload_and_query(
    file: UploadFile = File(...),
    query: Optional[str] = Form(None),
    models: List[str] = Form(None)
):
    
    global global_texts
    try:
        # Parse the models string into a list
        # Check the type of the first element in models and process accordingly
        model_str = models[0]
        if isinstance(model_str, list):
            selected_models = [embedding_models[int(model)] for model in model_str]
        else:
            new_model = str(model_str)
            model_list=[]
            model_list = new_model.split(",")   
            model_list_1 = [int(i) for i in model_list]
            selected_models = [embedding_models[model] for model in model_list_1]
            

        # Save the uploaded file temporarily
        with open(file.filename, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        # Load and process the document
        global_texts = load_document(file.filename)
        # Create vector stores only for selected models
        selected_embeddings = [emb for emb, model in zip(embeddings, embedding_models) if model in selected_models]
        vector_stores = create_vector_stores(global_texts, selected_embeddings)
        responses = []
        # If a query is provided, process it
        if query:
            results = []
            for i, vector_store in enumerate(vector_stores):
                qa_chain = RetrievalQA.from_chain_type(
                    llm=langchain_llm,
                    chain_type="stuff",
                    retriever=vector_store.as_retriever()
                )
                result = qa_chain.invoke(query)
                responses.append(result['result'])
               
            
            ranks_with_indices = calculate_rank(global_texts, responses)
            
            # Sort responses by rank
            sorted_responses = sorted(ranks_with_indices, key=lambda x: x[0],reverse=True)
            print(sorted_responses)
            # Create results with rank and sorted responses
            results = []
            for rank, index in sorted_responses:
                results.append({
                    "model": selected_models[index],
                    "response": responses[index],
                    "rank": str(rank)
                })
            
            
            return QueryResponse(results=results)
        else:
            # Clean up the temporary file
            @atexit.register
            def remove_temp_file():
                if os.path.exists(file.filename):
                    os.remove(file.filename)    
            return {"message": "File processed successfully. Use /query endpoint to ask questions."}
    
    except Exception as e:
        # Ensure the temporary file is removed in case of an error
        if os.path.exists(file.filename):
            os.remove(file.filename)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query", response_model=QueryResponse)
async def query_endpoint(request: QueryRequest):
    
    global global_texts
   
    if global_texts is None:
        raise HTTPException(status_code=400, detail="No file uploaded yet. Please upload a file first using /upload-and-query.")

    # making the global vector stores for the required models
    selected_models  = [embedding_models[int(model)] for model in request.models]
    selected_embeddings = [emb for emb, model in zip(embeddings, embedding_models) if model in selected_models]
    vector_stores = create_vector_stores(global_texts, selected_embeddings)
    responses = []
    try:
        results = []
        for i, vector_store in enumerate(vector_stores):
            qa_chain = RetrievalQA.from_chain_type(
                llm=langchain_llm,
                chain_type="stuff",
                retriever=vector_store.as_retriever()
            )
            result = qa_chain.invoke(request.query)
            responses.append(result['result'])
        
        ranks_with_indices = calculate_rank(global_texts, responses)
        
        # Sort responses by rank
        sorted_responses = sorted(ranks_with_indices, key=lambda x: x[0], reverse=True)
        print(sorted_responses)
        # Create results with rank and sorted responses
        results = []
        for i, rank in enumerate(sorted_responses):
            current_rank, index = rank
            results.append({
                "model": embedding_models[index],
                "response": responses[index],
                "rank": str(i+1)
            })
        return QueryResponse(results=results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, port=8000)



