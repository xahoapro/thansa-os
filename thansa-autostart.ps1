# ============================================================
# Thansa OS - tu khoi dong cung Windows (ban sao cua bin/thansa-autostart.sh ben Mac).
# Goi qua thansa-autostart.bat, dung goi truc tiep tru khi biet minh dang lam gi.
#
# Cach lam (0.306.0): ghi DUNG muc ma dashboard bat/tat (HKCU\...\Run, ten "ThansaOS",
# khong can quyen admin), tro vao `wscript start-thansa.vbs /open`: dang nhap may la server
# tu chay NEN roi tu mo dashboard trong cua so rieng. install.ps1 goi file nay mac dinh.
# Truoc 0.306.0 file nay dat shortcut trong thu muc Startup, con dashboard ghi Run key: hai
# muc cung bat thi luc dang nhap hai ban gianh nhau cong 7777. Gio chi con Run key,
# shortcut cu bi xoa khi install/uninstall.
# ============================================================
param([string]$Action = "status")

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Startup = [Environment]::GetFolderPath("Startup")
$Lnk = Join-Path $Startup "Thansa OS.lnk"         # muc cu (truoc 0.306.0), chi de don
$LnkCu = Join-Path $Startup "JAVIS OS.lnk"        # shortcut cua may cai truoc Thansa 1.19
$RunKey = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run"
$Approved = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\Run"
$Name = "ThansaOS"                                 # khop _AUTOSTART_NAME trong server/main.py
$NameCu = "JavisOS"                               # muc cua may cai truoc Thansa 1.19, chi de don

switch ($Action.ToLower()) {
  "install" {
    $vbs = Join-Path $Root "start-thansa.vbs"
    if (-not (Test-Path $vbs)) {
      Write-Host "Khong thay start-thansa.vbs canh script nay - dat thansa-autostart.ps1 o goc thu muc Thansa."
      exit 1
    }
    # Cung chuoi voi _autostart_command() trong server/main.py, de dashboard bao "Bat" chu khong bao "duong dan cu".
    $cmd = "wscript.exe //nologo `"$vbs`" /open"
    if (-not (Test-Path $RunKey)) { New-Item -Path $RunKey -Force | Out-Null }
    Set-ItemProperty -Path $RunKey -Name $Name -Value $cmd
    # Task Manager tat muc nay bang mot co rieng; bat lai thi go co do (giong nut trong dashboard).
    try {
      $raw = (Get-ItemProperty -Path $Approved -Name $Name -ErrorAction Stop).$Name
      if ($raw -and ($raw[0] -band 1)) {
        Set-ItemProperty -Path $Approved -Name $Name -Value ([byte[]](2,0,0,0,0,0,0,0,0,0,0,0))
      }
    } catch { }
    if (Test-Path $Lnk) { Remove-Item $Lnk -Force }
    if (Test-Path $LnkCu) { Remove-Item $LnkCu -Force }
    # Hai muc Run cung bat thi luc dang nhap hai ban gianh nhau cong 7777.
    Remove-ItemProperty -Path $RunKey -Name $NameCu -ErrorAction SilentlyContinue
    Write-Host "Da bat tu khoi dong cung Windows: dang nhap may la Thansa tu chay va tu mo dashboard."
    Write-Host "Tat: thansa-autostart.bat uninstall (hoac nut trong dashboard, trang Cai dat)."
  }
  "uninstall" {
    Remove-ItemProperty -Path $RunKey -Name $Name -ErrorAction SilentlyContinue
    Remove-ItemProperty -Path $RunKey -Name $NameCu -ErrorAction SilentlyContinue
    if (Test-Path $Lnk) { Remove-Item $Lnk -Force }
    if (Test-Path $LnkCu) { Remove-Item $LnkCu -Force }
    Write-Host "Da tat tu khoi dong cung Windows."
  }
  default {
    $val = (Get-ItemProperty -Path $RunKey -Name $Name -ErrorAction SilentlyContinue).$Name
    if ($val) {
      Write-Host "DANG bat tu khoi dong: $val"
    } elseif (Test-Path $Lnk) {
      Write-Host "DANG bat theo kieu cu (shortcut $Lnk). Chay thansa-autostart.bat install de len kieu moi."
    } else {
      Write-Host "CHUA bat tu khoi dong. Bat bang: thansa-autostart.bat install"
    }
  }
}
