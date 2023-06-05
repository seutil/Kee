
function Start-Tests {
    $tests = Get-ChildItem -Filter test_*.py -Recurse -Name
    foreach ($test in $tests)
    {
        Write-Host "Run $test..." -NoNewLine
        $result = python -m unittest $test 2> $null
        if ($LASTEXITCODE -ne 0)
        {
            Write-Host " failed!" -NoNewLine
            $runTest = Read-Host " Run? [Y/n]"
            if (@("y", "Y") -contains $runTest)
            {
                python -m unittest $test
            }
            exit
        }
        else
        {
            Write-Host " done!"
        }
    }
    echo "OK`n"
}

function Compile-Resources {
    Write-Host "Compile resources..." -NoNewLine
    pyrcc5 ui\resources\resources.qrc -o ui\resources\resources.py 2> $null
    if ($LASTEXITCODE -ne 0)
    {
        Write-Host " faield. " -NoNewLine
        $Continue = Read-Host "Continue? [Y/n]"
        if ($Continue -eq "n")
        {
            exit
        }

        $resourcesPath = "ui\resources\resources.py"
        if (!(Test-Path $resourcesPath))
        {
            New-Item -Path $resourcesPath | Out-Null
        }
    }
    else
    {
        Write-Host " done!"
    }
}

function Run-Application {
    Write-Host "Start application..." -NoNewLine
    python main.py
    if ($LASTEXITCODE -ne 0)
    {
        Write-Host " failed with error $LASTEXITCODE"
    }
    else
    {
        Write-Host " done!"
    }
}
clear
Write-Host "=== START TESTS ==="
Start-Tests
Write-Host "=== START APPLICATION ==="
Compile-Resources
Run-Application
Write-Host "=== STOP ==="
