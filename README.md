# Sistema de Controle de Frequência UFVJM

Projeto desenvolvido para a disciplina de **Sistemas Distribuídos**, sob orientação do Prof. Alessandro Vivas Andrade.

O sistema automatiza o controle de presença de alunos por meio de QR Code dinâmico, utilizando uma arquitetura modular preparada para escalabilidade, com processamento assíncrono e tolerância a falhas.

## Visão Geral e Maturidade Arquitetural

O sistema foi projetado seguindo princípios de **baixo acoplamento** e **alta coesão**. Embora seja um monólito em sua estrutura de implantação, ele utiliza padrões de sistemas distribuídos para garantir integridade e performance:

1.  **Processamento Assíncrono:** O registro de presença não bloqueia o usuário. A validação é feita na API, mas a persistência e tarefas derivadas (como notificações) ocorrem em background via **Celery** e **RabbitMQ**.
2.  **Arquitetura Orientada a Eventos (EDA):** O sistema utiliza **Django Signals** para reagir a eventos (ex: nova presença válida) sem acoplar os serviços de presença, acadêmico e de notificações.
3.  **Consistência e Cache:** O **Redis** atua como camada de cache e lock distribuído, evitando condições de corrida (race conditions) em registros duplicados.
4.  **Auditoria Completa:** Todas as entidades críticas possuem histórico de alterações via `django-simple-history`, garantindo rastreabilidade total — essencial para sistemas de auditoria acadêmica.

## Tecnologias e Infraestrutura

- **Backend:** Python 3.11 + Django 6.0.
- **Banco de Dados:** PostgreSQL (Produção/Container) e SQLite (Desenvolvimento Local).
- **Mensageria (Broker):** RabbitMQ.
- **Cache & Locks:** Redis.
- **Tasks:** Celery.
- **Containerização:** Docker & Docker Compose.

---

## Como Executar o Projeto (Via Docker)

Esta é a forma recomendada e mais rápida, pois configura todo o ambiente distribuído (Banco, Redis, RabbitMQ e Workers) automaticamente.

### 1. Pré-requisitos
- Docker e Docker Compose instalados.

### 2. Configuração
O sistema já possui um arquivo `.env` configurado em `apps_services/core_service/.env` com os valores padrão para o ambiente de container.

### 3. Execução
Na raiz do projeto (onde está o arquivo `docker-compose.yml`), execute:
```bash
docker-compose up --build
```
Este comando irá:
- Baixar e configurar as imagens do PostgreSQL, Redis e RabbitMQ.
- Construir a imagem do Django e instalar as dependências.
- Aplicar as migrações ao banco de dados automaticamente.
- Iniciar o servidor web em `http://localhost:8000`.
- Iniciar o Worker do Celery para processar as presenças.

### 4. Criar Superusuário (Admin)
Com os containers rodando, abra outro terminal e execute:
```bash
docker-compose exec web python manage.py createsuperuser
```

---

## Como Executar o Projeto (Localmente)

Caso prefira rodar sem Docker, o sistema mantém compatibilidade com SQLite para facilitar o desenvolvimento rápido.

### 1. Instalação
```bash
python -m venv venv
source venv/bin/activate  # No Windows: .\venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Serviços Necessários
Você precisará ter o **Redis** e o **RabbitMQ** instalados e rodando em sua máquina:
```bash
sudo service redis-server start
sudo service rabbitmq-server start
```

### 3. Execução do Servidor e Worker
Em terminais separados:
```bash
# Terminal 1: Servidor Django
cd apps_services/core_service
python manage.py migrate
python manage.py runserver

# Terminal 2: Worker Celery
cd apps_services/core_service
celery -A core_config worker -l info
```

---

## Fluxo Principal de Presença

1.  **Professor:** Abre uma aula vinculada a uma sala (geolocalizada).
2.  **Sistema:** Gera um QR Code dinâmico com token UUID rotativo.
3.  **Aluno:** Escaneia o código; o sistema valida:
    - Autenticação e matrícula na turma.
    - Janela de horário da aula.
    - Localização (Raio permitido em relação à sala).
    - IP institucional.
    - Duplicidade (via Lock no Redis).
4.  **Resultado:** Se válido, a tarefa é enviada para a fila e processada assincronamente.

## Checklist de Requisitos (Sistemas Distribuídos)

- [x] **Persistência Relacional:** Migração transparente entre SQLite e PostgreSQL.
- [x] **Comunicação Assíncrona:** Implementada com RabbitMQ e Celery.
- [x] **Coordenação:** Lock distribuído via Redis para evitar duplicidade de dados.
- [x] **Escalabilidade:** Estrutura pronta para subir múltiplos workers ou instâncias web.
- [x] **Containerização:** Dockerfile e Compose prontos para deploy.

## Autores
- Daniel Rodrigues
- Joana Martins
