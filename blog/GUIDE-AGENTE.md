# GUIA DE OPERACAO DO BLOG GuiMiranda.tech
## Manual oficial do agente de IA (zcode / modo autonomo)

Este arquivo e o CONTRATO de operacao do blog. Leia-o INTEIRO antes de publicar qualquer artigo.
Referencia viva: os artigos ja publicados em `blog/*/index.html` sao exemplos validos de formato.

---

## 1. ESTRUTURA DO BLOG (contrato de arquivos)

```
blog/
  index.html          -> listagem dos artigos (o PRIMEIRO card e automaticamente o destaque)
  _template.html      -> esqueleto do artigo com {{PLACEHOLDERS}} (copie daqui para criar novo post)
  GUIDE-AGENTE.md     -> este manual
  data/articles.json  -> indice de artigos em JSON (fonte da verdade do agente)
  <slug>/index.html   -> cada artigo vive na propria pasta (URL limpa: /blog/<slug>/)
img/blog/
  <slug>-hero.webp / .jpg    -> imagem de capa 2:1 (proporcao 2:1, ex.: 1344x672 ou 1024x512)
  og-<slug>.jpg              -> imagem Open Graph 1200x630 COM tipografia (badge + titulo + subtitulo)
sitemap.xml            -> URLs dos artigos entram dentro do bloco <!-- BLOG:START ... BLOG:END -->
```

Regras de ouro (INVIOLAVEIS):
1. NUNCA edite artigos ja publicados (pastas `blog/<slug>/` existentes).
2. NUNCA edite arquivos fora de: `blog/`, `img/blog/` e o bloco marcado em `sitemap.xml`.
3. NUNCA remova um artigo da listagem, do sitemap ou do articles.json.
4. NUNCA faca commit de tokens, senhas ou arquivos `.env`.
5. Idempotencia: antes de comecar, verifique se ja existe artigo publicado HOJE (procure a data de hoje em `blog/data/articles.json`). Se existir, ABORTE e reporte.
6. Toda escrita e em pt-BR, sem travessoes (o site usa virgulas, dois-pontos e "|" no lugar de travessoes).
7. Site esta em GitHub Pages SEM Jekyll (existe .nojekyll). NAO use frontmatter YAML, nao crie pastas iniciando com `_` fora do `blog/_template.html` (que ja existe).

## 2. FLUXO DIARIO (passo a passo)

### ETAPA 0: Pre-flight
1. `git pull origin main` (resolva conflitos; se nao conseguir, ABORTE e reporte).
2. Leia `blog/data/articles.json`: se ja houver artigo com a data de hoje, ABORTE.
3. Anote os ULTIMOS 5 temas publicados para nao repetir pauta.
4. Confira a data real do Brasil: `TZ=America/Sao_Paulo date +%F`.

### ETAPA 1: Pauta (pesquisa do tema do dia)
1. Pesquise nas ultimas 24 horas: lancamentos e noticias de IA (OpenAI, Anthropic, Google, Meta, DeepSeek, Z.ai/GLM), vibe coding, agentes, automacao, ferramentas para negocios, KDP/Amazon, LGPD e outros temas das 8 trilhas.
2. Escolha o tema de maior impacto OU, se o dia estiver morno, um tema evergreen alinhado as trilhas (IA para executivos, vibe coding, SEO/AEO, publicacao com IA...).
3. O tema DEVE conectar com o valor pratico de dominar IA nos negocios (o objetivo final e converter para a mentoria).
4. Defina a trilha principal relacionada (IA, Marketing, Presenca, Tecnologia, Gestao, Startups, Juridico, Livros) e a `category` do post (ex.: "IA e Vibe Coding", "Autoria e Livros", "Marketing e Vendas").
5. Nao repita pauta dos ultimos 5 artigos nem escreva sobre o mesmo fato de dois dias seguidos.

### ETAPA 2: Artigo (regras de conteudo)
- 2.000 a 3.000 palavras, denso e pratico, sem enrolacao.
- Tom: pragmatico, mao na massa, visionario, levemente provocador, altissima autoridade. Primeira pessoa quando falar do autor ("eu", "na minha mentoria").
- AEO (Answer Engine Optimization), OBRIGATORIO:
  * O primeiro paragrafo apos o H1 (o `lead`) responde DIRETAMENTE e de forma conclusiva a pergunta central do tema (para ser extraido por ChatGPT, Perplexity, Claude e Google AI Overviews).
  * Secao final H2 "Perguntas frequentes (FAQ)" com 4 ou 5 perguntas e respostas diretas de 2 a 3 frases.
  * H2s em forma de pergunta ou resposta direta sempre que couber.
- CTA da mentoria em DOIS pontos: uma caixa `cta-post` no meio do artigo e o `cta-banner` no final. Mensagem WhatsApp sempre identifica a origem: `Ola, Guilherme! Li o artigo sobre <tema> no blog e quero saber mais sobre a mentoria...` (URL-encoded).
- 3 a 6 links internos para paginas do site (trilhas, mentoria, planos, executivos, sobre). NUNCA linke para concorrentes.
- Factualidade: nao invente numeros, citacoes nem datas. Se nao tiver certeza, escreva qualitativamente ou verifique com busca. Fontes de destaque ficam registradas no articles.json.

### ETAPA 3: SEO/AEO tecnico (checklist OBRIGATORIO)
- `title` com ate 65 caracteres + sufixo " | GuiMiranda.tech".
- `meta description` com 150 a 160 caracteres, persuasiva, com a keyword principal.
- `keywords` com 6 a 10 termos, incluindo variacoes de cauda longa.
- `canonical` = `https://superaplicativos.github.io/GuiMiranda.tech/blog/<slug>/`.
- OG completo: og:type=article, og:locale=pt_BR, og:title, og:description, og:image (1200x630), article:published_time, article:section, article:tag.
- Twitter card: summary_large_image.
- JSON-LD em um bloco @graph com: BlogPosting (headline, description, image, datePublished, dateModified, wordCount, articleSection, keywords, author Person, publisher, mainEntityOfPage), FAQPage (as MESMAS perguntas e respostas visiveis no HTML) e BreadcrumbList (Inicio > Blog > artigo).
- Um UNICO H1 por pagina. H2s e H3s semanticos. Paragrafos de 3 a 5 frases (minimo).
- Alt descritivo em TODA imagem. `loading="lazy"` na listagem, `fetchpriority="high"` no hero.
- Datas: sempre fuso -03:00 (`2026-01-15T09:00:00-03:00`).
- Slug: minusculas, sem acentos, palavras separadas por hifen, 3 a 6 palavras, com a keyword principal.

### ETAPA 4: Imagens
1. Imagem de capa 2:1 (cyberpunk moderno, limpo e profissional, SEM texto legivel renderizado; tons violeta e ciano, identidade visual do site). Se houver foto real do Guilherme fornecida pelo usuario, USE-A em vez de imagem gerada.
2. Salve as versoes finais em `img/blog/`:
   * `<slug>-hero.webp` e `<slug>-hero.jpg` (2:1, ex.: 1344x672)
   * `og-<slug>.jpg` (1200x630, com gradiente escuro na base, badge "GUIMIRANDA.TECH  ·  BLOG" e o titulo curto em Sora/Inter)
3. Nomeie sempre com o slug do post. Nao sobrescreva imagens de outros artigos.

### ETAPA 5: Publicacao (arquivos que devem ser criados/editados)
1. CRIE `blog/<slug>/index.html` a partir de `blog/_template.html`, substituindo TODOS os placeholders (procure por `{{`).
2. EDITE `blog/index.html`: insira um novo `<article class="post-card card reveal">` IMEDIATAMENTE apos a linha `<!-- POSTS:START ... -->` (o post novo sempre primeiro; o CSS promove o primeiro card a destaque automaticamente). Card = link `post-thumb` com picture webp/jpg, `post-meta` (categoria + data), `h3` com link, `post-excerpt` (2 frases) e `post-more`.
3. ATUALIZE o JSON-LD `Blog` em `blog/index.html`: adicione o novo BlogPosting no array `blogPost`.
4. EDITE `blog/data/articles.json`: adicione o novo objeto no INICIO do array (slug, url, date, updated, title, description, category, tags, image, og, wordcount, readingtime, trend, fontes).
5. EDITE `sitemap.xml`: adicione a nova URL dentro do bloco `<!-- BLOG:START ... BLOG:END -->`, imediatamente apos a entrada `/blog/`, com `<lastmod>` da data de hoje e `priority` 0.8.
6. Git: `git add blog/<slug> img/blog/<slug>-hero.webp img/blog/<slug>-hero.jpg img/blog/og-<slug>.jpg blog/index.html blog/data/articles.json sitemap.xml` (somente os arquivos tocados), commit com mensagem `post: <titulo curto>` e `git push origin main`.
   - Nao consegue push via git? Use a Git Data API do GitHub (blobs -> tree -> commit -> update ref), do mesmo jeito que o script `push-api.py` do projeto faz.

### ETAPA 6: Validacao final (checklist antes do commit)
- [ ] JSON-LD valido (cole o bloco num parser JSON; se invalido, NAO publique).
- [ ] Nenhum `{{` restante no HTML.
- [ ] 0 travessoes (em/en dash) no texto.
- [ ] Meta description entre 150 e 160 caracteres.
- [ ] Todos os links internos resolvem (o artigo esta 2 niveis abaixo da raiz: use `../../`).
- [ ] Imagem de capa existente nos 3 formatos e referenciada corretamente.
- [ ] FAQ visivel identico em essencia ao FAQPage do JSON-LD.
- [ ] Card novo inserido no blog/index.html e sitemap.xml atualizado.
- [ ] articles.json continua um JSON valido.
- [ ] Apos o push, confira ao vivo: a URL do artigo responde HTTP 200 e o card aparece na listagem.

## 3. CATEGORIAS VALIDAS (use uma destas)
- IA e Vibe Coding
- Agentes e Automacao
- Marketing e Vendas
- SEO, AEO e Presenca Digital
- Tecnologia e Produtividade
- Gestao e Negocios
- Startups e Inovacao
- Juridico, LGPD e Direito Digital
- Autoria e Livros (Amazon KDP)

## 4. DADOS FIXOS DO SITE (nao inventar)
- Autor: Guilherme Miranda. Credenciais publicas: 27 anos fundando startups, mais de 1.200 sites e apps entregues, mais de 80 livros publicados na Amazon (mais de 260 obras globais), mentor em IA, marketing e tecnologia.
- WhatsApp: https://wa.me/5511966161611 (11) 96616-1611.
- Presencial em Ribeirao Preto e Sao Paulo, online em todo o Brasil.
- LinkedIn: https://www.linkedin.com/in/desenvolvimentodeaplicativos/
- URL base do site: https://superaplicativos.github.io/GuiMiranda.tech/
- Repo GitHub: superaplicativos/GuiMiranda.tech (branch main, GitHub Pages).

## 5. CRITERIOS DE SUCESSO DO DIA
Artigo publicado ao vivo + 0 erros de validacao + sitemap atualizado + card na home do blog + CTA WhatsApp identificando a origem. Nenhuma pagina antiga modificada ou quebrada.
