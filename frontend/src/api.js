import axios from "axios";

const API = axios.create({
  baseURL: "http://localhost:8000",  // 🔥 IMPORTANT
});

export default API;