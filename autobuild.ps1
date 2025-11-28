# autobuild.ps1 → Build siêu nhẹ chỉ với Nuitka + UPX

Write-Host "=== REGILAZI - BUILD BẰNG NUITKA ===" -ForegroundColor Cyan
Write-Host "Đang build... vui lòng chờ!" -ForegroundColor Yellow

# Tạo thư mục dist nếu chưa có
if (!(Test-Path "dist")) { New-Item -ItemType Directory -Path "dist" | Out-Null }

# Lệnh build Nuitka
& python -m nuitka `
  --standalone `
  --onefile `
  --enable-plugin=pyside6 `
  --windows-disable-console `
  --windows-icon-from-ico=icon.ico `
  --assume-yes-for-downloads `
  --clang `
  --lto=yes `
  --jobs=12 `
  --windows-product-name="Regilazi" `
  --windows-file-description="Regilazi - Laser Control Software" `
  --windows-product-version=1.0.0 `
  --output-dir=dist `
  --output-filename=Regilazi.exe `
  main.py

if ($LASTEXITCODE -eq 0) {
    Write-Host "`nBuild thành công!" -ForegroundColor Green

    # Nén UPX nếu có
    if (Test-Path "upx.exe") {
        Write-Host "Đang nén UPX..." -ForegroundColor Yellow
        .\upx.exe --best --lzma dist/Regilazi.exe
    } else {
        Write-Host "Không tìm thấy upx.exe → bỏ qua nén." -ForegroundColor DarkYellow
    }

    $size = "{0:N2}" -f ((Get-Item "dist/Regilazi.exe").Length / 1MB)
    Write-Host "`nHoàn tất!" -ForegroundColor Cyan
    Write-Host "File output: dist\Regilazi.exe   |   Size: $size MB" -ForegroundColor Green
    Invoke-Item dist
} else {
    Write-Host "`nBuild thất bại! Kiểm tra lỗi phía trên." -ForegroundColor Red
}

Read-Host "Nhấn Enter để thoát"
