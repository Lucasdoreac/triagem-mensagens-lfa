"""Motor de inferência por encadeamento para trás. Não conhece o domínio nem faz E/S."""

VERDADEIRA = "verdadeira"
FALSA = "falsa"
INDETERMINADA = "indeterminada"

CONFIRMADA = "confirmada"
REFUTADA = "refutada"
INCONCLUSIVA = "inconclusiva"

_ESTADO_PARA_VALOR = {CONFIRMADA: VERDADEIRA, REFUTADA: FALSA, INCONCLUSIVA: INDETERMINADA}


def _regras_que_concluem(objetivo, base):
    return [r for r in base["REGRAS"] if r["entao"][0] == objetivo]


def _valor_de_fato(fato, valor_esperado, base, respostas, perguntar, rastro, objetivo, regra_id):
    if fato not in respostas:
        respostas[fato] = perguntar(fato)
    resposta = respostas[fato]
    if resposta == "?":
        resultado = INDETERMINADA
    elif resposta == valor_esperado:
        resultado = VERDADEIRA
    else:
        resultado = FALSA
    rastro.append({"objetivo": objetivo, "regra": regra_id, "premissa": fato,
                   "valor": resposta, "conclusao": resultado})
    return resultado


def _valor_de_objetivo(nome, valor_esperado, base, respostas, perguntar, rastro, caminho, objetivo, regra_id):
    estado, _ = _provar(nome, base, respostas, perguntar, rastro, caminho)
    resultado = _ESTADO_PARA_VALOR[estado]
    rastro.append({"objetivo": objetivo, "regra": regra_id, "premissa": nome,
                   "valor": estado, "conclusao": resultado})
    return resultado


def _avaliar_regra(regra, base, respostas, perguntar, rastro, caminho, objetivo):
    resultado_regra = VERDADEIRA
    for nome, valor_esperado in regra["se"]:
        if nome in base["FATOS"]:
            v = _valor_de_fato(nome, valor_esperado, base, respostas, perguntar, rastro, objetivo, regra["id"])
        else:
            v = _valor_de_objetivo(nome, valor_esperado, base, respostas, perguntar, rastro, caminho, objetivo, regra["id"])
        if v == FALSA:
            return FALSA  # curto-circuito: as demais premissas não são perguntadas
        if v == INDETERMINADA:
            resultado_regra = INDETERMINADA
    return resultado_regra


def _provar(objetivo, base, respostas, perguntar, rastro, caminho):
    if objetivo in caminho:
        rastro.append({"objetivo": objetivo, "regra": None, "premissa": None,
                       "valor": "ciclo", "conclusao": INCONCLUSIVA})
        return INCONCLUSIVA, rastro
    regras = _regras_que_concluem(objetivo, base)
    if not regras:
        return INCONCLUSIVA, rastro
    novo_caminho = caminho + (objetivo,)
    todas_falsas = True
    for regra in regras:
        valor = _avaliar_regra(regra, base, respostas, perguntar, rastro, novo_caminho, objetivo)
        if valor == VERDADEIRA:
            return CONFIRMADA, rastro
        if valor != FALSA:
            todas_falsas = False
    return (REFUTADA if todas_falsas else INCONCLUSIVA), rastro


def provar(objetivo, base, respostas, perguntar):
    """Retorna (estado, rastro). `perguntar(fato)` devolve 'sim', 'não' ou '?'.

    `respostas` é um dict que o motor atualiza com cada resposta obtida, para que
    cada fato seja perguntado no máximo uma vez.
    """
    rastro = []
    estado, rastro = _provar(objetivo, base, respostas, perguntar, rastro, ())
    return estado, rastro
