# warbler
twitter clone

To get this application running, do the following in the Terminal:

1. `python3 -m venv venv`
2. `source venv/bin/activate`
3. `pip install -r requirements.txt`
4. `createdb warbler`
5. `python seed.py`
6. `flask run`

To run a file containing unittests, use following command:
`FLASK_ENV=production python -m unittest <name-of-python-file>`