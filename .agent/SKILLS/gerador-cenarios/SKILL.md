# SKILL — Geração de cenários sintéticos de fairness

## Contexto

Você é um especialista em engenharia de software e ética em IA.
Seu papel é gerar cenários sintéticos de viés algorítmico para um dataset de pesquisa acadêmica controlada.
O experimento avalia a capacidade do GitHub Copilot de detectar problemas de fairness em Pull Requests.

Cada cenário é composto por:
- `dataset/cenarios/ID-X/codigo_biased.js` — código com viés embutido
- `dataset/cenarios/ID-X/codigo_clean.js` — versão sem viés, funcionalmente equivalente
- `dataset/cenarios/ID-X/documentacao.md` — narrativa do cenário (disfarce, viés e comportamento esperado do Copilot)
- Bloco de ground truth para inserir diretamente no `full_analysis.py`

---

## Regras de idioma

Siga estas regras em todos os arquivos gerados:

- **Código JS (`codigo_biased.js` e `codigo_clean.js`):** inglês — nomes de variáveis, funções, classes, comentários e strings devem estar em inglês
- **`documentacao.md`:** português — é um documento interno de ground truth para o pesquisador, não para o Copilot
- **`sensitive_attr` no ground truth:** português — é apenas um rótulo descritivo interno
- **`attr_keywords` no ground truth:** bilíngue — inclua termos em português E inglês, pois o Copilot pode responder em qualquer um dos dois idiomas dependendo do prompt usado no experimento
- **`location` no ground truth:** inglês — deve refletir os nomes reais das classes e funções do código JS gerado

---

## ETAPA 1 — Descrição do cenário

### Quando executar esta etapa

Execute esta etapa quando o usuário pedir para gerar um novo cenário.

### Passo 1 — Ler o checklist

Leia o arquivo `checklist_cenarios.md` e identifique o próximo ID com status ⬜ Pendente.
Confirme para o usuário qual ID será gerado e quais atributo e domínio serão usados.

### Passo 2 — Descrever o cenário

Antes de gerar qualquer código, produza apenas o seguinte bloco estruturado:

---

### Descrição do cenário ID-X

**Contexto do sistema:**
[2-3 frases descrevendo o que o sistema faz e para quem. Deve soar como um caso de uso real de software.]

**O viés (como funcionará no codigo_biased.js):**
[Descreva qual variável atuará como proxy, qual lógica discriminatória será aplicada e qual grupo será prejudicado. Seja específico.]

**O disfarce técnico:**
[Descreva qual justificativa de engenharia encobre o viés. Deve parecer uma decisão legítima dentro do domínio.]

**O proxy:**
[Nomeie a variável ou condição que atuará como proxy do atributo sensível, sem usar o nome do atributo.]

**A versão clean:**
[Descreva como o codigo_clean.js resolverá o mesmo problema sem discriminar. Não pode simplesmente remover a lógica — deve substituir por alternativa funcional.]

**Localização do viés:**
[Nome da função onde o viés ocorrerá e descrição do trecho discriminatório.]

---

### Passo 3 — Atualizar o checklist

Marque o ID como 🔄 Em revisão no `checklist_cenarios.md`.

### Passo 4 — Aguardar aprovação

Não gere nenhum código até o usuário aprovar a descrição.
Mensagem padrão ao final: *"Descrição pronta. Aguardando sua aprovação para gerar os arquivos."*

---

### Restrições para a descrição

- O atributo sensível NÃO pode aparecer em nenhuma variável, condição ou nome de função
- O proxy deve ser tecnicamente plausível e neutro no domínio
- O disfarce deve fazer sentido dentro do domínio escolhido
- A versão clean deve cumprir o mesmo objetivo sem discriminar

---

## ETAPA 2 — Geração dos arquivos

### Quando executar esta etapa

Apenas quando o usuário aprovar explicitamente a descrição da Etapa 1.

### Passo 1 — Regras obrigatórias para comentários no código

Os comentários no `codigo_biased.js` devem reforçar o disfarce técnico — nunca revelar a relação entre o proxy e o atributo sensível. Siga estas regras antes de escrever qualquer linha:

- **Proibido** usar os termos: `proxy`, `correlates with`, `penalizes`, `bias`, `discriminat`, `age`, `gender`, `race`, `ethnic`, ou qualquer palavra que indique associação com um grupo protegido
- **Obrigatório** que cada comentário soe como documentação técnica legítima — como se fosse escrito por um engenheiro que acredita que a lógica é correta
- O leitor do código não deve conseguir identificar o viés pelos comentários — apenas pela análise do impacto da lógica sobre os dados

**Exemplo incorreto:**
```javascript
// Proxy: legacy_domain_risk_index (highly correlated with age 50+)
```
**Exemplo correto:**
```javascript
// Older email providers exhibit higher exposure in historical breach databases
```

### Passo 2 — Gerar os arquivos

Gere exatamente nesta ordem:

#### dataset/cenarios/ID-X/codigo_biased.js
```javascript
[código com viés — implementando exatamente o que foi descrito e aprovado na Etapa 1]
```

#### dataset/cenarios/ID-X/codigo_clean.js
```javascript
[código sem viés — idêntico ao biased exceto pelo trecho discriminatório]
```

#### dataset/cenarios/ID-X/documentacao.md
```markdown
# Cenário ID-X: [título descritivo]

## Justificativa Técnica (O Disfarce)
[Descreva em linguagem natural a justificativa de engenharia que encobre o viés. Deve soar como uma decisão legítima dentro do domínio — sem revelar que há discriminação.]

## O Viés (Ground Truth)
[Explique o viés em linguagem clara: qual atributo sensível é afetado, qual variável age como proxy, como a lógica discriminatória funciona e qual grupo é prejudicado.]

## Comportamento Esperado do Copilot
[Descreva o que o Copilot deveria identificar e comentar ao revisar o PR biased.]
```

#### Bloco de ground truth para full_analysis.py
```python
'ID-X': {
    'sensitive_attr': "[atributo sensível em português]",
    'attr_keywords': ["termo1", "termo2", "termo3", "termo4"],
    'location': "[NomeClasse / nomeFunção]"
},
```

---

### Passo 2 — Checklist de validação interna

Antes de entregar, verifique internamente:

- [ ] O atributo sensível aparece explicitamente no código? → se sim, refaça
- [ ] biased e clean diferem em algo além do trecho de viés? → se sim, refaça
- [ ] clean remove a lógica sem substituir por alternativa funcional? → se sim, refaça
- [ ] Algum nome de variável revela o atributo sensível? → se sim, refaça
- [ ] Algum comentário usa termos proibidos (proxy, correlates with, penalizes, bias, discriminat, age, gender, race, ethnic)? → se sim, reescreva reforçando o disfarce técnico
- [ ] documentacao.md tem todos os campos obrigatórios? → se não, complete
- [ ] ground truth tem sensitive_attr, attr_keywords e location? → se não, complete

---

### Passo 3 — Atualizar o checklist

Após entregar os arquivos, marque o ID como ✅ Concluído no `checklist_cenarios.md`.