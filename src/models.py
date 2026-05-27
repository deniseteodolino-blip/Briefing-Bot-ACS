from pydantic import BaseModel, Field, field_validator
from typing import Optional
import re


def parse_brl_value(value: str) -> Optional[float]:
    """Parse Brazilian Real string to float."""
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    # Remove R$, spaces, and convert comma to dot
    cleaned = re.sub(r'[R$\s]', '', str(value))
    cleaned = cleaned.replace('.', '').replace(',', '.')
    try:
        return float(cleaned)
    except (ValueError, AttributeError):
        return None


class Investidor(BaseModel):
    nome: str
    tipo: str  # PF ou PJ
    documento_tipo: Optional[str] = None  # cpf, cnpj, rnm, passaporte
    documento: Optional[str] = None
    nacionalidade: Optional[str] = None
    estado_civil: Optional[str] = None
    profissao: Optional[str] = None
    endereco: Optional[str] = None
    valor_integralizado: Optional[float] = None
    valor_a_integralizar: Optional[float] = None
    acao: Optional[str] = None  # entrada_nova, saida, alteracao

    @field_validator('tipo')
    @classmethod
    def validate_tipo(cls, v):
        if v not in ('PF', 'PJ'):
            raise ValueError(f'tipo must be PF or PJ, got {v}')
        return v

    @field_validator('valor_integralizado', 'valor_a_integralizar', mode='before')
    @classmethod
    def parse_valor(cls, v):
        return parse_brl_value(v)


class Classificacao(BaseModel):
    estrangeiros: list[dict] = Field(default_factory=list)
    simples_nacional: list[dict] = Field(default_factory=list)
    me_epp: list[dict] = Field(default_factory=list)
    sem_pendencia: list[dict] = Field(default_factory=list)
    erros: list[dict] = Field(default_factory=list)


class ConfiguracaoCNPJ(BaseModel):
    cnpj: str
    razao_social: Optional[str] = None
    porte: Optional[str] = None  # ME, EPP, DEMAIS
    optante_simples: Optional[bool] = None
    data_atualizacao: Optional[str] = None


class BriefingInput(BaseModel):
    spe: str
    acs_num: int
    data_corte: str  # DD/MM/AAAA
    minuta_path: str
    planilha_assinaturas: Optional[str] = None
    atualizacoes: Optional[list[str]] = None  # bullets adicionais


class BriefingOutput(BaseModel):
    message: str
    classificacao: Classificacao
    investidores: list[Investidor]