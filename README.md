# frog
One of the two server-side components required to retrieve data from the database. 
frog exposes several endpoints to facilitate connecting to the database and handling basic CRUD-level tasks.
In addition, it implements authorisation and user authentication using JWTs and roles. 

## Run Locally
1. download the infrastructure configuration repo and follow the instructions therein
https://github.com/MateuszMiekicki/pond.git
2. installing the necessary packages to run the project
3. `python3 app/src/main.py`

## Related
- [infrastructure](https://github.com/MateuszMiekicki/pond)
- [mqtt server](https://github.com/MateuszMiekicki/toad)

## License
[0BSD license](./LICENSE)
