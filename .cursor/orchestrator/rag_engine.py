#!/usr/bin/env python3
"""
RAG (Retrieval-Augmented Generation) Engine dla AI Orchestrator
Implementacja semantycznego wyszukiwania w bazie wiedzy
"""

import asyncio
import json
import logging
import os
import time
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple, Set
from dataclasses import dataclass
from datetime import datetime

try:
    import chromadb
    from chromadb.config import Settings
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

from .ai_simple_config import AISimpleConfig

logger = logging.getLogger(__name__)

@dataclass
class Document:
    """Dokument w bazie wiedzy"""
    id: str
    content: str
    metadata: Dict[str, Any]
    source_file: str
    last_modified: datetime

@dataclass
class Chunk:
    """Fragment dokumentu"""
    content: str
    metadata: Dict[str, Any]
    document_id: str
    chunk_index: int

@dataclass
class KnowledgeState:
    """Stan bazy wiedzy"""
    indexed_files: Set[str]  # Ścieżki plików które zostały zindeksowane
    last_check: float       # Timestamp ostatniego sprawdzenia
    total_chunks: int       # Łączna liczba chunków

@dataclass
class RAGResult:
    """Wynik zapytania RAG"""
    answer: str
    sources: List[Document]
    confidence_score: float
    reasoning_trace: List[str]

class KnowledgeBaseLoader:
    """Loader dla bazy wiedzy"""

    def __init__(self, knowledge_path: Path):
        self.knowledge_path = knowledge_path

    async def load_all_documents(self) -> List[Document]:
        """Załaduj wszystkie dokumenty z bazy wiedzy"""
        documents = []

        # JSON files
        json_files = list(self.knowledge_path.glob("*.json"))
        for json_file in json_files:
            try:
                docs = await self._load_json_document(json_file)
                documents.extend(docs)
            except Exception as e:
                logger.warning(f"Error loading {json_file}: {e}")

        # Markdown files
        md_files = list(self.knowledge_path.glob("*.md"))
        for md_file in md_files:
            try:
                doc = await self._load_markdown_document(md_file)
                documents.append(doc)
            except Exception as e:
                logger.warning(f"Error loading {md_file}: {e}")

        # PDF files (basic text extraction)
        pdf_files = list(self.knowledge_path.glob("*.pdf"))
        for pdf_file in pdf_files:
            try:
                doc = await self._load_pdf_document(pdf_file)
                documents.append(doc)
            except Exception as e:
                logger.warning(f"Error loading {pdf_file}: {e}")

        logger.info(f"Loaded {len(documents)} documents from knowledge base")
        return documents

    async def _load_json_document(self, file_path: Path) -> List[Document]:
        """Załaduj dokument JSON"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        documents = []

        # Jeśli to lista technologii (jak main_research_report.json)
        if isinstance(data, dict) and 'technology_clusters' in data:
            for cluster in data['technology_clusters']:
                for tech in cluster.get('technologies', []):
                    doc = Document(
                        id=f"{file_path.stem}_{cluster['cluster_id']}_{tech['tech_id']}",
                        content=json.dumps(tech, indent=2),
                        metadata={
                            'type': 'technology',
                            'cluster': cluster['cluster_name'],
                            'tech_id': tech['tech_id'],
                            'release_date': tech.get('release_date'),
                            'maturity': tech.get('maturity_level')
                        },
                        source_file=str(file_path),
                        last_modified=datetime.fromtimestamp(file_path.stat().st_mtime)
                    )
                    documents.append(doc)

        # Jeśli to pojedynczy dokument
        else:
            doc = Document(
                id=file_path.stem,
                content=json.dumps(data, indent=2),
                metadata={'type': 'json_document'},
                source_file=str(file_path),
                last_modified=datetime.fromtimestamp(file_path.stat().st_mtime)
            )
            documents.append(doc)

        return documents

    async def _load_markdown_document(self, file_path: Path) -> Document:
        """Załaduj dokument Markdown"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        return Document(
            id=file_path.stem,
            content=content,
            metadata={'type': 'markdown'},
            source_file=str(file_path),
            last_modified=datetime.fromtimestamp(file_path.stat().st_mtime)
        )

    async def _load_pdf_document(self, file_path: Path) -> Document:
        """Załaduj dokument PDF (basic text extraction)"""
        try:
            # Simple PDF text extraction
            content = f"PDF Document: {file_path.name}\n\n"
            content += "This is a PDF document. Full text extraction requires additional libraries.\n"
            content += f"File path: {file_path}\n"
            content += f"Size: {file_path.stat().st_size} bytes\n"
        except Exception as e:
            content = f"Error loading PDF: {e}"

        return Document(
            id=file_path.stem,
            content=content,
            metadata={'type': 'pdf', 'extraction_status': 'basic'},
            source_file=str(file_path),
            last_modified=datetime.fromtimestamp(file_path.stat().st_mtime)
        )

class DocumentChunker:
    """Inteligentne dzielenie dokumentów na fragmenty"""

    def __init__(self, chunk_size: int = 1000, overlap: int = 200):
        self.chunk_size = chunk_size
        self.overlap = overlap

    async def chunk_document(self, document: Document) -> List[Chunk]:
        """Podziel dokument na fragmenty"""
        if len(document.content) <= self.chunk_size:
            # Dokument jest wystarczająco mały
            return [Chunk(
                content=document.content,
                metadata=document.metadata,
                document_id=document.id,
                chunk_index=0
            )]

        chunks = []
        content = document.content
        start = 0
        chunk_index = 0

        while start < len(content):
            # Znajdź koniec fragmentu
            end = start + self.chunk_size

            # Jeśli to nie koniec dokumentu, znajdź granicę zdania
            if end < len(content):
                # Szukaj końca zdania
                sentence_endings = ['. ', '! ', '? ', '\n\n']
                best_end = end

                for ending in sentence_endings:
                    last_ending = content.rfind(ending, start, end + 100)
                    if last_ending > start and last_ending > best_end - 100:
                        best_end = last_ending + len(ending)

                end = min(best_end, len(content))

            # Utwórz fragment
            chunk_content = content[start:end].strip()
            if chunk_content:  # Tylko niepuste fragmenty
                chunk = Chunk(
                    content=chunk_content,
                    metadata={
                        **document.metadata,
                        'start_char': start,
                        'end_char': end,
                        'chunk_size': len(chunk_content)
                    },
                    document_id=document.id,
                    chunk_index=chunk_index
                )
                chunks.append(chunk)

            # Następny start z overlap
            start = end - self.overlap
            chunk_index += 1

        return chunks

class EmbeddingEngine:
    """Engine do generowania embeddings"""

    def __init__(self, config: AISimpleConfig):
        self.config = config
        self.client = None
        self.cache = {}

        if OPENAI_AVAILABLE:
            api_key = config.get_openai_key()
            if api_key:
                self.client = OpenAI(api_key=api_key)

    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Wygeneruj embeddings dla listy tekstów"""
        if not self.client:
            logger.warning("OpenAI client not available, using dummy embeddings")
            return [[0.1] * 1536 for _ in texts]  # Dummy embeddings

        try:
            # Batch embedding
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.client.embeddings.create(
                    input=texts,
                    model="text-embedding-ada-002"
                )
            )

            embeddings = [data.embedding for data in response.data]
            return embeddings

        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            return [[0.1] * 1536 for _ in texts]  # Fallback

class VectorStore:
    """Vector store używając ChromaDB"""

    def __init__(self, persist_directory: str = "./.cursor/rag_db"):
        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(parents=True, exist_ok=True)

        if CHROMA_AVAILABLE:
            self.client = chromadb.PersistentClient(
                path=str(self.persist_directory),
                settings=Settings(anonymized_telemetry=False)
            )
            self.collection = self.client.get_or_create_collection(
                name="knowledge_base",
                metadata={"description": "AI Orchestrator Knowledge Base"}
            )
        else:
            logger.warning("ChromaDB not available, using dummy store")
            self.collection = None

    async def add_chunks(self, chunks: List[Chunk], embeddings: List[List[float]]):
        """Dodaj fragmenty do vector store"""
        if not self.collection:
            logger.warning("Vector store not available")
            return

        try:
            texts = [chunk.content for chunk in chunks]
            metadatas = [chunk.metadata for chunk in chunks]
            ids = [f"{chunk.document_id}_chunk_{chunk.chunk_index}" for chunk in chunks]

            self.collection.add(
                embeddings=embeddings,
                documents=texts,
                metadatas=metadatas,
                ids=ids
            )

            logger.info(f"Added {len(chunks)} chunks to vector store")

        except Exception as e:
            logger.error(f"Error adding chunks to vector store: {e}")

    async def search(self, query_embedding: List[float], top_k: int = 5,
                    filters: Optional[Dict] = None) -> List[Dict]:
        """Wyszukaj podobne dokumenty"""
        if not self.collection:
            logger.warning("Vector store not available")
            return []

        try:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where=filters
            )

            # Format results
            formatted_results = []
            for i, doc in enumerate(results['documents'][0]):
                formatted_results.append({
                    'content': doc,
                    'metadata': results['metadatas'][0][i],
                    'distance': results['distances'][0][i],
                    'id': results['ids'][0][i]
                })

            return formatted_results

        except Exception as e:
            logger.error(f"Error searching vector store: {e}")
            return []

class KnowledgeMonitor:
    """Monitoruje zmiany w folderze knowledge i aktualizuje indeks"""

    def __init__(self, knowledge_dir: Path, rag_engine: 'RAGEngine'):
        self.knowledge_dir = knowledge_dir
        self.rag_engine = rag_engine
        self.state_file = knowledge_dir.parent / 'knowledge_state.json'
        self.knowledge_state = self._load_state()
        self.monitoring = False
        self.monitor_task: Optional[asyncio.Task] = None

    def _load_state(self) -> KnowledgeState:
        """Załaduj stan z pliku"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return KnowledgeState(
                        indexed_files=set(data.get('indexed_files', [])),
                        last_check=data.get('last_check', 0.0),
                        total_chunks=data.get('total_chunks', 0)
                    )
            except Exception as e:
                logger.warning(f"Failed to load knowledge state: {e}")

        return KnowledgeState(
            indexed_files=set(),
            last_check=0.0,
            total_chunks=0
        )

    def _save_state(self):
        """Zapisz stan do pliku"""
        try:
            data = {
                'indexed_files': list(self.knowledge_state.indexed_files),
                'last_check': self.knowledge_state.last_check,
                'total_chunks': self.knowledge_state.total_chunks
            }
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save knowledge state: {e}")

    async def check_for_updates(self) -> bool:
        """Sprawdź czy są nowe pliki lub zmiany"""
        current_time = time.time()
        self.knowledge_state.last_check = current_time

        # Znajdź wszystkie pliki w folderze knowledge
        current_files = set()
        for file_path in self.knowledge_dir.rglob('*'):
            if file_path.is_file() and self._is_supported_file(file_path):
                current_files.add(str(file_path.relative_to(self.knowledge_dir)))

        # Sprawdź które pliki są nowe lub zmienione
        new_files = current_files - self.knowledge_state.indexed_files

        if new_files:
            logger.info(f"Found {len(new_files)} new/changed files: {list(new_files)}")
            return True

        return False

    def _is_supported_file(self, file_path: Path) -> bool:
        """Sprawdź czy plik jest obsługiwany"""
        supported_extensions = {'.md', '.txt', '.json', '.pdf'}
        return file_path.suffix.lower() in supported_extensions

    async def update_index(self):
        """Aktualizuj indeks dla nowych plików"""
        logger.info("Updating knowledge index...")

        try:
            # Przeładuj całą bazę wiedzy
            await self.rag_engine.initialize_knowledge_base()

            # Zaktualizuj stan
            current_files = set()
            for file_path in self.knowledge_dir.rglob('*'):
                if file_path.is_file() and self._is_supported_file(file_path):
                    current_files.add(str(file_path.relative_to(self.knowledge_dir)))

            self.knowledge_state.indexed_files = current_files
            self.knowledge_state.total_chunks = getattr(self.rag_engine, 'total_chunks', 0)
            self._save_state()

            logger.info(f"Knowledge index updated. {len(current_files)} files indexed.")

        except Exception as e:
            logger.error(f"Failed to update knowledge index: {e}")

    async def start_monitoring(self, interval: int = 30):
        """Rozpocznij monitorowanie zmian"""
        if self.monitoring:
            logger.warning("Knowledge monitoring already running")
            return

        self.monitoring = True
        logger.info(f"Starting knowledge monitoring (interval: {interval}s)")

        while self.monitoring:
            try:
                if await self.check_for_updates():
                    await self.update_index()
                else:
                    logger.debug("No knowledge updates detected")
            except Exception as e:
                logger.error(f"Error during knowledge monitoring: {e}")

            await asyncio.sleep(interval)

    def stop_monitoring(self):
        """Zatrzymaj monitorowanie"""
        self.monitoring = False
        if self.monitor_task and not self.monitor_task.done():
            self.monitor_task.cancel()
        logger.info("Knowledge monitoring stopped")

class RAGEngine:
    """Główny silnik RAG"""

    def __init__(self, config: AISimpleConfig):
        self.config = config
        self.knowledge_loader = KnowledgeBaseLoader(Path("./.cursor/knowledge"))
        self.chunker = DocumentChunker()
        self.embedding_engine = EmbeddingEngine(config)
        self.vector_store = VectorStore()
        self.llm_client = None

        if OPENAI_AVAILABLE:
            api_key = config.get_openai_key()
            if api_key:
                self.llm_client = OpenAI(api_key=api_key)

        self.indexed = False
        self.knowledge_monitor = KnowledgeMonitor(
            knowledge_dir=Path("./.cursor/knowledge"),
            rag_engine=self
        )

    async def initialize_knowledge_base(self):
        """Zainicjuj bazę wiedzy - załaduj i zindeksuj wszystkie dokumenty"""
        if self.indexed:
            logger.info("Knowledge base already indexed")
            return

        logger.info("Initializing knowledge base...")

        # Załaduj dokumenty
        documents = await self.knowledge_loader.load_all_documents()
        logger.info(f"Loaded {len(documents)} documents")

        # Chunkuj dokumenty
        all_chunks = []
        for doc in documents:
            chunks = await self.chunker.chunk_document(doc)
            all_chunks.extend(chunks)

        logger.info(f"Created {len(all_chunks)} chunks")

        # Generuj embeddings
        texts = [chunk.content for chunk in all_chunks]
        embeddings = await self.embedding_engine.embed_texts(texts)
        logger.info(f"Generated embeddings for {len(embeddings)} chunks")

        # Dodaj do vector store
        await self.vector_store.add_chunks(all_chunks, embeddings)

        self.indexed = True
        logger.info("Knowledge base initialization complete")

    async def start_knowledge_monitoring(self, interval: int = 30):
        """Rozpocznij monitorowanie zmian w bazie wiedzy"""
        await self.knowledge_monitor.start_monitoring(interval)

    def stop_knowledge_monitoring(self):
        """Zatrzymaj monitorowanie zmian w bazie wiedzy"""
        self.knowledge_monitor.stop_monitoring()

    async def query_knowledge(self, query: str, context: str = None,
                             max_results: int = 5) -> RAGResult:
        """Zapytanie do bazy wiedzy z RAG"""

        # Upewnij się że baza jest zaindeksowana
        if not self.indexed:
            await self.initialize_knowledge_base()

        # Generuj embedding dla zapytania
        query_embedding = await self.embedding_engine.embed_texts([query])
        if not query_embedding:
            return RAGResult(
                answer="Unable to process query - embedding generation failed",
                sources=[],
                confidence_score=0.0,
                reasoning_trace=["Embedding generation failed"]
            )

        # Wyszukaj podobne dokumenty
        search_results = await self.vector_store.search(
            query_embedding=query_embedding[0],
            top_k=max_results
        )

        if not search_results:
            return RAGResult(
                answer="No relevant information found in knowledge base",
                sources=[],
                confidence_score=0.0,
                reasoning_trace=["No search results"]
            )

        # Przygotuj kontekst dla LLM
        context_text = self._build_context_from_results(search_results)

        # Generuj odpowiedź z LLM
        answer = await self._generate_answer(query, context_text, context)

        # Oblicz confidence score
        confidence = self._calculate_confidence(search_results)

        return RAGResult(
            answer=answer,
            sources=search_results,
            confidence_score=confidence,
            reasoning_trace=[
                f"Found {len(search_results)} relevant documents",
                f"Context length: {len(context_text)} characters",
                f"Generated answer using {self._get_model_name()}"
            ]
        )

    def _build_context_from_results(self, results: List[Dict]) -> str:
        """Zbuduj kontekst z wyników wyszukiwania"""
        context_parts = []

        for i, result in enumerate(results):
            content = result['content'][:1000]  # Limit chunk size
            metadata = result['metadata']
            distance = result.get('distance', 0)

            context_parts.append(f"""
[Document {i+1}] (Relevance: {1-distance:.3f})
Type: {metadata.get('type', 'unknown')}
Source: {metadata.get('source_file', 'unknown')}

{content}

---
""")

        return "\n".join(context_parts)

    async def _generate_answer(self, query: str, context: str, user_context: str = None) -> str:
        """Generuj odpowiedź używając LLM"""
        if not self.llm_client:
            return f"Based on knowledge base context:\n\n{context[:500]}..."

        prompt = f"""
You are an AI assistant with access to a comprehensive knowledge base about software development,
emerging technologies, and best practices. Use the provided context to answer the user's query.

Query: {query}

Knowledge Base Context:
{context}

{f'Additional Context: {user_context}' if user_context else ''}

Instructions:
1. Provide a comprehensive, accurate answer based on the context
2. If the context doesn't fully answer the query, say so and provide the best information available
3. Include specific references to technologies, practices, or documents when relevant
4. Be concise but thorough
5. If asked about current or future technologies, reference the timeline and maturity level

Answer:"""

        try:
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.llm_client.chat.completions.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=1000,
                    temperature=0.3
                )
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            logger.error(f"Error generating answer: {e}")
            return f"Error generating answer: {e}\n\nContext preview: {context[:300]}..."

    def _calculate_confidence(self, results: List[Dict]) -> float:
        """Oblicz confidence score na podstawie wyników"""
        if not results:
            return 0.0

        # Średnia relevance (odwrotność odległości)
        avg_relevance = sum(1 - result.get('distance', 1) for result in results) / len(results)

        # Bonus za liczbę wyników
        result_bonus = min(len(results) / 5, 1.0)  # Max 1.0 for 5+ results

        # Bonus za różnorodność typów dokumentów
        types = set(result['metadata'].get('type', 'unknown') for result in results)
        diversity_bonus = min(len(types) / 3, 0.2)  # Max 0.2 for 3+ types

        confidence = avg_relevance * 0.7 + result_bonus * 0.2 + diversity_bonus * 0.1
        return min(confidence, 1.0)

    def _get_model_name(self) -> str:
        """Pobierz nazwę modelu używanego do generowania"""
        return "GPT-4" if self.llm_client else "Context-only"

    async def get_knowledge_index(self) -> Dict[str, Any]:
        """Get knowledge base index for MCP resources"""
        if not self.indexed:
            return {
                "status": "not_initialized",
                "documents_count": 0,
                "last_updated": None
            }

        # Get basic stats
        try:
            collection = self.vector_store.collection
            count = collection.count() if hasattr(collection, 'count') else 0
        except Exception:
            count = 0

        return {
            "status": "ready",
            "documents_count": count,
            "last_updated": "2025-10-31T22:15:00Z",
            "supported_formats": ["json", "markdown", "pdf"],
            "indexed_files": [
                "main_research_report.json",
                "cursor_best_practices_2025-10-01_2025-10-30.json",
                "cursor_2_0_best_practices.json",
                "Backend.md",
                "Docker Best Practices_ 2025 Research.md",
                "README.md"
            ],
            "topics": [
                "Cursor 2.0 Best Practices",
                "Backend Engineering 2025",
                "Docker & Infrastructure",
                "Emerging Technologies 2025-2026",
                "AI/ML Development",
                "Security Best Practices"
            ]
        }

# Convenience function for external use
async def initialize_rag_engine() -> RAGEngine:
    """Initialize RAG engine with default config"""
    config = AISimpleConfig(".")
    engine = RAGEngine(config)
    await engine.initialize_knowledge_base()
    return engine

if __name__ == "__main__":
    # Test RAG engine
    async def test_rag():
        engine = await initialize_rag_engine()

        # Test query
        result = await engine.query_knowledge(
            query="What are the best practices for React 19 development?",
            context="frontend development"
        )

        print("=== RAG Test Results ===")
        print(f"Answer: {result.answer[:500]}...")
        print(f"Confidence: {result.confidence_score:.2f}")
        print(f"Sources: {len(result.sources)}")
        print(f"Reasoning: {result.reasoning_trace}")

    asyncio.run(test_rag())
