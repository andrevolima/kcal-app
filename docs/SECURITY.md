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

## Ownership da carteira

A carteira aplica três camadas: queryset filtrado no PostgreSQL, permission de papel e permission de objeto. Nutricionistas consultam `Athlete.objects.filter(nutritionist=request.user)`; atletas consultam somente `Athlete.objects.filter(user=request.user)`. IDs enviados pelo frontend nunca definem ownership. Tentativas cross-tenant retornam `404` para evitar confirmar a existência do recurso.

A criação deriva o nutricionista e o papel do atleta no backend. Campos administrativos e credenciais não são aceitos. Desativar um acompanhamento não bloqueia automaticamente a conta: `Athlete.is_active` e `User.is_active` são controles distintos.

## Convites de primeiro acesso

Convites usam tokens gerados por CSPRNG com 256 bits de entropia. O banco armazena somente SHA-256; o token bruto é uma credencial bearer presente apenas no link. Convites expiram em 48 horas por padrão, são de uso único e são consumidos junto com `set_password` em transação. Uma nova emissão revoga convites anteriores.

Links podem ser retornados pela API somente em ambiente de desenvolvimento com `ATHLETE_INVITATION_EXPOSE_LINK=True`; a aplicação recusa essa configuração fora de desenvolvimento. Tokens, links completos e senhas não devem aparecer em logs. Validação e ativação públicas retornam dados mínimos e possuem throttles próprios. Convite inicial não pode ser reutilizado como recuperação de senha.

## Rate limiting

O DRF aplica limites configuráveis por ambiente: anônimo `100/hora`, autenticado `1000/hora`, login `5/minuto`, refresh `10/minuto` e operações sensíveis `10/minuto`, por padrão. Essa camada reduz abuso comum, mas não substitui proteção de borda contra brute force ou negação de serviço. Consulte o ADR 0002.

Convites adicionam: emissão `5/hora`, validação `20/minuto` e ativação `5/minuto`.

## IA

Dados enviados à IA devem ser preparados e minimizados. Modelos não recebem acesso irrestrito ao banco e não podem alterar automaticamente métricas fundamentais ou decisões clínicas.

## Banco e produção

Use credenciais com privilégio mínimo, conexão segura, backups testados e rotação de secrets. Antes de produção, desative debug, defina uma secret key forte, restrinja hosts e origens CORS, configure HTTPS e execute o deployment checklist do Django.

## Decisões pendentes

A política de retenção de dados e a infraestrutura de proteção de borda ainda precisam de decisões antes da produção.
