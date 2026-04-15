import { useEffect, useState } from "react";
import API from "../api";
import { useNavigate } from "react-router-dom";

export default function Dashboard() {
  const [books, setBooks] = useState([]);
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");

  const navigate = useNavigate();

  useEffect(() => {
    fetchBooks();
  }, []);

  const fetchBooks = async () => {
    const res = await API.get("/books/");
    setBooks(res.data);
  };

  const handleUpload = async () => {
    if (!url) return;

    setLoading(true);
    setMessage("📚 Scraping your book... Please wait");

    try {
      await API.post("/upload/", { url });

      setMessage("✅ Book added successfully!");
      setUrl("");
      fetchBooks();
    } catch (err) {
      setMessage("❌ Failed to scrape book");
    }

    setLoading(false);

    // auto clear message
    setTimeout(() => setMessage(""), 3000);
  };

  return (
    <div className="min-h-screen bg-gray-100">

      {/* HEADER */}
      <div className="bg-white shadow-md py-4 px-6 flex justify-between items-center">
        <h1 className="text-2xl font-bold text-blue-600">AI Librarian – Book Intelligence System</h1>
      </div>

      {/* MAIN CONTAINER */}
      <div className="max-w-6xl mx-auto px-4 py-6">

        {/* ADD BOOK */}
        <div className="bg-white rounded-xl shadow-md p-5 mb-6">
          <h2 className="text-lg font-semibold mb-3">Add Book</h2>

          <div className="flex flex-col sm:flex-row gap-3">
            <input
              className="flex-1 border rounded-lg p-2 focus:ring-2 focus:ring-blue-400 outline-none"
              placeholder="Paste book URL..."
              value={url}
              onChange={(e) => setUrl(e.target.value)}
            />

            <button
              onClick={handleUpload}
              disabled={loading}
              className={`px-5 py-2 rounded-lg text-white transition ${
                loading
                  ? "bg-gray-400 cursor-not-allowed"
                  : "bg-blue-500 hover:bg-blue-600"
              }`}
            >
              {loading ? "Scraping..." : "Add Book"}
            </button>
          </div>

          {/* 🔥 MESSAGE */}
          {message && (
            <p className="mt-3 text-sm text-blue-600">{message}</p>
          )}

          {/* 🔥 SPINNER */}
          {loading && (
            <div className="flex items-center gap-2 mt-2">
              <div className="w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
              <span className="text-sm text-gray-600">
                Fetching book details...
              </span>
            </div>
          )}
        </div>

        {/* BOOK GRID */}
        <div className="grid gap-6 
                        grid-cols-1 
                        sm:grid-cols-2 
                        md:grid-cols-3 
                        lg:grid-cols-4">

          {books.map((book) => (
            <div
              key={book.id}
              onClick={() => navigate(`/book/${book.id}`)}
              className="bg-white rounded-xl shadow-md hover:shadow-xl transition cursor-pointer overflow-hidden"
            >
              {/* IMAGE */}
              <img
                src={book.image_url}
                alt=""
                className="w-full h-56 object-cover"
              />

              {/* CONTENT */}
              <div className="p-4">
                <h3 className="font-bold text-lg line-clamp-2">
                  {book.title}
                </h3>

                <p className="text-gray-600 text-sm mt-1">
                  {book.author}
                </p>

                {book.rating && (
                  <p className="text-yellow-500 mt-2 text-sm">
                    ⭐ {book.rating}
                  </p>
                )}
              </div>
            </div>
          ))}
        </div>

        {/* EMPTY STATE */}
        {books.length === 0 && (
          <p className="text-center text-gray-500 mt-10">
            No books yet. Add one above 👆
          </p>
        )}

      </div>
    </div>
  );
}