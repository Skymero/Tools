[CmdletBinding(SupportsShouldProcess)]
param([string]$TaskName = 'TTS_gen - Drive Queue')
$ErrorActionPreference = 'Stop'
if (Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue) {
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
    Write-Output "Removed $TaskName"
} else { Write-Output "$TaskName is not registered" }

