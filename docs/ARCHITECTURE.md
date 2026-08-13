# PPN — Arquitetura

## Visão geral

O PPN será inicialmente um monólito modular:

```text
React + TypeScript
        │ REST API
        ▼
Django REST Framework
        ▼
Business Modules
        ▼
Django ORM
        ▼
PostgreSQL
```

Quando necessário, o processamento assíncrono usará Django → Redis → Celery.

## Backend

Estrutura alvo:

```text
backend/
├── config/
├── apps/
│   ├── accounts/
│   ├── athletes/
│   ├── nutrition/
│   ├── adherence/
│   ├── training/
│   ├── checkins/
│   ├── analytics/
│   ├── alerts/
│   └── reports/
└── tests/
```

Nem todos os apps devem ser criados antecipadamente. Um módulo nasce quando existir funcionalidade real para ele.

### Camadas

- **Models:** persistência e invariantes locais.
- **Services:** operações de negócio que alteram estado.
- **Selectors:** consultas complexas e reutilizáveis.
- **API:** transporte HTTP, incluindo serializers, views, URLs e permissions.
- **Tasks:** operações assíncronas.

Fluxo preferencial de dependências: API → services/selectors → models → database. Evitar dependências circulares entre domínios.

> Estado atual: o projeto Django ainda usa o pacote `kcal_setup`. A migração para `config/` deve ser uma decisão explícita e separada.

## Frontend

Estrutura alvo baseada em features:

```text
frontend/src/
├── api/
├── components/
├── features/
│   ├── auth/
│   ├── athletes/
│   ├── nutrition/
│   ├── adherence/
│   ├── training/
│   ├── checkins/
│   └── dashboard/
├── routes/
├── hooks/
└── types/
```

> Estado atual: o frontend é uma base React em JavaScript. A adoção de TypeScript deve ocorrer antes do desenvolvimento das features.

## Escalabilidade

O backend deve permanecer stateless sempre que possível. Arquivos persistentes futuros devem usar armazenamento apropriado, não o filesystem local da instância. A arquitetura deve permitir múltiplas instâncias da API usando o mesmo PostgreSQL e serviços compartilhados. Microserviços não fazem parte da arquitetura inicial.

## Analytics e IA

Separação obrigatória: domain data → analytics → rules → alerts → AI interpretation. IA não pertence ao domínio fundamental e não deve ser necessária para cálculos determinísticos.
