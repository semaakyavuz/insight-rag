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
  conversation_id: string;
}

export async function askQuestion(
  question: string,
  conversationId?: string | null
): Promise<QueryResponse> {
  const res = await fetch(`${API_URL}/query`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      question,
      conversation_id: conversationId ?? null,
    }),
  });

  if (!res.ok) {
    throw new Error(`Sorgu başarısız oldu (${res.status})`);
  }

  return res.json();
}

export interface ConversationSummary {
  id: string;
  title: string | null;
  created_at: string;
}

export interface ConversationMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  sources: QuerySource[] | null;
  created_at: string;
}

export interface ConversationDetail {
  id: string;
  title: string | null;
  created_at: string;
  messages: ConversationMessage[];
}

export async function listConversations(): Promise<ConversationSummary[]> {
  const res = await fetch(`${API_URL}/conversations`);
  if (!res.ok) {
    throw new Error(`Konuşmalar alınamadı (${res.status})`);
  }
  return res.json();
}

export async function getConversation(
  id: string
): Promise<ConversationDetail> {
  const res = await fetch(`${API_URL}/conversations/${id}`);
  if (!res.ok) {
    throw new Error(`Konuşma alınamadı (${res.status})`);
  }
  return res.json();
}

export async function deleteConversation(id: string): Promise<void> {
  const res = await fetch(`${API_URL}/conversations/${id}`, {
    method: "DELETE",
  });
  if (!res.ok) {
    throw new Error(`Konuşma silinemedi (${res.status})`);
  }
}
