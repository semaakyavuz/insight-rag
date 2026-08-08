"use client";

import { useRef, useState } from "react";
import { FileText, X } from "lucide-react";
import { HeroParallax } from "@/components/ui/hero-parallax";
import { Component as AiLoader } from "@/components/ui/ai-loader";
import { MetalButton } from "@/components/ui/metal-button";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { cn } from "@/lib/utils";
import { askQuestion, uploadDocument } from "@/lib/api";

interface UploadedFile {
  id: number;
  name: string;
  status: "uploading" | "done" | "error";
  documentId?: string;
  errorMessage?: string;
}

interface AnsweredQuestion {
  id: number;
  question: string;
  answer: string;
  sources: { label: string }[];
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

  const handleUpload = async () => {
    if (!pendingFile) return;

    const file = pendingFile;
    const id = Date.now();

    setUploadedFiles((prev) => [
      ...prev,
      { id, name: file.name, status: "uploading" },
    ]);
    setPendingFile(null);
    if (fileInputRef.current) fileInputRef.current.value = "";

    try {
      const result = await uploadDocument(file);
      setUploadedFiles((prev) =>
        prev.map((f) =>
          f.id === id ? { ...f, status: "done", documentId: result.id } : f
        )
      );
    } catch (err) {
      setUploadedFiles((prev) =>
        prev.map((f) =>
          f.id === id
            ? {
                ...f,
                status: "error",
                errorMessage:
                  err instanceof Error ? err.message : "Yükleme başarısız oldu",
              }
            : f
        )
      );
    }
  };

  const handleRemoveFile = (id: number) => {
    setUploadedFiles((prev) => prev.filter((file) => file.id !== id));
  };

  const handleAsk = async () => {
    const trimmed = question.trim();
    if (!trimmed || isAsking) return;

    setIsAsking(true);
    setQuestion("");

    try {
      const result = await askQuestion(trimmed);
      setAnswers((prev) => [
        {
          id: Date.now(),
          question: trimmed,
          answer: result.answer,
          sources: result.sources.map((source) => ({
            label: `${source.chunk_text.slice(0, 60)}${
              source.chunk_text.length > 60 ? "…" : ""
            } — ${source.document_filename}`,
          })),
        },
        ...prev,
      ]);
    } catch {
      setAnswers((prev) => [
        {
          id: Date.now(),
          question: trimmed,
          answer: "Şu an cevap üretemiyorum, lütfen tekrar deneyin.",
          sources: [],
        },
        ...prev,
      ]);
    } finally {
      setIsAsking(false);
    }
  };

  return (
    <div className="flex flex-col">
      <HeroParallax onCtaClick={scrollToUpload} />

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
                    className="flex flex-col gap-1 rounded-md border border-border bg-muted/40 px-3 py-2 text-sm"
                  >
                    <div className="flex items-center justify-between gap-3">
                      <span className="flex min-w-0 items-center gap-2">
                        <FileText className="size-4 shrink-0 text-muted-foreground" />
                        <span className="truncate">{file.name}</span>
                        <span
                          className={cn(
                            "shrink-0 text-xs",
                            file.status === "error"
                              ? "text-destructive"
                              : "text-muted-foreground"
                          )}
                        >
                          {file.status === "uploading"
                            ? "yükleniyor..."
                            : file.status === "error"
                              ? "hata"
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
                    </div>
                    {file.status === "error" && file.errorMessage && (
                      <p className="pl-6 text-xs text-destructive">
                        {file.errorMessage}
                      </p>
                    )}
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
                          className="rounded-full bg-secondary px-2 py-0.5 text-xs text-secondary-foreground"
                        >
                          {source.label}
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
