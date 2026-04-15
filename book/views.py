from django.shortcuts import render
from rest_framework.response import Response
from .models import Book
from .serializers import BookSerializer
from rest_framework.decorators import api_view
from .scraper import scrape_book
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .rag import retrieve_chunks, generate_answer,store_book_embeddings,collection
import numpy as np
from django.db.models import Case, When


@api_view(['GET'])
def get_books(request): # this view used for retrieving all books from db

    books = Book.objects.all()
    serializer = BookSerializer(books,many=True)
    print(type(serializer.data))
    return Response(serializer.data)

def clean_url(url): # removing all url parameters so that each book should be unique
    return url.split("?")[0] if url else url



@api_view(["POST"])
def upload_book(request):
    url = request.data.get("url")

    if not url:
        return Response({"error": "URL is required"}, status=400)

    url = clean_url(url)

    # ✅ Check if already exists
    existing_book = Book.objects.filter(book_url=url).first()
    if existing_book:
        return Response({
            "message": "Book already exists",
            "book_id": existing_book.id
        }, status=200)

    # ✅ Scrape book
    try:
        data = scrape_book(url)
    except Exception as e:
        return Response({"error": f"Scraping failed: {str(e)}"}, status=500)

    if not data or not data.get("title"):
        return Response({"error": "Failed to fetch book data"}, status=500)

    # ✅ Safe rating conversion
    rating = None
    if data.get("rating"):
        try:
            rating = float(data["rating"])
        except ValueError:
            rating = None

    # ✅ Save book
    book = Book.objects.create(
        title=data.get("title"),
        author=data.get("author"),
        rating=rating,
        description=data.get("description"),
        image_url=data.get("image_url"),
        book_url=url
    )

    # ✅ Store embeddings (can move to background later)
    try:
        store_book_embeddings(book)
    except Exception as e:
        print("Embedding error:", e)

    return Response({
        "message": "Book added successfully",
        "book_id": book.id
    }, status=201)
@api_view(['POST'])
def ask_question(request):
    question = request.data.get("question")
    book_id = request.data.get("book_id")

    if not question or not book_id:
        return Response({"error": "question and book_id required"}, status=400)

    try:
        #1. Get book from DB (IMPORTANT)
        book = Book.objects.get(id=book_id)

        #2. Retrieve relevant chunks
        results = retrieve_chunks(question, book_id)

        documents = results.get("documents", [[]])[0]

        #If no chunks found
        if not documents:
            # fallback using DB only
            context = f"""
            Title: {book.title}
            Author: {book.author}
            Rating: {book.rating}
            Description: {book.description}
            """
        else:
            #  Combine DB + RAG context
            context = f"""
            Title: {book.title}
            Author: {book.author}
            Rating: {book.rating}
            """ + " ".join(documents)

        # Generate answer
        answer = generate_answer(question, context)

        return Response({
            "question": question,
            "answer": answer,
            "sources": documents if documents else [],
            "book": {
                "title": book.title,
                "author": book.author,
                "rating": book.rating
            }
        })

    except Book.DoesNotExist:
        return Response({"error": "Book not found"}, status=404)

    except Exception as e:
        print("Error:", str(e))
        return Response({"error": "Something went wrong"}, status=500)
@api_view(['GET'])
def recommend_books(request, book_id):
    try:
        results = collection.get(
            where={"book_id": str(book_id)},
            include=["embeddings"]
        )

        embeddings = results.get("embeddings", [])

        #convert safely
        embeddings = np.array(embeddings)

        if embeddings.size == 0:
            return Response({"count": 0, "data": []})

        # 🔥 fix shape issue
        if len(embeddings.shape) == 3:
            embeddings = embeddings.reshape(-1, embeddings.shape[-1])

        embeddings = embeddings[:5]

        query_embedding = np.mean(embeddings, axis=0).tolist()

        similar = collection.query(
            query_embeddings=[query_embedding],
            n_results=10,
            include=["metadatas", "distances"]
        )

        metadatas = similar.get("metadatas", [[]])[0]
        distances = similar.get("distances", [[]])[0]

        book_ids_with_dist = []
        seen = set()

        for meta, dist in zip(metadatas, distances):
            bid = meta.get("book_id")

            if bid and bid != str(book_id) and bid not in seen:
                seen.add(bid)
                book_ids_with_dist.append((int(bid), dist))

        # sort by similarity
        book_ids_with_dist.sort(key=lambda x: x[1])

        top_ids = [bid for bid, _ in book_ids_with_dist[:5]]

        if not top_ids:
            return Response({"count": 0, "data": []})

        # preserve order
        preserved_order = Case(
            *[When(id=pk, then=pos) for pos, pk in enumerate(top_ids)]
        )

        books = Book.objects.filter(id__in=top_ids).order_by(preserved_order)

        data = [
            {
                "id": b.id,
                "title": b.title,
                "author": b.author,
                "image_url": b.image_url,
            }
            for b in books
        ]

        return Response({
            "count": len(data),
            "data": data
        })

    except Exception as e:
        print("Recommendation Error:", str(e))
        return Response({
            "error": str(e),
            "data": []
        })