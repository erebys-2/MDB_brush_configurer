import configparser as cfgp
import os
from file_handler import file_handler as fh
from xml_handler import xml_handler as xmlh
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
    
    def get_import_path(self):
        return self.pathcfg['Import Path']['path']
    
    def set_path(self, section, path_str):
        self.pathcfg[section]['path'] = path_str
        with open('src/CurrentPath.ini', 'w') as configfile:
            self.pathcfg.write(configfile)
        

class cfg_handler():#cfg handler class responsible for main functionalities
    def __init__(self):
        pathcfg = path_cfg_handler()#get path to config files
        self.mdb_path = pathcfg.get_curr_path()
        self.import_path = pathcfg.get_import_path()
        del pathcfg
        
        self.file_handler = fh()#create file handler
        self.xml_handler = xmlh()
        
        self.newcfg = cfgp.ConfigParser()
        if 'BrushNew.xml' in os.listdir(self.import_path):#Fire Alpaca uses xml to store brush config data, generate ini from xml
            self.newcfg['General'] = {
                'activeIndex': '0',
                'version': '1'
            }
            section = 0
            for brush_datadict in self.xml_handler.brush_list:
                self.newcfg[str(section)] = brush_datadict
                section += 1 
            with open(os.path.join(self.import_path, 'Brush2.ini'), 'w', encoding='UTF-8') as configfile:
                self.newcfg.write(configfile)
                
        elif self.file_handler.check_for_loose_files(self.import_path):#check if current brush list directory has loose brush files eg .bs, .mdp, .png
            brush_list = self.file_handler.create_brush_list_from_files(self.import_path)#create list of dictionaries using inferred default values
            
            if 'Brush2.ini' not in os.listdir(self.import_path):#create new Brush2.ini if not found
                self.newcfg['General'] = {
                    'activeIndex': '0',
                    'version': '1'
                }
                section = 0
                for brush_datadict in brush_list:
                    self.newcfg[str(section)] = brush_datadict
                    section += 1 
                with open(os.path.join(self.import_path, 'Brush2.ini'), 'w', encoding='UTF-8') as configfile:
                    self.newcfg.write(configfile)
            else:
                self.newcfg.read(f'{self.import_path}/Brush2.ini', encoding='UTF-8')
                section = len(self.newcfg.sections()[1:])
                for brush_datadict in brush_list:
                    self.newcfg[str(section)] = brush_datadict
                    section += 1 
                with open(os.path.join(self.import_path, 'Brush2.ini'), 'w', encoding='UTF-8') as configfile:
                    self.newcfg.write(configfile)
                
            self.file_handler.organize_brush_list_folder(self.import_path)
        
        self.newcfg.read(f'{self.import_path}/Brush2.ini', encoding='UTF-8')
        
        self.brush2cfg = cfgp.ConfigParser()
        self.brushgroupcfg = cfgp.ConfigParser()
        
        self.BMPfile_delete_list = []
        self.BMPfile_copy_dict = {}
        self.BSfile_delete_list = []
        self.BSfile_copy_dict = {}
        
        # self.TEXfile_delete_list = []
        # self.TEXfile_copy_list = []
        
        #add ini files if not present directly to mdb_path
        if 'Brush2.ini' not in os.listdir(self.mdb_path):
            self.brush2cfg['General'] = {
                'activeIndex': '0',
                'version': '1'
            }
            with open(os.path.join(self.mdb_path, 'Brush2.ini'), 'w', encoding='UTF-8') as configfile:
                self.brush2cfg.write(configfile)
        else:
            self.brush2cfg.read(os.path.join(self.mdb_path, 'Brush2.ini'), encoding='UTF-8')
            #bring 'General' section to top
            if self.brush2cfg.sections().index('General') != 0:
                temp_cfg = cfgp.ConfigParser()#create tempcfg with general section
                temp_cfg['General'] = {
                    'activeIndex': '0',
                    'version': '1'
                }
                for section in self.brush2cfg:#move sections that aren't general over to tempcfg
                    if section != 'General':
                        temp_cfg[section] = self.brush2cfg[section]
                self.brush2cfg = temp_cfg
        
        if 'BrushGroup.ini' not in os.listdir(self.mdb_path):
            self.brushgroupcfg['0'] = {
                'name': 'New Brushes',
                'expand': 'true'
            }
            with open(os.path.join(self.mdb_path, 'BrushGroup.ini'), 'w', encoding='UTF-8') as configfile:
                self.brushgroupcfg.write(configfile)
        else:
            self.brushgroupcfg.read(os.path.join(self.mdb_path, 'BrushGroup.ini'), encoding='UTF-8')
            
        
                
        #dictionaries "readable name: actual section name"
        self.new_brushes_dict = self.create_brush_dict(self.newcfg, 1)
        self.brush_groups_dict = self.create_brush_dict(self.brushgroupcfg, 0)
        
        #list where str(index) is the actual section name
        self.current_brushes_list = self.current_brushes_list = [f'{self.brush2cfg[section]['name']}, group {self.brush2cfg[section]['group']}' for section in self.brush2cfg.sections()[1:]]
        
        
    #writes into csv files and copies/deletes files
    def save_changes(self, file_deletion_en):
        #regenerate sections
        self.brush2cfg = self.regenerate_sections(self.brush2cfg, 1)
        self.brushgroupcfg = self.regenerate_sections(self.brushgroupcfg, 0)
        
        #write config files
        with open(os.path.join(self.mdb_path, 'Brush2.ini'), 'w', encoding='UTF-8') as configfile:
            self.brush2cfg.write(configfile)
        with open(os.path.join(self.mdb_path, 'BrushGroup.ini'), 'w', encoding='UTF-8') as configfile:
            self.brushgroupcfg.write(configfile)
        
        #copy and delete files
        self.file_handler.copy_files(os.path.join(self.import_path, 'brush_script'), os.path.join(self.mdb_path, 'brush_script'), self.BSfile_copy_dict)
        self.file_handler.copy_files(os.path.join(self.import_path, 'brush_bitmap'), os.path.join(self.mdb_path, 'brush_bitmap'), self.BMPfile_copy_dict)
        if file_deletion_en:
            self.file_handler.remove_files(os.path.join(self.mdb_path, 'brush_script'), self.BSfile_delete_list)
            self.file_handler.remove_files(os.path.join(self.mdb_path, 'brush_bitmap'), self.BMPfile_delete_list)
            
        # if 'brush_texture' in os.listdir(self.mdb_path):
        #     self.file_handler.copy_files(os.path.join(self.import_path, 'brush_texture'), os.path.join(self.mdb_path, 'brush_texture'), self.TEXfile_copy_list)
        #     if file_deletion_en:
        #         self.file_handler.remove_files(os.path.join(self.mdb_path, 'brush_texture'), self.TEXfile_delete_list)
        # elif self.TEXfile_copy_list != []:#the brush_texture directory doens't exist and the copy file list isn't empty
        #     os.mkdir(os.path.join(self.mdb_path, 'brush_texture'))
        #     self.file_handler.copy_files(os.path.join(self.import_path, 'brush_texture'), os.path.join(self.mdb_path, 'brush_texture'), self.TEXfile_copy_list)
        
        #reset dictionaries and lists
        self.BMPfile_delete_list = []
        self.BMPfile_copy_dict = {}
        self.BSfile_delete_list = []
        self.BSfile_copy_dict = {}
            
        

    
    #creates formatted str list of brush names
    def regenerate_currbrushlist(self):
        self.current_brushes_list = [f'{self.brush2cfg[section]['name']}, group {self.brush2cfg[section]['group']}' for section in self.brush2cfg.sections()[1:]]
        
    #get list of brush names w/o repeats from the new ini file and w/ repeats for current ini file
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
    
    
    def import_brushes(self, import_name_list, group_section_name):
        new_group_made = self.add_group('New Brushes')#create new brush group for new brushes if it doesn't exist

        #update config file------------------------------------------------
        #get brush index (last brush)
        brush_index = len(self.brush2cfg.sections()[1:])
       
        #add new brushes
        for name in import_name_list:
            #if name not in [self.brush2cfg[section]['name'] for section in self.brush2cfg.sections()[1:]]:#no importing repeats
            section_entries = self.newcfg[self.new_brushes_dict[name]]
            if (('script' in section_entries and section_entries['script'] not in self.BSfile_copy_dict) or 
                ('bitmapfile' in section_entries and section_entries['bitmapfile'] not in self.BMPfile_copy_dict)
                ):
                self.brush2cfg.add_section(str(brush_index))
                self.brush2cfg[str(brush_index)] = section_entries
                
                #add files to copy to copy list
                if 'script' in section_entries:#copying files operates on unmodified names
                    new_name = self.file_handler.get_new_name(os.path.join(self.mdb_path, 'brush_script'), section_entries['script'])
                    self.BSfile_copy_dict[section_entries['script']] = new_name
                    self.brush2cfg[str(brush_index)]['script'] = new_name
                    
                elif 'bitmapfile' in section_entries:
                    new_name = self.file_handler.get_new_name(os.path.join(self.mdb_path, 'brush_bitmap'), section_entries['bitmapfile'])
                    self.BMPfile_copy_dict[section_entries['bitmapfile']] = new_name
                    self.brush2cfg[str(brush_index)]['bitmapfile'] = new_name

                # if 'texfile' in section_entries:
                #     self.TEXfile_copy_list.append(section_entries['texfile'])
                    #self.TEXfile_delete_list = [file for file in self.TEXfile_delete_list if file != section_entries['texfile']]
                
                if group_section_name == '-1':#no group selected
                    group_section_name = self.brush_groups_dict['New Brushes']
                self.brush2cfg[str(brush_index)]['group'] = group_section_name
                brush_index += 1
        self.regenerate_currbrushlist()
        return new_group_made
        
        
    def delete_brushes(self, del_index_list):#operates on actual brush names
        #if file_deletion_en:
        for index in del_index_list:#remove files
            #append files to delete list
            section_entries = self.brush2cfg[str(index)]
            if 'script' in section_entries:
                self.BSfile_delete_list.append(section_entries['script'])
                
            elif 'bitmapfile' in section_entries:
                self.BMPfile_delete_list.append(section_entries['bitmapfile'])
                
            # if 'texfile' in section_entries:
            #     self.TEXfile_delete_list.append(section_entries['texfile'])
                #self.TEXfile_copy_list = [file for file in self.TEXfile_copy_list if file != section_entries['texfile']]
                    
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
        
    def copy_brushes_to_group(self, brush_section_name_list, group_section_name):
        i = len(self.brush2cfg.sections()[1:])
        for section in brush_section_name_list:
            self.brush2cfg.add_section(str(i))
            self.brush2cfg[str(i)] = self.brush2cfg[str(section)]
            self.brush2cfg[str(i)]['group'] = group_section_name
            i+=1
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

            
            