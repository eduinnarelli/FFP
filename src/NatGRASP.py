'''
Projeto Final: Mateurística para o Problema dos Brigadistas.

nat_grasp.py: Mateurística baseada no GRASP criada por Natanael Ramos et al.

Disciplina:
    MC859/MO824 - Pesquisa Operacional.
Autores:
    Eduardo Barros Innarelli - RA 170161
    Victor Ferreira Ferrari  - RA 187890

Universidade Estadual de Campinas - UNICAMP - 2020

Modificado em: 17/12/2020
'''

from Solution import Solution
from FFP import FFP
from math import ceil
from time import time
from types import FunctionType

class NatGRASP(object):
    def __init__(self, k: int, f: FunctionType, eps: float, 
                 time_limit: float, start_time: float):
        self.k = k
        self.f = f
        self.eps = eps
        self.limit = time_limit
        self.start_time = start_time
    
    def constructive_heuristic(self, problem: FFP, alpha: float):
        raise NotImplementedError
    
    def pool_selection(self, S: set, rho: int):
        raise NotImplementedError
        
    def neighborhood_update(self, sigma: float, solution: Solution):
        return min(1, sigma+0.1) if solution.optimal else max(0, sigma-0.1)

    def adaptive_local_search(self, problem: FFP, pool: list,
                              best_sol: Solution, time: float):
        '''
            Função para busca local adaptativa da mateurística baseada no
            GRASP. Faz busca local em todos os elementos de um pool de
            soluções, atualizando os hiperparâmetros de acordo.
            
                Args:
                    problem    (FFP): O problema a ser resolvido.
                    pool       (list): o pool de soluções a ser explorado.
                    best_sol   (Solution): melhor solução do pool.
                    time       (float): duração atual da execução.
        '''
        
        # Inicializar parâmetros.
        pool.reverse()
        pool.remove(best_sol)
        inc_sol = best_sol
        sigma, rho = 0.5, len(pool)
        local_time = (self.limit - time)/2
        
        # Explorar pool de soluções (exceto a melhor)
        for s in pool:
            sol_time = (self.limit - time - local_time)/rho
            problem.T = ceil((1+self.eps)*s.T)
            curr_sol = problem.local_search(s, self.k, sigma, self.f,
                                            sol_time)
            inc_sol = curr_sol if curr_sol.cost > inc_sol.cost else inc_sol
            sigma = neighborhood_update(sigma, curr_sol)
            rho = rho - 1
            time = time() - self.start_time
        
        # Explorar melhor solução (agora com vizinhança adaptada)
        problem.T = ceil((1+self.eps)*best_sol.T)
        curr_sol = problem.local_search(best_sol, self.k, sigma, self.f, 
                                        local_time)
        inc_sol = curr_sol if curr_sol.cost > inc_sol.cost else inc_sol
        time = time() - self.start_time
        
        # TODO: intensificação
        return inc_sol


if __name__ == "__main__":
    # Argumentos da linha de comando
    parser = ArgumentParser(add_help=False)
    parser.add_argument('--input-file', type=str, required=True)
    parser.add_argument('--D', type=int, required=True)
    args = parser.parse_args()

    ffp = FFP(args.D)
    ffp.read_input(args.input_file)
    
    # Parâmetros
    k = 2
    f = None
    eps = 0.5
    limit = 1800
    alpha = 0.3
    eta = 11000
    rho = 4
    
    start_time = time()
    method = NatGRASP(k, f, eps, limit, start_time)
    
    # Passo 1: Construção
    S = set()
    best = method.constructive_heuristic(ffp, alpha)
    S.add(best)
    for i in range(eta-1):
        curr = method.constructive_heuristic(ffp, alpha)
        best = curr if curr.cost > best.cost else best
        S.add(curr)
    
    # Passo 2: Seleção
    P = method.pool_selection(S, rho)
    
    # Passo 3: Busca Local
    best = method.adaptive_local_search(ffp, P, best, time()-start_time)
    
    print(best)
