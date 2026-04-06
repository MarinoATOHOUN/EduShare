# EduShare API (Développeurs)

Cette documentation décrit l’API “Data” d’EduShare (extraction de cours en volume) et la gestion des API Keys.

## Base URL

- Production: `https://ton-domaine.com`
- Local: `http://127.0.0.1:8000`

Tous les endpoints ci-dessous sont préfixés par `/api`.

## Authentification (API Key)

Ajoute la clé via header HTTP :

```
X-API-Key: <TON_API_KEY>
```

La clé a la forme `edush_xxx.yyy` (ne pas ajouter `apikey=`).

## Quotas

Selon l’offre, un quota journalier s’applique :

- `daily_requests_limit`: nombre de requêtes/jour
- `daily_download_limit`: nombre de téléchargements/jour

Quand le quota est dépassé, l’API renvoie `429`.

## Endpoints

### Vérifier la clé / plan / quotas

`GET /api/data/whoami/`

Retourne le plan et les compteurs du jour.

### Lister des documents (paginé)

`GET /api/data/documents/`

Paramètres utiles :

- `page` (int)
- `page_size` (int) — plafonné par l’offre
- `search` (string)
- `domain` (string) — filtre sur `course_domain`
- `study_level` (id / key / name)
- `study_sublevel` (id / key / name)
- `tag` (key ou name)

Réponse (DRF pagination) :

- `count`, `next`, `previous`, `results[]`
- `results[].encrypted_id` et `results[].download_url`

### Télécharger un PDF

`GET /api/data/documents/{encrypted_id}/download/`

Ce endpoint compte dans le quota “downloads/jour”.

## Exemples

### curl

```bash
curl -s -H "X-API-Key: <TON_API_KEY>" "http://127.0.0.1:8000/api/data/whoami/"

curl -s -H "X-API-Key: <TON_API_KEY>" \
  "http://127.0.0.1:8000/api/data/documents/?page_size=50&search=python&domain=informatique&tag=python"

curl -fL -H "X-API-Key: <TON_API_KEY>" \
  "http://127.0.0.1:8000/api/data/documents/<encrypted_id>/download/" -o cours.pdf
```

### Python (requests)

```python
import requests

BASE_URL = "http://127.0.0.1:8000"
API_KEY = "<TON_API_KEY>"
headers = {"X-API-Key": API_KEY}

r = requests.get(f"{BASE_URL}/api/data/whoami/", headers=headers, timeout=30)
r.raise_for_status()
print(r.json())

params = {"page_size": 50, "search": "python"}
r = requests.get(f"{BASE_URL}/api/data/documents/", headers=headers, params=params, timeout=30)
r.raise_for_status()
data = r.json()

doc = data["results"][0]
with requests.get(doc["download_url"], headers=headers, stream=True, timeout=60) as resp:
    resp.raise_for_status()
    with open("cours.pdf", "wb") as f:
        for chunk in resp.iter_content(chunk_size=1024 * 64):
            if chunk:
                f.write(chunk)
```

### Node.js (fetch)

```js
import fs from "node:fs";

const BASE_URL = "http://127.0.0.1:8000";
const API_KEY = "<TON_API_KEY>";
const headers = { "X-API-Key": API_KEY };

const res = await fetch(`${BASE_URL}/api/data/documents/?page_size=5`, { headers });
if (!res.ok) throw new Error(await res.text());
const list = await res.json();

const dl = await fetch(list.results[0].download_url, { headers });
if (!dl.ok) throw new Error(await dl.text());

const file = fs.createWriteStream("cours.pdf");
await new Promise((resolve, reject) => {
  dl.body.pipe(file);
  dl.body.on("error", reject);
  file.on("finish", resolve);
});
```

## Codes d’erreur

- `400` paramètres invalides (ex: `encrypted_id` invalide)
- `401/403` API key invalide/révoquée ou absence d’offre active
- `404` ressource introuvable
- `429` quota dépassé

