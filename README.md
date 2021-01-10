Firefighter Problem (FFP)
================================

Projeto Final de MO824 - Tópicos em Otimização Combinatória.

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
(pode-se passar uma lista), e `OUT_FILE`: o nome do arquivo de saída (sem incluir _path_).

Finalmente, o parâmetro opcional `instance-list` considera `INPUT_FILE` como um arquivo
que contém, em cada linha, o caminho para uma instância. O parâmetro opcional `visualizer`
gera um arquivo que pode ser fornecido como entrada para o visualizador de soluções. Esses
dois parâmetros são mutualmente exclusivos, e apenas um método/D é usado com `visualizer`.

**Grupo:**
  - Eduardo Barros Innarelli (170161)
  - Victor Ferreira Ferrari (187890)

Disciplina oferecida no 2º semestre de 2020 pelo professor [Fábio Luiz Usberti](https://www.ic.unicamp.br/~fusberti/).

[Instituto de Computação](http://ic.unicamp.br/) - [UNICAMP](http://www.unicamp.br/unicamp/) (Universidade Estadual de Campinas)
