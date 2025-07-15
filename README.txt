Medibang Brush Config Manager

Description:
This is a config file manager for the old version of Medibang Paint for Windows.

This software is aimed to improve the user experience by:
a. providing access to default brushes from 2023 and FireAlpaca brushes
b. providing better UI for Brush Group management

============================================================================================================
Install:
1. Unzip and run scripts (from configurerGUI.py) or executable in the same directory as 'src'

Run:
1. Enter path to Medibang's config folder, usually at C:\Users\[username]\AppData\Local\Medibang\CloudAlpaca
2. Back up your current 'Brush2.ini' and 'BrushGroups.ini' files by copying into a separate directory (Optional but strongly reccomended)
3. Run program
4. Click overwrite button to save changes, exiting without clicking the overwrite button will not modify files
**Only run program when Medibang Paint is closed!!**

==========================================================================================================
Functionality:
-Import brushes selected from a brush list folder into user's local 'Brush2.ini' and their respective scripts or bitmaps (does not import repeats)
-Mass import brushes from FireAlpaca
-Edit brush groups in user's local 'BrushGroups.ini' and assign brushes to groups (repeat groups ignored)
-Duplicating selected brushes
-Quick compare for brush config code

Current Limitations:
-Cannot import brushes and files outside of those in src; you need to manually place files in before runtime
-Currently depends on an existing .xml or .ini file to get brush parameters
-Cannot rename brushes or change order within a group
-Cannot change order of brush groups
-**FireAlpaca brushes not guaranteed to work properly due to Medibang brushes not having a texture parameter

===========================================================================================================
How to add brush lists:

For Medibang Brushes:
1. Create new folder in 'src\brush_lists'
2. Copy 'Brush2.ini', 'brush_script', and 'brush_bitmap' from your Medibang config folder into the new folder
3. Run the program, your new brush list should appear in the initial window's list widget

For FireAlpaca Brushes:
1. Create new folder in 'src\brush_lists'
2. Copy 'BrushNew.xml', 'brush_script', 'brush_texture', and 'brush_bitmap' from your FireAlpaca config folder into the new folder
3. Run the program, your new brush list should appear in the initial window's list widget
