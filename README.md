# VID: The Virtual Information Desk AI Assistant

VID is a sophisticated, conversational AI assistant designed to provide comprehensive information about PES University. It leverages a powerful multi-agent system and a hybrid Retrieval-Augmented Generation (RAG) architecture to answer a wide range of user queries, from simple greetings to complex, multi-part questions.

## Core Features

- **Hybrid RAG Architecture**: VID seamlessly queries both a **PostgreSQL database** for structured, factual data (like lecturer details, club info) and a **FAISS vector store** for unstructured, descriptive content from PDF documents (like course objectives and university policies).
- **Multi-Agent System**: The system's logic is distributed among specialized AI agents, each with a distinct role:
    - **Planner Agent**: Analyzes the user's query and creates a dynamic, multi-step execution plan.
    - **Text-to-SQL Agent**: Converts natural language questions into executable PostgreSQL queries.
    - **Retriever/Reasoner Agents**: Perform semantic searches on the vector database and refine the retrieved context.
    - **Synthesizer Agent**: Generates a final, coherent, and conversational response based on the collected evidence.
- **Advanced Multi-Step Reasoning**: VID can understand and answer complex hybrid queries (e.g., "What are the objectives of the 5-credit Python course?") by creating a plan to first find the specific course in the database and then use that information to search the documents.
- **Self-Correcting SQL**: The Text-to-SQL agent is equipped with a retry mechanism. If it generates an invalid SQL query, it analyzes the database error and attempts to correct itself, significantly improving reliability.
- **Fully Configurable LLM Backend**: The AI's "brain" is highly flexible. You can easily switch between different LLM providers (`Google Gemini`, `Anthropic Claude`, `local Ollama`) and specific models by changing a single line in the `.env` file.
- **Timeout & Fallback Logic**: The system can be configured to use a primary LLM (like a local Ollama model) and automatically fall back to a more powerful cloud API if the primary model fails or takes too long to respond.

## Project Structure

```
vid-backend/
├── agents/
│   ├── planner.py         # Decomposes user query into a step-by-step plan
│   ├── text_to_sql.py     # Converts natural language to SQL, with self-correction
│   ├── synthesizer.py     # Generates the final, conversational response
│   ├── retriever_agent.py # Retrieves data from the vector store
│   └── reasoner.py        # Refines retrieved document chunks
├── core/
│   ├── db/
│   │   ├── database.py          # SQLAlchemy engine and session management
│   │   └── schema_inspector.py  # Dynamically gets DB schema for agents
│   ├── llm/
│   │   └── llm_client.py      # Centralized client for all LLM API calls (Gemini, Claude, Ollama)
│   └── rag/
│       ├── pdf_processor.py     # Processes PDFs into text chunks
│       └── vector_store.py      # Manages the FAISS vector database
├── data/
│   ├── archive/             # Stores CSVs that have been successfully ingested
│   ├── documents/
│   │   ├── source/          # Place source PDF files here
│   │   └── processed/       # Stores the generated FAISS vector index
│   └── staging/             # Place new CSV files here for ingestion
├── .env                     # Your local environment configuration (API keys, DB credentials)
├── .env.example             # Template for the .env file
├── .gitignore               # Specifies files for Git to ignore
├── app.py                   # Main Streamlit application UI and agent execution engine
├── ingest_data.py           # Script to ingest CSV data from /staging into PostgreSQL
├── process_documents.py     # Script to process PDFs from /source into the vector store
├── requirements.txt         # Project dependencies
└── run_dev.py               # Helper script to run the Streamlit app with hot-reloading
```

## Setup and Installation

1.  **Clone the Repository**
    ```bash
    git clone <your-repository-url>
    cd vid-backend
    ```

2.  **Create a Virtual Environment**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up PostgreSQL**
    - Ensure you have a PostgreSQL server running.
    - Create a new database (e.g., `VID`).

5.  **Configure Environment Variables**
    - Make a copy of the example environment file:
      ```bash
      cp .env.example .env
      ```
    - Edit the `.env` file with your specific credentials:
        - `PRIMARY_LLM_PROVIDER` and `FALLBACK_LLM_PROVIDER` (e.g., `google`, `anthropic`, `ollama`)
        - Your `GOOGLE_API_KEY` and/or `ANTHROPIC_API_KEY`.
        - Your PostgreSQL `DB_USER`, `DB_PASSWORD`, and `DB_NAME`.

## Usage

Follow these steps to populate the knowledge base and run the application.

1.  **Ingest Structured Data (CSVs)**
    - Place any CSV files you want to add to the database into the `data/staging/` directory.
    - Run the ingestion script:
      ```bash
      python ingest_data.py
      ```
    - The script will create tables in PostgreSQL, load the data, and move the processed CSVs to `data/archive/`.

2.  **Process Unstructured Data (PDFs)**
    - Place your PDF documents into the `data/documents/source/` directory.
    - Run the document processing script to create the vector store:
      ```bash
      python process_documents.py
      ```
    - This will generate a FAISS index in the `data/documents/processed/` folder.

3.  **Run the AI Assistant**
    - Start the Streamlit application:
      ```bash
      python run_dev.py
      ```
    - Open your web browser to `http://localhost:8501` to interact with the AI.
```# VID: The Virtual Information Desk AI Assistant

VID is a sophisticated, conversational AI assistant designed to provide comprehensive information about PES University. It leverages a powerful multi-agent system and a hybrid Retrieval-Augmented Generation (RAG) architecture to answer a wide range of user queries, from simple greetings to complex, multi-part questions.

## Core Features

- **Hybrid RAG Architecture**: VID seamlessly queries both a **PostgreSQL database** for structured, factual data (like lecturer details, club info) and a **FAISS vector store** for unstructured, descriptive content from PDF documents (like course objectives and university policies).
- **Multi-Agent System**: The system's logic is distributed among specialized AI agents, each with a distinct role:
    - **Planner Agent**: Analyzes the user's query and creates a dynamic, multi-step execution plan.
    - **Text-to-SQL Agent**: Converts natural language questions into executable PostgreSQL queries.
    - **Retriever/Reasoner Agents**: Perform semantic searches on the vector database and refine the retrieved context.
    - **Synthesizer Agent**: Generates a final, coherent, and conversational response based on the collected evidence.
- **Advanced Multi-Step Reasoning**: VID can understand and answer complex hybrid queries (e.g., "What are the objectives of the 5-credit Python course?") by creating a plan to first find the specific course in the database and then use that information to search the documents.
- **Self-Correcting SQL**: The Text-to-SQL agent is equipped with a retry mechanism. If it generates an invalid SQL query, it analyzes the database error and attempts to correct itself, significantly improving reliability.
- **Fully Configurable LLM Backend**: The AI's "brain" is highly flexible. You can easily switch between different LLM providers (`Google Gemini`, `Anthropic Claude`, `local Ollama`) and specific models by changing a single line in the `.env` file.
- **Timeout & Fallback Logic**: The system can be configured to use a primary LLM (like a local Ollama model) and automatically fall back to a more powerful cloud API if the primary model fails or takes too long to respond.

## Project Structure

```
vid-backend/
├── agents/
│   ├── planner.py         # Decomposes user query into a step-by-step plan
│   ├── text_to_sql.py     # Converts natural language to SQL, with self-correction
│   ├── synthesizer.py     # Generates the final, conversational response
│   ├── retriever_agent.py # Retrieves data from the vector store
│   └── reasoner.py        # Refines retrieved document chunks
├── core/
│   ├── db/
│   │   ├── database.py          # SQLAlchemy engine and session management
│   │   └── schema_inspector.py  # Dynamically gets DB schema for agents
│   ├── llm/
│   │   └── llm_client.py      # Centralized client for all LLM API calls (Gemini, Claude, Ollama)
│   └── rag/
│       ├── pdf_processor.py     # Processes PDFs into text chunks
│       └── vector_store.py      # Manages the FAISS vector database
├── data/
│   ├── archive/             # Stores CSVs that have been successfully ingested
│   ├── documents/
│   │   ├── source/          # Place source PDF files here
│   │   └── processed/       # Stores the generated FAISS vector index
│   └── staging/             # Place new CSV files here for ingestion
├── .env                     # Your local environment configuration (API keys, DB credentials)
├── .env.example             # Template for the .env file
├── .gitignore               # Specifies files for Git to ignore
├── app.py                   # Main Streamlit application UI and agent execution engine
├── ingest_data.py           # Script to ingest CSV data from /staging into PostgreSQL
├── process_documents.py     # Script to process PDFs from /source into the vector store
├── requirements.txt         # Project dependencies
└── run_dev.py               # Helper script to run the Streamlit app with hot-reloading
```

## Setup and Installation

1.  **Clone the Repository**
    ```bash
    git clone <your-repository-url>
    cd vid-backend
    ```

2.  **Create a Virtual Environment**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up PostgreSQL**
    - Ensure you have a PostgreSQL server running.
    - Create a new database (e.g., `VID`).

5.  **Configure Environment Variables**
    - Make a copy of the example environment file:
      ```bash
      cp .env.example .env
      ```
    - Edit the `.env` file with your specific credentials:
        - `PRIMARY_LLM_PROVIDER` and `FALLBACK_LLM_PROVIDER` (e.g., `google`, `anthropic`, `ollama`)
        - Your `GOOGLE_API_KEY` and/or `ANTHROPIC_API_KEY`.
        - Your PostgreSQL `DB_USER`, `DB_PASSWORD`, and `DB_NAME`.

## Usage

Follow these steps to populate the knowledge base and run the application.

1.  **Ingest Structured Data (CSVs)**
    - Place any CSV files you want to add to the database into the `data/staging/` directory.
    - Run the ingestion script:
      ```bash
      python ingest_data.py
      ```
    - The script will create tables in PostgreSQL, load the data, and move the processed CSVs to `data/archive/`.

2.  **Process Unstructured Data (PDFs)**
    - Place your PDF documents into the `data/documents/source/` directory.
    - Run the document processing script to create the vector store:
      ```bash
      python process_documents.py
      ```
    - This will generate a FAISS index in the `data/documents/processed/` folder.

3.  **Run the AI Assistant**
    - Start the Streamlit application:
      ```bash
      python run_dev.py
      ```
    - Open your web browser to `http://localhost:8501