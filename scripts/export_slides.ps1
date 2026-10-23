$pptPath = (Resolve-Path "presentation\Minor_Project_Presentation_Redesigned.pptx").Path
$outDir = Join-Path (Resolve-Path "presentation").Path "slide_images_redesigned"
if (-not (Test-Path $outDir)) {
    New-Item -ItemType Directory -Path $outDir | Out-Null
}

$ppt = New-Object -ComObject PowerPoint.Application
$presentation = $ppt.Presentations.Open($pptPath, [Microsoft.Office.Core.MsoTriState]::msoTrue, [Microsoft.Office.Core.MsoTriState]::msoFalse, [Microsoft.Office.Core.MsoTriState]::msoFalse)

$slideCount = $presentation.Slides.Count
Write-Output "Exporting $slideCount slides..."
for ($i = 1; $i -le $slideCount; $i++) {
    $slideName = "slide_{0:D2}.png" -f $i
    $imgPath = Join-Path $outDir $slideName
    $presentation.Slides.Item($i).Export($imgPath, "PNG", 1920, 1080)
    Write-Output "Exported slide $i to $imgPath"
}

$presentation.Close()
$ppt.Quit()
[System.Runtime.InteropServices.Marshal]::ReleaseComObject($ppt) | Out-Null
Write-Output "Done exporting slides."
