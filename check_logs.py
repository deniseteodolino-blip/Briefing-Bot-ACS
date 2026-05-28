import requests
import json

COOLIFY_API_KEY = "317|G1_F4DGBXOGO3aS1EXIOPzQZ8wSdQD6FaSEo9OldIoQ"
COOLIFY_URL = "https://deploy.seazone.dev/api/v1"

headers = {
    "Authorization": f"Bearer {COOLIFY_API_KEY}",
    "Content-Type": "application/json",
    "Accept": "application/json"
}

app_uuid = "it06ybiity702fi6ndy3j93a"

print("="*60)
print(f"VERIFICANDO LOGS DA APLICAÇÃO: {app_uuid}")
print("="*60)

try:
    # Get deployment logs
    deployment_uuid = "ii39u2dso1q7ad6j2ma4igik"
    logs_resp = requests.get(
        f"{COOLIFY_URL}/deployments/{deployment_uuid}",
        headers=headers
    )

    if logs_resp.status_code == 200:
        data = logs_resp.json()
        print(f"Status atual: {data.get('status')}")

        logs = data.get('logs', '')
        if isinstance(logs, str):
            lines = logs.split('\n')
            print("\nÚLTIMAS 20 LINHAS DO DEPLOY:")
            for line in lines[-20:]:
                print(line)
        elif isinstance(logs, list):
            print("\nÚLTIMAS 20 LINHAS DO DEPLOY:")
            for log in logs[-20:]:
                if isinstance(log, dict):
                    print(log.get('log', ''))
                else:
                    print(log)
        else:
            print("Nenhum log de deploy retornado.")
            print("Payload:", json.dumps(data)[:200])

except Exception as e:
    print(f"Erro: {e}")