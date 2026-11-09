"""Base de conhecimento: fatos, regras SE-ENTÃO e hipóteses. Só dados, sem inferência."""

TITULO = "Triagem de mensagens suspeitas (protótipo didático, regras sem validação)."

FATOS = {
    "urgencia": {"pergunta": "A mensagem exige ação imediata ou ameaça bloquear conta ou cartão?"},
    "pede_senha_ou_codigo": {"pergunta": "A mensagem pede senha, token ou código de verificação?"},
    "pede_transferencia_pix": {"pergunta": "A mensagem pede transferência, pagamento ou 'teste' de Pix?"},
    "link_suspeito": {"pergunta": "Há link cujo endereço não confere com o site oficial ou é encurtado?"},
    "nao_solicitado": {"pergunta": "Você não pediu este contato (o remetente entrou em contato primeiro)?"},
}

REGRAS = [
    {
        "id": "R1",
        "se": [("pede_senha_ou_codigo", "sim"), ("nao_solicitado", "sim")],
        "entao": ("phishing", "sim"),
        "fonte": "CERT.br, Cartilha de Segurança para Internet, fascículo Phishing e Outros Golpes (2022); confirmar no PDF oficial",
        "estado": "sem validação",
    },
    {
        "id": "R2",
        "se": [("link_suspeito", "sim"), ("urgencia", "sim")],
        "entao": ("phishing", "sim"),
        "fonte": "CERT.br, Cartilha de Segurança para Internet, fascículo Phishing e Outros Golpes (2022); confirmar no PDF oficial",
        "estado": "sem validação",
    },
    {
        "id": "R3",
        "se": [("pede_transferencia_pix", "sim"), ("nao_solicitado", "sim")],
        "entao": ("golpe_pix", "sim"),
        "fonte": "Febraban e Banco Central: bancos não pedem Pix de teste nem transferência por contato não solicitado; confirmar nos canais oficiais",
        "estado": "sem validação",
    },
    {
        "id": "R4",
        "se": [("phishing", "sim")],
        "entao": ("acao", "nao_informar_dados"),
        "fonte": "Regra de decisão derivada de R1 e R2; a validar com a Coordenação do curso",
        "estado": "sem validação",
    },
    {
        "id": "R5",
        "se": [("golpe_pix", "sim")],
        "entao": ("acao", "nao_transferir_e_ligar_ao_banco"),
        "fonte": "Regra de decisão derivada de R3; a validar com a Coordenação do curso",
        "estado": "sem validação",
    },
]

HIPOTESES = {
    "phishing": {"descricao": "Phishing (tentativa de roubar senha ou código)"},
    "golpe_pix": {"descricao": "Golpe de Pix (pedido de transferência por contato não solicitado)"},
    "acao": {"descricao": "Ação recomendada"},
}
