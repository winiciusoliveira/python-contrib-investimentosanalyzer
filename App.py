import sys
import subprocess
import os

def main():
    print("Selecione o modo de execução:")
    print("1 - Executar no Terminal")
    print("2 - Executar com Interface Gráfica")

    escolha = input("Digite sua escolha (1 ou 2): ").strip()

    # Obtém o caminho correto do interpretador Python dentro do ambiente virtual
    python_executable = sys.executable  # Isso aponta para o Python do venv

    if escolha == "1":
        subprocess.run([python_executable, "Main.py"])  # Executa com o Python correto
    elif escolha == "2":
        subprocess.run([python_executable, "interface/Gui.py"])  # Executa a GUI com o Python correto
    else:
        print("Opção inválida. Execute novamente e escolha 1 ou 2.")

if __name__ == "__main__":
    main()
