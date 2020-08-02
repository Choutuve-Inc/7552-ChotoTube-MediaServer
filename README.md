# Chotube
Trabajo practico Taller 2

Para levantar los conenedores con el servidor y la base de datos ejecute los siguientes comandos

## Build image docker
```
docker-compose build
```

## first run db:
```
docker-compose up -d db
```

## Second run the service
```
docker-compose up -d web
```

## Remove conteiner:
```
docker-compose down
```
add the -v flag to remove all volumes too

## Ensure the videos table was created:
```
docker-compose exec db psql --username=hello_flask --dbname=hello_flask_dev
\c hello_flask_dev
\dt
```

## Para ejecutar los test
```
coverage run -m unittest discover
```


## Para el % de coverage
```
coverage report -m
```
Para el coberage configure en el archivo .coveragerc que ingnore los site-packages

##Nota
Cuando queria ejecutar los test me tiraba error de que no detectaba los paquetes.
Como no supe resolverlo puse todo el codigo en un solo archivo, se encuentra todo en el init . Por favor disculpeme la desprolijidad.