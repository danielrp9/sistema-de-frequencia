# Sistema de Controle de Frequência UFVJM

Este projeto foi desenvolvido para a disciplina de **Sistemas Distribuídos**, sob a orientação do Prof. Alessandro Vivas Andrade. O sistema propõe uma solução robusta para o controle de presença estudantil, substituindo listas físicas por uma arquitetura distribuída e segura baseada em QR Codes dinâmicos e validações multifatoriais de contexto.

## 1. Arquitetura e Conceitos Distribuídos

O sistema não é apenas um gerenciador de registros, mas uma infraestrutura que implementa conceitos fundamentais de sistemas distribuídos:
*   **Desacoplamento de Serviços:** Através de **Django Signals**, os módulos de usuários, acadêmico e presença comunicam-se de forma assíncrona.
*   **Processamento de Background:** O registro de presença e os cálculos de infrequência são processados via **Celery** e **RabbitMQ**, garantindo que a resposta ao usuário seja imediata enquanto as operações pesadas ocorrem em paralelo.
*   **Consistência e Concorrência:** O uso do **Redis** como *Distributed Lock Manager* impede que falhas de rede ou requisições duplicadas gerem inconsistências no banco de dados.

---

## 2. Fluxo Estrutural e Regras de Negócio

A maturidade do sistema reflete-se na sua lógica de governança e segurança, dividida em fases claras:

### A. Construção da Base (Responsabilidade do Super Admin)
O sistema não funciona de forma isolada; ele exige uma base de dados geográfica e institucional sólida:
*   O **Administrador** deve mapear toda a universidade no sistema, cadastrando **Departamentos, Cursos e Disciplinas**.
*   **Geolocalização das Salas:** Cada sala de aula é cadastrada com suas coordenadas de latitude e longitude exatas, além de um raio de tolerância (geofencing). Isso facilita o trabalho do professor, que apenas seleciona uma sala já mapeada para abrir sua aula.
*   **Gestão de Cargas Horárias:** O Admin define a carga horária total de cada disciplina. Esta informação é a base para o cálculo automático do limite de 25% de faltas permitido pelo regulamento acadêmico.

### B. Ciclo de Vida dos Usuários e Segurança de Acesso
*   **Professores:** Podem realizar o cadastro por conta própria, mas o acesso é **bloqueado por padrão**. Para evitar que qualquer usuário assuma privilégios docentes indevidamente, a ativação das funcionalidades de professor exige **aprovação manual do Admin**.
*   **Alunos:** Podem se cadastrar livremente, porém, enquanto não forem vinculados a uma disciplina por um professor, permanecem como "usuários sem funcionalidades", garantindo que o sistema não seja usado de forma indevida ou para consultas de dados aos quais o aluno ainda não possui direito.

### C. Validação Multifatorial de Presença
O sistema impõe barreiras rigorosas para garantir que o aluno esteja, de fato, em sala:
*   **Identificação de IP de Rede:** O registro de presença só é concluído se o dispositivo do aluno estiver conectado à **rede institucional da universidade**. Tentativas de registro via redes externas (casa, 4G/5G) são sumariamente barradas.
*   **Geofencing (GPS):** Mesmo na rede correta, o sistema verifica a geolocalização. Se o aluno não estiver posicionado dentro do raio geográfico da sala onde a aula ocorre, o backend bloqueia a conclusão da presença.
*   **QR Code Dinâmico:** O token do QR Code é rotativo (UUID), impedindo que o aluno registre presença usando fotos ou capturas de tela enviadas por colegas fora do ambiente.

### D. Automação de Infrequência e Monitoramento
Seguindo o regulamento institucional, o sistema realiza o cálculo automático de frequência:
*   A partir da **Carga Horária Total** cadastrada pelo Admin, o sistema monitora cada hora-aula registrada.
*   Ao atingir o limite crítico (próximo aos 25% de faltas permitidas), o sistema gera informações e alertas tanto para o aluno quanto para o professor. Essa automação garante consistência acadêmica e evita erros manuais no fechamento de diários.

---

## 3. Guia de Execução (Docker)

Esta configuração permite que o sistema rode em qualquer ambiente Linux/Windows/Mac com Docker instalado, configurando automaticamente o PostgreSQL, Redis e RabbitMQ.

### 1. Preparação das Variáveis de Ambiente
Por segurança, as credenciais não são enviadas pelo Git. Crie o arquivo `.env` em `apps_services/core_service/.env`:

```env
# Django Config
DJANGO_SECRET_KEY='sua-chave-secreta-aqui'
DJANGO_DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (PostgreSQL no Docker)
DB_NAME=frequencia_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432

# Redis & RabbitMQ
REDIS_URL=redis://redis:6379/1
CELERY_BROKER_URL=amqp://guest:guest@rabbitmq:5672//

# Outras Configurações
PRESENCA_DUPLICATE_LOCK_TIMEOUT=60
```

### 2. Inicialização do Ambiente
```bash
docker-compose up --build
```
Após o build, o sistema estará disponível em `http://localhost:8000`.

### 3. Setup do Administrador
```bash
docker-compose exec web python manage.py createsuperuser
```

---

## Checklist de Requisitos (Sistemas Distribuídos)

- [x] **Persistência Distribuída:** PostgreSQL com auditoria via Simple History.
- [x] **Mensageria e Filas:** Implementada com RabbitMQ e Celery.
- [x] **Coordenação de Recursos:** Lock distribuído via Redis para evitar race conditions.
- [x] **Filtros de Camada:** Validação por IP Institucional e Geofencing de precisão.
- [x] **Segurança de Acesso:** Fluxo de aprovação administrativa de docentes.

## Autores
- Daniel Rodrigues
- Joana Martins
