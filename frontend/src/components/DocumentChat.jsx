/**
 * DocumentChat
 * Chat UI to question a PDF document (backend RAG + Groq).
 */

import { useEffect, useRef, useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Loader2, Send } from 'lucide-react';
import { documentsAPI } from '../lib/api';
import { useAuth } from '../hooks/useAuth';

const DEFAULT_SUGGESTIONS = [
  "Résume le document en 5 points.",
  "Explique les définitions clés.",
  "Donne les formules importantes avec explication.",
  "Propose 5 questions d'examen + corrigé.",
];

const DocumentChat = ({ documentId, documentTitle = '', suggestions = DEFAULT_SUGGESTIONS, className = '' }) => {
  const { isAuthenticated } = useAuth();
  const containerRef = useRef(null);
  const [messages, setMessages] = useState([
    { role: 'assistant', content: "Pose-moi une question sur ce document. Je réponds avec le contexte du PDF." },
  ]);
  const [draft, setDraft] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [errorDebug, setErrorDebug] = useState('');
  const [lastModel, setLastModel] = useState('');

  useEffect(() => {
    // Typeset math in this container (MathJax loaded globally in index.html).
    const mj = window.MathJax;
    if (mj?.typesetPromise && containerRef.current) {
      mj.typesetPromise([containerRef.current]).catch(() => {});
    }
  }, [messages]);

  useEffect(() => {
    // Reset when switching documents
    setMessages([
      { role: 'assistant', content: "Pose-moi une question sur ce document. Je réponds avec le contexte du PDF." },
    ]);
    setDraft('');
    setError('');
    setErrorDebug('');
    setLastModel('');
  }, [documentId]);

  const send = async () => {
    const text = draft.trim();
    if (!text || loading) return;
    setError('');
    setErrorDebug('');
    setLoading(true);

    const nextMessages = [...messages, { role: 'user', content: text }];
    setMessages(nextMessages);
    setDraft('');

    try {
      const history = nextMessages
        .filter((m) => m.role === 'user' || m.role === 'assistant')
        .slice(-10)
        .map((m) => ({ role: m.role, content: m.content }));

      const res = await documentsAPI.chat(documentId, text, history);
      setMessages((prev) => [...prev, { role: 'assistant', content: res.answer || '' }]);
      setLastModel(res.model || '');
    } catch (e) {
      setError(e?.response?.data?.detail || "Impossible d'obtenir une réponse.");
      setErrorDebug(e?.response?.data?.error || '');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card className={`h-full flex flex-col ${className}`}>
      <CardHeader>
        <div className="flex items-start justify-between gap-3">
          <div className="space-y-1">
            <CardTitle className="flex items-center gap-2">
              Assistant IA <Badge variant="secondary">Beta</Badge>
            </CardTitle>
            {documentTitle && (
              <p className="text-sm text-muted-foreground line-clamp-1">
                Pour: {documentTitle}
              </p>
            )}
          </div>
          {lastModel && (
            <Badge variant="outline" className="shrink-0">
              {lastModel}
            </Badge>
          )}
        </div>
      </CardHeader>
      <CardContent className="flex-1 min-h-0 flex flex-col gap-4">
        {!isAuthenticated && (
          <Alert>
            <AlertDescription>
              Connecte-toi pour utiliser le chat IA.
            </AlertDescription>
          </Alert>
        )}

        {error && (
          <Alert variant="destructive">
            <AlertDescription>
              <div className="space-y-1">
                <div>{error}</div>
                {errorDebug && (
                  <div className="text-xs opacity-80 break-words">
                    {errorDebug}
                  </div>
                )}
              </div>
            </AlertDescription>
          </Alert>
        )}

        <div
          ref={containerRef}
          className="flex-1 min-h-0 overflow-y-auto rounded-md border bg-background p-3 space-y-3"
        >
          {messages.map((m, idx) => (
            <div
              key={idx}
              className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[85%] rounded-lg px-3 py-2 text-sm whitespace-pre-wrap ${
                  m.role === 'user'
                    ? 'bg-primary text-primary-foreground'
                    : 'bg-muted text-foreground'
                }`}
              >
                {m.content}
              </div>
            </div>
          ))}
        </div>

        {isAuthenticated && Array.isArray(suggestions) && suggestions.length > 0 && (
          <div className="flex flex-wrap gap-2">
            {suggestions.slice(0, 6).map((s) => (
              <Button
                key={s}
                type="button"
                variant="secondary"
                size="sm"
                className="h-8"
                disabled={loading}
                onClick={() => {
                  setDraft(s);
                }}
              >
                {s}
              </Button>
            ))}
          </div>
        )}

        <div className="flex gap-2">
          <Input
            value={draft}
            onChange={(e) => setDraft(e.target.value)}
            placeholder="Ex: Résume le chapitre 2 et donne les formules importantes…"
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                if (isAuthenticated) send();
              }
            }}
            disabled={!isAuthenticated || loading}
          />
          <Button onClick={send} disabled={!isAuthenticated || loading || !draft.trim()}>
            {loading ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <>
                <Send className="h-4 w-4 mr-2" />
                Envoyer
              </>
            )}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};

export default DocumentChat;
