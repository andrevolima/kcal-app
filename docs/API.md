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

JWT foi definido no ADR 0001 e implementado com access token curto e refresh token rotativo. Endpoints DRF exigem autenticação por padrão; exceções públicas são explícitas.

O access token é enviado no header `Authorization: Bearer <token>`. O refresh fica exclusivamente no cookie `ppn_refresh`, inacessível ao JavaScript. Tokens e credenciais nunca devem aparecer em logs.

### `GET /api/v1/auth/csrf/`

Público. Inicializa o cookie CSRF usado nos POSTs de autenticação. Retorna `200`.

### `POST /api/v1/auth/login/`

Público, limitado a 5 tentativas/minuto por IP por padrão. Requer `X-CSRFToken`.

```json
{"email": "user@example.com", "password": "secret"}
```

Retorna `200` com `{ "access": "...", "user": { "id": 1, "email": "...", "role": "nutritionist" } }` e define o refresh em cookie `HttpOnly`. Credenciais inválidas ou usuário inativo retornam `401` com mensagem genérica.

### `POST /api/v1/auth/refresh/`

Público, limitado a 10/minuto por padrão. Requer cookie refresh e CSRF. Retorna `200` com novo access, rotaciona o refresh e invalida o anterior. Refresh ausente, expirado, inválido ou revogado retorna `401`.

### `POST /api/v1/auth/logout/`

Requer CSRF. Revoga o refresh presente, remove o cookie e retorna `204`. Não é apenas uma operação visual do frontend.

### `GET /api/v1/auth/me/`

Privado. Requer access válido. Retorna somente `id`, `email` e `role`. Sem autenticação ou com token inválido/expirado retorna `401`.

## Códigos comuns

- `400`: dados inválidos.
- `401`: autenticação ausente, inválida ou expirada.
- `403`: CSRF ou autorização recusada.
- `429`: limite excedido; a resposta inclui `Retry-After` quando disponível.

## Endpoint existente

`GET /api/health/` é um endpoint técnico temporário de saúde criado na fundação do projeto. Resposta esperada:

```json
{"status": "ok", "service": "kcal-api"}
```
