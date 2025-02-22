$monday = (Get-Date -Year 2025 -Month 2 -Day 17)

# ------------- Functions  ------------------------------------------

function Get-ResponseFromAPI($Date) {
    $formattedDate = $Date.ToString("dd-MM-yyyy")
    $request = "http://www.canto.ru/calendar/js/unicode.php?date=$formattedDate"
    Invoke-RestMethod -Uri $request
}

function Parse-Response($Response) {
    # Выделяем содержимое функции print_day
    $regex = 'function\s+print_day\s*\(\s*\)\s*{([^}]*)}'
    if ($Response -match $regex) {$saints = $matches[1].Trim()} else {$saints = 'Unknown'}
    # Удаляем лишние пробелы
    $saints = (($saints -split ";").Trim()) -join ''
    # Удаляем все HTML-теги
    $saints = $saints -replace '<[^>]+>', ''
     
    # Используем регулярное выражение для поиска всех текстов внутри двойных кавычек
    $matches = [regex]::Matches($saints, '"(.*?)"')

    # Создаем массив для хранения найденных фрагментов
    $resultFragments = @()

    # Добавляем найденные фрагменты в массив
    foreach ($match in $matches) {
        if (-not [string]::IsNullOrWhiteSpace($match.Groups[1].Value)) {
            $resultFragments += $match.Groups[1].Value.Trim()
        }
    }
    # Объединяем фрагменты в одну строку
    $saints = $resultFragments -join ' '

    $saints
}

function Get-Saints ($Date) {
    $response = (Get-ResponseFromAPI $Date)
    $saints = (Parse-Response $response)
    
    $saints
}

function Out-TableHeader {
    '<table class="alignleft schedule">' >> $outFile
    '<tbody>' >> $outFile
}

function Out-TableFooter {
    '</tbody>' >> $outFile
    '</table>' >> $outFile
}

function Out-TableRow ($date, $saints, $worships){
    # Название дня недели, первая буква заглавная
    $dayOfWeekRus = ((Get-Culture).DateTimeFormat.GetDayName($date.DayOfWeek))
    $dayOfWeekRus = ($dayOfWeekRus.Substring(0,1).ToUpper()+$dayOfWeekRus.Substring(1))
    # Выделяем номер дня и название месяца
    $date.ToLongDateString() -match '(, )(\S+ \S+)' > $null
    $dayMonthName = $matches[2]

    $dateForTable = "$dayOfWeekRus `n $dayMonthName"

    '<!-- *********** {0} ************************************************************ -->' -f $dayOfWeekRus  >> $outFile
    if ([int]$date.DayOfWeek -eq 0) {'<tr class="red">' >> $outFile}
    else {'<tr>' >> $outFile}
    '<td> {0} </td>' -f $dateForTable >> $outFile
    '<td> {0} </td>' -f $saints >> $outFile
    '<td> {0} </td>' -f $worships >> $outFile
    '</tr>' >> $outFile
}

# ------------- Main ------------------------------------------
$currentDirectory = $MyInvocation.MyCommand.Definition | split-path -parent
$outFile = $currentDirectory+'\table.html'
if (Test-Path $outFile) {Remove-Item $outFile}

$startDate = $monday.ToString("dd-MM-yyy")
$endDate = $monday.AddDays(6).ToString("dd-MM-yyy")

Write-Host "Make schedule from $startDate to $endDate"
Out-TableHeader

1 .. 7 | foreach {
    $date = $monday.AddDays($_-1)

    Write-Host "Request $($Date.ToString("dd-MM-yyyy")) ..."

    # Святые и праздники дня
    $saints = (Get-Saints $date)

    if ($_ -lt 6) 
        # Богослужения с понедельника по пятницу
        {$worships = "07:30 Часы. Божественная литургия `n 16:30 Вечернее богослужение "}
    elseif ($_ -lt 7)
        # Богослужения в пятницу
        {$worships = "08:00 Часы. Божественная литургия `n 16:30 Всенощное бдение "} 
    else
        # Богослужения в воскресенье
        {$worships = "08:00 Часы. Божественная литургия `n 16:30 Вечернее богослужение "} 

     
    Out-TableRow $date $saints $worships
}

Out-TableFooter
