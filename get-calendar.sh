#!/bin/bash
rm table.html
echo "table.html deleted"
pwsh canto.ps1
echo "table.html created"
vim table.html
