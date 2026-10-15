"""
Uso:
    python jarros.py [a_inicial b_inicial] [--sem-arvore] [--repeticoes N]

Exemplos:
    python jarros.py
    python jarros.py 0 0
    python jarros.py 1 2 --sem-arvore
"""

from collections import deque
import sys
import time

CAP_4 = 4
CAP_3 = 3
ALVO = 2
LIMITE_MAXIMO = 10
REPETICOES_PADRAO = 2000


class No:
    __slots__ = ("estado", "pai", "acao", "profundidade", "ident")

    def __init__(self, estado, pai, acao, ident):
        self.estado = estado
        self.pai = pai
        self.acao = acao
        self.profundidade = 0 if pai is None else pai.profundidade + 1
        self.ident = ident


def configurar_terminal():
    for fluxo in (sys.stdout, sys.stderr):
        try:
            fluxo.reconfigure(encoding="utf-8")
        except (AttributeError, OSError, ValueError):
            pass


def eh_meta(estado):
    return estado[0] == ALVO or estado[1] == ALVO


def sucessores(estado):
    a, b = estado
    filhos = []
    if a != CAP_4:
        filhos.append(((CAP_4, b), "Encher o jarro de 4 L na torneira"))
    if b != CAP_3:
        filhos.append(((a, CAP_3), "Encher o jarro de 3 L na torneira"))
    if a > 0:
        filhos.append(((0, b), "Esvaziar o jarro de 4 L"))
    if b > 0:
        filhos.append(((a, 0), "Esvaziar o jarro de 3 L"))
    if b > 0 and a < CAP_4:
        t = min(b, CAP_4 - a)
        filhos.append(((a + t, b - t), "Completar o jarro de 4 L com o de 3 L"))
    if a > 0 and b < CAP_3:
        t = min(a, CAP_3 - b)
        filhos.append(((a - t, b + t), "Completar o jarro de 3 L com o de 4 L"))
    return filhos


def _criar_no(estado, pai, acao, arvore):
    no = No(estado, pai, acao, len(arvore) + 1)
    arvore.append(no)
    return no


def buscar_largura(inicial):
    arvore = []
    raiz = _criar_no(inicial, None, None, arvore)
    expandidos = 0
    gerados = 0
    solucao = raiz if eh_meta(inicial) else None
    if solucao is None:
        fronteira = deque([raiz])
        visitados = {inicial}
        while fronteira:
            no = fronteira.popleft()
            expandidos += 1
            for estado_filho, acao in sucessores(no.estado):
                gerados += 1
                if estado_filho in visitados:
                    continue
                visitados.add(estado_filho)
                filho = _criar_no(estado_filho, no, acao, arvore)
                if eh_meta(estado_filho):
                    solucao = filho
                    break
                fronteira.append(filho)
            if solucao is not None:
                break
    return {
        "algoritmo": "Busca em Largura (BFS)",
        "sigla": "BFS",
        "solucao": solucao,
        "arvore": arvore,
        "expandidos": expandidos,
        "gerados": gerados,
        "cortes": 0,
        "iteracoes": 1,
        "limite": None,
        "historico": [],
    }


def buscar_profundidade(inicial):
    arvore = []
    raiz = _criar_no(inicial, None, None, arvore)
    expandidos = 0
    gerados = 0
    solucao = raiz if eh_meta(inicial) else None
    if solucao is None:
        pilha = [raiz]
        visitados = {inicial}
        while pilha:
            no = pilha.pop()
            expandidos += 1
            filhos = []
            for estado_filho, acao in sucessores(no.estado):
                gerados += 1
                if estado_filho in visitados:
                    continue
                visitados.add(estado_filho)
                filho = _criar_no(estado_filho, no, acao, arvore)
                if eh_meta(estado_filho):
                    solucao = filho
                    break
                filhos.append(filho)
            if solucao is not None:
                break
            pilha.extend(reversed(filhos))
    return {
        "algoritmo": "Busca em Profundidade (DFS)",
        "sigla": "DFS",
        "solucao": solucao,
        "arvore": arvore,
        "expandidos": expandidos,
        "gerados": gerados,
        "cortes": 0,
        "iteracoes": 1,
        "limite": None,
        "historico": [],
    }


def _dfs_limitada(inicial, limite):
    arvore = []
    raiz = _criar_no(inicial, None, None, arvore)
    expandidos = 0
    gerados = 0
    cortes = 0
    solucao = raiz if eh_meta(inicial) else None
    if solucao is None:
        pilha = [raiz]
        while pilha:
            no = pilha.pop()
            if no.profundidade >= limite:
                cortes += 1
                continue
            expandidos += 1
            caminho = set()
            atual = no
            while atual is not None:
                caminho.add(atual.estado)
                atual = atual.pai
            filhos = []
            for estado_filho, acao in sucessores(no.estado):
                gerados += 1
                if estado_filho in caminho:
                    continue
                filho = _criar_no(estado_filho, no, acao, arvore)
                if eh_meta(estado_filho):
                    solucao = filho
                    break
                filhos.append(filho)
            if solucao is not None:
                break
            pilha.extend(reversed(filhos))
    return {
        "solucao": solucao,
        "arvore": arvore,
        "expandidos": expandidos,
        "gerados": gerados,
        "cortes": cortes,
    }


def buscar_aprof_iterativo(inicial):
    t0 = time.perf_counter()
    total_expandidos = 0
    total_gerados = 0
    total_cortes = 0
    historico = []
    solucao = None
    arvore = []
    limite_encontrado = None
    for limite in range(LIMITE_MAXIMO + 1):
        parcial = _dfs_limitada(inicial, limite)
        total_expandidos += parcial["expandidos"]
        total_gerados += parcial["gerados"]
        total_cortes += parcial["cortes"]
        encontrou = parcial["solucao"] is not None
        historico.append(
            (limite, parcial["expandidos"], parcial["gerados"], parcial["cortes"], encontrou)
        )
        if encontrou:
            solucao = parcial["solucao"]
            arvore = parcial["arvore"]
            limite_encontrado = limite
            break
    duracao = time.perf_counter() - t0
    return {
        "algoritmo": "Busca com Aprofundamento Iterativo (IDDFS)",
        "sigla": "IDDFS",
        "solucao": solucao,
        "arvore": arvore,
        "expandidos": total_expandidos,
        "gerados": total_gerados,
        "cortes": total_cortes,
        "iteracoes": len(historico),
        "limite": limite_encontrado,
        "historico": historico,
        "tempo_interno": duracao,
    }


def caminho_da_solucao(no):
    sequencia = []
    while no is not None:
        sequencia.append(no)
        no = no.pai
    return list(reversed(sequencia))


def _fmt(estado):
    return "({}, {})".format(estado[0], estado[1])


def imprimir_caminho(resultado):
    solucao = resultado["solucao"]
    print("\n" + "=" * 78)
    print(resultado["algoritmo"])
    print("=" * 78)
    if solucao is None:
        print("Nenhuma solucao encontrada dentro do limite de profundidade.")
        return
    caminho = caminho_da_solucao(solucao)
    print("Caminho da solucao ({} passos):".format(len(caminho) - 1))
    for i, no in enumerate(caminho):
        if no.pai is None:
            print("  Passo {:d}: {}  [estado inicial]".format(i, _fmt(no.estado)))
        elif i == len(caminho) - 1:
            print("  Passo {:d}: {}  <- {}   *** META ATINGIDA ***".format(i, _fmt(no.estado), no.acao))
        else:
            print("  Passo {:d}: {}  <- {}".format(i, _fmt(no.estado), no.acao))


def imprimir_arvore(resultado, mostrar):
    if not mostrar:
        return
    arvore = resultado["arvore"]
    if not arvore:
        return
    em_caminho = set()
    no = resultado["solucao"]
    while no is not None:
        em_caminho.add(no)
        no = no.pai
    filhos = {}
    for n in arvore:
        if n.pai is not None:
            filhos.setdefault(n.pai, []).append(n)
    print()
    print("-" * 78)
    titulo = "Arvore de busca - {}".format(resultado["algoritmo"])
    if resultado["limite"] is not None:
        titulo += " (arvore da iteracao final, limite = {})".format(resultado["limite"])
    print(titulo)
    print("{} nos unicos; * = nos pertencentes ao caminho da solucao".format(len(arvore)))
    print("-" * 78)
    raiz = arvore[0]
    marca = "  *" if raiz in em_caminho else ""
    print("#{} {}  [inicial]{}".format(raiz.ident, _fmt(raiz.estado), marca))

    def _mostrar(no, prefixo):
        lista = filhos.get(no, [])
        for i, filho in enumerate(lista):
            ultimo = i == len(lista) - 1
            conector = "\\-- " if ultimo else "|-- "
            novo_prefixo = prefixo + ("    " if ultimo else "|   ")
            marca = "  *" if filho in em_caminho else ""
            print("{}{}#{} {}  <- {}{}".format(prefixo, conector, filho.ident, _fmt(filho.estado), filho.acao, marca))
            _mostrar(filho, novo_prefixo)

    _mostrar(raiz, "")


def imprimir_metricas(resultado, tempo_medio, repeticoes):
    solucao = resultado["solucao"]
    comprimento = len(caminho_da_solucao(solucao)) - 1 if solucao is not None else "-"
    profundidade = solucao.profundidade if solucao is not None else "-"
    print("\nMetricas:")
    print("  Nos expandidos .............. {}".format(resultado["expandidos"]))
    print("  Nos gerados ................. {}".format(resultado["gerados"]))
    print("  Cortes de profundidade ...... {}".format(resultado["cortes"]))
    print("  Tamanho do caminho .......... {}".format(comprimento))
    print("  Profundidade da solucao ..... {}".format(profundidade))
    if resultado["limite"] is not None:
        print("  Iteracoes do IDDFS ......... {} (limite final = {})".format(resultado["iteracoes"], resultado["limite"]))
    print("  Tempo medio por execucao .... {:.2f} us (media de {} execucoes)".format(tempo_medio * 1e6, repeticoes))


def imprimir_historico_iddfs(resultado):
    if not resultado["historico"]:
        return
    print("\nDetalhamento das iteracoes do IDDFS:")
    print("  {:>6} {:>11} {:>9} {:>8} {:>10}".format("limite", "expandidos", "gerados", "cortes", "solucao"))
    for limite, exp, ger, cor, achou in resultado["historico"]:
        print("  {:>6} {:>11} {:>9} {:>8} {:>10}".format(limite, exp, ger, cor, "sim" if achou else "nao"))


def imprimir_comparacao(resultados, tempo_medio_map):
    print("\n" + "=" * 96)
    print("ANALISE COMPARATIVA")
    print("=" * 96)
    cabecalho = "{:<44}{:>14}{:>11}{:>9}{:>9}{:>9}".format(
        "Algoritmo", "Tempo medio", "Expandidos", "Gerados", "Passos", "Caminho"
    )
    print(cabecalho)
    print("{:<44}{:>14}{:>11}{:>9}{:>9}{:>9}".format("", "(us)", "", "", "", ""))
    print("-" * 96)
    for res in resultados:
        solucao = res["solucao"]
        comprimento = len(caminho_da_solucao(solucao)) - 1 if solucao is not None else "-"
        profundidade = solucao.profundidade if solucao is not None else "-"
        print("{:<44}{:>14.2f}{:>11}{:>9}{:>9}{:>9}".format(
            res["algoritmo"],
            tempo_medio_map[res["sigla"]] * 1e6,
            res["expandidos"],
            res["gerados"],
            profundidade,
            comprimento,
        ))
    print("-" * 96)
    print("'Passos' = profundidade do no-meta (comprimento do caminho encontrado).")


def ler_estado_inicial(argv):
    inicial = None
    mostrar_arvore = True
    repeticoes = REPETICOES_PADRAO
    i = 0
    while i < len(argv):
        arg = argv[i]
        if arg == "--sem-arvore":
            mostrar_arvore = False
        elif arg == "--repeticoes":
            i += 1
            if i >= len(argv):
                raise ValueError("--repeticoes requer um numero")
            repeticoes = int(argv[i])
        elif arg in ("-h", "--help"):
            print(__doc__)
            raise SystemExit(0)
        else:
            if inicial is not None or i + 1 >= len(argv):
                raise ValueError("argumento invalido: " + arg)
            inicial = (int(arg), int(argv[i + 1]))
            i += 1
        i += 1
    if inicial is None:
        texto = input("Estado inicial (a b), padrao 0 0: ").strip()
        if not texto:
            inicial = (0, 0)
        else:
            partes = texto.replace(",", " ").split()
            inicial = (int(partes[0]), int(partes[1]))
    a, b = inicial
    if not (0 <= a <= CAP_4 and 0 <= b <= CAP_3):
        raise ValueError("estado invalido: ({}, {}) - jarro 4L aceita 0..4 e jarro 3L aceita 0..3".format(a, b))
    if repeticoes < 1:
        raise ValueError("--repeticoes deve ser >= 1")
    return inicial, mostrar_arvore, repeticoes


def medir_tempo(funcao, inicial, repeticoes, tempo_unitario):
    if tempo_unitario > 0.05:
        repeticoes = max(1, int(repeticoes * 0.05 / tempo_unitario))
    t0 = time.perf_counter()
    for _ in range(repeticoes):
        funcao(inicial)
    total = time.perf_counter() - t0
    return total / repeticoes, repeticoes


def executar(funcao, inicial, repeticoes):
    t0 = time.perf_counter()
    resultado = funcao(inicial)
    tempo_unitario = time.perf_counter() - t0
    tempo_medio, reps = medir_tempo(funcao, inicial, repeticoes, tempo_unitario)
    return resultado, tempo_medio, reps


def main():
    configurar_terminal()
    try:
        inicial, mostrar_arvore, repeticoes = ler_estado_inicial(sys.argv[1:])
    except (ValueError, IndexError) as erro:
        print("Erro: {}".format(erro), file=sys.stderr)
        print("Uso: python jarros.py [a b] [--sem-arvore] [--repeticoes N]", file=sys.stderr)
        raise SystemExit(1)

    algoritmos = [
        buscar_largura,
        buscar_profundidade,
        buscar_aprof_iterativo,
    ]

    print("=" * 78)
    print("PROBLEMA DOS JARROS D'AGUA - busca sem informacao")
    print("Jarros: 4 L e 3 L | Estado inicial: {} | Meta: 2 L em qualquer jarro".format(_fmt(inicial)))
    print("=" * 78)

    resultados = []
    tempos = {}
    reps_usadas = {}
    for funcao in algoritmos:
        resultado, tempo_medio, reps = executar(funcao, inicial, repeticoes)
        resultados.append(resultado)
        tempos[resultado["sigla"]] = tempo_medio
        reps_usadas[resultado["sigla"]] = reps

    for res in resultados:
        imprimir_caminho(res)
        imprimir_arvore(res, mostrar_arvore)
        imprimir_metricas(res, tempos[res["sigla"]], reps_usadas[res["sigla"]])
        if res["sigla"] == "IDDFS":
            imprimir_historico_iddfs(res)

    imprimir_comparacao(resultados, tempos)
    print()


if __name__ == "__main__":
    main()
