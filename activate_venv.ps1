# PowerShell script to activate virtual environment for litellm-ui project

Write-Host "正在为 litellm-ui 项目设置虚拟环境..." -ForegroundColor Green

# Check if virtual environment directory exists
if (-not (Test-Path "venv")) {
    Write-Host "正在创建虚拟环境..." -ForegroundColor Yellow
    python -m venv venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "错误：创建虚拟环境失败。请确保已安装 Python。" -ForegroundColor Red
        exit 1
    }
}

# Activate virtual environment
Write-Host "正在激活虚拟环境..." -ForegroundColor Yellow
try {
    & ".\venv\Scripts\Activate.ps1"
    Write-Host "虚拟环境激活成功！" -ForegroundColor Green
    
    # Show Python and pip paths
    $pythonPath = (Get-Command python -ErrorAction SilentlyContinue).Source
    $pipPath = (Get-Command pip -ErrorAction SilentlyContinue).Source
    
    if ($pythonPath) {
        Write-Host "Python 路径: $pythonPath" -ForegroundColor Cyan
    }
    if ($pipPath) {
        Write-Host "Pip 路径: $pipPath" -ForegroundColor Cyan
    }
    
    # Check if requirements are installed
    if (Test-Path "requirements.txt") {
        Write-Host "正在安装/更新依赖包..." -ForegroundColor Yellow
        pip install -r requirements.txt
        if ($LASTEXITCODE -eq 0) {
            Write-Host "依赖包安装成功！" -ForegroundColor Green
        } else {
            Write-Host "警告：某些依赖包可能安装失败。" -ForegroundColor Yellow
        }
    }
    
    Write-Host ""
    Write-Host "虚拟环境已准备就绪！现在可以运行：" -ForegroundColor Green
    Write-Host "  python main.py    # 或者" -ForegroundColor White
    Write-Host "  python app.py     # 根据你的入口点" -ForegroundColor White
    Write-Host ""
    Write-Host "要稍后停用虚拟环境，请运行：deactivate" -ForegroundColor Cyan
} catch {
    Write-Host "错误：激活虚拟环境失败。" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    exit 1
}