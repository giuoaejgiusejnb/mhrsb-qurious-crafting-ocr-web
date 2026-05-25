@echo off
:: 文字コードをUTF-8（コードページ65001）に変更して文字化けを防止
chcp 65001 >nul
setlocal enabledelayedexpansion

:: ドラッグ＆ドロップされたフォルダのパスを取得
set "SourceFolder=%~1"

:: 何もドロップされずに起動した場合は終了
if "%SourceFolder%"=="" (
    echo フォルダをこのアイコンにドラッグ＆ドロップしてください。
    pause
    exit /b
)

echo フォルダの処理中: %SourceFolder%
echo.
echo 保存先を選択する画面が表示されます。しばらくお待ちください...

:: 一時的なPowerShellスクリプトを作成して実行（バッチの記号エラーを回避）
set "ps_script=%temp%\select_folder_%random%.ps1"
(
    echo Add-Type -AssemblyName System.Windows.Forms
    echo $f = New-Object System.Windows.Forms.FolderBrowserDialog
    echo $f.Description = 'ZIP保存先選択'
    echo if ^($f.ShowDialog^(^) -eq 'OK'^) { Write-Output $f.SelectedPath }
) > "%ps_script%"

for /f "usebackq delims=" %%I in (`powershell -NoProfile -ExecutionPolicy Bypass -File "%ps_script%"`) do (
    set "TargetFolder=%%I"
)
del "%ps_script%" 2>nul

:: キャンセルされた場合は終了
if "%TargetFolder%"=="" (
    echo 保存先が選択されなかったため、処理を中止しました。
    pause
    exit /b
)

:: 出力するZIPファイルのフルパスを生成
set "ZipFilePath=%TargetFolder%\%~n1.zip"

echo.
echo 保存先: %ZipFilePath%
echo 処理を開始します...

:: 圧縮処理用のPowerShellスクリプトを作成して実行
set "ps_compress=%temp%\compress_%random%.ps1"
(
    echo Add-Type -AssemblyName System.IO.Compression.FileSystem
    echo if ^(Test-Path '%ZipFilePath%'^) { Remove-Item '%ZipFilePath%' -Force }
    echo [System.IO.Compression.ZipFile]::CreateFromDirectory^('%SourceFolder%', '%ZipFilePath%', [System.IO.Compression.CompressionLevel]::NoCompression, $false^)
) > "%ps_compress%"

powershell -NoProfile -ExecutionPolicy Bypass -File "%ps_compress%"
del "%ps_compress%" 2>nul

echo.
echo ZIPファイルの作成が完了しました
echo.
pause
