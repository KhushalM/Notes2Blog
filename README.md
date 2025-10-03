## Architecture Diagrams

### PDF Upload Pipeline

The following diagram illustrates the complete workflow of the `/pdf_upload` endpoint, from receiving a PDF file to storing it in the vector database:

```mermaid
sequenceDiagram
    participant Client
    participant FastAPI as FastAPI<br/>(main.py)
    participant PDFExtract as PDF Extract<br/>(pdf_extract.py)
    participant SemanticChunker as Semantic Chunker<br/>(chunk.py)
    participant MistralEmbed as Mistral Embeddings<br/>(mistral.py)
    participant VectorDB as Hybrid Vector DB<br/>(custom_vector_db.py)

    Client->>FastAPI: POST /pdf_upload (PDF files)
    
    alt File Already Uploaded
        FastAPI->>FastAPI: Check if filename in uploaded_files set
        FastAPI-->>Client: Return "already uploaded" message
    else File Not Uploaded
        FastAPI->>FastAPI: Save PDF to pdf_files/ directory
        
        FastAPI->>PDFExtract: extract_text_from_pdf(file_path)
        PDFExtract->>PDFExtract: Open PDF with PyMuPDF
        PDFExtract->>PDFExtract: Extract text from all pages
        PDFExtract-->>FastAPI: Return concatenated text
        
        FastAPI->>SemanticChunker: chunking(text)
        
        SemanticChunker->>SemanticChunker: sentence_chunks()<br/>Split text into sentences using regex
        Note over SemanticChunker: Regex: (?<=[.!?])\s+(?=[A-Z])
        
        SemanticChunker->>MistralEmbed: embed_documents(sentences)
        MistralEmbed->>MistralEmbed: Batch sentences (32 per batch)
        MistralEmbed->>MistralEmbed: Call Mistral API with<br/>model='mistral-embed'
        MistralEmbed-->>SemanticChunker: Return sentence embeddings
        
        SemanticChunker->>SemanticChunker: Calculate cosine similarity<br/>between consecutive sentences
        Note over SemanticChunker: similarity = dot(v1,v2) / (||v1|| * ||v2||)
        
        SemanticChunker->>SemanticChunker: Glue sentences together<br/>if similarity > 0.7 AND<br/>combined_size <= max_chunk_size
        
        SemanticChunker->>SemanticChunker: filter_chunks()<br/>Merge small chunks<br/>Split large chunks
        Note over SemanticChunker: min_chunk_size=100<br/>max_chunk_size=2000
        
        SemanticChunker-->>FastAPI: Return final chunks
        
        FastAPI->>MistralEmbed: embed_documents(chunks)
        MistralEmbed->>MistralEmbed: Batch chunks (32 per batch)
        MistralEmbed->>MistralEmbed: Call Mistral API with<br/>model='mistral-embed'
        MistralEmbed-->>FastAPI: Return chunk embeddings (vectors)
        
        FastAPI->>FastAPI: Create metadata for each chunk<br/>{filename, chunk_index,<br/>chunk_size, file_path}
        
        FastAPI->>FastAPI: Generate UUID for each chunk
        
        FastAPI->>VectorDB: add(vectors, chunks, metadatas, ids)
        
        VectorDB->>VectorDB: Normalize vectors<br/>(v / ||v||)
        
        VectorDB->>VectorDB: Extend internal storage<br/>(vectors, texts, metadata, ids)
        
        VectorDB->>VectorDB: _build_bm25_index()
        Note over VectorDB: Tokenize all texts<br/>Build word frequency map<br/>Calculate doc lengths & avg
        
        VectorDB-->>FastAPI: Storage complete
        
        FastAPI->>FastAPI: Mark filename as uploaded
        
        FastAPI-->>Client: Return success response<br/>{status, per_file_chunks,<br/>number_of_chunks, chunk_info}
    end
```

**Key Steps:**
1. **File Check**: Verify if PDF already uploaded to avoid duplicates
2. **Text Extraction**: Use PyMuPDF to extract text from all pages
3. **Sentence Splitting**: Break text into sentences using regex patterns
4. **Sentence Embeddings**: Generate embeddings for each sentence via Mistral API
5. **Cosine Similarity**: Calculate semantic similarity between consecutive sentences
6. **Semantic Gluing**: Merge similar sentences (threshold > 0.7) up to max chunk size (2000 chars)
7. **Chunk Filtering**: Ensure chunks meet size constraints (100-2000 chars)
8. **Chunk Embeddings**: Generate final embeddings for semantic chunks
9. **Metadata Creation**: Attach filename, index, size, and path to each chunk
10. **Vector DB Storage**: Normalize vectors and store in custom database
11. **BM25 Index**: Build lexical search index with tokenization and word frequencies

### Query Processing Pipeline

The following diagram shows the complete RAG query processing flow with safety checks, intelligent routing, and hallucination detection:

```mermaid
sequenceDiagram
    participant Client
    participant FastAPI as FastAPI<br/>(main.py)
    participant QueryRefusal as Query Refusal<br/>(query_refusal.py)
    participant QueryRouter as Query Router<br/>(query_router.py)
    participant MistralLLM as Mistral LLM<br/>(mistral.py)
    participant MistralEmbed as Mistral Embeddings<br/>(mistral.py)
    participant VectorDB as Hybrid Vector DB<br/>(custom_vector_db.py)
    participant Reranker as LLM Reranker<br/>(rerank.py)
    participant HallucinationCheck as Hallucination Check<br/>(hallucination_check.py)

    Client->>FastAPI: POST /query_processing<br/>{query, session_id, retrieval_mode}
    
    FastAPI->>FastAPI: Initialize chat_memories[session_id]<br/>if not exists
    
    alt No Vector DB
        FastAPI->>FastAPI: Check if vector_db.vectors empty
        FastAPI-->>Client: Error: "No VectorDB initialized,<br/>please upload at least one PDF"
    else Vector DB Exists
        FastAPI->>QueryRefusal: should_refuse_query(query)
        QueryRefusal->>QueryRefusal: Check for PII patterns<br/>(SSN, credit cards, emails, etc.)
        QueryRefusal->>QueryRefusal: Check for legal/medical keywords
        
        alt PII Detected
            QueryRefusal-->>FastAPI: action="REFUSE"
            FastAPI-->>Client: Refuse with message
        else Legal/Medical Query
            QueryRefusal-->>FastAPI: action="DISCLAIMER", message
            FastAPI->>FastAPI: Store disclaimer for later
        else Safe Query
            QueryRefusal-->>FastAPI: action="ALLOW"
        end
        
        FastAPI->>QueryRouter: analyze_and_transform(query, history)
        QueryRouter->>QueryRouter: Detect if KB retrieval needed<br/>(factual vs conversational)
        QueryRouter->>QueryRouter: Transform query with context<br/>& output format hints
        QueryRouter-->>FastAPI: (need_retrieval, transformed_query)
        
        alt No Retrieval Needed
            FastAPI->>MistralLLM: generate_response(query)
            Note over MistralLLM: Model: mistral-small-2503
            MistralLLM-->>FastAPI: Direct answer
            FastAPI->>FastAPI: Prepend disclaimer if needed
            FastAPI->>FastAPI: Add to chat_memories[session_id]
            FastAPI-->>Client: {answer, sources=[], processing_time}
            
        else Retrieval Required
            FastAPI->>FastAPI: Use transformed_query for retrieval
            
            FastAPI->>MistralEmbed: embed_query(transformed_query)
            MistralEmbed->>MistralEmbed: Call Mistral API<br/>model='mistral-embed'
            MistralEmbed-->>FastAPI: query_vector
            
            alt Hybrid Search (65% semantic + 35% lexical)
                FastAPI->>VectorDB: hybrid_search(query, query_vector)
                VectorDB->>VectorDB: semantic_search(query_vector)<br/>Cosine similarity with normalized vectors
                VectorDB->>VectorDB: lexical_search(query)<br/>BM25 scoring
                VectorDB->>VectorDB: Combine scores with weights<br/>Filter by threshold (0.5)
                Note over VectorDB: combined_score = 0.65*semantic + 0.35*lexical<br/>Return top-k if >= 0.5 threshold
            else Semantic Only
                FastAPI->>VectorDB: semantic_search(query_vector)
            else Lexical Only  
                FastAPI->>VectorDB: lexical_search(query)
            end
            
            alt No Results or Below Threshold
                VectorDB-->>FastAPI: Empty results
                FastAPI->>FastAPI: Prepend disclaimer if needed
                FastAPI-->>Client: "Insufficient evidence:<br/>Not enough reliable information<br/>to answer confidently"
                
            else Valid Results
                VectorDB-->>FastAPI: Retrieved documents
                
                FastAPI->>Reranker: rerank(query, results)
                Reranker->>Reranker: Use LLM to score relevance<br/>of each document to query
                Reranker-->>FastAPI: Reranked top documents
                
                FastAPI->>MistralLLM: create_rag_prompt(query, reranked_results)
                FastAPI->>MistralLLM: generate_response(prompt, temp, max_tokens)
                Note over MistralLLM: Model: mistral-large-latest<br/>Context: Retrieved documents + query
                MistralLLM-->>FastAPI: Generated answer
                
                FastAPI->>HallucinationCheck: check_hallucination(query, answer, sources)
                HallucinationCheck->>HallucinationCheck: Extract claims from answer
                HallucinationCheck->>HallucinationCheck: Verify each claim against sources
                HallucinationCheck-->>FastAPI: (unverified_claims, report)
                
                FastAPI->>FastAPI: Prepend disclaimer if needed
                FastAPI->>FastAPI: Add to chat_memories[session_id]
                FastAPI-->>Client: {answer, sources, unverified_claims,<br/>processing_time}
            end
        end
    end
```

**Key Steps:**
1. **Session Init**: Create or retrieve chat memory for session_id
2. **Vector DB Check**: Ensure at least one PDF uploaded
3. **Safety Check**: Refuse PII queries, add disclaimers for legal/medical
4. **Query Analysis**: Determine if KB search needed + transform query with context
5. **Direct Answer**: Use Mistral LLM (mistral-small-2503) for conversational queries
6. **Query Embedding**: Generate vector representation for retrieval queries
7. **Hybrid Search**: Combine semantic (65%) + BM25 (35%), filter by 0.5 threshold
8. **Insufficient Evidence**: Refuse to answer if no results meet threshold
9. **Reranking**: LLM-based reranking of retrieved documents
10. **Answer Generation**: Create RAG prompt with sources, generate with mistral-large-latest
11. **Hallucination Check**: Verify claims against retrieved context
12. **Response**: Return answer with sources and unverified claims report
