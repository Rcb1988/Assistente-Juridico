import requests
import streamlit as st
import openai

# 🔐 Chave da OpenAI via secrets
client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.set_page_config(page_title="Assistente Jurídico GPT", layout="centered")
st.title("⚖️ Assistente Jurídico com GPT + DataJud")

# 📚 Mapeamento dos códigos dos Tribunais Estaduais
TRIBUNAIS = {
    "01": "tjac", "02": "tjal", "03": "tjap", "04": "tjam", "05": "tjba",
    "06": "tjce", "07": "tjdf", "08": "tjes", "09": "tjgo", "10": "tjma",
    "11": "tjmt", "12": "tjms", "13": "tjmg", "14": "tjpa", "15": "tjpb",
    "16": "tjpr", "17": "tjpe", "18": "tjpi", "19": "tjrj", "20": "tjrn",
    "21": "tjrs", "22": "tjro", "23": "tjrr", "24": "tjsc", "25": "tjse",
    "26": "tjsp", "27": "tjto"
}

def identificar_tribunal(numero_processo):
    if len(numero_processo) >= 20:
        codigo = numero_processo[14:16]  # Correção definitiva
        return TRIBUNAIS.get(codigo)
    return None

# 📅 Entrada do número do processo
numero_processo = st.text_input(
    "📄 Digite o número do processo (sem pontos/traços):",
    placeholder="Ex: 10252178720218110041"
)

if st.button("Consultar"):
    if numero_processo:
        tribunal_api = identificar_tribunal(numero_processo)
        st.write(f"Código do tribunal extraído: {numero_processo[15:17]}")  # Debug ajustado
        if not tribunal_api:
            st.error("⚠️ Tribunal não identificado ou não suportado.")
            st.stop()

        url = f"https://api-publica.datajud.cnj.jus.br/api_publica_{tribunal_api}/_search"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'APIKey cDZHYzlZa0JadVREZDJCendQbXY6SkJlTzNjLV9TRENyQk1RdnFKZGRQdw=='
        }
        payload = {
            "query": {
                "match": {
                    "numeroProcesso": numero_processo
                }
            }
        }

        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            st.error(f"❌ Erro na requisição ao DataJud: {e}")
            st.stop()

        dados = response.json()

        if dados.get("hits", {}).get("hits"):
            processo = dados["hits"]["hits"][0]["_source"]

            # 🔍 Extrai informações principais do processo
            classe = processo["classe"]["nome"]
            tribunal = processo["tribunal"]
            orgao = processo["orgaoJulgador"]["nome"]
            assunto = processo["assuntos"][0]["nome"] if processo.get("assuntos") else "Não especificado"
            ajuizamento = processo["dataAjuizamento"][:10]
            status = processo.get("grau", "Não especificado")
            movimentos = processo.get("movimentos", [])

            markdown_output = f"""
### 📄 Informações do Processo

| Campo | Detalhes |
|-------|----------|
| **Número do Processo** | {numero_processo} |
| **Classe Processual** | {classe} |
| **Tipo de Ação** | {classe} |
| **Status do Processo** | {status} |
| **Tribunal** | {tribunal} |
| **Órgão Julgador** | {orgao} |
| **Assunto Principal** | {assunto} |
| **Data de Ajuizamento** | {ajuizamento} |

### 🔍 Últimos Andamentos

| Data | Movimento |
|------|-----------|
{''.join([f"| {m['dataHora'][:10]} | {m['nome']} |\n" for m in movimentos[:3]])}
"""

            st.subheader("📌 Resumo jurídico do GPT:")
            st.markdown(markdown_output)
        else:
            st.warning("❌ Nenhum processo encontrado com esse número.")
    else:
        st.warning("⚠️ Por favor, digite um número de processo válido.")

