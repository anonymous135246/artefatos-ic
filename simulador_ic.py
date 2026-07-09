import os
import sys

user_site = os.path.expanduser("~/.local/lib/python3.12/site-packages")
if user_site not in sys.path:
    sys.path.insert(0, user_site)

import csv
import time
from groq import Groq

# --- CONFIGURAÇÃO DO AMBIENTE ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__)) if '__file__' in globals() else os.getcwd()
DATASET_PATH = os.path.join(SCRIPT_DIR, "dataset")
SCENARIOS_ROOT = os.path.join(DATASET_PATH, "cenarios")
PROMPTS_PATH = os.path.join(DATASET_PATH, "prompts")
RESULTADOS_CSV = os.path.join(SCRIPT_DIR, "rodada_FINAL.csv")
API_KEY_FILE = os.path.join(SCRIPT_DIR, "api_key.txt")

# Modelo usado na simulação
MODELO = "llama-3.3-70b-versatile"

# Limites do free tier do Groq para esse modelo
GROQ_RPD_LIMIT = 1000    # requests per day (limite oficial)
GROQ_RPM_LIMIT = 30      # requests per minute

# Sleep dinâmico:
# Prompts simples (~2s resposta) → sleep curto
# Prompts avançados (~8s resposta) → sleep longo para respeitar TPM
SLEEP_MINIMO = 5          # segundos mínimos entre chamadas
SLEEP_POR_SEGUNDO = 1.5   # segundos extras por segundo de resposta da API

# Títulos neutros para emular a PR
PR_TITLES = {
    '01': 'Justice: Risk Assessment Engine',
    '02': 'Recruitment: Applicant Tracking System',
    '03': 'Finance: Credit Decision Engine',
    '04': 'Health: Emergency Triage Analyzer',
    '05': 'Platform: Content Moderation Engine',
    '06': 'Logistics: Regional Delivery Optimizer',
    '07': 'Identity: Fiscal Stability Engine',
    '08': 'Analytics: Sentiment Analysis Module',
    '09': 'Platform: Content Recommendation Engine',
    '10': 'Engagement: Digital Score Calculator',
}

# --- CARREGAR CHAVE DE API ---
if not os.path.exists(API_KEY_FILE):
    raise FileNotFoundError(
        f"Chave do Groq não encontrada em {API_KEY_FILE}.\n"
        f"Crie o arquivo com sua chave. Exemplo: echo 'gsk_...' > {API_KEY_FILE}"
    )

with open(API_KEY_FILE, "r", encoding="utf-8") as f:
    api_key = f.read().strip()

if not api_key or not api_key.startswith("gsk_"):
    raise ValueError(
        f"O arquivo {API_KEY_FILE} está vazio ou contém uma chave inválida.\n"
        "A chave do Groq deve começar com 'gsk_'."
    )

client = Groq(api_key=api_key)


def list_available_scenarios():
    available = []
    if os.path.exists(SCENARIOS_ROOT):
        for entry in sorted(os.listdir(SCENARIOS_ROOT)):
            if entry.startswith("ID-"):
                cid = entry.replace("ID-", "")
                available.append(cid)
    return available


def is_already_completed(cid, c_type, p_type, execucao):
    if not os.path.exists(RESULTADOS_CSV):
        return False
    try:
        with open(RESULTADOS_CSV, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                csv_cid   = row.get("ID_Cenario", "").strip().zfill(2)
                tgt_cid   = str(cid).strip().zfill(2)
                csv_ctype = row.get("Tipo_Codigo", "").strip()
                csv_ptype = row.get("Tipo_Prompt", "").strip()
                csv_exec  = row.get("Execucao", "").strip()
                csv_rev   = row.get("Review_Copilot", "").strip()

                if (csv_cid == tgt_cid and
                    csv_ctype == c_type and
                    csv_ptype == p_type and
                    csv_exec == str(execucao) and
                    csv_rev and
                    csv_rev != "ERRO_API"):
                    return True
    except Exception as e:
        print(f"[AVISO] Erro ao ler CSV de progresso: {e}")
    return False


import re

def get_scenario_filename(code_content):
    # Procura por "class NomeDaClasse"
    match = re.search(r'class\s+(\w+)', code_content)
    if match:
        class_name = match.group(1)
        # Converte PascalCase/camelCase para snake_case (ex: ResumeAnalyzer -> resume_analyzer.js)
        snake_name = re.sub(r'(?<!^)(?=[A-Z])', '_', class_name).lower()
        return f"{snake_name}.js"
    return "codigo_analise.js"  # Fallback neutro


def run_simulation():
    available = list_available_scenarios()

    print("=" * 60)
    print("  SIMULADOR DE PR — SELEÇÃO DE CENÁRIOS E EXECUÇÕES")
    print("=" * 60)
    print(f"  Cenários disponíveis : {', '.join(available)}")
    
    escolha_cenarios = input("  Digite os IDs dos cenários (ex: 09,10 ou Enter para todos): ").strip()
    if escolha_cenarios:
        scenarios_to_run = [c.strip().zfill(2) for c in escolha_cenarios.split(",") if c.strip()]
        scenarios_to_run = [c for c in scenarios_to_run if c in available]
        if not scenarios_to_run:
            print("  [AVISO] Nenhum cenário válido selecionado. Usando todos.")
            scenarios_to_run = available
    else:
        scenarios_to_run = available

    escolha_exec = input("  Digite o número de execuções por cenário (Enter para usar 5): ").strip()
    if escolha_exec:
        try:
            num_exec = int(escolha_exec)
        except ValueError:
            print("  [AVISO] Valor inválido. Usando o padrão de 5 execuções.")
            num_exec = 5
    else:
        num_exec = 5

    prompts   = ['simples', 'avancado']
    codigos   = ['biased', 'clean']

    total = len(scenarios_to_run) * len(prompts) * len(codigos) * num_exec

    print("\n" + "=" * 60)
    print("  SIMULADOR DE PR — GROQ API (Llama 3.3 70B)")
    print("=" * 60)
    print(f"  Cenários selecionados : {', '.join(scenarios_to_run)}")
    print(f"  Total de execuções    : {total}")
    print(f"  Execuções/combinação  : {num_exec}")
    print(f"  Modelo                : {MODELO}")
    print(f"  Limite RPD free tier  : {GROQ_RPD_LIMIT} req/dia")
    print(f"  Resultados em         : {RESULTADOS_CSV}")
    print("=" * 60)

    if os.path.exists(RESULTADOS_CSV):
        with open(RESULTADOS_CSV, mode="r", encoding="utf-8") as f:
            header = f.readline().strip().split(',')
        if "Titulo_PR" not in header:
            backup_name = RESULTADOS_CSV.replace(".csv", "_backup.csv")
            os.rename(RESULTADOS_CSV, backup_name)
            print(f"  [INFO] CSV antigo detectado. Salvo backup em {os.path.basename(backup_name)}")

    if not os.path.exists(RESULTADOS_CSV):
        with open(RESULTADOS_CSV, mode="w", encoding="utf-8", newline="") as f:
            csv.writer(f).writerow([
                "ID_Cenario", "Tipo_Codigo", "Tipo_Prompt",
                "Execucao", "Titulo_PR", "Review_Copilot", "Tempo_Resposta_Segundos"
            ])
        print("  [INFO] Novo CSV criado com header.\n")

    system_prompt = (
        "Você é o robô 'copilot-pull-request-reviewer'. Seu papel é analisar o código fornecido "
        "em uma Pull Request simulada e gerar uma revisão baseando-se estritamente nas "
        "instruções mandatórias especificadas pelo usuário."
    )

    requisicoes_feitas = 0

    for cid in scenarios_to_run:
        for p_type in prompts:
            for c_type in codigos:
                for execucao in range(1, num_exec + 1):

                    # --- CHECKPOINT ---
                    if is_already_completed(cid, c_type, p_type, execucao):
                        print(f"[SKIP] Cenário {cid} | {p_type} | {c_type} | execução: {execucao}/{num_exec} — já concluído.")
                        continue

                    # --- GUARDA DE COTA DIÁRIA ---
                    if requisicoes_feitas >= GROQ_RPD_LIMIT:
                        print("\n" + "=" * 60)
                        print(f"[PAUSA] Limite diário de {GROQ_RPD_LIMIT} requisições atingido.")
                        print("Execute o script novamente amanhã. O checkpoint garante")
                        print("que os cenários já salvos serão pulados automaticamente.")
                        print("=" * 60)
                        return

                    print(f"\n[EXEC] ID-{cid} | prompt: {p_type} | código: {c_type} | execução: {execucao}/{num_exec}")

                    # --- CARREGA INSTRUÇÕES DO PROMPT ---
                    prompt_file = os.path.join(PROMPTS_PATH, p_type, "copilot-instructions.md")
                    if not os.path.exists(prompt_file):
                        print(f"  [ERRO] Arquivo não encontrado: {prompt_file}")
                        continue
                    with open(prompt_file, "r", encoding="utf-8") as f:
                        instructions = f.read().strip()

                    # --- CARREGA CÓDIGO DO CENÁRIO ---
                    code_file = os.path.join(SCENARIOS_ROOT, f"ID-{cid}", f"codigo_{c_type}.js")
                    if not os.path.exists(code_file):
                        print(f"  [ERRO] Arquivo não encontrado: {code_file}")
                        continue
                    with open(code_file, "r", encoding="utf-8") as f:
                        code_content = f.read().strip()

                    code_with_trace = f"{code_content}\n\n// Trace ID: {time.time()}\n"
                    dynamic_filename = get_scenario_filename(code_content)
                    pr_title_neutro = PR_TITLES.get(cid, 'Update')
                    pr_title_rotulado = f"[{cid}] [{p_type}] [{c_type}] - {pr_title_neutro}"

                    user_prompt = f"""=== METADADOS DA PR SIMULADA ===
Título: {pr_title_neutro}
Descrição: Automated safety update.

=== CÓDIGO DA PR ({dynamic_filename}) ===
{code_with_trace}

=== INSTRUÇÕES MANDATÓRIAS (MANDATORY INSTRUCTIONS) ===
{instructions}

=== ESTRUTURA DE RESPOSTA OBRIGATÓRIA ===
Você deve responder exclusivamente no formato abaixo. Não adicione parágrafos livres fora desta estrutura.

Se houver problema de fairness:
- Possível problema de fairness detectado: <Sim ou Não>
- Tipo de preocupação: <group | intersectional | individual | estatistica | social-etica>
- Atributos sensíveis envolvidos: <atributo>
- Local: <classe / função / linha>
- Por que é problemático: <justificativa técnica>
- Sugestão de mitigação / ação: <mitigação técnica>

## Análise de Fairness
<Explicação detalhada sobre o problema de fairness detectado>

Se NÃO houver problema de fairness:
"Nenhuma evidência óbvia de problemas de fairness detectada — recomenda-se revisão manual considerando contexto social."

## Análise de Fairness
<Explique por que o código foi considerado seguro e quais diretrizes de fairness foram validadas>
"""

                    print("  -> Chamando Groq API...")
                    start_time = time.time()

                    max_retries = 3
                    retry_delay = 30
                    review_text = ""
                    elapsed = 0

                    for attempt in range(1, max_retries + 1):
                        try:
                            response = client.chat.completions.create(
                                model=MODELO,
                                messages=[
                                    {"role": "system", "content": system_prompt},
                                    {"role": "user",   "content": user_prompt}
                                ],
                                temperature=0.2,
                                max_tokens=2048,
                            )
                            elapsed = round(time.time() - start_time, 2)
                            review_text = response.choices[0].message.content.strip()

                            if not review_text:
                                raise ValueError("Resposta vazia recebida do modelo.")
                            break

                        except Exception as e:
                            err_str = str(e)
                            if "429" in err_str or "rate_limit" in err_str.lower() or "RateLimitError" in type(e).__name__:
                                print(f"  [!] Rate limit. Aguardando {retry_delay}s... (tentativa {attempt}/{max_retries})")
                                time.sleep(retry_delay)
                                retry_delay = min(retry_delay * 2, 120)
                                start_time = time.time()
                            else:
                                print(f"\n  [ERRO CRÍTICO] {type(e).__name__}: {e}")
                                print("  Abortando para evitar dados corrompidos.")
                                return
                    else:
                        print("\n  [ERRO] Máximo de tentativas esgotado. Execute novamente mais tarde.")
                        return

                    # --- GRAVA NO CSV ---
                    with open(RESULTADOS_CSV, mode="a", encoding="utf-8", newline="") as file:
                        csv.writer(file).writerow([
                            cid, c_type, p_type, execucao, pr_title_rotulado, review_text, elapsed
                        ])

                    requisicoes_feitas += 1

                    # Sleep dinâmico: quanto mais lenta a resposta, mais tokens foram
                    # consumidos — espera proporcionalmente para respeitar o TPM
                    sleep_time = round(SLEEP_MINIMO + (elapsed * SLEEP_POR_SEGUNDO), 1)
                    print(f"  [OK] Concluído em {elapsed}s | Req hoje: {requisicoes_feitas}/{GROQ_RPD_LIMIT} | Aguardando {sleep_time}s...")
                    time.sleep(sleep_time)

    print("\n" + "=" * 60)
    print("  Bateria finalizada com sucesso!")
    print(f"  Total de requisições feitas nesta sessão: {requisicoes_feitas}")
    print("=" * 60)


if __name__ == "__main__":
    run_simulation()