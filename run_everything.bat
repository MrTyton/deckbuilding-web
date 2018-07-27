REM python cleanup.py
REM C:\Python27\python.exe grab_archetypes.py
python generate_deck_page.py
python generate_readme.py
git add .
git commit -m "Update"
git push