import requests
import streamlit as st
import openai

# ✅ Acessa chave da OpenAI de forma segura
client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.set_page_config(page_title="Assistente Jurídico GPT", layout="centered")
st.title("⚖️ Assistente Jurídico com GPT + DataJud")

numero_processo = st.text_input(
    "📄 Digite o número do processo (sem pontos/traços):",
    placeholder="Ex: 00166893519968260625"
)

if st.button("Consultar"):
    if numero_processo:
        url = 'https://api-publica.datajud.cnj.jus.br/api_publica_tjsp/_search'
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'APIKey cDZHYzlZa0JadVREZDJCendQbXY6SkJlTzNjLV9TRENyQk1RdnFKZGRQdw=='  # substitua por sua chave real do DataJud
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
                    model="gpt-3.5-turbo",
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

