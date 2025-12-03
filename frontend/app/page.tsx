"use client";

import { useState, useRef, useEffect } from "react";
import { Send, Upload, FileText, Bot, User, Layers, File } from "lucide-react";

type Message = {
  role: "user" | "assistant";
  content: string;
};

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [docId, setDocId] = useState<string | null>(null);
  const [uploadStatus, setUploadStatus] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Scroll automatique vers le bas
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Gestion de l'upload PDF
  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files?.[0]) return;
    setUploadStatus("Uploading...");
    
    const formData = new FormData();
    formData.append("file", e.target.files[0]);

    try {
      const res = await fetch("http://127.0.0.1:8000/upload-pdf", {
        method: "POST",
        body: formData,
      });
      const data = await res.json();
      if (res.ok) {
        setDocId(data.doc_id);
        setUploadStatus("PDF Prêt !");
        // Petit message système pour confirmer
        setMessages(prev => [...prev, {role: "assistant", content: "J'ai bien reçu votre document. Posez-moi une question dessus !"}]);
      } else {
        setUploadStatus("Erreur upload");
      }
    } catch (error) {
      console.error(error);
      setUploadStatus("Erreur connexion");
    }
  };

  // Gestion de l'envoi de message (Mode Standard JSON)
  const sendMessage = async () => {
    if (!input.trim() || isLoading) return;

    const userMsg = input;
    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: userMsg }]);
    setIsLoading(true);

    // On ajoute une bulle temporaire "..."
    setMessages((prev) => [...prev, { role: "assistant", content: "..." }]);

    try {
      const response = await fetch("http://127.0.0.1:8000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          question: userMsg,
          doc_id: docId, 
          history: messages,
        }),
      });

      const data = await response.json();

      // On remplace les "..." par la vraie réponse
      setMessages((prev) => {
        const newHistory = [...prev];
        // On modifie le dernier message (qui était "...")
        newHistory[newHistory.length - 1].content = data.answer; 
        return newHistory;
      });

    } catch (error) {
      console.error(error);
      setMessages((prev) => {
        const newHistory = [...prev];
        newHistory[newHistory.length - 1].content = "Erreur : Impossible de joindre l'IA.";
        return newHistory;
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <main className="flex min-h-screen flex-col items-center bg-gray-50 p-4 md:p-8 font-sans text-gray-800">
      <div className="w-full max-w-4xl bg-white rounded-2xl shadow-xl overflow-hidden flex flex-col h-[85vh] border border-gray-200">
        
        {/* Header */}
        <div className="bg-slate-900 p-4 text-white flex justify-between items-center shadow-md">
          <div className="flex items-center gap-2">
            <Bot className="text-blue-400" />
            <h1 className="text-xl font-bold tracking-wide">RAG Chatbot</h1>
          </div>
          
          <div className="flex items-center gap-4 text-sm">
             {/* Status Indicator */}
            <div className={`flex items-center gap-2 px-3 py-1 rounded-full text-xs font-medium ${docId ? "bg-green-900 text-green-200" : "bg-indigo-900 text-indigo-200"}`}>
              {docId ? <File size={14} /> : <Layers size={14} />}
              {docId ? "Mode: Doc Unique" : "Mode: Multi-Docs"}
            </div>

             {/* Upload Button */}
            <label className="cursor-pointer bg-blue-600 hover:bg-blue-500 px-4 py-2 rounded-lg flex items-center gap-2 transition shadow-sm font-semibold">
              <Upload size={16} />
              <span>{uploadStatus || "Nouveau PDF"}</span>
              <input type="file" accept=".pdf" className="hidden" onChange={handleUpload} />
            </label>
          </div>
        </div>

        {/* Zone de Chat */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6 bg-slate-50">
          {messages.length === 0 && (
            <div className="h-full flex flex-col items-center justify-center text-gray-400 opacity-60">
              <FileText size={64} className="mb-4 text-slate-300" />
              <p className="text-lg font-medium">Envoyez un PDF pour commencer</p>
              <p className="text-sm">ou posez une question sur la base existante</p>
            </div>
          )}
          
          {messages.map((msg, idx) => (
            <div key={idx} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
              <div className={`max-w-[80%] p-4 rounded-2xl shadow-sm flex gap-3 ${
                msg.role === "user" 
                  ? "bg-blue-600 text-white rounded-br-none" 
                  : "bg-white text-gray-800 border border-gray-100 rounded-bl-none"
              }`}>
                <div className={`mt-1 min-w-[20px] ${msg.role === "user" ? "text-blue-200" : "text-blue-600"}`}>
                  {msg.role === "user" ? <User size={20} /> : <Bot size={20} />}
                </div>
                <div className="leading-relaxed whitespace-pre-wrap">{msg.content}</div>
              </div>
            </div>
          ))}
          {isLoading && (
            <div className="flex justify-start animate-pulse">
               <div className="bg-white p-4 rounded-2xl rounded-bl-none shadow-sm border border-gray-100 flex gap-3 items-center text-gray-400">
                  <Bot size={20} />
                  <span className="text-sm">L'IA réfléchit...</span>
               </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Zone */}
        <div className="p-4 bg-white border-t border-gray-100">
          <div className="flex gap-3 relative">
            <input
              type="text"
              className="w-full p-4 pr-12 rounded-xl bg-gray-50 border border-gray-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:bg-white transition text-gray-800 placeholder-gray-400"
              placeholder="Posez votre question sur les documents..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && sendMessage()}
              disabled={isLoading}
            />
            <button
              onClick={sendMessage}
              disabled={isLoading || !input.trim()}
              className="absolute right-2 top-2 bottom-2 bg-slate-900 hover:bg-slate-800 disabled:bg-gray-300 text-white p-3 rounded-lg transition shadow-sm flex items-center justify-center aspect-square"
            >
              <Send size={20} />
            </button>
          </div>
          <div className="text-center mt-2">
             <button 
               onClick={() => setDocId(null)} 
               className={`text-xs hover:underline ${!docId ? 'hidden' : 'text-gray-400'}`}
             >
               Sortir du mode Document Unique (Recherche Globale)
             </button>
          </div>
        </div>
      </div>
    </main>
  );
}