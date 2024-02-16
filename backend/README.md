## Sample Directory
```bash
└── project
    ├── frontend
    │   └── _some_features...
    ├── backend
    │   ├── app
    │   │   ├── __init__.py
    │   │   ├── migrations # DB migration with `alembic` package
    │   │   ├── routers  # controllers
    │   │   │   ├── __init__.py
    │   │   │   ├── embedding_router.py
    │   │   │   └── _other_features...
    │   │   ├── services  # main logics
    │   │   │   ├── __init__.py
    │   │   │   └── embedding_service.py
    │   │   ├── schemas  # Pydantic structure: return/get body(DTO), metadata ...
    │   │   │   ├── __init__.py
    │   │   │   └── embedding_schema.py
    │   │   ├── models  # DB structure, CRUD
    │   │   │   ├── __init__.py
    │   │   │   └── embedding.py
    │   │   ├── cores  # control base things
    │   │   │   ├── __init__.py
    │   │   │   ├── dependencies.py  # DI methods / classes
    │   │   │   ├── constants.py  # constants
    │   │   │   ├── config.py  # configs like .env, .ini ...
    │   │   │   ├── exceptions.py  # exception control
    │   │   │   └── utils.py  # some simple functions for utility
    │   │   ├── database  # include DB and VS
    │   │   └── main.py  # run main process
    │   ├── test  # test logics
    │   ├── (cloud)  # control cloud and server
    │   └── _other_files  # .env, .gitignore, .yml ...
    └── _other_files  # .env, .gitignore, .yml ...
```

## Note
- DB migration에 `alembic` 패키지를 사용한다고 합니다. 지금은 환경에 없습니다.
- Embedding key로 인해 `.env` 파일이 필요하다면 cores 폴더 안에 만들면 됩니다.
    - 이 파일을 쉽게 불러오는 `python-dotenv` 패키지를 사용하는 것도 고려해볼 수 있습니다.
- Qdrant 로컬 저장소는 `database` 폴더 안에 만들면 됩니다.
- 파일 이름들은 샘플이며, 바뀔 수 있습니다.
- Python은 상수(재정의 불가 값) 정의가 복잡해서, `constants.py` 파일에 간단한 상수 정의 예시가 있습니다.

## Reference
- [참고 구조](https://github.com/tiangolo/full-stack-fastapi-postgresql/tree/master/src/backend/app/app)