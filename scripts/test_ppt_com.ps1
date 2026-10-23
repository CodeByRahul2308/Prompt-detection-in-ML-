try {
    $ppt = New-Object -ComObject PowerPoint.Application
    Write-Output "PowerPoint COM version: $($ppt.Version)"
    $ppt.Quit()
    [System.Runtime.InteropServices.Marshal]::ReleaseComObject($ppt) | Out-Null
} catch {
    Write-Output "Error: $_"
}
