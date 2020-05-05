# Chotube
Trabajo practico Taller 2


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
