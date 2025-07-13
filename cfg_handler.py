import configparser as cfgp
import os
from file_handler import file_handler as fh
#File contains cfg parser related classes
#Note: The 'General' section in Brush2.ini initially gets moved to the last index after Medibang initially downloads brushes
#Close and reopen Medibang twice and it goes to the top of the file.
#Having an incorrectly placed 'General' section will most likely crash the program since indexing will be off.

class path_cfg_handler():#cfg handler class for initial window and setting path for program
    def __init__(self):
        self.pathcfg = cfgp.ConfigParser()
        self.pathcfg.read('src/CurrentPath.ini')
        
    def get_curr_path(self):
        return self.pathcfg['Medibang Config Path']['path']
    
    def set_curr_path(self, path_str):
        self.pathcfg['Medibang Config Path']['path'] = path_str
        with open('src/CurrentPath.ini', 'w') as configfile:
            self.pathcfg.write(configfile)
        

class cfg_handler():#cfg handler class responsible for main functionalities
    def __init__(self):
        pathcfg = path_cfg_handler()#get path to config files
        self.mdb_path = pathcfg.get_curr_path()
        del pathcfg
        
        self.file_handler = fh()#create file handler
        
        self.defaultcfg = cfgp.ConfigParser()
        self.defaultcfg.read('src/Default.ini')
        
        self.brush2cfg = cfgp.ConfigParser()
        self.brushgroupcfg = cfgp.ConfigParser()
        
        self.BMPfile_delete_list = []
        self.BMPfile_copy_list = []
        
        self.BSfile_delete_list = []
        self.BSfile_copy_list = []
        
        #add ini files if not present directly to mdb_path
        if 'Brush2.ini' not in os.listdir(self.mdb_path):
            self.brush2cfg['General'] = {
                'activeIndex': '0',
                'version': '1'
            }
            with open(os.path.join(self.mdb_path, 'Brush2.ini'), 'w') as configfile:
                self.brush2cfg.write(configfile)
        else:
            self.brush2cfg.read(os.path.join(self.mdb_path, 'Brush2.ini'))
            #bring 'General' section to top
            if self.brush2cfg.sections().index('General') != 0:
                temp_cfg = cfgp.ConfigParser()
                temp_cfg['General'] = {
                    'activeIndex': '0',
                    'version': '1'
                }
                for section in self.brush2cfg:
                    if section != 'General':
                        temp_cfg[section] = self.brush2cfg[section]
                self.brush2cfg = temp_cfg
        
        if 'BrushGroup.ini' not in os.listdir(self.mdb_path):
            self.brushgroupcfg['0'] = {
                'name': 'New Brushes',
                'expand': 'true'
            }
            with open(os.path.join(self.mdb_path, 'BrushGroup.ini'), 'w') as configfile:
                self.brushgroupcfg.write(configfile)
        else:
            self.brushgroupcfg.read(os.path.join(self.mdb_path, 'BrushGroup.ini'))
            
        
                
        #dictionaries "readable name: actual section name"
        self.default_brushes_dict = self.create_brush_dict(self.defaultcfg, 1)
        self.brush_groups_dict = self.create_brush_dict(self.brushgroupcfg, 0)
        
        #list where str(index) is the actual section name
        self.current_brushes_list = self.current_brushes_list = [f'{self.brush2cfg[section]['name']}, group {self.brush2cfg[section]['group']}' for section in self.brush2cfg.sections()[1:]]
        
        
    #writes into csv files and copies/deletes files
    def save_changes(self, file_deletion_en):
        #regenerate sections
        self.brush2cfg = self.regenerate_sections(self.brush2cfg, 1)
        self.brushgroupcfg = self.regenerate_sections(self.brushgroupcfg, 0)
        
        #write config files
        with open(os.path.join(self.mdb_path, 'Brush2.ini'), 'w') as configfile:
            self.brush2cfg.write(configfile)
        with open(os.path.join(self.mdb_path, 'BrushGroup.ini'), 'w') as configfile:
            self.brushgroupcfg.write(configfile)

        #copy and delete files
        self.file_handler.copy_files('src\\brush_script_src', os.path.join(self.mdb_path, 'brush_script'), self.BSfile_copy_list)
        self.file_handler.copy_files('src\\brush_bitmap_src', os.path.join(self.mdb_path, 'brush_bitmap'), self.BMPfile_copy_list)
        if file_deletion_en:
            self.file_handler.remove_files(os.path.join(self.mdb_path, 'brush_script'), self.BSfile_delete_list)
            self.file_handler.remove_files(os.path.join(self.mdb_path, 'brush_bitmap'), self.BMPfile_delete_list)

    
    #creates formatted str list of brush names
    def regenerate_currbrushlist(self):
        self.current_brushes_list = [f'{self.brush2cfg[section]['name']}, group {self.brush2cfg[section]['group']}' for section in self.brush2cfg.sections()[1:]]
        
    #get list of brush names w/o repeats from the default ini file and w/ repeats for current ini file
    def create_brush_dict(self, cfg_, start_index):
        temp_name_dict = {}
        for section in cfg_.sections()[start_index:]:#section is a string
            temp_name_dict[cfg_[section]['name']] = section
                
        return temp_name_dict
    
    #return str list of entries in a section
    def get_brush_details(self, cfg_, brush_dict, brush_name):
        temp_list = []
        
        if brush_name != 'None Selected' and brush_name != '-1':
            if brush_dict != None:
                cfg_key = brush_dict[brush_name]
            else:
                cfg_key = brush_name
            
            for key in cfg_[cfg_key]:
                temp_list.append(key + ': ' + cfg_[cfg_key][key])
            
        return temp_list
    
    
    def update_current_brushes(self):
        del self.brush2cfg
        self.brush2cfg = cfgp.ConfigParser()
        self.brush2cfg.read(os.path.join(self.mdb_path,'Brush2.ini'))
        self.brush2cfg['General']['activeindex'] = '0'
        self.regenerate_currbrushlist()

        
    def import_brushes(self, import_name_list, group_section_name):
        new_group_made = self.add_group('New Brushes')#create new brush group for new brushes if it doesn't exist

        #update config file------------------------------------------------
        #get brush index (last brush)
        brush_index = len(self.brush2cfg.sections()[1:])
       
        #add new brushes
        for name in import_name_list:
            if name not in [self.brush2cfg[section]['name'] for section in self.brush2cfg.sections()[1:]]:#no importing repeats
                section_entries = self.defaultcfg[self.default_brushes_dict[name]]
                self.brush2cfg.add_section(str(brush_index))
                self.brush2cfg[str(brush_index)] = section_entries
                
                #add files to copy to copy list; remove instances in delete list
                if 'script' in section_entries:
                    self.BSfile_copy_list.append(section_entries['script'])
                    self.BSfile_delete_list = [file for file in self.BSfile_delete_list if file != section_entries['script']]
                elif 'bitmapfile' in section_entries:
                    self.BMPfile_copy_list.append(section_entries['bitmapfile'])
                    self.BMPfile_delete_list = [file for file in self.BMPfile_delete_list if file != section_entries['bitmapfile']]
                
                if group_section_name == '-1':#no group selected
                    group_section_name = self.brush_groups_dict['New Brushes']
                self.brush2cfg[str(brush_index)]['group'] = group_section_name
                brush_index += 1
        self.regenerate_currbrushlist()
        return new_group_made
        
        
    def delete_brushes(self, del_index_list):
        #if file_deletion_en:
        for index in del_index_list:#remove files
            #append files to delete list; remove instances from import list
            section_entries = self.brush2cfg[str(index)]
            if 'script' in section_entries:
                self.BSfile_delete_list.append(section_entries['script'])
                self.BSfile_copy_list = [file for file in self.BSfile_copy_list if file != section_entries['script']]
            elif 'bitmapfile' in section_entries:
                self.BMPfile_delete_list.append(section_entries['bitmapfile'])
                self.BMPfile_copy_list = [file for file in self.BMPfile_copy_list if file != section_entries['bitmapfile']]
                    
        for index in del_index_list:#remove sections in cfg file
            self.brush2cfg.remove_section(str(index))
            
        self.brush2cfg = self.regenerate_sections(self.brush2cfg, 1)
        #print([section for section in self.brush2cfg])

        
    #cfg files are structured with sections being ordered integers
    #after a section deletion, this is called to reorder the sections
    def regenerate_sections(self, cfg_, start_index):
        temp_cfg = cfgp.ConfigParser()
        if start_index == 1:#copy initial section if it exists
            temp_cfg.add_section('General') 
            temp_cfg['General'] = {
                'activeIndex': '0',
                'version': '1'
            }
        i = 0
        for section in cfg_.sections()[start_index:]:#rebuild a new cfg
            temp_cfg.add_section(str(i))
            temp_cfg[str(i)] = cfg_[section]
            i+= 1
            
        return temp_cfg
    
    #==========================================================brush group related=========================================================
    
    #brushes are typically selected by row index, which corresponds to section
    #when filtering by group, the 1:1 correspondance is lost and needs a hash
    def get_relative_hash(self, group_section_name):
        return [int(section) for section in self.brush2cfg.sections()[1:] if self.brush2cfg[section]['group'] == group_section_name]
        
    #returns a formatted str list of brushes when filtered
    def get_filtered_currbrush_list(self, group_section_name):
        return [f'{self.brush2cfg[section]['name']}, group {self.brush2cfg[section]['group']}' for section in self.brush2cfg.sections()[1:] 
                if self.brush2cfg[section]['group'] == group_section_name]
    
    #sets brush group entry of sections selected
    def set_brush_group(self, brush_section_name_list, group_section_name):
        for section in brush_section_name_list:
            self.brush2cfg[str(section)]['group'] = group_section_name
        self.regenerate_currbrushlist()
        
        
    def add_group(self, group_name):
        success = False
        if group_name not in self.brush_groups_dict.keys():
            section_name = str(len(self.brushgroupcfg)-1)
            self.brushgroupcfg.add_section(section_name)
            self.brushgroupcfg[section_name]['name'] = group_name
            self.brushgroupcfg[section_name]['expand'] = 'false'

            self.brush_groups_dict[group_name] = section_name #update dictionary
            success = True
        return success
            

    def get_brush_names_from_group(self, group_section_name):
        return [self.brush2cfg[section]['name'] for section in self.brush2cfg.sections()[1:] 
                if self.brush2cfg[section]['group'] == group_section_name]
    
    def delete_group(self, section_name):
        if section_name in self.brush_groups_dict.values():
            for section in self.brush2cfg.sections()[1:]:
                if self.brush2cfg[section]['group'] == section_name:#unassign brushes in group
                    self.brush2cfg[section]['group'] = '-1'
                if int(self.brush2cfg[section]['group']) > int(section_name):#move up groups of other brushes
                    self.brush2cfg[section]['group'] = str(int(self.brush2cfg[section]['group']) - 1)

            self.regenerate_currbrushlist()
            self.brushgroupcfg.remove_section(section_name)#remove section
            self.brushgroupcfg = self.regenerate_sections(self.brushgroupcfg, 0)#reorder sections
        
        self.brush_groups_dict = self.create_brush_dict(self.brushgroupcfg, 0)#recreate dictionary
        #print([section for section in self.brushgroupcfg])
        
    def rename_group(self, section_name, new_readable_name):
        if section_name in self.brush_groups_dict.values():
            self.brushgroupcfg[section_name]['name'] = new_readable_name
                
            self.brush_groups_dict = self.create_brush_dict(self.brushgroupcfg, 0)#recreate dictionary
        
    def get_formatted_brushgroup_strlist(self):
        return [f'{self.brush_groups_dict[key]}: {key}' for key in self.brush_groups_dict]

            
            