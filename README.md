# Backend Vap AfiliAds - Automação

## 1. Gerar a chave do Firebase (Admin SDK)
1. Acesse o Console do Firebase → projeto `vapafiliads`
2. Ícone de engrenagem → **Configurações do projeto** → aba **Contas de serviço**
3. Clique em **Gerar nova chave privada** → baixa um arquivo `.json`
4. Abra o arquivo e copie todo o conteúdo (é um JSON)

## 2. Subir o código no GitHub
1. Crie um repositório novo (ex: `vapafiliads-backend`)
2. Suba os arquivos: `main.py`, `requirements.txt`, `Procfile`
   **Não suba a chave do Firebase no repositório.**

## 3. Deploy no Render (grátis)
1. Crie conta em render.com
2. **New +** → **Web Service** → conecte o repositório do GitHub
3. Configurações:
   - Runtime: Python 3
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Em **Environment**, adicione a variável:
   - Key: `FIREBASE_KEY_JSON`
   - Value: cole o conteúdo do JSON baixado no passo 1 (tudo em uma linha)
5. Deploy. Ao final você recebe uma URL tipo:
   `https://vapafiliads-backend.onrender.com`

## 4. Testar
```
POST https://vapafiliads-backend.onrender.com/add-product
Body (JSON):
{
  "url": "https://www.amazon.com.br/dp/XXXXXXX",
  "user_id": "uid_do_usuario_logado"
}
```
Isso já cria o anúncio direto no Firestore, aparecendo no site.

## Observação
O plano gratuito do Render "dorme" após 15 min sem uso — a primeira
chamada depois disso demora ~30s para acordar. Normal.
