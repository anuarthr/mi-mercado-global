$ErrorActionPreference = 'Stop'

Write-Host ""
Write-Host "==> Levantando contenedores (LocalStack + Redis + cdk_env)..." -ForegroundColor Cyan
docker compose up -d
if ($LASTEXITCODE -ne 0) { throw "Falló docker compose up" }

Write-Host ""
Write-Host "==> Esperando a que LocalStack quede healthy..." -ForegroundColor Cyan
$timeout = 90
$start = Get-Date
while ($true) {
    $health = (docker inspect --format "{{.State.Health.Status}}" ministack_local 2>$null) | Out-String
    $health = $health.Trim()
    if ($health -eq 'healthy') {
        Write-Host "    LocalStack listo." -ForegroundColor Green
        break
    }
    if (((Get-Date) - $start).TotalSeconds -gt $timeout) {
        throw "LocalStack no quedó healthy en $timeout segundos (último estado: '$health')"
    }
    Start-Sleep -Seconds 2
}

Write-Host ""
Write-Host "==> Ejecutando deploy (tabla DynamoDB + Lambdas + API Gateway)..." -ForegroundColor Cyan
docker compose run --rm cdk_env bash scripts/deploy.sh 2>&1 | Tee-Object -Variable deployOutput
if ($LASTEXITCODE -ne 0) { throw "Falló el deploy" }

Write-Host ""
Write-Host "==> Inyectando URL del API en el playground..." -ForegroundColor Cyan
try {
    # CDK imprime una línea tipo:
    #   MiMercadoStack.ApiUrl = https://<apiId>.execute-api.localhost.localstack.cloud:4566/prod/
    $apiId = $null
    foreach ($line in $deployOutput) {
        if ("$line" -match 'MiMercadoStack\.ApiUrl\s*=\s*https?://([a-z0-9]+)\.execute-api') {
            $apiId = $Matches[1]
            break
        }
    }
    if (-not $apiId) { throw "No se encontró 'MiMercadoStack.ApiUrl' en el output del deploy" }

    # Usamos la forma HTTP alternativa (no la canónica HTTPS) para evitar el
    # cert autofirmado de LocalStack que el navegador rechaza.
    $baseUrl  = "http://localhost:4566/restapis/$apiId/prod/_user_request_"
    $htmlPath = Join-Path $PSScriptRoot '..\lambda-playground.html'
    $html     = Get-Content -Raw $htmlPath
    $newHtml  = $html -replace '(<input id="base-url-input" value=")[^"]*(")', "`$1$baseUrl`$2"
    Set-Content -Path $htmlPath -Value $newHtml -NoNewline

    Write-Host "    API ID:   $apiId" -ForegroundColor Green
    Write-Host "    Base URL: $baseUrl" -ForegroundColor Green
    Write-Host "    Inyectada en lambda-playground.html" -ForegroundColor Green
} catch {
    Write-Host "    No se pudo inyectar la URL automáticamente: $_" -ForegroundColor Yellow
    Write-Host "    Pega la URL del API manualmente en el playground." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "==> Todo listo. Abre lambda-playground.html." -ForegroundColor Green
