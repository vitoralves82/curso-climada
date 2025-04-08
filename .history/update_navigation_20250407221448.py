import os
import re

# --- Configuração ---
# Arquivos onde a navegação principal pode ter sido alterada
all_html_files = [
    "index.html",
    "dashboard.html",
    "climada_module1_updated.html",
    "climada_practice1_updated.html",
    "climada_quiz1_updated.html",
    "climada_resources_updated.html",
]

# Mapeamento correto dos links de conteúdo
# Chave: Nome do arquivo de destino
# Valor: Padrão de texto no link que DEVE apontar para essa chave
correct_content_links = {
    "climada_module1_updated.html": [r"Módulo 1", r"Iniciar Módulo 1", r"Fundamentos"],
    "climada_practice1_updated.html": [r"Prática 1", r"Ir para Prática 1", r"Instalação"],
    "climada_quiz1_updated.html": [r"Quiz (do|do Módulo|Módulo) 1", r"Fazer Quiz"],
    "climada_resources_updated.html": [r"Recursos", r"Complementares"],
    # Adicione outros mapeamentos se necessário
}

# Links que DEVEM apontar para o dashboard (em arquivos que NÃO são o dashboard)
dashboard_link_texts = [
    r"Início", r"Homepage", r"Meu Dashboard", r"Voltar ao Dashboard", r"Página Inicial"
]

# Links que DEVEM apontar para a homepage original (index.html) (Principalmente no Dashboard)
homepage_link_texts = [
    r"Homepage do Curso", r"Sobre o Curso", r"Visão Geral Curso"
]


# Botões "Comece Agora" no index.html devem ir para dashboard
start_button_regex = r'(<a\s+[^>]*?href=")[^"]*?("[^>]*?class="[^"]*?bg-yellow-500[^"]*?"[^>]*?>\s*Comece o Curso Agora\s*</a>)'
start_button_target = "dashboard.html"

# --- Fim da Configuração ---

count_total_changes = 0
files_updated_count = 0

print("--- Iniciando Correção da Navegação ---")

# Função auxiliar para encontrar e substituir href baseado no texto do link
def replace_href_by_link_text(content, link_texts_regex, target_href):
    modified = False
    original_content = content
    for text_pattern in link_texts_regex:
        # Regex para encontrar <a href="QUALQUER_COISA">TEXTO_PADRÃO</a>
        # CUIDADO: Regex simples, pode falhar em casos complexos de HTML aninhado
        regex = r'(<a\s+[^>]*?href=")[^"]*?("[^>]*?>\s*(?:<i.*?</i>\s*)?' + text_pattern + r'\s*(?:<i.*?</i>\s*)?</a>)'
        # \s* para espaços, (?:<i...)? opcionalmente captura ícones antes/depois
        try:
            # Usa uma função lambda para substituir apenas o grupo 1 (o href)
            # Mas verifica se o href já está correto antes de substituir
            def replacer(match):
                nonlocal modified
                prefix = match.group(1)
                current_href = re.search(r'href="([^"]*)"', match.group(0)).group(1) # Extrai href atual
                suffix = match.group(2)
                if current_href != target_href:
                    modified = True
                    # print(f"      Substituindo href='{current_href}' por href='{target_href}' para texto '{text_pattern}'")
                    return f'{prefix}{target_href}{suffix}'
                else:
                    return match.group(0) # Retorna o original se já estiver correto

            content = re.sub(regex, replacer, content, flags=re.IGNORECASE | re.DOTALL)

        except Exception as e:
            print(f"      Erro no regex '{regex}': {e}")

    if modified:
         return content, (content != original_content) # Retorna conteúdo e se mudou
    else:
         return original_content, False

# Processa cada arquivo
for filename in all_html_files:
    if not os.path.exists(filename):
        print(f"AVISO: Arquivo '{filename}' não encontrado. Pulando.")
        continue

    print(f"\nProcessando arquivo: '{filename}'")
    made_changes = False
    try:
        with open(filename, 'r', encoding='utf-8') as f_read:
            content = f_read.read()
            original_content = content

        # 1. Corrigir links para CONTEÚDO (Módulos, Práticas, etc.)
        for target_file, text_patterns in correct_content_links.items():
            content, changed = replace_href_by_link_text(content, text_patterns, target_file)
            if changed: made_changes = True

        # 2. Corrigir links para DASHBOARD (exceto no próprio dashboard)
        if filename != "dashboard.html":
            content, changed = replace_href_by_link_text(content, dashboard_link_texts, "dashboard.html")
            if changed: made_changes = True

        # 3. Corrigir links para HOMEPAGE ORIGINAL (index.html) (Principalmente no dashboard)
        # (Isso pode reverter algumas substituições do passo 2 se o texto for ambíguo,
        # por isso é importante ter textos distintos ou fazer manualmente no dashboard)
        content, changed = replace_href_by_link_text(content, homepage_link_texts, "index.html")
        if changed: made_changes = True

        # 4. Corrigir botões "Comece Agora" no index.html
        if filename == "index.html":
             new_content_temp = re.sub(start_button_regex, rf'\1{start_button_target}\2', content)
             if new_content_temp != content:
                 print(f"  - Corrigindo href dos botões 'Comece o Curso Agora' para '{start_button_target}'")
                 content = new_content_temp
                 made_changes = True

        # 5. Caso ESPECIAL: No dashboard, o link 'Curso CLIMADA' ou 'Visão Geral Curso' deve ir para index.html
        if filename == "dashboard.html":
             content, changed = replace_href_by_link_text(content, [r"Curso CLIMADA", r"Visão Geral Curso"], "index.html")
             if changed: made_changes = True


        # Salvar se houve alterações
        if made_changes:
            with open(filename, 'w', encoding='utf-8') as f_write:
                f_write.write(content)
            print(f"  -> Arquivo '{filename}' atualizado.")
            files_updated_count += 1
            count_total_changes += 1 # Contando arquivos modificados, não substituições exatas
        else:
            print(f"  -> Nenhuma alteração necessária em '{filename}'.")

    except Exception as e:
        print(f"  ERRO ao processar '{filename}': {e}")

print("\n--- Processo Concluído ---")
print(f"Total de arquivos verificados: {len(all_html_files)}")
print(f"Total de arquivos atualizados: {files_updated_count}")

print("\n--- Verificação Manual RECOMENDADA ---")
print("1. ABRA os arquivos modificados e VERIFIQUE os links na barra de navegação, rodapé e botões principais.")
print("2. NO DASHBOARD (`dashboard.html`):")
print("   - Certifique-se de que há um link claro para a HOMEPAGE original (`index.html`).")
print("   - Certifique-se de que há links para iniciar/continuar o curso (ex: para `climada_module1_updated.html`). Verifique a seção 'Visão Geral do Curso' ou adicione um botão 'Iniciar Curso'.")
print("3. NAS PÁGINAS DE CONTEÚDO (Módulos, Práticas, etc.):")
print("   - Certifique-se de que o link 'Início' ou 'Dashboard' aponta para `dashboard.html`.")
print("   - Certifique-se de que links para outros módulos/práticas apontam para os arquivos corretos.")
print("4. NA PÁGINA INICIAL (`index.html`):")
print("   - Certifique-se de que os botões 'Comece o Curso Agora' apontam para `dashboard.html`.")

print("\n--- Próximos Passos ---")
print("1. Use 'git diff' para ver as mudanças exatas.")
print("2. Se correto, faça o commit:")
print("   git add .")
print("   git commit -m \"Fix navigation links to prevent loop and ensure content access\"")
print("   git push")
print("3. Teste exaustivamente a navegação no site publicado.")
print("-" * 30)
