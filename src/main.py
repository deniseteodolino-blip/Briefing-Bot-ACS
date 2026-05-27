import argparse
import sys
from pathlib import Path

from dotenv import load_dotenv

from minuta_reader import extract_pendencias_with_retry, InvalidExtractionError
from cnpj_classifier import classify_pj
from briefing_composer import compose_briefing
from slack_output import create_private_canvas, format_message_for_copy

load_dotenv()


def run(spe: str, acs_num: int, data_corte: str, minuta_path: str,
        planilha: str = None, atualizacoes: list = None, force_refresh: bool = False):
    """
    Run the briefing bot workflow.

    1. Extract pendencies from minuta (red text / qualification section)
    2. Classify each PJ via CNPJ API
    3. Compose briefing message
    4. Create Slack DM for review
    """
    print(f"\n{'='*60}")
    print(f"BRIEFING BOT ACS - {spe or 'Minuta'}")
    print(f"{'='*60}\n")

    # Step 1: Extract pendencies from minuta
    print(f"[1/4] Extraindo pendências da minuta: {minuta_path}")
    try:
        pendencias = extract_pendencias_with_retry(minuta_path)

        # Use extracted data if available, otherwise use provided values
        if pendencias.get('spe') and not spe:
            spe = pendencias['spe']
        if pendencias.get('acs_num') and not acs_num:
            acs_num = pendencias['acs_num']
        if pendencias.get('data_corte') and not data_corte:
            data_corte = pendencias['data_corte']

        print(f"  → Estrangeiros: {len(pendencias['estrangeiros'])}")
        print(f"  → Simples Nacional: {len(pendencias['simples_nacional'])}")
        print(f"  → ME/EPP: {len(pendencias['me_epp'])}")

    except Exception as e:
        print(f"ERRO: Falha ao extrair pendências: {e}")
        sys.exit(1)

    # Step 2: Classify PJ investors via CNPJ API
    print(f"\n[2/4] Classificando empresas...")

    classificacao = {
        "estrangeiros": pendencias.get('estrangeiros', []),
        "simples_nacional": [],
        "me_epp": [],
        "sem_pendencia": [],
        "erros": []
    }

    # Classify Simples Nacional companies
    for empresa in pendencias.get('simples_nacional', []):
        cnpj = empresa.get('cnpj')
        if cnpj:
            cnpj_clean = ''.join(c for c in cnpj if c.isdigit())
            print(f"\nConsultando CNPJ: {empresa['nome']}")
            result = classify_pj(cnpj_clean, force_refresh)
            if result['bucket'] == 'simples_nacional':
                classificacao['simples_nacional'].append({
                    "nome": empresa['nome'],
                    "cnpj": cnpj_clean,
                    "razao_social": result.get('razao_social'),
                    "optante_simples": result.get('optante_simples')
                })
            elif result['bucket'] == 'me_epp':
                result['nome'] = empresa['nome']
                classificacao['me_epp'].append(result)
            elif result['bucket'] == 'erro':
                result['nome'] = empresa['nome']
                classificacao['erros'].append(result)

    # Classify ME/EPP companies
    for empresa in pendencias.get('me_epp', []):
        cnpj = empresa.get('cnpj')
        if cnpj:
            cnpj_clean = ''.join(c for c in cnpj if c.isdigit())
            if not any(e.get('cnpj') == cnpj_clean for e in classificacao['me_epp']):
                print(f"\nConsultando CNPJ: {empresa['nome']}")
                result = classify_pj(cnpj_clean, force_refresh)
                result['nome'] = empresa['nome']
                if result['bucket'] == 'me_epp':
                    classificacao['me_epp'].append(result)
                elif result['bucket'] == 'simples_nacional':
                    classificacao['simples_nacional'].append(result)
                elif result['bucket'] == 'erro':
                    classificacao['erros'].append(result)

    # Print classification summary
    print("\n  RESUMO DOS BUCKETS:")
    print(f"    - Estrangeiros: {len(classificacao['estrangeiros'])}")
    print(f"    - Simples Nacional: {len(classificacao['simples_nacional'])}")
    print(f"    - ME/EPP: {len(classificacao['me_epp'])}")
    if classificacao['erros']:
        print(f"    - Erros: {len(classificacao['erros'])}")

    # Step 3: Compose briefing message
    print(f"\n[3/4] Compondo mensagem do pacote...")

    mensagem = compose_briefing(
        spe=spe,
        acs_num=acs_num,
        data_corte=data_corte,
        classificacao=classificacao,
        atualizacoes=atualizacoes,
        planilha_assinaturas=planilha
    )

    # Step 4: Create Slack DM
    print(f"\n[4/4] Enviando mensagem para sua DM no Slack...")

    canvas_result = create_private_canvas(
        message=mensagem,
        title=f"ACS #{acs_num} - {spe}"
    )

    if canvas_result.get('ok'):
        print("\n✅ Mensagem enviada para sua DM!")
        print(f"   Timestamp: {canvas_result.get('ts')}")
    else:
        print("\n⚠️  Falha ao enviar DM - use a mensagem abaixo:")
        print("-" * 60)
        print(format_message_for_copy(mensagem))
        print("-" * 60)

    print("\n" + "="*60)
    print("PRONTO PARA REVISÃO")
    print("="*60)

    return {
        "mensagem": mensagem,
        "classificacao": classificacao,
        "pendencias": pendencias,
        "canvas": canvas_result
    }


def main():
    parser = argparse.ArgumentParser(
        description="Briefing Bot ACS - Automação de pacote de validação CSI"
    )

    subparsers = parser.add_subparsers(dest='command', help='Comandos disponíveis')

    # Run command
    run_parser = subparsers.add_parser('run', help='Executar o bot')
    run_parser.add_argument('--spe', help='Nome da SPE (opcional - extrai da minuta)')
    run_parser.add_argument('--acs-num', type=int, help='Número da ACS (opcional - extrai da minuta)')
    run_parser.add_argument('--data-corte', help='Data de corte DD/MM/AAAA (opcional - extrai da minuta)')
    run_parser.add_argument('--minuta', required=True, help='Caminho para arquivo da minuta')
    run_parser.add_argument('--planilha-assinaturas', help='Link da planilha de controle')
    run_parser.add_argument('--atualizacao', action='append', help='Atualizações da ACS (pode repetir)')
    run_parser.add_argument('--force-refresh', action='store_true', help='Ignora cache de CNPJ')

    args = parser.parse_args()

    if args.command == 'run':
        result = run(
            spe=args.spe,
            acs_num=args.acs_num,
            data_corte=args.data_corte,
            minuta_path=args.minuta,
            planilha=args.planilha_assinaturas,
            atualizacoes=args.atualizacao,
            force_refresh=args.force_refresh
        )
    else:
        parser.print_help()


if __name__ == '__main__':
    main()