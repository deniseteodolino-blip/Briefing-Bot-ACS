import os
import re


def compose_briefing(
    spe: str,
    acs_num: int,
    data_corte: str,
    classificacao: dict,
    atualizacoes: list[str] = None,
    planilha_assinaturas: str = None
) -> str:
    """
    Compose final briefing message using the standard template.

    Template sections:
    1. Header with data_corte
    2. Control link (optional)
    3. Foreign investors section
    4. Simples Nacional section
    5. ME/EPP section
    6. Updates section (always included)
    7. Footer
    """
    # Format data_corte to Brazilian date format
    match = re.search(r'(\d{2})/(\d{2})/(\d{4})', data_corte)
    if match:
        meses = {
            "01": "janeiro", "02": "fevereiro", "03": "março", "04": "abril",
            "05": "maio", "06": "junho", "07": "julho", "08": "agosto",
            "09": "setembro", "10": "outubro", "11": "novembro", "12": "dezembro"
        }
        mes_extenso = meses.get(match.group(2), match.group(2))
        ano = match.group(3)
        data_formatada = f"{match.group(1)} de {mes_extenso} de {ano}"
    else:
        data_formatada = data_corte

    # Build sections
    sections = []

    # Section 1: Estrangeiros
    estrangeiros = classificacao.get('estrangeiros', [])
    if estrangeiros:
        nomes = "\n".join([f"\t• {e['nome']}" for e in estrangeiros])
        section = f"""1. Investidores residentes no exterior
{nomes}

Devem informar:
RNM e endereço no Brasil; ou
Procurador residente no Brasil (com CPF e endereço).

Caso não indiquem, pode ser sugerido o Ambrosi como procurador. Se, ainda assim, não houver indicação, não poderão ingressar nesta ACS.

Segue o modelo de procuração: https://docs.google.com/document/d/1dqJb9rmC9ba21Ach2fBvTKgoBwjVfUfg/edit#heading=h.yd8z8c23m0ia

Formas de assinatura da procuração:
1 Assinatura digital (recomendado)
Via Gov.br (nível Prata ou Ouro) ou e-CPF
Vantagem: sem custo e dispensa apostilamento e tradução juramentada
2 Assinatura física no exterior
Exige Apostila de Haia (no país de origem) + tradução juramentada no Brasil
Impacto: processo mais caro e demorado
Confirmar se possuem acesso ao Gov.br (Prata/Ouro) ou e-CPF para evitar custos e prazos adicionais."""
        sections.append(section)

    # Section 2: Simples Nacional
    simples = classificacao.get('simples_nacional', [])
    if simples:
        nomes = "\n".join([f"\t• {s['razao_social'] or s['nome']}" for s in simples])
        count = len(simples)
        verb = "Não pode" if count == 1 else "Não podem"
        verb2 = "alteração" if count == 1 else "alterações"

        section = f"""2. Empresas optantes pelo Simples Nacional:
As empresas abaixo {verb} ingressar nesta ACS sem alteração do regime tributário:
{nomes}.

Necessária a {verb2} do regime tributário para poderem ingressar na próxima ACS."""
        sections.append(section)

    # Section 3: ME/EPP
    me_epp = classificacao.get('me_epp', [])
    if me_epp:
        nomes = "\n".join([f"\t• {s['razao_social'] or s['nome']}" for s in me_epp])

        section = f"""3. Empresas enquadradas como ME ou EPP:
{nomes}

Será necessário realizar o enquadramento para o porte "DEMAIS".

Motivo:
Conforme o art. 3º, §4º, VII da LC 123/06, empresas enquadradas como ME ou EPP não podem participar do capital de outra pessoa jurídica nessas condições.

Próximos passos:
Entrar em contato com o contador para providenciar o desenquadramento o quanto antes. Sem essa regularização, não será possível concluir a inclusão nessa ACS."""
        sections.append(section)

    # Section 4: Updates - sempre incluir com 3 bullets padrão
    updates_default = [
        f"Entrada de investidores (conforme movimentações ocorridas até {data_formatada}) e saída da Seazone;",
        f"Valores integralizados e a integralizar por cada sócio atualizados até {data_formatada};",
        "Inclusão de tópico referente à reestruturação das cláusulas do contrato social, a fim de prever disposições mais robustas e evitar que o contrato permaneça apenas com as cláusulas simplificadas da constituição."
    ]
    items = "\n".join([f"\t• {a}" for a in updates_default])
    section = f"""Principais atualizações da ACS:
{items}"""
    sections.append(section)

    # Build final message
    header = f"""Boa tarde!

Por gentileza, solicitamos a validação de todos os investidores na {acs_num}ª ACS de {spe}, considerando a data de corte em {data_formatada}."""

    if planilha_assinaturas:
        header += f"\n\nControle de assinaturas: {planilha_assinaturas}"

    pendencias_header = "\n\nPendências a serem tratadas pelo CSI:\n\n"

    body = "\n\n".join(sections)

    footer = "\n\nFico à disposição para qualquer dúvida. Obrigada!"

    return header + pendencias_header + body + footer