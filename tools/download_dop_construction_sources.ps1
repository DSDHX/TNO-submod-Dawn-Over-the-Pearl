param(
	[string]$OutputRoot = ""
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
if (-not $OutputRoot) {
	$OutputRoot = Join-Path $ProjectRoot "output\imagegen\construction_previews"
}
$SourceDir = Join-Path $OutputRoot "sources"
$MetadataPath = Join-Path $OutputRoot "sources.json"
$DownloadInput = Join-Path $OutputRoot "aria2-input.txt"
$DownloadLog = Join-Path $OutputRoot "download.log"
$SourcesDoc = Join-Path $ProjectRoot "docs\DOP_construction_image_sources.md"

$Sources = @(
	[ordered]@{ Id=1; FileName="01_sky_tower.jpg"; Title="File:Canton Tower 20220626 (cropped).jpg" },
	[ordered]@{ Id=2; FileName="02_rose_garden.jpg"; Title="File:HKIA The Three Runways System Expansion reclamation 201911.jpg" },
	[ordered]@{ Id=3; FileName="03_alice_dream_factory.jpg"; Title="File:City Of Dreams.jpg" },
	[ordered]@{ Id=4; FileName="04_daya_bay_nuclear_plant.jpg"; Title="File:Guangdong 04780019 (8389262688).jpg" },
	[ordered]@{ Id=5; FileName="05_guangdong_shinkansen.jpg"; Title="File:Wuguang PDL viaduct.JPG" },
	[ordered]@{ Id=6; FileName="06_chaoshan_university.jpg"; Title="File:Shantou University Auditorium.jpg" },
	[ordered]@{ Id=7; FileName="07_mountain_reservoirs.jpg"; Title="File:河源市新丰江大坝 - panoramio.jpg" },
	[ordered]@{ Id=8; FileName="08_western_guangdong_granary.jpg"; Title="File:Langkawi Malaysia Rice-Harvesting-08.jpg" },
	[ordered]@{ Id=9; FileName="09_pinglu_canal.jpg"; Title="File:Panama Canal under construction, 1907.jpg" },
	[ordered]@{ Id=10; FileName="10_south_china_sea_oil.jpg"; Title="File:Oil platform P-51 (Brazil).jpg" },
	[ordered]@{ Id=11; FileName="11_wenchang_space_center.jpg"; Title="File:Wentian launched from Wenchang.jpg" },
	[ordered]@{ Id=12; FileName="12_guangxi_industrial_institute.jpg"; Title="File:Guangxi University of Finance and Economics, Xiangsihu campus (20240216183717).jpg" },
	[ordered]@{ Id=13; FileName="13_guangxi_expressway.jpg"; Title="File:The Lanhai Expressway Qinjiang Bridge in Guangxi.jpg" },
	[ordered]@{ Id=14; FileName="14_nanyue_folk_park.jpg"; Title="File:Chengyang Yongji Bridge, Guangxi.jpg" },
	[ordered]@{ Id=15; FileName="15_lijiang_waterway.jpg"; Title="File:Li River cruise from Guilin to Yangshuo.JPG" },
	[ordered]@{ Id=16; FileName="16_friendship_pass.jpg"; Title="File:The main gate of Friendship Pass in China.jpg" },
	[ordered]@{ Id=17; FileName="17_prd_maglev.jpg"; Title="File:Shanghai Maglev 2.jpg" },
	[ordered]@{ Id=18; FileName="18_shantou_integration.jpg"; Title="File:Jieyang Chaoshan Airport.JPG" },
	[ordered]@{ Id=19; FileName="19_granite_uranium_mining.jpg"; Title="File:Rossing Uranium Mine (01810465) (12220614635).jpg" },
	[ordered]@{ Id=20; FileName="20_shale_oil_refineries.jpg"; Title="File:Refinery, Bayport Industrial Complex, Harris County, Texas.jpg" }
)

New-Item -ItemType Directory -Force -Path $OutputRoot, $SourceDir, (Split-Path -Parent $SourcesDoc) | Out-Null
$Metadata = [System.Collections.Generic.List[object]]::new()
$AriaLines = [System.Collections.Generic.List[string]]::new()

$Titles = ($Sources | ForEach-Object { $_.Title }) -join "|"
$Api = "https://commons.wikimedia.org/w/api.php?action=query&titles=" +
	[Uri]::EscapeDataString($Titles) +
	"&prop=imageinfo&iiprop=url|size|mime|extmetadata&iiurlwidth=2000&format=json&origin=*"
$Response = Invoke-RestMethod -Uri $Api -TimeoutSec 30 -Headers @{ "User-Agent" = "Dawn-Over-the-Pearl-preview-builder/260828C" }
$Pages = $Response.query.pages.psobject.Properties.Value

foreach ($Source in $Sources) {
	$Page = $Pages | Where-Object { $_.title -eq $Source.Title } | Select-Object -First 1
	if (-not $Page.imageinfo) {
		throw "Commons source not found: $($Source.Title)"
	}
	$Info = $Page.imageinfo[0]
	$CommonsFileName = $Source.Title.Substring(5)
	$DownloadUrl = "https://commons.wikimedia.org/wiki/Special:Redirect/file/" +
		[Uri]::EscapeDataString($CommonsFileName) + "?width=1200"
	$ExpectedBytes = if ($Info.thumbsize) { [int64]$Info.thumbsize } else { [int64]$Info.size }
	$TargetPath = Join-Path $SourceDir $Source.FileName
	if (-not (Test-Path -LiteralPath $TargetPath) -or (Get-Item -LiteralPath $TargetPath).Length -lt 1024) {
		$AriaLines.Add($DownloadUrl)
		$AriaLines.Add("  out=$($Source.FileName)")
	}
	$Artist = [regex]::Replace([string]$Info.extmetadata.Artist.value, "<[^>]+>", "")
	$Metadata.Add([ordered]@{
		id = $Source.Id
		file_name = $Source.FileName
		title = $Source.Title
		source_page = [string]$Info.descriptionurl
		original_url = [string]$Info.url
		download_url = [string]$DownloadUrl
		expected_bytes = $ExpectedBytes
		width = if ($Info.thumbwidth) { [int]$Info.thumbwidth } else { [int]$Info.width }
		height = if ($Info.thumbheight) { [int]$Info.thumbheight } else { [int]$Info.height }
		license = [string]$Info.extmetadata.LicenseShortName.value
		license_url = [string]$Info.extmetadata.LicenseUrl.value
		author = [System.Net.WebUtility]::HtmlDecode($Artist).Trim()
		processing = "aspect-preserving portrait crop; high contrast; low saturation; cyan-blue grade; scanlines; grain; no left shadow or gradient; 2px cyan border burned into final bitmap"
	})
}

[IO.File]::WriteAllLines($DownloadInput, $AriaLines, [Text.UTF8Encoding]::new($false))
$Metadata | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $MetadataPath -Encoding utf8

if ($AriaLines.Count -gt 0) {
	$Aria = (Get-Command aria2c -ErrorAction Stop).Source
	& $Aria "--input-file=$DownloadInput" "--dir=$SourceDir" "--continue=true" "--max-concurrent-downloads=1" "--split=1" "--min-split-size=1M" "--connect-timeout=30" "--timeout=30" "--max-tries=3" "--retry-wait=12" "--summary-interval=2" "--auto-file-renaming=false" "--user-agent=Dawn-Over-the-Pearl-preview-builder/260828C" "--referer=https://commons.wikimedia.org/" "--log=$DownloadLog" "--log-level=notice" "--console-log-level=notice"
	if ($LASTEXITCODE -ne 0) {
		throw "aria2c failed with exit code $LASTEXITCODE; resume with the same command"
	}
}

foreach ($Entry in $Metadata) {
	$Path = Join-Path $SourceDir $Entry.file_name
	if (-not (Test-Path -LiteralPath $Path)) {
		throw "Missing downloaded source: $Path"
	}
	$Actual = (Get-Item -LiteralPath $Path).Length
	if ($Actual -lt 1024) {
		throw "Downloaded source is unexpectedly small: $($Entry.file_name) ($Actual bytes)"
	}
	$Entry | Add-Member -NotePropertyName actual_bytes -NotePropertyValue $Actual -Force
}
$Metadata | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $MetadataPath -Encoding utf8

$Lines = [System.Collections.Generic.List[string]]::new()
$Lines.Add("# 南粤建设系统：现实图片来源")
$Lines.Add("")
$Lines.Add("20张预览图均使用下列Wikimedia Commons现实照片重新制作；最终图不使用旧预览帧、帧条、左侧阴影或渐变。")
$Lines.Add("")
$Lines.Add("| ID | 项目原图文件 | Commons来源 | 作者 | 许可 |")
$Lines.Add("|---:|---|---|---|---|")
foreach ($Entry in $Metadata) {
	$SafeAuthor = ([string]$Entry.author).Replace("|", "\|")
	$Lines.Add("| $($Entry.id) | $($Entry.file_name) | [$($Entry.title)]($($Entry.source_page)) | $SafeAuthor | [$($Entry.license)]($($Entry.license_url)) |")
}
$Lines.Add("")
$Lines.Add("## 生成式清理")
$Lines.Add("")
$Lines.Add("ID 6、7、8、12、17 的现实原图含有与项目语境冲突的院校名、水库题字、制造商logo、门牌或上海磁悬浮标识。内置imagegen只清除这些文字和logo；对应现实原图继续保存在 `sources/`，清理版单独保存在 `cleaned/`。其余15项直接读取现实原图。完整提示词和不变量见 `docs/DOP_construction_image_cleanup_prompts.md`。")
[IO.File]::WriteAllLines($SourcesDoc, $Lines, [Text.UTF8Encoding]::new($false))

Write-Output "sources: $SourceDir"
Write-Output "metadata: $MetadataPath"
Write-Output "licenses: $SourcesDoc"
