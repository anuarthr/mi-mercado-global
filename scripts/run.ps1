$ErrorActionPreference = 'Stop'

Write-Host ""
Write-Host "==> Levantando contenedores (LocalStack + Redis + cdk_env)..." -ForegroundColor Cyan
docker compose up -d
if ($LASTEXITCODE -ne 0) { throw "Falló docker compose up" }

Write-Host ""
Write-Host "==> Esperando a que LocalStack quede healthy..." -ForegroundColor Cyan
$timeout = 60
$start = Get-Date
while ($true) {
    $status = docker compose ps localstack --format json | ConvertFrom-Json
    if ($status.Health -eq 'healthy') {
        Write-Host "    LocalStack listo." -ForegroundColor Green
        break
    }
    if (((Get-Date) - $start).TotalSeconds -gt $timeout) {
        throw "LocalStack no quedó healthy en $timeout segundos"
    }
    Start-Sleep -Seconds 2
}

Write-Host ""
Write-Host "==> Ejecutando deploy (tabla DynamoDB + Lambdas + API Gateway)..." -ForegroundColor Cyan
docker compose run --rm cdk_env bash scripts/deploy.sh
if ($LASTEXITCODE -ne 0) { throw "Falló el deploy" }

Write-Host ""
Write-Host "==> Todo listo. Abre lambda-playground.html y actualiza la Base URL si cambió el API ID." -ForegroundColor Green
