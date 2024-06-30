# trabalho2-mc714-2024s1

Este repositório contém o Trabalho 2 da disciplina MC714 - Sistemas Distribuídos, feito pelos alunos **Caio Petrucci dos Santos Rosa (RA 248245)** e **Jonathan do Ouro (RA 248364)**.

O relatório e o vídeo explicativo do trabalho podem ser encontrados nos seguintes, respectivamente: [Relatório](dummy) e [Vídeo](dummy).

## Problema de motivação

Construir um banco de dados distribuído.

Para construção da aplicação, foi utilizado os seguintes algoritmos:

- Algoritmo [Raft](https://thesecretlivesofdata.com/raft/) de consenso distribuído.

- Relógio de Lamport.

- Locks de exclusão mútua.

Para a comunicação entre diferentes nós do sistema foi utilizado gRPC e protobuffers.

## Execução do código

O trabalho foi implementado utilizando a linguagem de programação Go.

Para construir a imagem Docker, execute esse comando:

```bash
$ docker build -t trabalho2-mc714-dev .
```

Para rodar o container, execute esse comando:

```bash
$ docker run -t trabalho2-mc714-dev
```

Para executar diversas instâncias/nós do sistema, rode o seguinte comando com `docker-compose`:

```bash
$ docker compose up
```