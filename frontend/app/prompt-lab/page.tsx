"use client"

import { useEffect, useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"

const API = "http://localhost:8000/api/prompt-lab"

type Prompt = {
  id: number
  name: string
  description: string | null
  created_at: string
}

type PromptVersion = {
  id: number
  prompt_id: number
  version_number: number
  content: string
  stage: string
  commit_message: string | null
  created_at: string
}

const STAGE_STYLE: Record<string, string> = {
  draft:      "text-zinc-400 border-zinc-700 bg-zinc-900",
  staging:    "text-amber-400 border-amber-800 bg-amber-950",
  production: "text-emerald-400 border-emerald-800 bg-emerald-950",
}

export default function PromptLabPage() {
  const [prompts, setPrompts]               = useState<Prompt[]>([])
  const [loading, setLoading]               = useState(true)
  const [selected, setSelected]             = useState<Prompt | null>(null)
  const [versions, setVersions]             = useState<PromptVersion[]>([])
  const [showCreate, setShowCreate]         = useState(false)
  const [newName, setNewName]               = useState("")
  const [newDesc, setNewDesc]               = useState("")
  const [newContent, setNewContent]         = useState("")
  const [newCommitMsg, setNewCommitMsg]     = useState("")
  const [committing, setCommitting]         = useState(false)

  function fetchPrompts() {
    fetch(`${API}/prompts`)
      .then(r => r.json())
      .then(data => { setPrompts(data); setLoading(false) })
  }

  function fetchVersions(id: number) {
    fetch(`${API}/prompts/${id}/versions`)
      .then(r => r.json())
      .then(setVersions)
  }

  useEffect(() => { fetchPrompts() }, [])

  function handleSelect(p: Prompt) {
    setSelected(p)
    fetchVersions(p.id)
  }

  function handleCreate() {
    if (!newName.trim()) return
    fetch(`${API}/prompts`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name: newName.trim(), description: newDesc }),
    })
      .then(r => r.json())
      .then(() => { fetchPrompts(); setShowCreate(false); setNewName(""); setNewDesc("") })
  }

  function handleCommit() {
    if (!selected || !newContent.trim()) return
    setCommitting(true)
    fetch(`${API}/prompts/${selected.id}/versions`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ content: newContent, commit_message: newCommitMsg }),
    })
      .then(r => r.json())
      .then(() => { fetchVersions(selected.id); setNewContent(""); setNewCommitMsg(""); setCommitting(false) })
  }

  function handlePromote(versionId: number, stage: string) {
    if (!selected) return
    fetch(`${API}/prompts/${selected.id}/versions/${versionId}/promote`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ stage }),
    })
      .then(r => r.json())
      .then(() => fetchVersions(selected.id))
  }

  return (
    <div className="flex h-screen overflow-hidden">

      {/* ── Left: prompt list ── */}
      <div className="w-64 border-r border-border flex flex-col bg-card/20 shrink-0">

        {/* Header */}
        <div className="px-4 py-3 border-b border-border flex items-center justify-between">
          <div>
            <p className="text-xs font-semibold text-foreground">Prompt Lab</p>
            <p className="text-[10px] text-muted-foreground">{prompts.length} prompts</p>
          </div>
          <button
            onClick={() => setShowCreate(!showCreate)}
            className="text-[10px] px-2 py-1 rounded border border-border text-muted-foreground hover:text-foreground hover:border-primary/50 hover:bg-primary/5 transition-all font-mono"
          >
            + new
          </button>
        </div>

        {/* Create form */}
        {showCreate && (
          <div className="p-3 border-b border-border bg-muted/20 flex flex-col gap-2">
            <Input
              value={newName}
              onChange={e => setNewName(e.target.value)}
              placeholder="prompt-name"
              className="h-7 text-xs font-mono bg-background/50 border-border"
              onKeyDown={e => e.key === "Enter" && handleCreate()}
            />
            <Input
              value={newDesc}
              onChange={e => setNewDesc(e.target.value)}
              placeholder="Description (optional)"
              className="h-7 text-xs bg-background/50 border-border"
            />
            <div className="flex gap-1.5">
              <Button size="sm" onClick={handleCreate} className="h-6 text-[10px] flex-1 bg-primary text-primary-foreground hover:bg-primary/90">
                Create
              </Button>
              <Button size="sm" variant="ghost" onClick={() => setShowCreate(false)} className="h-6 text-[10px]">
                Cancel
              </Button>
            </div>
          </div>
        )}

        {/* List */}
        <div className="flex-1 overflow-auto">
          {loading ? (
            <div className="p-4 text-[10px] text-muted-foreground font-mono animate-pulse">loading...</div>
          ) : prompts.length === 0 ? (
            <div className="p-4 text-[10px] text-muted-foreground">No prompts yet.</div>
          ) : (
            prompts.map(p => (
              <button
                key={p.id}
                onClick={() => handleSelect(p)}
                className={`w-full text-left px-4 py-3 border-b border-border/50 transition-all duration-100 group ${
                  selected?.id === p.id
                    ? "bg-primary/8 border-l-2 border-l-primary"
                    : "hover:bg-accent/50"
                }`}
              >
                <p className={`text-xs font-mono font-medium truncate ${selected?.id === p.id ? "text-primary" : "text-foreground"}`}>
                  {p.name}
                </p>
                {p.description && (
                  <p className="text-[10px] text-muted-foreground truncate mt-0.5">{p.description}</p>
                )}
                <p className="text-[9px] text-muted-foreground/50 mt-1 font-mono">
                  {new Date(p.created_at).toLocaleDateString()}
                </p>
              </button>
            ))
          )}
        </div>
      </div>

      {/* ── Right: versions panel ── */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {!selected ? (
          <div className="flex-1 flex flex-col items-center justify-center gap-3 text-muted-foreground">
            <div className="w-12 h-12 rounded-xl border border-border flex items-center justify-center text-xl opacity-30">✦</div>
            <p className="text-xs">Select a prompt to view versions</p>
          </div>
        ) : (
          <>
            {/* Prompt header */}
            <div className="px-6 py-4 border-b border-border flex items-center justify-between">
              <div>
                <div className="flex items-center gap-2">
                  <span className="text-[10px] text-muted-foreground font-mono">#{selected.id}</span>
                  <h2 className="text-sm font-semibold font-mono text-foreground">{selected.name}</h2>
                </div>
                {selected.description && (
                  <p className="text-[11px] text-muted-foreground mt-0.5">{selected.description}</p>
                )}
              </div>
              <div className="text-[10px] text-muted-foreground font-mono">{versions.length} versions</div>
            </div>

            <div className="flex-1 overflow-auto p-6 flex flex-col gap-5">

              {/* Commit new version */}
              <div className="rounded-lg border border-border bg-card/50 overflow-hidden">
                <div className="px-4 py-2.5 border-b border-border bg-muted/20 flex items-center gap-2">
                  <span className="text-[10px] text-primary font-mono font-semibold">+ commit version</span>
                </div>
                <div className="p-4 flex flex-col gap-3">
                  <Textarea
                    value={newContent}
                    onChange={e => setNewContent(e.target.value)}
                    placeholder={"You are a helpful assistant.\nAnswer the user's question: {{question}}"}
                    className="font-mono text-xs min-h-[90px] bg-background/50 border-border resize-none leading-relaxed"
                  />
                  <div className="flex gap-2 items-center">
                    <Input
                      value={newCommitMsg}
                      onChange={e => setNewCommitMsg(e.target.value)}
                      placeholder="Commit message..."
                      className="h-7 text-xs bg-background/50 border-border flex-1 font-mono"
                      onKeyDown={e => e.key === "Enter" && handleCommit()}
                    />
                    <Button
                      size="sm"
                      onClick={handleCommit}
                      disabled={committing || !newContent.trim()}
                      className="h-7 text-[10px] px-3 bg-primary text-primary-foreground hover:bg-primary/90 font-mono"
                    >
                      {committing ? "saving..." : "commit →"}
                    </Button>
                  </div>
                </div>
              </div>

              {/* Version history */}
              <div>
                <p className="text-[10px] font-mono text-muted-foreground uppercase tracking-widest mb-3">
                  — version history
                </p>
                {versions.length === 0 ? (
                  <p className="text-xs text-muted-foreground">No versions yet. Commit your first version above.</p>
                ) : (
                  <div className="flex flex-col gap-2.5">
                    {versions.map(v => (
                      <div key={v.id} className="rounded-lg border border-border bg-card/40 overflow-hidden group hover:border-border/80 transition-colors">
                        {/* Version bar */}
                        <div className="px-4 py-2 border-b border-border/50 flex items-center justify-between">
                          <div className="flex items-center gap-2.5">
                            <span className="text-[10px] font-mono text-muted-foreground">v{v.version_number}</span>
                            <span className={`text-[9px] font-mono px-1.5 py-0.5 rounded border ${STAGE_STYLE[v.stage] ?? STAGE_STYLE.draft}`}>
                              {v.stage}
                            </span>
                            {v.commit_message && (
                              <span className="text-[10px] text-muted-foreground/70 italic truncate max-w-[200px]">
                                "{v.commit_message}"
                              </span>
                            )}
                          </div>
                          {/* Promote buttons */}
                          <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                            {v.stage !== "staging" && (
                              <button
                                onClick={() => handlePromote(v.id, "staging")}
                                className="text-[9px] px-1.5 py-0.5 rounded border border-amber-800/50 text-amber-500 hover:bg-amber-950 transition-colors font-mono"
                              >
                                staging
                              </button>
                            )}
                            {v.stage !== "production" && (
                              <button
                                onClick={() => handlePromote(v.id, "production")}
                                className="text-[9px] px-1.5 py-0.5 rounded border border-emerald-800/50 text-emerald-500 hover:bg-emerald-950 transition-colors font-mono"
                              >
                                production
                              </button>
                            )}
                          </div>
                        </div>
                        {/* Content */}
                        <pre className="px-4 py-3 text-[11px] font-mono text-foreground/75 whitespace-pre-wrap leading-relaxed">
                          {v.content}
                        </pre>
                        <div className="px-4 py-1.5 border-t border-border/30">
                          <span className="text-[9px] text-muted-foreground/50 font-mono">
                            {new Date(v.created_at).toLocaleString()}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  )
}
