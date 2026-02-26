# 📱 FinFlow PWA — Controle Financeiro para Android

App de controle financeiro pessoal que **instala no seu celular Android** como um app nativo, sem precisar da Play Store.

---

## 🚀 Deploy no Render (gratuito)

### Passo 1 — Criar conta e repositório

1. Crie uma conta em **[github.com](https://github.com)** (se não tiver)
2. Crie um novo repositório privado: `finflow`
3. Faça upload de todos os arquivos desta pasta para o repositório

### Passo 2 — Deploy no Render

1. Acesse **[render.com](https://render.com)** e crie uma conta gratuita
2. Clique em **"New +"** → **"Web Service"**
3. Conecte seu repositório GitHub `finflow`
4. Configure:
   - **Name:** `finflow`
   - **Environment:** `Python`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app --bind 0.0.0.0:$PORT --workers 1`
5. Em **"Advanced"**, adicione um **Disk**:
   - Name: `finflow-db`
   - Mount Path: `/data`
   - Size: 1 GB
6. Clique em **"Create Web Service"**

Aguarde ~2 minutos. Você receberá uma URL como: `https://finflow-xxxx.onrender.com`

---

## 📲 Instalar no Android

1. Abra a URL do Render no **Google Chrome** do seu celular
2. O app vai mostrar um banner "Instalar FinFlow" → toque em **Instalar**
3. Se não aparecer o banner: toque nos **3 pontinhos** (⋮) → **"Adicionar à tela inicial"**
4. O FinFlow vai aparecer como app na sua tela inicial! ✅

---

## 🏗 Estrutura do projeto

```
finflow-pwa/
├── app.py              # Backend Flask (API + serve o frontend)
├── index.html          # Frontend React PWA (mobile-first)
├── manifest.json       # Configuração PWA (nome, ícone, cor)
├── sw.js               # Service Worker (cache offline)
├── requirements.txt    # Dependências Python
├── render.yaml         # Config automática do Render
└── static/
    └── icons/
        ├── icon-192.png
        └── icon-512.png
```

## ✨ Funcionalidades

- **Dashboard** — Saldo, receitas e despesas do mês + gráfico
- **Transações** — Lançar, editar, filtrar e deletar
- **Metas** — Metas de poupança com barra de progresso
- **Categorias** — Personalizáveis com cor e emoji

## 🛠 Tecnologias

- **Backend:** Python + Flask + SQLite + Gunicorn
- **Frontend:** React + Recharts (PWA)
- **Deploy:** Render.com (plano gratuito)
- **Instalação:** PWA via Chrome no Android

---

> 💡 **Dica:** No plano gratuito do Render, o serviço "hiberna" após 15 min sem uso. O primeiro acesso pode demorar ~30 segundos para acordar. Para uso contínuo, considere o plano pago ($7/mês).
