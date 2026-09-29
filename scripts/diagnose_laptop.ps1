# Comprehensive Windows Performance Diagnostics Script
Write-Output "=================================================="
Write-Output "       1. SYSTEM & CPU SPECIFICATIONS             "
Write-Output "=================================================="
$cs = Get-CimInstance Win32_ComputerSystem
$proc = Get-CimInstance Win32_Processor
[PSCustomObject]@{
    Manufacturer = $cs.Manufacturer
    Model = $cs.Model
    RAM_Total_GB = [math]::Round($cs.TotalPhysicalMemory / 1GB, 2)
    CPU_Name = $proc.Name
    Cores = $proc.NumberOfCores
    Threads = $proc.NumberOfLogicalProcessors
    MaxSpeed_MHz = $proc.MaxClockSpeed
} | Format-List

Write-Output "=================================================="
Write-Output "       2. DRIVE TYPE & FREE SPACE                 "
Write-Output "=================================================="
Get-PhysicalDisk | Select-Object DeviceId, FriendlyName, MediaType, BusType, @{Name="Size_GB";Expression={[math]::Round($_.Size/1GB,1)}} | Format-Table -AutoSize
Get-PSDrive -PSProvider FileSystem | Select-Object Name, @{Name="Free_GB";Expression={[math]::Round($_.Free/1GB,1)}}, @{Name="Total_GB";Expression={[math]::Round(($_.Used+$_.Free)/1GB,1)}}, @{Name="Percent_Free";Expression={[math]::Round(($_.Free/($_.Used+$_.Free))*100,1)}} | Format-Table -AutoSize

Write-Output "=================================================="
Write-Output "       3. RAM USAGE & COMMIT CHARGE               "
Write-Output "=================================================="
$os = Get-CimInstance Win32_OperatingSystem
[PSCustomObject]@{
    Total_RAM_MB = [math]::Round($os.TotalVisibleMemorySize/1024, 0)
    Free_RAM_MB = [math]::Round($os.FreePhysicalMemory/1024, 0)
    RAM_Used_Pct = [math]::Round((($os.TotalVisibleMemorySize - $os.FreePhysicalMemory)/$os.TotalVisibleMemorySize)*100, 1)
    Total_PageFile_MB = [math]::Round($os.TotalVirtualMemorySize/1024, 0)
    Free_PageFile_MB = [math]::Round($os.FreeVirtualMemory/1024, 0)
} | Format-List

Write-Output "=================================================="
Write-Output "       4. STARTUP PROGRAMS (BOOT HOGS)            "
Write-Output "=================================================="
Get-CimInstance Win32_StartupCommand | Select-Object Name, Command, Location, User | Format-Table -AutoSize

Write-Output "=================================================="
Write-Output "       5. TOP MEMORY CONSUMING PROCESSES          "
Write-Output "=================================================="
Get-Process | Sort-Object WorkingSet64 -Descending | Select-Object -First 12 Id, ProcessName, @{Name="RAM_MB";Expression={[math]::Round($_.WorkingSet64/1MB,1)}}, @{Name="CPU_Total_Sec";Expression={[math]::Round($_.CPU,1)}} | Format-Table -AutoSize

Write-Output "=================================================="
Write-Output "       6. SYSTEM EVENT LOG (BOOT/CRASH WARNINGS)  "
Write-Output "=================================================="
Get-WinEvent -FilterHashtable @{LogName='System'; Level=1,2; StartTime=(Get-Date).AddDays(-2)} -MaxEvents 6 -ErrorAction SilentlyContinue | Select-Object TimeCreated, Id, ProviderName, Message | Format-List
