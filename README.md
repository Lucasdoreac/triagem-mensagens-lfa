# Triagem de mensagens suspeitas

Sistema especialista didático, em terminal, para triagem de mensagens que podem ser golpes digitais (phishing e golpe de Pix). Projeto final de Linguagens Formais e Autômatos (UDF), "Projeto para AI". Especificação em `../rfc/RFC-001-sistema-especialista-lfa.md`.

**As regras não foram validadas por humanos.** A conclusão é uma hipótese para confirmação pelo canal oficial do banco. O sistema não lê o conteúdo da mensagem, não visita links e não acessa contas.

## Escopo

- **Quem consulta:** qualquer pessoa que recebeu uma mensagem suspeita e quer uma triagem antes de agir.
- **Decisão apoiada:** qual hipótese é provável (phishing ou golpe de Pix) e qual ação recomendar.
- **Fora do escopo:** ler o conteúdo da mensagem, verificar links na internet, consultar bases de fraude, acessar contas ou substituir o canal oficial do banco.

## Executar

Requer Python 3.10 ou superior. Usa só a biblioteca padrão.

```sh
python3 cli.py              # menu: 1 = ação recomendada, 2 = relatório completo
python3 -m unittest -v      # testes
```

Respostas: `s` (sim), `n` (não) ou `?` (desconhecido). Espaços e caixa são aceitos. Outras entradas são recusadas.

## Arquitetura

- `base.py`: fatos, regras SE-ENTÃO, hipóteses e fontes. Só dados.
- `motor.py`: encadeamento para trás com semântica de três valores e rastro. Não conhece o domínio nem faz entrada e saída.
- `cli.py`: perguntas no terminal e apresentação da explicação.
- `test_motor.py`: testes T1 a T8 e checagens RQ1, RQ2, RQ9 e RQ10 do RFC.
- `video/`: composição HyperFrames (HTML e GSAP) que explica o sistema. Renderizada em `video/renders/triagem-mensagens.mp4` (1920x1080, 70 s, sem áudio).

## Base de regras

| Regra | SE | ENTÃO | Fonte | Estado |
|---|---|---|---|---|
| R1 | `pede_senha_ou_codigo = sim` E `nao_solicitado = sim` | `phishing = sim` | CERT.br, fascículo Phishing e Outros Golpes (a confirmar no PDF) | sem validação |
| R2 | `link_suspeito = sim` E `urgencia = sim` | `phishing = sim` | CERT.br, fascículo Phishing e Outros Golpes (a confirmar no PDF) | sem validação |
| R3 | `pede_transferencia_pix = sim` E `nao_solicitado = sim` | `golpe_pix = sim` | Febraban e Banco Central (a confirmar em bcb.gov.br) | sem validação |
| R4 | `phishing = sim` | `acao = nao_informar_dados` | decisão a validar com a Coordenação | sem validação |
| R5 | `golpe_pix = sim` | `acao = nao_transferir_e_ligar_ao_banco` | decisão a validar com a Coordenação | sem validação |

## Casos de demonstração

- **Caso A (confirmado):** `pede_senha_ou_codigo = sim` e `nao_solicitado = sim`. A CLI conclui `acao = nao_informar_dados` por R4 e R1, sem perguntar os outros três fatos.
- **Caso B (inconclusivo):** `pede_senha_ou_codigo = sim`, `nao_solicitado = ?`, `link_suspeito = ?`, `urgencia = ?`. `phishing` e `acao` ficam inconclusivas. A CLI mostra quais fatos faltaram.

## Registro de testes

Saída completa de `python3 -m unittest -v` em `registro-testes.txt`: 15 testes, todos aprovados.

| Cenário | Entrada | Resultado esperado | Regra verificada | Obtido |
|---|---|---|---|---|
| Confirmação (T1) | senha = sim; não solicitado = sim | ação confirmada, só 2 perguntas | R1, R4 | confirmada |
| Desconhecido (T2) | senha = sim; não solicitado = ? | phishing inconclusiva, não refutada | R1 | inconclusiva |
| Rastro (T3) | pedido de Pix = sim; não solicitado = sim | rastro com R3 e os dois fatos | R3 | confirmada |
| Ciclo (T5) | regras x→y e y→x | termina como inconclusiva | ciclo | inconclusiva |
| Fato compartilhado (T6) | fato em duas regras | perguntado uma vez | r1, r2 | refutada, 1 pergunta |
| Premissa falsa (T7) | senha = não; link = não | refutada, sem perguntar o resto | R1, R2 | refutada |
| Sem regra (T8) | hipótese sem regra | inconclusiva, nunca refutada | — | inconclusiva |
| Cobertura R2 | senha = não; link = sim; urgência = sim | confirmada | R2 | confirmada |
| Cobertura R5 | senha e link = não; Pix = sim; não solicitado = sim | ação confirmada | R4 falsa, R3, R5 | confirmada |
| Entrada inválida | "talvez" e depois "s" | pede de novo e aceita "s" | — | sim |

## Material-base

- Profa. Kadidja Valéria, slide "Hands On! Modelando o seu Sistema" e PDF "Sistemas Especialistas" (aula de 27/10/2026): estrutura de base de conhecimento, motor e encadeamento para trás.
- Guia de entregáveis da disciplina, copiado em `docs/guia-professora.md`.

## Limitações

- As regras são escritas à mão e não foram validadas. Um golpe sem link e sem pedido de senha ou Pix pode aparecer como "refutada" (falso negativo).
- Fontes do CERT.br e do Banco Central foram obtidas por busca web; o PDF oficial ainda precisa ser lido.

## Melhoria proposta

Substituir a pergunta manual por leitura automática de campos (remetente, texto, domínio do link), mantendo a base separada e o rastro de explicação.
