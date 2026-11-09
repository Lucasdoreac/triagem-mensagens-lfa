"""Síntese de sons de fundo e efeitos com a biblioteca padrão do Python.

Gera, em 44,1 kHz mono 16 bits:
- ambiente-v2.wav: vento de fundo (ruído marrom com oscilação lenta) e um pad de acordes
  com harmônicos, desafinação leve e reverberação.
- whoosh-v2.wav: varredura de ruído com filtro passa-faixa, de grave para agudo.
- clique-v2.wav: tique curto com seno e transiente de ruído.
"""

import math
import random
import struct
import wave

SR = 44100
rng = random.Random(7)  # semente fixa: o mesmo script gera sempre o mesmo som


def salvar(caminho, amostras, pico=0.7):
    m = max(1e-9, max(abs(x) for x in amostras))
    fator = pico / m
    dados = b"".join(struct.pack("<h", int(max(-1, min(1, x * fator)) * 32767)) for x in amostras)
    with wave.open(caminho, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(dados)


def fade(amostras, entrada=0.02, saida=0.3):
    n = len(amostras)
    ne, ns = int(entrada * SR), int(saida * SR)
    for i in range(min(ne, n)):
        amostras[i] *= i / ne
    for i in range(min(ns, n)):
        amostras[n - 1 - i] *= i / ns
    return amostras


def passa_baixa_um_polo(x, fc):
    a = math.exp(-2 * math.pi * fc / SR)
    y, out = 0.0, []
    for v in x:
        y = (1 - a) * v + a * y
        out.append(y)
    return out


def ruido_marrom(n):
    y, out = 0.0, []
    for _ in range(n):
        y = max(-1.0, min(1.0, y + rng.uniform(-1, 1) * 0.02))
        out.append(y)
    # remove o deslocamento da integração
    media = sum(out) / len(out)
    return [v - media for v in out]


def reverb(x, mix=0.25):
    """Reverberação de Schroeder: quatro filtros comb e dois allpass."""
    combs = [(0.0297, 0.78), (0.0371, 0.76), (0.0411, 0.74), (0.0437, 0.72)]
    saidas = [0.0] * len(x)
    for atraso, ganho in combs:
        d = int(atraso * SR)
        buf = [0.0] * len(x)
        for i in range(len(x)):
            buf[i] = x[i] + (buf[i - d] * ganho if i >= d else 0.0)
        for i in range(len(x)):
            saidas[i] += buf[i] * 0.25
    for atraso, ganho in [(0.005, 0.7), (0.0017, 0.7)]:
        d = int(atraso * SR)
        buf = [0.0] * len(saidas)
        for i in range(len(saidas)):
            entrada = saidas[i]
            saida_ap = -ganho * entrada + (buf[i - d] if i >= d else 0.0)
            buf[i] = entrada + ganho * saida_ap if i >= d else entrada
            saidas[i] = saida_ap
    return [(1 - mix) * x[i] + mix * saidas[i] for i in range(len(x))]


def ambiente(duracao=16.0):
    n = int(duracao * SR)
    vento = passa_baixa_um_polo(ruido_marrom(n), 500)
    # oscilação lenta do vento (dois ciclos por 16 s, com desvio para não repetir igual)
    vento = [v * (0.55 + 0.25 * math.sin(2 * math.pi * 0.11 * i / SR) + 0.1 * math.sin(2 * math.pi * 0.047 * i / SR))
             for i, v in enumerate(vento)]

    # pad: quatro notas de um acorde maior com sétima, cada uma com 4 harmônicos e desafinação
    notas = [130.81, 164.81, 196.00, 246.94]   # C3, E3, G3, B3
    pesos = [1.0, 0.5, 0.25, 0.12]
    pad = [0.0] * n
    for f in notas:
        for desafino in (-4.0, 4.0):           # duas vozes por nota, desafinadas em cents
            fr = f * 2 ** (desafino / 1200)
            fase = rng.uniform(0, 2 * math.pi)
            for h, p in enumerate(pesos, start=1):
                w = 2 * math.pi * fr * h / SR
                for i in range(n):
                    pad[i] += p * math.sin(w * i + fase) / h
    # envelope lenta de ataque e liberação, e vibrato suave
    pad = [v * min(1.0, i / (2.5 * SR)) * min(1.0, (n - i) / (3.0 * SR)) * (0.8 + 0.2 * math.sin(2 * math.pi * 0.2 * i / SR))
           for i, v in enumerate(pad)]
    pad = passa_baixa_um_polo(pad, 1400)

    mix = [0.6 * vento[i] + 0.4 * pad[i] for i in range(n)]
    return fade(reverb(mix, mix=0.3), 0.5, 1.5)


def whoosh(duracao=1.4):
    n = int(duracao * SR)
    ruido = [rng.uniform(-1, 1) for _ in range(n)]
    saida = [0.0] * n
    x1 = x2 = y1 = y2 = 0.0
    q = 1.2
    for i in range(n):
        t = i / n
        fc = 250 * (14 ** t)                      # varredura exponencial de 250 Hz a 3500 Hz
        w0 = 2 * math.pi * fc / SR
        alpha = math.sin(w0) / (2 * q)
        # passa-faixa de ganho de pico constante (forma I), coeficientes atualizados por amostra
        b0, b1, b2 = alpha, 0.0, -alpha
        a0, a1, a2 = 1 + alpha, -2 * math.cos(w0), 1 - alpha
        x = ruido[i]
        y = (b0 * x + b1 * x1 + b2 * x2 - a1 * y1 - a2 * y2) / a0
        x2, x1 = x1, x
        y2, y1 = y1, y
        env = math.sin(math.pi * t) ** 2          # sobe e desce no meio do efeito
        saida[i] = y * env * 4.0                  # compensa a perda de energia do filtro
    return fade(saida, 0.01, 0.2)


def clique(duracao=0.12):
    n = int(duracao * SR)
    out = []
    for i in range(n):
        t = i / SR
        tom = math.sin(2 * math.pi * 1800 * t) * math.exp(-t * 90)
        transiente = rng.uniform(-1, 1) * math.exp(-t * 900) * 0.6
        out.append(0.7 * tom + transiente)
    return out


def gerar(pasta):
    """Gera os três sons em `pasta` e devolve {arquivo: sha256}, com a semente fixa."""
    import hashlib
    import json
    import os
    global rng
    rng = random.Random(7)  # cada geração começa da mesma semente
    os.makedirs(pasta, exist_ok=True)
    hashes = {}
    for nome, fn in [("ambiente-v2.wav", lambda: ambiente(150.0)), ("whoosh-v2.wav", whoosh), ("clique-v2.wav", clique)]:
        caminho = os.path.join(pasta, nome)
        rng = random.Random(7)
        salvar(caminho, fn())
        with open(caminho, "rb") as f:
            hashes[nome] = hashlib.sha256(f.read()).hexdigest()
    manifesto = {"sample_rate": SR, "semente": 7, "arquivos": hashes}
    with open(os.path.join(pasta, "manifesto.json"), "w", encoding="utf-8") as f:
        json.dump(manifesto, f, indent=2, ensure_ascii=False)
    return hashes


def verificar(pasta):
    """Confere se os arquivos em `pasta` batem com o manifesto. Devolve lista de divergências."""
    import hashlib
    import json
    import os
    with open(os.path.join(pasta, "manifesto.json"), encoding="utf-8") as f:
        manifesto = json.load(f)
    divergencias = []
    for nome, esperado in manifesto["arquivos"].items():
        with open(os.path.join(pasta, nome), "rb") as f:
            if hashlib.sha256(f.read()).hexdigest() != esperado:
                divergencias.append(nome)
    return divergencias


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="Gera ou verifica os sons determinísticos do vídeo.")
    ap.add_argument("--saida", default="out")
    ap.add_argument("--verificar", action="store_true", help="confere os hashes em vez de gerar")
    args = ap.parse_args()
    if args.verificar:
        d = verificar(args.saida)
        print("ok, hashes conferem" if not d else "divergem: " + ", ".join(d))
        raise SystemExit(1 if d else 0)
    h = gerar(args.saida)
    print("gerado:", ", ".join(f"{k}={v[:12]}" for k, v in h.items()))
