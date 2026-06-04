#!/bin/sh

# Se houver um DB_HOST, esperar ele ficar online
if [ "$DB_HOST" = "db" ]
then
    echo "Aguardando o banco de dados PostgreSQL..."
    while ! nc -z $DB_HOST $DB_PORT; do
      sleep 0.1
    done
    echo "PostgreSQL iniciado!"
fi

# Aplicar migrações
echo "Aplicando migrações..."
python manage.py migrate --noinput

# Coletar arquivos estáticos
echo "Coletando arquivos estáticos..."
python manage.py collectstatic --noinput

# Executar o comando passado (geralmente gunicorn ou runserver)
exec "$@"
