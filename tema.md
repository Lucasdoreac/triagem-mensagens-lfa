# Tema: triagem de mensagens suspeitas (cibergolpes)

**Aluno:** Lucas Cardoso · **Disciplina:** Linguagens Formais e Autômatos (UDF) · **Validação:** 10/11/2026

## Problema real

Pessoas recebem mensagens que parecem vir de banco ou de conhecido, pedindo senha, código ou Pix. Não há ferramenta simples que guie a decisão com regras explícitas e explique o motivo. O sistema faz essa triagem: pergunta sinais observáveis, aplica regras e mostra a conclusão e a ação recomendada.

## Por que é sistema especialista

O sistema não processa dados fixos. Ele pergunta só o que a regra precisa, encadeia regras para trás a partir de um objetivo (a ação) e explica o caminho. Desconhecido não vira "não": o resultado fica inconclusivo e mostra o fato que falta.

## Base de conhecimento (5 fatos, 5 regras)

| Regra | SE | ENTÃO | Fonte | Estado |
|---|---|---|---|---|
| R1 | pede senha ou código = sim E não solicitado = sim | phishing = sim | CERT.br, fascículo Phishing e Outros Golpes | sem validação |
| R2 | link suspeito = sim E urgência = sim | phishing = sim | CERT.br, fascículo Phishing e Outros Golpes | sem validação |
| R3 | pede Pix ou transferência = sim E não solicitado = sim | golpe de Pix = sim | Febraban e Banco Central | sem validação |
| R4 | phishing = sim | ação = não informar dados | a validar com a Coordenação | sem validação |
| R5 | golpe de Pix = sim | ação = não transferir e ligar ao banco | a validar com a Coordenação | sem validação |

## Simulação (backward chaining)

- **Caso A (confirmado):** senha = sim, não solicitado = sim. A ação "não informar dados" é confirmada por R4 e R1. Só duas perguntas são feitas.
- **Caso B (inconclusivo):** senha = sim, e as demais respostas são "?". R1 fica indeterminada, phishing e ação ficam inconclusivas, e o sistema lista os fatos que faltam.

## Estado

- Código em `triagem-mensagens/` (base, motor, CLI), 15 testes passando.
- README com escopo, limitações e melhoria proposta.
- Vídeo de demonstração (76 s, sem narração).

## Pendências honestas

- As fontes do CERT.br e do Banco Central ainda não foram conferidas no documento original.
- As regras não foram validadas por humanos.
