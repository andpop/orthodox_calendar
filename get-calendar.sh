#!/bin/bash
rm table.html
echo "table.html deleted"
# pwsh Get-Calendar_linux.ps1
pwsh canto.ps1
echo "table.html created"
vim table.html
#cat table.html
#cat table.html | xclip -i
#echo "table.html copied to clipboard"
