import pytest
from pathlib import Path
from src.minuta_reader import load_minuta, extract_investidores
from src.models import Investidor, InvalidExtractionError


class TestLoadMinuta:
    def test_load_nonexistent_file(self):
        with pytest.raises(FileNotFoundError):
            load_minuta("nonexistent.pdf")

    def test_unsupported_file_type(self, tmp_path):
        test_file = tmp_path / "test.txt"
        test_file.write_text("dummy content")

        with pytest.raises(ValueError) as exc_info:
            load_minuta(str(test_file))

        assert "Unsupported file type" in str(exc_info.value)


class TestInvestidorModel:
    def test_valid_investidor_pf(self):
        inv = Investidor(
            nome="FULANO DE TAL",
            tipo="PF",
            documento_tipo="cpf",
            documento="12345678900",
            nacionalidade="brasileiro",
            estado_civil="casado",
            profissao="empresário",
            valor_integralizado=50000.00
        )
        assert inv.nome == "FULANO DE TAL"
        assert inv.tipo == "PF"

    def test_valid_investidor_pj(self):
        inv = Investidor(
            nome="EMPRESA LTDA",
            tipo="PJ",
            documento_tipo="cnpj",
            documento="12345678000199",
            valor_integralizado=100000.00
        )
        assert inv.tipo == "PJ"

    def test_invalid_tipo(self):
        with pytest.raises(ValueError):
            Investidor(nome="TEST", tipo="INVALID")

    def test_optional_fields(self):
        inv = Investidor(nome="TEST", tipo="PF")
        assert inv.documento_tipo is None
        assert inv.nacionalidade is None
        assert inv.valor_integralizado is None