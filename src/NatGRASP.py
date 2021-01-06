'''
Projeto Final: Mateurística para o Problema dos Brigadistas.

NatGRASP.py: Mateurística baseada no GRASP criada por Natanael Ramos et al.

Disciplina:
    MC859/MO824 - Pesquisa Operacional.
Autores:
    Eduardo Barros Innarelli - RA 170161
    Victor Ferreira Ferrari  - RA 187890

Universidade Estadual de Campinas - UNICAMP - 2020

Modificado em: 05/01/2021
'''

from argparse import ArgumentParser
from math import ceil, inf
from random import sample, seed
from time import time
from types import FunctionType
from os.path import exists, split

from Solution import Solution
from FFP import FFP
from f_desc import num_of_descendants


class NatGRASP(object):
    def __init__(self, ffp: FFP, k: int, f: FunctionType, eps: float,
                 time_limit: float, start_time: float):
        self.ffp = ffp
        self.k = k
        self.f = f
        self.eps = eps
        self.limit = time_limit
        self.start_time = start_time

    def constructive_heuristic_th(self, alpha: float):
        '''
        Heurística construtiva Th executada no modo probabilístico, onde em
        cada etapa são escolhidos até D vértices para serem defendidos de forma
        aleatória, com maior prioridade àqueles que estão ameaçados.

            Args:
                alpha (float): parâmetro alpha do GRASP, que rege o quão guloso
                    ou aleatória é a heurística.
            Returns:
                A solução com os vértices defendidos, queimados e o custo.
        '''

        B = self.ffp.B
        D = self.ffp.D
        G = self.ffp.G
        n = G.number_of_nodes()

        # Inicialmente defendidos e queimados
        defended = set()
        burned = set(B)

        # Conjunto de vértices intocados
        U = set(G.nodes - B)

        # Registrar iterações em que um vértice é "tocado" (defendido ou
        # queimado)
        its = [0 if v in burned else inf for v in range(n)]
        t = 1

        # Tentar executar enquanto houver vértices intocados
        while len(U) > 0:

            # Os vértices ameaçados são os vizinhos dos vértices queimados que
            # não estão defendidos ou queimados
            th = set()
            for b in burned:
                th.update([
                    v_n for v_n in G.adj[b]
                    if v_n not in defended.union(burned)
                ])

            # Se não houver vértices ameaçados, todos estão queimados,
            # defendidos ou salvos
            if len(th) == 0:
                break

            # Rankear candidatos (maior prioridade aos ameaçados)
            ranked = list(th) + list(U - th)

            # Construir lista de candidatos restritos (RCL)
            RCL = ranked[:ceil(alpha * len(ranked))]

            # Defender até D vértices da RCL
            defend = sample(RCL, D if D < len(RCL) else len(RCL))

            # Queimar vértices ameaçados não defendidos
            burn = th - set(defend)

            # Atualizar iterações
            for v in burn.union(defend):
                its[v] = t
            t += 1

            # Atualizar conjuntos
            U -= th.union(defend)
            defended.update(defend)
            burned.update(burn)

        # Construir e retornar solução
        sol = Solution(defended=defended, burned=burned,
                       iterations=its, T=t)
        sol.calculate_cost(G)
        sol.construct_full_neighborhood(self.k, G)
        return sol

    def pool_selection(self, S: set, rho: int):
        '''
        Método que seleciona um pool de tamanho `rho` do conjunto de soluções
        `S`. O objetivo é selecionar um nº pequeno de soluções diversas e de
        boa qualidade, visto que a busca local envolve a resolução do modelo
        PLI.

            Args:
                S   (set): conjunto de soluções únicas geradas pela heurística
                    construtiva.
                rho (int): tamanho desejado do pool.
            Returns:
                O pool de soluções selecionado.
        '''

        S = sorted(S, key=lambda s: s.cost)

        # Criar vetor q de quartis q1, q2, q3 e q4 de S
        # https://pt.wikipedia.org/wiki/Quartil
        n = len(S)
        q = [
            S[n // 4].cost,  # q1
            (S[n // 2].cost + S[(n + 1) // 2].cost) / 2 \
            if n % 2 == 0 else S[n // 2].cost,  # q2
            S[3*n // 4].cost,  # q3
            S[-1].cost  # q4
        ]

        # Subconjuntos Si com soluções de S (menos a melhor) distribuidas entre
        # os quartis
        best = S.pop()
        Si = [[], [], [], []]
        i = 0
        for s in S:
            # Obs: podem haver quartis iguais, por isso o while
            while s.cost > q[i] and i < 3:
                i += 1
            Si[i].append(s)

        # Iniciar pool e armazenar vizinhanças
        pool = []
        n_s = {s: s.neighborhood for s in S}
        n_best = best.neighborhood

        # Pseudocodigo começa aqui:
        # Para cada Si (ao contrário), adiciona no pool até "rho-1" elementos.
        # Em seguida, verifica diversidade, substituindo os elementos
        # menos diversos até acabar o último conjunto.
        for i in range(4)[::-1]:
            for s in Si[i]:

                # Adicionar as primeiras rho-1 soluções visitadas ao pool
                if len(pool) < rho-1:
                    pool.append(s)

                else:
                    # Solução do pool com menor diferença simétrica da
                    # vizinhança em relação a n_best
                    old_s = min(pool, key=lambda x: len(
                        n_s[x].symmetric_difference(n_best)))

                    # Se a diferença simétrica da vizinhanaça de s em rel. a
                    # n_best for maior que a de old_s, substituir old_s por s
                    # no pool
                    if len(n_s[s].symmetric_difference(n_best)) > \
                            len(n_s[old_s].symmetric_difference(n_best)):
                        pool.remove(old_s)
                        pool.append(s)

            # Parar se pool estiver cheio, para priorizar soluções boas
            if len(pool) == rho-1:
                break

        return pool, best

    def neighborhood_update(self, sigma: float, solution: Solution):
        return min(1, sigma+0.1) if solution.optimal else max(0, sigma-0.1)

    def adaptive_local_search(self, problem: FFP, pool: list,
                              best_sol: Solution, curr_time: float):
        '''
            Função para busca local adaptativa da mateurística baseada no
            GRASP. Faz busca local em todos os elementos de um pool de
            soluções, atualizando os hiperparâmetros de acordo.

                Args:
                    problem    (FFP): O problema a ser resolvido.
                    pool       (list): o pool de soluções a ser explorado.
                    best_sol   (Solution): melhor solução do pool.
                    curr_time  (float): duração atual da execução.
        '''

        # Inicializar parâmetros.
        pool.reverse()
        inc_sol = best_sol
        sigma, rho = 0.5, len(pool)
        local_time = (self.limit - curr_time)/2

        # Explorar pool de soluções (exceto a melhor)
        for s in pool:
            sol_time = (self.limit - curr_time - local_time)/rho

            # Busca local com T iterações
            T = ceil((1+self.eps)*s.T)
            curr_sol = problem.local_search(s, self.k, sigma, self.f, T,
                                            sol_time)
            inc_sol = curr_sol if curr_sol.cost > inc_sol.cost else inc_sol

            # Atualizar sigma e outros parâmetros
            sigma = self.neighborhood_update(sigma, curr_sol)
            rho = rho - 1
            curr_time = time() - self.start_time

        # Explorar melhor solução (agora com vizinhança adaptada)
        T = ceil((1+self.eps)*best_sol.T)
        curr_sol = problem.local_search(best_sol, self.k, sigma, self.f,
                                        T, local_time)
        inc_sol = curr_sol if curr_sol.cost > inc_sol.cost else inc_sol
        curr_time = time() - self.start_time

        return self.intensification(problem, sigma, inc_sol, curr_time)

    def intensification(self, problem: FFP, sigma: float,
                        best_sol: Solution, curr_time: float):
        '''
            Função de intensificação de busca da mateurística baseada no
            GRASP. Realiza uma série de buscas locais em cima da melhor
            solução, com diferentes valores de "sigma" para busca local.
            Early stopping em caso de convergência.

                Args:
                    problem    (FFP): O problema a ser resolvido.
                    sigma      (float): fração de elementos da vizinhança.
                    best_sol   (Solution): melhor solução do pool.
                    curr_time  (float): duração atual da execução.
        '''

        # Iniciar parâmetros
        prev_sol = best_sol
        gamma = False
        prev_sig = sigma

        # Consecutivas buscas locais na melhor solução.
        while(curr_time < self.limit):
            N_prev = prev_sol.filter_neighborhood(
                self.k, prev_sig, self.ffp.G, self.f)

            # Busca local com T iterações
            T = ceil((1+self.eps)*prev_sol.T)
            curr_sol = problem.local_search(prev_sol, self.k, prev_sig,
                                            self.f, T, self.limit - curr_time)
            best_sol = curr_sol if curr_sol.cost > best_sol.cost else best_sol

            # Atualizar sigma
            sigma = self.neighborhood_update(sigma, curr_sol)

            # Verificar critérios de parada: convergência e segundo reinício.
            N_curr = curr_sol.filter_neighborhood(
                self.k, sigma, self.ffp.G, self.f)
            if len(N_prev.symmetric_difference(N_curr)) == 0 or \
                    (sigma == prev_sig and gamma):
                break

            # Reinício.
            if sigma == prev_sig and not gamma:
                sigma = 0.5
                gamma = True

            # Atualizar parâmetros
            prev_sol = curr_sol
            prev_sig = sigma
            curr_time = time() - self.start_time

        return best_sol


if __name__ == "__main__":
    # Ler argumentos da linha de comando
    parser = ArgumentParser(add_help=False)
    parser.add_argument('--input-file', type=str, required=True)
    parser.add_argument('--D', type=int, required=True)
    args = parser.parse_args()

    if not exists(args.input_file):
        print("Instance does not exist! Try again.")

    # Instanciar problema
    ffp = FFP(args.D)
    ffp.read_input(args.input_file)

    # Parâmetros
    k = 2
    f = num_of_descendants
    eps = 0.5
    limit = ffp.G.number_of_nodes() / 2
    alpha = 0.3
    eta = 11000
    rho = 4
    seed_number = 1337

    # Instanciar mateurística
    seed(seed_number)
    start_time = time()
    method = NatGRASP(ffp, k, f, eps, limit, start_time)

    # PASSO 1: Construção
    S = dict()

    # Critério de parada 1: eta iterações
    for _ in range(eta):

        # Critério de parada 2: metade do limite de tempo alcançado
        if time() - method.start_time >= method.limit / 2:
            break

        curr = method.constructive_heuristic_th(alpha)
        neigh_key = str(sorted(curr.neighborhood))

        # Armazenar solução corrente se não tiver sido encontrada nenhuma
        # solução com a mesma vizinhança ou se a encontrada tiver menor custo
        if neigh_key not in S.keys() or (neigh_key in S.keys() and
                                         curr.cost > S[neigh_key].cost):
            S[neigh_key] = curr

    # Converter S em lista de soluções
    S = list(S.values())

    # PASSO 2: Seleção
    P, best = method.pool_selection(S, rho)

    print("Best before local search:\n", best)

    # PASSO 3: Busca Local
    best = method.adaptive_local_search(ffp, P, best, time()-start_time)

    # PASSO FINAL: Imprimir resultado
    final_time = time()-start_time
    path, filename = split(args.input_file)
    directory = split(path)[1]

    print("Best after local search:\n", best)
    print(f"\"{directory}\",{ffp.G.number_of_nodes()},{best.cost},"
          f"\"{filename}\",{args.D},{final_time:.4f},{seed_number}")
