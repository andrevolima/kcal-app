# Kcalor — Design System

## Direção visual

O Kcalor deve transmitir saúde, energia, movimento, qualidade de vida, performance e simplicidade. A interface é clara, moderna, jovem e fácil de entender, evitando aparência hospitalar, excesso de informação e efeitos decorativos.

> **Performance sem complicação.**

Quando houver dúvida entre uma solução elaborada e uma simples, escolha a mais simples. Elementos visuais devem ajudar o usuário a entender, decidir ou agir.

## Tokens de cor

| Token CSS | Valor | Uso |
|---|---|---|
| `--color-brand` | `#9DFF00` | Marca, ação principal, seleção e pequenos destaques |
| `--color-graphite` | `#1D1E20` | Contraste, navegação e ícones |
| `--color-background` | `#FFFFFF` | Fundo principal e cards |
| `--color-background-soft` | `#F7F8F5` | Fundo secundário |
| `--color-text-primary` | `#1D1E20` | Texto principal |
| `--color-text-secondary` | `#686B66` | Texto secundário |
| `--color-border` | `#E6E8E3` | Bordas sutis |
| `--color-disabled` | `#B7BAB4` | Estados desabilitados |
| `--color-success` | `#22A06B` | Sucesso |
| `--color-warning` | `#E9A23B` | Alerta |
| `--color-danger` | `#D64545` | Erro e ação destrutiva |
| `--color-info` | `#3B82F6` | Informação |

O verde Kcalor é uma cor de marca e ação, não um sinônimo de sucesso. Não cubra grandes áreas com verde e não use essa cor em ações destrutivas.

## Tipografia

```css
font-family: Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
```

Pesos preferenciais:

- `400`: texto;
- `500`: labels;
- `600`: títulos e ações;
- `700`: destaques importantes.

Use poucos tamanhos e mantenha a hierarquia: informação principal → secundária → detalhes.

## Formas e espaçamento

Raios:

| Token | Valor |
|---|---:|
| `--radius-small` | `8px` |
| `--radius-medium` | `12px` |
| `--radius-large` | `16px` |

Escala de espaçamento:

| Token | Valor |
|---|---:|
| `--space-1` | `4px` |
| `--space-2` | `8px` |
| `--space-3` | `12px` |
| `--space-4` | `16px` |
| `--space-6` | `24px` |
| `--space-8` | `32px` |
| `--space-12` | `48px` |

Prefira espaço entre grupos a divisores e bordas adicionais.

## Componentes

### Cards

Fundo branco, borda sutil, raio de 12–16px e espaço interno confortável. Evite sombras fortes, gradientes e excesso de conteúdo.

### Botões

- **Primary:** fundo verde Kcalor e texto grafite; uma ação principal por contexto.
- **Secondary:** fundo branco ou transparente, borda neutra e texto grafite.
- **Danger:** cor semântica danger, somente para ações destrutivas.

### Inputs

Inputs possuem label, área confortável, fundo branco e borda neutra. O foco usa destaque da marca. Erros sempre precisam de mensagem textual, não apenas cor.

### Ícones

Use ícones lineares, simples e consistentes apenas quando ajudarem na compreensão. Não misture famílias ou estilos.

## Imagens

Prefira pessoas reais, esporte, corrida, ciclismo, alimentação, natureza, movimento e rotina saudável. Evite estética hospitalar, fisiculturismo, fitness agressivo ou uma representação artificial de “saúde perfeita”.

## Dashboards e mobile

Dashboards devem priorizar: atenção necessária, indicadores principais, tendência e detalhes. Não transforme a tela em um painel repleto de gráficos.

No mobile, use uma coluna, alvos de toque confortáveis e menos informação secundária. Evite tabelas largas e preserve a hierarquia visual.

## Regras de desenvolvimento

- Reutilize os tokens globais definidos em `frontend/src/styles.css`.
- Não adicione cores HEX diretamente em componentes.
- Não crie padrões de botão ou input por feature.
- Não adicione gradientes ou sombras fortes sem justificativa documentada.
- Não adicione uma biblioteca de UI sem decisão arquitetural.
- Antes de criar um padrão, confirme que os existentes não resolvem o problema.
- Todo novo token global deve ser registrado neste documento e no CSS.
