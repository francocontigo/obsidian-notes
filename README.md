# 🧠 Second Brain — Karpathy LLM-Wiki, no Obsidian

Um **segundo cérebro mantido por LLM**. Você decide *o que* entra; o **Claude** lê, organiza,
interliga e mantém uma wiki de markdown consistente. Baseado no padrão "LLM Wiki" do Andrej Karpathy.

> A virada de chave: em vez de **você** manter a wiki e às vezes perguntar à IA, **a IA mantém a wiki
> inteira**. Karpathy: *"humanos abandonam wikis porque a manutenção cresce mais rápido que o valor; o LLM
> não cansa, não esquece de atualizar uma referência cruzada e toca 15 arquivos num passe."*

Tudo é **markdown puro** em disco: sem RAG, sem embeddings, sem banco vetorial, sem formato proprietário.
Cabe no contexto longo dos modelos atuais e você audita tudo no Obsidian (grafo, backlinks).

---

## Como está organizado e por quê

```
raw/            # FONTES IMUTÁVEIS. Você despeja aqui; o Claude lê, nunca edita.
  inbox.md      #   captura rápida (escreve no topo, estilo "append-and-review")
  assets/       #   imagens/anexos das fontes
wiki/           # CONSTRUÍDO PELO CLAUDE — markdown interligado por [[wikilinks]]
  sources/      #   1 resumo por fonte ingerida (sempre cita o original)
  entities/     #   pessoas, empresas, produtos, ferramentas
  concepts/     #   ideias, frameworks, técnicas
  synthesis/    #   análises que cruzam várias fontes
  index.md      #   catálogo mestre (MOC) — sempre atualizado
  log.md        #   registro append-only de toda operação
output/         # respostas geradas por /query e planos de estudo (/gaps)
review/         # CAMADA DE APRENDIZADO
  queue.md      #   deck de repetição espaçada (cards Q/A + box Leitner + sessão de vencimento)
CLAUDE.md       # "schema": o que é o cérebro + regras que o Claude SEMPRE segue
.claude/commands/   # slash commands customizados (ingest, query, lint, process-inbox, study, gaps, explain)
```

**Por quê assim?**
- `raw/` separado e imutável = uma **fonte da verdade** confiável; o Claude nunca corrompe o original.
- `wiki/` dividido em sources/entities/concepts/synthesis = o grafo do Obsidian fica navegável e cada tipo
  de conhecimento tem seu lugar.
- `index.md` + `log.md` = você sempre sabe o que existe e o que mudou (auditável, versionado no git).
- `CLAUDE.md` na raiz = o Claude Code lê automaticamente; é o contrato que garante consistência entre sessões.
- As notas legadas (`0 Notebook`, `1 Books&Courses`, …) **não são tocadas** — entram como fontes.

> **Regras de ouro** (em `CLAUDE.md`): nunca editar `raw/`; toda página cita a fonte; tudo conecta por
> `[[wikilink]]`; sempre atualizar `index.md` e acrescentar em `log.md`; contradições são *sinalizadas*, não apagadas.

---

## Três formas de usar (todas mexem nos mesmos arquivos)

### 1) Dentro do Claude Code (slash commands)
| Comando | O que faz |
|---|---|
| `/ingest <arquivo-ou-URL>` | Lê uma fonte, cria/atualiza páginas, interliga, **gera cards de recall**, atualiza índice e log |
| `/process-inbox` | Tria os itens de `raw/inbox.md` para a wiki (mesmo tratamento de cards) |
| `/query <pergunta>` | Responde a partir da wiki, salva em `output/` |
| `/lint` | Saúde **estrutural** da wiki: links quebrados, órfãos, fontes sem citação, contradições, lacunas |
| `/study [N]` | Sessão de **repetição espaçada** (active recall, interleaved) — interativo |
| `/explain <conceito>` | Modo **Feynman**: você explica, o Claude corrige e preenche buracos — interativo |
| `/gaps` | Saúde de **aprendizado**: páginas rasas, sem recall, cards mal-respondidos → plano em `output/study-plan.md` |

### 2) Automação via terminal (headless) — macOS e Windows
Wrappers finos que chamam o `claude` em modo não-interativo (`claude -p "/ingest …"`), pra você scriptar/agendar.

**macOS / Linux (`make`):**
```bash
make ingest SRC="1 Books&Courses/Descomplicando SQL.md"
make ingest SRC="https://exemplo.com/artigo"
make process-inbox
make query Q="o que minhas notas dizem sobre big-o de linked list?"
make lint
make capture TEXT="uma ideia rápida"   # só anexa no inbox, sem LLM
# aprendizado:
make study N=10                        # sessão de repetição espaçada (interativo)
make explain C="big o notation"        # modo Feynman (interativo)
make gaps                              # plano de estudo em output/study-plan.md
make ui                                # abre o Streamlit
```

**Windows (`PowerShell`):**
```powershell
./sb.ps1 ingest "1 Books&Courses/Descomplicando SQL.md"
./sb.ps1 process-inbox
./sb.ps1 query "o que minhas notas dizem sobre big-o de linked list?"
./sb.ps1 lint
./sb.ps1 capture "uma ideia rápida"
./sb.ps1 study 10
./sb.ps1 explain "big o notation"
./sb.ps1 gaps
./sb.ps1 ui
```
> Por que dois arquivos? Windows não tem `make` por padrão. Os dois têm os mesmos verbos e chamam o mesmo
> `claude`. `--permission-mode acceptEdits` deixa o Claude escrever na wiki sem pedir confirmação a cada arquivo.

### 3) Interface gráfica (Python + Streamlit)
Uma camada **opcional, por cima do Claude** — o LLM continua fazendo o trabalho; a UI só dá clique e um leitor da wiki.
```bash
pip install -r app/requirements.txt
make ui            # ou ./sb.ps1 ui   ou   streamlit run app/app.py
```
Abas: **Capture** (joga no inbox), **Ingest** (ingerir / processar inbox), **Study** (flashcards de repetição
espaçada com auto-correção), **Ask** (perguntar), **Browse wiki** (ler as páginas renderizadas),
**Status** (contadores + rodar lint/gaps + últimas linhas do log).

> Diferença das duas formas de estudar: no **terminal** (`make study`) o Claude lê sua resposta em texto livre
> e corrige com nuance; na **UI** o estudo é auto-corrigido (você marca ✅/❌). Os dois usam a mesma
> `review/queue.md` e o mesmo esquema Leitner — pode alternar à vontade.

---

## 🎓 O pipe de estudo (camada de aprendizado)

Guardar conhecimento ≠ aprender. Esta camada aplica 4 princípios da ciência de aprendizagem:

| Princípio | Como o sistema usa |
|---|---|
| **Active recall** | Cada página de `concepts/`/`synthesis/` termina com `## Recall` (perguntas Q→A) |
| **Spaced repetition** | `review/queue.md` agenda cada card por **caixas de Leitner** |
| **Interleaving** | `/study` mistura tópicos de áreas diferentes numa sessão |
| **Elaboration (Feynman)** | `/explain` te faz ensinar o conceito e revela os buracos |

**O ciclo:**
```
capturar → /ingest (resumo + cards de recall + conexões)
        → /study (active recall das cartas vencidas, interleaved)
        → acerto/erro reagenda o card (Leitner)
        → /gaps acha pontos fracos → sugere o próximo estudo → /explain ou novo /ingest
```

**Como funciona o Leitner (em `review/queue.md`):** os intervalos são contados em **sessões** (não em datas
do calendário — assim funciona offline e sem depender de relógio). Caixas e intervalos: box 1→1, 2→2, 3→4,
4→8, 5→16 sessões. Acertou → sobe de caixa (intervalo maior); errou → volta pra caixa 1. Um contador
`session:` no topo do arquivo avança a cada `/study`. Rode 1 sessão por dia e "sessão" ≈ "dia".

---

## 🔎 Busca / RAG (camada opcional, na UI)

> **Nota de design:** o LLM Wiki do Karpathy é deliberadamente *sem RAG* (markdown puro no contexto).
> Esta é uma camada **opcional** por cima, na aba **Search** do Streamlit — útil conforme a wiki cresce.
> Não altera o fluxo de slash commands.

**Engine de busca híbrida** (`app/rag/`): combina **BM25** (léxico) + **embeddings semânticos locais**
(`sentence-transformers`, offline, sem chave), fundidos por **Reciprocal Rank Fusion** e reordenados por um
**cross-encoder** (rerank). Degrada com elegância: sem o `sentence-transformers`, roda só BM25 e avisa quais
modos estão ativos.

**Resposta (RAG) com escolha de provider:** abstração em `app/rag/llm.py` que gera a resposta com **OpenAI**
ou **Anthropic** (modelo e chave escolhidos na barra lateral; chave também via `OPENAI_API_KEY` /
`ANTHROPIC_API_KEY`). Default Anthropic: `claude-opus-4-8`; default OpenAI: `gpt-4o`.

**Perplexity score (confiança):** calculada como `exp(média(-logprob dos tokens))` — **menor = mais
confiante**. Só disponível com **OpenAI** (expõe logprobs); com **Anthropic** aparece como indisponível,
porque a API não expõe logprobs. A resposta sempre cita as páginas usadas como `[[wikilink]]`.

```bash
pip install -r app/requirements.txt   # inclui rank-bm25, sentence-transformers (torch), openai, anthropic
make ui                                # aba "Search"
```

## Pré-requisitos
- [Claude Code CLI](https://docs.claude.com/claude-code) instalado, no PATH (`claude`), e logado (`claude` → login na 1ª vez).
- Para a UI: Python 3.10+ e `pip install -r app/requirements.txt`.
- Git já cuida do versionamento (obsidian-git/github-sync já configurados neste vault).

## Primeiro uso (passo a passo)
1. Abra um terminal **dentro da pasta do vault**:
   `cd "/Users/ricardo.franco/Documents/obsidian-notes"` (ou a pasta equivalente no Windows).
2. Inicie o Claude Code: digite `claude` e tecle Enter. Os slash commands (`/ingest`, `/study`, …) rodam
   **dentro dessa sessão** — não no terminal puro. Ex.: digite `/ingest 1 Books&Courses/Descomplicando SQL.md`.
3. (Alternativa sem abrir sessão) use os atalhos `make ...` (macOS) / `./sb.ps1 ...` (Windows) — eles chamam o Claude por você.
4. **Windows — liberar scripts (1ª vez):** se `./sb.ps1` der erro de permissão, rode no PowerShell:
   `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned` (ou rode pontual:
   `powershell -ExecutionPolicy Bypass -File .\sb.ps1 study`).
5. Para a interface gráfica: `pip install -r app/requirements.txt` e depois `make ui` / `./sb.ps1 ui`.

## Fluxo recomendado
1. Capture ideias soltas no `raw/inbox.md` (ou jogue PDFs/artigos em `raw/`).
2. `make process-inbox` / `/ingest` quando quiser consolidar (já gera os cards de recall).
3. **Estude todo dia:** `make study` (ou aba Study na UI) — leva poucos minutos e fixa o que entrou.
4. `/query` para perguntar; `/lint` (estrutura) e `/gaps` (aprendizado) de vez em quando.
5. Use `/explain <conceito>` quando quiser dominar um ponto de verdade.
6. Navegue o resultado no Obsidian (grafo + backlinks) ou na UI Streamlit.
