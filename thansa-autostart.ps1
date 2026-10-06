# ============================================================
# Thansa OS - tu khoi dong cung Windows (ban sao cua bin/thansa-autostart.sh ben Mac).
# Goi qua thansa-autostart.bat, dung goi truc tiep tru khi biet minh dang lam gi.
#
# Cach lam: dat mot shortcut trong thu muc Startup cua USER (khong can quyen admin)
# tro vao start-thansa.vbs - dang nhap may la server tu chay NEN, khong bat trinh
# duyet, khong cua so den. Muon mo dashboard thi double-click "Thansa OS.bat".
# ============================================================
param([string]$Action = "status")

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Startup = [Environment]::GetFolderPath("Startup")
$Lnk = Join-Path $Startup "Thansa OS.lnk"
# Shortcut cua may cai TRUOC 1.19 (tro vao start-javis.vbs - nay la file cau noi).
$LnkCu = Join-Path $Startup "JAVIS OS.lnk"

switch ($Action.ToLower()) {
  "install" {
    $vbs = Join-Path $Root "start-thansa.vbs"
    if (-not (Test-Path $vbs)) {
      Write-Host "Khong thay start-thansa.vbs canh script nay - dat thansa-autostart.ps1 o goc thu muc Javis."
      exit 1
    }
    $ws = New-Object -ComObject WScript.Shell
    $s = $ws.CreateShortcut($Lnk)
    $s.TargetPath = "wscript.exe"
    $s.Arguments = "//nologo `"$vbs`""
    $s.WorkingDirectory = $Root
    $s.Description = "Thansa OS - tu chay nen khi dang nhap may"
    $s.Save()
    if (Test-Path $LnkCu) { Remove-Item $LnkCu -Force }
    Write-Host "Da bat tu khoi dong cung Windows."
    Write-Host "Shortcut: $Lnk"
    Write-Host "Go bo: thansa-autostart.bat uninstall"
  }
  "uninstall" {
    if (Test-Path $Lnk) { Remove-Item $Lnk -Force }
    if (Test-Path $LnkCu) { Remove-Item $LnkCu -Force }
    Write-Host "Da tat tu khoi dong cung Windows."
  }
  default {
    if ((Test-Path $Lnk) -or (Test-Path $LnkCu)) {
      Write-Host "DANG bat tu khoi dong (shortcut: $Lnk)."
    } else {
      Write-Host "CHUA bat tu khoi dong. Bat bang: thansa-autostart.bat install"
    }
  }
}
