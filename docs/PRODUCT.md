# PPN — Product Specification

## 1. Produto

PPN significa Painel de Performance Nutricional. É uma plataforma de acompanhamento contínuo para atletas de endurance, inicialmente corredores e triatletas. O objetivo não é apenas digitalizar consultas: o sistema deve permitir ao nutricionista acompanhar o que acontece com seus atletas entre as consultas.

## 2. Fluxo central

O produto possui três pilares:

```text
PRESCRIÇÃO                    O que deveria acontecer
     ↓
EXECUÇÃO / MONITORAMENTO      O que realmente aconteceu
     ↓
ANÁLISE / INTELIGÊNCIA        O que os dados significam
```

O sistema deve permitir comparar planejamento e execução.

## 3. Usuários

- **Nutritionist:** profissional responsável por uma carteira de atletas. Pode acessar somente atletas sob sua responsabilidade.
- **Athlete:** atleta acompanhado por um nutricionista. Pode acessar somente seus próprios dados.

## 4. Entidade central

`Athlete` é a entidade central do domínio. O atleta poderá possuir perfil, objetivos, modalidade, dieta, adesão, treinos, check-ins, sono, hidratação, sintomas, métricas, alertas e relatórios. Nem todas essas informações precisam fazer parte da primeira implementação.

## 5. Prescrição nutricional

A dieta deve ser armazenada de forma estruturada:

```text
NutritionPlan
└── NutritionPlanVersion
    └── Meal
        └── MealItem
```

Planos precisam possuir histórico. Uma versão nova não deve destruir a versão anterior.

## 6. Adesão

O sistema não pretende exigir que o atleta registre cada alimento consumido como um contador tradicional de calorias. O principal dado é a relação entre execução e planejamento.

Estados inicialmente previstos: `followed`, `substituted`, `partial`, `skipped` e `off_plan`. Quando necessário, podem ser registrados motivo e observações. Esses eventos formarão a base para o cálculo posterior de aderência e tendências.

## 7. Treinos

Inicialmente, os treinos podem ser registrados manualmente. Informações previstas incluem atleta, data, modalidade, duração, distância, percepção subjetiva de esforço, tipo, conclusão e observações. Integrações com plataformas esportivas não são dependência do MVP.

## 8. Check-ins

- **Diário:** deve ser extremamente rápido.
- **Semanal:** acompanha percepção da semana, dificuldades, recuperação, fome, digestão e mudanças de rotina.
- **Mensal:** permite avaliação mais ampla de evolução, metas, performance, alimentação, treinamento, estratégia nutricional, suplementação e feedback.

O MVP deverá priorizar os check-ins definidos no roadmap.

## 9. PPN

O PPN será um score composto. Dimensões conceituais incluem nutrição/adesão, fueling, hidratação, sono, recuperação, treinamento, suplementação e consistência/check-ins. A fórmula definitiva deve ser definida e documentada antes de ser tratada como regra estável do produto.

## 10. Tendências

O sistema não deve depender apenas do score atual. Deve permitir observar PPN atual, PPN anterior, PPN de 30 dias atrás e tendência histórica.

## 11. Motor de regras

Alertas devem poder existir independentemente de IA. Exemplos: queda recorrente de adesão; piora do sono combinada com aumento da carga; falha recorrente na estratégia de treino. Regras precisam ser transparentes e explicáveis.

## 12. Inbox de atenção

Uma das principais propostas de valor para o nutricionista é responder: **quem precisa da minha atenção hoje?** A aplicação deverá apresentar atletas e situações que merecem revisão.

## 13. IA

IA é uma camada de interpretação e não deve calcular métricas fundamentais:

```text
PostgreSQL → analytics → scores → tendências → alertas
           → payload preparado → IA → interpretação
```

Possíveis saídas incluem resumo, principais mudanças, pontos para revisão, perguntas sugeridas e contexto para a próxima interação. A responsabilidade clínica e a comunicação final permanecem com o profissional.

## 14. Dashboard do nutricionista

Deverá permitir visualizar carteira, atletas que precisam de atenção, score/tendência, informações resumidas e acesso ao detalhe do atleta.

## 15. Dashboard do atleta

Deve ser mais simples e focado em execução, consistência, atividades pendentes e evolução. Não deve funcionar como ferramenta de diagnóstico.

## 16. MVP

O escopo de referência inclui autenticação de nutricionista e atleta, cadastro e convite de atletas, criação e visualização da dieta, adesão às refeições, registro de treino, check-ins semanal e mensal, cálculo e histórico do PPN, dashboards individual e da carteira, fila de atenção, resumo mensal por IA e relatório PDF.

## 17. Fora do MVP

Funcionalidades futuras devem permanecer fora do caminho crítico enquanto não forem priorizadas: integrações com wearables e plataformas esportivas, comunicação interna completa, competições avançadas, métricas clínicas genéricas e automações avançadas.
