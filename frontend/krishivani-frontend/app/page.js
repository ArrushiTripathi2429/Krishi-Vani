"use client";

import { useState } from "react";
import axios from "axios";
import { motion } from "framer-motion";

import VoiceRecorder from "@/components/VoiceRecorder";
import SourceCard from "@/components/SourceCard";

const API = "http://localhost:8000/api";

export default function Home() {
  const [query, setQuery] = useState("");
  const [language, setLanguage] = useState("english");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleSubmit = async () => {
    if (!query.trim()) return;

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const res = await axios.post(`${API}/query`, {
        query,
        language,
      });

      setResult(res.data);
    } catch {
      setError("Unable to fetch response. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleVoiceBlob = async (blob) => {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const formData = new FormData();
      formData.append("audio", blob, "recording.webm");
      formData.append("language", language);

      const res = await axios.post(`${API}/voice-query`, formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });

      setResult(res.data);
    } catch {
      setError("Could not process audio.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="relative min-h-screen overflow-hidden bg-black text-white">

      {/* Animated Background */}
      <div className="absolute inset-0 overflow-hidden">

        <div className="absolute top-0 left-0 w-[600px] h-[600px] bg-green-500/20 rounded-full blur-[180px] animate-pulse" />

        <div className="absolute bottom-0 right-0 w-[500px] h-[500px] bg-emerald-500/20 rounded-full blur-[180px] animate-pulse" />

        <div className="absolute top-1/2 left-1/2 w-[300px] h-[300px] bg-lime-400/10 rounded-full blur-[120px]" />

      </div>

      <div className="relative z-10 max-w-5xl mx-auto px-6 py-16">

        {/* Hero */}
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="text-center mb-14"
        >

          <motion.div
            animate={{ y: [0, -12, 0] }}
            transition={{
              repeat: Infinity,
              duration: 3,
            }}
            className="text-7xl mb-6"
          >
            🌾
          </motion.div>

          <h1
            className="
            text-6xl
            md:text-8xl
            font-black
            bg-gradient-to-r
            from-green-300
            via-emerald-500
            to-lime-300
            bg-clip-text
            text-transparent
            animate-gradient
          "
          >
            KrishiVani
          </h1>

          <p className="mt-6 text-lg text-gray-400 max-w-2xl mx-auto">
            AI-powered agricultural intelligence platform built on
            73,000+ expert KCC responses.
          </p>

          <div className="flex justify-center mt-6">
            <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-full px-5 py-2 text-sm text-green-300">
              Smart Farming Assistant
            </div>
          </div>
        </motion.div>

        {/* Language Toggle */}
        <div className="flex justify-center mb-8">
          <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-1 flex gap-1">

            {["english", "hindi"].map((lang) => (
              <button
                key={lang}
                onClick={() => setLanguage(lang)}
                className={`px-5 py-2 rounded-xl transition-all ${
                  language === lang
                    ? "bg-green-600 text-white"
                    : "text-gray-400 hover:text-white"
                }`}
              >
                {lang === "english" ? "English" : "Hindi"}
              </button>
            ))}

          </div>
        </div>

        {/* Search Box */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="
          bg-white/5
          backdrop-blur-xl
          border
          border-white/10
          rounded-3xl
          p-3
          shadow-2xl
          mb-8
        "
        >
          <div className="flex gap-3">

            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) =>
                e.key === "Enter" && handleSubmit()
              }
              placeholder="Ask about crops, diseases, fertilizers..."
              className="
              flex-1
              bg-transparent
              text-white
              placeholder:text-gray-500
              outline-none
              px-4
            "
            />

            <VoiceRecorder
              onTranscribed={handleVoiceBlob}
              language={language}
            />

            <button
              onClick={handleSubmit}
              disabled={loading}
              className="
              px-6
              py-3
              rounded-2xl
              font-semibold
              bg-gradient-to-r
              from-green-500
              to-emerald-600
              hover:scale-105
              transition-all
              shadow-lg
              shadow-green-500/30
            "
            >
              {loading ? "..." : "Ask AI"}
            </button>

          </div>
        </motion.div>

        {/* Error */}
        {error && (
          <div className="bg-red-500/10 border border-red-500/30 rounded-2xl p-4 text-red-300 mb-6">
            {error}
          </div>
        )}

        {/* Result */}
        {result && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="space-y-6"
          >

            <div
              className="
              bg-white/5
              backdrop-blur-xl
              border
              border-white/10
              rounded-3xl
              p-6
              shadow-2xl
            "
            >

              <div className="flex flex-wrap gap-2 items-center mb-4">

                <span className="font-semibold text-green-300">
                  🤖 AI Recommendation
                </span>

                {result.crop_detected && (
                  <span className="px-3 py-1 rounded-full text-xs bg-green-500/20 border border-green-500/20 text-green-300">
                    {result.crop_detected}
                  </span>
                )}

                {result.agro_zone && (
                  <span className="px-3 py-1 rounded-full text-xs bg-blue-500/20 border border-blue-500/20 text-blue-300">
                    {result.agro_zone}
                  </span>
                )}
              </div>

              <p className="text-gray-300 whitespace-pre-wrap leading-8">
                {result.answer}
              </p>

              {result.fallback_triggered && (
                <div className="mt-4 text-orange-300 text-sm">
                  Extended agricultural search was used.
                </div>
              )}
            </div>

            {/* Sources */}
            {result.sources?.length > 0 && (
              <div>

                <h3 className="text-gray-300 font-semibold mb-4">
                  Knowledge Sources
                </h3>

                <div className="grid gap-4">
                  {result.sources.map((src, i) => (
                    <SourceCard
                      key={i}
                      source={src}
                      index={i}
                    />
                  ))}
                </div>

              </div>
            )}

          </motion.div>
        )}

      </div>
    </main>
  );
}