# Insurance RAG System Architecture

## High Level Architecture

                         ┌────────────────────────────┐
                         │        User / PM            │
                         │  Streamlit Chat Interface   │
                         └──────────────┬─────────────┘
                                        │
                                        │ User Question
                                        ▼
                         ┌────────────────────────────┐
                         │        app.py              │
                         │ Streamlit UI + Chat Memory │
                         │ last 5 Q&A in session      │
                         └──────────────┬─────────────┘
                                        │
                                        ▼
                         ┌────────────────────────────┐
                         │      rag_chain.py          │
                         │ Builds prompt              │
                         │ Adds chat history          │
                         │ Calls retriever + LLM      │
                         └──────────────┬─────────────┘
                                        │
                                        ▼
                         ┌────────────────────────────┐
                         │      Retriever             │
                         │ MMR semantic search        │
                         │ Top K relevant chunks      │
                         └──────────────┬─────────────┘
                                        │
                                        ▼
                         ┌────────────────────────────┐
                         │      ChromaDB              │
                         │ Stores chunk embeddings    │
                         │ Metadata + chunk_id hash   │
                         └──────────────┬─────────────┘
                                        │
                                        ▼
                         ┌────────────────────────────┐
                         │ Retrieved Context          │
                         │ Policy chunks + sources    │
                         └──────────────┬─────────────┘
                                        │
                                        ▼
                         ┌────────────────────────────┐
                         │ OpenRouter LLM             │
                         │ Generates grounded answer  │
                         └──────────────┬─────────────┘
                                        │
                                        ▼
                         ┌────────────────────────────┐
                         │ Final Answer in UI         │
                         └────────────────────────────┘

## Data Ingestion Flow

                ┌──────────────────────┐
                │ Insurance Documents  │
                │ PDF / TXT / MD / CSV │
                └──────────┬───────────┘
                           │
                           ▼
                ┌──────────────────────┐
                │ Document Loaders     │
                │ PyMuPDFLoader        │
                │ TextLoader           │
                │ CSVLoader            │
                │ MarkdownLoader       │
                └──────────┬───────────┘
                           │
                           ▼
                ┌──────────────────────┐
                │ Data Cleaning        │
                │ Remove extra spaces  │
                │ Normalize text       │
                │ Clean formatting     │
                └──────────┬───────────┘
                           │
                           ▼
                ┌──────────────────────┐
                │ Chunking             │
                │ Size = 1000          │
                │ Overlap = 200        │
                └──────────┬───────────┘
                           │
                           ▼
                ┌──────────────────────┐
                │ Hash Mapping         │
                │ Generate chunk_id    │
                │ MD5 hash             │
                └──────────┬───────────┘
                           │
                           ▼
                ┌──────────────────────┐
                │ Embeddings           │
                │ BAAI/bge-small-en    │
                │ v1.5                 │
                └──────────┬───────────┘
                           │
                           ▼
                ┌──────────────────────┐
                │ ChromaDB             │
                │ Vector Database      │
                └──────────────────────┘





1. Insurance documents (PDF, TXT, Markdown, CSV) load kiye.
2. Data clean kiya aur unnecessary formatting remove ki.
3. Documents ko 1000 character chunks me split kiya with 200 overlap.
4. Har chunk ka unique hash ID generate kiya for tracking.
5. Har chunk ko BGE embedding model se vector me convert kiya.
6. Embeddings aur metadata ChromaDB vector database me store kiye.
7. Ye database baad me semantic search ke liye use hota hai.

## Online Question Answering Flow

                    ┌─────────────────────┐
                    │      User           │
                    │  Ask Question       │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │    Streamlit UI     │
                    │ Receives Question   │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   Chat Memory       │
                    │ Last 5 Conversations│
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Query Processing    │
                    │ Build Retrieval     │
                    │ Query               │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   Retriever         │
                    │ MMR Semantic Search │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │     ChromaDB        │
                    │ Vector Search       │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Top-K Chunks        │
                    │ Relevant Context    │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   Prompt Builder    │
                    │ Context + Memory    │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   OpenRouter LLM    │
                    │ Generate Answer     │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   Final Answer      │
                    │ Returned to User    │
                    └─────────────────────┘

## Components

### 1. Data Sources
- PDF
- TXT
- Markdown
- CSV

### 2. Chunking
- RecursiveCharacterTextSplitter
- Chunk Size = 1000
- Chunk Overlap = 200

### 3. Hash Mapping
- MD5 based chunk_id generation
- Used for chunk tracking

### 4. Embeddings
- BAAI/bge-small-en-v1.5

### 5. Vector Database
- ChromaDB

### 6. Retrieval
- MMR (Maximum Marginal Relevance)
- Top K = 5

### 7. LLM
- OpenRouter
- Google Gemma / Llama based model

### 8. Memory
- Last 5 conversation turns
- Session-based memory

### 9. Frontend
- Streamlit UI