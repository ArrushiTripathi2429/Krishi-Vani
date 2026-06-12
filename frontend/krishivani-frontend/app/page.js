"use client";

import { useState } from "react";
import axios from "axios";
import { motion } from "framer-motion";
import VoiceRecorder from "@/components/VoiceRecorder";

const API = "http://localhost:8000/api";

export default function Home() {
  const [query, setQuery] = useState("");
  const [language, setLanguage] = useState("english");
  const [loading, setLoading] = useState(false);
  const [messages, setMessages] = useState([]);
  const [error, setError] = useState(null);

  const handleSubmit = async () => {
    if (!query.trim()) return;
    setLoading(true);
    setError(null);

    const userMessage = { role: "user", content: query };
    const updatedHistory = [...messages, userMessage];
    setMessages(updatedHistory);
    setQuery("");

    try {
      const res = await axios.post(`${API}/chat`, {
        message: userMessage.content,
        history: updatedHistory,
        language,
      });

      const assistantMessage = {
        role: "assistant",
        content: res.data.answer,
        sources: res.data.sources || [],
        is_farming: res.data.is_farming,
      };
      setMessages([...updatedHistory, assistantMessage]);
    } catch {
      setError("Unable to fetch response. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleVoiceBlob = async (blob) => {
    setLoading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append("audio", blob, "recording.webm");
      formData.append("language", language);

      const res = await axios.post(`${API}/voice-query`, formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      const userMessage = { role: "user", content: "🎤 Voice message" };
      const assistantMessage = {
        role: "assistant",
        content: res.data.answer,
        sources: res.data.sources || [],
        is_farming: true,
      };
      setMessages((prev) => [...prev, userMessage, assistantMessage]);
    } catch {
      setError("Could not process audio.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="relative min-h-screen overflow-hidden bg-black text-white">

      {/* Background */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute top-0 left-0 w-[600px] h-[600px] bg-green-500/20 rounded-full blur-[180px] animate-pulse" />
        <div className="absolute bottom-0 right-0 w-[500px] h-[500px] bg-emerald-500/20 rounded-full blur-[180px] animate-pulse" />
      </div>

      <div className="relative z-10 max-w-3xl mx-auto px-6 py-16 flex flex-col min-h-screen">

        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="text-center mb-10"
        >
          <motion.div
            animate={{ y: [0, -12, 0] }}
            transition={{ repeat: Infinity, duration: 3 }}
            className="text-7xl mb-4"
          >
            🌾
          </motion.div>
          <h1 className="text-6xl md:text-8xl font-black bg-gradient-to-r from-green-300 via-emerald-500 to-lime-300 bg-clip-text text-transparent">
            KrishiVani
          </h1>
          <p className="mt-4 text-gray-400 max-w-xl mx-auto">
            AI-powered agricultural intelligence platform built on 73,000+ expert KCC responses.
          </p>
        </motion.div>

        {/* Language Toggle */}
        <div className="flex justify-center mb-6">
          <div className="bg-white/5 border border-white/10 rounded-2xl p-1 flex gap-1">
            {["english", "hindi"].map((lang) => (
              <button
                key={lang}
                onClick={() => setLanguage(lang)}
                className={`px-5 py-2 rounded-xl transition-all ${
                  language === lang ? "bg-green-600 text-white" : "text-gray-400 hover:text-white"
                }`}
              >
                {lang === "english" ? "English" : "Hindi"}
              </button>
            ))}
          </div>
        </div>

        {/* Chat Messages */}
        <div className="flex-1 space-y-4 mb-6 overflow-y-auto">
          {messages.length === 0 && (
            <div className="text-center text-gray-600 mt-20">
              <p className="text-lg">Koi bhi sawaal poochho</p>
              <p className="text-sm mt-2">Farming related ya general — dono chalega!</p>
            </div>
          )}

          {messages.map((msg, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
            >
              <div className={`max-w-[80%] rounded-2xl px-5 py-3 text-sm leading-7 ${
                msg.role === "user"
                  ? "bg-green-600 text-white rounded-br-none"
                  : "bg-white/5 border border-white/10 text-gray-300 rounded-bl-none"
              }`}>
                {msg.role === "assistant" && (
                  <p className="text-green-400 text-xs font-semibold mb-1">
                    KrishiVani {msg.is_farming ? "🌾" : "💬"}
                  </p>
                )}
                <p className="whitespace-pre-wrap">{msg.content}</p>

                {/* Sources */}
                {msg.sources?.length > 0 && (
                  <div className="mt-3 pt-3 border-t border-white/10">
                    <p className="text-xs text-gray-500 mb-2">📚 Sources</p>
                    <div className="space-y-2">
                      {msg.sources.slice(0, 2).map((src, j) => (
                        <div key={j} className="text-xs bg-white/5 rounded-xl px-3 py-2">
                          <span className="text-green-400">🌾 {src.crop || "N/A"}</span>
                          <span className="text-gray-500 ml-2">📍 {src.district || "N/A"}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </motion.div>
          ))}

          {loading && (
            <div className="flex justify-start">
              <div className="bg-white/5 border border-white/10 rounded-2xl px-5 py-3 text-gray-400 text-sm animate-pulse">
                Thinking
              </div>
            </div>
          )}
        </div>

        {/* Error */}
        {error && (
          <div className="bg-red-500/10 border border-red-500/30 rounded-2xl p-3 text-red-300 text-sm mb-4">
            {error}
          </div>
        )}

        {/* Input Box */}
        <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-3xl p-3 shadow-2xl">
          <div className="flex gap-3">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSubmit()}
              placeholder="Ask about crops, diseases, or anything..."
              className="flex-1 bg-transparent text-white placeholder:text-gray-500 outline-none px-4"
            />
            <VoiceRecorder onTranscribed={handleVoiceBlob} language={language} />
            <button
              onClick={handleSubmit}
              disabled={loading}
              className="px-6 py-3 rounded-2xl font-semibold bg-gradient-to-r from-green-500 to-emerald-600 hover:scale-105 transition-all shadow-lg shadow-green-500/30 disabled:opacity-50"
            >
              {loading ? "..." : "Ask AI"}
            </button>
          </div>
        </div>

      </div>
    </main>
  );
}