from mip import *

class No:
    def __init__(self, n_variaveis, c, A, b, restricoes_adicionais=None):
        self.n = n_variaveis
        self.c = c
        self.A = A
        self.b = b
        self.restricoes_adicionais = restricoes_adicionais or []
    
    def __str__(self):
        return f"Nó com {len(self.restricoes_adicionais)} restrições adicionais: {self.restricoes_adicionais}"
    
    def n(self):
        return self.n

def resolver_relaxado(no):
    modelo = Model(sense=MAXIMIZE, solver_name="CBC")
    x = [modelo.add_var(var_type="CONTINUOUS", lb=0, ub=1) for _ in range(no.n)]

    print('print em todo mundo:')

    # Função objetivo
    modelo.objective = xsum(no.c[i] * x[i] for i in range(no.n))
    
    # Restrições principais
    for linha, limite in zip(no.A, no.b):
        modelo += xsum(linha[i] * x[i] for i in range(no.n)) <= limite
        
    # Restrições adicionais (ramificações)
    for idx, valor in no.restricoes_adicionais:
        modelo += x[idx] == valor

    status = modelo.optimize()

    #if status != 'Optimal':
    #    return None, None

    solucao = [x[i].x for i in range(no.n)]
    valor = modelo.objective_value
    return solucao, valor

def branch_and_bound(n, c, A, b):
    melhor_valor = float('-inf')
    melhor_solucao = None

    raiz = No(n, c, A, b)
    

    pilha = [raiz]  # Busca em profundidade
    

    iteracao = 0

    while pilha:
        iteracao += 1
        no_atual = pilha.pop()
        print(f"\n--- Iteração {iteracao} ---")
        
        solucao, valor = resolver_relaxado(no_atual)

        if valor is None:
            valor = 0

        if solucao[0] is None:
            print("-> Sem solução viável.")
            continue

        print(f"-> Solução relaxada: {solucao}")
        print(f"-> Valor objetivo: {valor}")

        if valor <= melhor_valor:
            print("-> Podado: valor inferior ao ótimo atual.")
            continue

        # Verifica se é inteira
        if all(abs(v - round(v)) < 1e-5 for v in solucao):
            print("-> Solução inteira!")
            if valor > melhor_valor:
                melhor_valor = valor
                melhor_solucao = solucao
                print("-> Novo ótimo encontrado!")
            continue

        # Encontra variável fracionária mais próxima de 0.5
        fracionarias = [(i, abs(solucao[i] - 0.5)) for i in range(n) if abs(solucao[i] - round(solucao[i])) > 1e-5]
        if not fracionarias:
            print("-> Nenhuma variável fracionária para ramificar.")
            continue

        indice, _ = min(fracionarias, key=lambda x: x[1])
        print(f"-> Variável escolhida para ramificar: x{indice+1}")

        restricoes_0 = no_atual.restricoes_adicionais + [(indice, 0)]
        restricoes_1 = no_atual.restricoes_adicionais + [(indice, 1)]

        filho_0 = No(n, c, A, b, restricoes_0)
        filho_1 = No(n, c, A, b, restricoes_1)

        pilha.append(filho_0)
        pilha.append(filho_1)

        print("-> Filhos adicionados à pilha.")
    
    return melhor_solucao, melhor_valor



def ler_arquivo_entrada(caminho_arquivo):
    with open(caminho_arquivo, 'r') as f:
        linhas = f.readlines()

    # Primeira linha: número de variáveis e restrições
    n_variaveis, n_restricoes = map(int, linhas[0].strip().split())

    # Segunda linha: coeficientes da função objetivo
    c = list(map(int, linhas[1].strip().split()))

    # Linhas seguintes: restrições (coeficientes + lado direito)
    A = []  # matriz de coeficientes das restrições
    b = []  # lado direito das restrições

    for linha in linhas[2:2 + n_restricoes]:
        partes = list(map(int, linha.strip().split()))
        A.append(partes[:-1])
        b.append(partes[-1])

    return n_variaveis, n_restricoes, c, A, b

arquivo = 'teste1.txt'
#arquivo = 'teste2.txt'
#arquivo = 'teste3.txt'
#arquivo = 'teste4.txt'  # caminho para o arquivo de entrada

n, m, c, A, b = ler_arquivo_entrada(arquivo)

print(f"Variáveis: {n}")
print(f"Restrições: {m}")
print(f"Função objetivo: {c}")
print("Matriz A:")
for linha in A:
    print(linha)
print("Vetor b:", b)

solucao, valor = branch_and_bound(n, c, A, b)

print(f"Melhor valor: {valor}")
print(f"Solução: {[int(round(x)) for x in solucao]}")
