# Waits until no other builds are running on this machine (never kills foreign processes).
# Exit codes: 0 - confirmed no builds; 2 - failed to list processes; 3 - timeout reached.
# Example: powershell -NoProfile -File <path>\wait-builds.ps1 -ExtraNames node,cargo
param(
  [string[]]$ExtraNames = @(),   # extra project build tools (process names without .exe)
  [int]$IntervalSeconds = 30,    # poll interval
  [int]$TimeoutSeconds = 0       # 0 = wait without limit
)

$names = @('UnrealBuildTool','MSBuild','cl','link','lld-link','xgConsole','BuildConsole','AutomationTool','ninja','cmake','gradle','xcodebuild') +
  @($ExtraNames | ForEach-Object { "$_".Trim() -replace '\.exe$', '' } | Where-Object { $_ })
$deadline = if ($TimeoutSeconds -gt 0) { (Get-Date).AddSeconds($TimeoutSeconds) } else { $null }

while ($true) {
  try {
    $procs = @(Get-CimInstance Win32_Process -ErrorAction Stop)
  } catch {
    "{0:HH:mm:ss} error: cannot list processes: {1}" -f (Get-Date), $_.Exception.Message
    exit 2
  }
  if ($procs.Count -eq 0) {
    "{0:HH:mm:ss} error: empty process list" -f (Get-Date)
    exit 2
  }
  $busy = @($procs | Where-Object {
    $_.ProcessId -ne $PID -and $_.CommandLine -notmatch 'Get-CimInstance' -and (
      $names -contains [IO.Path]::GetFileNameWithoutExtension($_.Name) -or
      ($_.Name -eq 'dotnet.exe' -and $_.CommandLine -match 'UnrealBuildTool|\bbuild\b|msbuild') -or
      ($_.Name -eq 'cmd.exe' -and $_.CommandLine -match '\\(Build|RunUAT)\.bat'))
  })
  if ($busy.Count -eq 0) { "{0:HH:mm:ss} no builds running" -f (Get-Date); exit 0 }
  "{0:HH:mm:ss} waiting for: {1}" -f (Get-Date), (($busy | ForEach-Object { "$($_.Name)#$($_.ProcessId)" }) -join ', ')
  if ($deadline -and (Get-Date).AddSeconds($IntervalSeconds) -gt $deadline) {
    "{0:HH:mm:ss} timeout after {1}s" -f (Get-Date), $TimeoutSeconds
    exit 3
  }
  Start-Sleep -Seconds $IntervalSeconds
}
