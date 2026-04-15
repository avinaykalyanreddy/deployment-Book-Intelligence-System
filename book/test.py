from sentence_transformers import SentenceTransformer
import chromadb
import google.generativeai as genai
genai.configure(api_key="AIzaSyAkreKsYfCTvbVb3SsSDucJghlB8XUyPVo")

model = SentenceTransformer("all-MiniLM-L6-v2")

client = chromadb.Client()

collection = client.get_or_create_collection("books")

def chunk_text(text, size=200, overlap=50):
    words = text.split()
    chunks = []
    step = size - overlap

    for i in range(0, len(words), step):
        chunk = " ".join(words[i:i+size])
        chunks.append(chunk)

    return chunks

def store_book_embeddings(book):
    chunks = chunk_text(book.description)

    for i, chunk in enumerate(chunks):
        embedding = model.encode(chunk).tolist()

        collection.add(
            documents=[chunk],
            embeddings=[embedding],
            ids=[f"{book.id}_{i}"],
            metadatas=[{"book_id": str(book.id)}]  # 🔥 IMPORTANT
        )


def retrieve_chunks(question, book_id):
    query_embedding = model.encode(question).tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=3,
        where={"book_id": str(book_id)}  # 🔥 FILTER
    )

    return results

def generate_answer(question, context):
    models = ["gemini-2.5-flash", "gemini-2.5-pro", "gemini-flash-latest", "gemini-2.5-flash-lite",
              "gemini-pro-latest", "gemini-2.0-flash",
              "gemini-2.0-flash-001", "gemini-2.0-flash-lite", "gemini-2.0-flash-lite-001",
              "gemini-3-flash-preview", "gemini-3-pro-preview",
              "gemini-3-pro-preview", "gemini-3.1-pro-preview", "gemini-3.1-flash-lite-preview",
              "gemma-3-27b-it", "gemma-3-12b-it", "gemma-3-12b-it",
              "gemma-3-4b-it", "gemma-3-1b-it"]
    print(question,context)
    for m in models:

        model = genai.GenerativeModel(m)

        try:
            prompt = f"""
                You are a helpful AI assistant.

                Answer ONLY using the context below.
                If answer is not present, say "Not found in document".

                Context:
                {context}

                Question:
                {question}
                """

            response = model.generate_content(prompt)

            return response.text

        except Exception as e:
            print(f"Model {m} failed:", e)
            continue

    return "something went wrong"


