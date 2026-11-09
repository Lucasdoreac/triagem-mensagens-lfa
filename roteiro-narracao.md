# Roteiro de narração e tempos

Duração total: 136.7 s. Ritmo de referência: 2.4 palavras por segundo, mais 1.5 s de folga por cena.

| Início | Duração | Locutor | Texto narrado |
|---|---|---|---|
| 000.0 s | 12.8 s | Nicolas | Oi, pessoal. Nosso projeto de Linguagens Formais e Autômatos é um sistema especialista para triagem de mensagens suspeitas: golpes que pedem senha ou Pix. |
| 012.8 s | 10.4 s | Nicolas | Imagine uma mensagem dizendo que a conta vai ser bloqueada hoje e pedindo a senha. O sistema não sabe nada sobre ela. Então ele precisa perguntar. |
| 023.2 s | 15.5 s | Deivid | Primeiro, a base de conhecimento. Ela guarda só dados: cada regra tem premissas, uma conclusão e uma fonte. Esta é a R1: se a mensagem pede senha e o contato não foi solicitado, é phishing. |
| 038.7 s | 9.6 s | Deivid | Agora o sistema pergunta só o que a regra precisa. Aqui, duas respostas bastam. As outras três perguntas nem são feitas. |
| 048.3 s | 9.8 s | Deivid | O motor avalia as premissas da esquerda para a direita. Se uma for falsa, ele para ali: a regra é falsa e nada mais é perguntado. |
| 058.1 s | 14.3 s | Deivid | A inferência é para trás. Parte da ação recomendada, acha a regra que a conclui e busca os fatos que a sustentam. A ação exige phishing; phishing exige a R1 e os dois fatos dela. |
| 072.4 s | 10.4 s | Deivid | Quando uma premissa é outra hipótese, o motor prova essa hipótese antes. Se o objetivo já está na cadeia, o ciclo para e o resultado é inconclusivo. |
| 082.8 s | 12.3 s | Lucas | Agora, um caso sem resposta suficiente. Uma das respostas é interrogação. Desconhecido não vira não: a regra fica indeterminada e a ação fica inconclusiva. |
| 095.1 s | 8.9 s | Lucas | A explicação mostra cada regra usada, o fato e o valor encontrado. Quem usa vê o caminho inteiro, e não só o resultado. |
| 104.0 s | 11.1 s | Lucas | Os quinze testes automatizados cobrem isso: a resposta desconhecida, o ciclo, o fato repetido e a entrada inválida. Todos passam. |
| 115.1 s | 14.4 s | Lucas | O sistema tem cinco regras SE-ENTÃO, cada uma com fonte. Faz inferência para trás e explica o caminho. É um protótipo didático: cobre os casos que as regras descrevem, e não todos os golpes possíveis. |
| 129.5 s | 7.2 s | Lucas | Obrigado. Fontes: CERT.br, Febraban e Banco Central. |

## Trechos de código mostrados

### 023.2 s · base.py · linhas 14–20
```python
  14      {
  15          "id": "R1",
  16          "se": [("pede_senha_ou_codigo", "sim"), ("nao_solicitado", "sim")],
  17          "entao": ("phishing", "sim"),
  18          "fonte": "CERT.br, Cartilha de Segurança para Internet, fascículo Phishing e Outros Golpes (2022); confirmar no PDF oficial",
  19          "estado": "sem validação",
  20      },
```

### 048.3 s · motor.py · linhas 41–52
```python
  41  def _avaliar_regra(regra, base, respostas, perguntar, rastro, caminho, objetivo):
  42      resultado_regra = VERDADEIRA
  43      for nome, valor_esperado in regra["se"]:
  44          if nome in base["FATOS"]:
  45              v = _valor_de_fato(nome, valor_esperado, base, respostas, perguntar, rastro, objetivo, regra["id"])
  46          else:
  47              v = _valor_de_objetivo(nome, valor_esperado, base, respostas, perguntar, rastro, caminho, objetivo, regra["id"])
  48          if v == FALSA:
  49              return FALSA  # curto-circuito: as demais premissas não são perguntadas
  50          if v == INDETERMINADA:
  51              resultado_regra = INDETERMINADA
  52      return resultado_regra
```

### 072.4 s · motor.py · linhas 55–70
```python
  55  def _provar(objetivo, base, respostas, perguntar, rastro, caminho):
  56      if objetivo in caminho:
  57          rastro.append({"objetivo": objetivo, "regra": None, "premissa": None,
  58                         "valor": "ciclo", "conclusao": INCONCLUSIVA})
  59          return INCONCLUSIVA, rastro
  60      regras = _regras_que_concluem(objetivo, base)
  61      if not regras:
  62          return INCONCLUSIVA, rastro
  63      novo_caminho = caminho + (objetivo,)
  64      todas_falsas = True
  65      for regra in regras:
  66          valor = _avaliar_regra(regra, base, respostas, perguntar, rastro, novo_caminho, objetivo)
  67          if valor == VERDADEIRA:
  68              return CONFIRMADA, rastro
  69          if valor != FALSA:
  70              todas_falsas = False
```

### 095.1 s · cli.py · linhas 27–31
```python
  27  def explicar(estado, rastro):
  28      for linha in rastro:
  29          if linha["regra"] is None:
  30              continue
  31          print(f"  {linha['regra']}: {linha['premissa']} = {linha['valor']} -> {linha['conclusao']}")
```

### 104.0 s · test_motor.py · linhas 41–45
```python
  41      def test_T2_resposta_desconhecida_nao_vira_nao(self):
  42          espiao = Espiao({"pede_senha_ou_codigo": "sim", "nao_solicitado": "?"})
  43          estado, _ = provar("phishing", base_real(), {}, espiao)
  44          self.assertEqual(estado, INCONCLUSIVA)
  45          self.assertNotEqual(estado, REFUTADA)
```

