# NEXPRIME-LANGCHAIN

## Tools
<div align="center">

[![Python](https://img.shields.io/badge/python-3.11.7-34d058?logo=python)](https://www.python.org/downloads/release/python-3117/)
[![FastAPI](https://img.shields.io/badge/fastapi-v0.109.2-34d058?logo=fastapi)](https://fastapi.tiangolo.com/)
[![LangChain](https://img.shields.io/badge/%F0%9F%A6%9C%EF%B8%8Flangchain-v0.1.6-34d058)](https://www.langchain.com/)
[![Uvicorn](https://img.shields.io/badge/uvicorn-0.27.1-34d058?logo=data%3Aimage%2Fsvg%2Bxml%3Bbase64%2CPCEtLSBSZXBsYWNlIHRoZSBjb250ZW50cyBvZiB0aGlzIGVkaXRvciB3aXRoIHlvdXIgU1ZHIGNvZGUgLS0%2BCgo8c3ZnIHJvbGU9ImltZyIgdmlld0JveD0iMCAwIDI0IDI0IiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciPgogIDxwYXRoIGQ9Ik0xMiA4YTMgMyAwIDAgMCAzLTMgMyAzIDAgMCAwLTMtMyAzIDMgMCAwIDAtMyAzIDMgMyAwIDAgMCAzIDNtMCAzLjU0QzkuNjQgOS4zNSA2LjUgOCAzIDh2MTFjMy41IDAgNi42NCAxLjM1IDkgMy41NCAyLjM2LTIuMTkgNS41LTMuNTQgOS0zLjU0VjhjLTMuNSAwLTYuNjQgMS4zNS05IDMuNTRaIj48L3BhdGg%2BCjwvc3ZnPg%3D%3D&logoColor=white)](https://www.uvicorn.org/)<br>
[![OpenAI](https://img.shields.io/badge/openai-412991?style=for-the-badge&logo=openai)](https://openai.com/)
[![PostgreSQL](https://img.shields.io/badge/postgresql-008bb9?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Vector Store](https://img.shields.io/badge/vector_store-ffffff?style=for-the-badge&logo=data:image/svg+xml;base64,PD94bWwgdmVyc2lvbj0iMS4wIiA/PjxzdmcgaGVpZ2h0PSIxNzkyIiB2aWV3Qm94PSIwIDAgMTc5MiAxNzkyIiB3aWR0aD0iMTc5MiIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cGF0aCBkPSJNODk2IDc2OHEyMzcgMCA0NDMtNDN0MzI1LTEyN3YxNzBxMCA2OS0xMDMgMTI4dC0yODAgOTMuNS0zODUgMzQuNS0zODUtMzQuNS0yODAtOTMuNS0xMDMtMTI4di0xNzBxMTE5IDg0IDMyNSAxMjd0NDQzIDQzem0wIDc2OHEyMzcgMCA0NDMtNDN0MzI1LTEyN3YxNzBxMCA2OS0xMDMgMTI4dC0yODAgOTMuNS0zODUgMzQuNS0zODUtMzQuNS0yODAtOTMuNS0xMDMtMTI4di0xNzBxMTE5IDg0IDMyNSAxMjd0NDQzIDQzem0wLTM4NHEyMzcgMCA0NDMtNDN0MzI1LTEyN3YxNzBxMCA2OS0xMDMgMTI4dC0yODAgOTMuNS0zODUgMzQuNS0zODUtMzQuNS0yODAtOTMuNS0xMDMtMTI4di0xNzBxMTE5IDg0IDMyNSAxMjd0NDQzIDQzem0wLTExNTJxMjA4IDAgMzg1IDM0LjV0MjgwIDkzLjUgMTAzIDEyOHYxMjhxMCA2OS0xMDMgMTI4dC0yODAgOTMuNS0zODUgMzQuNS0zODUtMzQuNS0yODAtOTMuNS0xMDMtMTI4di0xMjhxMC02OSAxMDMtMTI4dDI4MC05My41IDM4NS0zNC41eiIvPjwvc3ZnPg==)]()<br>
[![Pipenv](https://img.shields.io/badge/pipenv-v2023.12.1-3776ab)](https://pipenv.pypa.io/en/latest/)
[![Pytest](https://img.shields.io/badge/pytest-v8.0.0-3776ab)](https://docs.pytest.org/en/8.0.x/)
</div>

## Installation
_Download_ `Python 3.11.7` based on your OS.<br>
Link: https://www.python.org/downloads/releasepython-3117<br>
> Make sure it's available from your command line. You can check this by
> ```bash
> $ python --version  # for windows OS
> Python 3.11.7
> $ pip --version
> pip 24.0 from <your-pip-path> (python 3.11)
> ```

_Install_ `pipenv` to manage the project virtual environment. Don't forget to check.
```bash
$ pip install pipenv --user
$ pipenv --version
pipenv, version 2023.12.1
```
> [!IMPORTANT]
> You may get some $\textsf{\color{orange}warning signs}$ because of the __environment variable PATH__. Please follow that sign before checking the `pipenv` installation.

_Make_ a virtual environment and install packages in your local project directory. The name is automatically created based on the project folder name.
```bash
$ cd <your-project-directory>
$ pipenv --python 3.11.7 install --dev --ignore-pipfile
```

`pipenv` provides two package categories: $\textsf{\color{palegreen}default}$ and $\textsf{\color{violet}dev}$. We use both when developing including custom category $\textsf{\color{darksalmon}personal}$.<br>
Lastly, check the package dependencies ifnecessary.
```bash
$ pipenv shell  # (Optional) Activate the environment
$ pipenv graph
```
> [!TIP]
> VScode activates the environment automatically if you select the interpreter. Check the activated status by looking at the name in front of the directory path.

## Note
- You $\textsf{\color{red}MUST}$ carefully distinguish the package installation environment.
    - For testing, personal use or not allowed, install into the custom $\textsf{\color{darksalmon}personal}$ group without synchronization with `pipfile.lock`.
        ```bash
        pipenv install <package> --categories=personal --skip-lock
        ```
    - After discussion with team members, they will be imported into the $\textsf{\color{palegreen}default}$ or $\textsf{\color{violet}dev}$ group.
- Packages that manage DB and vector store have $\textsf{\color{red}NOT}$ been installed yet. Updates will be made later.
- The `pytest` package is in the $\textsf{\color{violet}dev}$ group.
- Formatters are recommanded. Pick one of the following after discussion:
    - [`black` with VScode extension](https://marketplace.visualstudio.com/items?itemName=ms-python.black-formatter)
    - [`autopep8` with VScode extension](https://marketplace.visualstudio.com/items?itemName=ms-python.autopep8)
    - [`yapf` with VScode extension](https://marketplace.visualstudio.com/items?itemName=eeyore.yapf)

    You can use them by installing packages, but should use those extensions if VScode.
- There is a `requirements.txt` generated by `pipenv`.

## Reference
- [Handle the environment variable PATH error for Python](https://stackoverflow.com/questions/63940952/py-works-but-not-python-in-command-prompt-for-windows-10)
- [`pipenv` installation guide](https://pipenv.pypa.io/en/latest/installation.html)
- [Handle the environment variable PATH error for `pipenv`](https://sooblair84.tistory.com/15)