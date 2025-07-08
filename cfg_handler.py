import configparser as cfgp
import os
from file_handler import file_handler as fh
#File contains cfg parser related classes

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
        self.brush2cfg.read(os.path.join(self.mdb_path, 'Brush2.ini'))
        
        self.brushgroupcfg = cfgp.ConfigParser()
        self.brushgroupcfg.read(os.path.join(self.mdb_path,'BrushGroup.ini'))
                
        #dictionaries "readable name: actual section name"
        self.default_brushes_dict = self.create_brush_dict(self.defaultcfg, 1)
        self.brush_groups_dict = self.create_brush_dict(self.brushgroupcfg, 0)
        
        #list where str(index) is the actual section name
        self.current_brushes_list = [f'{self.brush2cfg[section]['name']}, group {self.brush2cfg[section]['group']}' for section in self.brush2cfg.sections()[1:]]
            
            
    def regenerate_currbrushlist(self):
        self.current_brushes_list = [f'{self.brush2cfg[section]['name']}, group {self.brush2cfg[section]['group']}' for section in self.brush2cfg.sections()[1:]]
        
    #get list of brush names w/o repeats from the default ini file and w/ repeats for current ini file

    def create_brush_dict(self, cfg_, start_index):
        temp_name_dict = {}
        for section in cfg_.sections()[start_index:]:#section is a string
            temp_name_dict[cfg_[section]['name']] = section
                
        return temp_name_dict
    
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
        #self.current_brushes_list = [f'{self.brush2cfg[section]['name']}, group {self.brush2cfg[section]['group']}' for section in self.brush2cfg.sections()[1:]]
            
        
    def import_brushes(self, import_name_list, group_section_name):
        new_group_made = self.add_group('New Brushes')#create new brush group for new brushes if it doesn't exist
        BSfile_list = []
        BMPfile_list = []
        
        #update config file------------------------------------------------
        #get brush index (last brush)
        brush_index = len(self.brush2cfg.sections()[1:])
       
        #add new brushes
        for name in import_name_list:
            section_entries = self.defaultcfg[self.default_brushes_dict[name]]
            self.brush2cfg.add_section(str(brush_index))
            self.brush2cfg[str(brush_index)] = section_entries
            
            if 'script' in section_entries:
                BSfile_list.append(section_entries['script'])
            elif 'bitmapfile' in section_entries:
                BMPfile_list.append(section_entries['bitmapfile'])
            
            if group_section_name == '-1':#no group selected
                group_section_name = self.brush_groups_dict['New Brushes']
            self.brush2cfg[str(brush_index)]['group'] = group_section_name
            brush_index += 1
            
        #write file
        with open(os.path.join(self.mdb_path, 'Brush2.ini'), 'w') as configfile:
            self.brush2cfg.write(configfile)
        
        self.update_current_brushes()
        
        #check brush files and add if it exists in src and not found in dest---------------------------------
        self.file_handler.copy_files('src\\brush_script_src', os.path.join(self.mdb_path, 'brush_script'), BSfile_list)
        self.file_handler.copy_files('src\\brush_bitmap_src', os.path.join(self.mdb_path, 'brush_bitmap'), BMPfile_list)
        
        return new_group_made
        
        
    def delete_brushes(self, del_index_list, file_deletion_en):
        BSfile_list = []
        BMPfile_list = []
        for index in del_index_list:#remove files
            section_entries = self.brush2cfg[str(index)]
            if 'script' in section_entries:
                BSfile_list.append(section_entries['script'])
            elif 'bitmapfile' in section_entries:
                BMPfile_list.append(section_entries['bitmapfile'])
        if file_deletion_en:
            self.file_handler.remove_files(os.path.join(self.mdb_path, 'brush_script'), BSfile_list)
            self.file_handler.remove_files(os.path.join(self.mdb_path, 'brush_bitmap'), BMPfile_list)
            
        
        for index in del_index_list:#remove sections in cfg file
            self.brush2cfg.remove_section(str(index))
            
        temp_cfg = self.regenerate_sections(self.brush2cfg, 1)#reorder sections
        
        with open(os.path.join(self.mdb_path, 'Brush2.ini'), 'w') as configfile:#write file
                temp_cfg.write(configfile)
 
        self.update_current_brushes()
        
        
    def regenerate_sections(self, cfg_, start_index):
        temp_cfg = cfgp.ConfigParser()
        if start_index == 1:#copy initial section if it exists
            temp_cfg.add_section('General') 
            temp_cfg['General'] = cfg_['General']
        
        i = 0
        for section in cfg_.sections()[start_index:]:#rebuild a new cfg
            temp_cfg.add_section(str(i))
            temp_cfg[str(i)] = cfg_[section]
            i+= 1
            
        return temp_cfg
    
    #brush group related
    def get_relative_hash(self, group_section_name):
        return [int(section) for section in self.brush2cfg.sections()[1:] if self.brush2cfg[section]['group'] == group_section_name]
        
    def get_filtered_currbrush_list(self, group_section_name):
        return [f'{self.brush2cfg[section]['name']}, group {self.brush2cfg[section]['group']}' for section in self.brush2cfg.sections()[1:] 
                if self.brush2cfg[section]['group'] == group_section_name]
    
    
    
    
    def set_brush_group(self, brush_name_section_list, group_section_name):
        for section in brush_name_section_list:
            self.brush2cfg[str(section)]['group'] = group_section_name
            
        with open(os.path.join(self.mdb_path, 'Brush2.ini'), 'w') as configfile:
            self.brush2cfg.write(configfile)
            
        
    def add_group(self, group_name):
        success = False
        if group_name not in self.brush_groups_dict.keys():
            section_name = str(len(self.brushgroupcfg)-1)
            self.brushgroupcfg.add_section(section_name)
            self.brushgroupcfg[section_name]['name'] = group_name
            self.brushgroupcfg[section_name]['expand'] = 'false'
            with open(os.path.join(self.mdb_path, 'BrushGroup.ini'), 'w') as configfile:
                self.brushgroupcfg.write(configfile)
            
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
            with open(os.path.join(self.mdb_path, 'Brush2.ini'), 'w') as configfile:
                self.brush2cfg.write(configfile)
            self.regenerate_currbrushlist()
                
            self.brushgroupcfg.remove_section(section_name)#remove section
            
            temp_cfg = self.regenerate_sections(self.brushgroupcfg, 0)#reorder sections
            with open(os.path.join(self.mdb_path, 'BrushGroup.ini'), 'w') as configfile:
                temp_cfg.write(configfile)
                
        del self.brushgroupcfg #some object problem in python makes it so I need to manually recreate the obj..?
        self.brushgroupcfg = cfgp.ConfigParser()
        self.brushgroupcfg.read(os.path.join(self.mdb_path,'BrushGroup.ini'))
        
        self.brush_groups_dict = self.create_brush_dict(self.brushgroupcfg, 0)#recreate dictionary
        
    def rename_group(self, section_name, new_readable_name):
        if section_name in self.brush_groups_dict.values():
            self.brushgroupcfg[section_name]['name'] = new_readable_name
            with open(os.path.join(self.mdb_path, 'BrushGroup.ini'), 'w') as configfile:
                self.brushgroupcfg.write(configfile)
                
            self.brush_groups_dict = self.create_brush_dict(self.brushgroupcfg, 0)#recreate dictionary
        
    def get_formatted_brushgroup_strlist(self):
        return [f'{self.brush_groups_dict[key]}: {key}' for key in self.brush_groups_dict]

            
            