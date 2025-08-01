
# Download de Arquivos Oracle APEX Versão 1.0

Módulo de automação para download de aplicação, compeonentes, triggers, procedures, etc...


## Instalação

Para que a automação possa acontecer é necessário ter [Python](https://python.org.br/instalacao-windows/), após instalado e configurado realizar os seguintes passos:

1. Clone o repositório:

    ```bash
    https://github.com/Wellyngton-douglas/baixar_arquivos_apex_oracle.git
    ```

2. Navegue até a pasta onde o projeto foi clonado:

    ```bash
    cd nome_pasta
    ```

3. Crie a máquina virtual python:

    ```bash
    python -m venv venv
    ```

4. Acessando a máquina virtual python:

    > **Windows**: `.\venv\Scripts\Activate`
    **Linux**: `source nome_do_env/bin/activate`

5. Comando para sair da máquina virtual python:

    > **Windows**: `.\venv\Scripts\Deactivate`
    **Linux**: `source nome_do_env/bin/deactivate`

6. Instale as deppendências:

    ```bash
    pip install -r requirements.txt
    ```

### clientes.json

Crie um arquivo chamado clientes.json com base no clientes.example.json e preencha com os clientes que deseja realizar a exportação dos arquivos. Exemplo:
```json
{
    "cliente1": {
        "workspace": "root",
        "usuario": "root",
        "senha": "root@123",
        "url": "https://meudominio.com.br/....."
    },
}
```

### objetos.json

Crie um arquivo chamado objetos.json com base no objetos.example.json e preencha com as informações que deseja realizar a exportação. Exemplo:
```json
{
    "app": "1",
    "telas": ["1"],
    "componentes": ["lov_usuario"],
    "pkg": ["pkg_cria_usuario"],
    "prc": ["prc_acesso_usuario"],
    "trg": ["trg_usuario_auditoria"],
    "view": ["vw_usuario_excluido"],
    "fnc": ["fnc_inutiliza_usuario"]
}
```

## Executar

```
python index.py
```