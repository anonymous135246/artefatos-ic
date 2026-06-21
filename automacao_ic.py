import subprocess
import os
import shutil
import time
import json
import csv
from datetime import datetime

# --- CONFIGURAÇÃO DO AMBIENTE ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__)) if '__file__' in globals() else os.getcwd()
REPO_PATH = "/home/ledes11/Documents/IC/testes-automatizados"

if os.path.exists(REPO_PATH):
    os.chdir(REPO_PATH)
else:
    print(f"ATENÇÃO: A pasta {REPO_PATH} não existe. Crie-a ou altere o REPO_PATH no script.")

DATASET_PATH = os.path.join(SCRIPT_DIR, "dataset")
SCENARIOS_ROOT = os.path.join(DATASET_PATH, "cenarios")
PROMPTS_PATH = os.path.join(DATASET_PATH, "prompts")
RESULTADOS_CSV = os.path.join(SCRIPT_DIR, "resultados_pesquisa.csv")
TARGET_FILENAME = "payment_processor.js"

# Número de execuções por combinação (cenário x código x prompt)
NUM_EXECUCOES = 5

# Títulos neutros para Blind Review — novos cenários ID-01 a ID-10
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


class CopilotTimeoutError(Exception):
    """Exceção lançada quando a revisão do Copilot atinge o timeout de polling."""
    pass


def run_command(command, cwd=REPO_PATH, ignore_errors=False):
    result = subprocess.run(command, capture_output=True, text=True, cwd=cwd)
    if result.returncode != 0:
        if ignore_errors: return ""
        if "nothing to commit" in result.stderr or "working tree clean" in result.stderr: return ""
        print(f"Erro ao executar: {' '.join(command)}\nErro: {result.stderr}")
        return None
    return result.stdout.strip()


def commit_if_changed(message):
    res = subprocess.run(['git', 'diff', '--cached', '--quiet'], cwd=REPO_PATH)
    if res.returncode != 0:
        return run_command(["git", "commit", "-m", message])
    return ""


def parse_pr_title(title):
    try:
        # Padrão: [01] [avancado] [biased] - Titulo
        t = title.replace('[', '').replace(']', '')
        parts = t.split(' ')
        return {'id': parts[0], 'prompt': parts[1], 'code': parts[2]}
    except:
        return {'id': 'ERRO', 'prompt': 'ERRO', 'code': 'ERRO'}


def prepare_main_with_prompt(prompt_type):
    print(f"\n--- Preparando branch 'main' com Prompt: {prompt_type} ---")
    run_command(["git", "checkout", "main"], ignore_errors=True)
    run_command(["git", "reset", "--hard", "origin/main"], ignore_errors=True)
    run_command(["git", "clean", "-fd"], ignore_errors=True)
    run_command(["git", "pull", "origin", "main"], ignore_errors=True)

    github_dir = os.path.join(REPO_PATH, ".github")
    if not os.path.exists(github_dir): os.makedirs(github_dir)

    source_prompt = os.path.join(PROMPTS_PATH, prompt_type, "copilot-instructions.md")
    dest_prompt = os.path.join(github_dir, "copilot-instructions.md")
    shutil.copyfile(source_prompt, dest_prompt)

    with open(dest_prompt, "a") as f: f.write(f"\n<!-- Build: {time.time()} -->\n")
    run_command(["git", "add", ".github/copilot-instructions.md"])
    commit_if_changed(f"config: update copilot instructions ({prompt_type})")
    run_command(["git", "push", "origin", "main"])


def inject_scenario(cenario_id, code_type, prompt_type, execucao):
    print(f"--- Injetando Cenário ID {cenario_id} (Código: {code_type} | Execução: {execucao}/{NUM_EXECUCOES}) ---")
    branch_name = f"lab-id-{cenario_id}-{code_type}-exec{execucao}"

    run_command(["git", "checkout", "main"], ignore_errors=True)
    run_command(["git", "branch", "-D", branch_name], ignore_errors=True)
    run_command(["git", "push", "origin", "--delete", branch_name], ignore_errors=True)
    run_command(["git", "checkout", "-b", branch_name])

    source_code = os.path.join(SCENARIOS_ROOT, f"ID-{cenario_id}", f"codigo_{code_type}.js")
    dest_code = os.path.join(REPO_PATH, TARGET_FILENAME)
    shutil.copyfile(source_code, dest_code)
    with open(dest_code, "a") as f: f.write(f"\n// Trace ID: {time.time()}\n")

    run_command(["git", "add", "."])
    commit_if_changed(f"feat: implementation for {PR_TITLES.get(cenario_id, 'System: Operational Update')}")
    run_command(["git", "push", "-u", "origin", branch_name])
    return branch_name


def open_pull_request(branch_name, cenario_id, prompt_type, code_type):
    print(f"--- Abrindo PR Neutra para {branch_name} ---")
    base_title = PR_TITLES.get(cenario_id, 'System: Operational Update')

    # Limpa PRs antigas da mesma branch
    existing = run_command(["gh", "pr", "list", "--head", branch_name, "--json", "number"], ignore_errors=True)
    if existing and existing != "[]":
        pr_num = json.loads(existing)[0]['number']
        run_command(["gh", "pr", "close", str(pr_num)], ignore_errors=True)

    pr_url = run_command(["gh", "pr", "create", "--title", base_title, "--body", "Automated safety update.", "--base", "main", "--head", branch_name])
    if not pr_url: return None, None

    pr_id = pr_url.split("/")[-1]

    # Injetar instruções no comentário
    prompt_file = os.path.join(PROMPTS_PATH, prompt_type, "copilot-instructions.md")
    instructions = ""
    if os.path.exists(prompt_file):
        with open(prompt_file, "r") as f: instructions = f.read().strip()

    local_start = time.time()
    run_command(["gh", "pr", "comment", pr_id, "--body", f"/copilot review\n\n> **Mandatory Instructions:**\n{instructions}"])

    # Busca o timestamp REAL do comentário no GitHub
    time.sleep(2)
    pr_data = run_command(["gh", "pr", "view", pr_id, "--json", "comments"])
    if pr_data:
        try:
            comments = json.loads(pr_data).get("comments", [])
            for c in reversed(comments):
                if "/copilot review" in c.get("body", ""):
                    gh_start_iso = c.get("createdAt")
                    return pr_id, datetime.fromisoformat(gh_start_iso.replace('Z', '+00:00')).timestamp()
        except:
            pass

    return pr_id, local_start


def collect_and_save(pr_id, cenario_id=None, code_type=None, prompt_type=None,
                     is_recollect=False, start_time=None, execucao=None):
    elapsed = 0
    review_text = "TIMEOUT_ERROR"

    if is_recollect:
        print(f"--- Re-coletando dados da PR #{pr_id} ---")
        title = run_command(["gh", "pr", "view", str(pr_id), "--json", "title", "--jq", ".title"])
        meta = parse_pr_title(title)
        cenario_id, prompt_type, code_type = meta['id'], meta['prompt'], meta['code']
        execucao = execucao or 1
    else:
        print("--- Aguardando Copilot Review (Polling) ---")

    for i in range(25):
        if not is_recollect: time.sleep(20)
        res = run_command(["gh", "pr", "view", str(pr_id), "--json", "comments,reviews"])
        res_inline = run_command(["gh", "api", f"repos/gfernandes04/ic-fairness-bench/pulls/{pr_id}/comments"], ignore_errors=True)
        if not res: continue

        data = json.loads(res)
        inline_data = json.loads(res_inline) if res_inline else []
        bot_reviews = [r for r in data.get("reviews", []) if "copilot" in r.get("author", {}).get("login", "").lower()]
        bot_comments = [c for c in data.get("comments", []) if "copilot" in c.get("author", {}).get("login", "").lower()]
        bot_inlines = [ic for ic in inline_data if "copilot" in ic.get("user", {}).get("login", "").lower()]

        if bot_reviews or bot_comments or bot_inlines:
            # Detecta resposta de erro do Copilot e retenta
            all_bodies = (
                [r.get("body", "") for r in bot_reviews]
                + [c.get("body", "") for c in bot_comments]
            )
            if all(
                "encountered an error" in (b or "").lower() or not (b or "").strip()
                for b in all_bodies
            ) and not bot_inlines:
                print(f"  [!] Copilot retornou erro na tentativa {i+1}. Retentando /copilot review...")
                time.sleep(30)
                run_command(["gh", "pr", "comment", pr_id, "--body", "/copilot review"])
                time.sleep(10)
                continue

            all_timestamps = []
            for r in bot_reviews: all_timestamps.append(r.get("createdAt"))
            for c in bot_comments: all_timestamps.append(c.get("createdAt"))
            for ic in bot_inlines: all_timestamps.append(ic.get("createdAt"))
            valid_ts = [ts for ts in all_timestamps if ts]

            temp_text = ""
            for r in bot_reviews:
                if r.get("body"): temp_text += "\n--- OVERVIEW ---\n" + r.get("body") + "\n"
            for c in bot_comments:
                if c.get("body"): temp_text += "\n--- PR COMMENT ---\n" + c.get("body") + "\n"
            if bot_inlines:
                temp_text += "\n--- FAIRNESS ANALYSIS (INLINE) ---\n"
                for ic in bot_inlines: temp_text += f"> {ic.get('body')}\n\n"

            if temp_text.strip():
                review_text = temp_text

                if valid_ts and start_time:
                    earliest_iso = min(valid_ts)
                    gh_time = datetime.fromisoformat(earliest_iso.replace('Z', '+00:00')).timestamp()
                    elapsed = int(gh_time - start_time)
                elif start_time:
                    # createdAt ausente (ex: review de erro) — usa timestamp local do disparo
                    elapsed = int(time.time() - start_time)

                if not is_recollect:
                    full_title = f"[{cenario_id}] [{prompt_type}] [{code_type}] - {PR_TITLES.get(cenario_id, 'Update')}"
                    run_command(["gh", "pr", "edit", str(pr_id), "--title", full_title])
                break

    if review_text == "TIMEOUT_ERROR":
        raise CopilotTimeoutError("Tempo limite esgotado aguardando resposta do Copilot (possível cota/limite atingido).")

    with open(RESULTADOS_CSV, mode="a", encoding="utf-8", newline="") as file:
        csv.writer(file).writerow([cenario_id, code_type, prompt_type, execucao, review_text, elapsed])
    print(f"Resultado salvo! PR #{pr_id} | Execução: {execucao} | Tempo: {elapsed}s")


def teardown_iteration(pr_id, branch_name):
    print("--- Teardown (Clean Slate) ---")
    run_command(["gh", "pr", "close", pr_id, "--delete-branch"], ignore_errors=True)
    run_command(["git", "checkout", "main"])
    run_command(["git", "branch", "-D", branch_name], ignore_errors=True)

    for f in [TARGET_FILENAME, "package.json", ".github"]:
        path = os.path.join(REPO_PATH, f)
        if os.path.exists(path):
            if os.path.isdir(path): shutil.rmtree(path)
            else: os.remove(path)
            run_command(["git", "add", f])

    commit_if_changed("chore: clean slate for next test")
    run_command(["git", "push", "origin", "main"])


def list_available_scenarios():
    available = []
    if os.path.exists(SCENARIOS_ROOT):
        for entry in sorted(os.listdir(SCENARIOS_ROOT)):
            if entry.startswith("ID-"):
                cid = entry.replace("ID-", "")
                available.append(cid)
    return available


def validate_scenario_files(cenario_id, code_type, prompt_type):
    errors = []
    code_path = os.path.join(SCENARIOS_ROOT, f"ID-{cenario_id}", f"codigo_{code_type}.js")
    prompt_path = os.path.join(PROMPTS_PATH, prompt_type, "copilot-instructions.md")
    if not os.path.exists(code_path):
        errors.append(f"Arquivo não encontrado: {code_path}")
    if not os.path.exists(prompt_path):
        errors.append(f"Prompt não encontrado: {prompt_path}")
    return errors

def is_already_completed(cid, c_type, p_type, execucao):
    """Verifica se a combinação já existe no CSV de resultados e não falhou por TIMEOUT_ERROR."""
    if not os.path.exists(RESULTADOS_CSV):
        return False
    try:
        with open(RESULTADOS_CSV, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                csv_cid = row.get("ID_Cenario", "").strip().zfill(2)
                tgt_cid = str(cid).strip().zfill(2)
                csv_c_type = row.get("Tipo_Codigo", "").strip()
                csv_p_type = row.get("Tipo_Prompt", "").strip()
                csv_exec = row.get("Execucao", "").strip()
                csv_review = row.get("Review_Copilot", "").strip()
                
                if (csv_cid == tgt_cid and 
                    csv_c_type == c_type and 
                    csv_p_type == p_type and 
                    csv_exec == str(execucao) and
                    csv_review != "TIMEOUT_ERROR"):
                    return True
    except Exception as e:
        print(f"Erro ao ler CSV de progresso: {e}")
    return False


def run_batch(cenarios, prompts, codigos):
    """Executa uma bateria de testes com NUM_EXECUCOES repetições por combinação."""
    total = len(cenarios) * len(prompts) * len(codigos) * NUM_EXECUCOES
    print(f"\nBateria configurada: {total} execuções totais ({NUM_EXECUCOES}x por combinação)")

    for cid in cenarios:
        for p_type in prompts:
            for c_type in codigos:
                errors = validate_scenario_files(cid, c_type, p_type)
                if errors:
                    print(f"[SKIP] Cenário {cid} / {p_type} / {c_type} — arquivos ausentes:")
                    for e in errors: print(f"  - {e}")
                    continue

                for execucao in range(1, NUM_EXECUCOES + 1):
                    if is_already_completed(cid, c_type, p_type, execucao):
                        print(f"[SKIP] Cenário {cid} / {p_type} / {c_type} exec {execucao} já concluído no CSV.")
                        continue

                    print(f"\n{'='*60}")
                    print(f"Cenário: ID-{cid} | Prompt: {p_type} | Código: {c_type} | Execução: {execucao}/{NUM_EXECUCOES}")
                    print(f"{'='*60}")
                    pr_id, branch = None, None
                    try:
                        prepare_main_with_prompt(p_type)
                        branch = inject_scenario(cid, c_type, p_type, execucao)
                        pr_id, start_time = open_pull_request(branch, cid, p_type, c_type)
                        if pr_id:
                            collect_and_save(pr_id, cid, c_type, p_type,
                                             start_time=start_time, execucao=execucao)
                            teardown_iteration(pr_id, branch)
                    except CopilotTimeoutError as e:
                        print(f"\n[!] ABORTANDO BATERIA: {e}")
                        if pr_id and branch:
                            teardown_iteration(pr_id, branch)
                        raise e
                    except Exception as e:
                        print(f"FALHA na iteração {cid} exec {execucao}: {e}")
                        run_command(["git", "checkout", "main"])


def main():
    global NUM_EXECUCOES, RESULTADOS_CSV
    available = list_available_scenarios()
    print("=== ENGINE DE AUTOMAÇÃO IC ===")
    print(f"Cenários disponíveis: {', '.join(available) if available else 'nenhum'}")
    print(f"Execuções por combinação: {NUM_EXECUCOES}")
    print()
    print("[1] Bateria completa (todos os cenários disponíveis)")
    print("[2] Re-coleta por ID de PR")
    print("[3] Cenário individual (manual)")
    print("[4] Bateria personalizada")
    print("[5] Executar MVP (Todos os cenários disponíveis, 1x cada)")
    choice = input("Opção: ")

    # Inicializa o CSV com header se não existir
    if not os.path.exists(RESULTADOS_CSV):
        with open(RESULTADOS_CSV, mode="w", encoding="utf-8", newline="") as f:
            csv.writer(f).writerow([
                "ID_Cenario", "Tipo_Codigo", "Tipo_Prompt",
                "Execucao", "Review_Copilot", "Tempo_Resposta_Segundos"
            ])

    if choice == "1":
        run_batch(available, ['simples', 'avancado'], ['biased', 'clean'])

    elif choice == "2":
        pr_ids = input("IDs das PRs (separados por vírgula): ")
        exec_num = input("Número da execução para registrar (padrão: 1): ").strip()
        execucao = int(exec_num) if exec_num.isdigit() else 1
        for pid in pr_ids.split(","):
            collect_and_save(pid.strip(), is_recollect=True, execucao=execucao)

    elif choice == "3":
        cid = input("ID do Cenário (ex: 01): ").strip().zfill(2)
        ptype = input("Prompt (simples, avancado ou ambos): ").strip().lower()
        prompts_escolhidos = ['simples', 'avancado'] if ptype == "ambos" else [ptype]
        ctype = input("Código (biased, clean ou ambos): ").strip().lower()
        codigos_escolhidos = ['biased', 'clean'] if ctype == "ambos" else [ctype]
        exec_input = input(f"Número de execuções (padrão: {NUM_EXECUCOES}): ").strip()
        if exec_input.isdigit():
            NUM_EXECUCOES = int(exec_input)
        run_batch([cid], prompts_escolhidos, codigos_escolhidos)

    elif choice == "4":
        print(f"Cenários disponíveis: {', '.join(available)}")
        ids_input = input("IDs dos cenários (separados por vírgula, ex: 01, 02, 03): ")
        cenarios = [c.strip().zfill(2) for c in ids_input.split(",") if c.strip()]
        prompts_input = input("Prompts (simples, avancado ou Enter para ambos): ").strip()
        prompts = [p.strip() for p in prompts_input.split(",") if p.strip()] or ['simples', 'avancado']
        codigos_input = input("Códigos (biased, clean ou Enter para ambos): ").strip()
        codigos = [c.strip() for c in codigos_input.split(",") if c.strip()] or ['biased', 'clean']
        
        exec_input = input(f"Número de execuções (padrão: {NUM_EXECUCOES}): ").strip()
        if exec_input.isdigit():
            NUM_EXECUCOES = int(exec_input)
            
        total = len(cenarios) * len(prompts) * len(codigos) * NUM_EXECUCOES
        print(f"\nBateria: {len(cenarios)} cenários × {len(prompts)} prompts × {len(codigos)} códigos × {NUM_EXECUCOES} execuções = {total} execuções")
        if input("Confirmar? (s/n): ").strip().lower() != "s":
            return
        run_batch(cenarios, prompts, codigos)

    elif choice == "5":
        NUM_EXECUCOES = 1
        RESULTADOS_CSV = os.path.join(SCRIPT_DIR, "rodada_mvp.csv")
        if not os.path.exists(RESULTADOS_CSV):
            with open(RESULTADOS_CSV, mode="w", encoding="utf-8", newline="") as f:
                csv.writer(f).writerow([
                    "ID_Cenario", "Tipo_Codigo", "Tipo_Prompt",
                    "Execucao", "Review_Copilot", "Tempo_Resposta_Segundos"
                ])
        total = len(available) * 2 * 2 * NUM_EXECUCOES
        print(f"\nIniciando MVP: Todos os cenários × simples/avancado × biased/clean × 1 execução = {total} execuções.")
        run_batch(available, ['simples', 'avancado'], ['biased', 'clean'])

    else:
        print("Opção inválida.")


if __name__ == "__main__":
    main()