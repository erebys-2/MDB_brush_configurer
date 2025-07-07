import configparser as cfgp
import os
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
        pathcfg = path_cfg_handler()
        self.mdb_path = pathcfg.get_curr_path()
        del pathcfg
        
        self.defaultcfg = cfgp.ConfigParser()
        self.defaultcfg.read('src/Default.ini')

        self.brush2cfg = cfgp.ConfigParser()
        self.brush2cfg.read(os.path.join(self.mdb_path, 'Brush2.ini'))
        
        self.brushgroupcfg = cfgp.ConfigParser()
        self.brushgroupcfg.read(os.path.join(self.mdb_path,'BrushGroup.ini'))
                
        #dictionaries "readable name: actual section name"
        self.default_brushes = self.create_brush_dict(self.defaultcfg, 1)
        self.brush_groups = self.create_brush_dict(self.brushgroupcfg, 0)
        
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
        self.current_brushes_list = [f'{self.brush2cfg[section]['name']}, group {self.brush2cfg[section]['group']}' for section in self.brush2cfg.sections()[1:]]
            
        
    def import_brushes(self, import_name_list, group_actual_name):
        new_group_made = self.add_group('New Brushes')#create new brush group for new brushes if it doesn't exist
        brush_import_file_list = []
        
        #update config file------------------------------------------------
        #get brush index (last brush)
        brush_index = len(self.brush2cfg.sections()[1:])
       
        #add new brushes
        for name in import_name_list:
            new_section_data = self.defaultcfg[self.default_brushes[name]]
            self.brush2cfg.add_section(str(brush_index))
            self.brush2cfg[str(brush_index)] = new_section_data
            
            if 'script' in new_section_data:
                brush_import_file_list.append(new_section_data['script'])
            elif 'bitmapfile' in new_section_data:
                brush_import_file_list.append(new_section_data['bitmapfile'])
            
            if group_actual_name == '-1':#no group selected
                group_actual_name = self.brush_groups['New Brushes']
            self.brush2cfg[str(brush_index)]['group'] = group_actual_name
            brush_index += 1
            
        #write file
        with open(os.path.join(self.mdb_path, 'Brush2.ini'), 'w') as configfile:
            self.brush2cfg.write(configfile)
        
        self.update_current_brushes()
        
        #check brush files and add if not found---------------------------------
        print(brush_import_file_list)
        
        return new_group_made
        
        
    def delete_brushes(self, del_index_list):
        for index in del_index_list:#remove sections
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
    
    
    def set_brush_group(self, brush_name_list, real_group_name):
        for name in brush_name_list:
            self.brush2cfg[self.current_brushes_list[name]]['group'] = real_group_name
            
        with open(os.path.join(self.mdb_path, 'Brush2.ini'), 'w') as configfile:
            self.brush2cfg.write(configfile)
            
        
    def add_group(self, group_name):
        success = False
        if group_name not in self.brush_groups.keys():
            section_name = str(len(self.brushgroupcfg)-1)
            self.brushgroupcfg.add_section(section_name)
            self.brushgroupcfg[section_name]['name'] = group_name
            self.brushgroupcfg[section_name]['expand'] = 'false'
            with open(os.path.join(self.mdb_path, 'BrushGroup.ini'), 'w') as configfile:
                self.brushgroupcfg.write(configfile)
            
            self.brush_groups[group_name] = section_name #update dictionary
            success = True
        return success
            

    def get_brush_names_from_group(self, real_group_name):
        return [self.brush2cfg[section]['name'] for section in self.brush2cfg.sections()[1:] 
                if self.brush2cfg[section]['group'] == real_group_name]
    
    def delete_group(self, real_group_name):
        if real_group_name in self.brush_groups.values():
            for section in self.brush2cfg.sections()[1:]:
                if self.brush2cfg[section]['group'] == real_group_name:#unassign brushes in group
                    self.brush2cfg[section]['group'] = '-1'
                if int(self.brush2cfg[section]['group']) > int(real_group_name):#move up groups of other brushes
                    self.brush2cfg[section]['group'] = str(int(self.brush2cfg[section]['group']) - 1)
            with open(os.path.join(self.mdb_path, 'Brush2.ini'), 'w') as configfile:
                self.brush2cfg.write(configfile)
            self.regenerate_currbrushlist()
                
            self.brushgroupcfg.remove_section(real_group_name)#remove section
            
            temp_cfg = self.regenerate_sections(self.brushgroupcfg, 0)#reorder sections
            with open(os.path.join(self.mdb_path, 'BrushGroup.ini'), 'w') as configfile:
                temp_cfg.write(configfile)
                
        del self.brushgroupcfg #some object problem in python..?
        self.brushgroupcfg = cfgp.ConfigParser()
        self.brushgroupcfg.read(os.path.join(self.mdb_path,'BrushGroup.ini'))
        
        self.brush_groups = self.create_brush_dict(self.brushgroupcfg, 0)#recreate dictionary

            
            