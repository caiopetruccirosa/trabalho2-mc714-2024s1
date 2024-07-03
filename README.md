# trabalho2-mc714-2024s1

Este repositório contém o Trabalho 2 da disciplina MC714 - Sistemas Distribuídos, feito pelos alunos **Caio Petrucci dos Santos Rosa (RA 248245)** e **Jonathan do Ouro (RA 248364)**.

O relatório e o vídeo explicativo do trabalho podem ser encontrados nos seguintes, respectivamente: [Relatório](dummy) e [Vídeo](dummy).

## Algoritmos implementados

Neste trabalho foram implementados os seguintes algoritmos:

- Relógio de Lamport (`./lamport-mutual-exclusion`);

- Algoritmo de exclusão mútua com Relógio de Lamport (`./lamport-mutual-exclusion`);

- Algoritmo valentão para eleição de líder (`./bully-algorithm`).

Para a comunicação entre diferentes nós do sistema foi utilizado gRPC e Protocol Buffers (também conhecido como protobuf).

## Execução do código

O trabalho foi implementado utilizando a linguagem de programação Python.

É possível executar dois sistemas neste projeto. Um sistema de nós está implementado na pasta `./lamport-mutual-exclusion` e o outro está implementado na pasta `./bully-algorithm`. Os comandos descritos devem ser executados dentro de uma das pastas.

Para iniciar/executar todos os nós do sistema, com todas as configurações corretas, rode o seguinte comando:

```bash
$ docker compose up --detach --build
```

Para parar todos os nós de ambos os sistemas, rode o seguinte seguinte comando:

```bash
$ docker compose down
```

Para fins de demonstração, pode ser interessante interromper a execução de algum container. Para isso, execute os seguintes comandos:

```bash
$ docker container list
$ docker kill <container_id>
```