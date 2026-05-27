# Briefing Bot ACS Skill

Automação para montagem do pacote de validação enviado ao CSI a cada nova ACS.

## Uso

```
/briefing-bot run --spe "SPE Japaratinga" --acs-num 4 --data-corte 27/05/2026 --minuta caminho/minuta.pdf
```

## Parâmetros

| Parâmetro | Descrição | Obrigatório |
|-----------|-----------|-------------|
| `--spe` | Nome da SPE | Sim |
| `--acs-num` | Número da ACS | Sim |
| `--data-corte` | Data de corte (DD/MM/AAAA) | Sim |
| `--minuta` | Caminho para arquivo da minuta (.pdf/.docx) | Sim |
| `--planilha-assinaturas` | Link da planilha de controle de assinaturas | Não |
| `--atualizacao` | Atualizações da ACS (pode repetir para múltiplos bullets) | Não |
| `--force-refresh` | Ignora cache de CNPJ, força reconsulta | Não |

## Fluxo

1. **Extração**: Lê a minuta e extrai lista de investidores via Claude API
2. **Classificação**: Consulta BrasilAPI para classificar PJs (Simples Nacional / ME-EPP / DEMAIS)
3. **Composição**: Monta mensagem final com concordância correta
4. **Output**: Cria Canvas privado no Slack para revisão

## Regras de Negócio

- **Optante Simples Nacional** → Bloqueio (não pode ingressar)
- **ME ou EPP** → Precisa virar porte DEMAIS (art. 3º, §4º, VII LC 123/06)
- **PF estrangeiro** → Precisa RNM + endereço no Brasil OU procurador
- **PJ nacional regular** → Sem pendência

## Troubleshooting

- **Claude retorna JSON inválido**: retry automático (1 vez)
- **CNPJ não encontrado**: marca no bucket "erros" e sinaliza no Canvas
- **API fora do ar**: retry com backoff exponencial (3 tentativas)
- **Minuta sem cláusula de sócios**: mensagem de erro clara

## Estrutura de arquivos

```
src/
├── minuta_reader.py      # Extração de investidores
├── cnpj_classifier.py    # Classificação de PJ via API
├── pf_classifier.py      # Classificação de PF (embutido em cnpj_classifier)
├── briefing_composer.py  # Composição da mensagem
├── slack_output.py       # Output Slack/Canvas
├── cache.py              # SQLite para cache
└── main.py               # CLI
```