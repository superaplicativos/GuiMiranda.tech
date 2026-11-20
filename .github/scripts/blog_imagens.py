#!/usr/bin/env python3
"""
Gerador de imagens do blog GuiMiranda.tech

Dois modos:

  1) Capa provisoria (roda em qualquer lugar, sem internet):
       python3 .github/scripts/blog_imagens.py provisorio <slug> "<titulo OG>" "<subtitulo OG>"
     Gera img/blog/<slug>-hero.webp, <slug>-hero.jpg e og-<slug>.jpg com arte abstrata
     na identidade do site, para o post nunca subir com imagem quebrada.

  2) Fila de IA (roda no GitHub Actions, que tem internet aberta):
       python3 .github/scripts/blog_imagens.py fila
     Le blog/data/imagens-fila.json, gera a capa por IA (Pollinations, modelo Flux, gratuito),
     sobrescreve as 3 imagens do slug e marca o item como "gerada".

Formato da fila (array, item novo no inicio):
  {"slug": "...", "prompt": "prompt em ingles", "og_titulo": "titulo curto",
   "og_sub": "subtitulo curto", "status": "pendente", "tentativas": 0}
"""
import io, json, math, os, random, sys, time, urllib.parse, urllib.request
from datetime import datetime, timezone, timedelta

from PIL import Image, ImageDraw, ImageFilter, ImageFont

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
IMG_DIR = os.path.join(RAIZ, "img", "blog")
FILA = os.path.join(RAIZ, "blog", "data", "imagens-fila.json")
FONT_DIR = os.path.join(RAIZ, ".github", "fonts")

HERO_W, HERO_H = 1344, 672
OG_W, OG_H = 1200, 630
VIOLETA = (139, 92, 246)
CIANO = (34, 211, 238)
ESTILO = (", modern cyberpunk aesthetic, clean and professional, deep violet and cyan neon lighting, "
          "dark background, cinematic composition, high detail, photorealistic, 8k, "
          "no text, no letters, no words, no watermark, no logo")
MAX_TENTATIVAS = 6


# ---------------------------------------------------------------- fontes
def _fonte(nomes, tamanho):
    candidatos = []
    for n in nomes:
        candidatos += [os.path.join(FONT_DIR, n), n]
    candidatos += [
        "/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ]
    for c in candidatos:
        try:
            f = ImageFont.truetype(c, tamanho)
            return f
        except Exception:
            continue
    return ImageFont.load_default()


def fonte_titulo(t):
    f = _fonte(["Sora.ttf"], t)
    try:
        f.set_variation_by_axes([700])
    except Exception:
        pass
    return f


def fonte_texto(t, peso=500):
    f = _fonte(["Inter.ttf", "/usr/share/fonts/opentype/inter/Inter-Medium.otf"], t)
    try:
        f.set_variation_by_axes([14, peso])
    except Exception:
        try:
            f.set_variation_by_axes([peso])
        except Exception:
            pass
    return f


# ---------------------------------------------------------------- arte provisoria
def arte_abstrata(w, h, seed):
    rnd = random.Random(seed)
    fundo = Image.linear_gradient("L").resize((w, h))
    base = Image.merge("RGB", [fundo.point(lambda v, a=a, b=b: int(a + b * v / 255)) for a, b in ((12, 14), (8, 6), (26, 30))])
    glow = Image.new("RGB", (w, h), (0, 0, 0))
    d = ImageDraw.Draw(glow)
    for _ in range(5):
        cx, cy = rnd.randint(0, w), rnd.randint(0, h)
        r = rnd.randint(int(h * .25), int(h * .6))
        cor = VIOLETA if rnd.random() < .55 else CIANO
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=tuple(int(c * .55) for c in cor))
    glow = glow.filter(ImageFilter.GaussianBlur(h // 5))
    base = Image.merge("RGB", [Image.eval(Image.merge("L", [a]), lambda v: v) for a in base.split()])
    from PIL import ImageChops
    base = ImageChops.add(base, glow)
    # grade em perspectiva
    linhas = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    dl = ImageDraw.Draw(linhas)
    horiz = int(h * .58)
    for i in range(-20, 21):
        x0 = w / 2 + i * w * .09
        dl.line([(w / 2 + i * 8, horiz), (x0, h)], fill=CIANO + (55,), width=1)
    for k in range(1, 14):
        y = horiz + (h - horiz) * (k / 13) ** 1.8
        dl.line([(0, y), (w, y)], fill=VIOLETA + (60,), width=1)
    # nos e conexoes
    pts = [(rnd.randint(int(w * .1), int(w * .9)), rnd.randint(int(h * .08), int(h * .55))) for _ in range(22)]
    for i, a in enumerate(pts):
        for b in pts[i + 1:]:
            if math.dist(a, b) < w * .16:
                dl.line([a, b], fill=CIANO + (70,), width=1)
    for p in pts:
        r = rnd.randint(2, 5)
        dl.ellipse([p[0] - r, p[1] - r, p[0] + r, p[1] + r], fill=(220, 240, 255, 200))
    halo = linhas.filter(ImageFilter.GaussianBlur(4))
    base = base.convert("RGBA")
    base.alpha_composite(halo)
    base.alpha_composite(linhas)
    return base.convert("RGB")


# ---------------------------------------------------------------- composicao OG
def quebra(texto, fonte, largura, draw):
    palavras, linhas, atual = texto.split(), [], ""
    for p in palavras:
        teste = (atual + " " + p).strip()
        if draw.textlength(teste, font=fonte) <= largura:
            atual = teste
        else:
            if atual:
                linhas.append(atual)
            atual = p
    if atual:
        linhas.append(atual)
    return linhas


def compor_og(img, titulo, sub):
    og = cover(img, OG_W, OG_H).convert("RGBA")
    grad = Image.new("L", (1, OG_H))
    for y in range(OG_H):
        t = max(0.0, (y - OG_H * .25) / (OG_H * .75))
        grad.putpixel((0, y), int(235 * t ** 1.1))
    escuro = Image.new("RGBA", (OG_W, OG_H), (10, 6, 24, 255))
    escuro.putalpha(grad.resize((OG_W, OG_H)))
    og.alpha_composite(escuro)
    veu = Image.new("RGBA", (OG_W, OG_H), (20, 10, 45, 70))
    og.alpha_composite(veu)
    d = ImageDraw.Draw(og)
    # badge
    fb = fonte_texto(22, 500)
    txt = "GUIMIRANDA.TECH  ·  BLOG"
    tw = d.textlength(txt, font=fb)
    d.rounded_rectangle([58, 52, 58 + tw + 44, 100], radius=24, fill=(20, 12, 40, 170), outline=VIOLETA + (255,), width=2)
    d.text((80, 63), txt, font=fb, fill=CIANO + (255,))
    # titulo
    tam = 64
    while True:
        ft = fonte_titulo(tam)
        linhas = quebra(titulo, ft, OG_W - 130, d)
        if len(linhas) <= 3 or tam <= 40:
            break
        tam -= 4
    altura_l = int(tam * 1.18)
    fs = fonte_texto(26, 400)
    y_sub = OG_H - 50
    y = y_sub - 30 - altura_l * len(linhas)
    for ln in linhas:
        d.text((58, y), ln, font=ft, fill=(245, 243, 255, 255))
        y += altura_l
    d.rectangle([58, y + 14, 132, y + 19], fill=VIOLETA + (255,))
    d.rectangle([140, y + 14, 168, y + 19], fill=CIANO + (255,))
    if sub:
        d.text((58, y_sub - 8), sub, font=fs, fill=(205, 200, 230, 255))
    return og.convert("RGB")


def cover(img, w, h):
    iw, ih = img.size
    esc = max(w / iw, h / ih)
    nw, nh = int(iw * esc + .5), int(ih * esc + .5)
    img = img.resize((nw, nh), Image.LANCZOS)
    l, t = (nw - w) // 2, (nh - h) // 2
    return img.crop((l, t, l + w, t + h))


def salvar(slug, hero_img, og_titulo, og_sub):
    os.makedirs(IMG_DIR, exist_ok=True)
    hero = cover(hero_img.convert("RGB"), HERO_W, HERO_H)
    hero.save(os.path.join(IMG_DIR, f"{slug}-hero.webp"), "WEBP", quality=82, method=6)
    hero.save(os.path.join(IMG_DIR, f"{slug}-hero.jpg"), "JPEG", quality=84, optimize=True, progressive=True)
    compor_og(hero_img.convert("RGB"), og_titulo, og_sub).save(
        os.path.join(IMG_DIR, f"og-{slug}.jpg"), "JPEG", quality=86, optimize=True, progressive=True)


# ---------------------------------------------------------------- IA
# Ordem de preferencia (usa a primeira que tiver credencial e responder):
#   1) Cloudflare Workers AI, FLUX.1 schnell (secrets CF_ACCOUNT_ID + CF_API_TOKEN), gratis no plano free
#   2) Pollinations com chave gratis (secret POLLINATIONS_TOKEN), Flux sem marca d'agua
#   3) Pollinations anonimo (ultimo recurso; a faixa inferior com a marca d'agua e cortada)
def _cloudflare(prompt, seed):
    conta, token = os.environ.get("CF_ACCOUNT_ID"), os.environ.get("CF_API_TOKEN")
    if not (conta and token):
        return None
    import base64
    url = f"https://api.cloudflare.com/client/v4/accounts/{conta}/ai/run/@cf/black-forest-labs/flux-1-schnell"
    corpo = json.dumps({"prompt": prompt + ESTILO, "steps": 8, "seed": seed}).encode()
    req = urllib.request.Request(url, data=corpo, method="POST", headers={
        "Authorization": f"Bearer {token}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r:
        resp = json.loads(r.read())
    b64 = (resp.get("result") or {}).get("image")
    if not b64:
        raise RuntimeError(f"Cloudflare sem imagem: {str(resp)[:200]}")
    img = Image.open(io.BytesIO(base64.b64decode(b64)))
    img.load()
    print(f"  ok: Cloudflare FLUX {img.size}")
    return img


def _pollinations_token(prompt, seed):
    token = os.environ.get("POLLINATIONS_TOKEN")
    if not token:
        return None
    p = urllib.parse.quote(prompt + ESTILO, safe="")
    for u in (f"https://gen.pollinations.ai/image/{p}?width={HERO_W}&height={HERO_H}&model=flux&nologo=true&seed={seed}",
              f"https://image.pollinations.ai/prompt/{p}?width={HERO_W}&height={HERO_H}&model=flux&nologo=true&seed={seed}"):
        try:
            req = urllib.request.Request(u, headers={"Authorization": f"Bearer {token}",
                                                     "User-Agent": "GuiMiranda.tech-blog-bot/1.0"})
            with urllib.request.urlopen(req, timeout=180) as r:
                img = Image.open(io.BytesIO(r.read()))
                img.load()
            print(f"  ok: Pollinations com chave {img.size}")
            return img
        except Exception as e:
            print(f"  Pollinations com chave falhou: {str(e)[:120]}")
    return None


def gerar_ia(prompt, seed):
    for fonte in (_cloudflare, _pollinations_token):
        try:
            img = fonte(prompt, seed)
            if img is not None:
                return img
        except Exception as e:
            print(f"  {fonte.__name__} falhou: {str(e)[:200]}")
    img = _pollinations_anonimo(prompt, seed)
    w, h = img.size
    return img.crop((0, 0, w, int(h * 672 / 736)))  # remove a faixa com a marca d'agua


def _pollinations_anonimo(prompt, seed):
    p = urllib.parse.quote(prompt + ESTILO, safe="")
    HERO_H_ = 736  # gera mais alto para cortar a marca d'agua no rodape
    urls = [
        f"https://image.pollinations.ai/prompt/{p}?width={HERO_W}&height={HERO_H_}&model=flux&nologo=true&enhance=true&seed={seed}",
        f"https://gen.pollinations.ai/image/{p}?width={HERO_W}&height={HERO_H_}&model=flux&nologo=true&seed={seed}",
    ]
    _nao_usado = [
        f"https://image.pollinations.ai/prompt/{p}?width={HERO_W}&height={HERO_H}&model=flux&nologo=true&enhance=true&seed={seed}",
        f"https://image.pollinations.ai/prompt/{p}?width={HERO_W}&height={HERO_H}&nologo=true&seed={seed}",
        f"https://gen.pollinations.ai/image/{p}?width={HERO_W}&height={HERO_H}&model=flux&nologo=true&seed={seed}",
    ]
    ultimo = None
    for rodada in range(3):
        for u in urls:
            try:
                req = urllib.request.Request(u, headers={"User-Agent": "GuiMiranda.tech-blog-bot/1.0"})
                with urllib.request.urlopen(req, timeout=180) as r:
                    dados = r.read()
                img = Image.open(io.BytesIO(dados))
                img.load()
                if img.size[0] >= 512:
                    print(f"  ok: {u.split('?')[0][:60]}... {img.size}")
                    return img
            except Exception as e:
                ultimo = e
                print(f"  falhou ({type(e).__name__}: {str(e)[:120]})")
        time.sleep(20 * (rodada + 1))
    raise RuntimeError(f"Pollinations indisponivel: {ultimo}")


def modo_fila():
    if not os.path.exists(FILA):
        print("Sem fila de imagens.")
        return 0
    fila = json.load(open(FILA, encoding="utf-8"))
    mudou = False
    for item in fila:
        if item.get("status") != "pendente":
            continue
        if item.get("tentativas", 0) >= MAX_TENTATIVAS:
            continue
        slug = item["slug"]
        print(f"Gerando imagem IA: {slug}")
        item["tentativas"] = item.get("tentativas", 0) + 1
        mudou = True
        try:
            img = gerar_ia(item["prompt"], abs(hash(slug)) % 99999)
            salvar(slug, img, item.get("og_titulo", slug), item.get("og_sub", ""))
            item["status"] = "gerada"
            item["gerada_em"] = datetime.now(timezone(timedelta(hours=-3))).isoformat(timespec="seconds")
            item.pop("erro", None)
        except Exception as e:
            item["erro"] = str(e)[:300]
            print(f"  ERRO: {e}")
    if mudou:
        with open(FILA, "w", encoding="utf-8") as f:
            json.dump(fila, f, ensure_ascii=False, indent=2)
            f.write("\n")
    return 0


def modo_provisorio(slug, titulo, sub):
    salvar(slug, arte_abstrata(HERO_W, HERO_H, slug), titulo, sub)
    print(f"Capa provisoria gerada para {slug}")


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "fila":
        sys.exit(modo_fila())
    if len(sys.argv) >= 4 and sys.argv[1] == "provisorio":
        modo_provisorio(sys.argv[2], sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else "")
        sys.exit(0)
    print(__doc__)
    sys.exit(1)
