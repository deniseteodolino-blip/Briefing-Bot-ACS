import os
import requests
import json
import time
from dotenv import load_dotenv

load_dotenv()

COOLIFY_API_KEY = "317|G1_F4DGBXOGO3aS1EXIOPzQZ8wSdQD6FaSEo9OldIoQ"
COOLIFY_URL = "https://deploy.seazone.dev/api/v1"

headers = {
    "Authorization": f"Bearer {COOLIFY_API_KEY}",
    "Content-Type": "application/json",
    "Accept": "application/json"
}

def create_application():
    print("Obtendo projetos...")
    # First, get a project
    projects_resp = requests.get(f"{COOLIFY_URL}/projects", headers=headers)

    if projects_resp.status_code != 200:
        print(f"Erro ao obter projetos: {projects_resp.text}")
        return None

    projects = projects_resp.json()
    if not projects:
        print("Nenhum projeto encontrado. Criando um...")
        proj_resp = requests.post(
            f"{COOLIFY_URL}/projects",
            headers=headers,
            json={"name": "Briefing Bot", "description": "ACS Briefing Bot Hackathon"}
        )
        project_uuid = proj_resp.json().get('uuid')

        # Create environment
        env_resp = requests.post(
            f"{COOLIFY_URL}/projects/{project_uuid}/environments",
            headers=headers,
            json={"name": "production"}
        )
        env_name = "production"
    else:
        project_uuid = projects[0]['uuid']
        envs = projects[0].get('environments', [])
        if not envs:
            env_resp = requests.post(
                f"{COOLIFY_URL}/projects/{project_uuid}/environments",
                headers=headers,
                json={"name": "production"}
            )
            env_name = "production"
        else:
            env_name = envs[0]['name']

    print(f"Projeto: {project_uuid} | Ambiente: {env_name}")

    print("\nObtendo servidores...")
    servers_resp = requests.get(f"{COOLIFY_URL}/servers", headers=headers)
    server_uuid = servers_resp.json()[0]['uuid']
    print(f"Servidor: {server_uuid}")

    print("\nObtendo GitHub App / Source...")
    sources_resp = requests.get(f"{COOLIFY_URL}/sources", headers=headers)
    github_app_uuid = None
    try:
        sources_data = sources_resp.json()
        if isinstance(sources_data, list) and len(sources_data) > 0:
            github_app_uuid = sources_data[0]['uuid']
        elif isinstance(sources_data, dict) and 'data' in sources_data and len(sources_data['data']) > 0:
            github_app_uuid = sources_data['data'][0]['uuid']
    except Exception as e:
        print(f"Não foi possível obter fontes do GitHub: {e}, dados: {sources_resp.text}")
    print(f"GitHub App: {github_app_uuid}")

    print("\nCriando aplicação...")
    app_data = {
        "project_uuid": project_uuid,
        "environment_name": env_name,
        "server_uuid": server_uuid,
        "github_app_uuid": github_app_uuid,
        "repository": "deniseteodolino-blip/Briefing-Bot-ACS",
        "branch": "main",
        "build_pack": "dockercompose",
        "ports_exposes": "8501",
        "is_static": False
    }

    app_resp = requests.post(
        f"{COOLIFY_URL}/applications/github",
        headers=headers,
        json=app_data
    )

    if app_resp.status_code not in (200, 201):
        print(f"Erro ao criar aplicação: {app_resp.text}")

        # Let's try public github if github app fails
        print("\nTentando via Public GitHub...")
        public_app_data = {
            "project_uuid": project_uuid,
            "environment_name": env_name,
            "server_uuid": server_uuid,
            "git_repository": "https://github.com/deniseteodolino-blip/Briefing-Bot-ACS",
            "git_branch": "main",
            "build_pack": "dockerfile",
            "ports_exposes": "8501",
            "name": "Briefing Bot ACS"
        }

        app_resp = requests.post(
            f"{COOLIFY_URL}/applications/public",
            headers=headers,
            json=public_app_data
        )

        if app_resp.status_code not in (200, 201):
            print(f"Erro ao criar aplicação pública: {app_resp.text}")
            return None

    app_uuid = app_resp.json().get('uuid')
    print(f"Aplicação criada! UUID: {app_uuid}")

    print("\nConfigurando variáveis de ambiente...")
    envs_to_set = [
        {"name": "SUPABASE_URL", "value": os.getenv("SUPABASE_URL"), "is_build_time": False},
        {"name": "SUPABASE_KEY", "value": os.getenv("SUPABASE_KEY"), "is_build_time": False},
        {"name": "ANTHROPIC_API_KEY", "value": os.getenv("ANTHROPIC_API_KEY"), "is_build_time": False},
        {"name": "SLACK_BOT_TOKEN", "value": os.getenv("SLACK_BOT_TOKEN"), "is_build_time": False},
        {"name": "SLACK_USER_ID", "value": os.getenv("SLACK_USER_ID"), "is_build_time": False}
    ]

    for env in envs_to_set:
        if env["value"]:
            requests.post(
                f"{COOLIFY_URL}/applications/{app_uuid}/envs",
                headers=headers,
                json=env
            )

    # Deploy!
    print("\nIniciando Deploy...")
    deploy_resp = requests.post(
        f"{COOLIFY_URL}/applications/{app_uuid}/start",
        headers=headers
    )

    print(f"Status Deploy: {deploy_resp.status_code}")
    print(deploy_resp.json())

    return app_uuid

if __name__ == "__main__":
    create_application()