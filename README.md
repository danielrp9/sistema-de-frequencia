# Sistema Distribuído de Controle de Frequência (QR Code)

Este sistema foi desenvolvido para o trabalho de Sistemas Distribuídos do Prof. Alessandro Vivas Andrade. O objetivo é permitir o registro de presença via QR Code com validação de geolocalização e rede institucional, garantindo que o aluno esteja fisicamente presente e conectado à infraestrutura da universidade.

## 🏗️ Arquitetura
O sistema foi projetado com foco em escalabilidade e disponibilidade, utilizando técnicas modernas de sistemas distribuídos para suportar milhares de acessos simultâneos:

* **Backend:** Django 5.0 + Django REST Framework.
* **Banco de Dados:** PostgreSQL (Persistência de dados segura).
* **Cache/Sessão:** Redis (Validação rápida de tokens e controle de duplicidade).
* **Fila de Eventos:** RabbitMQ + Celery (Processamento assíncrono de registros de presença).
* **Auditoria:** Registro completo de histórico de alterações (quem, o quê e quando) em todos os modelos principais.

## 🚀 Pré-requisitos
Antes de rodar o projeto, certifique-se de ter instalado em seu ambiente Linux:
* Python 3.12+
* PostgreSQL 16+
* Redis Server
* RabbitMQ Server

## 🔧 Instalação e Configuração

1. **Clonar o repositório:**
   ```bash
   git clone https://github.com/danielrp9/sistema_frequencia.git
   cd sistema_frequencia
   ```

2. **Configurar o Ambiente Virtual:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Configurar o Banco de Dados (PostgreSQL):**
   Acesse o terminal `psql` e execute os comandos para criar o banco e ajustar as permissões de schema:
   ```sql
   CREATE DATABASE frequencia_db;
   CREATE USER daniel_admin WITH PASSWORD 'sua_senha_segura';
   GRANT ALL PRIVILEGES ON DATABASE frequencia_db TO daniel_admin;
   
   -- Conectar ao banco e ajustar o schema public para o Django
   \c frequencia_db
   GRANT ALL ON SCHEMA public TO daniel_admin;
   ALTER SCHEMA public OWNER TO daniel_admin;
   ```

4. **Migrações e Superusuário:**
   ```bash
   cd apps_services/core_service
   python manage.py makemigrations
   python manage.py migrate
   python manage.py createsuperuser
   ```

## 🏃 Como Executar

Para garantir o funcionamento da arquitetura distribuída, é necessário rodar os seguintes serviços em terminais separados:

* **Terminal 1 (Aplicação Django):**
    ```bash
    python manage.py runserver
    ```
* **Terminal 2 (Celery Worker - Processamento de Fila):**
    ```bash
    celery -A core_config worker -l info
    ```
* **Serviços de Background:**
    Certifique-se de que o Redis e o RabbitMQ estão ativos:
    ```bash
    sudo systemctl start redis-server
    sudo systemctl start rabbitmq-server
    ```

## 🛠️ Funcionalidades Implementadas (Parte 1)
- [x] Autenticação robusta via `django-allauth`.
- [x] Modelos complexos para Aluno, Professor, Disciplina, Sala e Aula.
- [x] Geração dinâmica de QR Code com token de segurança (UUID).
- [x] Validação de rede institucional (IP/NAT) e geolocalização (raio de 50m).
- [x] Sistema de auditoria para rastreamento de ações de usuários.

