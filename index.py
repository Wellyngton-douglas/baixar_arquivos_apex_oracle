import json
import time
import os
from datetime import datetime
from playwright.sync_api import sync_playwright
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError


# Função para ler JSON de arquivo
def ler_json(caminho_arquivo):
    with open(caminho_arquivo, "r", encoding="utf-8") as f:
        return json.load(f)


def login_apex(page, usuario, senha, workspace):
    try:
        page.wait_for_selector("#F4550_P1_COMPANY", timeout=10000)
        page.wait_for_selector("#F4550_P1_USERNAME", timeout=10000)
        page.wait_for_selector("#F4550_P1_PASSWORD", timeout=10000)

        page.fill("#F4550_P1_COMPANY", workspace)
        page.fill("#F4550_P1_USERNAME", usuario)
        page.fill("#F4550_P1_PASSWORD", senha)

        # Clicar no botão pelo ID
        page.click("#B232005500580944564")

        page.wait_for_load_state("networkidle", timeout=10000)

        print("Login realizado com sucesso!")
        return True
    except Exception as e:
        print(f"Erro no login: {e}")
        return False


def resetar_senha_se_necessario(page, senha):
    try:
        # Espera um seletor que indique a página de reset de senha
        page.wait_for_selector("#P68_ENTER_CURRENT_PASSWORD", timeout=5000)

        # Se chegou aqui, significa que tem que resetar a senha
        print("Tela de reset de senha detectada, atualizando senha...")

        # Preencher senha antiga
        page.fill("#P68_ENTER_CURRENT_PASSWORD", senha)
        # Preencher nova senha
        page.fill("#P68_PASSWORD", senha)
        # Confirmar nova senha
        page.fill("#P68_CONFIRM_PASSWORD", senha)

        # Clicar no botão para salvar (ajuste o seletor)
        page.click("#B8156708906870311")

        # Espera a página confirmar o reset (ou redirecionar)
        page.wait_for_load_state("networkidle", timeout=10000)

        print("Senha atualizada com sucesso!")
        return True
    except Exception:
        # Se timeout ou erro, assume que não precisa resetar senha
        print("Tela de reset de senha não detectada, continuando...")
        return False


def clicar_menu(page, codigo):
    try:
        page.wait_for_selector("#a_Header_menu", timeout=10000)

        page.click(f"#a_Header_menu_{codigo}")
        print(f"Cliquei no menu com código a_Header_menu_{codigo}")
        return True
    except Exception as e:
        print(f"Erro ao clicar no menu com código a_Header_menu_{codigo}")
        return False


def clicar_card_por_codigo(page, codigo):
    try:
        # Espera a região da tabela carregar (por classe)
        page.wait_for_selector(".a-IRR-region", timeout=10000)

        locator = page.locator("a.a-AppCards-link").filter(
            has=page.locator(f'div.a-AppCards-info:text("{codigo}")')
        )
        locator.first.click()
        print(f"Cliquei no card com código {codigo}")
        return True
    except Exception as e:
        print(f"Erro ao clicar no card {codigo}: {e}")
        return False


def clicar_card_para_exportar(page, codigo):
    try:
        # Espera a região da tabela carregar (por id)
        page.wait_for_selector("#R74808517252457688", timeout=10000)

        link = page.locator("a.a-ImageNav-link").filter(
            has=page.locator("span.a-ImageNav-label", has_text="Export / Import")
        )
        link.first.click()

        print(f"Cliquei no card com código {codigo}")
        return True
    except Exception as e:
        print(f"Erro ao clicar no card {codigo}: {e}")
        return False


def navegar_para_export_app_telas_lovs(page):
    try:
        print("Iniciando exportação de aplicação/telas/lovs...")
        clicar_menu(page, "0i")

        sucesso = clicar_card_por_codigo(page, 101)

        if sucesso:
            sucesso = clicar_card_para_exportar(page, 101)
            if sucesso:
                page.click("#B45317931133446209")
                return
        return sucesso
    except Exception as e:
        print(f"Erro ao tentar exportar aplicações, telas e lovs")
        return False


def download_arquivo(page, cliente, objeto, id_botao):
    try:
        pasta_destino = "script"
        os.makedirs(pasta_destino, exist_ok=True)

        # Gera nome do arquivo: AAAAMMDDHHMM_nomeCliente_nomeObjetoExportado.sql
        timestamp = datetime.now().strftime("%Y%m%d%H%M")
        nome_arquivo = f"{timestamp}_{cliente}_f{101}_{objeto}.sql"
        caminho_completo = os.path.join(pasta_destino, nome_arquivo)

        with page.expect_download() as download_info:
            page.click(id_botao)

        download = download_info.value
        download.save_as(caminho_completo)
        return True

    except Exception as e:
        print(f"Erro ao tentar exportar aplicações")
        return False


def exportar_app(page, cliente_nome, codigo_app):
    try:
        navegar_para_export_app_telas_lovs(page)

        print(f"Exportando aplicação...{codigo_app}")

        page.wait_for_selector("#FB_FB_EXPORT_FLOW_ID", timeout=10000)

        download_arquivo(page, cliente_nome, codigo_app, "#B6923471041")

    except Exception as e:
        print(f"Erro ao tentar exportar aplicações")


def exportar_tela(page, cliente_nome, tela_ids):
    try:
        navegar_para_export_app_telas_lovs(page)

        print(f"Exportando telas...{tela_ids}")

        page.wait_for_selector('a:has-text("Export Page")', timeout=10000)
        page.click('a:has-text("Export Page")')

        page.wait_for_selector("#P164_MEXPORT_PAGE_ID", timeout=5000)
        select = page.locator("#P164_MEXPORT_PAGE_ID")

        opcoes = select.locator("option").all()
        valores_disponiveis = [op.get_attribute("value") for op in opcoes]

        for tela_id in tela_ids:
            try:
                str_id = str(tela_id)
                if str_id not in valores_disponiveis:
                    print(f"  Tela {tela_id} não encontrada no sistema. Pulando...")
                    continue

                print(f"  Exportando tela {tela_id}...")

                page.wait_for_selector("#P164_MEXPORT_PAGE_ID", timeout=5000)
                page.select_option("#P164_MEXPORT_PAGE_ID", str(tela_id))

                download_arquivo(page, cliente_nome, tela_id, "#B47047810549366053")
            except Exception as e:
                print(f"Erro ao exportar tela {tela_id}: {e}")
                continue

    except Exception as e:
        print(f"Erro ao tentar exportar telas")


def exportar_lov(page, cliente_nome, nome_lovs):
    try:
        navegar_para_export_app_telas_lovs(page)

        print(f"Exportando lovs...{nome_lovs}")

        page.wait_for_selector('a:has-text("Component Export")', timeout=10000)
        page.click('a:has-text("Component Export")')

    except Exception as e:
        print(f"Erro ao tentar exportar lovs")


def exportar_componentes(page, nome_cliente, nomes_componentes):
    try:
        for nome in nomes_componentes:
            navegar_para_export_app_telas_lovs(page)

            print("Iniciando exportação de componentes...")

            page.wait_for_selector('a:has-text("Component Export")', timeout=10000)
            page.click('a:has-text("Component Export")')

            page.wait_for_timeout(5000)
            botao = page.locator("#B207483303013432369")
            if botao.is_visible():
                botao.click()
                page.wait_for_timeout(1000)

            try:
                nome = nome.upper()

                page.fill('input[type="text"]', "")
                page.fill('input[type="text"]', nome)
                page.press('input[type="text"]', "Enter")
                page.wait_for_timeout(1000)

                # Busca todos os <td> da coluna NAME
                tds = page.locator('td[headers="NAME"]')
                count = tds.count()

                encontrado = None
                for i in range(count):
                    texto = tds.nth(i).inner_text().strip()
                    if texto == nome:
                        encontrado = tds.nth(i)
                        break

                if encontrado:
                    print(f" Componente encontrado: {nome}")
                    tr = encontrado.locator("xpath=ancestor::tr")
                    checkbox = tr.locator('input[type="checkbox"]')
                    checkbox.check()

                    page.click("#B205852907944540404")
                    page.click("#B207498113252624579")

                    download_arquivo(page, nome_cliente, nome, "#B210501022616376574")
                else:
                    print(f" Componente '{nome}' não encontrado.")

            except Exception as e:
                print(f"  Erro ao tentar marcar '{nome}': {e}")
                continue

    except Exception as e:
        print(f"❌ Erro ao exportar componentes: {e}")
        return False


def main():
    clientes = ler_json("clientes.json")
    objetos = ler_json("objetos.json")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(accept_downloads=True)

        for cliente_nome, cliente_info in clientes.items():
            print(f"Processando cliente: {cliente_nome}")

            page = context.new_page()
            url = cliente_info.get("url")
            if not url:
                print(f"URL não definida para {cliente_nome}, pulando...")
                continue

            page.goto(url)
            page.wait_for_load_state("load")

            usuario = cliente_info.get("usuario")
            senha = cliente_info.get("senha")
            workspace = cliente_info.get("workspace")

            if not usuario or not senha or not workspace:
                print(
                    f"Usuário, senha ou workspace não definidos para {cliente_nome}, pulando login."
                )
                page.close()
                continue

            sucesso = login_apex(
                page,
                usuario,
                senha,
                workspace,
            )

            if sucesso:
                resetar_senha_se_necessario(page, senha)

                if objetos.get("app"):
                    exportar_app(page, cliente_nome, objetos.get("app"))
                if objetos.get("telas"):
                    exportar_tela(page, cliente_nome, objetos.get("telas"))
                if objetos.get("componentes"):
                    exportar_componentes(page, cliente_nome, objetos.get("componentes"))
                # elif rota == "outros":
                #     print("Iniciando exportação de objetos técnicos (pkg, prc, etc)...")
                #     navegar_para_outros_objetos(page)

                else:
                    print("Nenhum objeto especificado para exportação.")

            elif not sucesso:
                print(f"Falha no login para {cliente_nome}")
                page.close()
                continue

            # Aqui você pode continuar com as outras operações depois do login

            time.sleep(10)

            page.close()

        browser.close()


if __name__ == "__main__":
    main()
