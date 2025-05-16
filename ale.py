from googlesearch import search
import google.generativeai as genai
import requests
from bs4 import BeautifulSoup
import streamlit as st

# Configurar a API do Gemini
genai.configure(api_key="AIzaSyArTog-quWD9Tqf-CkkFAq_-UOZfK1FTtA")  # Substitua YOUR_API_KEY pela sua chave
model = genai.GenerativeModel('gemini-2.0-flash-exp')

def pesquisar_e_filtrar(query, num_resultados=5):
    """
    Pesquisa no Google usando a consulta fornecida e filtra os resultados usando o Gemini.

    Args:
        query (str): A consulta de pesquisa.
        num_resultados (int, opcional): O número máximo de resultados a retornar do Google. Padrão é 5.

    Returns:
        list: Uma lista de resultados filtrados pelo Gemini, contendo título, URL e resumo.
    """
    resultados_google = list(search(query, num_results=num_resultados))
    resultados_filtrados = []

    for url in resultados_google:
        try:
            # Buscar o conteúdo da página web
            response = requests.get(url)
            response.raise_for_status()  # Verificar se a resposta foi bem-sucedida
            soup = BeautifulSoup(response.text, 'html.parser')
            title = soup.title.string if soup.title else "Título não encontrado"
            # Tenta obter o resumo da meta descrição, se disponível
            summary = soup.find('meta', attrs={'name': 'description'})
            summary = summary['content'] if summary else "Resumo não encontrado"

            # Filtrar o resultado usando o Gemini
            prompt = f"Você é um especialista em identificar informações relevantes na web. Dada a seguinte URL, título e resumo, determine se o conteúdo é relevante para a consulta: '{query}'.\n\nURL: {url}\nTítulo: {title}\nResumo: {summary}\n\nRetorne 'Relevante' se o conteúdo for relevante, caso contrário, retorne 'Irrelevante'."
            response = model.generate_content(prompt)
            if "Relevante" in response.text:
                resultados_filtrados.append({'url': url, 'title': title, 'summary': summary})
        except requests.exceptions.RequestException as e:
            print(f"Erro ao buscar a URL {url}: {e}")
            # Mesmo em caso de erro, inclua no resultado filtrado para manter a paridade com o número de resultados
            resultados_filtrados.append({'url': url, 'title': "Título não disponível", 'summary': "Resumo não disponível"})

    return resultados_filtrados

def main():
    """
    Função principal para executar a aplicação Streamlit.
    """
    # Configuração da página Streamlit
    st.set_page_config(
        page_title="Pesquisa Inteligente com Gemini",
        page_icon="🔍",  # Ícone da página
        layout="wide",  # Layout da página
        initial_sidebar_state="collapsed" # Estado inicial da sidebar
    )

    # Estilos CSS personalizados
    st.markdown(
        """
        <style>
        body {
            color: #333;
            background-color: #f0f4f8;
            font-family: 'Arial', sans-serif;
        }
        .title {
            color: #4c1130;
        }
        .header {
            color: #1a5235;
        }
        .bold {
            font-weight: bold;
        }
        .link {
            color: #007bff;
            text-decoration: none;
        }
        .link:hover {
            text-decoration: underline;
        }
        .warning {
            color: #856404;
            background-color: #fff3cd;
            border-color: #ffeeba;
            padding: 10px;
            border-radius: 4px;
        }
        .resultado {
            background-color: #e9ecef;
            padding: 15px;
            margin-bottom: 10px;
            border-radius: 8px;
            border: 1px solid #ced4da;
        }
        </style>
    """,
        unsafe_allow_html=True
    )

    # Título da aplicação
    st.markdown("<h1 class='title'>Pesquisa Inteligente com Gemini</h1>", unsafe_allow_html=True)
    st.markdown("Use o Gemini para filtrar resultados do Google e obter informações relevantes.", unsafe_allow_html=True)

    # Sidebar para configurações
    with st.sidebar:
        st.header("Configurações")
        query = st.text_input("Digite sua consulta de pesquisa:", "Resumo dos jogos de futebol em Angola")
        num_resultados = st.slider("Número de resultados do Google:", 1, 10, 5)

    # Botão de pesquisa
    if st.button("Pesquisar", use_container_width=True):
        st.spinner("Pesquisando e filtrando...")
        resultados_filtrados = pesquisar_e_filtrar(query, num_resultados)

        # Exibir resultados
        if resultados_filtrados:
            st.markdown("<h2 class='header'>Resultados da Pesquisa:</h2>", unsafe_allow_html=True)
            for resultado in resultados_filtrados:
                st.markdown(
                    f"<div class='resultado'>"
                    f"<p><span class='bold'>Título:</span> {resultado['title']}</p>"
                    f"<p><span class='bold'>URL:</span> <a href='{resultado['url']}' class='link' target='_blank'>{resultado['url']}</a></p>"
                    f"<p><span class='bold'>Resumo:</span> {resultado['summary']}</p>"
                    f"</div>",
                    unsafe_allow_html=True
                )
        else:
            st.markdown("<div class='warning'>Nenhum resultado relevante encontrado.</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
