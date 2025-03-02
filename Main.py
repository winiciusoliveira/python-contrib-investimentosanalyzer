from func.Utils import format_large_numbers
from func import WebScraping
from func import RelatorioPDF

if __name__ == "__main__":
    fii = input("Digite o código do FII: ")
    tipo_fii = WebScraping.get_fii_tipo_investidor10(fii)

    # Coleta dados de ambos os sites
    dados_fundsexplorer = WebScraping.get_fii_data_fundsexplorer(fii)
    dados_investidor10 = WebScraping.get_fii_data_investidor10(fii)

    # Mescla os dados das duas fontes
    dados = dados_fundsexplorer or {}

    for key, value in (dados_investidor10 or {}).items():
        if key not in dados or dados[key] is None:
            dados[key] = value

    # Cálculo do Cap Rate usando Último Rendimento e Cotação
    cap_rate = WebScraping.calcular_cap_rate(dados.get("Último Rendimento"), dados.get("Cotação"))
    dados["Cap Rate"] = cap_rate

    # Exibir dados
    print("\n📊 Dados coletados:")
    for key, value in dados.items():
        print(f"📌 {WebScraping.DADOS_FII.get(key, key)}: {format_large_numbers(value)} ({value})")

    print("\n📈 Análise de Investimento:")
    analise, nota_fii, recomendacao = WebScraping.avaliar_fii(dados)

    for key, value in analise.items():
        print(f"{key}: {value}")

    print(f"\n⭐ Nota Final do FII: {nota_fii}/10 ⭐")

    print("\n🔎 Avaliação do Cap Rate:")
    print(WebScraping.avaliar_cap_rate(tipo_fii, cap_rate))

    dados_relatorio = RelatorioPDF.parse_fii_report(fii)

    print(f"\n🔹 Tipo do FII: {tipo_fii}")
    print(f"👍 Recomendação: {recomendacao}")

    print("\n📄 Informações do Relatório PDF:")

    for key, value in dados_relatorio.items():
        print(f"📌 {key}: {value}")
