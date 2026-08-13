# Kcal

Projeto com API Django e frontend React/Vite.

## Documentação

- [Produto](docs/PRODUCT.md)
- [Arquitetura](docs/ARCHITECTURE.md)
- [Banco de dados](docs/DATABASE.md)
- [Segurança](docs/SECURITY.md)
- [API](docs/API.md)
- [Desenvolvimento](docs/DEVELOPMENT.md)
- [Roadmap](docs/ROADMAP.md)
- [Design System](docs/DESIGN_SYSTEM.md)
- [Decisões arquiteturais](docs/decisions/README.md)

## Backend

```powershell
cd backend
.\venv\Scripts\Activate.ps1
python manage.py migrate
python manage.py runserver
```

A API fica disponível em `http://127.0.0.1:8000`. O endpoint de teste é
`GET /api/health/`.

## Frontend

Em outro terminal:

```powershell
cd frontend
npm install
npm run dev
```

Abra `http://localhost:5173`. Durante o desenvolvimento, o Vite encaminha as
requisições feitas para `/api` ao backend Django na porta 8000.
