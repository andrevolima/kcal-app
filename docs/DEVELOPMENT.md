# Desenvolvimento

## Ambiente local

Requisitos: Python 3.10+, PostgreSQL e Node.js com npm.

Copie `.env.example` para `backend/.env` e ajuste as credenciais. Nunca versione o arquivo real.

### Backend

```powershell
cd backend
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### Frontend

```powershell
cd frontend
npm install
npm run dev
```

## Verificações

```powershell
cd backend
python manage.py check
python manage.py test
ruff check .

cd ..\frontend
npm run lint
npm run typecheck
npm test
npm run build
```

O backend usa Ruff para lint. O frontend usa ESLint e TypeScript em modo estrito.

## Migrations e commits

Crie migrations para toda alteração de schema e revise o SQL/estado gerado. Não edite migrations já compartilhadas. Commits devem ser pequenos, descritivos e conter apenas mudanças relacionadas.

## Definition of Done

Consulte `AGENTS.md`. Em resumo: código claro, regras testadas, autorização considerada, migrations corretas, verificações aprovadas e documentação atualizada.
