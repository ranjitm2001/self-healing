FROM postgres:latest
ENV POSTGRES_DB=mydb
ENV POSTGRES_USER=myuser
ENV POSTGRES_PASSWORD=mypassword


# Write Dockerfile and add FROM, ENV things
# Pull Postgres from repository, to local images | docker pull postgres
# Build local container from that image | docker build -t my_postgres_image .
# Run the image | docker run --name postgres-container -e POSTGRES_PASSWORD=mypassword -d -p 5432:5432 postgres
# Run PSQL | psql -h localhost -p 5432 -U postgres -d postgres
# docker execute -it db-image psql -U postgres


# docker-compose.yml would be like a wrapper around Dockerfile, and it can run directly
# psql -h localhost -p 5432 -d mydb -U myuser | to connect to psql via cli