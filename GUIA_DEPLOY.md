# Guia de Deploy — Docol Wellness Insights
## Hospedagem gratuita no Render.com (10 minutos)

---

## Pré-requisitos

Você vai precisar de:
- Uma conta no **GitHub** (gratuita) — [github.com/signup](https://github.com/signup)
- Uma conta no **Render** (gratuita, sem cartão) — [render.com](https://render.com)

---

## PASSO 1 — Criar repositório no GitHub

1. Acesse [github.com/new](https://github.com/new)
2. Preencha:
   - **Repository name:** `docol-wellness`
   - **Description:** `Coleta de Insights — Portfólio BE`
   - Marque **Public**
   - Marque **Add a README file**
3. Clique **Create repository**

---

## PASSO 2 — Fazer upload dos arquivos

No repositório recém-criado:

1. Clique no botão **Add file** → **Upload files**
2. Arraste os **4 arquivos** da pasta `deploy/` para a área de upload:
   - `server.py`
   - `index.html`
   - `requirements.txt`
   - `render.yaml`
3. Em "Commit message" escreva: `upload app files`
4. Clique **Commit changes**

✅ Seu repositório agora deve mostrar os 4 arquivos + README.

---

## PASSO 3 — Criar conta no Render

1. Acesse [render.com](https://render.com)
2. Clique **Get Started for Free**
3. Escolha **Sign in with GitHub** (mais fácil)
4. Autorize o acesso ao GitHub

---

## PASSO 4 — Deploy no Render

1. No Dashboard do Render, clique em **New** → **Web Service**
2. Selecione **Build and deploy from a Git repository** → **Next**
3. Conecte o repositório `docol-wellness` que você criou
4. Configure:
   - **Name:** `docol-wellness`
   - **Region:** escolha a mais próxima (recomendo **South America - São Paulo** se disponível, senão **US East**)
   - **Branch:** `main`
   - **Runtime:** `Python 3`
   - **Build Command:** (deixe vazio)
   - **Start Command:** `python server.py`
5. Em **Instance Type**, selecione **Free**
6. Clique **Create Web Service**

⏳ Aguarde 1-2 minutos enquanto o Render faz o deploy.

---

## PASSO 5 — Pronto!

Quando o status mudar para **Live**, você verá um link como:

```
https://docol-wellness.onrender.com
```

Esse é o link que você compartilha com os participantes!

| Quem | Link |
|------|------|
| **Participantes** | `https://docol-wellness.onrender.com` |
| **Facilitador (você)** | `https://docol-wellness.onrender.com/#facilitador` |

---

## IMPORTANTE — Comportamento do plano gratuito

O Render gratuito **adormece o servidor após 15 minutos sem acesso**. O primeiro acesso após adormecer demora ~30 segundos para acordar.

### Como preparar para o evento:

1. **30 minutos antes do evento**, abra o link do facilitador no navegador
2. O servidor vai acordar e ficar ativo
3. Enquanto houver acessos (participantes conectados), ele **não adormece**
4. Durante o evento com todos conectados, tudo funciona em tempo real normalmente

### Dica profissional:

Se quiser garantir que o servidor nunca adormece, abra uma aba do navegador com este endereço e deixe aberta:

```
https://docol-wellness.onrender.com/api/stats
```

Isso faz uma requisição periódica que mantém o servidor acordado.

---

## Gerar QR Code para os participantes

Com o link em mãos, gere um QR Code para facilitar o acesso via celular:

1. Acesse [qr.io](https://qr.io) ou [qrcode-monkey.com](https://www.qrcode-monkey.com/)
2. Cole o link: `https://docol-wellness.onrender.com`
3. Gere e baixe o QR Code
4. Projete na tela da sala ou imprima

---

## Atualizar o app depois do deploy

Se precisar alterar algo no `index.html` ou `server.py`:

1. Vá ao repositório no GitHub
2. Clique no arquivo que quer editar
3. Clique no ícone de lápis (✏️) para editar
4. Faça a alteração
5. Clique **Commit changes**
6. O Render detecta automaticamente e faz re-deploy em ~1 minuto

---

## Exportar dados depois do evento

No modo facilitador, clique em **JSON** para exportar todos os cards e participantes. Depois, cole no Claude para análise IA usando o botão **Copiar p/ IA**.

---

## Troubleshooting

| Problema | Solução |
|----------|---------|
| Página demora para carregar | Servidor estava dormindo — aguarde 30s |
| Erro 502 | Re-deploy: Render Dashboard → seu serviço → Manual Deploy |
| Cards não aparecem em tempo real | Verifique se o servidor está Live no Dashboard |
| Erro ao enviar card | Verifique conexão de internet do celular |
