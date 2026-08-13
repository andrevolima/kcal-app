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

## IA

Dados enviados à IA devem ser preparados e minimizados. Modelos não recebem acesso irrestrito ao banco e não podem alterar automaticamente métricas fundamentais ou decisões clínicas.

## Banco e produção

Use credenciais com privilégio mínimo, conexão segura, backups testados e rotação de secrets. Antes de produção, desative debug, defina uma secret key forte, restrinja hosts e origens CORS, configure HTTPS e execute o deployment checklist do Django.

## Decisões pendentes

O mecanismo de autenticação, política de sessão/token, proteção contra abuso e política de retenção de dados ainda precisam de ADRs antes da implementação.
