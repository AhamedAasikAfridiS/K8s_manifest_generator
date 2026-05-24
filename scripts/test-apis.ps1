$AuthUrl = if ($env:AUTH_URL) { $env:AUTH_URL } else { "http://localhost:8001" }
$AiUrl = if ($env:AI_URL) { $env:AI_URL } else { "http://localhost:8002" }
$Email = if ($env:TEST_EMAIL) { $env:TEST_EMAIL } else { "devops@example.com" }
$Password = if ($env:TEST_PASSWORD) { $env:TEST_PASSWORD } else { "SecurePass123" }
$Username = if ($env:TEST_USERNAME) { $env:TEST_USERNAME } else { "devopsuser" }

Write-Host "== Health checks =="
Invoke-RestMethod "$AuthUrl/health"
Invoke-RestMethod "$AiUrl/health"

Write-Host "== Register =="
$body = @{ email = $Email; username = $Username; password = $Password } | ConvertTo-Json
try {
    Invoke-RestMethod -Method Post -Uri "$AuthUrl/register" -ContentType "application/json" -Body $body
} catch {
    Write-Host "Register may already exist, continuing..."
}

Write-Host "== Login =="
$login = Invoke-RestMethod -Method Post -Uri "$AuthUrl/login" -ContentType "application/json" -Body $body
$token = $login.access_token
Write-Host "Token acquired"

Write-Host "== Upload test PNG =="
$pngPath = Join-Path $env:TEMP "test-diagram.png"
$bytes = [Convert]::FromBase64String("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==")
[IO.File]::WriteAllBytes($pngPath, $bytes)

$upload = Invoke-RestMethod -Method Post -Uri "$AiUrl/upload-diagram" `
    -Headers @{ Authorization = "Bearer $token" } `
    -Form @{ file = Get-Item $pngPath }

Write-Host "== Generate manifest =="
$genBody = @{ file_id = $upload.file_id; namespace = "production"; app_name = "web-app" } | ConvertTo-Json
$manifest = Invoke-RestMethod -Method Post -Uri "$AiUrl/generate-manifest" `
    -Headers @{ Authorization = "Bearer $token" } `
    -ContentType "application/json" -Body $genBody

Write-Host "manifest_id=$($manifest.manifest_id)"

Write-Host "== Validate manifest =="
$valBody = @{ manifest_id = $manifest.manifest_id } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri "$AiUrl/validate-manifest" `
    -Headers @{ Authorization = "Bearer $token" } `
    -ContentType "application/json" -Body $valBody

Write-Host "API test flow completed."
