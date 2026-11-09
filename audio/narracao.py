"""Gera a narração do vídeo com a voz da Siri do macOS (Sandra, pt-BR), uma fala por cena.

Cada fala vira audio/out/narracao-NN.wav (44,1 kHz mono). A duração real de cada arquivo
é gravada em audio/out/narracao.json, e é ela que define o tempo de cada cena no vídeo.
A voz do `say` é determinística: o mesmo texto gera o mesmo arquivo.
"""

import argparse
import hashlib
import json
import os
import subprocess
import sys
import wave

VOZ = "com.apple.siri.natural.Sandra"  # voz da Siri (preferência de voz do sistema, pt-BR)


def gerar(textos, pasta):
    os.makedirs(pasta, exist_ok=True)
    registro = []
    for i, texto in enumerate(textos, start=1):
        base = os.path.join(pasta, f"narracao-{i:02d}")
        subprocess.run(["say", "-v", VOZ, "-o", base + ".aiff", texto], check=True)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", base + ".aiff",
                        "-ar", "44100", "-ac", "1", base + ".wav"], check=True)
        os.remove(base + ".aiff")
        with wave.open(base + ".wav", "rb") as w:
            duracao = w.getnframes() / w.getframerate()
        with open(base + ".wav", "rb") as f:
            sha = hashlib.sha256(f.read()).hexdigest()
        registro.append({"arquivo": os.path.basename(base) + ".wav", "duracao": round(duracao, 3), "sha256": sha})
    with open(os.path.join(pasta, "narracao.json"), "w", encoding="utf-8") as f:
        json.dump({"voz": VOZ, "falas": registro}, f, indent=2, ensure_ascii=False)
    return registro


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Gera a narração do vídeo com a voz do macOS.")
    ap.add_argument("--saida", default="out")
    args = ap.parse_args()
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "video"))
    import build_video
    textos = [texto for _loc, texto in build_video.NARRACAO]
    registro = gerar(textos, args.saida)
    for r in registro:
        print(f"{r['arquivo']}  {r['duracao']:.2f}s")
