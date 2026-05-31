# Sistema de Controle de Frequência UFVJM

Projeto desenvolvido para a disciplina de **Sistemas Distribuídos**, sob orientação do Prof. Alessandro Vivas Andrade.

O sistema automatiza o controle de presença de alunos por meio de QR Code dinâmico, autenticação, validação de horário, geolocalização, IP institucional, cache distribuído, fila assíncrona e auditoria de alterações.

## Visão Geral

O fluxo principal funciona assim:

1. O professor abre uma aula.
2. O sistema gera um QR Code dinâmico com `aula_id` e token UUID.
3. O aluno escaneia o QR Code pela interface web.
4. O frontend envia a chamada para a API REST de presença.
5. O backend valida usuário, turma, horário, token, IP, geolocalização e duplicidade.
6. O Redis cria um lock temporário para evitar registros duplicados.
7. A presença validada é enviada para a fila Celery/RabbitMQ.
8. A task assíncrona cria o registro de presença no banco.
9. O dashboard e os relatórios exibem os dados consolidados.
10. Alterações importantes ficam registradas via `django-simple-history`.

## Tecnologias

- Python
- Django
- Django REST Framework
- Django Allauth
- Django Simple History
- Redis
- Celery
- RabbitMQ
- SQLite em desenvolvimento
- Chart.js
- Tailwind CSS via templates
- HTML5 QR Code scanner

## Estrutura do Projeto

```text
sistema-de-frequencia/
├── apps_services/
│   └── core_service/
│       ├── academic/           # Departamentos, cursos, disciplinas, salas e turmas
│       ├── classes/            # Aulas, QR Code e relatórios
│       ├── presence_service/   # Validação, API e processamento de presença
│       ├── users/              # Usuários, alunos, professores e dashboard
│       ├── core_config/        # Settings, rotas e Celery
│       ├── templates/          # Interface web
│       └── manage.py
├── requirements.txt
└── README.md
```

## Funcionalidades Implementadas

### Autenticação e Perfis

- Login e logout.
- Usuário customizado.
- Perfis de administrador, professor e aluno.
- Criação automática de perfil de aluno/professor por signal.
- Controle de acesso por tipo de usuário.

### Gestão Acadêmica

- Cadastro de departamentos.
- Cadastro de cursos.
- Cadastro de disciplinas.
- Cadastro de salas com latitude, longitude e raio permitido.
- Cadastro de turmas.
- Matrícula de alunos em turmas.

### Aulas e QR Code

- Professor pode abrir aula para uma turma e sala.
- QR Code dinâmico com token UUID.
- Atualização periódica do token.
- Encerramento manual de aula.
- Validação de aula ativa por horário.

### Registro de Presença

- Registro via scanner de QR Code no frontend.
- Endpoint REST autenticado para presença.
- Validação de aluno autenticado.
- Validação de matrícula na turma.
- Validação de token do QR Code.
- Validação de horário da aula.
- Validação de IP institucional.
- Validação de geolocalização pelo raio da sala.
- Bloqueio de duplicidade por banco e por cache.
- Status da presença (`VALIDA` ou `INVALIDA`).

### Redis

- Redis configurado como cache padrão fora do ambiente de testes.
- Uso real no lock de presença duplicada.
- Chaves com prefixo `frequencia`.
- Timeout de conexão configurado para evitar travamento quando o serviço está indisponível.
- Testes usam cache local automaticamente para não depender de Redis.

### Celery e RabbitMQ

- Celery configurado no projeto.
- RabbitMQ configurado como broker.
- Presença não é mais criada diretamente na view.
- API valida e enfileira o processamento.
- Task Celery cria a presença de forma assíncrona.
- Retry automático na task.
- Resposta da API usa `202 Accepted` quando a presença é enfileirada.
- Erro `FILA_INDISPONIVEL` quando o broker não está acessível.
- Testes usam `CELERY_TASK_ALWAYS_EAGER` para executar task sem precisar do RabbitMQ.

### Dashboard e Relatórios

- Dashboard por tipo de usuário.
- Gráficos com Chart.js.
- Visão de presença por turma.
- Resumo geral de presenças e faltas.
- Frequência por disciplina para aluno.
- Relatório completo por turma/disciplina.
- Exportação visual do relatório via impressão/PDF.
- Monitoramento de Redis, Celery/RabbitMQ e banco no dashboard administrativo.

### Auditoria e Histórico

Auditoria via `django-simple-history` nos principais modelos:

- Usuário.
- Aluno.
- Professor.
- Departamento.
- Curso.
- Disciplina.
- Sala.
- Turma.
- Matrículas de alunos em turma.
- Aula.
- Presença.

Os modelos auditados usam `SimpleHistoryAdmin`, permitindo consultar o histórico pelo Django Admin.

## Como Executar

### 1. Criar e ativar ambiente virtual

No Windows PowerShell:

```powershell
cd D:\Projetos\Vivas\sistema-de-frequencia
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

No Linux/WSL:

```bash
cd /caminho/para/sistema-de-frequencia
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configurar variáveis de ambiente

Crie um arquivo `.env` em:

```text
apps_services/core_service/.env
```

Exemplo:

```env
DJANGO_SECRET_KEY=dev
DJANGO_DEBUG=True
DJANGO_USE_REDIS_CACHE=True
REDIS_URL=redis://127.0.0.1:6379/1
CELERY_BROKER_URL=pyamqp://guest@localhost//
PRESENCA_DUPLICATE_LOCK_TIMEOUT=60
```

### 3. Subir Redis e RabbitMQ

No WSL/Linux:

```bash
sudo service redis-server start
sudo service rabbitmq-server start
```

Para conferir no Windows PowerShell:

```powershell
Test-NetConnection 127.0.0.1 -Port 6379
Test-NetConnection 127.0.0.1 -Port 5672
```

Os dois devem retornar `TcpTestSucceeded: True`.

### 4. Aplicar migrations

```powershell
cd apps_services\core_service
python manage.py migrate
```

### 5. Criar superusuário

```powershell
python manage.py createsuperuser
```

### 6. Subir o servidor Django

```powershell
python manage.py runserver
```

Acesse:

```text
http://127.0.0.1:8000/
```

### 7. Subir o worker Celery

Em outro terminal, com o ambiente virtual ativo e dentro de `apps_services/core_service`:

```powershell
celery -A core_config worker -l info --pool=solo
```

No Windows, o `--pool=solo` evita problemas de execução do Celery.

## Como Testar o Fluxo Principal

1. Entre como administrador ou professor.
2. Cadastre/valide salas, disciplinas, turmas e alunos.
3. Matricule alunos na turma.
4. Como professor, abra uma aula.
5. Projete o QR Code da aula.
6. Como aluno, acesse o scanner de presença.
7. Escaneie o QR Code.
8. Permita o uso de localização no navegador.
9. Verifique o retorno da presença.
10. Confira o dashboard e o relatório da disciplina.

Observação: câmera e geolocalização funcionam melhor em `localhost` ou HTTPS. Para testar em celular acessando o IP da máquina, o navegador pode bloquear câmera/localização em HTTP. Nesse caso, use HTTPS ou uma ferramenta como ngrok.

## Comandos de Verificação

```powershell
python manage.py check
python manage.py test
```

Status atual dos testes:

```text
4 testes executados com sucesso.
```

Observação: existe um warning conhecido do Allauth sobre `ACCOUNT_EMAIL_REQUIRED`, mas ele não impede a execução.

## Checklist do Trabalho

### API e Frontend

- [x] Endpoint REST para presença.
- [x] Consumo da API pelo scanner no frontend.
- [x] Respostas JSON padronizadas.
- [x] Interface web funcional.

### Regras de Presença

- [x] Autenticação.
- [x] Validação de horário.
- [x] Validação de token QR.
- [x] Validação de matrícula na turma.
- [x] Validação de IP institucional.
- [x] Validação de geolocalização.
- [x] Bloqueio de duplicidade.

### Redis

- [x] Configuração via `REDIS_URL`.
- [x] Uso real como cache.
- [x] Lock de duplicidade de presença.
- [x] Monitoramento no dashboard.

### Fila

- [x] Celery configurado.
- [x] RabbitMQ configurado como broker.
- [x] Task de processamento de presença.
- [x] Presença criada pela task, não pela view.
- [x] Retry automático.
- [x] Tratamento de fila indisponível.
- [x] Monitoramento de worker no dashboard.

### Relatórios e Dashboard

- [x] Relatório por disciplina/turma.
- [x] Gráficos com Chart.js.
- [x] Dashboard por perfil.
- [x] Monitoramento de infraestrutura.

### Auditoria

- [x] `simple_history` configurado.
- [x] Histórico em usuários e perfis.
- [x] Histórico em entidades acadêmicas.
- [x] Histórico em turmas e matrículas.
- [x] Histórico em aulas.
- [x] Histórico em presenças.
- [x] Consulta via Django Admin.

## Limitações Conhecidas

- O projeto ainda está em arquitetura monolítica, embora organizado em apps.
- O banco padrão de desenvolvimento é SQLite.
- RabbitMQ e Redis precisam estar rodando para testar o fluxo distribuído real.
- Em Windows, recomenda-se Celery com `--pool=solo`.
- Não há JWT; a autenticação atual usa sessão Django.

## Autores

- Daniel Rodrigues
- Joana Martins
