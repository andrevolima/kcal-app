# PPN — Instruções para agentes de desenvolvimento

Este arquivo define as regras que qualquer agente de IA, incluindo Codex, deve seguir ao modificar este repositório.

## 1. Antes de programar

Leia, nesta ordem:

1. `docs/PRODUCT.md`
2. `docs/ARCHITECTURE.md`
3. `docs/DATABASE.md`
4. `docs/SECURITY.md`
5. `docs/API.md`
6. Documentação específica da feature, quando existir.

Não implemente uma decisão importante que contradiga esses documentos. Se houver conflito ou uma decisão arquitetural relevante não estiver documentada, pare e apresente o problema antes de escolher uma solução.

## 2. Stack

Backend: Python, Django, Django REST Framework e PostgreSQL.

Frontend: React e TypeScript.

Processamento assíncrono planejado: Celery e Redis.

Arquitetura: monólito modular, API REST e frontend separado do backend. Não introduza microserviços, event sourcing, CQRS, filas adicionais ou outras abstrações arquiteturais sem necessidade documentada.

## 3. Filosofia

Prioridades, nesta ordem: correção, segurança, clareza, simplicidade, testabilidade, performance e abstração.

Prefira código explícito e simples. Não crie abstrações para problemas que ainda não existem.

## 4. Backend

Apps Django representam domínios de negócio. Estrutura preferencial:

```text
app/
├── models/
├── services/
├── selectors/
├── api/
├── tasks.py
└── tests/
```

- `models`: persistência e invariantes locais.
- `services`: operações que modificam estado e regras de negócio.
- `selectors`: consultas de leitura complexas.
- `serializers`: validação de entrada e representação.
- `views`: HTTP e orquestração.
- `permissions`: autorização.
- `tasks`: execução assíncrona.

Views e serializers não devem concentrar regras complexas de negócio. Signals não são o mecanismo padrão para workflows de negócio.

## 5. Banco

Toda alteração de schema exige migration. Nunca altere migrations que já possam ter sido aplicadas em ambientes compartilhados. Não use `JSONField` para evitar modelagem relacional quando os dados possuem estrutura conhecida. Preserve histórico quando ele tiver significado de negócio. Planos nutricionais publicados não devem ser silenciosamente sobrescritos.

## 6. Segurança

A autorização acontece no backend. Nunca considere esconder elementos no frontend como mecanismo de segurança. Nutricionistas só podem acessar atletas sob sua responsabilidade; atletas só podem acessar seus próprios dados. Toda entrada externa deve ser tratada como não confiável. Secrets nunca entram no repositório. Nunca registre senhas, tokens ou secrets em logs.

## 7. IA

IA não é fonte de verdade para métricas fundamentais. O fluxo conceitual é:

```text
dados → analytics → scores/tendências → regras/alertas → IA
```

A IA recebe dados previamente preparados e minimizados. Não forneça acesso irrestrito ao banco para modelos de IA. Não permita que respostas de IA alterem automaticamente scores fundamentais.

## 8. Dependências

Não adicione bibliotecas sem necessidade. Antes de adicionar uma dependência, explique o problema, verifique se a stack existente já resolve e explique por que a nova dependência é apropriada.

## 9. Escopo

Implemente somente a tarefa solicitada. Não implemente funcionalidades futuras “aproveitando” a alteração atual. Não refatore módulos não relacionados sem necessidade.

## 10. Antes de uma implementação relevante

Apresente objetivo, arquivos afetados, alterações de banco, impacto de segurança, testes necessários e riscos ou decisões pendentes. Se uma decisão importante não estiver documentada, solicite decisão antes de implementá-la.

## 11. Depois da implementação

Verifique migrations, testes, lint, type checking quando aplicável, permissions, alterações inesperadas e documentação afetada. Informe claramente o que foi alterado.

## 12. Definition of Done

Uma feature não está concluída apenas porque funciona. Ela está concluída quando:

- a implementação está clara;
- regras de negócio relevantes possuem testes;
- autorização foi considerada;
- migrations estão corretas;
- lint e testes passam;
- a documentação afetada foi atualizada;
- não existem alterações não relacionadas.
