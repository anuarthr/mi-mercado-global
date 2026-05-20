#   docker compose run --rm cdk_env bash scripts/deploy.sh
# Las variables AWS_* y AWS_ENDPOINT_URL vienen del docker-compose.yml.
set -e

echo "==> Instalando dependencias de las Lambdas en /workspace/lambda/"
pip install -r /workspace/lambda/requirements.txt -t /workspace/lambda/ --quiet

echo "==> Bootstrap CDK (idempotente, no falla si ya estaba hecho)"
cd /workspace/infra
cdk bootstrap aws://000000000000/us-east-1 2>&1 | tail -3 || true

echo "==> Desplegando MiMercadoStack"
cdk deploy --require-approval never

echo ""
echo "==> Deploy terminado. Copia la URL (ApiUrl) al playground."
