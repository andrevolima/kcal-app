# API

## Convenções

- Novos endpoints públicos devem usar o prefixo `/api/v1/`.
- Recursos e campos usam nomes consistentes em inglês e `snake_case` no JSON.
- Coleções devem ser paginadas.
- Mudanças incompatíveis exigem nova versão da API.
- Autorização e ownership são verificados em cada recurso no backend.

## Erros

Formato alvo:

```json
{
  "error": {
    "code": "validation_error",
    "message": "Os dados enviados são inválidos.",
    "details": {}
  }
}
```

Não exponha stack traces ou dados internos ao cliente.

## Autenticação

O mecanismo ainda não foi decidido. Ele deve ser documentado em ADR antes da implementação.

## Endpoint existente

`GET /api/health/` é um endpoint técnico temporário de saúde criado na fundação do projeto. Resposta esperada:

```json
{"status": "ok", "service": "kcal-api"}
```
