"""Interface de terminal: lê respostas, chama o motor e mostra a explicação."""

import base as base_conhecimento
from motor import provar, CONFIRMADA, REFUTADA, INCONCLUSIVA

ENTRADAS = {"s": "sim", "n": "não", "?": "?"}


def normalizar_resposta(texto):
    """Aceita s, n ou ? com espaços e caixa indiferentes. Devolve None se inválida."""
    return ENTRADAS.get(texto.strip().casefold())


def _base():
    return {"FATOS": base_conhecimento.FATOS, "REGRAS": base_conhecimento.REGRAS}


def perguntar_terminal(fato):
    pergunta = base_conhecimento.FATOS[fato]["pergunta"]
    while True:
        resposta = normalizar_resposta(input(f"{pergunta} [s/n/?] "))
        if resposta is not None:
            return resposta
        print("Resposta inválida. Digite s, n ou ?.")


def explicar(estado, rastro):
    for linha in rastro:
        if linha["regra"] is None:
            continue
        print(f"  {linha['regra']}: {linha['premissa']} = {linha['valor']} -> {linha['conclusao']}")


def triagem(objetivo, respostas=None, perguntar=perguntar_terminal):
    respostas = {} if respostas is None else respostas
    estado, rastro = provar(objetivo, _base(), respostas, perguntar)
    descricao = base_conhecimento.HIPOTESES[objetivo]["descricao"]
    print(f"\n{descricao}: {estado}")
    explicar(estado, rastro)
    return estado


def main():
    print(base_conhecimento.TITULO)
    print("1 - Ação recomendada   2 - Relatório completo das hipóteses   0 - Sair")
    opcao = input("Opção: ").strip()
    if opcao == "1":
        triagem("acao")
    elif opcao == "2":
        respostas = {}
        ordem = [h for h in base_conhecimento.HIPOTESES if h != "acao"] + ["acao"]
        for hipotese in ordem:
            triagem(hipotese, respostas)
    else:
        print("Encerrado.")


if __name__ == "__main__":
    main()
