import requests
from func.Utils import format_large_numbers, convert_to_number
from bs4 import BeautifulSoup

# Configuração de cabeçalho para simular um navegador real
HEADERS = {"User-Agent": "Mozilla/5.0"}

# Dicionário de nomes personalizados para os campos coletados
DADOS_FII = {
    "Cotação": "Cotação Atual",
    "P/VP": "P/VP",
    "Liquidez Diária": "Liquidez Média Diária",
    "DY (12M)": "Dividend Yield (12M)",
    "Último Rendimento": "Último Rendimento",
    "Vacância": "Vacância (%)",
    "Cap Rate": "Cap Rate (%)",
    "Patrimônio Líquido": "Patrimônio Líquido",
    "Número de Ativos": "Quantidade de Imóveis",
}

# Cap Rate médio por tipo de FII
CAP_RATE_MEDIO = {
    "Escritórios": (6, 9),  # Ok, depende da localização e ocupação
    "Galpões Logísticos": (7, 10),  # Ok, galpões bem localizados são muito demandados
    "Shopping Centers": (6, 9),  # Ajustado, pois o risco do setor subiu nos últimos anos
    "Lajes Corporativas": (6, 9),  # Ok, semelhante a Escritórios
    "Fundos de Papel (CRIs)": (10, 15),  # Ok, retornos altos pelo risco de crédito
    "Fundos de Desenvolvimento": (12, 20),  # Ajustado para refletir o maior risco e retorno
    "Imóveis Residenciais": (4, 6),  # Ajustado, pois são menos rentáveis do que comerciais
    "Imóveis Comerciais": (6, 10),  # Ok, maior risco do que residenciais
    "Fiagros": (8, 14),  # Ajustado para refletir a alta volatilidade do setor agro
    "Hospitalares": (7, 11),  # Ok, hospitais são ativos defensivos
    "Educacionais": (6, 10),  # Ajustado, pois universidades privadas têm risco operacional
    "Hotéis": (6, 10),  # Ajustado para refletir recuperação pós-pandemia
    "Varejo": (6, 10),  # Ok, reflete a volatilidade do setor
    "Fundos de Fundos (FoFs)": (7, 12),  # Ok, pois mesclam diferentes estratégias
    "Híbrido": (6, 10),  # Ok, pois mistura tijolo e papel
    "Data Centers": (8, 12),  # Ok, segmento crescente com demanda por infraestrutura digital
    "Self Storage": (7, 11),  # Ok, setor em expansão no Brasil
    "Agências Bancárias": (5, 8),  # Ok, contratos longos, mas risco de fechamento
    "Casas de Repouso/Saúde": (7, 11),  # Ajustado para refletir demanda crescente
    "Imóveis Industriais": (7, 11),  # Ok, setor com alta demanda
    "Fazendas e Agronegócio (Agro FIIs)": (8, 14),  # Ok, setor forte e resiliente
    "Ativos de Infraestrutura": (9, 14),  # Ok, essencial para utilities e telecom
    "Títulos e Valores Mobiliários": (10, 15), # Ok, setor com alta volatilidade
    "Outros": (6, 12)  # Ok, categoria genérica para ativos não listados
}


def get_fii_tipo_investidor10(fii):
    """Coleta do tipo de FII no Investidor10."""
    url = f"https://investidor10.com.br/fiis/{fii.lower()}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        return {}

    soup = BeautifulSoup(response.text, "html.parser")
    data = {}

    try:
        # Extração de DY Atual do Investidor10
        type_value = extract_value_from_desc(soup, "SEGMENTO")
        if type_value:
            return type_value

    except AttributeError:
        pass

def avaliar_cap_rate(tipo_fii, cap_rate):
    if tipo_fii in CAP_RATE_MEDIO:
        min_cap, max_cap = CAP_RATE_MEDIO[tipo_fii]
        if cap_rate:
            if min_cap <= cap_rate <= max_cap:
                return "✅ O Cap Rate está dentro da média e é atrativo!"
            else:
                return "❌ O Cap Rate está fora da média e pode não ser atrativo."
    return "⚠️ Tipo de FII não encontrado na base de referência."


def extract_value_from_card(soup, title):
    """Busca valores dentro das divs ._card-body (Cotação, Liquidez Diária)."""
    card_headers = soup.find_all("div", class_="_card-header")
    for header in card_headers:
        span = header.find("span")
        if span and title.lower() in span.get_text(strip=True).lower():
            body = header.find_next("div", class_="_card-body")
            value_span = body.find("span")
            if value_span:
                return convert_to_number(value_span.get_text(strip=True))
    return None


def extract_value_from_desc(soup, label):
    """Busca valores dentro das divs .desc (Vacância e Número de Cotistas)."""
    elements = soup.find_all("div", class_="desc")
    for element in elements:
        name_span = element.find("span", class_="name")
        if name_span and label in name_span.get_text(strip=True):
            value_element = element.find_next("div", class_="value").find("span")
            if value_element:
                return value_element.get_text(strip=True)
    return "N/A"


def get_fii_data_fundsexplorer(fii):
    """Coleta indicadores de um Fundo Imobiliário no Funds Explorer."""
    url = f"https://www.fundsexplorer.com.br/funds/{fii.lower()}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        return {}

    soup = BeautifulSoup(response.text, "html.parser")
    data = {}

    # Extraindo informações do Funds Explorer
    mapeamento = {
        "liquidezMediaDiaria": "Liquidez Diária",
        "patrimonioLiquido": "Patrimônio Líquido",
        "vacancia": "Vacância",
        "numeroImoveis": "Número de Ativos",
        "yieldMensal": "DY (12M)",
        "pvp": "P/VP"
    }

    for li in soup.select("ul.comparator__cols__list--data li"):
        key = li.get("data-row", "").strip()
        value = li.get_text(strip=True)
        if key in mapeamento:
            data[mapeamento[key]] = convert_to_number(value)

    # Pegando Cotação e Último Rendimento para cálculo do Cap Rate
    cotacao_element = soup.find("div", class_="headerTicker__content__price")
    if cotacao_element:
        cotacao = cotacao_element.find("p")
        if cotacao:
            data["Cotação"] = convert_to_number(cotacao.get_text(strip=True).replace("R$", ""))

    for box in soup.find_all("div", class_="indicators__box"):
        p_label = box.find("p")
        if p_label and "Último Rendimento" in p_label.get_text():
            b_val = box.find("b")
            if b_val:
                data["Último Rendimento"] = convert_to_number(b_val.get_text(strip=True))

    return data


def get_fii_data_investidor10(fii):
    """Coleta indicadores de um Fundo Imobiliário no Investidor10."""
    url = f"https://investidor10.com.br/fiis/{fii.lower()}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        return {}

    soup = BeautifulSoup(response.text, "html.parser")
    data = {}

    try:
        # Extração de DY Atual do Investidor10
        dy_value = extract_value_from_card(soup, "DY (12M)")
        if dy_value:
            data["Dividend Yield (Investidor 10) (12M)"] = dy_value

        # Extração de Vacância
        vacancia_value = extract_value_from_desc(soup, "VACÂNCIA")
        if vacancia_value and vacancia_value != "N/A":
            # formatar para duas casas decimais
            data["Vacância"] = round(float(vacancia_value.replace("%", "").replace(".", "").replace(",", ".")) / 100, 2)

        # Extração de Número de Cotistas
        cotistas_value = extract_value_from_desc(soup, "COTISTAS")
        if cotistas_value and cotistas_value != "N/A":
            data["Número de Cotistas"] = convert_to_number(cotistas_value)

        # Extração de número de Ativos
        tabela_ativos = soup.find("table", {"id": "properties-index-table"})

        total_imoveis = 0

        if tabela_ativos:
            imoveis = []

            # Iterando pelas linhas da tabela
            for tr in tabela_ativos.find_all("tr"):
                nome = tr.find("td").get_text(strip=True)  # Nome do local
                quantidade = int(tr.find("span", class_="count").get_text(strip=True))  # Pegando a quantidade

                total_imoveis += quantidade
                imoveis.append((nome, quantidade))

        if total_imoveis and total_imoveis != "N/A":
            data["Quantidade de Imóveis"] = total_imoveis

    except AttributeError:
        pass

    return data


def calcular_cap_rate(ultimo_rendimento, cotacao):
    """Calcula o Cap Rate"""
    if ultimo_rendimento and cotacao:
        receita_anual = ultimo_rendimento * 12
        return round((receita_anual / cotacao) * 100, 2)
    return None

def avaliar_fii(data):
    """Avalia se o FII atende aos critérios de investimento e gera uma nota"""
    criterios = {
        "Liquidez Diária": lambda x: x is not None and x >= 500_000,
        "Patrimônio Líquido": lambda x: x is not None and x >= 500_000_000,
        "Vacância": lambda x: x is not None and x <= 10,
        "Quantidade de Imóveis": lambda x: x is not None and x >= 5,
        "DY (12M)": lambda x: x is not None and x >= 6,
        "P/VP": lambda x: x is not None and 0.85 <= x <= 1.15
    }

    analise = {}
    pontuacao = 0

    for crit, func in criterios.items():
        valor = data.get(crit, None)

        aprovado = func(valor)
        analise[crit] = f"✅ Atende ({format_large_numbers(valor)})" if aprovado else f"❌ Não atende ({format_large_numbers(valor)})"
        if aprovado:
            pontuacao += 1

    nota_fii = round((pontuacao / len(criterios)) * 10, 2)
    recomendacao = "👍 Vale a pena investir!" if nota_fii >= 7 else "👎 Melhor procurar outra opção."

    return analise, nota_fii, recomendacao
