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
