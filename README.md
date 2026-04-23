# Sistema de Controle de Frequência UFVJM (Etapa 1)

Este projeto consiste em uma solução para o registro de presença de discentes mediante o uso de QR Codes dinâmicos, desenvolvida para a disciplina de **Sistemas Distribuídos**, sob orientação do Prof. Alessandro Vivas Andrade. O sistema foca na integridade do registro através de validações de geolocalização e infraestrutura de rede institucional.

## Descrição do Projeto
O sistema automatiza o processo de chamada acadêmica. A arquitetura foi planejada para garantir que o registro de presença ocorra apenas quando o discente preencher requisitos fundamentais: autenticação em conta institucional, presença física no raio da sala de aula (via GPS) e conexão à rede da universidade (via IP).

Nesta **Etapa 1**, o trabalho concentra-se na fundação do sistema: gestão de identidades, modelagem do domínio acadêmico e estruturação da comunicação assíncrona.

---

## Estrutura de Diretórios e Arquitetura
O projeto adota uma estrutura organizada em serviços para facilitar a futura transição para microserviços independentes:

```text
sistema_frequencia/
├── apps_services/              # Diretório de serviços da aplicação
│   └── core_service/           # Serviço central 
│       ├── academic/           # Gestão de Cursos, Disciplinas e Salas
│       ├── classes/            # Gestão de Aulas e Frequência
│       ├── users/              # CustomUser e Perfis (Professor/Aluno)
│       ├── core_config/        # Configurações globais do Django (settings/urls)
│       ├── templates/          # Interface visual (HTML/Tailwind)
│       ├── .env                # Variáveis de ambiente e chaves de API
│       ├── db.sqlite3          # Base de dados local (Etapa 1)
│       └── manage.py           # Utilitário de gerenciamento do Django
├── venv/                       # Ambiente virtual (isolamento de dependências)
├── LICENSE                     # Licença do projeto
├── .gitignore                  # Definição de arquivos ignorados pelo Git
├── README.md                   # Documentação do projeto
└── requirements.txt            # Lista de dependências do sistema
```

### Tecnologias Utilizadas:
* **Django + Allauth:** Gestão de autenticação e segurança de contas conforme requisito do projeto.
* **Redis:** Camada de cache e gerenciamento de sessões, garantindo performance na validação de tokens.
* **Celery & RabbitMQ:** Processamento de tarefas em segundo plano (background tasks) para envio de e-mails transacionais.
* **Resend API:** Entrega real de e-mails de recuperação de senha.
* **SQLite:** Mantido nesta fase para simplificar a portabilidade. A migração para **PostgreSQL** está prevista para a Etapa 2.

---

## Instalação e Execução

### 1. Preparação do Ambiente
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configuração de Serviços de Infraestrutura
É necessário que os servidores Redis e RabbitMQ estejam ativos no ambiente Linux:
```bash
sudo service redis-server start
sudo service rabbitmq-server start
```

### 3. Configuração de Variáveis de Ambiente
Criar um arquivo `.env` no diretório `apps_services/core_service/` com o seguinte conteúdo:
```text
DJANGO_SECRET_KEY='sua_chave_secreta'
DJANGO_DEBUG=True
RESEND_API_KEY='re_seu_token'
DEFAULT_FROM_EMAIL='onboarding@resend.dev'
```

> **OBSERVAÇÃO IMPORTANTE (Configuração de E-mail):**
> Para o funcionamento do fluxo de recuperação de senha, é indispensável a utilização do serviço **Resend**.
> 1. Deve-se criar uma conta gratuita em [resend.com](https://resend.com).
> 2. O token gerado deve ser inserido na variável `RESEND_API_KEY` no arquivo `.env`.
> 3. Sem esta configuração e sem a execução do **Celery** (Terminal 2), o sistema não processará o envio de mensagens de segurança.

### 4. Migrações e Superusuário
```bash
python3 manage.py makemigrations
python3 manage.py migrate
python3 manage.py createsuperuser
```

---

## Execução do Sistema
Utilizar dois terminais distintos para garantir a operação distribuída:

* **Terminal 1 (Servidor de Aplicação):** `python3 manage.py runserver`
* **Terminal 2 (Processamento Assíncrono):** `celery -A core_config worker -l info`

---

## Cronograma e Funcionalidades

### **1ª Etapa (Concluída - Entrega Atual)**
- [x] **Autenticação (Django-Allauth):** Login, logout, criptografia de senhas e recuperação via e-mail.
- [x] **CRUDs de Administração:** Cadastro estruturado de usuários (Admin/Professor/Aluno), Departamentos, Cursos e Disciplinas.
- [x] **Infraestrutura Física:** Cadastro de Salas com suporte a geolocalização e raio permitido (50m).
- [x] **Validação de Rede:** Lógica inicial para identificação de IP/NAT institucional.
- [x] **Histórico de Alterações:** Auditoria completa registrando quem, o quê e quando houve modificações (`django-simple-history`).
- [x] **Interface Base:** Estrutura responsiva utilizando Tailwind CSS.

### **2ª Etapa (Planejamento - Requisitos do PDF)**
- [ ] **Banco de Dados de Produção:** Migração completa para PostgreSQL.
- [ ] **Geração de QR Code Dinâmico:** Implementação de tokens UUID únicos por aula para evitar compartilhamento indevido.
- [ ] **Lógica de Presença com Redis:** Uso de cache para controle de duplicidade e validação rápida de tokens.
- [ ] **Fila de Eventos (Celery/RabbitMQ):** Processamento assíncrono do registro de presença para garantir escalabilidade.
- [ ] **Dashboard e Relatórios:** Criação de interface para visualização de estatísticas de frequência por disciplina e aluno.

---