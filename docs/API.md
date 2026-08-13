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

JWT foi definido no ADR 0001. Os endpoints de login, refresh, logout e usuário atual pertencem à Etapa 1B e ainda não existem. Endpoints DRF exigem autenticação por padrão; exceções públicas devem ser explícitas.

As rotas futuras ficarão sob `/api/v1/auth/`. Tokens e credenciais nunca devem aparecer em logs ou respostas além do necessário para o protocolo aprovado.

## Endpoint existente

`GET /api/health/` é um endpoint técnico temporário de saúde criado na fundação do projeto. Resposta esperada:

```json
{"status": "ok", "service": "kcal-api"}
```
