# self-healing

## Commands

* Virtual environment
  * `python3 -m venv venv`
  * `source venv/bin/activate`
  * `pip install -r requirements.txt`
  * If new packages are added,
    * `pip freeze > requirements.txt`
* Postgres Up and Running
  * If docker-compose.yaml is to be used,
    * `docker-compose up`
    * `psql -h localhost -p 5432 -d mydb -U myuser`
  * If Dockerfile is to be used,
    * `docker pull postgres`
    * `docker build -t my_postgres_image .`
    * `docker run --name postgres-container -e POSTGRES_PASSWORD=mypassword -d -p 5432:5432 postgres`
    * `psql -h localhost -p 5432 -U postgres -d postgres`
    * `docker execute -it db-image psql -U postgres`
* Run
  * To run the main automation,
    * `python3 main.py`
  * To update the maintenance_mode,
    * `python3 maintanenace_update.py`