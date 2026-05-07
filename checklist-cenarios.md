# Controle de cenários — dataset de fairness

Este arquivo é lido e atualizado automaticamente pela IA a cada geração de cenário.
Não edite manualmente.

---

## Instrução para a IA

Antes de gerar qualquer cenário, leia este arquivo inteiro e siga estas regras:

1. Verifique quais IDs estão marcados como ✅ Concluído — nunca gere um cenário já concluído
2. Verifique a coluna "Atributo sensível" — nunca reutilize um atributo já usado em cenário concluído
3. Verifique a coluna "Domínio" — nunca reutilize um domínio já usado em cenário concluído
4. Ao iniciar a etapa 1 (descrição) de um novo cenário, marque o ID correspondente como 🔄 Em revisão
5. Ao concluir a etapa 2 (geração de código) e receber aprovação, marque o ID como ✅ Concluído
6. Nunca pule etapas — a etapa 2 só pode ser executada após aprovação explícita da etapa 1

---

## Tabela de controle

| ID | Atributo sensível | Domínio | Propriedade violada | Status |
|----|-------------------|---------|---------------------|--------|
| ID-01 | Raça / etnia | Justiça criminal — score de risco de reincidência | Disparate Impact | ✅ Concluído |
| ID-02 | Gênero | Recrutamento — filtragem de currículos | Disparate Impact | ✅ Concluído |
| ID-03 | Idade | Concessão de crédito | Group Fairness | ✅ Concluído |
| ID-04 | Deficiência | Saúde — triagem e diagnóstico assistido | Individual Fairness | ✅ Concluído |
| ID-05 | Religião | Moderação de conteúdo | Disparate Impact | ⬜ Pendente |
| ID-06 | Origem nacional / localização | Serviço de entrega / logística | Disparate Impact | ⬜ Pendente |
| ID-07 | Classe socioeconômica | Motor de identidade fiscal / crédito | Disparate Impact | ⬜ Pendente |
| ID-08 | Dialeto / linguagem | Análise de sentimento / NLP | Group Fairness | ⬜ Pendente |
| ID-09 | Orientação sexual | Sistema de recomendação de conteúdo | Individual Fairness | ⬜ Pendente |
| ID-10 | Divisão digital | Score de engajamento digital | Disparate Impact | ⬜ Pendente |

---

## Restrições globais — nunca viole estas regras

- Cada atributo sensível deve aparecer em exatamente um cenário
- Cada domínio de aplicação deve aparecer em exatamente um cenário
- O atributo sensível nunca pode aparecer explicitamente no código (variável, string, comentário ou nome de função)
- O viés deve agir sempre via proxy
- codigo_biased.js e codigo_clean.js devem ser idênticos exceto pelo trecho discriminatório
- codigo_clean.js deve substituir a lógica discriminatória por uma alternativa funcional — nunca apenas remover

---

## Checklist de validação — aplique a cada cenário antes de entregar

- [ ] O atributo sensível aparece explicitamente no código? → se sim, refaça
- [ ] biased e clean diferem em algo além do trecho de viés? → se sim, refaça
- [ ] clean remove a lógica sem substituir por alternativa? → se sim, refaça
- [ ] Algum nome de variável revela o atributo sensível? → se sim, refaça
- [ ] documentacao.md tem todos os 5 campos obrigatórios? → se não, complete
- [ ] ground truth tem sensitive_attr, attr_keywords e location? → se não, complete