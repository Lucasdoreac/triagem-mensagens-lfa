"""Testes T1 a T8 do RFC-001 e checagens de RQ1, RQ2, RQ4 e RQ9."""

import ast
import pathlib
import sys
import unittest

import base as base_conhecimento
import cli
from motor import provar, CONFIRMADA, REFUTADA, INCONCLUSIVA

DIR = pathlib.Path(__file__).parent


def base_real():
    return {"FATOS": base_conhecimento.FATOS, "REGRAS": base_conhecimento.REGRAS}


class Espiao:
    """Responde com um dicionário e registra cada fato perguntado, na ordem."""

    def __init__(self, respostas):
        self.respostas = respostas
        self.perguntados = []

    def __call__(self, fato):
        self.perguntados.append(fato)
        return self.respostas.get(fato, "?")


class MotorTest(unittest.TestCase):

    def test_T1_acao_por_phishing_pergunta_so_os_fatos_necessarios(self):
        espiao = Espiao({"pede_senha_ou_codigo": "sim", "nao_solicitado": "sim"})
        estado, rastro = provar("acao", base_real(), {}, espiao)
        self.assertEqual(estado, CONFIRMADA)
        self.assertEqual(espiao.perguntados, ["pede_senha_ou_codigo", "nao_solicitado"])
        self.assertTrue(any(l["regra"] == "R1" for l in rastro))
        self.assertTrue(any(l["regra"] == "R4" for l in rastro))

    def test_T2_resposta_desconhecida_nao_vira_nao(self):
        espiao = Espiao({"pede_senha_ou_codigo": "sim", "nao_solicitado": "?"})
        estado, _ = provar("phishing", base_real(), {}, espiao)
        self.assertEqual(estado, INCONCLUSIVA)
        self.assertNotEqual(estado, REFUTADA)

    def test_T3_rastro_contem_regra_e_fatos_que_sustentam(self):
        espiao = Espiao({"pede_transferencia_pix": "sim", "nao_solicitado": "sim"})
        _, rastro = provar("golpe_pix", base_real(), {}, espiao)
        premissas = {(l["regra"], l["premissa"], l["valor"]) for l in rastro}
        self.assertIn(("R3", "pede_transferencia_pix", "sim"), premissas)
        self.assertIn(("R3", "nao_solicitado", "sim"), premissas)

    def test_T5_ciclo_termina_e_fica_inconclusivo(self):
        base = {
            "FATOS": {},
            "REGRAS": [
                {"id": "Ra", "se": [("y", "sim")], "entao": ("x", "sim")},
                {"id": "Rb", "se": [("x", "sim")], "entao": ("y", "sim")},
            ],
        }
        estado, rastro = provar("x", base, {}, Espiao({}))
        self.assertEqual(estado, INCONCLUSIVA)
        self.assertTrue(any(l["valor"] == "ciclo" for l in rastro))

    def test_T6_fato_compartilhado_e_perguntado_uma_vez(self):
        base = {
            "FATOS": {"u": {}, "a": {}, "b": {}},
            "REGRAS": [
                {"id": "r1", "se": [("u", "sim"), ("a", "sim")], "entao": ("h", "sim")},
                {"id": "r2", "se": [("u", "sim"), ("b", "sim")], "entao": ("h", "sim")},
            ],
        }
        espiao = Espiao({"u": "não"})
        estado, _ = provar("h", base, {}, espiao)
        self.assertEqual(espiao.perguntados.count("u"), 1)
        self.assertEqual(estado, REFUTADA)

    def test_T7_fato_falso_refuta_sem_perguntar_o_resto_da_regra(self):
        espiao = Espiao({"pede_senha_ou_codigo": "não", "link_suspeito": "não"})
        estado, rastro = provar("phishing", base_real(), {}, espiao)
        self.assertEqual(estado, REFUTADA)
        self.assertNotIn("nao_solicitado", espiao.perguntados)
        self.assertNotIn("urgencia", espiao.perguntados)
        self.assertTrue(any(l["regra"] == "R1" and l["premissa"] == "pede_senha_ou_codigo" and l["valor"] == "não"
                            for l in rastro))

    def test_T8_hipotese_sem_regra_e_inconclusiva_nao_refutada(self):
        base = {"FATOS": {}, "REGRAS": []}
        estado, _ = provar("sem_regra", base, {}, Espiao({}))
        self.assertEqual(estado, INCONCLUSIVA)


class CoberturaDasRegrasTest(unittest.TestCase):
    """Cada uma das seis regras é usada ao menos uma vez em um teste (exigência do guia da professora)."""

    def test_R2_phishing_por_link_suspeito_e_urgencia(self):
        espiao = Espiao({"pede_senha_ou_codigo": "não", "link_suspeito": "sim", "urgencia": "sim"})
        estado, rastro = provar("phishing", base_real(), {}, espiao)
        self.assertEqual(estado, CONFIRMADA)
        self.assertTrue(any(l["regra"] == "R2" for l in rastro))

    def test_R5_acao_de_golpe_pix(self):
        espiao = Espiao({"pede_senha_ou_codigo": "não", "link_suspeito": "não",
                         "pede_transferencia_pix": "sim", "nao_solicitado": "sim"})
        estado, rastro = provar("acao", base_real(), {}, espiao)
        self.assertEqual(estado, CONFIRMADA)
        self.assertTrue(any(l["regra"] == "R5" for l in rastro))


class CliTest(unittest.TestCase):

    def test_entrada_invalida_pede_de_novo(self):
        from unittest import mock
        with mock.patch("builtins.input", side_effect=["talvez", "s"]), \
                mock.patch("builtins.print"):
            self.assertEqual(cli.perguntar_terminal("nao_solicitado"), "sim")

    def test_T4_entradas_aceitas_e_recusadas(self):
        self.assertEqual(cli.normalizar_resposta(" S "), "sim")
        self.assertEqual(cli.normalizar_resposta("n"), "não")
        self.assertEqual(cli.normalizar_resposta("?"), "?")
        self.assertIsNone(cli.normalizar_resposta("talvez"))
        self.assertIsNone(cli.normalizar_resposta(""))


class SeparacaoTest(unittest.TestCase):

    def test_RQ1_base_tem_no_minimo_3_fatos_e_5_regras(self):
        self.assertGreaterEqual(len(base_conhecimento.FATOS), 3)
        self.assertGreaterEqual(len(base_conhecimento.REGRAS), 5)

    def test_RQ2_motor_e_cli_nao_contem_literais_do_dominio(self):
        dominio = ["phishing", "pix", "senha", "urgência", "urgencia", "link", "febraban", "golpe"]
        for nome in ("motor.py", "cli.py"):
            fonte = (DIR / nome).read_text(encoding="utf-8").casefold()
            for termo in dominio:
                self.assertNotIn(termo, fonte, f"{termo} aparece em {nome}")

    def test_RQ9_so_biblioteca_padrao(self):
        for nome in ("base.py", "motor.py", "cli.py"):
            arvore = ast.parse((DIR / nome).read_text(encoding="utf-8"))
            for no in ast.walk(arvore):
                if isinstance(no, ast.Import):
                    modulos = [a.name.split(".")[0] for a in no.names]
                elif isinstance(no, ast.ImportFrom):
                    modulos = [(no.module or "").split(".")[0]]
                else:
                    continue
                for modulo in modulos:
                    if modulo in ("base", "motor", "cli", ""):
                        continue
                    self.assertIn(modulo, sys.stdlib_module_names, f"{modulo} em {nome}")

    def test_RQ10_toda_regra_tem_fonte_e_estado(self):
        for regra in base_conhecimento.REGRAS:
            self.assertTrue(regra.get("fonte"))
            self.assertIn(regra.get("estado"), ("sem validação", "validada"))


if __name__ == "__main__":
    unittest.main()
