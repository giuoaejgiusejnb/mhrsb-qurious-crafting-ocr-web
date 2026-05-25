@echo off
setlocal

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

for /f "usebackq delims=" %%I in (`powershell -Command "Add-Type -AssemblyName System.Windows.Forms; $f = New-Object System.Windows.Forms.FolderBrowserDialog; $f.Description = 'ZIP保存先選択'; if ($f.ShowDialog() -eq 'OK') { $f.SelectedPath }"`) do (
    set "TargetFolder=%%I"
)

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

:: PowerShellで無圧縮ZIPを作成
powershell -Command "Add-Type -AssemblyName System.IO.Compression.FileSystem; if (Test-Path '%ZipFilePath%') { Remove-Item '%ZipFilePath%' -Force }; [System.IO.Compression.ZipFile]::CreateFromDirectory('%SourceFolder%', '%ZipFilePath%', [System.IO.Compression.CompressionLevel]::NoCompression, $false);"

echo.
echo ZIPファイルの作成が完了しました
echo.
pause
