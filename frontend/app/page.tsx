"use client";

import { useRef, useState } from "react";
import { FileText, X } from "lucide-react";
import { AnimatedGradient } from "@/components/ui/animated-gradient";
import { Component as AiLoader } from "@/components/ui/ai-loader";
import { MetalButton } from "@/components/ui/metal-button";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { cn } from "@/lib/utils";

interface UploadedFile {
  id: number;
  name: string;
  status: "uploading" | "done";
}

interface AnsweredQuestion {
  id: number;
  question: string;
  answer: string;
  sources: string[];
}

export default function Home() {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [pendingFile, setPendingFile] = useState<File | null>(null);
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([]);

  const [question, setQuestion] = useState("");
  const [isAsking, setIsAsking] = useState(false);
  const [answers, setAnswers] = useState<AnsweredQuestion[]>([]);

  const scrollToUpload = () => {
    document.getElementById("upload")?.scrollIntoView({ behavior: "smooth" });
  };

  const handleFileChange = (e: { target: { files: FileList | null } }) => {
    setPendingFile(e.target.files?.[0] ?? null);
  };

  const handleUpload = () => {
    if (!pendingFile) return;

    const id = Date.now();
    setUploadedFiles((prev) => [
      ...prev,
      { id, name: pendingFile.name, status: "uploading" },
    ]);
    setPendingFile(null);
    if (fileInputRef.current) fileInputRef.current.value = "";

    setTimeout(() => {
      setUploadedFiles((prev) =>
        prev.map((file) =>
          file.id === id ? { ...file, status: "done" } : file
        )
      );
    }, 1500);
  };

  const handleRemoveFile = (id: number) => {
    setUploadedFiles((prev) => prev.filter((file) => file.id !== id));
  };

  const handleAsk = () => {
    const trimmed = question.trim();
    if (!trimmed || isAsking) return;

    setIsAsking(true);
    setQuestion("");

    setTimeout(() => {
      const fakeSourceDoc =
        uploadedFiles[uploadedFiles.length - 1]?.name ?? "ornek-belge.pdf";

      setAnswers((prev) => [
        {
          id: Date.now(),
          question: trimmed,
          answer:
            "Bu bir örnek cevaptır. Backend bağlantısı henüz aktif değil.",
          sources: [fakeSourceDoc, "chunk #3"],
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
                ref={fileInputRef}
                type="file"
                accept=".pdf,.txt"
                onChange={handleFileChange}
                className="flex-1 rounded-md border border-input bg-background px-3 py-2 text-sm file:mr-3 file:rounded file:border-0 file:bg-secondary file:px-3 file:py-1.5 file:text-sm file:text-secondary-foreground"
              />
              <MetalButton
                variant="default"
                onClick={handleUpload}
                disabled={!pendingFile}
              >
                Yükle
              </MetalButton>
            </div>

            {uploadedFiles.length > 0 && (
              <ul className="flex flex-col gap-2">
                {uploadedFiles.map((file) => (
                  <li
                    key={file.id}
                    className="flex items-center justify-between gap-3 rounded-md border border-border bg-muted/40 px-3 py-2 text-sm"
                  >
                    <span className="flex min-w-0 items-center gap-2">
                      <FileText className="size-4 shrink-0 text-muted-foreground" />
                      <span className="truncate">{file.name}</span>
                      <span className="shrink-0 text-xs text-muted-foreground">
                        {file.status === "uploading"
                          ? "yükleniyor..."
                          : "tamamlandı"}
                      </span>
                    </span>
                    <button
                      type="button"
                      onClick={() => handleRemoveFile(file.id)}
                      aria-label={`${file.name} dosyasını kaldır`}
                      className="shrink-0 rounded-sm p-1 text-muted-foreground hover:bg-muted hover:text-foreground"
                    >
                      <X className="size-4" />
                    </button>
                  </li>
                ))}
              </ul>
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
                <div key={item.id} className="flex flex-col gap-2">
                  <div className="flex justify-end">
                    <div className="max-w-[85%] rounded-2xl rounded-br-sm bg-primary px-4 py-2 text-sm text-primary-foreground">
                      {item.question}
                    </div>
                  </div>
                  <div className="flex flex-col items-start gap-2">
                    <div className="max-w-[85%] rounded-2xl rounded-bl-sm bg-muted px-4 py-2 text-sm text-foreground">
                      {item.answer}
                    </div>
                    <div className="flex flex-wrap gap-1.5 pl-1">
                      {item.sources.map((source, index) => (
                        <span
                          key={index}
                          className={cn(
                            "rounded-full bg-secondary px-2 py-0.5 text-xs text-secondary-foreground"
                          )}
                        >
                          {source}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
