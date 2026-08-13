# ADR 0002 — Rate limiting da API

- **Status:** aceita
- **Data:** 2026-08-12

## Contexto

A API precisa de proteção básica contra abuso, especialmente nos endpoints de autenticação, sem introduzir infraestrutura antes da necessidade real.

## Decisão

Usar throttling do Django REST Framework com limites por ambiente e escopos por categoria:

| Categoria | Default inicial | Identidade |
|---|---:|---|
| anônimo | 100/hora | IP |
| autenticado | 1000/hora | usuário |
| login | 5/minuto | IP |
| refresh | 10/minuto | usuário/IP |
| operação sensível | 10/minuto | usuário |

Os valores são uma linha de base conservadora para desenvolvimento e início do produto, não uma garantia contra brute force ou negação de serviço. Devem ser revisados com métricas reais. Login, refresh e operações sensíveis usarão `ScopedRateThrottle` quando suas views forem implementadas.

## Consequências

O cache local é suficiente apenas para desenvolvimento. Produção com múltiplas instâncias exigirá cache compartilhado e proteção adicional no proxy/WAF. O throttling do DRF usa operações de cache não atômicas e pode permitir pequenas imprecisões sob concorrência.

Referência: https://www.django-rest-framework.org/api-guide/throttling/
