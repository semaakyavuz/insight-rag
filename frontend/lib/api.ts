import { API_URL } from "@/lib/config";

export interface UploadDocumentResponse {
  id: string;
  filename: string;
  content_type: string;
  chunk_count: number;
}

export async function uploadDocument(
  file: File
): Promise<UploadDocumentResponse> {
  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch(`${API_URL}/documents`, {
    method: "POST",
    body: formData,
  });

  if (!res.ok) {
    const body = await res.json().catch(() => null);
    throw new Error(body?.detail ?? `Yükleme başarısız oldu (${res.status})`);
  }

  return res.json();
}

export interface QuerySource {
  chunk_id: string;
  chunk_text: string;
  similarity_score: number;
  document_filename: string;
}

export interface QueryResponse {
  answer: string;
  sources: QuerySource[];
}

export async function askQuestion(question: string): Promise<QueryResponse> {
  const res = await fetch(`${API_URL}/query`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  });

  if (!res.ok) {
    throw new Error(`Sorgu başarısız oldu (${res.status})`);
  }

  return res.json();
}
