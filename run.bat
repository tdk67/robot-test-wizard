@echo off
set ENV=%1
if "%ENV%"=="" set ENV=default.yaml
set SUITE=%2
if "%SUITE%"=="" set SUITE=testcases\bstackdemo_e2e.robot

echo Running Robot Framework with Environment: %ENV%
echo Target Suite: %SUITE%

.\.venv\Scripts\python.exe -m robot --outputdir results --prerunmodifier resources\keywords\custom-libs\DataLoader.py:%ENV% %SUITE%
