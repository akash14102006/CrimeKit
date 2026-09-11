"use client";

import { useState, useCallback } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  Bookmark,
  Pin,
  PinOff,
  Trash2,
  Play,
  Plus,
  Search,
} from "lucide-react";
import { useSearchStore } from "../store/searchStore";

export function SavedSearches() {
  const {
    savedSearches,
    loadSavedSearch,
    deleteSavedSearch,
    togglePinSavedSearch,
  } = useSearchStore();
  const [showSave, setShowSave] = useState(false);
  const [saveName, setSaveName] = useState("");
  const { saveSearch, query } = useSearchStore();

  const handleSave = useCallback(() => {
    if (saveName.trim() && query.trim()) {
      saveSearch(saveName.trim());
      setSaveName("");
      setShowSave(false);
    }
  }, [saveName, query, saveSearch]);

  const pinned = savedSearches.filter((s) => s.pinned);
  const unpinned = savedSearches.filter((s) => !s.pinned);

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Bookmark className="h-3.5 w-3.5 text-muted-foreground" />
          <span className="text-xs font-medium">Saved Searches</span>
          {savedSearches.length > 0 && (
            <Badge variant="secondary" className="text-[10px]">
              {savedSearches.length}
            </Badge>
          )}
        </div>
        {query.trim() && (
          <Button
            variant="ghost"
            size="sm"
            className="h-6 text-[10px] gap-1"
            onClick={() => setShowSave(!showSave)}
          >
            <Plus className="h-2.5 w-2.5" />
            Save
          </Button>
        )}
      </div>

      {showSave && (
        <div className="flex items-center gap-2">
          <Input
            value={saveName}
            onChange={(e) => setSaveName(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSave()}
            placeholder="Search name..."
            className="h-7 text-xs flex-1"
            autoFocus
          />
          <Button size="sm" className="h-7 text-xs" onClick={handleSave}>
            Save
          </Button>
          <Button
            variant="ghost"
            size="sm"
            className="h-7 text-xs"
            onClick={() => setShowSave(false)}
          >
            Cancel
          </Button>
        </div>
      )}

      <ScrollArea className="max-h-[300px]">
        <div className="space-y-1">
          {pinned.length > 0 && (
            <>
              <div className="text-[10px] text-muted-foreground font-medium px-1">
                Pinned
              </div>
              {pinned.map((ss) => (
                <SavedSearchItem
                  key={ss.id}
                  search={ss}
                  onRun={() => loadSavedSearch(ss.id)}
                  onDelete={() => deleteSavedSearch(ss.id)}
                  onTogglePin={() => togglePinSavedSearch(ss.id)}
                />
              ))}
            </>
          )}

          {unpinned.length > 0 && (
            <>
              {pinned.length > 0 && (
                <div className="text-[10px] text-muted-foreground font-medium px-1 mt-2">
                  All
                </div>
              )}
              {unpinned.map((ss) => (
                <SavedSearchItem
                  key={ss.id}
                  search={ss}
                  onRun={() => loadSavedSearch(ss.id)}
                  onDelete={() => deleteSavedSearch(ss.id)}
                  onTogglePin={() => togglePinSavedSearch(ss.id)}
                />
              ))}
            </>
          )}

          {savedSearches.length === 0 && (
            <div className="text-center py-6">
              <Bookmark className="h-6 w-6 mx-auto text-muted-foreground/30 mb-2" />
              <p className="text-[10px] text-muted-foreground">
                No saved searches. Search and save for quick access.
              </p>
            </div>
          )}
        </div>
      </ScrollArea>
    </div>
  );
}

function SavedSearchItem({
  search,
  onRun,
  onDelete,
  onTogglePin,
}: {
  search: { id: string; name: string; query: string; mode: string; pinned: boolean };
  onRun: () => void;
  onDelete: () => void;
  onTogglePin: () => void;
}) {
  return (
    <div className="group flex items-center gap-2 p-2 rounded-md hover:bg-muted/50 transition-colors">
      <Search className="h-3 w-3 text-muted-foreground shrink-0" />
      <div className="flex-1 min-w-0">
        <div className="text-xs font-medium truncate">{search.name}</div>
        <div className="text-[10px] text-muted-foreground truncate">
          {search.query}
        </div>
      </div>
      <div className="flex items-center gap-0.5 opacity-0 group-hover:opacity-100 transition-opacity">
        <Button variant="ghost" size="sm" className="h-5 w-5 p-0" onClick={onRun}>
          <Play className="h-2.5 w-2.5" />
        </Button>
        <Button variant="ghost" size="sm" className="h-5 w-5 p-0" onClick={onTogglePin}>
          {search.pinned ? <PinOff className="h-2.5 w-2.5" /> : <Pin className="h-2.5 w-2.5" />}
        </Button>
        <Button
          variant="ghost"
          size="sm"
          className="h-5 w-5 p-0 text-destructive"
          onClick={onDelete}
        >
          <Trash2 className="h-2.5 w-2.5" />
        </Button>
      </div>
    </div>
  );
}
