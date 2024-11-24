# NeYapAI

## Setup

Create a `.env` file in the root directory and add the following environment variables:

```.env
MONGODB_URI="mongodb+srv://ardaaltinors:<PASSW0RD>@cluster0.dxted.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
DATABASE_NAME=dev

GEMINI_API_KEY=<https://aistudio.google.com/apikey>
LANGCHAIN_TRACING_V2="true"
LANGCHAIN_ENDPOINT="https://api.smith.langchain.com"
LANGCHAIN_API_KEY=<GET-FROM-LANGSMITH>
LANGCHAIN_PROJECT="neyapai-test"
```

## Running Demo Frontend

- Switch to the `UI` directory
- Run Streamlit server

```bash
   streamlit run ui/main.py
```


## Running Backend

- Switch to the `server` directory

- Run FastAPI development server

```bash
   pipenv run uvicorn server.main:app --reload 
```