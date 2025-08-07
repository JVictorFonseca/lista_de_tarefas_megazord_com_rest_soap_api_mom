Canva: https://www.canva.com/design/DAGvWmlY6oY/_BA6XeQjnBhe_NJ5dy145Q/edit?utm_content=DAGvWmlY6oY&utm_campaign=designshare&utm_medium=link2&utm_source=sharebutton
Vídeo: https://drive.google.com/file/d/1RUp4eH56886z_68clLrJEV4sTk3zNWwC/view?usp=drive_link


# Gerenciador de Tarefas e Usuários Distribuído (gRPC, REST, SOAP, MOM) 

Python (https://img.shields.io/badge/Python-3.x-blue.svg)
Go (https://img-shields.io/badge/Go-1.22%2B-blue.svg)
gRPC (https://img.shields.io/badge/gRPC-Framework-green.svg)
REST (https://img.shields.io/badge/REST-API-red.svg)
SOAP (https://img.shields.io/badge/SOAP-Web%20Service-purple.svg)
FastAPI (https://img.shields.io/badge/FastAPI-Python-009688.svg)
Spine (https://img.shields.io/badge/Spine-SOAP%20Python-orange.svg)
RabbitMQ (https://img.shields.io/badge/RabbitMQ-MOM-ff6600.svg)
License (https://img.shields.io/badge/License-MIT-yellow.svg)

## Visão Geral do Projeto

Este projeto é uma demonstração completa de uma arquitetura de microsserviços que integra diferentes padrões de comunicação: gRPC, REST, SOAP e um MOM (Message-Orientated Middleware), orquestrados por um API Gateway. Ele permite o gerenciamento de Tarefas e Usuários através de uma interface web interativa.

Para máxima simplicidade na execução, os arquivos de código gRPC e Protobuf gerados já estão incluídos neste repositório.

## Funcionalidades

### Gerenciamento de Tarefas (via gRPC)
* Criação de Tarefas: Adicione novas tarefas com título, descrição e criador.
* Listagem de Tarefas: Visualize todas as tarefas existentes.
* Atualização de Tarefas: Modifique título, descrição ou status de tarefas por ID.
* Exclusão de Tarefas: Remova tarefas existentes por ID.
* Busca de Tarefa: Encontre uma tarefa específica pelo seu ID.

### Gerenciamento de Usuários (via SOAP)
* Criação de Usuários: Registre novos usuários com nome e e-mail.
* Listagem de Usuários: Visualize todos os usuários registrados.
* Busca de Usuário: Encontre um usuário específico pelo seu ID.

## Arquitetura do Sistema

A arquitetura emprega um API Gateway como ponto de entrada único, roteando e traduzindo requisições para serviços backend especializados. A comunicação para a criação de tarefas e usuários pode ser assíncrona, utilizando um MOM (RabbitMQ).

[Diagrama de Arquitetura]

Componentes:

* Cliente Web (web_client/): Interface interativa no navegador (HTML, CSS, JavaScript) que se comunica via REST com o API Gateway.
* API Gateway (api_gateway/): Desenvolvido em Python com FastAPI. É o ponto de entrada RESTful. Roteia requisições de tarefas para o serviço gRPC e requisições de usuários para o serviço SOAP. Implementa HATEOAS e gera documentação Swagger.
* Serviço gRPC de Tarefas (go_server/): Desenvolvido em Go. Gerencia as operações de tarefas. O Gateway se comunica com ele via gRPC.
* Serviço SOAP de Usuários (soap_user_service/): Desenvolvido em Python com Spine. Gerencia as operações de usuários via protocolo SOAP. Expõe seu próprio WSDL.
* Cliente SOAP (go_soap_client/): Desenvolvido em Go. Cliente separado que demonstra o consumo direto do Serviço SOAP de Usuários, utilizando o WSDL.

## Tecnologias Utilizadas

* Linguagens: Python (v3.8+), Go (v1.22+), JavaScript (Frontend)
* Frameworks/Bibliotecas:
    * Backend: FastAPI (Python), Spyne (Python SOAP), net/smtp (Go Email)
    * Comunicação: gRPC, Protocol Buffers, httpx (Python HTTP client), gosoap (Go SOAP client)
    * Frontend: HTML5, CSS3, JavaScript (Vanilla JS)
* Ferramentas: protoc (Protocol Buffers Compiler), pip, go mod, Docker e Docker Compose (para o RabbitMQ)
* Controle de Versão: Git / GitHub

## Como Rodar o Projeto

Siga estes passos para configurar e executar todos os componentes do sistema.

### Pré-requisitos

Certifique-se de ter instalado em sua máquina:

* Git (https://git-scm.com/downloads)
* Python 3.8+ (com pip configurado)
* Go 1.22+ (https://go.dev/dl/)
* Docker Desktop (https://www.docker.com/products/docker-desktop/) (para rodar o RabbitMQ)

### 1. Clonar o Repositório

Abra seu terminal (ou Prompt de Comando/PowerShell) e execute:

git clone https://github.com/SEU_USUARIO/SEU_REPOSITORIO.git # Substitua pelo seu link
cd SEU_REPOSITORIO_CLONADO # Substitua pelo nome da sua pasta

### 2. Instalar Dependências

Na raiz do projeto (SEU_REPOSITORIO_CLONADO), execute os comandos para instalar as bibliotecas necessárias para cada serviço:

# Para Go: Baixa as dependências do módulo Go
go mod tidy

# Para Python: Instala as bibliotecas para FastAPI e Spyne
pip install "uvicorn[standard]" fastapi spyne httpx lxml
# Nota: 'spyne' é a biblioteca para SOAP
# 'uvicorn[standard]' inclui uvicorn e httptools/watchfiles para rodar FastAPI

### 3. Gerar Código gRPC (Se necessário, caso não esteja commitado)

Embora os arquivos gerados estejam incluídos para simplificar, se você precisar regenerá-los (ex: após alterar tasks.proto), siga:

* Instale protoc: Baixe protoc-X.X-win64.zip de protobuf releases (https://github.com/protocolbuffers/protobuf/releases) e adicione a pasta bin ao seu PATH.

* Instale plugins Go/Python:

  go install google.golang.org/protobuf/cmd/protoc-gen-go@latest
  go install google.golang.org/grpc/cmd/protoc-gen-go-grpc@latest
  pip install grpcio grpcio-tools
  
* Gere o código (na raiz do projeto):

  protoc --go_out=./go_server/pb --go_opt=paths=source_relative --go-grpc_out=./go_server/pb --go-grpc_opt=paths=source_relative tasks.proto
  python -m grpc_tools.protoc -I. --python_out=./python_client --grpc_python_out=./python_client tasks.proto
  
### 4. Executar os Serviços Backend (Em Terminais Separados)

Você precisará de três terminais separados para rodar os serviços backend.

ATENÇÃO: CONFIGURAÇÃO DE FIREWALL 
É CRUCIAL que você permita os executáveis do Python (python.exe) e do Go (go.exe) através do firewall do Windows Defender na(s) máquina(s) onde os serviços estão rodando. As portas utilizadas são:

* SOAP Service: 8001 (TCP)

* API Gateway: 8000 (TCP)

* gRPC Server: 50051 (TCP)

* RabbitMQ: 5672 (TCP) e 15672 (TCP)

#### a. Iniciar o RabbitMQ (MOM)

1. Abra um terminal na raiz do projeto.

2. Execute:

   docker compose up -d
   
   Você verá logs indicando que o contêiner foi iniciado. Deixe este terminal aberto.

#### b. Iniciar o Serviço SOAP de Usuários (Python)

1. Abra um novo terminal na pasta soap_user_service/.

2. Execute:

   python service.py
   
   Você verá logs indicando que o serviço SOAP está ouvindo na porta 8001. Deixe este terminal aberto.

#### c. Iniciar o Servidor gRPC de Tarefas (Go)

1. Abra um novo terminal na pasta go_server/.

2. Execute:

   go run main.go
   
   Você verá logs indicando que o servidor gRPC está ouvindo na porta 50051. Deixe este terminal aberto.

#### d. Iniciar o API Gateway (Python/FastAPI)

1. Abra um novo terminal na pasta api_gateway/.

2. Execute:

   python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
   
   Você verá logs indicando que o FastAPI está rodando na porta 8000. Deixe este terminal aberto.

   * A documentação interativa (Swagger UI) do Gateway estará disponível em: http://localhost:8000/swagger

### 5. Executar os Clientes (Em Terminais/Navegadores Separados)

#### a. Acessar o Cliente Web (Frontend)

1. Abra seu navegador web.

2. Navegue até o diretório web_client/ no seu computador e abra o arquivo index.html diretamente.

   * Alternativamente, você pode usar um servidor HTTP simples (como o Live Server do VS Code, ou Python's http.server):

     * Abra um terminal na pasta web_client/.

     * Execute: python -m http.server 8080

     * Então, acesse http://localhost:8080/index.html no seu navegador.

3. A interface do gerenciador de tarefas e usuários será carregada.

#### b. Executar o Cliente SOAP (Go)

1. Abra um novo terminal na pasta go_soap_client/.

2. Execute:

   go run client.go
   
   Este cliente fará chamadas diretas ao Serviço SOAP de Usuários (na porta 8001) e exibirá os resultados no terminal.

## Como Usar e Testar

### No Cliente Web (index.html):

* Tarefas: Use os campos e botões na seção "Tarefas" para criar, listar, atualizar, deletar e buscar tarefas. Observe como as requisições REST vão para o Gateway, que as traduz para gRPC e as envia ao Servidor Go.

* Usuários: Use os campos e botões na seção "Usuários" para criar e listar usuários. Observe como as requisições REST vão para o Gateway, que as traduz para SOAP e as envia ao Serviço SOAP Python.

* Logs da Aplicação: A caixa "Logs da Aplicação" no frontend mostrará o status das requisições HTTP para o Gateway.

* Console do Navegador: Abra o console do desenvolvedor (F12) para ver as requisições de rede e as respostas do Gateway.

### Nos Terminais Backend:

* Serviço SOAP: Observe os logs de criação e listagem de usuários.

* Servidor gRPC: Observe os logs de criação, listagem, atualização e exclusão de tarefas.

* API Gateway: Observe os logs detalhados de cada requisição REST recebida, a tradução para gRPC/SOAP e as respostas dos serviços internos.

### No Terminal do Cliente SOAP Go:

* Observe as chamadas diretas ao serviço SOAP e as respostas.

## Próximas Melhorias Possíveis

* Persistência de Dados: Integrar um banco de dados (SQLite, PostgreSQL) para todos os serviços.

* Autenticação/Autorização: Adicionar mecanismos de segurança.

* Monitoramento: Implementar ferramentas de monitoramento e tracing.

* Dockerização: Empacotar cada serviço em um contêiner Docker para facilitar o deployment.

Este é um projeto robusto e demonstra um conhecimento aprofundado de arquitetura de microsserviços e comunicação entre sistemas. Boa sorte na implementação e na apresentação!
