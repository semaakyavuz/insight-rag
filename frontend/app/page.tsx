"use client";

import { useState } from "react";
import { AnimatedGradient } from "@/components/ui/animated-gradient";
import { Component as AiLoader } from "@/components/ui/ai-loader";
import { MetalButton } from "@/components/ui/metal-button";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

interface AnsweredQuestion {
  id: number;
  question: string;
  answer: string;
}

export default function Home() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploadStatus, setUploadStatus] = useState<
    "idle" | "uploading" | "done"
  >("idle");

  const [question, setQuestion] = useState("");
  const [isAsking, setIsAsking] = useState(false);
  const [answers, setAnswers] = useState<AnsweredQuestion[]>([]);

  const scrollToUpload = () => {
    document.getElementById("upload")?.scrollIntoView({ behavior: "smooth" });
  };

  const handleFileChange = (e: { target: { files: FileList | null } }) => {
    setSelectedFile(e.target.files?.[0] ?? null);
    setUploadStatus("idle");
  };

  const handleUpload = () => {
    if (!selectedFile || uploadStatus === "uploading") return;
    setUploadStatus("uploading");
    setTimeout(() => {
      setUploadStatus("done");
    }, 1500);
  };

  const handleAsk = () => {
    const trimmed = question.trim();
    if (!trimmed || isAsking) return;

    setIsAsking(true);
    setQuestion("");

    setTimeout(() => {
      setAnswers((prev) => [
        {
          id: Date.now(),
          question: trimmed,
          answer:
            "Bu bir örnek cevaptır. Backend bağlantısı henüz aktif değil.",
        },
        ...prev,
      ]);
      setIsAsking(false);
    }, 2000);
  };

  return (
    <div className="flex flex-col">
      <section className="relative flex h-[60vh] min-h-95 w-full items-center justify-center overflow-hidden sm:h-[70vh]">
        <AnimatedGradient config={{ preset: "Aurora" }} />
        <div className="relative z-10 flex flex-col items-center gap-3 px-6 text-center sm:gap-6">
          <h1 className="font-heading text-4xl font-bold tracking-tight text-white sm:text-6xl">
            InsightRAG
          </h1>
          <p className="max-w-md text-sm text-white/80 sm:text-lg">
            Dokümanlarınla konuş, anında cevap al
          </p>
          <MetalButton
            variant="primary"
            onClick={scrollToUpload}
            className="mt-2 h-9 px-4 text-xs sm:h-11 sm:px-6 sm:text-sm"
          >
            Başla
          </MetalButton>
        </div>
      </section>

      <div
        id="upload"
        className="mx-auto grid w-full max-w-6xl grid-cols-1 gap-8 px-6 py-16 md:grid-cols-2 sm:py-24"
      >
        <Card>
          <CardHeader>
            <CardTitle className="font-bold">Doküman Yükle</CardTitle>
          </CardHeader>
          <CardContent className="flex flex-col gap-4">
            <div className="flex flex-col items-stretch gap-3 sm:flex-row sm:items-center">
              <input
                type="file"
                accept=".pdf,.txt"
                onChange={handleFileChange}
                className="flex-1 rounded-md border border-input bg-background px-3 py-2 text-sm file:mr-3 file:rounded file:border-0 file:bg-secondary file:px-3 file:py-1.5 file:text-sm file:text-secondary-foreground"
              />
              <MetalButton
                variant="default"
                onClick={handleUpload}
                disabled={!selectedFile || uploadStatus === "uploading"}
              >
                Yükle
              </MetalButton>
            </div>
            {selectedFile && (
              <p className="text-sm text-muted-foreground">
                {selectedFile.name} —{" "}
                {uploadStatus === "uploading"
                  ? "yükleniyor..."
                  : uploadStatus === "done"
                    ? "tamamlandı"
                    : "hazır"}
              </p>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="font-bold">Soru Sor</CardTitle>
          </CardHeader>
          <CardContent className="flex flex-col gap-4">
            <div className="flex flex-col items-stretch gap-3 sm:flex-row sm:items-center">
              <input
                type="text"
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter") handleAsk();
                }}
                placeholder="Dokümanlarınla ilgili bir soru sor..."
                className="flex-1 rounded-md border border-input bg-background px-3 py-2 text-sm"
              />
              <MetalButton
                variant="success"
                onClick={handleAsk}
                disabled={isAsking || !question.trim()}
              >
                Sor
              </MetalButton>
            </div>

            {isAsking && (
              <div className="flex justify-center py-4">
                <AiLoader />
              </div>
            )}

            <div className="flex flex-col gap-4">
              {answers.map((item) => (
                <div
                  key={item.id}
                  className="rounded-lg border border-border bg-card p-4"
                >
                  <p className="text-sm font-medium text-foreground">
                    {item.question}
                  </p>
                  <p className="mt-2 text-sm text-muted-foreground">
                    {item.answer}
                  </p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
