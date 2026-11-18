[CmdletBinding()]
param([string]$TaskName = 'TTS_gen - Drive Queue')
$ErrorActionPreference = 'Stop'
$project = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$python = Join-Path $project '.venv\Scripts\python.exe'
$script = Join-Path $project 'run_drive_queue.py'
if (-not (Test-Path -LiteralPath $python)) { throw "Python not found: $python" }
if (-not (Test-Path -LiteralPath $script)) { throw "Queue script not found: $script" }
$action = New-ScheduledTaskAction -Execute $python -Argument "`"$script`" --once" -WorkingDirectory $project
$trigger = New-ScheduledTaskTrigger -AtLogOn -User $env:USERNAME
$trigger.Repetition.Interval = 'PT5M'
$trigger.Repetition.Duration = 'P1D'
$settings = New-ScheduledTaskSettingsSet -MultipleInstances IgnoreNew -StartWhenAvailable
Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Settings $settings -Description 'Processes one TTS_gen Drive chapter per run.' -Force | Out-Null
Write-Output "Registered $TaskName. The selected account must independently resolve FFmpeg, read the secrets directory, reach Drive/Langflow, and remain awake/on-network."

