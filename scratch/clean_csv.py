import re
import csv
import io

input_file = '/home/ledes11/Documents/IC/resultados_pesquisa.csv'
output_file = '/home/ledes11/Documents/IC/resultados_pesquisa_limpo.csv'

with open(input_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()

header = lines[0].strip()
content = "".join(lines[1:])

# Regex explanation:
# Group 1: ID (digits)
# Group 2: Tipo_Codigo (biased|clean)
# Group 3: Tipo_Prompt (simples|avancado)
# Group 4: Review (everything between the start quote and the end quote-comma-time pattern)
# Group 5: Time (digits)
# Note: This pattern assumes records are separated by what looks like a new valid record start.
pattern = re.compile(r'^(\d+),(biased|clean|avancado),(simples|avancado),"(.*?)"\,(\d+)', re.DOTALL | re.MULTILINE)

matches = pattern.findall(content)

clean_records = []
for m in matches:
    clean_records.append({
        'ID_Cenario': m[0],
        'Tipo_Codigo': m[1],
        'Tipo_Prompt': m[2],
        'Review_Copilot': m[3],
        'Tempo_Resposta_Segundos': m[4]
    })

# Write to a new clean CSV using standard csv module to ensure proper quoting
with open(output_file, 'w', encoding='utf-8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['ID_Cenario', 'Tipo_Codigo', 'Tipo_Prompt', 'Review_Copilot', 'Tempo_Resposta_Segundos'])
    writer.writeheader()
    writer.writerows(clean_records)

print(f"Limpeza concluída. {len(clean_records)} registros válidos extraídos.")
print(f"Arquivo salvo em: {output_file}")
