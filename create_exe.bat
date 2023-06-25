PyInstaller --noconfirm --log-level=WARN --window  --onefile ^
        --add-data="PGA-Ss-S1.csv;." ^
	    --add-data="systems.csv;." ^
	      --add-data="fa.csv;." ^
	         --add-data="fv.csv;." ^
	           --add-data="main_window.ui;." ASCE7.py
