from .models import Pipeline, Document, EvalResult
from core.ollama_client import chat
from sqlmodel import Session, select
import chromadb
from langchain_community.document_loaders import PyPDFLoader,TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from chromadb.utils.embedding_functions import OllamaEmbeddingFunction

chroma_client = chromadb.PersistentClient(path="./chroma_db")


def create_pipeline(session: Session, name: str, chunk_size: int, chunk_overlap: int, embedding_model: str) -> Pipeline:
    pipeline = Pipeline(name=name, chunk_size=chunk_size, chunk_overlap=chunk_overlap, embedding_model=embedding_model)
    session.add(pipeline)
    session.commit()
    session.refresh(pipeline)
    return pipeline

def get_pipeline(session: Session, pipeline_id: int) -> Pipeline | None:
    return session.get(Pipeline, pipeline_id)

def get_all_pipelines(session: Session) -> list[Pipeline]:
    return session.exec(select(Pipeline)).all()

def ingest_document(session: Session, pipeline_id: int,file_path: str,filename: str,file_type: str) -> Document:
    pipeline = get_pipeline(session, pipeline_id)
    if not pipeline:
        raise ValueError("Pipeline not found")
    
    if file_type == "pdf":
        loader = PyPDFLoader(file_path)
        docs = loader.load()
    else:
        docs = TextLoader(file_path).load()

    splitter = RecursiveCharacterTextSplitter(chunk_size=pipeline.chunk_size, chunk_overlap=pipeline.chunk_overlap)
    chunks = splitter.split_documents(docs)

    embedding_fn = OllamaEmbeddingFunction(
        model_name=pipeline.embedding_model,
        url="http://localhost:11434/api/embeddings"
    )
    collection = chroma_client.get_or_create_collection(name=f"pipeline_{pipeline_id}", embedding_function=embedding_fn)
    collection.add(documents=[chunk.page_content for chunk in chunks], metadatas=[{"source": filename} for _ in chunks],ids=[f"{filename}_{i}" for i in range(len(chunks))])

    document = Document(pipeline_id=pipeline_id, file_name=filename, file_type=file_type)
    session.add(document)
    session.commit()
    session.refresh(document)
    return document


def _get_embedding_fn(embedding_model: str) -> OllamaEmbeddingFunction:
    return OllamaEmbeddingFunction(
        model_name=embedding_model,
        url="http://localhost:11434/api/embeddings"
    )


def query_pipeline(session: Session, pipeline_id: int, question: str, model: str) -> dict:
    pipeline = get_pipeline(session, pipeline_id)
    if not pipeline:
        raise ValueError("Pipeline not found")

    collection = chroma_client.get_or_create_collection(
        name=f"pipeline_{pipeline_id}",
        embedding_function=_get_embedding_fn(pipeline.embedding_model)
    )

    results = collection.query(query_texts=[question], n_results=3)
    contexts = results["documents"][0]

    context_str = "\n\n".join(contexts)
    prompt = f"""Answer the question using only the context below.

Context:
{context_str}

Question: {question}"""

    response = chat(model=model, messages=[{"role": "user", "content": prompt}])

    return {
        "question": question,
        "answer": response.message.content,
        "contexts": contexts
    }