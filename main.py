import os
import re
import json
import requests
from bs4 import BeautifulSoup
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import firebase_admin
from firebase_admin import credentials, firestore

# ---------------------------------------------------------
# Inicialização do Firebase Admin
# A chave vem de uma variável de ambiente (JSON) no Render.
# ---------------------------------------------------------
firebase_key_json = os.environ.get("FIREBASE_KEY_JSON")
if not firebase_key_json:
    raise RuntimeError("Variável de ambiente FIREBASE_KEY_JSON não configurada.")

cred = credentials.Certificate(json.loads(firebase_key_json))
firebase_admin.initialize_app(cred)
db = firestore.client()

app = FastAPI(title="Vap AfiliAds - Automação")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # depois restrinja para o domínio do seu site
    allow_methods=["*"],
    allow_headers=["*"],
)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
}


class LinkInput(BaseModel):
    url: str
    user_id: str  # uid do usuário logado no site (para salvar como dono do anúncio)


def extrair_dados(url: str) -> dict:
    resp = requests.get(url, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    def meta(prop):
        tag = soup.find("meta", property=prop) or soup.find("meta", attrs={"name": prop})
        return tag["content"].strip() if tag and tag.get("content") else None

    title = meta("og:title") or (soup.title.string.strip() if soup.title else "Produto sem título")
    description = meta("og:description") or ""
    image = meta("og:image") or ""

    # Tenta achar preço via meta tags comuns ou regex no texto
    price = meta("product:price:amount") or meta("og:price:amount")
    if not price:
        match = re.search(r"R\$\s?\d{1,3}(?:\.\d{3})*(?:,\d{2})?", resp.text)
        price = match.group(0) if match else ""

    return {
        "title": title,
        "description": description[:500],
        "image": image,
        "price": price,
    }


@app.post("/preview")
def preview(data: LinkInput):
    """Só extrai os dados, sem salvar. Útil para o app mostrar antes de confirmar."""
    try:
        return extrair_dados(data.url)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro ao ler o link: {e}")


@app.post("/add-product")
def add_product(data: LinkInput):
    """Extrai os dados do link e já salva no Firestore, no formato usado pelo site."""
    try:
        info = extrair_dados(data.url)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro ao ler o link: {e}")

    doc = {
        "userId": data.user_id,
        "title": info["title"],
        "price": info["price"],
        "description": info["description"],
        "image": info["image"],
        "url": data.url,
        "views": 0,
        "clicks": 0,
        "createdAt": firestore.SERVER_TIMESTAMP,
    }
    ref = db.collection("ads").add(doc)
    return {"status": "ok", "id": ref[1].id, "data": info}


@app.get("/")
def health():
    return {"status": "online"}
