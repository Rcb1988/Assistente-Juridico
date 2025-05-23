import requests
import streamlit as st
import openai

# 🔐 Chave da OpenAI via secrets
client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.set_page_config(page_title="Assistente Jurídico GPT", layout="centered")
st.title("⚖️ Assistente Jurídico com GPT + DataJud")

# 🔁 Mapeia códigos de tribunais CNJ para nomes no índice da API do DataJud
TRIBUNAIS = {
    "01": "tjac", "02": "tjse", "03": "tjal", "04": "tjdf", "05": "tjap", "06": "tjba",
    "07": "tjce", "08": "tjto", "09": "tjma", "10": "tjmt", "11": "tjms", "12": "tjmg",
    "13": "tjpr", "14": "tjpb", "15": "tjpa", "16": "tjpe", "17": "tjpi", "18": "tjrn",
    "19": "tjrs", "20": "tjrj", "21": "tjro", "22": "tjrr", "23": "tjsp", "24": "tjsc",
    "25": "tjgo", "26": "tjrr", "27": "tjam"
}

def identificar_tribunal(numero_processo):
    if len(numero_processo) >= 20:
        codigo = numero_processo[16:18]
        return TRIBUNAIS.get(codigo)
    return None

# 📥 Entrada do número do processo
numero_processo = st.text_input(
    "📄 Digite o número do processo (sem pontos/traços):",
    placeholder="Ex: 00166893519968260625"
)

if st.button("Consultar"):
    if numero_processo:
        tribunal_api = identificar_tribunal(numero_processo)
        if not tribunal_api:
            st.error("Tribunal não identificado ou não suportado.")
            st.stop()

        url = f"https://api-publica.datajud.cnj.jus.br/api_publica_{tribunal_api}/_search"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': st.secrets["DATAJUD_API_KEY"]
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
            st.error(f"Erro na requisição ao DataJud: {e}")
            st.stop()

        dados = response.json()

        if dados.get("hits", {}).get("hits"):
            processo = dados["hits"]["hits"][0]["_source"]

            # 🧠 Extrai os dados principais
            classe = processo["classe"]["nome"]
            tribunal = processo["tribunal"]
            orgao = processo["orgaoJulgador"]["nome"]
            assunto = processo["assuntos"][0]["nome"] if processo.get("assuntos") else "Não especificado"
            ajuizamento = processo["dataAjuizamento"][:10]
            movimentos = processo.get("movimentos", [])
            ultimos_movs = "\n".join([f"- {m['dataHora'][:10]}: {m['nome']}" for m in movimentos[:5]])

            prompt = f"""
Você é um assistente jurídico. Com base nos dados abaixo, forneça um resumo claro e técnico do processo judicial.

Número do processo: {numero_processo}
Classe: {classe}
Tribunal: {tribunal}
Órgão julgador: {orgao}
Assunto principal: {assunto}
Data de ajuizamento: {ajuizamento}
Últimos movimentos:
{ultimos_movs}
"""

            try:
                resposta = client.chat.completions.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": prompt}]
                )
                st.subheader("📌 Resumo jurídico do GPT:")
                st.markdown(resposta.choices[0].message.content)
            except Exception as e:
                st.error(f"Erro ao consultar o GPT: {e}")
        else:
            st.warning("❌ Nenhum processo encontrado com esse número.")
    else:
        st.warning("⚠️ Por favor, digite um número de processo válido.")


