import requests
import json
import time

COOLIFY_API_KEY = "317|G1_F4DGBXOGO3aS1EXIOPzQZ8wSdQD6FaSEo9OldIoQ"
COOLIFY_URL = "https://deploy.seazone.dev/api/v1"

headers = {
    "Authorization": f"Bearer {COOLIFY_API_KEY}",
    "Content-Type": "application/json",
    "Accept": "application/json"
}

# The deployment UUID returned previously
deployment_uuid = "ii39u2dso1q7ad6j2ma4igik"
app_uuid = "it06ybiity702fi6ndy3j93a"

print("="*60)
print(f"VERIFICANDO DEPLOY: {deployment_uuid}")
print("="*60)

try:
    # Check deployment status
    status_resp = requests.get(
        f"{COOLIFY_URL}/deployments/{deployment_uuid}",
        headers=headers
    )

    if status_resp.status_code == 200:
        data = status_resp.json()
        print(f"Status do Deploy: {data.get('status')}")
    else:
        print(f"Erro ao checar deploy: {status_resp.status_code} - {status_resp.text}")

    # Check application details (to get the generated URL)
    print("\nBuscando a URL da Aplicação...")
    app_resp = requests.get(
        f"{COOLIFY_URL}/applications/{app_uuid}",
        headers=headers
    )

    if app_resp.status_code == 200:
        app_data = app_resp.json()
        fqdn = app_data.get('fqdn')
        if fqdn:
            print(f"✅ URL PÚBLICA GERADA: {fqdn}")
        else:
            print("⚠️ FQDN (URL) ainda não foi configurado pelo Coolify. Gerando um automaticamente...")
            # We can update the app to set a random coolify domain
            fqdn_url = f"https://briefing-bot-acs-{int(time.time())}.deploy.seazone.dev"
            update_resp = requests.patch(
                f"{COOLIFY_URL}/applications/{app_uuid}",
                headers=headers,
                json={"fqdn": fqdn_url}
            )
            if update_resp.status_code == 201 or update_resp.status_code == 200:
                print(f"✅ URL PÚBLICA GERADA: {fqdn_url}")
            else:
                print(f"Erro ao forçar URL: {update_resp.text}")
    else:
        print(f"Erro ao buscar detalhes da app: {app_resp.text}")

except Exception as e:
    print(f"Erro no script: {e}")