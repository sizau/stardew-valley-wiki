@echo off
REM ===================================================================
REM ==     音频文件批量重命名工具 (最终版-带引导提示)    ==
REM ==  读取同目录下的CSV文件，并处理子文件夹中的音频文件  ==
REM ===================================================================

REM 设置代码页为UTF-8以正确显示文件名
chcp 65001 > nul
cls

REM ======================== 用户引导提示 ========================
echo.
echo  ========================= 准备工作 =========================
echo.
echo  请在使用前，下载并运行WaveBankExtractPackV2解包Wave Bank.xwb和Wave Bank(1.4).xwb
echo. 并确保文件结构如下:
echo.
echo    -^> 你的工作文件夹/
echo          ^|
echo          +--- Wave Bank/         (包含原始.wav文件的文件夹)
echo          ^|
echo          +--- Wave Bank(1.4)/     (包含原始.wav文件的文件夹)
echo          ^|
echo          +--- wavebank.csv        (由getAudioNameToCSV脚本生成的映射文件)
echo          ^|
echo          +--- wavebank_1_4.csv    (由getAudioNameToCSV脚本生成的映射文件)
echo          ^|
echo          +--- rename_files.bat    (即本脚本文件)
echo.
echo  ============================================================
echo.
echo  确认CSV文件和本脚本在同一目录下后，请按任意键开始...
echo.
pause
cls
REM =============================================================

echo [信息] 脚本启动，准备开始重命名任务...
echo.

REM --- [1/2] 处理 'Wave Bank' 文件夹 ---
echo [--- 正在处理 'Wave Bank' 文件夹 ---]

REM 检查目标文件夹和CSV文件是否存在
if not exist "Wave Bank" (
    echo [错误] "Wave Bank" 文件夹不存在!
    goto process_1_4
)
if not exist "wavebank.csv" (
    echo [错误] "wavebank.csv" 文件不存在!
    goto process_1_4
)

pushd "Wave Bank"
echo 已进入目录: "%cd%"

for /F "skip=1 usebackq tokens=1,* delims=," %%a in ("../wavebank.csv") do (
    if exist "%%a.*" (
        echo   [重命名] "%%a.*"  -^>  "%%b.*"
        ren "%%a.*" "%%b.*"
        if errorlevel 1 (
            echo     [!!! 失败 !!!] 无法重命名。目标文件名可能已存在或无效。
        )
    )
)
echo.
echo 'Wave Bank' 文件夹处理完毕。
popd
echo.
echo -------------------------------------------------------------------
echo.


:process_1_4
REM --- [2/2] 处理 'Wave Bank(1.4)' 文件夹 ---
echo [--- 正在处理 'Wave Bank(1.4)' 文件夹 ---]

if not exist "Wave Bank(1.4)" (
    echo [错误] "Wave Bank(1.4)" 文件夹不存在!
    goto end_script
)
if not exist "wavebank_1_4.csv" (
    echo [错误] "wavebank_1_4.csv" 文件不存在!
    goto end_script
)

pushd "Wave Bank(1.4)"
echo 已进入目录: "%cd%"

for /F "skip=1 usebackq tokens=1,* delims=," %%a in ("../wavebank_1_4.csv") do (
    if exist "%%a.*" (
        echo   [重命名] "%%a.*"  -^>  "%%b.*"
        ren "%%a.*" "%%b.*"
        if errorlevel 1 (
            echo     [!!! 失败 !!!] 无法重命名。目标文件名可能已存在或无效。
        )
    )
)
echo.
echo 'Wave Bank(1.4)' 文件夹处理完毕。
popd
echo.


:end_script
echo ===================================================================
echo ==                      所有操作已完成                       ==
echo ===================================================================
echo.
pause