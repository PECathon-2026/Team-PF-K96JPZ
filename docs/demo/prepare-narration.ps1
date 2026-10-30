param([Parameter(Mandatory=$true)][string]$OutputDirectory)
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Speech
New-Item -ItemType Directory -Path $OutputDirectory -Force | Out-Null
$plan = Get-Content -Raw (Join-Path $PSScriptRoot 'demo-plan.json') | ConvertFrom-Json
$voice = New-Object System.Speech.Synthesis.SpeechSynthesizer
$voice.SelectVoice('Microsoft Zira Desktop')
function Get-WaveDuration([string]$Path) {
    $reader = New-Object IO.BinaryReader([IO.File]::OpenRead($Path))
    try {
        $reader.BaseStream.Position = 12
        $bytesPerSecond = 0
        while ($reader.BaseStream.Position + 8 -le $reader.BaseStream.Length) {
            $id = [Text.Encoding]::ASCII.GetString($reader.ReadBytes(4))
            $length = $reader.ReadUInt32()
            $position = $reader.BaseStream.Position
            if ($id -eq 'fmt ') {
                $reader.BaseStream.Position = $position + 8
                $bytesPerSecond = $reader.ReadUInt32()
            }
            if ($id -eq 'data' -and $bytesPerSecond -gt 0) { return $length / $bytesPerSecond }
            $reader.BaseStream.Position = $position + $length + ($length % 2)
        }
        throw 'Unable to read generated speech duration.'
    } finally { $reader.Dispose() }
}
$metadata = @()
try {
    for ($index=0; $index -lt $plan.scenes.Count; $index++) {
        $scene = $plan.scenes[$index]
        $wav = Join-Path $OutputDirectory ('voice-{0}.wav' -f $index)
        for ($rate=0; $rate -le 6; $rate++) {
            $voice.Rate = $rate
            $voice.SetOutputToWaveFile($wav)
            $voice.Speak($scene.text)
            $voice.SetOutputToNull()
            $duration = Get-WaveDuration $wav
            if ($duration -le $scene.seconds - 0.6) { break }
        }
        if ($duration -gt $scene.seconds - 0.6) { throw 'Speech exceeds allocated scene duration.' }
        $metadata += @{ index=$index; duration=$duration; rate=$rate; voice='Microsoft Zira Desktop' }
        Write-Output ('Scene {0}: {1:N1}s speech / {2}s scene, rate {3}' -f ($index+1),$duration,$scene.seconds,$rate)
    }
    $metadata | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $OutputDirectory 'speech.json') -Encoding UTF8
} finally { $voice.Dispose() }
