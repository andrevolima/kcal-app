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

## Carteira de atletas

Todos os endpoints exigem JWT e permanecem sob o throttle autenticado global. Recursos de outra carteira não aparecem no queryset do nutricionista e retornam `404`.

### `POST /api/v1/athletes/`

Exclusivo para nutricionistas. Cria `User` e `Athlete` atomicamente na carteira do usuário autenticado.

```json
{
  "email": "athlete@example.com",
  "first_name": "Nome",
  "last_name": "Sobrenome"
}
```

Retorna `201`. `nutritionist`, `role` e privilégios são derivados no backend. O usuário recebe senha inutilizável; convite e definição inicial de senha pertencem à Etapa 2B.

### `GET /api/v1/athletes/`

Exclusivo para nutricionistas. Retorna coleção paginada contendo somente a própria carteira, com 20 itens por página por padrão.

### `GET /api/v1/athletes/{id}/`

O nutricionista acessa apenas atletas sob sua responsabilidade. Um usuário Athlete pode acessar somente o perfil associado à própria identidade.

### `PATCH /api/v1/athletes/{id}/`

Exclusivo para o nutricionista responsável. Aceita somente `first_name` e `last_name`. E-mail exige um futuro fluxo de reverificação e não pode ser alterado aqui.

### `POST /api/v1/athletes/{id}/deactivate/`

Exclusivo para o nutricionista responsável. Define `Athlete.is_active=false`, preserva o registro e não altera `User.is_active`. Retorna `200` com o recurso atualizado.

Não existe endpoint `DELETE` para atletas.

## Convite e primeiro acesso

### `POST /api/v1/athletes/{id}/invite/`

Exclusivo para o nutricionista responsável e limitado a `5/hour`. Emite um convite com validade padrão de 48 horas e revoga convites anteriores ainda abertos. Atletas inativos ou que já possuem senha utilizável não podem receber convite de primeiro acesso.

Retorna `201` com `status` e `expires_at`. Somente em desenvolvimento, quando explicitamente habilitado, inclui `invitation_url`; produção nunca retorna o token bruto.

### `GET /api/v1/auth/invitations/{token}/`

Público e limitado a `20/minute` por IP. Retorna somente validade e expiração, ou um motivo mínimo entre `invalid`, `expired`, `used` e `revoked`. Não retorna dados do atleta.

### `POST /api/v1/auth/invitations/{token}/activate/`

Público, protegido por CSRF e limitado a `5/minute` por IP.

```json
{
  "password": "new password",
  "password_confirm": "new password"
}
```

Valida a senha com os validators oficiais do Django, define o hash com `set_password` e consome o convite atomicamente. Retorna `{ "activated": true }`. Não realiza login automático; o atleta usa o login JWT normal depois da ativação.

## Endpoint existente

`GET /api/health/` é um endpoint técnico temporário de saúde criado na fundação do projeto. Resposta esperada:

```json
{"status": "ok", "service": "kcal-api"}
```
