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

### 1. Extract the zip file

After downloading the project, extract the zip file and navigate to the project directory `Project-2`.

### 2. Set Up Django App

```bash
cd ws_project_1
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Before the next step make sure that **GraphDB** is running on [http://localhost:7200](http://localhost:7200).

### 3.Import Data and Create Repositories

First you need to create a GraphDB repository for the football data. **IMPORTANT**: The repository name must be `football`.

After creating a repository in GraphDB, you need to import the RDF data.
- File `data/import/football_rdf_data.nt` contains the football data in RDF format.
- File `data/import/ontology/football_ontology.n3` contains the ontology configuration for the football data.

### 4. Run Django

```bash
GRAPHDB_ENDPOINT=http://localhost:7200 python3 manage.py runserver
```
The variable `GRAPHDB_ENDPOINT` should point to your GraphDB instance. So, if you are not running GraphDB on the default port, you need to change it accordingly.

## Project Structure

- `data/`: Contains the RDF data and configuration files
- `ws_project_1/`: Main project code (Django application)
- `docs/`: Documentation files

### 5. Other Tests

In order to import both the data and the ontology into Protégé, there is a file, `data/import/football_rdf_data_ontology.n3`, that serves that same purpose.

The SPIN rules used for this project are located in:
- `data/import/ontology/football_spin_rules.n3`

In order to see how they are applied, it is possible to do so in the following files:
- `ws_project_1/app/utils/spin_client.py`
- `ws_project_1/app/utils/spin_queries.py`

_Note: the name of the folder is 'ws\_project\_1' because both projects are available on GitHub and the second is a fork of the first._

### 6. Possible Errors
In some pages, messages like _Some additional information could not be loaded from external sources_ may appear, due to errors fetching data from Wikidata. If that happens, refresh the page (this is not a coding issue from our part, it's a problem with wikidata and their API ).
