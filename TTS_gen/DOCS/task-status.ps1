[CmdletBinding()]
param([string]$TaskName = 'TTS_gen - Drive Queue')
$ErrorActionPreference = 'Stop'
$task = Get-ScheduledTask -TaskName $TaskName
$info = Get-ScheduledTaskInfo -TaskName $TaskName
[pscustomobject]@{TaskName=$TaskName; State=$task.State; LastRunTime=$info.LastRunTime; LastTaskResult=$info.LastTaskResult; NextRunTime=$info.NextRunTime}

