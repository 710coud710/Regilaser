# Path tới file service.json trong AppData
$serviceFile = "$env:APPDATA\Regilazi\service.json"

if (Test-Path $serviceFile) {
    try {
        $json = Get-Content $serviceFile | ConvertFrom-Json

        if ($json.action -eq "restart" -and $json.app_path) {
            # Lấy tên process từ đường dẫn exe
            $exeName = Split-Path $json.app_path -Leaf
            if ($exeName.EndsWith(".exe")) {
                $exeName = $exeName.Substring(0, $exeName.Length - 4)
            }

            # Kill process nếu đang chạy
            $proc = Get-Process -Name $exeName -ErrorAction SilentlyContinue
            if ($proc) {
                Write-Host "Killing process $($proc.Name)..."
                Stop-Process -Id $proc.Id -Force
            }

            # Start lại app
            Write-Host "Starting $($json.app_path)..."
            Start-Process $json.app_path

            # Xóa file JSON sau khi thực hiện xong
            Remove-Item $serviceFile -Force
            Write-Host "Restart completed."
        }
    }
    catch {
        Write-Host "error reading JSON or restarting app: $_"
    }
}
