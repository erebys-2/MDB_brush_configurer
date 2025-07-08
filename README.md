Medibang Brush Config Manager

Description:
This is a config file manager for the old version of Medibang Paint for Windows.

This software is aimed to improve the user experience by:
a. providing optional access to default brushes from 2023
b. providing better UI for Brush Group management

Install:
1. Unzip and run scripts (from configurerGUI.py) or executable in the same directory as 'src' 
2. Enter path to Medibang's config folder, usually at C:\Users\[username]\AppData\Local\Medibang\CloudAlpaca
3. Back up your current 'Brush2.ini' and 'BrushGroups.ini' files by copying into a separate directory (Optional but strongly reccomended)
4. Run program

Functionality:
-Import brushes selected from 'Default.ini' into user's local 'Brush2.ini' and their respective scripts or bitmaps (will not import repeats)
-Edit brush groups in user's local 'BrushGroups.ini' and assign brushes to groups (repeat groups ignored)
-Quick compare for brush config code

Current Limitations:
-Cannot import brushes and files outside of those in src; currently has no means of automatically updating default.ini
-^Contributers see comments in file_handler.py
-Cannot rename or duplicate brushes or change order within a group
-Cannot change order of brush groups

Notes:
-Only run program when Medibang Paint is closed