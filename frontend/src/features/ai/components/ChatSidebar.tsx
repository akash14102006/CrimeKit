"use client";

import { useState, useCallback } from "react";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  MessageSquare,
  Plus,
  Trash2,
  Pin,
  PinOff,
  Pencil,
  Search,
  ChevronLeft,
  Check,
  X,
} from "lucide-react";
import { useAIStore } from "../store/aiStore";

function ConversationItem({
  conv,
  isActive,
  onSelect,
  onDelete,
  onRename,
  onTogglePin,
}: {
  conv: { id: string; title: string; agent_id?: string; updated_at: number; pinned: boolean; messages: unknown[] };
  isActive: boolean;
  onSelect: () => void;
  onDelete: () => void;
  onRename: (title: string) => void;
  onTogglePin: () => void;
}) {
  const [editing, setEditing] = useState(false);
  const [editTitle, setEditTitle] = useState(conv.title);

  const handleSave = useCallback(() => {
    if (editTitle.trim()) {
      onRename(editTitle.trim());
    }
    setEditing(false);
  }, [editTitle, onRename]);

  return (
    <div
      className={`group flex items-center gap-2 px-3 py-2 rounded-md cursor-pointer text-sm transition-colors ${
        isActive ? "bg-muted" : "hover:bg-muted/50"
      }`}
      onClick={onSelect}
    >
      {editing ? (
        <div className="flex items-center gap-1 flex-1" onClick={(e) => e.stopPropagation()}>
          <Input
            value={editTitle}
            onChange={(e) => setEditTitle(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") handleSave();
              if (e.key === "Escape") setEditing(false);
            }}
            className="h-6 text-xs"
            autoFocus
          />
          <Button variant="ghost" size="sm" className="h-6 w-6 p-0" onClick={handleSave}>
            <Check className="h-3 w-3" />
          </Button>
          <Button variant="ghost" size="sm" className="h-6 w-6 p-0" onClick={() => setEditing(false)}>
            <X className="h-3 w-3" />
          </Button>
        </div>
      ) : (
        <>
          {conv.pinned && <Pin className="h-3 w-3 text-amber-500 shrink-0" />}
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-1.5">
              <span className="truncate font-medium text-xs">{conv.title}</span>
              {isActive && (
                <span className="h-1.5 w-1.5 rounded-full bg-emerald-500 animate-pulse shrink-0" />
              )}
            </div>
            <div className="flex items-center gap-2 text-[10px] text-muted-foreground">
              {conv.agent_id && (
                <span className="font-mono uppercase text-[9px] bg-muted/80 px-1 rounded">
                  {conv.agent_id.replace("case-orchestrator", "orchestrator")}
                </span>
              )}
              <span>{conv.messages.length} msgs</span>
            </div>
          </div>
          <div className="flex items-center gap-0.5 opacity-0 group-hover:opacity-100 transition-opacity">
            <Button
              variant="ghost"
              size="sm"
              className="h-6 w-6 p-0"
              onClick={(e) => {
                e.stopPropagation();
                onTogglePin();
              }}
            >
              {conv.pinned ? (
                <PinOff className="h-3 w-3" />
              ) : (
                <Pin className="h-3 w-3" />
              )}
            </Button>
            <Button
              variant="ghost"
              size="sm"
              className="h-6 w-6 p-0"
              onClick={(e) => {
                e.stopPropagation();
                setEditing(true);
              }}
            >
              <Pencil className="h-3 w-3" />
            </Button>
            <Button
              variant="ghost"
              size="sm"
              className="h-6 w-6 p-0 text-destructive hover:text-destructive"
              onClick={(e) => {
                e.stopPropagation();
                onDelete();
              }}
            >
              <Trash2 className="h-3 w-3" />
            </Button>
          </div>
        </>
      )}
    </div>
  );
}

export function ChatSidebar({ caseId }: { caseId?: string }) {
  const {
    conversations,
    activeConversationId,
    sidebarOpen,
    createConversation,
    setActiveConversation,
    deleteConversation,
    renameConversation,
    togglePinConversation,
    setSidebarOpen,
  } = useAIStore();

  const [searchQuery, setSearchQuery] = useState("");

  const filteredConversations = conversations.filter(
    (c) =>
      c.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      c.messages.some((m) =>
        m.content?.toLowerCase().includes(searchQuery.toLowerCase()),
      ),
  );

  const pinned = filteredConversations.filter((c) => c.pinned);
  const unpinned = filteredConversations
    .filter((c) => !c.pinned)
    .sort((a, b) => b.updated_at - a.updated_at);

  if (!sidebarOpen) {
    return (
      <div className="w-10 border-r flex flex-col items-center py-2 gap-2">
        <Button
          variant="ghost"
          size="sm"
          className="h-8 w-8 p-0"
          onClick={() => setSidebarOpen(true)}
        >
          <MessageSquare className="h-4 w-4" />
        </Button>
        <Button
          variant="ghost"
          size="sm"
          className="h-8 w-8 p-0"
          onClick={() => createConversation(caseId)}
        >
          <Plus className="h-4 w-4" />
        </Button>
      </div>
    );
  }

  return (
    <div className="w-64 border-r flex flex-col">
      <div className="flex items-center justify-between p-3 border-b">
        <h3 className="text-sm font-semibold">Conversations</h3>
        <div className="flex items-center gap-1">
          <Button
            variant="ghost"
            size="sm"
            className="h-7 w-7 p-0"
            onClick={() => createConversation(caseId)}
          >
            <Plus className="h-4 w-4" />
          </Button>
          <Button
            variant="ghost"
            size="sm"
            className="h-7 w-7 p-0"
            onClick={() => setSidebarOpen(false)}
          >
            <ChevronLeft className="h-4 w-4" />
          </Button>
        </div>
      </div>

      <div className="p-2">
        <div className="relative">
          <Search className="absolute left-2 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-muted-foreground" />
          <Input
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search conversations..."
            className="h-8 pl-7 text-xs"
          />
        </div>
      </div>

      <ScrollArea className="flex-1">
        <div className="p-2 space-y-1">
          {pinned.length > 0 && (
            <>
              <div className="text-[10px] text-muted-foreground font-medium px-2 py-1">
                Pinned
              </div>
              {pinned.map((c) => (
                <ConversationItem
                  key={c.id}
                  conv={c}
                  isActive={c.id === activeConversationId}
                  onSelect={() => setActiveConversation(c.id)}
                  onDelete={() => deleteConversation(c.id)}
                  onRename={(t) => renameConversation(c.id, t)}
                  onTogglePin={() => togglePinConversation(c.id)}
                />
              ))}
            </>
          )}

          {unpinned.length > 0 && (
            <>
              {pinned.length > 0 && (
                <div className="text-[10px] text-muted-foreground font-medium px-2 py-1">
                  Recent
                </div>
              )}
              {unpinned.map((c) => (
                <ConversationItem
                  key={c.id}
                  conv={c}
                  isActive={c.id === activeConversationId}
                  onSelect={() => setActiveConversation(c.id)}
                  onDelete={() => deleteConversation(c.id)}
                  onRename={(t) => renameConversation(c.id, t)}
                  onTogglePin={() => togglePinConversation(c.id)}
                />
              ))}
            </>
          )}

          {filteredConversations.length === 0 && (
            <div className="text-center py-8">
              <MessageSquare className="h-8 w-8 mx-auto text-muted-foreground/30 mb-2" />
              <p className="text-xs text-muted-foreground">
                {searchQuery ? "No matching conversations" : "No conversations yet"}
              </p>
            </div>
          )}
        </div>
      </ScrollArea>
    </div>
  );
}
