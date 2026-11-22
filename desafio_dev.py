#!/usr/bin/env python3
"""
Desafio Devesenvolvedor - 3 programas em um só arquivo, com menu.

  1. Comissão de vendedores
  2. Movimentação de estoque (entrada / saída)
  3. Cálculo de juros por atraso

Uso:  python desafio_dev.py
Requer Python 3.8+ (somente biblioteca padrão).
Keilo Marcio da Silva
"""
import json
from collections import defaultdict
from datetime import date, datetime
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

CENTAVOS = Decimal("0.01")

def arredondar(valor: Decimal) -> Decimal:
    return valor.quantize(CENTAVOS, rounding=ROUND_HALF_UP)

def brl(valor: Decimal) -> str:
    """Formata como moeda brasileira: R$ 1.234,56"""
    texto = f"{arredondar(valor):,.2f}"
    return "R$ " + texto.replace(",", "X").replace(".", ",").replace("X", ".")

def ler_decimal(mensagem: str) -> Decimal:
    while True:
        texto = input(mensagem).strip().replace("R$", "").replace(" ", "")
        # aceita 1.234,56 e 1234.56
        if "," in texto:
            texto = texto.replace(".", "").replace(",", ".")
        try:
            valor = Decimal(texto)
            if valor < 0:
                print("  Informe um valor positivo.")
                continue
            return valor
        except Exception:
            print("  Valor inválido. Exemplo: 1500,50")

# ---------------------------------------------------------------------------
# 1) COMISSÃO DE VENDEDORES
# ---------------------------------------------------------------------------
# Regra por venda:
#   valor < 100          -> sem comissão
#   100 <= valor < 500   -> 1%
#   valor >= 500         -> 5%

VENDAS_JSON = """
{
  "vendas": [
    { "vendedor": "João Silva", "valor": 1200.50 },
    { "vendedor": "João Silva", "valor": 950.75 },
    { "vendedor": "João Silva", "valor": 1800.00 },
    { "vendedor": "João Silva", "valor": 1400.30 },
    { "vendedor": "João Silva", "valor": 1100.90 },
    { "vendedor": "João Silva", "valor": 1550.00 },
    { "vendedor": "João Silva", "valor": 1700.80 },
    { "vendedor": "João Silva", "valor": 250.30 },
    { "vendedor": "João Silva", "valor": 480.75 },
    { "vendedor": "João Silva", "valor": 320.40 },

    { "vendedor": "Maria Souza", "valor": 2100.40 },
    { "vendedor": "Maria Souza", "valor": 1350.60 },
    { "vendedor": "Maria Souza", "valor": 950.20 },
    { "vendedor": "Maria Souza", "valor": 1600.75 },
    { "vendedor": "Maria Souza", "valor": 1750.00 },
    { "vendedor": "Maria Souza", "valor": 1450.90 },
    { "vendedor": "Maria Souza", "valor": 400.50 },
    { "vendedor": "Maria Souza", "valor": 180.20 },
    { "vendedor": "Maria Souza", "valor": 90.75 },

    { "vendedor": "Carlos Oliveira", "valor": 800.50 },
    { "vendedor": "Carlos Oliveira", "valor": 1200.00 },
    { "vendedor": "Carlos Oliveira", "valor": 1950.30 },
    { "vendedor": "Carlos Oliveira", "valor": 1750.80 },
    { "vendedor": "Carlos Oliveira", "valor": 1300.60 },
    { "vendedor": "Carlos Oliveira", "valor": 300.40 },
    { "vendedor": "Carlos Oliveira", "valor": 500.00 },
    { "vendedor": "Carlos Oliveira", "valor": 125.75 },

    { "vendedor": "Ana Lima", "valor": 1000.00 },
    { "vendedor": "Ana Lima", "valor": 1100.50 },
    { "vendedor": "Ana Lima", "valor": 1250.75 },
    { "vendedor": "Ana Lima", "valor": 1400.20 },
    { "vendedor": "Ana Lima", "valor": 1550.90 },
    { "vendedor": "Ana Lima", "valor": 1650.00 },
    { "vendedor": "Ana Lima", "valor": 75.30 },
    { "vendedor": "Ana Lima", "valor": 420.90 },
    { "vendedor": "Ana Lima", "valor": 315.40 }
  ]
}
"""

# Calculo de comissão de vendas
def comissao_da_venda(valor: Decimal) -> Decimal:
    if valor < 100:
        return Decimal("0.00")
    taxa = Decimal("0.01") if valor < 500 else Decimal("0.05")
    return arredondar(valor * taxa)

# Calculo de comissão
def calcular_comissoes(dados: dict) -> dict:
    resumo = defaultdict(lambda: {"vendas": 0, "total_vendido": Decimal("0"),
                                  "comissao": Decimal("0")})
    for venda in dados["vendas"]:
        valor = Decimal(str(venda["valor"]))
        r = resumo[venda["vendedor"]]
        r["vendas"] += 1
        r["total_vendido"] += valor
        r["comissao"] += comissao_da_venda(valor)
    return resumo

def programa_comissoes():
    # parse_float=Decimal evita erros de ponto flutuante nos valores em dinheiro
    dados = json.loads(VENDAS_JSON, parse_float=Decimal)
    resumo = calcular_comissoes(dados)

    print("\n=== COMISSÃO POR VENDEDOR ===\n")
    print(f"{'Vendedor':<18}{'Vendas':>7}{'Total vendido':>18}{'Comissão':>16}")
    print("-" * 59)
    for nome, r in resumo.items():
        print(f"{nome:<18}{r['vendas']:>7}{brl(r['total_vendido']):>18}"
              f"{brl(r['comissao']):>16}")
    print("-" * 59)
    total = sum((r["comissao"] for r in resumo.values()), Decimal("0"))
    print(f"{'Total de comissões':<43}{brl(total):>16}")

# ---------------------------------------------------------------------------
# 2) MOVIMENTAÇÃO DE ESTOQUE
# ---------------------------------------------------------------------------
# Os dados ficam salvos em "estoque_dados.json" (mesma pasta do script),
# então o saldo e o histórico continuam na próxima vez que abrir o programa.

ESTOQUE_INICIAL = {
    "estoque": [
        {"codigoProduto": 101, "descricaoProduto": "Caneta Azul", "estoque": 150},
        {"codigoProduto": 102, "descricaoProduto": "Caderno Universitário", "estoque": 75},
        {"codigoProduto": 103, "descricaoProduto": "Borracha Branca", "estoque": 200},
        {"codigoProduto": 104, "descricaoProduto": "Lápis Preto HB", "estoque": 320},
        {"codigoProduto": 105, "descricaoProduto": "Marcador de Texto Amarelo", "estoque": 90},
    ]
}

# Grava o arqquivo de estoque
ARQUIVO_ESTOQUE = Path(__file__).with_name("estoque_dados.json")

class Deposito:
    def __init__(self, arquivo: Path = ARQUIVO_ESTOQUE):
        self.arquivo = arquivo
        if arquivo.exists():
            dados = json.loads(arquivo.read_text(encoding="utf-8"))
        else:
            dados = {
                "estoque": json.loads(json.dumps(ESTOQUE_INICIAL["estoque"])),
                "movimentacoes": [],
            }
        self.produtos = {p["codigoProduto"]: p for p in dados["estoque"]}
        self.movimentacoes = dados["movimentacoes"]

    def salvar(self):
        dados = {"estoque": list(self.produtos.values()),
                 "movimentacoes": self.movimentacoes}
        self.arquivo.write_text(json.dumps(dados, ensure_ascii=False, indent=2),
                                encoding="utf-8")

    def _proximo_id(self) -> int:
        # Identificador único e sequencial (nunca repete, mesmo após reiniciar)
        return max((m["id"] for m in self.movimentacoes), default=0) + 1

    def movimentar(self, codigo: int, tipo: str, quantidade: int, descricao: str) -> dict:
        if codigo not in self.produtos:
            raise ValueError(f"Produto {codigo} não encontrado.")
        if tipo not in ("ENTRADA", "SAIDA"):
            raise ValueError("Tipo deve ser ENTRADA ou SAIDA.")
        if quantidade <= 0:
            raise ValueError("A quantidade deve ser maior que zero.")
        if not descricao.strip():
            raise ValueError("Informe a descrição da movimentação.")

        produto = self.produtos[codigo]
        if tipo == "SAIDA" and quantidade > produto["estoque"]:
            raise ValueError(
                f"Estoque insuficiente: há {produto['estoque']} un. e a saída é de {quantidade}.")

        produto["estoque"] += quantidade if tipo == "ENTRADA" else -quantidade
        mov = {
            "id": self._proximo_id(),
            "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "codigoProduto": codigo,
            "tipo": tipo,
            "quantidade": quantidade,
            "descricao": descricao.strip(),
            "estoqueFinal": produto["estoque"],
        }
        self.movimentacoes.append(mov)
        self.salvar()
        return mov
    
# Procediemnto para ler numeros inteiros
def ler_inteiro(mensagem: str, minimo: int = None) -> int:
    while True:
        try:
            n = int(input(mensagem).strip())
            if minimo is not None and n < minimo:
                print(f"  Informe um número maior ou igual a {minimo}.")
                continue
            return n
        except ValueError:
            print("  Informe um número inteiro.")

# Procedimento para listar produtos
def listar_produtos(dep: Deposito):
    print(f"\n{'Código':<8}{'Produto':<30}{'Estoque':>8}")
    print("-" * 46)
    for p in dep.produtos.values():
        print(f"{p['codigoProduto']:<8}{p['descricaoProduto']:<30}{p['estoque']:>8}")

# Procedimento para listar históricos
def listar_historico(dep: Deposito):
    if not dep.movimentacoes:
        print("\nNenhuma movimentação lançada ainda.")
        return
    print(f"\n{'ID':<5}{'Data':<20}{'Prod.':<7}{'Tipo':<9}{'Qtde':>6}{'Saldo':>7}  Descrição")
    print("-" * 85)
    for m in dep.movimentacoes:
        print(f"{m['id']:<5}{m['data']:<20}{m['codigoProduto']:<7}{m['tipo']:<9}"
              f"{m['quantidade']:>6}{m['estoqueFinal']:>7}  {m['descricao']}")

def programa_estoque():
    dep = Deposito()
    while True:
        print("\n=== MOVIMENTAÇÃO DE ESTOQUE ===")
        print("1 - Lançar movimentação")
        print("2 - Consultar estoque")
        print("3 - Histórico de movimentações")
        print("0 - Voltar")
        opcao = input("Escolha: ").strip()

        if opcao == "1":
            listar_produtos(dep)
            codigo = ler_inteiro("\nCódigo do produto: ")
            if codigo not in dep.produtos:
                print("  Produto não encontrado.")
                continue
            tipo = ""
            while tipo not in ("E", "S"):
                tipo = input("Tipo - (E)ntrada ou (S)aída: ").strip().upper()[:1]
            quantidade = ler_inteiro("Quantidade: ", minimo=1)
            descricao = input("Descrição da movimentação (ex.: Compra, Venda, Devolução, Ajuste): ")
            try:
                mov = dep.movimentar(codigo, "ENTRADA" if tipo == "E" else "SAIDA",
                                     quantidade, descricao)
            except ValueError as erro:
                print(f"  ERRO: {erro}")
                continue
            nome = dep.produtos[codigo]["descricaoProduto"]
            print(f"\nMovimentação nº {mov['id']} registrada ({mov['tipo']}: {mov['descricao']}).")
            print(f"Estoque final de '{nome}': {mov['estoqueFinal']} unidades.")
        elif opcao == "2":
            listar_produtos(dep)
        elif opcao == "3":
            listar_historico(dep)
        elif opcao == "0":
            return
        else:
            print("  Opção inválida.")

# ---------------------------------------------------------------------------
# 3) JUROS POR ATRASO
# ---------------------------------------------------------------------------
# Juros simples de 2,5% ao dia sobre o valor, contando os dias corridos entre
# o vencimento e hoje. Se ainda não venceu, não há juros.

TAXA_DIARIA = Decimal("0.025")

# Procedimento para calcular juros
def calcular_juros(valor: Decimal, vencimento: date, hoje: date = None):
    hoje = hoje or date.today()
    dias = max((hoje - vencimento).days, 0)
    juros = arredondar(valor * TAXA_DIARIA * dias)
    return dias, juros

# Procedimento para ler data
def ler_data(mensagem: str) -> date:
    while True:
        texto = input(mensagem).strip()
        try:
            return datetime.strptime(texto, "%d/%m/%Y").date()
        except ValueError:
            print("  Data inválida. Use o formato dd/mm/aaaa (ex.: 15/10/2026).")


def programa_juros():
    print("\n=== CÁLCULO DE JUROS ===")
    valor = ler_decimal("Valor (R$): ")
    vencimento = ler_data("Data de vencimento (dd/mm/aaaa): ")
    hoje = date.today()
    dias, juros = calcular_juros(valor, vencimento, hoje)

    print(f"\nHoje:               {hoje.strftime('%d/%m/%Y')}")
    if dias == 0:
        print("Sem atraso - não há juros a cobrar.")
    else:
        print(f"Dias em atraso:     {dias}")
        print(f"Valor do juros:     {brl(juros)}  (2,5% ao dia)")
        print(f"Total a pagar:      {brl(valor + juros)}")


# ---------------------------------------------------------------------------
# MENU PRINCIPAL
# ---------------------------------------------------------------------------

def main():
    while True:
        print("\n===== DESAFIO DEV =====")
        print("1 - Comissão de vendedores")
        print("2 - Movimentação de estoque")
        print("3 - Cálculo de juros")
        print("0 - Sair")
        opcao = input("Escolha: ").strip()
        if opcao == "1":
            programa_comissoes()
        elif opcao == "2":
            programa_estoque()
        elif opcao == "3":
            programa_juros()
        elif opcao == "0":
            print("Até logo!")
            break
        else:
            print("  Opção inválida.")


if __name__ == "__main__":
    main()
