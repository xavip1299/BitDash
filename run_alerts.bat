@echo off
REM Script para executar verificação de alertas
REM Para usar com Windows Task Scheduler

echo [%date% %time%] Iniciando verificacao de alertas...

cd /d "C:\Users\Pc\Desktop\dashbit\deploy"
python webhook_alerts.py

echo [%date% %time%] Verificacao concluida.
