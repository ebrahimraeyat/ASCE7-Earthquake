pyinstaller --noconfirm --log-level=WARN ^
    --onefile --window ^
    --add-data="data/PGA-Ss-S1.csv;data" ^
    --add-data="data/systems.csv;data" ^
    --add-data="widgets/main_window.ui;widgets" ^
    pyqtgraph1.py