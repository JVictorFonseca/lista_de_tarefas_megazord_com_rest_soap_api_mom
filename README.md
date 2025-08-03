# 🚀 Gerenciador de Tarefas e Usuários Distribuído (gRPC, REST, SOAP, API Gateway) 🚀

![Python](https://img.shields.io/badge/Python-3.x-blue.svg)
![Go](https://img.shields.io/badge/Go-1.22%2B-blue.svg)
![gRPC](https://img.shields.io/badge/gRPC-Framework-green.svg)
![REST](https://img.shields.io/badge/REST-API-red.svg)
![SOAP](https://img.shields.io/badge/SOAP-Web%20Service-purple.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-Python-009688.svg)
![Spine](https://img.shields.io/badge/Spine-SOAP%20Python-orange.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## 📝 Visão Geral do Projeto

Este projeto é uma demonstração completa de uma **arquitetura de microsserviços** que integra diferentes padrões de comunicação: **gRPC**, **REST** e **SOAP**, orquestrados por um **API Gateway**. Ele permite o gerenciamento de **Tarefas** e **Usuários** através de uma **interface web interativa**.

Para máxima simplicidade na execução, os arquivos de código gRPC e Protobuf gerados já estão **incluídos neste repositório**.

## ✨ Funcionalidades

### Gerenciamento de Tarefas (via gRPC)
* **Criação de Tarefas:** Adicione novas tarefas com título, descrição e criador.
* **Listagem de Tarefas:** Visualize todas as tarefas existentes.
* **Atualização de Tarefas:** Modifique título, descrição ou status de tarefas por ID.
* **Exclusão de Tarefas:** Remova tarefas existentes por ID.
* **Busca de Tarefa:** Encontre uma tarefa específica pelo seu ID.

### Gerenciamento de Usuários (via SOAP)
* **Criação de Usuários:** Registre novos usuários com nome e e-mail.
* **Listagem de Usuários:** Visualize todos os usuários registrados.
* **Busca de Usuário:** Encontre um usuário específico pelo seu ID.

## 📐 Arquitetura do Sistema

A arquitetura emprega um **API Gateway** como ponto de entrada único, roteando e traduzindo requisições para serviços backend especializados.

+------------------------------------+
|                                    |
|         Cliente Web (Frontend)     |<-----------------------------------+
|     (HTML/CSS/JavaScript)          |                                    |
|  (Gerenciamento de Tarefas e Usuários) |          (HTTP/REST)               |
+------------------------------------+                                    |
|
V
+-------------------------------------------------------------------------------------------------+
|                                     API Gateway (Python/FastAPI)                                |
| (Ponto de Entrada Único, Roteamento, HATEOAS, Documentação Swagger)                             |
+-------------------------------------------------------------------------------------------------+
|                                          |                                 |
| (Chamada gRPC para Tarefas)              | (Chamada SOAP para Usuários)    |
V                                          V                                 V
+---------------------+                   +---------------------+             +---------------------+
|                     |                   |                     |             |                     |
| gRPC Task Service   |                   |    Serviço SOAP     |             |   Cliente SOAP      |
| (Go Server)         |                   |  (Python/Spine)     |             |  (Go - usando WSDL) |
|                     |                   | (Gerenciamento de   |             |                     |
|                     |                   |    Usuários)        |             |                     |
+---------------------+                   +---------------------+             +---------------------+
^
| (WSDL)
|
+--------------------------

### Componentes:

* **Cliente Web (`web_client/`):** Interface interativa no navegador (HTML, CSS, JavaScript) que se comunica via REST com o API Gateway.
* **API Gateway (`api_gateway/`):** Desenvolvido em **Python com FastAPI**. É o ponto de entrada RESTful. Roteia requisições de tarefas para o serviço gRPC e requisições de usuários para o serviço SOAP. Implementa HATEOAS e gera documentação Swagger.
* **Serviço gRPC de Tarefas (`go_server/`):** Desenvolvido em **Go**. Gerencia as operações de tarefas. O Gateway se comunica com ele via gRPC.
* **Serviço SOAP de Usuários (`soap_user_service/`):** Desenvolvido em **Python com Spine**. Gerencia as operações de usuários via protocolo SOAP. Expõe seu próprio WSDL.
* **Cliente SOAP (`go_soap_client/`):** Desenvolvido em **Go**. Cliente separado que demonstra o consumo direto do Serviço SOAP de Usuários, utilizando o WSDL.

## 🛠️ Tecnologias Utilizadas

* **Linguagens:** Python (v3.8+), Go (v1.22+), JavaScript (Frontend)
* **Frameworks/Bibliotecas:**
    * **Backend:** FastAPI (Python), Spyne (Python SOAP), `net/smtp` (Go Email)
    * **Comunicação:** gRPC, Protocol Buffers, `httpx` (Python HTTP client), `gosoap` (Go SOAP client)
    * **Frontend:** HTML5, CSS3, JavaScript (Vanilla JS)
* **Ferramentas:** `protoc` (Protocol Buffers Compiler), `pip`, `go mod`
* **Controle de Versão:** Git / GitHub

## 🚀 Como Rodar o Projeto

Siga estes passos para configurar e executar todos os componentes do sistema.

### Pré-requisitos

Certifique-se de ter instalado em sua máquina:

* [**Git**](https://git-scm.com/downloads)
* [**Python 3.8+**](https://www.python.org/downloads/) (com `pip` configurado)
* [**Go 1.22+**](https://go.dev/dl/)

### 1. Clonar o Repositório

Abra seu terminal (ou Prompt de Comando/PowerShell) e execute:

```bash
git clone [https://github.com/SEU_USUARIO/SEU_REPOSITORIO.git](https://github.com/SEU_USUARIO/SEU_REPOSITORIO.git) # Substitua pelo seu link
cd SEU_REPOSITORIO_CLONADO # Substitua pelo nome da sua pasta

2. Instalar Dependências
Na raiz do projeto (SEU_REPOSITORIO_CLONADO), execute os comandos para instalar as bibliotecas necessárias para cada serviço:

# Para Go: Baixa as dependências do módulo Go
go mod tidy

# Para Python: Instala as bibliotecas para FastAPI e Spyne
pip install "uvicorn[standard]" fastapi spyne httpx lxml
# Nota: 'spyne' é a biblioteca para SOAP
# 'uvicorn[standard]' inclui uvicorn e httptools/watchfiles para rodar FastAPI

3. Gerar Código gRPC (Se necessário, caso não esteja commitado)
Embora os arquivos gerados estejam incluídos para simplificar, se você precisar regenerá-los (ex: após alterar tasks.proto), siga:

Instale protoc: Baixe protoc-X.X-win64.zip de protobuf releases e adicione a pasta bin ao seu PATH.

Instale plugins Go/Python:

go install google.golang.org/protobuf/cmd/protoc-gen-go@latest
go install google.golang.org/grpc/cmd/protoc-gen-go-grpc@latest
pip install grpcio grpcio-tools

Gere o código (na raiz do projeto):

protoc --go_out=./go_server/pb --go_opt=paths=source_relative --go-grpc_out=./go_server/pb --go-grpc_opt=paths=source_relative tasks.proto
python -m grpc_tools.protoc -I. --python_out=./python_client --grpc_python_out=./python_client tasks.proto


4. Executar os Serviços Backend (Em Terminais Separados)
Você precisará de três terminais separados para rodar os serviços backend.

⚠️ ATENÇÃO: CONFIGURAÇÃO DE FIREWALL ⚠️
É CRUCIAL que você permita os executáveis do Python (python.exe) e do Go (go.exe) através do firewall do Windows Defender na(s) máquina(s) onde os serviços estão rodando. As portas utilizadas são:

SOAP Service: 8001 (TCP)

API Gateway: 8000 (TCP)

gRPC Server: 50051 (TCP)

a. Iniciar o Serviço SOAP de Usuários (Python)
Abra um terminal na pasta soap_user_service/.

Execute:

python service.py

Você verá logs indicando que o serviço SOAP está ouvindo na porta 8001 e que o WSDL está disponível em http://0.0.0.0:8001/?wsdl. Deixe este terminal aberto.
