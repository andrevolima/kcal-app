# Segurança

## Princípios

- Autenticação e autorização são responsabilidades do backend.
- Nutricionistas acessam apenas atletas sob sua responsabilidade.
- Atletas acessam apenas os próprios dados.
- Toda consulta e mutação deve aplicar ownership no servidor.
- Toda entrada externa é não confiável e deve ser validada.
- Esconder elementos no frontend não constitui controle de acesso.

## Secrets e logs

Secrets ficam em variáveis de ambiente e nunca são versionados. Use `.env.example` apenas com valores fictícios. Senhas, tokens, chaves e dados pessoais sensíveis não devem aparecer em logs.

## Autenticação

A estratégia aprovada é JWT. O access token dura 5 minutos por padrão e permanece somente em memória. O refresh dura 7 dias por padrão e fica exclusivamente em cookie `HttpOnly`, restrito a `/api/v1/auth/`, com `Secure` em produção e `SameSite=Lax` por padrão. Refresh tokens são rotacionados e o anterior entra na blacklist; logout revoga o token atual. A chave JWT é independente da `DJANGO_SECRET_KEY`. Consulte o ADR 0001.

Login, refresh e logout exigem token CSRF porque estabelecem ou usam credenciais em cookie. CORS aceita credenciais apenas para origens explicitamente configuradas. O frontend não usa `localStorage` nem `sessionStorage` para tokens.

O backend nega acesso por padrão nos endpoints DRF. Cada endpoint público deverá declarar essa condição explicitamente. Papéis e ownership sempre serão validados no servidor.

## Rate limiting

O DRF aplica limites configuráveis por ambiente: anônimo `100/hora`, autenticado `1000/hora`, login `5/minuto`, refresh `10/minuto` e operações sensíveis `10/minuto`, por padrão. Essa camada reduz abuso comum, mas não substitui proteção de borda contra brute force ou negação de serviço. Consulte o ADR 0002.

## IA

Dados enviados à IA devem ser preparados e minimizados. Modelos não recebem acesso irrestrito ao banco e não podem alterar automaticamente métricas fundamentais ou decisões clínicas.

## Banco e produção

Use credenciais com privilégio mínimo, conexão segura, backups testados e rotação de secrets. Antes de produção, desative debug, defina uma secret key forte, restrinja hosts e origens CORS, configure HTTPS e execute o deployment checklist do Django.

## Decisões pendentes

A política de retenção de dados e a infraestrutura de proteção de borda ainda precisam de decisões antes da produção.
