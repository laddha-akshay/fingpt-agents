# FinGPT Agents  
Lightweight finance research and analysis agents powered by retrieval and structured reasoning.

## Overview  
FinGPT Agents is a demo system that simulates a multi agent workflow for financial research.  
It ingests market related text files, indexes them with embeddings, retrieves relevant context for queries, and generates concise structured insights.  
This project is designed as a portfolio friendly example of building custom AI agents for finance.

## Key Features  
• Upload market reports, earnings summaries, news, or analyst notes  
• Convert text documents into embeddings  
• Search through information using FAISS  
• Query interface that returns structured financial answers  
• Designed to run locally with both small and large models  
• Clean FastAPI backend and minimal UI

## Architecture  
```
Documents → Embeddings → FAISS Index → Retrieval → Financial Reasoning Agent → Summary Output
```

## Architecture Diagram  
```
                   +----------------------+
                   |      Web UI          |
                   +-----------+----------+
                               |
                    Upload files and ask queries
                               |
                   +-----------+-----------+
                   |         FastAPI        |
                   +-----------+-----------+
                               |
         +---------------------+----------------------+
         |                                            |
         v                                            v
    File Ingestion                              Query Agent
   (read and clean)                          (retrieve and reason)
         |                                            |
         v                                            v
Embedding Model (MiniLM)                    LLM or fallback summary
         |                                            |
         v                                            v
     FAISS Index                             Final financial insight
```

## How to Run Locally  

### Create virtual environment  
```bash
python -m venv venv
```

### Activate it  
```bash
source venv/bin/activate
```

### Install dependencies  
```bash
pip install -U pip
pip install -r requirements.txt
```

### Start the server  
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Open the UI  
```
http://localhost:8000
```

## Example Query  
Ask something like:  
```
Summarize key risks and opportunities from the uploaded market reports.
```

## Example Output  
The system returns:  
• Relevant extracted financial text  
• Short structured summary  
• Highlights of risks and opportunities  
• Confidence score  


