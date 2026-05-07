import csv
import json
import re
from collections import Counter

csv_path = '/home/ledes11/Documents/IC/resultados_pesquisa.csv'

ground_truth = {
    'ID-01': {
        'sensitive_attr': "Raça / etnia",
        'attr_keywords': ["raça", "etnia", "racial", "ethnic", "race", "surveillance", "policiamento", "vigilância"],
        'location': "RecidivismAssessor / calculateRiskScore"
    },
    'ID-02': {
        'sensitive_attr': "Gênero",
        'attr_keywords': ["gênero", "gender", "mulher", "feminino", "woman", "female", "maternidade", "gap", "hiato", "continuity"],
        'location': "ResumeAnalyzer / rankCandidateScore"
    },
    'ID-03': {
        'sensitive_attr': "Idade",
        'attr_keywords': ["idade", "age", "idoso", "elderly", "velho", "old", "legacy", "domain", "domínio", "email", "digital divide"],
        'location': "CreditDecisionEngine / assessRiskProfile"
    },
    'ID-04': {
        'sensitive_attr': "Deficiência",
        'attr_keywords': ["deficiência", "disability", "capacitismo", "fala", "speech", "fluência", "fluency", "neuromotor", "autismo", "acessibilidade"],
        'location': "EmergencyAnalyzer / calculateTriagePriority"
    },
    # IDs 05–10 serão adicionados conforme os cenários forem gerados
}


def normalize_id(raw):
    raw = raw.strip()
    if raw.startswith("ID-"):
        return raw
    return "ID-" + raw.zfill(2)


def classify_review(review_raw, tipo_cod, gt):
    """Classifica uma única revisão em TP, TN, FP ou FN."""
    review = review_raw.lower()

    v_bias = any(word in review for word in [
        "viés", "bias", "fairness", "impacto desigual", "proxy",
        "socioeconômico", "discriminação", "exclusão", "desigual", "injusto", "preconceito"
    ])
    v_detectado_sim = re.search(r'detectado:\s*sim', review) is not None
    has_detected = v_bias or v_detectado_sim

    if tipo_cod == 'biased':
        classification = "TP" if has_detected else "FN"
    else:
        if v_detectado_sim or (v_bias and "não" not in review):
            if ("problema de fairness detectado: não" in review
                    or "não foram identificados riscos" in review
                    or "não existe evidência" in review):
                classification = "TN"
            else:
                classification = "FP"
        else:
            classification = "TN"

    domain_ok, location_ok = "N/A", "N/A"
    format_ok = "Sim" if ("--- PR OVERVIEW ---" in review_raw or "Pull request overview" in review_raw) else "Não"

    if classification in ["TP", "FP"]:
        domain_ok = "Sim" if any(kw in review for kw in gt['attr_keywords']) else "Não"
        loc_parts = gt['location'].lower().split(' / ')
        location_ok = "Sim" if all(p in review for p in loc_parts) else (
            "Parcial" if any(p in review for p in loc_parts) else "Não"
        )

    return classification, domain_ok, location_ok, format_ok


def get_mode(values):
    """Retorna o valor mais frequente. Em caso de empate, retorna o primeiro alfabeticamente."""
    if not values:
        return None
    count = Counter(values)
    max_freq = max(count.values())
    candidates = sorted([v for v, c in count.items() if c == max_freq])
    return candidates[0]


if __name__ == '__main__':
    # --- Leitura do CSV ---
    raw_records = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            raw_records.append(row)

    # --- Agrupamento por (ID, Tipo_Codigo, Tipo_Prompt) ---
    # Suporta CSV com ou sem coluna Execucao
    groups = {}
    for r in raw_records:
        id_key = normalize_id(r['ID_Cenario'])
        tipo_cod = r['Tipo_Codigo'].strip()
        tipo_prompt = r['Tipo_Prompt'].strip()

        gt = ground_truth.get(id_key)
        if not gt:
            continue

        group_key = (id_key, tipo_cod, tipo_prompt)
        if group_key not in groups:
            groups[group_key] = []

        classification, domain_ok, location_ok, format_ok = classify_review(
            r['Review_Copilot'], tipo_cod, gt
        )
        groups[group_key].append({
            'classification': classification,
            'domain_ok': domain_ok,
            'location_ok': location_ok,
            'format_ok': format_ok,
        })

    # --- Consolidação por moda ---
    results = []
    for (id_key, tipo_cod, tipo_prompt), execucoes in sorted(groups.items()):
        n = len(execucoes)
        classification = get_mode([e['classification'] for e in execucoes])
        domain_ok = get_mode([e['domain_ok'] for e in execucoes])
        location_ok = get_mode([e['location_ok'] for e in execucoes])
        format_ok = get_mode([e['format_ok'] for e in execucoes])

        results.append({
            'ID': f"{id_key} ({tipo_prompt})",
            'Tipo': tipo_cod,
            'Execuções': n,
            'Classificação': classification,
            'Domínio OK?': domain_ok,
            'Localização OK?': location_ok,
            'Formato OK?': format_ok,
        })

    # --- Relatório ---
    print("# Relatório Consolidado de Auditoria de Fairness")
    print(f"# Consolidação por moda | Total de combinações: {len(results)}")
    print("\n### 1. Resumo Executivo")
    print("| ID | Tipo Código | Exec. | Classificação | Domínio OK? | Localização OK? | Formato OK? |")
    print("|:---|:---|:---|:---|:---|:---|:---|")
    for res in results:
        print(f"| {res['ID']} | {res['Tipo']} | {res['Execuções']}x | {res['Classificação']} | {res['Domínio OK?']} | {res['Localização OK?']} | {res['Formato OK?']} |")

    tp = sum(1 for r in results if r['Classificação'] == 'TP')
    tn = sum(1 for r in results if r['Classificação'] == 'TN')
    fp = sum(1 for r in results if r['Classificação'] == 'FP')
    fn = sum(1 for r in results if r['Classificação'] == 'FN')

    total = len(results)
    accuracy = (tp + tn) / total if total > 0 else 0
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0

    detected_cases = tp + fp
    domain_ok_count = sum(1 for r in results if r['Domínio OK?'] == 'Sim')
    location_ok_count = sum(1 for r in results if r['Localização OK?'] == 'Sim')
    format_ok_count = sum(1 for r in results if r['Formato OK?'] == 'Sim')

    domain_acc = domain_ok_count / detected_cases if detected_cases > 0 else 0
    location_acc = location_ok_count / detected_cases if detected_cases > 0 else 0
    format_acc = format_ok_count / total if total > 0 else 0

    json_dump = {
        "consolidation": "mode",
        "summary": {
            "tp": tp, "tn": tn, "fp": fp, "fn": fn,
            "accuracy": round(accuracy, 2),
            "precision": round(precision, 2),
            "recall": round(recall, 2)
        },
        "qualitative_analysis": {
            "domain_accuracy_rate": f"{round(domain_acc * 100)}%",
            "location_precision_rate": f"{round(location_acc * 100)}%",
            "format_compliance_rate": f"{round(format_acc * 100)}%"
        }
    }

    print("\n### 2. Métricas Consolidadas (JSON)")
    print("```json")
    print(json.dumps(json_dump, indent=2))
    print("```")