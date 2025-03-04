def convert_to_number(value):
    """Converte valores formatados (K, M, B, %, R$) para float"""
    if not value:
        return None
    value = value.replace(".", "").replace(",", ".").replace("%", "").strip()
    if "K" in value:
        return float(value.replace("K", "")) * 1e3
    elif "M" in value:
        return float(value.replace("M", "")) * 1e6
    elif "B" in value:
        return float(value.replace("B", "")) * 1e9
    elif "R$" in value:
        return float(value.replace("R$", "").strip())
    try:
        return float(value)
    except ValueError:
        return None

def format_large_numbers(value):
    """Formata números grandes para K, M, B"""
    if value is None:
        return "Não encontrado"
    if value >= 1e9:
        return f"{value / 1e9:.2f}B"
    elif value >= 1e6:
        return f"{value / 1e6:.2f}M"
    elif value >= 1e3:
        return f"{value / 1e3:.2f}K"
    return str(value)

def format_large_numbers_relatorio(value):
    """Formata números grandes para K, M, B"""
    if value is None or value == "N/A":
        return "N/A"
    try:
        value = float(value.replace(".", "").replace(",", "."))
        if value >= 1e9:
            return f"{value / 1e9:.2f}B"
        elif value >= 1e6:
            return f"{value / 1e6:.2f}M"
        elif value >= 1e3:
            return f"{value / 1e3:.2f}K"
        return str(value)
    except ValueError:
        return "N/A"