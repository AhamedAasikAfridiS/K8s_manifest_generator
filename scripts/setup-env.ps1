$RootDir = Split-Path -Parent $PSScriptRoot

function Copy-IfMissing($Source, $Dest) {
    if (-not (Test-Path $Dest)) {
        Copy-Item $Source $Dest
        Write-Host "Created $Dest"
    } else {
        Write-Host "Exists $Dest (skipped)"
    }
}

Copy-IfMissing "$RootDir\.env.example" "$RootDir\.env"
Copy-IfMissing "$RootDir\authservice\.env.example" "$RootDir\authservice\.env"
Copy-IfMissing "$RootDir\ai-agent-service\.env.example" "$RootDir\ai-agent-service\.env"
Copy-IfMissing "$RootDir\frontend\.env.example" "$RootDir\frontend\.env"

Write-Host "Environment files are ready."
