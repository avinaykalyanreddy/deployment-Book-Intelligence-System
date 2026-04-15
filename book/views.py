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
def upload_book(request): # uploading new book to db using www.goodreads.com url

    url = request.data.get("url")
    if not url:

        return Response({"error":"URL is required"},status=400)

    url  = clean_url(url)
    existing_book = Book.objects.filter(book_url=url).first()

    if existing_book:
        return Response({
            "message": "Book already exists",
            "book_id": existing_book.id
        }, status=200)

    data = scrape_book(url)
    if not data["title"] or "403" in data["title"]:
        return Response({"error": "Scraping failed"}, status=500)

    book = Book.objects.create(title=data["title"],
        author=data["author"],
        rating=float(data["rating"]) if data["rating"] else None,
        description=data["description"],
        image_url=data["image_url"],
        book_url=url)
    store_book_embeddings(book)
    return Response({
        "message": "Book added successfully",
        "book_id": book.id
    })

@api_view(['POST'])
def ask_question(request): # user asks question on book it generates it response
    question = request.data.get("question")
    book_id = request.data.get("book_id")

    if not question or not book_id:
        return Response({"error": "question and book_id required"}, status=400)

    # 🔍 retrieve only that book
    results = retrieve_chunks(question, book_id)

    documents = results.get("documents", [[]])[0]

    if not documents:
        return Response({"answer": "No relevant data found"}, status=200)

    # 🧠 combine context
    context = " ".join(documents)

    # 🤖 generate answer
    answer = generate_answer(question, context)

    return Response({
        "question": question,
        "answer": answer,
        "sources": documents
    })

@api_view(['GET'])
def recommend_books(request, book_id):
    try:
        results = collection.get(
            where={"book_id": str(book_id)},
            include=["embeddings"]
        )

        embeddings = results.get("embeddings", [])

        # ✅ convert safely
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