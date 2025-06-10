# Football Data Web Service Project

This project provides access to football (soccer) player and club statistics through a web service. The data is stored in RDF format and served through a GraphDB repository.

## Prerequisites

- [Git](https://git-scm.com/downloads)
- [Docker](https://www.docker.com/get-started)
- [Docker Compose](https://docs.docker.com/compose/install/) (included with Docker Desktop on Windows and Mac)

## How to Run the Project (**WITH DOCKER**)

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/WS-Project-1.git
cd WS-Project-1
```

### 2. Start the Docker Containers

Build and start all the services in detached mode:

```bash
docker compose up --build -d
```

This command will:
- Build the necessary Docker images
- Create and start the containers
- Set up the GraphDB repository with football data
- Make the web service available

The first startup might take some time as it needs to build the images and import the football data.

### 3. Accessing the Services

Once the containers are running, you can access:

- GraphDB interface: [http://localhost:7200](http://localhost:7200)
- Web service: [http://localhost:8000](http://localhost:8000)

### 4. Shutting Down

To stop and remove all containers, networks, and volumes created by `docker compose up`:

```bash
docker compose down -v
```

## How to Run the Project (**WITHOUT DOCKER**)

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/WS-Project-1.git
cd WS-Project-1
```

### 2. Set Up Django App

```bash
cd ws_project_1
python3 -m venv venv
source venv/bin/active
pip install -r requirements
```

Before the next step make sure that **GraphDB** is running on [http://localhost:7200](http://localhost:7200) and **import file** `data/import/football_rdf_data.nt`.

### 3.Import Data and Create Repositories
```bash
bash ./data/config/init-repository.sh ./data/config
```

### 4. Run Django

```bash
GRAPHDB_ENDPOINT=http://locahost:7200 python3 manage.py runserver 0.0.0.0:8000
```

## Project Structure

- `data/`: Contains the RDF data and configuration files
- `ws_project_1/`: Main project code (Django application)
- `docs/`: Documentation files
