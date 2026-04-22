/**
 * DocumentChat — RAG-powered PDF chatbot with source citations.
 * Developed by Marino ATOHOUN.
 */

import { useEffect, useRef, useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Loader2, Send, BookOpen, ChevronDown, ChevronUp, Sparkles } from 'lucide-react';
import { documentsAPI } from '../lib/api';
import { useAuth } from '../hooks/useAuth';

// ─── Markdown renderer (no dependency) ────────────────────────────────────────
/**
 * Convert a simple Markdown string to JSX.
 * Supports: **bold**, *italic*, `code`, ## headings, - lists, (p. X) citations.
 */
function renderMarkdown(text) {
  if (!text) return null;

  const lines = text.split('\n');
  const elements = [];
  let key = 0;
  let listBuffer = [];

  const flushList = () => {
    if (listBuffer.length === 0) return;
    elements.push(
      <ul key={key++} className="list-disc list-inside space-y-1 my-2 ml-2">
        {listBuffer.map((item, i) => (
          <li key={i} className="text-sm leading-relaxed">{inlineMarkdown(item)}</li>
        ))}
      </ul>
    );
    listBuffer = [];
  };

  for (const raw of lines) {
    const line = raw.trimEnd();

    // Heading ##
    const hMatch = line.match(/^(#{1,4})\s+(.+)/);
    if (hMatch) {
      flushList();
      const level = hMatch[1].length;
      const sizeClass = level === 1 ? 'text-base font-bold' : level === 2 ? 'text-sm font-bold' : 'text-sm font-semibold';
      elements.push(
        <p key={key++} className={`${sizeClass} mt-3 mb-1`}>{inlineMarkdown(hMatch[2])}</p>
      );
      continue;
    }

    // Horizontal rule ---
    if (/^-{3,}$/.test(line.trim())) {
      flushList();
      elements.push(<hr key={key++} className="my-2 border-border" />);
      continue;
    }

    // List item
    const listMatch = line.match(/^[\-\*]\s+(.*)/);
    if (listMatch) {
      listBuffer.push(listMatch[1]);
      continue;
    }

    // Numbered list
    const numMatch = line.match(/^\d+\.\s+(.*)/);
    if (numMatch) {
      listBuffer.push(numMatch[1]);
      continue;
    }

    flushList();

    if (line.trim() === '') {
      elements.push(<br key={key++} />);
    } else {
      elements.push(
        <p key={key++} className="text-sm leading-relaxed my-0.5">{inlineMarkdown(line)}</p>
      );
    }
  }
  flushList();
  return elements;
}

function inlineMarkdown(text) {
  // Parse inline: **bold**, *italic*, `code`, (p. X)
  const parts = [];
  const regex = /(\*\*(.+?)\*\*|\*(.+?)\*|`([^`]+)`|\(p\.\s*\d+(?:\s*[-,]\s*\d+)*\))/g;
  let last = 0;
  let m;
  let k = 0;

  while ((m = regex.exec(text)) !== null) {
    if (m.index > last) {
      parts.push(text.slice(last, m.index));
    }
    const match = m[0];
    if (match.startsWith('**')) {
      parts.push(<strong key={k++}>{m[2]}</strong>);
    } else if (match.startsWith('*')) {
      parts.push(<em key={k++}>{m[3]}</em>);
    } else if (match.startsWith('`')) {
      parts.push(
        <code key={k++} className="bg-muted px-1 py-0.5 rounded text-xs font-mono">
          {m[4]}
        </code>
      );
    } else if (match.startsWith('(p.')) {
      // Page citation — highlight it
      parts.push(
        <span key={k++} className="inline-flex items-center gap-0.5 bg-primary/10 text-primary px-1.5 py-0.5 rounded text-xs font-medium">
          <BookOpen className="h-3 w-3" />
          {match}
        </span>
      );
    }
    last = m.index + match.length;
  }
  if (last < text.length) parts.push(text.slice(last));
  return parts.length ? parts : text;
}

// ─── Source citation card ─────────────────────────────────────────────────────
function SourceCard({ source }) {
  const [expanded, setExpanded] = useState(false);
  return (
    <div className="rounded-lg border border-primary/20 bg-primary/5 overflow-hidden">
      <button
        onClick={() => setExpanded((v) => !v)}
        className="w-full flex items-center justify-between gap-2 px-3 py-2 text-left hover:bg-primary/10 transition-colors"
      >
        <div className="flex items-center gap-2 min-w-0">
          <BookOpen className="h-3.5 w-3.5 text-primary shrink-0" />
          <span className="text-xs font-semibold text-primary">Page {source.page}</span>
        </div>
        {expanded
          ? <ChevronUp className="h-3 w-3 text-primary shrink-0" />
          : <ChevronDown className="h-3 w-3 text-primary shrink-0" />}
      </button>
      {expanded && (
        <div className="px-3 pb-3">
          <p className="text-xs text-muted-foreground leading-relaxed italic border-l-2 border-primary/30 pl-2">
            « {source.excerpt} »
          </p>
        </div>
      )}
    </div>
  );
}

// ─── Source citations panel ───────────────────────────────────────────────────
function SourcesPanel({ sources }) {
  if (!sources || sources.length === 0) return null;
  // Deduplicate by page
  const unique = sources.filter(
    (s, i, arr) => arr.findIndex((x) => x.page === s.page) === i
  );
  return (
    <div className="mt-2 space-y-1.5">
      <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wide flex items-center gap-1.5">
        <BookOpen className="h-3 w-3" />
        Sources utilisées ({unique.length} page{unique.length > 1 ? 's' : ''})
      </p>
      {unique.map((src) => (
        <SourceCard key={`${src.page}-${src.chunk_id}`} source={src} />
      ))}
    </div>
  );
}

// ─── Message bubble ───────────────────────────────────────────────────────────
function MessageBubble({ message }) {
  const isUser = message.role === 'user';
  return (
    <div className={`flex flex-col ${isUser ? 'items-end' : 'items-start'} gap-1`}>
      <div
        className={`max-w-[90%] rounded-xl px-3 py-2.5 ${
          isUser
            ? 'bg-primary text-primary-foreground rounded-br-sm'
            : 'bg-muted text-foreground rounded-bl-sm'
        }`}
      >
        {isUser
          ? <p className="text-sm whitespace-pre-wrap">{message.content}</p>
          : renderMarkdown(message.content)
        }
      </div>
      {/* Show sources below AI messages */}
      {!isUser && message.sources && message.sources.length > 0 && (
        <div className="max-w-[90%] w-full">
          <SourcesPanel sources={message.sources} />
        </div>
      )}
    </div>
  );
}

// ─── Suggestions ─────────────────────────────────────────────────────────────
const DEFAULT_SUGGESTIONS = [
  "Résume le document en 5 points clés.",
  "Explique les définitions importantes.",
  "Donne les formules avec leurs explications.",
  "Propose 5 questions d'examen + corrigé.",
  "Quelles sont les conclusions principales ?",
  "Explique le concept le plus complexe.",
];

// ─── Main component ───────────────────────────────────────────────────────────
const DocumentChat = ({
  documentId,
  documentTitle = '',
  suggestions = DEFAULT_SUGGESTIONS,
  className = '',
}) => {
  const { isAuthenticated } = useAuth();
  const bottomRef = useRef(null);
  const inputRef = useRef(null);

  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content:
        "Bonjour ! Je suis votre assistant IA pour ce document.\n\n" +
        "Je peux répondre à vos questions en m'appuyant sur les passages précis du PDF et en vous citant les pages sources.\n\n" +
        "Que voulez-vous savoir ?",
      sources: [],
    },
  ]);
  const [draft, setDraft] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [errorDebug, setErrorDebug] = useState('');
  const [lastModel, setLastModel] = useState('');

  // Scroll to bottom when messages change
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  // Typeset math (MathJax loaded globally in index.html)
  useEffect(() => {
    const mj = window.MathJax;
    if (mj?.typesetPromise) {
      mj.typesetPromise().catch(() => {});
    }
  }, [messages]);

  // Reset on document change
  useEffect(() => {
    setMessages([
      {
        role: 'assistant',
        content:
          "Bonjour ! Je suis votre assistant IA pour ce document.\n\n" +
          "Je peux répondre à vos questions en m'appuyant sur les passages précis du PDF et en vous citant les pages sources.\n\n" +
          "Que voulez-vous savoir ?",
        sources: [],
      },
    ]);
    setDraft('');
    setError('');
    setErrorDebug('');
    setLastModel('');
  }, [documentId]);

  const send = async (text = draft) => {
    const trimmed = text.trim();
    if (!trimmed || loading) return;
    setError('');
    setErrorDebug('');
    setLoading(true);

    const userMsg = { role: 'user', content: trimmed, sources: [] };
    const nextMessages = [...messages, userMsg];
    setMessages(nextMessages);
    setDraft('');
    inputRef.current?.focus();

    try {
      const history = nextMessages
        .filter((m) => m.role === 'user' || m.role === 'assistant')
        .slice(-10)
        .map((m) => ({ role: m.role, content: m.content }));

      const res = await documentsAPI.chat(documentId, trimmed, history);

      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: res.answer || '',
          sources: Array.isArray(res.sources) ? res.sources : [],
        },
      ]);
      setLastModel(res.model || '');
    } catch (e) {
      setError(e?.response?.data?.detail || "Impossible d'obtenir une réponse.");
      setErrorDebug(e?.response?.data?.error || '');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card className={`h-full flex flex-col overflow-hidden ${className}`}>
      {/* Header */}
      <CardHeader className="pb-3 shrink-0">
        <div className="flex items-start justify-between gap-3">
          <div className="space-y-0.5 min-w-0">
            <CardTitle className="flex items-center gap-2 text-base">
              <Sparkles className="h-4 w-4 text-primary" />
              Assistant IA
              <Badge variant="secondary" className="text-xs">RAG</Badge>
            </CardTitle>
            {documentTitle && (
              <p className="text-xs text-muted-foreground line-clamp-1">
                {documentTitle}
              </p>
            )}
          </div>
          {lastModel && (
            <Badge variant="outline" className="shrink-0 text-xs font-mono">
              {lastModel.split('/').pop()}
            </Badge>
          )}
        </div>
      </CardHeader>

      <CardContent className="flex-1 min-h-0 flex flex-col gap-3 pt-0">
        {/* Not authenticated alert */}
        {!isAuthenticated && (
          <Alert>
            <AlertDescription className="text-sm">
              Connecte-toi pour utiliser l'assistant IA.
            </AlertDescription>
          </Alert>
        )}

        {/* Error */}
        {error && (
          <Alert variant="destructive">
            <AlertDescription>
              <div className="space-y-1">
                <div className="text-sm">{error}</div>
                {errorDebug && (
                  <div className="text-xs opacity-75 break-words">{errorDebug}</div>
                )}
              </div>
            </AlertDescription>
          </Alert>
        )}

        {/* Messages */}
        <div className="flex-1 min-h-0 overflow-y-auto rounded-lg border bg-background p-3 space-y-4 scroll-smooth">
          {messages.map((m, idx) => (
            <MessageBubble key={idx} message={m} />
          ))}

          {/* Typing indicator */}
          {loading && (
            <div className="flex items-start gap-2">
              <div className="bg-muted rounded-xl rounded-bl-sm px-3 py-2.5 flex items-center gap-2">
                <Loader2 className="h-3.5 w-3.5 animate-spin text-muted-foreground" />
                <span className="text-xs text-muted-foreground">Analyse du document en cours…</span>
              </div>
            </div>
          )}
          <div ref={bottomRef} />
        </div>

        {/* Suggestions */}
        {isAuthenticated && suggestions.length > 0 && messages.length <= 1 && (
          <div className="flex flex-wrap gap-1.5 shrink-0">
            {suggestions.slice(0, 4).map((s) => (
              <Button
                key={s}
                type="button"
                variant="outline"
                size="sm"
                className="h-7 text-xs"
                disabled={loading}
                onClick={() => send(s)}
              >
                {s}
              </Button>
            ))}
          </div>
        )}

        {/* Input */}
        <div className="flex gap-2 shrink-0">
          <Input
            ref={inputRef}
            value={draft}
            onChange={(e) => setDraft(e.target.value)}
            placeholder="Posez votre question sur ce document…"
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                if (isAuthenticated) send();
              }
            }}
            disabled={!isAuthenticated || loading}
            className="text-sm"
          />
          <Button
            onClick={() => send()}
            disabled={!isAuthenticated || loading || !draft.trim()}
            size="icon"
            className="shrink-0"
          >
            {loading
              ? <Loader2 className="h-4 w-4 animate-spin" />
              : <Send className="h-4 w-4" />
            }
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};

export default DocumentChat;
