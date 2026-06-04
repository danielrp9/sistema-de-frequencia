# Sistema de Controle de Frequência UFVJM

Este projeto foi desenvolvido para a disciplina de **Sistemas Distribuídos**, sob orientação do Prof. Alessandro Vivas Andrade. O sistema propõe a automatização do controle de presença estudantil através de uma arquitetura modular que utiliza QR Codes dinâmicos e validações multifatoriais de contexto.

## Lógica de Funcionamento e Arquitetura

O sistema foi estruturado para operar como um ambiente distribuído, garantindo integridade e performance:
*   **Processamento Assíncrono:** O registro de presença e os cálculos de carga horária são processados via **Celery** e **RabbitMQ**. Isso assegura que operações pesadas de banco de dados e notificações não bloqueiem a navegação do usuário.
*   **Desacoplamento via Signals:** Utilizamos **Django Signals** para que os módulos de usuários, acadêmico e presença se comuniquem de forma organizada, mantendo o código modular e fácil de expandir.
*   **Gestão de Concorrência:** O **Redis** atua como um gerenciador de travas distribuídas (*Distributed Locks*), impedindo que instabilidades de rede gerem registros de presença duplicados.

---

## Regras de Negócio e Fluxo de Uso

A segurança do sistema é baseada em camadas, exigindo que o aluno esteja física e logicamente dentro do ambiente universitário.

### 1. Preparação da Base de Dados (Admin)
O sistema exige que o **Administrador** realize o mapeamento prévio da infraestrutura:
*   **Estrutura Institucional:** Cadastro de Departamentos, Cursos e Disciplinas.
*   **Geofencing (Mapeamento de Salas):** Cada sala deve ser cadastrada com suas coordenadas geográficas (latitude/longitude) e um raio de tolerância. O professor apenas seleciona a sala já mapeada, e o sistema assume o controle das validações espaciais.
*   **Gestão de Frequência:** O Admin define a carga horária total das disciplinas. Com base nisso, o sistema monitora o limite de 25% de faltas permitido pelo regulamento, automatizando os alertas para alunos e docentes.

### 2. Controle de Acesso e Perfis
*   **Docentes:** O cadastro de professores é permitido, mas o acesso permanece **bloqueado por padrão**. A liberação das funcionalidades exige aprovação manual do Administrador, garantindo que apenas usuários autorizados gerenciem turmas.
*   **Discentes:** O acesso do aluno é limitado à visualização básica até que ele seja vinculado a uma disciplina ativa por um professor.

### 3. Validação de Presença
Para registrar a frequência, o sistema valida três fatores simultâneos:
*   **IP Institucional:** O dispositivo deve estar conectado à rede interna da universidade. Acessos externos são automaticamente bloqueados.
*   **Geolocalização:** O backend compara o GPS do aluno com as coordenadas da sala. O registro só é concluído se o aluno estiver dentro do raio permitido.
*   **Token Dinâmico:** O QR Code utiliza um UUID que expira periodicamente, o que impede o uso de fotos ou capturas de tela compartilhadas.

---

## Procedimentos de Execução

O sistema oferece duas alternativas de execução, dependendo do nível de isolamento e controle de infraestrutura desejado.

### Alternativa A: Implantação via Docker Compose
Esta opção automatiza a configuração de toda a stack tecnológica (PostgreSQL, Redis, RabbitMQ e Workers) dentro de containers isolados.

1.  **Configuração de Ambiente:** Crie o arquivo `.env` em `apps_services/core_service/.env` seguindo o formato:
    ```env
    DJANGO_SECRET_KEY='sua-chave-secreta-aqui'
    DJANGO_DEBUG=True
    ALLOWED_HOSTS=localhost,127.0.0.1
    DB_HOST=db
    DB_PORT=5432
    DB_NAME=frequencia_db
    DB_USER=postgres
    DB_PASSWORD=postgres
    REDIS_URL=redis://redis:6379/1
    CELERY_BROKER_URL=amqp://guest:guest@rabbitmq:5672//
    ```
2.  **Inicialização:** Na raiz do projeto, execute:
    ```bash
    docker-compose up --build
    ```
3.  **Setup de Admin:** Com os containers ativos, crie o superusuário em outro terminal:
    ```bash
    docker-compose exec web python manage.py createsuperuser
    ```

### Alternativa B: Execução em Ambiente Local (Manual)
Esta opção é voltada para desenvolvimento direto no host, utilizando SQLite como banco de dados padrão.

1.  **Instalação de Dependências:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # No Windows: .\venv\Scripts\activate
    pip install -r requirements.txt
    ```
2.  **Serviços de Infraestrutura:** Certifique-se de que o **Redis** e o **RabbitMQ** estejam ativos no seu sistema operacional:
    ```bash
    sudo service redis-server start
    sudo service rabbitmq-server start
    ```
3.  **Inicialização do Servidor e Worker:** Em terminais distintos:
    ```bash
    # Terminal 1: Banco e Servidor Web
    cd apps_services/core_service
    python manage.py migrate
    python manage.py runserver

    # Terminal 2: Processamento de Filas (Worker)
    cd apps_services/core_service
    celery -A core_config worker -l info
    ```

---

## Checklist de Requisitos Implementados

- [x] **Persistência Relacional:** Suporte a PostgreSQL (Docker) e SQLite (Local).
- [x] **Comunicação Assíncrona:** Implementada com RabbitMQ e Celery.
- [x] **Segurança:** Validação por IP Institucional e Geofencing.
- [x] **Auditoria:** Histórico de alterações via Simple History.
- [x] **Gestão de Acesso:** Fluxo de aprovação de docentes e privilégios de alunos.

## Autores
- Daniel Rodrigues
- Joana Martins
