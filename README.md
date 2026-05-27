# Briefing Bot ACS

Automação para montagem do pacote de validação enviado ao CSI a cada nova ACS.

## Problema

Hoje, cada pacote de validação leva ~45 minutos para montar manualmente:
- Ler investidor por investidor na cláusula de sócios
- Abrir cartão CNPJ na Receita para cada PJ
- Classificar estrangeiros vs. nacionais
- Escrever o texto do zero

**Impacto**: ~60 pacotes/ano × 45 min = ~45h/ano

## Solução

Sistema web (Streamlit) que:
1. Permite upload da minuta da ACS (PDF/DOCX)
2. Extrai pendências automaticamente lendo o texto entre `{}`
3. Classifica cada empresa via API CNPJ (BrasilAPI)
4. Compoe mensagem final com template padrão
5. Salva histórico no Supabase para consulta posterior
6. Envia DM no Slack para revisão antes de postar no canal

## Interface Web

Acesse: **http://localhost:8501**

### Funcionalidades:
- **Upload de minuta**: arraste ou selecione arquivo (.pdf ou .docx)
- **Processamento automático**: extrai pendências e gera mensagem
- **Histórico**: consulta todos os processamentos anteriores
- **Persistência de login**: não precisa fazer login a cada atualização

### Abas:
1. **📁 Processar Minuta** - subir novos arquivos
2. **📜 Histórico** - ver processamentos anteriores com data/hora

## Setup

### 1. Instalar dependências

```bash
cd hackathon-cfo-briefing-bot
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configurar variáveis de ambiente

```bash
cp .env.example .env
# Edite .env com suas credenciais
```

### 3. Variáveis necessárias no .env

```env
# Supabase (autenticação + histórico)
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_KEY=sua-chave-anon

# Anthropic API (extração de pendências)
ANTHROPIC_API_KEY=sk-ant-sua-chave

# Slack (opcional - para enviar DM)
SLACK_BOT_TOKEN=xoxb-sua-token
SLACK_USER_ID=seu-user-id
```

### 4. Criar tabela no Supabase

```sql
CREATE TABLE processamento (
    id SERIAL PRIMARY KEY,
    filename TEXT NOT NULL,
    spe TEXT,
    acs_num INTEGER,
    data_corte TEXT,
    processed_at TIMESTAMP DEFAULT NOW(),
    resultado_json TEXT,
    mensagem TEXT
);

-- Permissão para todos autenticados
ALTER TABLE processamento ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Todos podem ver registros" ON processamento
    FOR SELECT USING (true);
```

### 5. Rodar o app

```bash
streamlit run app.py --server.headless true --server.port 8501
```

## Uso

1. Abra **http://localhost:8501**
2. Faça login (ou "Continuar em modo demo")
3. Selecione a minuta (.pdf ou .docx)
4. Opcionalmente informe o link da planilha de assinaturas
5. Clique em **Processar Minuta**
6. Copie a mensagem gerada e cole no canal **#suporte-cs-investimentos**

## Regras de Negócio

| Tipo | Regra |
|------|-------|
| PF estrangeiro com endereço fora do Brasil | Listado como "residente no exterior" → precisa RNM + endereço no Brasil OU procurador |
| Empresa optante Simples Nacional | **Bloqueio**: não pode ingressar até mudar regime |
| Empresa ME ou EPP | Precisa virar porte "DEMAIS". Justificativa: art. 3º, §4º, VII da LC 123/06 |
| Qualquer investidor com `{}` na minuta | Listado no template conforme a necessidade |

## Estrutura do Projeto

```
hackathon-cfo-briefing-bot/
├── app.py                    # Interface web (Streamlit)
├── src/
│   ├── minuta_reader.py      # Extração de pendências da minuta
│   ├── cnpj_classifier.py    # Classificação via BrasilAPI
│   ├── briefing_composer.py  # Composição da mensagem
│   ├── history.py            # Histórico no Supabase/SQLite
│   └── slack_output.py       # Envio de DM no Slack
├── tests/                    # Testes unitários
├── .env.example              # Template de variáveis
└── requirements.txt         # Dependências Python
```

## Troubleshooting

**API CNPJ falha**: o sistema assume "ME" por segurança e inclui a empresa no template para verificação manual.

**Login não persiste**: certifique-se de que o Supabase está configurado corretamente no .env.

**Minuta não processa**: verifique se o arquivo é .pdf ou .docx válido.

## Deploy na Nuvem

Para其他人 acessarem, subir no Streamlit Cloud:
1. Fork este repo no GitHub
2. Conecte ao [Streamlit Cloud](https://streamlit.io/cloud)
3. Configure os secrets (SUPABASE_URL, SUPABASE_KEY, ANTHROPIC_API_KEY)
4. Deploy!

## Tecnologias

- **Python 3.11+**
- **Streamlit** - interface web
- **Supabase** - autenticação + banco de dados
- **Anthropic Claude API** - extração de pendências
- **BrasilAPI** - consulta CNPJ (Receita Federal)
- **SQLite** - cache local de CNPJs