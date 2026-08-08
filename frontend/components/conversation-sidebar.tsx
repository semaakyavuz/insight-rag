"use client";

import { useEffect, useState } from "react";
import { Plus, Trash2 } from "lucide-react";
import { cn } from "@/lib/utils";
import {
  deleteConversation,
  listConversations,
  type ConversationSummary,
} from "@/lib/api";

interface ConversationSidebarProps {
  isOpen: boolean;
  activeConversationId: string | null;
  refreshKey: number;
  onSelectConversation: (id: string) => void;
  onNewConversation: () => void;
}

export function ConversationSidebar({
  isOpen,
  activeConversationId,
  refreshKey,
  onSelectConversation,
  onNewConversation,
}: ConversationSidebarProps) {
  const [conversations, setConversations] = useState<ConversationSummary[]>(
    []
  );

  useEffect(() => {
    let cancelled = false;
    listConversations()
      .then((result) => {
        if (!cancelled) setConversations(result);
      })
      .catch(() => {
        if (!cancelled) setConversations([]);
      });
    return () => {
      cancelled = true;
    };
  }, [refreshKey]);

  const handleDelete = async (
    event: React.MouseEvent<HTMLButtonElement>,
    id: string
  ) => {
    event.stopPropagation();
    setConversations((prev) => prev.filter((c) => c.id !== id));
    if (activeConversationId === id) {
      onNewConversation();
    }
    try {
      await deleteConversation(id);
    } catch {
      // Best-effort removal; the list re-syncs on the next refresh.
    }
  };

  return (
    <aside
      className={cn(
        "fixed inset-y-0 left-0 z-40 flex w-64 -translate-x-full flex-col border-r border-border bg-background transition-transform duration-200",
        "md:sticky md:top-14 md:h-[calc(100vh-3.5rem)] md:translate-x-0",
        isOpen && "translate-x-0"
      )}
    >
      <div className="p-3">
        <button
          type="button"
          onClick={onNewConversation}
          className="flex w-full items-center justify-center gap-2 rounded-md border border-border px-3 py-2 text-sm hover:bg-muted"
        >
          <Plus className="size-4" />
          Yeni Konuşma
        </button>
      </div>

      <nav className="flex-1 overflow-y-auto px-2 pb-3">
        {conversations.map((conversation) => (
          <div
            key={conversation.id}
            role="button"
            tabIndex={0}
            onClick={() => onSelectConversation(conversation.id)}
            onKeyDown={(event) => {
              if (event.key === "Enter" || event.key === " ") {
                onSelectConversation(conversation.id);
              }
            }}
            className={cn(
              "group flex w-full cursor-pointer items-center justify-between gap-2 rounded-md px-3 py-2 text-left text-sm hover:bg-muted",
              activeConversationId === conversation.id && "bg-muted"
            )}
          >
            <span className="flex min-w-0 flex-col">
              <span className="truncate">
                {conversation.title || "Adsız konuşma"}
              </span>
              <span className="text-xs text-muted-foreground">
                {new Date(conversation.created_at).toLocaleDateString(
                  "tr-TR"
                )}
              </span>
            </span>
            <button
              type="button"
              onClick={(event) => handleDelete(event, conversation.id)}
              aria-label="Konuşmayı sil"
              className="shrink-0 rounded-sm p-1 text-muted-foreground opacity-0 hover:bg-destructive/10 hover:text-destructive focus-visible:opacity-100 group-hover:opacity-100"
            >
              <Trash2 className="size-4" />
            </button>
          </div>
        ))}
      </nav>
    </aside>
  );
}
