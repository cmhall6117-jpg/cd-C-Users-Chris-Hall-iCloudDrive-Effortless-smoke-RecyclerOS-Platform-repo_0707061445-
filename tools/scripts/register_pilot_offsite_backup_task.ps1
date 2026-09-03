[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$ConfigPath,

    [string]$PythonExecutable = "python",

    [string]$TaskName = "RecyclerOS Pilot Off-Platform Backup",

    [datetime]$DailyAt = "02:00",

    [Parameter(Mandatory = $true)]
    [string]$Confirm
)

$ErrorActionPreference = "Stop"
$RequiredConfirmation = "REGISTER RECYCLEROS OFFSITE BACKUP"
if ($Confirm -cne $RequiredConfirmation) {
    throw "Confirm must exactly match: $RequiredConfirmation"
}

$RepositoryRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$BackupScript = Join-Path $PSScriptRoot "pilot_postgres_offsite_backup.py"
$ConfigPath = (Resolve-Path $ConfigPath).Path
$PythonCommand = Get-Command $PythonExecutable -ErrorAction Stop
if ($PythonCommand.CommandType -ne "Application") {
    throw "PythonExecutable must resolve to an executable application."
}
$PythonExecutable = $PythonCommand.Source

$ValidationOutput = @(
    & $PythonExecutable $BackupScript --config $ConfigPath --validate-only 2>&1
)
if (
    $LASTEXITCODE -ne 0 -or
    $ValidationOutput -notcontains "PASS off-platform backup configuration"
) {
    throw "Off-platform backup configuration validation failed."
}
Write-Output "PASS off-platform backup configuration"

$ExistingTask = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($null -ne $ExistingTask) {
    throw "A scheduled task named '$TaskName' already exists."
}

$Arguments = '"{0}" --config "{1}"' -f $BackupScript, $ConfigPath
$Action = New-ScheduledTaskAction `
    -Execute $PythonExecutable `
    -Argument $Arguments `
    -WorkingDirectory $RepositoryRoot
$Trigger = New-ScheduledTaskTrigger -Daily -At $DailyAt
$Settings = New-ScheduledTaskSettingsSet `
    -StartWhenAvailable `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -ExecutionTimeLimit (New-TimeSpan -Hours 2) `
    -MultipleInstances IgnoreNew
$UserId = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
$Principal = New-ScheduledTaskPrincipal `
    -UserId $UserId `
    -LogonType Interactive `
    -RunLevel Limited

Register-ScheduledTask `
    -TaskName $TaskName `
    -Action $Action `
    -Trigger $Trigger `
    -Settings $Settings `
    -Principal $Principal | Out-Null

Write-Output "Registered '$TaskName' for $($DailyAt.ToString('HH:mm'))."
Write-Output "The task runs only while $UserId is signed in."
