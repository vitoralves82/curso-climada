import os
import re # Import regular expressions for more specific replacements

# --- Configuração ---
# Arquivos onde links de "Início/Homepage/Voltar" devem apontar para o dashboard
files_to_dashboard = [
    "climada_module1_updated.html",
    "climada_practice1_updated.html",
    "climada_quiz1_updated.html",
    "climada_resources_updated.html",
]

# Arquivo da página inicial original
main_index_file = "index.html" # O arquivo já renomeado

# Links a serem substituídos nos arquivos_to_dashboard
# Substitui tanto o nome antigo quanto o nome já renomeado para garantir
replacements_in_content_pages = {
    "href=\"climada_course_index.html\"": "href=\"dashboard.html\"",
    "href=\"index.html\"": "href=\"dashboard.html\""
}

# Links a serem substituídos especificamente no main_index_file
# Altera o link do botão "Comece Agora"
replacements_in_main_index = {
     # Alvo: <a href="QUALQUER_COISA_AQUI" class="...bg-yellow-500...">Comece o Curso Agora</a>
     # Usamos regex para encontrar o href dentro dessa tag específica
     r'(<a\s+[^>]*?href=")[^"]*?("[^>]*?class="[^"]*?bg-yellow-500[^"]*?"[^>]*?>\s*Comece o Curso Agora\s*</a>)':
     r'\1dashboard.html\2' # \1 pega a parte antes do href, \2 pega a parte depois
}

# Arquivo do Dashboard (para instruções manuais)
dashboard_file = "dashboard.html"

# --- Fim da Configuração ---

count_total_changes = 0
files_updated_count = 0

print("--- Iniciando Atualização da Navegação ---")

# Função para processar substituições em um arquivo
def process_file(filename, replacements, is_regex=False):
    global count_total_changes, files_updated_count
    if not os.path.exists(filename):
        print(f"AVISO: Arquivo '{filename}' não encontrado. Pulando.")
        return

    print(f"\nProcessando arquivo: '{filename}'")
    changes_in_file = 0
    try:
        with open(filename, 'r', encoding='utf-8') as f_read:
            content = f_read.read()
            original_content = content # Guardar original para comparação

        for search_term, replace_term in replacements.items():
            count_before = 0
            if is_regex:
                # Contagem de correspondências Regex (pode não ser perfeita para todas as regex)
                count_before = len(re.findall(search_term, content))
                new_content_temp = re.sub(search_term, replace_term, content)
            else:
                count_before = content.count(search_term)
                new_content_temp = content.replace(search_term, replace_term)

            if new_content_temp != content:
                print(f"  - Substituindo '{search_term}' por '{replace_term}' ({count_before} ocorrência(s))")
                content = new_content_temp
                changes_in_file += count_before # Use count_before para o log, mesmo que regex substitua diferente

        if content != original_content:
            with open(filename, 'w', encoding='utf-8') as f_write:
                f_write.write(content)
            print(f"  -> Arquivo '{filename}' atualizado.")
            count_total_changes += changes_in_file # Acumula a contagem
            files_updated_count +=1
        else:
            print(f"  -> Nenhuma alteração necessária em '{filename}'.")

    except Exception as e:
        print(f"  ERRO ao processar '{filename}': {e}")

# Processar arquivos de conteúdo (módulos, práticas, etc.)
for fname in files_to_dashboard:
    process_file(fname, replacements_in_content_pages)

# Processar arquivo index.html principal (usando regex)
process_file(main_index_file, replacements_in_main_index, is_regex=True)


print("\n--- Processo Concluído ---")
print(f"Total de arquivos verificados: {len(files_to_dashboard) + 1}")
print(f"Total de arquivos atualizados: {files_updated_count}")
print(f"Total de substituições realizadas (aproximado para regex): {count_total_changes}")

print("\n--- Ações Manuais NECESSÁRIAS ---")
print(f"1. ABRA o arquivo '{dashboard_file}'.")
print(f"2. ENCONTRE a seção `<nav>` dentro da div com a classe `sidebar`.")
print(f"3. ADICIONE um link para a página inicial original (index.html). Sugestão:")
print("""
   <!-- Adicione este link dentro da tag <nav> do sidebar -->
   <a href="index.html" class="sidebar-link">
       <i class="fas fa-flag mr-3"></i>
       <span>Homepage do Curso</span>
   </a>
""")
print(f"4. VERIFIQUE se o link 'Dashboard' no sidebar tem a classe 'active'.")
print(f"5. Salve o arquivo '{dashboard_file}'.")

print("\n--- Próximos Passos ---")
print("1. Verifique as alterações feitas nos arquivos (use 'git diff').")
print("2. Se tudo estiver correto, faça o commit das alterações no Git:")
print("   git add .")
print("   git commit -m \"Update navigation links for dashboard integration\"")
print("   git push")
print("3. Teste a navegação no site publicado após o deploy do GitHub Pages.")
print("-" * 30)