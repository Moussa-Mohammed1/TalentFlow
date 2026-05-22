from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import re
import numpy as np 

class ChunkService:

    def __init__(self):
        self.model = SentenceTransformer(
            "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
        )
        self.similarity_threshold = 0.65

    # split the extracted text into chunks 
    def split_lines(self, text:str) -> list[str]:

        if not text or not text.strip():
            return []

        paragraphs = [
            paragraph.strip()
            for paragraph in re.split(r"\n\s*\n+", text.strip())
            if paragraph.strip()
        ]

        chunks = []
        for paragraph in paragraphs:
            sentences = [
                sentence.strip()
                for sentence in re.split(r"(?<=[.!?])\s+", paragraph)
                if sentence.strip()
            ]

            if len(sentences) > 1:
                chunks.extend(sentences)
            else:
                lines = [
                    line.strip()
                    for line in paragraph.split("\n")
                    if len(line.strip()) > 5
                ]
                chunks.extend(lines or [paragraph])

        return [chunk for chunk in chunks if len(chunk.strip()) > 5]
    
    # generate embeddings for the text chunks 
    def generate_embeddings(self, chunks: list[str]) -> np.ndarray:

        if not chunks:
            return np.empty((0, 0))
        
        embeddings = self.model.encode(chunks)
        return embeddings
    
    # merge semantically similar consecutive chunks 
    def semantic_chunking(self, chunks: list[str], embeddings: np.ndarray) -> list[str]:
        if not chunks:
            return []

        semantic_chunks = []
        
        current_chunk = chunks[0]
        
        for i in range(1, len(chunks)):
            previous_embedding = embeddings[i - 1].reshape(1, -1)
            current_embedding = embeddings[i].reshape(1, -1)
            
            similarity = cosine_similarity(
                previous_embedding, 
                current_embedding
            )[0][0]
            
            if similarity >= self.similarity_threshold:
                current_chunk += " " + chunks[i]
            else:
                semantic_chunks.append(current_chunk)
                current_chunk = chunks[i]
        semantic_chunks.append(current_chunk)
        return semantic_chunks
    
    def process(self, text:str) -> list[dict]:
        chunks = self.split_lines(text)
        if not chunks:
            return []

        embeddings = self.generate_embeddings(chunks)
        
        semantic_chunks = self.semantic_chunking(chunks, embeddings)
        if not semantic_chunks:
            return []

        semantic_embeddings = self.generate_embeddings(semantic_chunks)
        
        results = []
        
        for chunk, embedding in zip(semantic_chunks, semantic_embeddings):
            results.append({
                "text": chunk, 
                "embeddings": embedding.tolist()
            })
        return results
    