# Sistema de Controle de Frequência UFVJM (Etapa 1)

Projeto desenvolvido para a disciplina de **Sistemas Distribuídos**, sob orientação do Prof. Alessandro Vivas Andrade.

O sistema realiza o controle de presença de alunos utilizando QR Code dinâmico, com validações de autenticação, horário, geolocalização e rede institucional.

---

## Descrição do Projeto

O sistema automatiza o processo de chamada acadêmica, garantindo que o registro de presença ocorra apenas quando o aluno:

* esteja autenticado no sistema
* esteja dentro do horário da aula
* esteja fisicamente próximo da sala (geolocalização)
* esteja conectado à rede institucional (IP)

A arquitetura foi planejada para evoluir para um modelo distribuído, com uso de cache, filas e separação de serviços.

---

## Estrutura de Diretórios e Arquitetura

```text
sistema_frequencia/
├── apps_services/
│   └── core_service/
│       ├── academic/           # Cursos, disciplinas e salas
│       ├── classes/            # Aulas e QR Code
│       ├── presence_service/   # Registro de presença
│       ├── users/              # Usuários e autenticação
│       ├── core_config/        # Configurações do Django
│       ├── templates/          # Interface (HTML/Tailwind)
│       ├── .env
│       ├── db.sqlite3
│       └── manage.py
├── requirements.txt
└── README.md
```

### Tecnologias Utilizadas

* Django + Allauth
* Django REST Framework (parcial)
* SQLite (Etapa 1)
* Redis (configurado)
* Celery + RabbitMQ (configurado)
* Tailwind CSS
* Resend API

---

## Instalação e Execução

### 1. Ambiente

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

### 2. Variáveis de ambiente

Criar `.env` em:

```bash
apps_services/core_service/
```

```env
DJANGO_SECRET_KEY=dev
DJANGO_DEBUG=True

# Configuração de email (Resend)
RESEND_API_KEY=
DEFAULT_FROM_EMAIL=onboarding@resend.dev
```

---

### Observação importante (envio de e-mail)

Para o funcionamento completo do sistema, especialmente a funcionalidade de recuperação de senha, é necessário configurar o serviço de e-mail utilizando a plataforma Resend.

Passos:

1. Criar uma conta gratuita em https://resend.com
2. Gerar uma API Key no painel da plataforma
3. Inserir a chave no campo:

```env
RESEND_API_KEY=seu_token_aqui
```

Comportamento sem configuração:

* O sistema continuará funcionando normalmente para login e uso geral
* A recuperação de senha não funcionará
* E-mails não serão enviados

Dependência com Celery:

O envio de e-mails é processado de forma assíncrona.

Para que funcione corretamente, é necessário executar o worker do Celery:

```bash
celery -A core_config worker -l info
```

Caso o Celery não esteja em execução:

* As requisições de envio de e-mail não serão processadas
* O usuário não receberá mensagens de recuperação de senha

---

### 3. Banco de dados

```bash
cd apps_services/core_service
python manage.py migrate
python manage.py createsuperuser
```

---

### 4. Execução

```bash
python manage.py runserver
```

Opcional (assíncrono):

```bash
celery -A core_config worker -l info
```

---

## Status do Projeto (Checklist Detalhado)

### Autenticação e Usuários

* [x] Login e logout
* [x] Criptografia de senha (Django)
* [x] Políticas de senha seguras
* [x] Controle de permissões (Admin, Professor, Aluno)
* [x] Recuperação de senha via email
* [ ] Auditoria completa de ações de usuário (apenas models atualmente)

---

### Modelos de Dados

* [x] Aluno
* [x] Professor
* [x] Disciplina
* [x] Sala (com latitude/longitude e raio)
* [x] Aula (com token QR)
* [ ] Campo `status` em Presença (necessário para regras completas)

---

### QR Code

* [x] Geração de QR Code por aula
* [x] Token único (UUID)
* [x] Link com identificador + token
* [x] Atualização dinâmica

---

### Registro de Presença

* [x] Validação de usuário autenticado
* [x] Validação de horário da aula
* [x] Prevenção de presença duplicada

#### Validações parciais

* [ ] Bloqueio por IP institucional (apenas verificação, não bloqueia)
* [ ] Bloqueio por geolocalização (cálculo existe, mas não impede registro)

---

### CRUD

* [x] CRUD via Django Admin (todos os modelos)
* [x] CRUD via views HTML
* [ ] CRUD completo via API REST

---

### API REST

* [x] Django REST Framework instalado
* [x] Serializers criados
* [ ] Endpoints públicos
* [ ] Endpoints autenticados
* [ ] Autenticação via token/JWT

---

### Infraestrutura Distribuída

#### Redis

* [x] Configurado
* [ ] Uso real para cache
* [ ] Controle de presença duplicada via cache

#### Celery + RabbitMQ

* [x] Configurado
* [x] Estrutura de task criada
* [ ] Uso efetivo no fluxo de presença
* [ ] Retry automático
* [ ] Processamento assíncrono completo

---

### Arquitetura

* [x] Separação lógica em apps (academic, users, presence, etc.)
* [ ] Microserviços reais (atualmente monolito)
* [ ] Comunicação entre serviços

---

### Dashboard

* [x] Dados de frequência disponíveis
* [ ] Gráficos (Chart.js ou similar)
* [ ] Interface analítica completa

---

### Frontend

* [x] Templates Django (HTML + Tailwind)
* [x] Interface funcional
* [ ] SPA (React/Vue)
* [ ] Consumo via API REST

---

### Banco de Dados

* [x] SQLite funcional
* [ ] PostgreSQL (requisito do projeto)

---

### Segurança

* [x] Autenticação básica segura
* [ ] Rate limiting
* [ ] 2FA
* [ ] Configuração segura de produção
* [ ] Validações obrigatórias (IP + geolocalização)

---

## Organização por Etapas

### Etapa 1 (Entrega Atual)

* [x] Autenticação completa
* [x] Modelagem do sistema acadêmico
* [x] CRUD administrativo
* [x] Geração de QR Code
* [x] Registro básico de presença
* [x] Estrutura inicial para sistemas distribuídos
* [x] Configuração de Redis e Celery

---

### Etapa 2 (Pendências do Projeto)

* [ ] API REST completa
* [ ] Validações obrigatórias (IP + geolocalização)
* [ ] Uso real de Redis
* [ ] Processamento assíncrono com Celery
* [ ] Dashboard com gráficos
* [ ] Migração para PostgreSQL

---

## Observações Importantes

* O sistema funciona em ambiente local com SQLite
* Redis e RabbitMQ estão configurados, mas não são obrigatórios para execução
* Algumas validações estão implementadas, porém ainda não são obrigatórias
* O sistema ainda não está totalmente desacoplado em microserviços

---

## Conclusão

O projeto apresenta uma base sólida e funcional, com autenticação, modelagem acadêmica e geração de QR Code operando corretamente.

A arquitetura já está preparada para evolução para um sistema distribuído completo, sendo necessárias implementações adicionais para atender integralmente aos requisitos avançados do projeto.

---

## Desenvolvimento

Daniel Rodrigues
Joana Martins


