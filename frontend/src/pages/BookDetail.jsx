import { useEffect, useState } from "react";
import API from "../api";
import { useParams, useNavigate } from "react-router-dom";

export default function BookDetail() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [book, setBook] = useState(null);
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);

  const [recommendations, setRecommendations] = useState([]);
  const [loadingRec, setLoadingRec] = useState(false);

  useEffect(() => {
    fetchBook();
  }, []);

  // 📘 Fetch book
  const fetchBook = async () => {
    const res = await API.get("/books/");
    const found = res.data.find((b) => b.id == id);
    setBook(found);
  };

  // 💬 Ask question
  const askQuestion = async () => {
    if (!question) return;

    setLoading(true);

    const newMessages = [
      ...messages,
      { type: "user", text: question },
    ];

    setMessages(newMessages);
    setQuestion("");

    try {
      const res = await API.post("/ask/", {
        question,
        book_id: id,
      });

      setMessages([
        ...newMessages,
        { type: "bot", text: res.data.answer },
      ]);
    } catch {
      setMessages([
        ...newMessages,
        { type: "bot", text: "Error getting answer" },
      ]);
    }

    setLoading(false);
  };

  // 📚 Fetch recommendations
  const fetchRecommendations = async () => {
    setLoadingRec(true);
    try {
      const res = await API.get(`/recommend/${id}/`);
      setRecommendations(res.data.data);
    } catch (err) {
      console.log(err);
    }
    setLoadingRec(false);
  };

  if (!book) return <div className="p-6">Loading...</div>;

  return (
    <div className="min-h-screen bg-gray-100">

      {/* HEADER */}
      <div className="bg-white shadow-md p-4 flex items-center gap-4">
        <img
          src={book.image_url}
          alt=""
          className="w-16 h-20 object-cover rounded"
        />
        <div>
          <h1 className="text-xl font-bold">{book.title}</h1>
          <p className="text-gray-600 text-sm">{book.author}</p>
        </div>
      </div>

      {/* MAIN */}
      <div className="max-w-3xl mx-auto p-4">

        {/* DESCRIPTION */}
        <div className="bg-white p-4 rounded-xl shadow mb-4">
          <p className="text-gray-700 text-sm leading-relaxed">
            {book.description}
          </p>
        </div>

        {/* CHAT BOX */}
        <div className="bg-white rounded-xl shadow p-4 h-[400px] overflow-y-auto mb-4">
          {messages.length === 0 && (
            <p className="text-gray-400 text-center mt-10">
              Ask something about this book 👇
            </p>
          )}

          {messages.map((msg, index) => (
            <div
              key={index}
              className={`mb-3 flex ${
                msg.type === "user" ? "justify-end" : "justify-start"
              }`}
            >
              <div
                className={`px-4 py-2 rounded-xl max-w-xs ${
                  msg.type === "user"
                    ? "bg-blue-500 text-white"
                    : "bg-gray-200 text-black"
                }`}
              >
                {msg.text}
              </div>
            </div>
          ))}

          {loading && (
            <p className="text-gray-400">Thinking...</p>
          )}
        </div>

        {/* INPUT */}
        <div className="flex gap-2 mb-4">
          <input
            className="flex-1 border rounded-lg p-2 focus:ring-2 focus:ring-blue-400 outline-none"
            placeholder="Ask something about this book..."
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
          />

          <button
            onClick={askQuestion}
            className="bg-blue-500 text-white px-5 py-2 rounded-lg hover:bg-blue-600 transition"
          >
            Ask
          </button>
        </div>

        {/* 🔥 RECOMMEND BUTTON */}
        <button
          onClick={fetchRecommendations}
          className="bg-green-500 text-white px-4 py-2 rounded-lg hover:bg-green-600 transition mb-4"
        >
          📚 Recommend Books
        </button>

        {/* 🔥 RECOMMENDATIONS */}
        <div>
          <h2 className="text-lg font-bold mb-3">Similar Books</h2>

          {loadingRec && <p className="text-gray-400">Loading...</p>}

          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            {recommendations.map((rec) => (
              <div
                key={rec.id}
                onClick={() => navigate(`/book/${rec.id}`)}
                className="bg-white rounded-lg shadow hover:shadow-lg cursor-pointer overflow-hidden"
              >
                <img
                  src={rec.image_url}
                  alt=""
                  className="w-full h-40 object-cover"
                />

                <div className="p-2">
                  <p className="text-sm font-semibold line-clamp-2">
                    {rec.title}
                  </p>
                  <p className="text-xs text-gray-500">
                    {rec.author}
                  </p>
                </div>
              </div>
            ))}
          </div>

          {recommendations.length === 0 && !loadingRec && (
            <p className="text-gray-400 mt-2">
              Click button to see recommendations
            </p>
          )}
        </div>

      </div>
    </div>
  );
}