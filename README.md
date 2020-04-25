# Chotube
Trabajo practico Taller 2


## Build image docker
```
docker-compose build
```

## Run the container:
```
docker-compose up -d
```

## Remove conteiner:
```
docker-compose down -v
```


## Create the table:
```
docker-compose exec web python server.py create_db
```

## Ensure the videos table was created:
```
docker-compose exec db psql --username=hello_flask --dbname=hello_flask_dev
\c hello_flask_dev
\dt
```
