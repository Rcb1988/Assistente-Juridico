import streamlit as st
import requests
import openai
import json

# Substitua pela sua chave da OpenAI
openai.api_key = 'SUA_CHAVE_OPENAI_AQUI'  # Insira sua chave aqui

st.title("Assistente Jurídico com GPT e DataJud")

numero_processo = st.text_input("Digite o número do processo (ex: 00166893519968260625):")

if st.button("Consultar"):
    if numero_processo:
        # Consulta à API do DataJud
        url = 'https://api-publica.datajud.cnj.jus.br/api_publica_tjsp/_search'
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'ApiKey SUA_CHAVE_DATAJUD_AQUI'  # Substitua pela chave válida
        }
        payload = {
            "query": {
                "match": {
                    "numeroProcesso": numero_processo
                }
            }
        }
        response = requests.post(url, headers=headers, json=payload)

        st.write("Status da requisição:", response.status_code)
        st.write("Resposta da API:", response.text)

        if response.status_code == 200:
            dados = response.json()

            # Verifica se veio algum processo
            if dados["hits"]["hits"]:
                processo = dados["hits"]["hits"][0]["_source"]

                # Extrai dados principais
                classe = processo["classe"]["nome"]
                tribunal = processo["tribunal"]
                orgao = processo["orgaoJulgador"]["nome"]
                assunto = processo["assuntos"][0]["nome"] if processo.get("assuntos") else "N/A"
                movimentos = [mov["nome"] for mov in processo["movimentos"][:5]]

                # Monta prompt limpo
                prompt = f"""
                Resumo do processo {numero_processo}:

                Classe: {classe}
                Tribunal: {tribunal}
                Órgão julgador: {orgao}
                Assunto: {assunto}
                Últimos movimentos: {', '.join(movimentos)}

                Com base nessas informações, forneça um resumo jurídico deste processo.
                """

                resposta = openai.ChatCompletion.create(
                    model="gpt-4-0613",
                    messages=[{"role": "user", "content": prompt}]
                )
                st.subheader("📄 Resumo do GPT:")
                st.write(resposta['choices'][0]['message']['content'])
            else:
                st.warning("Nenhum processo encontrado com esse número.")
        else:
            st.error("Erro ao consultar o processo.")
    else:
        st.warning("Por favor, insira o número do processo.")

