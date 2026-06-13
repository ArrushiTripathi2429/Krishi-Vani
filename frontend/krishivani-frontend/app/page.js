"use client";

import { useState, useEffect } from "react";
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
  const [threadId, setThreadId] = useState(null);
  const [threads, setThreads] = useState([]);
  const [sidebarOpen, setSidebarOpen] = useState(true);

  // Load all threads on mount
  useEffect(() => {
    fetchThreads();
  }, []);

  const fetchThreads = async () => {
    try {
      const res = await axios.get(`${API}/threads`);
      setThreads(res.data);
    } catch {}
  };

  const loadThread = async (tid) => {
    try {
      const res = await axios.get(`${API}/threads/${tid}/messages`);
      setMessages(res.data);
      setThreadId(tid);
    } catch {}
  };

  const newChat = () => {
    setMessages([]);
    setThreadId(null);
    setError(null);
    setQuery("");
  };

  const deleteThread = async (tid, e) => {
    e.stopPropagation();
    try {
      await axios.delete(`${API}/threads/${tid}`);
      if (tid === threadId) newChat();
      fetchThreads();
    } catch {}
  };

  const handleSubmit = async () => {
    if (!query.trim()) return;
    setLoading(true);
    setError(null);

    const userMessage = { role: "user", content: query };
    setMessages((prev) => [...prev, userMessage]);
    setQuery("");

    try {
      const res = await axios.post(`${API}/thread-chat`, {
        message: userMessage.content,
        thread_id: threadId,
        language,
      });

      const assistantMessage = {
        role: "assistant",
        content: res.data.answer,
        sources: res.data.sources || [],
        is_farming: res.data.is_farming,
      };
      setMessages((prev) => [...prev, assistantMessage]);
      
      // Set thread id if new
      if (!threadId) {
        setThreadId(res.data.thread_id);
        fetchThreads();
      }
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

      const userMessage = { role: "user", content: " Voice message" };
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
    <main className="relative min-h-screen overflow-hidden bg-black text-white flex">

      {/* Background */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-0 left-0 w-[600px] h-[600px] bg-green-500/20 rounded-full blur-[180px] animate-pulse" />
        <div className="absolute bottom-0 right-0 w-[500px] h-[500px] bg-emerald-500/20 rounded-full blur-[180px] animate-pulse" />
      </div>

      {/* Sidebar */}
      {sidebarOpen && (
        <div className="relative z-10 w-64 min-h-screen bg-white/5 border-r border-white/10 flex flex-col p-4">
          <div className="flex items-center justify-between mb-4">
            <span className="text-green-400 font-bold text-sm"> Threads</span>
            <button
              onClick={() => setSidebarOpen(false)}
              className="text-gray-500 hover:text-white text-xs"
            >
              ✕
            </button>
          </div>

          <button
            onClick={newChat}
            className="w-full mb-4 py-2 rounded-xl bg-green-600 hover:bg-green-700 text-white text-sm font-medium transition-all"
          >
            + New Chat
          </button>

          <div className="flex-1 overflow-y-auto space-y-2">
            {threads.length === 0 && (
              <p className="text-gray-600 text-xs text-center mt-4">No threads yet</p>
            )}
            {threads.map((t) => (
              <div
                key={t.id}
                onClick={() => loadThread(t.id)}
                className={`group flex items-center justify-between px-3 py-2 rounded-xl cursor-pointer text-xs transition-all ${
                  threadId === t.id
                    ? "bg-green-600/30 text-green-300 border border-green-500/30"
                    : "hover:bg-white/5 text-gray-400"
                }`}
              >
                <span className="truncate flex-1">{t.title}</span>
                <button
                  onClick={(e) => deleteThread(t.id, e)}
                  className="ml-2 opacity-0 group-hover:opacity-100 text-red-400 hover:text-red-300 transition-all"
                >
                  🗑
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Main Chat Area */}
      <div className="relative z-10 flex-1 flex flex-col max-h-screen">

        {/* Top bar */}
        <div className="flex items-center gap-3 px-6 py-4 border-b border-white/10">
          {!sidebarOpen && (
            <button
              onClick={() => setSidebarOpen(true)}
              className="text-gray-400 hover:text-white text-sm"
            >
              ☰
            </button>
          )}
          <h1 className="text-xl font-black bg-gradient-to-r from-green-300 to-lime-300 bg-clip-text text-transparent">
            KrishiVani 
          </h1>
          <div className="ml-auto flex gap-1 bg-white/5 border border-white/10 rounded-xl p-1">
            {["english", "hindi"].map((lang) => (
              <button
                key={lang}
                onClick={() => setLanguage(lang)}
                className={`px-4 py-1.5 rounded-lg text-xs transition-all ${
                  language === lang ? "bg-green-600 text-white" : "text-gray-400 hover:text-white"
                }`}
              >
                {lang === "english" ? "English" : "Hindi"}
              </button>
            ))}
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto px-6 py-6 space-y-4">
          {messages.length === 0 && (
            <div className="text-center text-gray-600 mt-32">
              <p className="text-4xl mb-4">🌾</p>
              <p className="text-lg font-medium text-gray-500">Ask anything</p>
              <p className="text-sm mt-1 text-gray-600">Farming related ya general — dono chalega!</p>
            </div>
          )}

          {messages.map((msg, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
            >
              <div className={`max-w-[75%] rounded-2xl px-5 py-3 text-sm leading-7 ${
                msg.role === "user"
                  ? "bg-green-600 text-white rounded-br-none"
                  : "bg-white/5 border border-white/10 text-gray-300 rounded-bl-none"
              }`}>
                {msg.role === "assistant" && (
                  <p className="text-green-400 text-xs font-semibold mb-1">
                    KrishiVani {msg.is_farming ? "" : ""}
                  </p>
                )}
                <p className="whitespace-pre-wrap">{msg.content}</p>

                {msg.sources?.length > 0 && (
                  <div className="mt-3 pt-3 border-t border-white/10">
                    <p className="text-xs text-gray-500 mb-2"> Sources</p>
                    <div className="space-y-2">
                      {msg.sources.slice(0, 2).map((src, j) => (
                        <div key={j} className="text-xs bg-white/5 rounded-xl px-3 py-2">
                          <span className="text-green-400"> {src.crop || "N/A"}</span>
                          <span className="text-gray-500 ml-2">{src.district || "N/A"}</span>
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
                Thinking...
              </div>
            </div>
          )}
        </div>

        {/* Error */}
        {error && (
          <div className="mx-6 mb-2 bg-red-500/10 border border-red-500/30 rounded-2xl p-3 text-red-300 text-sm">
            {error}
          </div>
        )}

        {/* Input */}
        <div className="px-6 py-4 border-t border-white/10">
          <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-3xl p-3">
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

      </div>
    </main>
  );
}