@echo off
set ENV=%1
if "%ENV%"=="" set ENV=default.yaml
set SUITE=%2
if "%SUITE%"=="" set SUITE=testcases\bstackdemo_e2e.robot
set EXTRA=%3

echo Running Robot Framework with Environment: %ENV%
echo Target Suite: %SUITE%

.\.venv\Scripts\python.exe -m robot %EXTRA% --outputdir results --prerunmodifier resources\keywords\custom-libs\DataLoader.py:%ENV% %SUITE%
