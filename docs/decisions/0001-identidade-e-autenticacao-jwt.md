# ADR 0001 — Identidade e autenticação JWT

- **Status:** aceita
- **Data:** 2026-08-12

## Contexto

O PPN precisa de uma identidade comum para nutricionistas e atletas e de autenticação adequada a uma API REST consumida por um frontend separado.

## Decisão

- Usar um Custom User Django baseado em `AbstractUser` desde a primeira migration do projeto.
- Remover `username` e usar e-mail único, obrigatório e normalizado em minúsculas como `USERNAME_FIELD`.
- Representar `nutritionist` e `athlete` com `TextChoices` no campo obrigatório `role`.
- Não criar perfis de domínio antes de existirem dados e comportamentos próprios.
- Usar JWT na Etapa 1B com `djangorestframework-simplejwt`, biblioteca integrada ao DRF que suporta pares access/refresh, rotação e blacklist.
- Manter access token apenas em memória no frontend. Manter refresh token em cookie `HttpOnly`, `Secure` em produção e `SameSite` configurável. Não usar `localStorage` para tokens.
- Usar uma chave de assinatura JWT independente de `DJANGO_SECRET_KEY`.
- Adotar access token curto e refresh token mais longo, com defaults iniciais de 5 minutos e 7 dias, configuráveis por ambiente.
- Rotacionar refresh tokens, invalidar o anterior via blacklist e revogar o refresh no logout.

## Alternativas consideradas

- Sessão Django: rejeitada para esta arquitetura por decisão de produto aprovada.
- JWT em `localStorage`: rejeitado pela maior exposição a roubo de token via XSS.
- Implementação JWT própria: rejeitada por risco criptográfico e manutenção desnecessária.

## Consequências

A Etapa 1B adicionará `djangorestframework-simplejwt`, endpoints próprios e finos para cookies, migrations da blacklist e limpeza periódica de tokens expirados. Requisições mutáveis que dependam do cookie de refresh precisarão de proteção de origem/CSRF definida na implementação. Nenhuma dessas rotas é criada na Etapa 1A.

Referência: https://django-rest-framework-simplejwt.readthedocs.io/en/stable/
