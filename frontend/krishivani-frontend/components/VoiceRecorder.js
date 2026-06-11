"use client";
import { useState, useRef } from "react";

export default function VoiceRecorder({ onTranscribed, language }) {
  const [recording, setRecording] = useState(false);
  const mediaRecorderRef = useRef(null);
  const chunksRef = useRef([]);

  const startRecording = async () => {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    const mediaRecorder = new MediaRecorder(stream);
    mediaRecorderRef.current = mediaRecorder;
    chunksRef.current = [];

    mediaRecorder.ondataavailable = (e) => {
      if (e.data.size > 0) chunksRef.current.push(e.data);
    };

    mediaRecorder.onstop = async () => {
      const blob = new Blob(chunksRef.current, { type: "audio/webm" });
      onTranscribed(blob);
      stream.getTracks().forEach((t) => t.stop());
    };

    mediaRecorder.start();
    setRecording(true);
  };

  const stopRecording = () => {
    mediaRecorderRef.current?.stop();
    setRecording(false);
  };

  return (
    <button
      onClick={recording ? stopRecording : startRecording}
      className={`p-3 rounded-full text-white text-xl transition-all duration-200 ${
        recording
          ? "bg-red-500 animate-pulse scale-110"
          : "bg-green-600 hover:bg-green-700"
      }`}
      title={recording ? "Recording... click to stop" : "Speak your query"}
    >
      {recording ? "⏹" : "🎤"}
    </button>
  );
}