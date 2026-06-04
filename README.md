# Sistema de Controle de Frequência UFVJM

Este projeto foi desenvolvido para a disciplina de **Sistemas Distribuídos**, sob orientação do Prof. Alessandro Vivas Andrade. A ideia do sistema é resolver o problema das listas de presença físicas usando uma estrutura moderna com QR Codes dinâmicos e validações automáticas de segurança.

## Como o sistema funciona (Lógica Distribuída)

Para garantir que o sistema seja confiável e aguente o uso real, aplicamos alguns conceitos fundamentais:
*   **Tarefas em segundo plano:** O registro de presença e os cálculos de faltas não travam o site. Usamos **Celery** e **RabbitMQ** para processar tudo isso por fora, deixando a resposta pro usuário bem rápida.
*   **Organização por Sinais:** Os módulos do sistema (alunos, professores, presença) conversam entre si de forma organizada através de **Signals**, o que facilita muito a manutenção.
*   **Controle de Concorrência:** Usamos o **Redis** para garantir que uma presença não seja registrada duas vezes por erro de rede ou cliques repetidos.

---

## Regras do Sistema e Fluxo de Uso

O sistema foi pensado com uma lógica de segurança em camadas para que ninguém consiga "burlar" a presença.

### 1. Configuração da Base (Admin)
Antes de tudo, o **Administrador** precisa preparar o terreno:
*   É necessário cadastrar os Departamentos, Cursos e as Disciplinas.
*   **Mapeamento das Salas:** Cada sala de aula deve ser cadastrada com sua geolocalização exata (latitude/longitude) e um raio de tolerância. Assim, o professor só precisa escolher a sala na hora de abrir a aula, sem precisar configurar nada manualmente.
*   **Cargas Horárias:** O Admin define o total de horas de cada disciplina. O sistema usa isso para calcular automaticamente o limite de 25% de faltas permitido, avisando o aluno e o professor quando a situação ficar crítica.

### 2. Controle de Acesso e Perfis
*   **Professores:** Podem se cadastrar, mas ficam **bloqueados** até que o Administrador aprove o acesso. Isso evita que qualquer pessoa se passe por docente.
*   **Alunos:** O cadastro é livre, mas o aluno não tem acesso a nada enquanto não for matriculado em uma turma por um professor.

### 3. Validações para a Presença
Para que o aluno consiga registrar a presença, ele precisa passar por três barreiras:
*   **Rede da Universidade:** O sistema identifica o IP e só aceita o registro se o aluno estiver conectado no Wi-Fi/Rede institucional.
*   **Localização (GPS):** O sistema verifica se o aluno está realmente dentro da sala de aula (baseado na geolocalização cadastrada pelo Admin). Se estiver fora do raio, a presença é barrada.
*   **QR Code Dinâmico:** O código gerado pelo professor muda sozinho de tempos em tempos. Se alguém tirar foto e mandar pra um colega fora da sala, o código já terá expirado.

---

## Como rodar o projeto (Docker)

A forma mais fácil de executar o sistema é usando o Docker, que já configura o Banco de Dados (Postgres), o Redis e o RabbitMQ sozinho.

### 1. Configurando o arquivo .env
Para o sistema funcionar corretamente, você **deve** criar um arquivo chamado `.env` dentro da pasta `apps_services/core_service/`. Use o formato abaixo para que as conexões funcionem de primeira:

```env
# Configurações do Django
DJANGO_SECRET_KEY='sua-chave-secreta-aqui'
DJANGO_DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Banco de Dados (PostgreSQL no Docker)
DB_NAME=frequencia_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432

# Redis & RabbitMQ
REDIS_URL=redis://redis:6379/1
CELERY_BROKER_URL=amqp://guest:guest@rabbitmq:5672//

# Outros ajustes
PRESENCA_DUPLICATE_LOCK_TIMEOUT=60
```

### 2. Subindo os containers
Com o Docker instalado, abra o terminal na raiz do projeto e rode:
```bash
docker-compose up --build
```
Depois que terminar de carregar, o sistema estará pronto em `http://localhost:8000`.

### 3. Criando o acesso de Administrador
Com os containers ligados, abra outro terminal e execute:
```bash
docker-compose exec web python manage.py createsuperuser
```

---

## Checklist do que foi feito

- [x] **Banco de Dados:** PostgreSQL com histórico de auditoria.
- [x] **Mensageria:** RabbitMQ e Celery para tarefas assíncronas.
- [x] **Segurança:** Bloqueio por IP Institucional e Geolocalização.
- [x] **Controle:** Lock no Redis para evitar duplicidade.
- [x] **Gestão:** Fluxo de aprovação de professores e vínculo de alunos.

## Autores
- Daniel Rodrigues
- Joana Martins
