import pytest
from unittest.mock import patch, MagicMock
from src.cnpj_classifier import classify_pj, classify_investidores, _classify_cnpj_result


class TestClassifyPJ:
    @patch('src.cnpj_classifier.get_cached_cnpj')
    @patch('src.cnpj_classifier.requests.get')
    def test_classify_simples_nacional(self, mock_get, mock_cache):
        mock_cache.return_value = None
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "razao_social": "Empresa Teste LTDA",
            "porte": "ME",
            "optante_simples": True
        }
        mock_get.return_value = mock_response

        result = classify_pj("12345678000199")

        assert result['bucket'] == 'simples_nacional'
        assert result['optante_simples'] == True

    @patch('src.cnpj_classifier.get_cached_cnpj')
    @patch('src.cnpj_classifier.requests.get')
    def test_classify_me_epp(self, mock_get, mock_cache):
        mock_cache.return_value = None
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "razao_social": "Empresa ME LTDA",
            "porte": "ME",
            "optante_simples": False
        }
        mock_get.return_value = mock_response

        result = classify_pj("12345678000199")

        assert result['bucket'] == 'me_epp'
        assert result['porte'] == 'ME'

    @patch('src.cnpj_classifier.get_cached_cnpj')
    @patch('src.cnpj_classifier.requests.get')
    def test_classify_demais(self, mock_get, mock_cache):
        mock_cache.return_value = None
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "razao_social": "Empresa DEMAIS SA",
            "porte": "DEMAIS",
            "optante_simples": False
        }
        mock_get.return_value = mock_response

        result = classify_pj("12345678000199")

        assert result['bucket'] == 'sem_pendencia'
        assert result['porte'] == 'DEMAIS'

    @patch('src.cnpj_classifier.get_cached_cnpj')
    def test_use_cache(self, mock_cache):
        mock_cache.return_value = {
            "razao_social": "Empresa Cache",
            "porte": "DEMAIS",
            "optante_simples": False
        }

        result = classify_pj("12345678000199")

        assert result['bucket'] == 'sem_pendencia'
        mock_cache.assert_called_once()


class TestClassifyInvestidores:
    def test_classify_estrangeiro(self):
        from src.models import Investidor

        investidores = [
            Investidor(
                nome="CRISTIAN MOLINARI",
                tipo="PF",
                documento_tipo="passaporte",
                documento="AA123456",
                nacionalidade="argentino"
            )
        ]

        result = classify_investidores(investidores)

        assert len(result['estrangeiros']) == 1
        assert result['estrangeiros'][0]['nome'] == "CRISTIAN MOLINARI"
        assert result['estrangeiros'][0]['nacionalidade'] == "argentino"

    def test_classify_brasileiro(self):
        from src.models import Investidor

        investidores = [
            Investidor(
                nome="JOÃO SILVA",
                tipo="PF",
                documento_tipo="cpf",
                documento="12345678900",
                nacionalidade="brasileiro"
            )
        ]

        result = classify_investidores(investidores)

        assert len(result['sem_pendencia']) == 1
        assert result['sem_pendencia'][0]['nome'] == "JOÃO SILVA"