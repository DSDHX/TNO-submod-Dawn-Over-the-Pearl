param(
    [Parameter(Mandatory = $true)]
    [string]$InputPath,

    [Parameter(Mandatory = $true)]
    [string]$OutputPath
)

Add-Type -AssemblyName System.Drawing

$sourcePath = (Resolve-Path -LiteralPath $InputPath).Path
$source = [Drawing.Bitmap]::new([string]$sourcePath)
$width = $source.Width
$height = $source.Height
$count = $width * $height

$red = [byte[]]::new($count)
$green = [byte[]]::new($count)
$blue = [byte[]]::new($count)
$distance = [double[]]::new($count)
$candidate = [bool[]]::new($count)
$background = [bool[]]::new($count)

$backgroundRed = 248.0
$backgroundGreen = 248.0
$backgroundBlue = 248.0
$connectThreshold = 70.0

for ($y = 0; $y -lt $height; $y++) {
    for ($x = 0; $x -lt $width; $x++) {
        $index = $y * $width + $x
        $color = $source.GetPixel($x, $y)
        $red[$index] = $color.R
        $green[$index] = $color.G
        $blue[$index] = $color.B
        $dr = $backgroundRed - $color.R
        $dg = $backgroundGreen - $color.G
        $db = $backgroundBlue - $color.B
        $d = [Math]::Sqrt($dr * $dr + $dg * $dg + $db * $db)
        $distance[$index] = $d
        $protectedForeground = $false
        if ($y -ge 215) {
            $progress = [Math]::Min(1.0, ($y - 215.0) / ($height - 1.0 - 215.0))
            $protectLeft = [Math]::Floor(102.0 * (1.0 - $progress))
            $protectRight = [Math]::Ceiling(174.0 + (101.0 * $progress))
            $protectedForeground = $x -ge $protectLeft -and $x -le $protectRight
        }
        $candidate[$index] = ($d -le $connectThreshold) -and -not $protectedForeground
    }
}

$queue = [Collections.Generic.Queue[int]]::new()

function Add-BackgroundSeed([int]$x, [int]$y) {
    $index = $y * $width + $x
    if ($candidate[$index] -and -not $background[$index]) {
        $background[$index] = $true
        $queue.Enqueue($index)
    }
}

for ($x = 0; $x -lt $width; $x++) {
    Add-BackgroundSeed $x 0
}

for ($y = 0; $y -lt $height; $y++) {
    Add-BackgroundSeed 0 $y
    Add-BackgroundSeed ($width - 1) $y
}

$neighbors = @(
    @(-1, -1), @(0, -1), @(1, -1),
    @(-1, 0),             @(1, 0),
    @(-1, 1),  @(0, 1),  @(1, 1)
)

while ($queue.Count -gt 0) {
    $index = $queue.Dequeue()
    $x = $index % $width
    $y = [Math]::Floor($index / $width)

    foreach ($offset in $neighbors) {
        $nx = $x + $offset[0]
        $ny = $y + $offset[1]
        if ($nx -lt 0 -or $nx -ge $width -or $ny -lt 0 -or $ny -ge $height) {
            continue
        }

        $neighborIndex = $ny * $width + $nx
        if ($candidate[$neighborIndex] -and -not $background[$neighborIndex]) {
            $background[$neighborIndex] = $true
            $queue.Enqueue($neighborIndex)
        }
    }
}

# Absorb isolated JPEG speckles that sit inside the connected white backdrop.
for ($pass = 0; $pass -lt 2; $pass++) {
    $toBackground = [Collections.Generic.List[int]]::new()
    for ($y = 1; $y -lt $height - 1; $y++) {
        for ($x = 1; $x -lt $width - 1; $x++) {
            $index = $y * $width + $x
            if ($background[$index] -or $distance[$index] -gt 105.0) {
                continue
            }

            $backgroundNeighbors = 0
            foreach ($offset in $neighbors) {
                $neighborIndex = ($y + $offset[1]) * $width + ($x + $offset[0])
                if ($background[$neighborIndex]) {
                    $backgroundNeighbors++
                }
            }

            if ($backgroundNeighbors -ge 5) {
                $toBackground.Add($index)
            }
        }
    }

    foreach ($index in $toBackground) {
        $background[$index] = $true
    }
}

$output = [Drawing.Bitmap]::new($width, $height, [Drawing.Imaging.PixelFormat]::Format32bppArgb)

for ($y = 0; $y -lt $height; $y++) {
    for ($x = 0; $x -lt $width; $x++) {
        $index = $y * $width + $x
        if ($background[$index]) {
            $output.SetPixel($x, $y, [Drawing.Color]::FromArgb(0, 0, 0, 0))
            continue
        }

        $touchesBackground = $false
        for ($dy = -2; $dy -le 2 -and -not $touchesBackground; $dy++) {
            for ($dx = -2; $dx -le 2; $dx++) {
                $nx = $x + $dx
                $ny = $y + $dy
                if ($nx -ge 0 -and $nx -lt $width -and $ny -ge 0 -and $ny -lt $height) {
                    if ($background[$ny * $width + $nx]) {
                        $touchesBackground = $true
                        break
                    }
                }
            }
        }

        if (-not $touchesBackground) {
            $output.SetPixel($x, $y, [Drawing.Color]::FromArgb(255, $red[$index], $green[$index], $blue[$index]))
            continue
        }

        $bestIndex = -1
        $bestRadiusSquared = [int]::MaxValue
        for ($dy = -6; $dy -le 6; $dy++) {
            for ($dx = -6; $dx -le 6; $dx++) {
                $nx = $x + $dx
                $ny = $y + $dy
                if ($nx -lt 0 -or $nx -ge $width -or $ny -lt 0 -or $ny -ge $height) {
                    continue
                }

                $candidateIndex = $ny * $width + $nx
                if ($background[$candidateIndex] -or $distance[$candidateIndex] -lt 120.0) {
                    continue
                }

                $radiusSquared = $dx * $dx + $dy * $dy
                if ($radiusSquared -lt $bestRadiusSquared) {
                    $bestRadiusSquared = $radiusSquared
                    $bestIndex = $candidateIndex
                }
            }
        }

        if ($bestIndex -lt 0) {
            $output.SetPixel($x, $y, [Drawing.Color]::FromArgb(255, $red[$index], $green[$index], $blue[$index]))
            continue
        }

        $vr = $red[$bestIndex] - $backgroundRed
        $vg = $green[$bestIndex] - $backgroundGreen
        $vb = $blue[$bestIndex] - $backgroundBlue
        $cr = $red[$index] - $backgroundRed
        $cg = $green[$index] - $backgroundGreen
        $cb = $blue[$index] - $backgroundBlue
        $denominator = $vr * $vr + $vg * $vg + $vb * $vb
        $alpha = if ($denominator -gt 0) { ($cr * $vr + $cg * $vg + $cb * $vb) / $denominator } else { 1.0 }
        $alpha = [Math]::Max(0.0, [Math]::Min(1.0, $alpha))

        if ($alpha -lt 0.06) {
            $output.SetPixel($x, $y, [Drawing.Color]::FromArgb(0, 0, 0, 0))
        }
        elseif ($alpha -lt 0.97) {
            $a = [int][Math]::Round($alpha * 255.0)
            $output.SetPixel($x, $y, [Drawing.Color]::FromArgb($a, $red[$bestIndex], $green[$bestIndex], $blue[$bestIndex]))
        }
        else {
            $output.SetPixel($x, $y, [Drawing.Color]::FromArgb(255, $red[$index], $green[$index], $blue[$index]))
        }
    }
}

$outputDirectory = Split-Path -Parent $OutputPath
if ($outputDirectory) {
    [IO.Directory]::CreateDirectory($outputDirectory) | Out-Null
}

$output.Save($OutputPath, [Drawing.Imaging.ImageFormat]::Png)
$output.Dispose()
$source.Dispose()

$OutputPath
