FROM python:3

WORKDIR /usr/src/app

COPY ./libs ./libs
RUN pip install --no-cache-dir libs/reframed

RUN pip install --no-cache-dir -i https://pypi.gurobi.com gurobipy

COPY ./misolib ./misolib
COPY ./scripts ./scripts
COPY ./setup.py ./setup.py
RUN pip install --no-cache-dir .