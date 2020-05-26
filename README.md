# Tableau data source to pandas dataframe

## installation

### required libraries (pip)

You will need to create a python virtual environment (e.g. `python3 -m virtualenv venv`) and activate it (e.g. `source venv/bin/activate`).

You install the dependencies by using pip:

```shell
pip install -r requirements.txt
```

### environment file

You will also need to create a `.env` file to store confidential information.
Typically, it contains the following information:

```shell
export TABLEAU_SERVER=https://tableau.yourdomain.com
export TABLEAU_USERNAME=XXXX
export TABLEAU_PASSWORD=YYYY
```

## running the code

simply run the main module:

```shell
python main.py
```

## output

You should get `.pkl` file which is a pickle serialized representation of the pandas dataframe.
