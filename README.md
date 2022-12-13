[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

# Graph4Med 

Graph4Med is an open-source tool for visualizing and analysis of a cohort of patients.

You can try a [live demo](http://graph4med.cs.uni-frankfurt.de/demo) (no password required).

For more information visit the [project homepage](http://graph4med.cs.uni-frankfurt.de) 
or read the full paper:

[Schäfer, J., Tang, M., Luu, D. et al. Graph4Med: a web application and a graph database for visualizing and analyzing medical databases. BMC Bioinformatics 23, 537 (2022).](https://rdcu.be/c1uKv) [(https://doi.org/10.1186/s12859-022-05092-0)](https://doi.org/10.1186/s12859-022-05092-0)

## Prerequisites

Graph4Med has been tested with the following versions (others might work as well):
- Python 3.6+
- [Neo4j 4.4.4](https://neo4j.com/release-notes/database/)
  - [Neo4j APOC Library 4.4.0.3](https://neo4j.com/labs/apoc/)
  - [Neo4j Graph Data Science (GDS) Library 1.8.4](https://neo4j.com/download-center/)
- [NeoDash 2.0.13](https://github.com/nielsdejong/neodash)

## Running Graph4Med

Install/setup a [Neo4j](https://neo4j.com/download-center/) instance with default database `neo4j`. 
Make sure to install the APOC and GDS plugins matching your Neo4j version and configure a
[bolt connector](https://neo4j.com/docs/operations-manual/current/configuration/connectors/).

Clone this repository:

    git clone https://github.com/jeschaef/Graph4Med.git

Change into project folder and install requirements:

    pip install -r requirements.txt

Configure the environment variables in the [`.env`](.env) file according to your setup:

    NEO4J_SERVER="localhost:7687"
    NEO4J_USER="myusername"
    NEO4J_PASSWORD="mypassword"

If you want to populate the Neo4j database with the sample data from this repository, 
you can execute the [`demo.py`](demo.py) script:

    python demo.py

Run [NeoDash](https://github.com/nielsdejong/neodash) and connect to your Neo4j database instance.
If you populated the database with [`demo.py`](demo.py) script, there will already be one
NeoDash dashboard stored in the default database. Otherwise you can load the 
[dashboard](res/dashboard.json) file from this repository.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE).
