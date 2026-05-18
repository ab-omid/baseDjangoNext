run notebook execute this command

`env DJANGO_ALLOW_ASYNC_UNSAFE=true ./manage.py shell_plus --notebook`

run celery:
 
`env DJANGO_ALLOW_ASYNC_UNSAFE=true python -m celery --app=PDNR.celery.celery worker --loglevel=info  --logfile=/home/omid/www/html/pdnr/storage/logs/app.log --max-memory-per-child=10000 --without-gossip --without-mingle --without-heartbeat -E -B`

run flower:

`env CELERY_BROKER_URL=redis://127.0.0.1:6379/0 celery flower --port=5555 --address='localhost'`