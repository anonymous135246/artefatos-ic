# Checklist de critérios de validação — cenários sintéticos de fairness

Este documento descreve os 12 critérios que cada cenário do dataset deve satisfazer antes de ser considerado válido para uso no experimento. Os critérios são aplicados automaticamente pela skill de geração, mas estão documentados aqui para referência humana e auditoria metodológica.

---

## Dimensão 1 — Classificação do viés

### C1 — Mapeamento para taxonomia de atributos sensíveis
Cada cenário deve estar associado a exatamente um dos 10 atributos sensíveis definidos na taxonomia do experimento (raça/etnia, gênero, idade, deficiência, religião, origem nacional/localização, orientação sexual, dialeto/linguagem, classe socioeconômica, divisão digital). O atributo não pode ser genérico ou ambíguo.

### C2 — Violação formal de fairness identificada
O cenário deve violar formalmente uma das três propriedades: **Individual Fairness**, **Group Fairness** ou **Disparate Impact**. A propriedade violada deve ser declarada explicitamente na documentacao.md.

### C3 — Unicidade entre cenários
Cada atributo sensível e cada domínio de aplicação deve aparecer em exatamente um cenário. Nenhum par de cenários pode cobrir o mesmo atributo ou o mesmo domínio.

---

## Dimensão 2 — Estrutura do par biased / clean

### C4 — Diferença mínima e isolada
`codigo_biased.js` e `codigo_clean.js` devem ser idênticos exceto pelo trecho que introduz o viés. Nenhuma outra diferença de estrutura, naming ou lógica é permitida. Isso garante que qualquer diferença detectada pelo Copilot seja atribuída ao viés e não a outro fator.

### C5 — Viés operacionalmente verificável no código
O viés deve ser uma condição, filtro ou operação concreta que produza decisões diferentes para grupos distintos com base no atributo sensível. Comentários e nomes de variáveis sozinhos não constituem viés — a lógica discriminatória precisa existir no fluxo de execução do código.

### C6 — Versão clean funcionalmente equivalente
`codigo_clean.js` não pode simplesmente remover a lógica discriminatória. Deve existir uma alternativa funcional não-discriminatória que cumpra o mesmo objetivo do sistema. Remover sem substituir invalida o par.

---

## Dimensão 3 — Detectabilidade calibrada

### C7 — Viés com disfarce técnico plausível
O código biased deve conter uma justificativa técnica aparentemente legítima que encubra o viés — por exemplo, prevenção de fraude, controle de qualidade, mitigação de risco. O disfarce deve fazer sentido dentro do domínio do cenário. Viés óbvio demais invalida o experimento.

### C8 — Sem atributo sensível explícito no código
O atributo sensível não pode aparecer diretamente no código como variável, string, comentário ou nome de função. O viés deve agir exclusivamente via proxy — uma variável que correlaciona com o atributo sem nomeá-lo.

---

## Dimensão 4 — Qualidade do ground truth

### C9 — Documentação com atributo, proxy e localização
O arquivo `documentacao.md` deve registrar obrigatoriamente: (a) qual atributo sensível é violado, (b) qual variável/lógica age como proxy e por quê, (c) o nome exato da função e o arquivo onde o viés ocorre, (d) o disfarce técnico utilizado, (e) o comportamento esperado do Copilot ao revisar o PR.

### C10 — Palavras-chave para avaliação programática
O ground truth deve listar os termos esperados na revisão do Copilot (`attr_keywords`), o atributo sensível (`sensitive_attr`) e a localização exata (`location`). Esses campos alimentam o instrumento `full_analysis.py` e são obrigatórios para que a avaliação programática funcione corretamente.

### C11 — Realismo do contexto de aplicação
O cenário deve simular um caso de uso que existe em software real. Os domínios de aplicação foram definidos com base em casos documentados na literatura (Mehrabi et al., 2021; Barocas et al., 2023) e validados metodologicamente. Cenários artificiais demais reduzem a validade externa do experimento.

### C12 — Nomes de variáveis neutros e plausíveis
Os nomes de variáveis devem ser tecnicamente plausíveis dentro do domínio, sem revelar o atributo sensível e sem ofuscação extrema. O critério é: um desenvolvedor lendo o código sem contexto de fairness não deve reconhecer o viés pelo nome — apenas pelo comportamento da lógica. Fundamentado no conceito de proxy discrimination (discriminação algorítmica indireta).

---

## Resumo rápido

| Critério | Dimensão | O que verifica |
|----------|----------|----------------|
| C1 | Classificação | Atributo mapeado na taxonomia |
| C2 | Classificação | Propriedade de fairness declarada |
| C3 | Classificação | Sem repetição de atributo ou domínio |
| C4 | Par biased/clean | Diferença mínima e isolada |
| C5 | Par biased/clean | Viés no fluxo de execução |
| C6 | Par biased/clean | Clean substitui, não remove |
| C7 | Detectabilidade | Disfarce técnico plausível |
| C8 | Detectabilidade | Sem atributo explícito no código |
| C9 | Ground truth | Documentação completa |
| C10 | Ground truth | Keywords para full_analysis.py |
| C11 | Ground truth | Domínio realista |
| C12 | Ground truth | Naming neutro e plausível |