import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from func.Utils import format_large_numbers
from func import WebScraping, RelatorioPDF

def obter_dados_fii(event=None):
    """Obtém os dados do FII digitado pelo usuário e exibe na interface gráfica."""
    fii = entrada_fii.get().strip().upper()
    if not fii:
        messagebox.showwarning("Entrada Inválida", "Digite um código de FII válido.")
        return

    try:
        tipo_fii = WebScraping.get_fii_tipo_investidor10(fii)
        dados_fundsexplorer = WebScraping.get_fii_data_fundsexplorer(fii)
        dados_investidor10 = WebScraping.get_fii_data_investidor10(fii)

        # Mescla os dados das duas fontes
        dados = dados_fundsexplorer or {}
        for key, value in (dados_investidor10 or {}).items():
            if key not in dados or dados[key] is None:
                dados[key] = value

        # Cálculo do Cap Rate
        cap_rate = WebScraping.calcular_cap_rate(dados.get("Último Rendimento"), dados.get("Cotação"))
        dados["Cap Rate"] = cap_rate

        # Avaliação do investimento
        analise, nota_fii, recomendacao = WebScraping.avaliar_fii(dados)
        avaliacao_cap_rate = WebScraping.avaliar_cap_rate(tipo_fii, cap_rate)

        # Obtém dados do relatório PDF
        dados_relatorio = RelatorioPDF.parse_fii_report(fii)

        print(type(fii))

        # Atualiza a exibição na interface
        resultado_texto.config(state=tk.NORMAL)
        resultado_texto.delete(1.0, tk.END)
        resultado_texto.insert(tk.END, f"\n🤔 Nome do FII: {fii}\n\n")
        resultado_texto.insert(tk.END, f"⭐ Nota Final do FII: {nota_fii}/10\n\n")
        resultado_texto.insert(tk.END, f"🔹 Tipo do FII: {tipo_fii}\n")
        resultado_texto.insert(tk.END, f"👍 Recomendação: {recomendacao}\n\n")
        resultado_texto.insert(tk.END, f"📈 Cap Rate: {cap_rate:.2f}%\n")
        resultado_texto.insert(tk.END, f"🔎 {avaliacao_cap_rate}\n\n")
        resultado_texto.insert(tk.END, "📊 Dados coletados:\n")
        for k, v in dados.items():
            if v is not None:
                resultado_texto.insert(tk.END, f"📌 {WebScraping.DADOS_FII.get(k, k)}: {format_large_numbers(v)} ({v})\n")
        resultado_texto.insert(tk.END, "\n📄 Informações do Relatório PDF:\n")
        for k, v in dados_relatorio.items():
            resultado_texto.insert(tk.END, f"📌 {k}: {v}\n")
        resultado_texto.config(state=tk.DISABLED)

    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao coletar dados, veja se o nome do FII foi digitado corretamente: {e}")

# Configuração da interface gráfica
janela = tk.Tk()
janela.title("Analisador de Fundos Imobiliários")
janela.geometry("600x500")

# Campo de entrada para o código do FII
tk.Label(janela, text="Digite o código do FII:", font=("Arial", 12)).pack(pady=5)
entrada_fii = tk.Entry(janela, font=("Arial", 12), width=20)
entrada_fii.pack(pady=5)
entrada_fii.bind("<Return>", obter_dados_fii)  # Permite buscar ao pressionar Enter

# Botão para buscar os dados
botao_buscar = tk.Button(janela, text="Buscar Dados", font=("Arial", 12), command=obter_dados_fii)
botao_buscar.pack(pady=10)

# Área de exibição dos resultados com scroll
frame_resultado = tk.Frame(janela)
frame_resultado.pack(pady=10, padx=10, fill="both", expand=True)

resultado_texto = scrolledtext.ScrolledText(frame_resultado, font=("Arial", 10), wrap=tk.WORD, height=20, state=tk.DISABLED)
resultado_texto.pack(fill="both", expand=True)

# Executa o loop da interface
tk.mainloop()