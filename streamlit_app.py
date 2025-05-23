import streamlit as st
import requests
import openai
import json

# Substitua pela sua chave da OpenAI
openai.api_key = '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'  # Substitua antes de rodar!

st.title("Assistente Jurídico com GPT e DataJud")

numero_processo = st.text_input("Digite o número do processo (ex: 00166893519968260625):")

if st.button("Consultar"):
    if numero_processo:
        # Consulta à API do DataJud
        url = 'https://api-publica.datajud.cnj.jus.br/api_publica_tjsp/_search'
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
        response = requests.post(url, headers=headers, json=payload)

        # 🔍 Mostrar detalhes da resposta da API
        st.write("Status da requisição:", response.status_code)
        st.write("Resposta da API:", response.text)

        if response.status_code == 200:
            dados = response.json()
            # Envia os dados para o GPT
            prompt = f"Com base nos seguintes dados do processo {numero_processo}, forneça um resumo:\n{json.dumps(dados)}"
            resposta = openai.ChatCompletion.create(
                model="gpt-4-0613",
                messages=[{"role": "user", "content": prompt}]
            )
            st.write("🔎 Resposta do GPT:")
            st.write(resposta['choices'][0]['message']['content'])
        else:
            st.error("Erro ao consultar o processo.")
    else:
        st.warning("Por favor, insira o número do processo.")
