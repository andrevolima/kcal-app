# PPN — Painel de Performance Nutricional

## 1. Visão do produto

O PPN é uma plataforma de acompanhamento nutricional contínuo, inicialmente voltada para atletas de endurance, como corredores e triatletas.

O produto não pretende apenas digitalizar o modelo tradicional de consulta + retorno.

O objetivo é criar um ciclo contínuo de acompanhamento entre nutricionista e atleta, no qual:

1. o nutricionista prescreve;
2. o atleta registra o que realmente aconteceu;
3. o sistema transforma esses registros em dados estruturados;
4. o sistema calcula indicadores e tendências;
5. o nutricionista identifica rapidamente quem precisa de atenção;
6. nutricionista e atleta podem se comunicar para realizar ajustes.

O sistema possui dois produtos conectados:

* **PPN Athlete** — aplicativo mobile utilizado pelo atleta;
* **PPN Coach** — painel web utilizado pelo nutricionista.

Ambos utilizam a mesma API e a mesma fonte de dados.

---

# 2. Princípio central

O PPN é estruturado em três grandes pilares:

```text
PRESCRIÇÃO
O que deveria acontecer

        ↓

MONITORAMENTO
O que realmente aconteceu

        ↓

INTELIGÊNCIA
O que os dados significam
```

## Prescrição

Responsabilidade principal do nutricionista.

Inclui:

* dieta;
* refeições;
* quantidades;
* orientações;
* versões do plano;
* estratégias nutricionais futuras.

## Monitoramento

Responsabilidade principalmente do atleta através do aplicativo mobile.

Inclui:

* adesão à dieta;
* substituições;
* refeições parciais;
* refeições não realizadas;
* saídas do planejamento;
* check-in semanal;
* check-in mensal;
* treinos realizados;
* percepção do atleta;
* sintomas e dificuldades quando aplicável.

## Inteligência

Responsabilidade do backend.

Inclui:

* cálculo do PPN;
* scores por dimensão;
* tendências;
* comparação temporal;
* identificação de queda de aderência;
* identificação de mudanças relevantes;
* alertas;
* fila de atenção do nutricionista.

A IA poderá posteriormente interpretar esses dados, mas não será responsável pelos cálculos fundamentais.

---

# 3. Produtos

## 3.1 PPN Athlete — Mobile App

Aplicativo utilizado pelo atleta.

Seu objetivo principal é manter a base de acompanhamento atualizada com o menor atrito possível.

O aplicativo deve responder:

> O que o atleta precisa registrar ou fazer hoje?

O atleta não utilizará o app como painel clínico complexo.

O foco é:

* execução;
* consistência;
* comunicação;
* acompanhamento da própria evolução.

---

## 3.2 PPN Coach — Web

Painel utilizado pelo nutricionista.

Seu objetivo principal é transformar os dados registrados pelos atletas em informação acionável.

O painel deve responder:

> Quem precisa da minha atenção e por quê?

O nutricionista não deve precisar abrir individualmente todos os pacientes para descobrir problemas.

---

# 4. Usuários e autorização

Existem inicialmente dois papéis:

```text
User
├── nutritionist
└── athlete
```

## Nutritionist

Pode acessar somente atletas pertencentes à sua carteira.

## Athlete

Pode acessar somente seus próprios dados.

Toda autorização deve acontecer no backend.

Frontend web e aplicativo mobile nunca são considerados mecanismos de segurança.

---

# 5. Athlete

`Athlete` é a entidade central do domínio.

Conceitualmente:

```text
Athlete
│
├── User
├── Nutritionist
├── perfil
├── objetivos
├── modalidade
│
├── NutritionPlan
├── MealAdherence
│
├── TrainingSession
│
├── WeeklyCheckIn
├── MonthlyCheckIn
│
├── PPNScore
├── Alert
│
└── Conversation / Messages
```

Nem todas essas entidades precisam ser implementadas simultaneamente.

---

# 6. Onboarding

O nutricionista adiciona um atleta à própria carteira.

Fluxo:

```text
Nutritionist
      ↓
cria Athlete
      ↓
convite seguro
      ↓
Athlete ativa conta
      ↓
define senha
      ↓
login no aplicativo mobile
```

O nutricionista nunca define ou conhece a senha do atleta.

---

# 7. Dieta

A dieta é criada pelo nutricionista através do PPN Coach.

Deve ser armazenada de maneira estruturada e versionada.

Estrutura:

```text
Athlete
└── NutritionPlan
    └── NutritionPlanVersion
        └── Meal
            └── MealItem
```

Uma versão publicada representa uma prescrição histórica.

Versões publicadas não podem ser sobrescritas.

Alterações futuras devem gerar uma nova versão.

Exemplo:

```text
NutritionPlan

v1 — published
01/08 → 18/08

v2 — published
19/08 → atual

v3 — draft
em edição
```

Isso permite saber exatamente o que estava prescrito quando determinado evento de adesão foi registrado.

---

# 8. PPN Coach — Editor de dieta

O nutricionista deve conseguir:

* selecionar um atleta;
* criar plano;
* criar versão;
* adicionar refeições;
* adicionar itens;
* definir quantidades;
* definir unidades;
* adicionar observações;
* editar draft;
* publicar;
* consultar histórico;
* criar nova versão a partir da anterior.

O MVP não precisa inicialmente de um banco nutricional completo de alimentos.

Um `MealItem` poderá inicialmente representar:

```text
description
quantity
unit
notes
```

Catálogo nutricional poderá ser introduzido posteriormente.

---

# 9. PPN Athlete — Visualização da dieta

O atleta visualiza no aplicativo somente sua versão publicada atual.

Exemplo:

```text
MINHA DIETA

Café da manhã

Pão integral
2 fatias

Ovos
2 unidades

Banana
1 unidade


Almoço

Arroz
150 g

Frango
120 g
```

O atleta não pode alterar a prescrição.

---

# 10. Adesão alimentar

O objetivo não é transformar o PPN em um contador tradicional de calorias.

O atleta registra sua relação com aquilo que foi prescrito.

Para cada refeição:

```text
Planejado
↓
Meal

Executado
↓
MealAdherence
```

Estados iniciais:

* `followed`
* `substituted`
* `partial`
* `skipped`
* `off_plan`

Interface mobile deve traduzir isso para linguagem simples.

Exemplo:

```text
CAFÉ DA MANHÃ

Como foi?

✓ Segui a dieta
↔ Fiz substituição
◐ Comi parcialmente
✕ Não comi
+ Comi algo fora do plano
```

---

# 11. Substituições

Quando o atleta selecionar `substituted`, poderá informar resumidamente o que mudou.

Exemplo:

```text
Planejado:
Pão + ovos + banana

Executado:
Tapioca + ovos + banana

Motivo:
Não tinha pão disponível.
```

O MVP não precisa obrigatoriamente transformar toda substituição em composição nutricional detalhada.

O objetivo inicial é identificar:

* frequência;
* contexto;
* padrão;
* impacto na adesão.

---

# 12. Registro de dificuldades

O atleta poderá informar situações como:

* não conseguiu realizar refeição;
* estava sem fome;
* esqueceu;
* estava sem o alimento;
* rotina/trabalho;
* desconforto gastrointestinal;
* viagem;
* treino interferiu;
* outra situação.

Isso permite ao nutricionista distinguir:

```text
baixa adesão
```

de:

```text
problema recorrente que exige ajuste da prescrição
```

---

# 13. Check-in semanal

Realizado pelo aplicativo mobile.

Deve levar aproximadamente poucos minutos.

Objetivo:

capturar como foi a semana sem criar um formulário excessivamente longo.

Pode incluir:

* percepção geral;
* adesão;
* fome;
* energia;
* recuperação;
* sono;
* digestão;
* dificuldades;
* sintomas;
* mudanças na rotina;
* observações.

Os campos definitivos devem ser definidos antes da implementação.

O check-in semanal alimentará métricas e tendências.

---

# 14. Check-in mensal

Mais profundo que o semanal.

Pode avaliar:

* evolução percebida;
* metas;
* performance;
* alimentação;
* treinamento;
* recuperação;
* estratégia nutricional;
* suplementação;
* principais dificuldades;
* feedback sobre a dieta;
* necessidade percebida de ajustes.

Também poderá servir de base para resumo mensal.

---

# 15. Treinos

No MVP, o atleta poderá registrar manualmente treinos realizados.

Estrutura conceitual:

```text
TrainingSession

athlete
date
sport
type
duration
distance
rpe
completed
notes
```

Exemplo:

```text
Corrida

70 min
12 km
PSE 7/10

Observação:
senti queda de energia no final
```

Integrações com Garmin, Strava, Apple Health, Google Health Connect ou outras plataformas são evoluções futuras.

O modelo deve permitir integração futura sem depender dela no MVP.

---

# 16. Comunicação

Comunicação entre nutricionista e atleta passa a fazer parte do produto.

Estrutura conceitual:

```text
Conversation
│
├── Athlete
├── Nutritionist
│
└── Message
    ├── sender
    ├── content
    ├── created_at
    └── read_at
```

O atleta poderá utilizar o aplicativo para:

* tirar dúvidas;
* informar dificuldades;
* conversar sobre dieta;
* solicitar revisão da dieta.

O nutricionista poderá responder através do painel web.

---

# 17. Solicitação de ajuste da dieta

Uma solicitação de nova dieta ou ajuste não deve necessariamente ser apenas uma mensagem perdida na conversa.

O produto deve permitir futuramente distinguir uma solicitação acionável.

Conceitualmente:

```text
DietAdjustmentRequest

athlete
nutrition_plan
reason
notes
status
created_at
resolved_at
```

Possíveis estados:

```text
pending
in_review
resolved
rejected
```

Para o MVP, avaliar se isso será uma entidade própria ou inicialmente uma ação estruturada dentro da comunicação.

Essa decisão deve ser tomada antes da implementação.

---

# 18. PPN Score

O sistema calcula um score de acompanhamento de 0 a 100.

Conceitualmente:

```text
PPN
├── Nutrição / adesão
├── Fueling
├── Hidratação
├── Sono
├── Recuperação
├── Treinamento
├── Suplementação
└── Check-ins
```

A fórmula definitiva deverá ser documentada antes da implementação.

O score não deve existir apenas como valor atual.

O sistema deve armazenar histórico suficiente para observar tendências.

---

# 19. Tendência

O painel deve responder:

```text
PPN atual
84

7 dias atrás
81

30 dias atrás
76

Tendência
↑
```

E também:

```text
PPN atual
71

7 dias atrás
77

Tendência
↓
```

O nutricionista deve conseguir identificar rapidamente melhora, estabilidade ou piora.

---

# 20. Motor de regras

O backend deve detectar situações importantes sem depender de IA.

Exemplos conceituais:

```text
adesão caiu de forma relevante
→ alerta

substituições recorrentes
→ possível ajuste

múltiplas refeições ignoradas
→ atenção

check-in piorou
→ atenção

carga de treino aumentou + recuperação piorou
→ atenção

atleta solicitou ajuste
→ prioridade
```

As regras devem ser:

* determinísticas;
* testáveis;
* transparentes;
* documentadas.

---

# 21. Fila de atenção

Esta é uma das principais telas do PPN Coach.

Ao entrar, o nutricionista deve encontrar algo semelhante a:

```text
BOM DIA

47 atletas ativos

5 precisam de atenção
────────────────────

🔴 João
PPN 72 ↓ 8
Adesão caiu
Solicitou ajuste da dieta

🟠 Marina
PPN 78 ↓ 3
3 refeições ignoradas
Check-in semanal piorou

🟡 Pedro
PPN 82 →
5 substituições nesta semana
```

O objetivo é responder:

> Quem precisa da minha atenção hoje?

---

# 22. Dashboard geral do nutricionista

O PPN Coach deve fornecer um panorama da carteira.

Exemplo:

```text
ATLETAS ATIVOS
47

PPN MÉDIO
81 ↑

PRECISAM DE ATENÇÃO
5

ESTÁVEIS
33

──────────────────

CARTEIRA

João      91 ↑
Pedro     86 →
Marina    78 ↓
Carlos    64 ↓
```

O nutricionista deve poder:

* pesquisar atleta;
* filtrar;
* ordenar;
* identificar tendências;
* identificar alertas;
* abrir detalhe individual.

---

# 23. Dashboard individual do nutricionista

Ao abrir um atleta:

```text
JOÃO

PPN
84 ↑ +3

────────────────

Nutrição        91
Treino          86
Sono            81
Recuperação     77

────────────────

Dieta
Adesão: 87%

Check-in
Último: 2 dias

Treinos
4 esta semana

────────────────

Pontos de atenção

• 3 substituições no jantar
• recuperação piorou
• solicitou ajuste da dieta

────────────────

Timeline
```

O nutricionista deve conseguir acessar a partir daqui:

* dieta;
* histórico de dieta;
* adesão;
* check-ins;
* treinos;
* mensagens;
* alertas;
* histórico do PPN.

---

# 24. Timeline

O sistema deve transformar registros separados em uma história cronológica.

Exemplo:

```text
HOJE

07:30
Check-in realizado

09:15
Café da manhã
✓ dieta

12:30
Almoço
↔ substituição

18:00
Treino
Corrida 70 min
PSE 7

20:10
Mensagem
"Sentiu desconforto durante o treino"
```

O nutricionista deve conseguir compreender o contexto sem abrir vários módulos isoladamente.

---

# 25. PPN Athlete — Home

O aplicativo do atleta deve ser orientado a ações.

Exemplo:

```text
Olá, João

HOJE

○ Registrar dieta
✓ Check-in concluído
○ Registrar treino

────────────────

MINHA DIETA
Ver plano atual

────────────────

MEU ACOMPANHAMENTO

PPN 84 ↑

────────────────

NUTRICIONISTA

2 mensagens

Falar com nutricionista
```

Evitar transformar o app do atleta em um dashboard clínico excessivamente complexo.

---

# 26. Arquitetura de clientes

A arquitetura passa a possuir dois clientes.

```text
             ┌────────────────────┐
             │ PPN Coach          │
             │ React / Web        │
             └─────────┬──────────┘
                       │
                       │
                       ▼
                 REST API / JWT
                       ▲
                       │
                       │
             ┌─────────┴──────────┐
             │ PPN Athlete        │
             │ Mobile App         │
             └────────────────────┘

                       │
                       ▼

                Django + DRF
                       │
             ┌─────────┼─────────┐
             ▼         ▼         ▼
        PostgreSQL   Redis     Celery
```

Web e mobile compartilham regras de negócio e autorização através da mesma API.

Nenhum cliente acessa diretamente o banco.

---

# 27. API

A API deve ser desenhada em torno dos casos de uso e não especificamente de telas.

Isso permite que:

```text
Web
   ┐
   ├──→ mesma regra de negócio
Mobile
   ┘
```

Autenticação:

* JWT;
* access token curto;
* refresh conforme política de segurança;
* revogação;
* rate limiting.

A estratégia de armazenamento seguro dos tokens no mobile deverá ser definida na documentação técnica específica do aplicativo antes da implementação.

---

# 28. Segurança

O sistema contém dados pessoais e de acompanhamento do atleta.

Princípios obrigatórios:

* autenticação em todos os recursos privados;
* autorização no backend;
* object-level ownership;
* rate limiting;
* validação de inputs;
* secrets fora do código;
* tokens protegidos;
* logs minimizados;
* histórico preservado;
* operações sensíveis auditáveis;
* HTTPS em produção.

Nutritionist:

```text
request.user
↓
somente própria carteira
```

Athlete:

```text
request.user
↓
somente próprio Athlete
↓
somente próprios dados
```

---

# 29. IA

IA permanece como camada posterior.

Fluxo:

```text
dados do atleta
↓
analytics determinístico
↓
PPN
↓
tendências
↓
rules engine
↓
alertas
↓
payload preparado
↓
IA
```

Possíveis usos:

* resumo mensal;
* resumo do atleta;
* identificação textual das principais mudanças;
* preparação da próxima consulta;
* organização de contexto.

IA não calcula o score oficial e não altera dieta automaticamente.

---

# 30. MVP atualizado

## Fundação

* autenticação JWT;
* Nutritionist;
* Athlete;
* convite/ativação;
* ownership;
* rate limiting.

## PPN Coach — Web

* login;
* carteira;
* criação de atletas;
* criação e versionamento de dieta;
* editor de refeições;
* visualização da adesão;
* visualização de check-ins;
* visualização de treinos;
* PPN atual e histórico;
* tendências;
* fila de atenção;
* dashboard geral;
* dashboard individual;
* comunicação.

## PPN Athlete — Mobile

* login;
* ativação da conta;
* visualização da dieta;
* registro de adesão;
* registro de substituição;
* registro de refeição parcial;
* registro de refeição não realizada;
* registro de saída do plano;
* check-in semanal;
* check-in mensal;
* registro manual de treino;
* acompanhamento básico do PPN;
* comunicação com nutricionista;
* solicitação de ajuste da dieta.

## Backend

* cálculo determinístico do PPN;
* histórico;
* rules engine;
* alertas;
* processamento assíncrono quando necessário.

---

# 31. Fora do MVP inicial

Manter inicialmente fora:

* integração automática com wearables;
* Garmin;
* Strava;
* Apple Health;
* Health Connect;
* banco nutricional avançado;
* análise automática de fotos;
* alteração automática de dieta por IA;
* prontuário clínico completo;
* billing;
* marketplace;
* múltiplos profissionais por atleta;
* integrações laboratoriais.

Esses recursos não devem influenciar a arquitetura do MVP além de evitar decisões que tornem sua inclusão futura desnecessariamente difícil.

---

# 32. Princípio de experiência

## Athlete Mobile

Pergunta principal:

> O que preciso fazer hoje?

O registro deve exigir poucos passos.

## Nutritionist Web

Pergunta principal:

> Quem precisa da minha atenção hoje?

O sistema deve priorizar exceções, tendências e situações acionáveis.

O objetivo não é fazer o nutricionista navegar por dezenas de dashboards todos os dias.

---

# 33. Métrica de sucesso do produto

O PPN funciona quando transforma:

```text
dieta prescrita
+
execução do atleta
+
check-ins
+
treinos
+
comunicação
```

em:

```text
dados longitudinais
↓
tendências
↓
alertas
↓
decisões melhores do nutricionista
```

O produto deve reduzir o esforço necessário para o atleta manter o nutricionista informado e reduzir o esforço necessário para o nutricionista descobrir quem precisa de intervenção.
