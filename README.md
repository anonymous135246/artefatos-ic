# Experimento de Fairness na Auditoria de Código (Iniciação Científica)

Este repositório contém as ferramentas e os conjuntos de dados utilizados para simular e avaliar a detecção de problemas de *fairness* (justiça/viés) em Pull Requests utilizando modelos de linguagem (LLMs) via API do Groq.

---

## 📂 Estrutura do Projeto

*   **`simulador_ic.py`**: Script principal responsável por executar a simulação da revisão de código. Ele carrega os cenários e os prompts, faz as requisições para a API do Groq usando o modelo `llama-3.3-70b-versatile` e salva as respostas em formato CSV.
*   **`evaluate_rodada.py`**: Script de avaliação. Ele lê o CSV gerado pela simulação, calcula as métricas de desempenho (Verdadeiros Positivos, Falsos Positivos, etc., além de Acurácia, Precisão e Recall) e gera um relatório consolidado em Markdown.
*   **`dataset/`**:
    *   **`cenarios/`**: Diretórios de `ID-01` a `ID-10`, cada um contendo:
        *   `codigo_biased.js`: Código JavaScript contendo um viés ou problema de *fairness* deliberado.
        *   `codigo_clean.js`: Versão corrigida e livre de problemas óbvios de *fairness*.
    *   **`prompts/`**: Modelos de instruções fornecidos ao revisor:
        *   `simples/copilot-instructions.md`: Instruções básicas de revisão.
        *   `avancado/copilot-instructions.md`: Instruções detalhadas com foco em categorias de fairness.
*   **`api_key.txt`**: Arquivo local (não rastreado) contendo a chave de API do Groq.

---

## 🚀 Como Executar o Experimento (Passo a Passo)

### 1. Pré-requisitos
Certifique-se de ter o Python 3 instalado em sua máquina.

### 2. Configurar a Chave da API do Groq
O simulador utiliza a API do Groq para interagir com o modelo Llama 3.3.
1. Obtenha uma chave de API gratuita no painel do [Groq Console](https://console.groq.com/).
2. Na raiz deste projeto, crie um arquivo chamado `api_key.txt` e cole a sua chave (ela deve começar com `gsk_`):
   ```bash
   echo "sua_chave_aqui_gsk_..." > api_key.txt
   ```

### 3. Instalar as Dependências
Instale a biblioteca oficial do Groq:
```bash
pip install groq
```

### 4. Executar a Simulação
Rode o script simulador:
```bash
python simulador_ic.py
```

O script é interativo e solicitará duas configurações no terminal:
1. **IDs dos cenários**: Digite os IDs que deseja executar separados por vírgula (ex: `01,02,03`) ou apenas aperte **Enter** para executar todos os 10 cenários disponíveis.
2. **Execuções por cenário**: Quantas vezes cada combinação deve ser repetida (padrão: 5 execuções por combinação).

> [!NOTE]
> **Mecanismo de Checkpoint:** O simulador salva os resultados no arquivo `rodada_FINAL.csv` a cada chamada concluída. Se a execução for interrompida por limites de taxa (Rate Limits) ou queda de conexão, basta rodar o script novamente. Ele identificará os registros já concluídos no CSV e continuará exatamente de onde parou.

---

## 📊 Como Avaliar os Resultados

Após a conclusão da simulação, os resultados consolidados estarão salvos no arquivo `rodada_FINAL.csv`. Para gerar as métricas:

1. Abra o arquivo `evaluate_rodada.py` e valide se os caminhos das variáveis `CSV_PATH` e `OUTPUT_MD` estão corretos para a sua estrutura de pastas local.
2. Execute o script de avaliação:
   ```bash
   python evaluate_rodada.py
   ```
3. O script criará um relatório em formato Markdown (ex: no diretório `resultados/`) detalhando:
   *   Tabela com o número de Verdadeiros Positivos (TP), Verdadeiros Negativos (TN), Falsos Positivos (FP) e Falsos Negativos (FN) por tipo de prompt (`simples` vs `avancado`).
   *   Acurácia, Precisão e Recall globais e segmentados.
   *   Um payload em formato JSON com todos os dados calculados para fácil integração ou consumo.
