Firefighter Problem (FFP)
================================

Projeto Final de MO824 - Tópicos em Otimização Combinatória.

Implementação de uma mateurística para o Problema dos Brigadistas, baseada no GRASP e proposta por 
[Ramos, et al](https://onlinelibrary.wiley.com/doi/full/10.1111/itor.12638).
Inclui também a implementação de dois modelos lineares inteiros para o problema.

**Dependências:**

Antes de executar, é preciso estar em um ambiente Python com os pacotes do `requirements.txt` e o 
[Gurobi](https://www.gurobi.com/wp-content/plugins/hd_documentations/documentation/9.1/quickstart_linux.pdf) instalados.

O *visualizador de soluções* tem requisitos extras, detalhados em seu repositório, que não estão presentes em `requirements.txt`.

**Como executar:** 

Para testar qualquer método implementado, na pasta raiz do projeto execute o comando:

```
python3 src/main.py [-h] --input-file INPUT_FILE [--out-file OUT_FILE] [--D D [D ...]]
                    [--instance-list | --visualizer]
                    method
```
Onde `INPUT_FILE` é a instância (instâncias disponíveis em `instances/tipo_de_inst/nome_da_inst`,  
e `method` é o método que deve ser avaliado (opções: `all`, `ilp`, `ffm`, `mffm`, `grasp`).

Parâmetros opcionais incluem `D`: o número de bombeiros que devem ser considerados para a instância
(pode-se passar uma lista), e `OUT_FILE`: o nome do arquivo de saída (sem incluir _path_). Se nenhum
arquivo de saída for passado, os resultados são impressos na saída padrão.

Finalmente, o parâmetro opcional `instance-list` considera `INPUT_FILE` como um arquivo
que contém, em cada linha, o caminho para uma instância. O parâmetro opcional `visualizer`
gera um arquivo que pode ser fornecido como entrada para o visualizador de soluções. Esses
dois parâmetros são mutualmente exclusivos, e apenas um método/D é usado com `visualizer`
(`OUT_FILE` não é necessário, e será desconsiderado).

**Verbosidade:**

Por padrão, ao executar, apenas o progresso da execução, e possivelmente o resultado final de cada
execução, são impressos na saída padrão. Todos os métodos usam o _solver_ Gurobi, mas a ferramenta
foi configurada para não gerar saída verbosa. Para incluir a saída da ferramenta, basta trocar a
configuração do arquivo `gurobi.env` para `OutputFlag 1`.

**Resultados:**

Os resultados da pasta `results` estão divididos em subpastas com base em finalidade e origem. Na
subpasta `nat` estão os resultados do artigo original, e em `project` estão os resultados desta
implementação. Em `profiles` se encontram perfis de desempenho gerados pelo _script_ `src/pp.py`
a partir dos resultados desta implementação. Finalmente, em `visualizer` estão arquivos de entrada
e vídeos/imagens GIF demonstrando soluções do problema para certas instâncias.

**Grupo:**
  - Eduardo Barros Innarelli (170161)
  - Victor Ferreira Ferrari (187890)

**Referência:**
N. Ramos, C. C. de Souza, e P. J. de Rezende, "A matheuristic for the firefighter problem on graphs",
_International Transactions in Operational Research_, vol. 27, no. 2, pp. 739-766, 2020. DOI 10.1111/itor.12638.
Disponível em: [https://onlinelibrary.wiley.com/doi/full/10.1111/itor.12638](https://onlinelibrary.wiley.com/doi/full/10.1111/itor.12638).

Disciplina oferecida no 2º semestre de 2020 pelo professor [Fábio Luiz Usberti](https://www.ic.unicamp.br/~fusberti/).

[Instituto de Computação](http://ic.unicamp.br/) - [UNICAMP](http://www.unicamp.br/unicamp/) (Universidade Estadual de Campinas)
