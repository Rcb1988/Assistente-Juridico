import streamlit as st
import requests
import json
import openai

# ✅ Cria cliente OpenAI com sua chave (v1)
client = openai.OpenAI(api_key="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")  # Substitua aqui

st.set_page_config(page_title="Assistente Jurídico GPT", layout="centered")
st.title("⚖️ Assistente Jurídico com GPT + DataJud")

numero_processo = st.text_input("📄 Digite o número do processo (sem pontos/traços):", placeholder="Ex: 00166893519968260625")

if st.button("Consultar"):
    if numero_processo:
        # Consulta à API do DataJud
        url = 'https://api-publica.datajud.cnj.jus.br/api_publica_tjsp/_search'
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'APIKey cDZHYzlZa0JadVREZDJCendQbXY6SkJlTzNjLV9TRENyQk1RdnFKZGRQdw=='  # Substitua aqui
        }
        payload = {
            "query": {
                "match": {
                    "numeroProcesso": numero_processo
                }
            }
        }

        response = requests.post(url, headers=headers, json=payload)

        if response.status_code == 200:
            dados = response.json()

            if dados["hits"]["hits"]:
                processo = dados["hits"]["hits"][0]["_source"]

                # Extrai dados principais
                classe = processo["classe"]["nome"]
                tribunal = processo["tribunal"]
                orgao = processo["orgaoJulgador"]["nome"]
                assunto = processo["assuntos"][0]["nome"] if processo.get("assuntos") else "Não especificado"
                ajuizamento = processo["dataAjuizamento"][:10]
                movimentos = processo["movimentos"]
                ultimos_movs = "\n".join([f"- {m['dataHora'][:10]}: {m['nome']}" for m in movimentos[:5]])

                # Prompt limpo e claro para o GPT
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

                resposta = client.chat.completions.create(
                    model="gpt-4-0613",
                    messages=[{"role": "user", "content": prompt}]
                )

                st.subheader("📌 Resumo jurídico do GPT:")
                st.markdown(resposta.choices[0].message.content)
            else:
                st.warning("❌ Nenhum processo encontrado com esse número.")
        else:
            st.error("❌ Erro ao consultar a API do DataJud. Verifique a chave ou tente mais tarde.")
    else:
        st.warning("⚠️ Por favor, digite um número de processo válido.")
