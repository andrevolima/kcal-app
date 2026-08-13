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

A estratégia aprovada é JWT. A Etapa 1B usará access token curto em memória e refresh token em cookie `HttpOnly`, com rotação, blacklist e revogação no logout. A chave JWT será independente da `DJANGO_SECRET_KEY`. Consulte o ADR 0001.

O backend nega acesso por padrão nos endpoints DRF. Cada endpoint público deverá declarar essa condição explicitamente. Papéis e ownership sempre serão validados no servidor.

## Rate limiting

O DRF aplica limites globais para usuários anônimos e autenticados. Login, refresh e operações sensíveis terão escopos mais restritivos quando forem implementados. Os limites são configuráveis por ambiente. Essa camada reduz abuso comum, mas não substitui proteção de borda contra brute force ou negação de serviço. Consulte o ADR 0002.

## IA

Dados enviados à IA devem ser preparados e minimizados. Modelos não recebem acesso irrestrito ao banco e não podem alterar automaticamente métricas fundamentais ou decisões clínicas.

## Banco e produção

Use credenciais com privilégio mínimo, conexão segura, backups testados e rotação de secrets. Antes de produção, desative debug, defina uma secret key forte, restrinja hosts e origens CORS, configure HTTPS e execute o deployment checklist do Django.

## Decisões pendentes

A política de retenção de dados e a infraestrutura de proteção de borda ainda precisam de decisões antes da produção.
