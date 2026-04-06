/**
 * Developer API Page
 * API plans + API key management + documentation.
 */

import { useEffect, useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Separator } from '@/components/ui/separator';
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from '@/components/ui/accordion';
import { Copy, KeyRound, RefreshCw, Terminal } from 'lucide-react';
import { developerAPI } from '../lib/api';
import { useAuth } from '../hooks/useAuth';
import { useToast } from '../hooks/use-toast';

const DeveloperApiPage = () => {
  const { isAuthenticated } = useAuth();
  const { toast } = useToast();

  const [keys, setKeys] = useState([]);
  const [keysLoading, setKeysLoading] = useState(false);

  const [newKeyName, setNewKeyName] = useState('');
  const [createdKey, setCreatedKey] = useState(null);

  const fetchDevData = async () => {
    if (!isAuthenticated) return;
    setKeysLoading(true);
    try {
      const keysData = await developerAPI.listApiKeys();
      setKeys(Array.isArray(keysData) ? keysData : []);
    } catch {
      // ignore
    } finally {
      setKeysLoading(false);
    }
  };

  useEffect(() => {
    fetchDevData();
  }, [isAuthenticated]);

  const handleCreateKey = async () => {
    try {
      const data = await developerAPI.createApiKey(newKeyName);
      setCreatedKey(data);
      setNewKeyName('');
      await fetchDevData();
      toast({ title: 'Clé créée', description: 'Copie la clé maintenant (elle ne sera plus affichée).' });
    } catch {
      toast({ title: 'Erreur', description: 'Impossible de créer la clé.', variant: 'destructive' });
    }
  };

  const handleRevoke = async (id) => {
    try {
      await developerAPI.revokeApiKey(id);
      await fetchDevData();
      toast({ title: 'Clé révoquée' });
    } catch {
      toast({ title: 'Erreur', description: 'Impossible de révoquer la clé.', variant: 'destructive' });
    }
  };

  const copy = async (text) => {
    try {
      await navigator.clipboard.writeText(text);
      toast({ title: 'Copié', description: 'Collé dans le presse-papier.' });
    } catch {
      toast({ title: 'Erreur', description: 'Impossible de copier.', variant: 'destructive' });
    }
  };

  const CodeBlock = ({ children }) => (
    <pre className="rounded-md bg-muted p-3 overflow-x-auto text-xs leading-relaxed">
      <code className="whitespace-pre">{children}</code>
    </pre>
  );

  return (
    <div className="max-w-5xl mx-auto space-y-8">
      <div className="space-y-2">
        <h1 className="text-3xl font-bold flex items-center gap-2">
          <Terminal className="h-6 w-6" />
          API EduShare (Développeurs)
        </h1>
        <p className="text-muted-foreground">
          Accède à la base de cours via une API Key, avec des quotas selon ton offre.
        </p>
        <div className="flex flex-wrap gap-2">
          <Badge variant="secondary">Docs + API keys</Badge>
          <Button asChild variant="outline" size="sm">
            <a href="/pricing">Voir les tarifs</a>
          </Button>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <KeyRound className="h-5 w-5" />
            API Keys
          </CardTitle>
          <CardDescription>
            {isAuthenticated ? 'Crée et révoque tes clés API.' : 'Connecte-toi pour générer une API key.'}
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {isAuthenticated && (
            <>
              {createdKey && (
                <Alert>
                  <AlertDescription className="space-y-2">
                    <div className="font-medium">Ta nouvelle clé (affichée une seule fois) :</div>
                    <div className="flex items-center gap-2">
                      <code className="text-xs break-all">{createdKey.api_key}</code>
                      <Button size="sm" variant="outline" onClick={() => copy(createdKey.api_key)}>
                        <Copy className="h-4 w-4 mr-2" />
                        Copier
                      </Button>
                    </div>
                  </AlertDescription>
                </Alert>
              )}

              <div className="flex flex-col md:flex-row gap-2">
                <Input
                  value={newKeyName}
                  onChange={(e) => setNewKeyName(e.target.value)}
                  placeholder="Nom de la clé (ex: script-recherche)"
                />
                <Button onClick={handleCreateKey}>Créer une clé</Button>
                <Button variant="outline" onClick={fetchDevData} disabled={keysLoading}>
                  <RefreshCw className="h-4 w-4 mr-2" />
                  Rafraîchir
                </Button>
              </div>
            </>
          )}

          {isAuthenticated && (
            <div className="space-y-2">
              {keysLoading ? (
                <p className="text-sm text-muted-foreground">Chargement…</p>
              ) : keys.length ? (
                keys.map((k) => (
                  <div key={k.id} className="flex items-center justify-between border rounded-md p-3">
                    <div className="space-y-1">
                      <div className="flex items-center gap-2">
                        <Badge variant={k.is_active ? 'secondary' : 'outline'}>
                          {k.is_active ? 'Active' : 'Révoquée'}
                        </Badge>
                        <span className="font-medium">{k.name || '(sans nom)'}</span>
                      </div>
                      <div className="text-sm text-muted-foreground">Préfixe: {k.prefix}</div>
                    </div>
                    <div className="flex gap-2">
                      {k.is_active && (
                        <Button variant="destructive" size="sm" onClick={() => handleRevoke(k.id)}>
                          Révoquer
                        </Button>
                      )}
                    </div>
                  </div>
                ))
              ) : (
                <p className="text-sm text-muted-foreground">Aucune clé pour l’instant.</p>
              )}
            </div>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Documentation API</CardTitle>
          <CardDescription>Exemples d’usage (curl, Python, Node.js, PHP, Go). API key requise.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6 text-sm">
          <div className="space-y-2">
            <div className="font-medium">Base URL</div>
            <p className="text-muted-foreground">
              En production, utilise ton domaine (ex: <code>https://edushare.com</code>). En local : <code>http://127.0.0.1:8000</code>.
            </p>
          </div>

          <div className="space-y-2">
            <div className="font-medium">Authentification</div>
            <p className="text-muted-foreground">Ajoute la clé via le header HTTP :</p>
            <div className="flex items-start gap-2">
              <div className="flex-1">
                <CodeBlock>{`X-API-Key: <TON_API_KEY>\n# Exemple: edush_xxx.yyy`}</CodeBlock>
              </div>
              <Button size="sm" variant="outline" onClick={() => copy('X-API-Key: <TON_API_KEY>')}>
                <Copy className="h-4 w-4 mr-2" />
                Copier
              </Button>
            </div>
            <p className="text-xs text-muted-foreground">
              Mets uniquement <code>edush_xxx.yyy</code> (pas de <code>apikey=</code>).
            </p>
          </div>

          <div className="space-y-2">
            <div className="font-medium">Endpoints</div>
            <CodeBlock>{`GET  /api/data/whoami/                       # statut clé + quotas\nGET  /api/data/documents/                    # liste paginée\nGET  /api/data/documents/{encrypted_id}/download/  # télécharge le PDF`}</CodeBlock>
          </div>

          <Accordion type="multiple" className="w-full">
            <AccordionItem value="curl">
              <AccordionTrigger>Exemples curl</AccordionTrigger>
              <AccordionContent className="space-y-3">
                <CodeBlock>{`# 1) Vérifier la clé + quotas\ncurl -s -H "X-API-Key: <TON_API_KEY>" "http://127.0.0.1:8000/api/data/whoami/" | jq\n\n# 2) Liste (paginée) + filtres\ncurl -s -H "X-API-Key: <TON_API_KEY>" \\\n  "http://127.0.0.1:8000/api/data/documents/?page_size=50&search=python&domain=informatique&tag=python"\n\n# 3) Télécharger (évite d’écrire une erreur JSON dans un .pdf)\ncurl -fL -H "X-API-Key: <TON_API_KEY>" \\\n  "http://127.0.0.1:8000/api/data/documents/<encrypted_id>/download/" -o cours.pdf`}</CodeBlock>
              </AccordionContent>
            </AccordionItem>

	            <AccordionItem value="python">
	              <AccordionTrigger>Python (requests)</AccordionTrigger>
	              <AccordionContent className="space-y-3">
	                <CodeBlock>{`import requests\n\nBASE_URL = "https://ton-domaine.com"  # ou http://127.0.0.1:8000\nAPI_KEY = "<TON_API_KEY>"\n\nheaders = {"X-API-Key": API_KEY}\n\n# whoami\nr = requests.get(f"{BASE_URL}/api/data/whoami/", headers=headers, timeout=30)\nr.raise_for_status()\nprint(r.json())\n\n# list documents\nparams = {"search": "python", "page_size": 50}\nr = requests.get(f"{BASE_URL}/api/data/documents/", headers=headers, params=params, timeout=30)\nr.raise_for_status()\ndata = r.json()\nfor doc in data["results"]:\n    print(doc["encrypted_id"], doc["title"], doc["download_url"])\n\n# download first doc\ndoc = data["results"][0]\nurl = doc["download_url"]\nwith requests.get(url, headers=headers, stream=True, timeout=60) as resp:\n    resp.raise_for_status()\n    with open("cours.pdf", "wb") as f:\n        for chunk in resp.iter_content(chunk_size=1024 * 64):\n            if chunk:\n                f.write(chunk)`}</CodeBlock>
	              </AccordionContent>
	            </AccordionItem>

	            <AccordionItem value="node">
	              <AccordionTrigger>Node.js (fetch)</AccordionTrigger>
	              <AccordionContent className="space-y-3">
	                <CodeBlock>{`import fs from "node:fs";\n\nconst BASE_URL = "https://ton-domaine.com"; // ou http://127.0.0.1:8000\nconst API_KEY = "<TON_API_KEY>";\n\nconst headers = { "X-API-Key": API_KEY };\n\n// list\nconst listRes = await fetch(\n  BASE_URL + "/api/data/documents/?page_size=50&search=python",\n  { headers }\n);\nif (!listRes.ok) throw new Error(await listRes.text());\nconst list = await listRes.json();\nconsole.log(list.count, list.results[0]);\n\n// download\nconst url = list.results[0].download_url;\nconst dlRes = await fetch(url, { headers });\nif (!dlRes.ok) throw new Error(await dlRes.text());\n\nconst file = fs.createWriteStream("cours.pdf");\nawait new Promise((resolve, reject) => {\n  dlRes.body.pipe(file);\n  dlRes.body.on("error", reject);\n  file.on("finish", resolve);\n});`}</CodeBlock>
	              </AccordionContent>
	            </AccordionItem>

	            <AccordionItem value="php">
	              <AccordionTrigger>PHP (cURL)</AccordionTrigger>
	              <AccordionContent className="space-y-3">
	                <CodeBlock>{`<?php\n$base = "https://ton-domaine.com"; // ou http://127.0.0.1:8000\n$apiKey = "<TON_API_KEY>";\n\nfunction getJson($url, $apiKey) {\n  $ch = curl_init($url);\n  curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);\n  curl_setopt($ch, CURLOPT_HTTPHEADER, ["X-API-Key: $apiKey"]);\n  $body = curl_exec($ch);\n  $status = curl_getinfo($ch, CURLINFO_HTTP_CODE);\n  curl_close($ch);\n  if ($status >= 400) throw new Exception($body);\n  return json_decode($body, true);\n}\n\n$list = getJson("$base/api/data/documents/?page_size=5", $apiKey);\n$doc = $list["results"][0];\n\n// download\n$fp = fopen("cours.pdf", "w");\n$ch = curl_init($doc["download_url"]);\ncurl_setopt($ch, CURLOPT_FILE, $fp);\ncurl_setopt($ch, CURLOPT_HTTPHEADER, ["X-API-Key: $apiKey"]);\n$status = curl_exec($ch);\ncurl_close($ch);\nfclose($fp);\n?>`}</CodeBlock>
	              </AccordionContent>
	            </AccordionItem>

	            <AccordionItem value="go">
	              <AccordionTrigger>Go (net/http)</AccordionTrigger>
	              <AccordionContent className="space-y-3">
	                <CodeBlock>{`package main\n\nimport (\n  "encoding/json"\n  "fmt"\n  "io"\n  "net/http"\n  "os"\n)\n\ntype ListResponse struct {\n  Count   int ` + "`json:\"count\"`" + `\n  Results []struct {\n    EncryptedID string ` + "`json:\"encrypted_id\"`" + `\n    Title       string ` + "`json:\"title\"`" + `\n    DownloadURL string ` + "`json:\"download_url\"`" + `\n  } ` + "`json:\"results\"`" + `\n}\n\nfunc main() {\n  base := "http://127.0.0.1:8000"\n  apiKey := "<TON_API_KEY>"\n\n  req, _ := http.NewRequest("GET", base+"/api/data/documents/?page_size=5", nil)\n  req.Header.Set("X-API-Key", apiKey)\n  res, err := http.DefaultClient.Do(req)\n  if err != nil { panic(err) }\n  defer res.Body.Close()\n  if res.StatusCode >= 400 {\n    b, _ := io.ReadAll(res.Body)\n    panic(string(b))\n  }\n\n  var list ListResponse\n  json.NewDecoder(res.Body).Decode(&list)\n  fmt.Println(list.Count, list.Results[0].Title)\n\n  dlReq, _ := http.NewRequest("GET", list.Results[0].DownloadURL, nil)\n  dlReq.Header.Set("X-API-Key", apiKey)\n  dlRes, err := http.DefaultClient.Do(dlReq)\n  if err != nil { panic(err) }\n  defer dlRes.Body.Close()\n  if dlRes.StatusCode >= 400 {\n    b, _ := io.ReadAll(dlRes.Body)\n    panic(string(b))\n  }\n\n  f, _ := os.Create("cours.pdf")\n  defer f.Close()\n  io.Copy(f, dlRes.Body)\n}`}</CodeBlock>
	              </AccordionContent>
	            </AccordionItem>
          </Accordion>

          <div className="space-y-2">
            <div className="font-medium">Codes d’erreur</div>
            <CodeBlock>{`401/403  Clé API invalide, révoquée ou sans offre\n429      Quota dépassé (requêtes ou téléchargements/jour)\n400      Paramètres invalides (ex: encrypted_id invalide)\n404      Document introuvable`}</CodeBlock>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default DeveloperApiPage;
