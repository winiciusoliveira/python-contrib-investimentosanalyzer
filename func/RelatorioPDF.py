import os
import PyPDF2
import re
from func.Utils import format_large_numbers_relatorio


def extract_text_from_pdf(pdf_path):
    """Extrai o texto de um arquivo PDF."""
    if not os.path.exists(pdf_path):
        return None

    text = ""
    with open(pdf_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text += page.extract_text() + "\n"
    return text if text.strip() else None


def clean_text(text):
    """Remove quebras de linha e espaços extras para facilitar a extração via regex."""
    text = text.replace("\n", " ")  # Substitui quebras de linha por espaços
    text = re.sub(r'\s+', ' ', text)  # Substitui múltiplos espaços por um único espaço
    return text


def parse_fii_report(fii):
    """Analisa o relatório PDF do FII e extrai informações relevantes."""
    pdf_path = os.path.join("relatorios", f"{fii}.pdf")
    pdf_text = extract_text_from_pdf(pdf_path)

    if not pdf_text:
        return {"Relatório": "N/A"}

    pdf_text_cleaned = clean_text(pdf_text)

    # Dicionário de palavras-chave e expressões regulares para capturar os valores corretamente
    regex_patterns = {
        "Gestor": r"Gestora\s+([^\n]+)",
        "Administrador": r"Administradora\s+([^\n]+)",
        "Segmento": r"Segmento\s+([^\n]+)",
        "Patrimônio Líquido": r"PATRIMÔNIO LÍQUIDO\s+R\$ ([\d.,]+)",
        "Vacância": r"Vacância[:\s]+([^\n]+)",
        "Cap Rate": r"Cap Rate[:\s]+([^\n]+)",
        "Último Rendimento": r"Rendimento Distribuído por Cota\s+([\d.,]+)",
        "Número de Cotas": r"NÚMERO DE COTAS\s+([\d.,]+)",
        "P/VP": r"P/VP[:\s]+([\d.,]+)",
        "DY (12M) %": r"DY\s+ANUALIZADO\s+COTA\s+MERCADO\s+.*?\s+([\d.,]+)\s*%"
    }

    data = {}

    for key, pattern in regex_patterns.items():
        match_default = re.search(pattern, pdf_text, re.IGNORECASE)
        match_extra = re.search(pattern, pdf_text_cleaned, re.IGNORECASE)

        if match_default:
            if key != "Vacância" and any(char.isdigit() for char in match_default.group(1).strip()):  # Verifica se há números na string
                data[key] = format_large_numbers_relatorio(match_default.group(1).strip())
            else:
                data[key] = match_default.group(1).strip()
        elif match_default is None:
            if match_extra:
                if key != "Vacância" and any(char.isdigit() for char in match_extra.group(1).strip()):  # Verifica se há números na string
                    data[key] = format_large_numbers_relatorio(match_extra.group(1).strip())
                else:
                    data[key] = match_extra.group(1).strip()
        else:
            data[key] = "N/A"

    return data
