# Prediction Markets
The prediction_markets repo offers a Python toolkit for interacting with Futuur, manifold.market, and Polymarket APIs. It enables searching, correlating, and trading in prediction markets. Key features include easy API integration, secure key storage with .env, and functionality for both market analysis and trading operations.


# Development environment
## Install development environment manually

Requires:
- Python 3.10

Installing:
1.  Run on Shell / PowerShell
    ```
    mkdir <project_dir>  # prediction_markets name suggestion
    cd <project_dir>
    git clone https://github.com/futuur/core.git src
    python -m venv .venv
    source .venv/bin/activate  # for linux
    .venv\bin\activate         # for windows
    cd src
    pip install -r requirements.txt

2. Make a **.env** file from **.env.example** and set basic variables. Remove or comment other variables.

# Project structure

## /futuur

Holds the service that is responsible for interacting with the Futuur API.

## /manifold

Holds the service that is responsible for interacting with the Manifold API.

## /abitrage

Has a proof of concept script that interacts with the API services. As a first step the matching bets will be hardcoded or manually saved on a file. In the future there can be a discovery service responsible for browsing the different markets and finding matching bets