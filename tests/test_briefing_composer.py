import pytest
from src.briefing_composer import (
    compose_briefing,
    _compose_estrangeiros_section,
    _compose_simples_section,
    _compose_me_epp_section,
    _compose_updates_section
)


class TestComposeSections:
    def test_estrangeiros_section_single(self):
        result = _compose_estrangeiros_section([
            {"nome": "FELIPE", "nacionalidade": "argentino"}
        ])

        assert "1. Investidor(es) residente(s) no exterior" in result
        assert "FELIPE" in result
        assert "argentino" in result
        assert "precisa informar" in result  # singular

    def test_estrangeiros_section_multiple(self):
        result = _compose_estrangeiros_section([
            {"nome": "FELIPE", "nacionalidade": "argentino"},
            {"nome": "MARIA", "nacionalidade": "uruguaia"}
        ])

        assert "precisam informar" in result  # plural

    def test_simples_section(self):
        result = _compose_simples_section([
            {"nome": "EMPRESA LTDA", "razao_social": "Empresa Ltda", "cnpj": "12345678000199"}
        ])

        assert "2. Empresa(s) optante(s) pelo Simples Nacional" in result
        assert "NÃO pode ingressar" in result
        assert "EMPRESA LTDA" in result

    def test_me_epp_section(self):
        result = _compose_me_epp_section([
            {"nome": "ME LTDA", "razao_social": "ME Ltda", "cnpj": "12345678000199", "porte": "ME"}
        ])

        assert "3. Empresa(s) enquadrada(s) como ME ou EPP" in result
        assert "precisa alterar" in result
        assert "art. 3º, §4º, VII da Lei Complementar 123/06" in result

    def test_updates_section(self):
        result = _compose_updates_section([
            "Entrada de novo investidor",
            "Atualização de capital"
        ])

        assert "Principais atualizações da ACS:" in result
        assert "Entrada de novo investidor" in result


class TestComposeBriefing:
    def test_empty_classificacao(self):
        result = compose_briefing(
            spe="SPE Teste",
            acs_num=1,
            data_corte="27/05/2026",
            classificacao={}
        )

        assert "SPE Teste" in result
        assert "1ª ACS" in result
        assert "27/05/2026" in result

    def test_with_estrangeiros(self):
        result = compose_briefing(
            spe="SPE Foz",
            acs_num=2,
            data_corte="27/05/2026",
            classificacao={
                "estrangeiros": [{"nome": "FELIPE", "nacionalidade": "argentino"}],
                "simples_nacional": [],
                "me_epp": [],
                "sem_pendencia": []
            }
        )

        assert "FELIPE" in result
        assert "argentino" in result