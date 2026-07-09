python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pygbag --build --ume_block 0 --title "Mosaic Star Raiders" --app_name "Mosaic Star Raiders" .
Write-Host "Build generated in build/web"
