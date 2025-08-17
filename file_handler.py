import os
import shutil

class file_handler():
    def __init__(self):
        pass
    #notes for implementing import brushes:
    #
    #When you import a brush through medibang it automatically appends an arbitrary 10 digit number infront of the brush file name.
    #This is probably to prevent name conflicts for original brushes but can potentially be a pain in the ass.
    #
    #Need to analyze brush scripts to get an idea of how to write a config file section for a brush...
    #
    #Probably create another directory for user provided brushes in \src and update Default.ini on start up
    
    def has_file(self, src_path, file_name):#returns path to file if found
        return file_name in os.listdir(src_path)
    
    def get_name_and_ext(self, file_name):
        i = 0
        for char in file_name:
            if char == '.':
                break
            i += 1
        return(file_name[:i], file_name[i:])
    
    def get_new_name(self, src_path, file_name):
        n = 0
        name, ext = self.get_name_and_ext(file_name)
        
        while file_name in os.listdir(src_path):
            n += 1
            file_name = name + '_' + str(n) + ext
            
        return file_name
    
    def check_for_loose_files(self, src_path):
        found = False
        for file_name in os.listdir(src_path):
            name, ext = self.get_name_and_ext(file_name)
            if ext in ('.bs', '.png', '.PNG', '.mdp'):
                found = True
                break
        return found
    
    def create_brush_list_from_files(self, src_path):
        rtn_list = []
        for file_name in os.listdir(src_path):
            name, ext = self.get_name_and_ext(file_name)
            if ext in ('.bs', '.png', '.PNG', '.mdp'):
                if ext == '.bs':
                    brush_type = 'program'
                    file_type = 'script'
                else:
                    brush_type = 'bitmap'
                    file_type = 'bitmapfile'
                
                tempdict = {
                    'name': name,
                    'type': brush_type,
                    'group': '-1',
                    'width': '15',
                    'min': '5',
                    'opacity': '1',
                    'psize': 'True',
                    'palpha': 'True', 
                    'cloudid': '-1',
                    'clouduuid': '',
                    file_type: file_name                
                    }
                
                extended_dict = {
                    'option': '50',
                    'option2': '0',
                    'option3': '50',
                    'option4': '0',
                    'option5': '1',
                    'option6': '0',
                    'option7': '0'
                    }
                
                if brush_type == 'bitmap':
                    tempdict.update(extended_dict)
            
                rtn_list.append(tempdict)
            
        return rtn_list
        
    
    def organize_brush_list_folder(self, src_path, has_dupes):#call after creating a cfg file
        #check for and create directories
        if 'brush_script' not in os.listdir(src_path):
            os.mkdir(os.path.join(src_path, 'brush_script'))
        if 'brush_bitmap' not in os.listdir(src_path):
            os.mkdir(os.path.join(src_path, 'brush_bitmap'))
        if has_dupes and 'duplicate_files' not in os.listdir(src_path):
            os.mkdir(os.path.join(src_path, 'duplicate_files'))
        
        #move brushes into respective folders
        for file_name in os.listdir(src_path):
            name, ext = self.get_name_and_ext(file_name)
            file_path = os.path.join(src_path, file_name)
            if has_dupes:
                dupes_path = os.path.join(src_path, 'duplicate_files')
                
            if ext == '.bs':
                copy_path = os.path.join(src_path, 'brush_script')
                if not self.has_file(copy_path, file_name):
                    shutil.move(file_path, copy_path)
                elif has_dupes:
                    shutil.move(file_path, dupes_path)
                else:
                    os.remove(file_path)
            elif ext in ('.PNG', '.png', '.mdp'):
                copy_path = os.path.join(src_path, 'brush_bitmap')
                if not self.has_file(copy_path, file_name):
                    shutil.move(file_path, copy_path)
                elif has_dupes:
                    shutil.move(file_path, dupes_path)
                else:
                    os.remove(file_path)
                
                
    
    def copy_files(self, src_path, dest_path, file_name_dict):
        if file_name_dict != {}:
            for file_name in file_name_dict:
                if self.has_file(src_path, file_name):
                    shutil.copy(os.path.join(src_path, file_name), os.path.join(dest_path, file_name_dict[file_name]))#shutil copy file to directory
                    print(f'copy {file_name} success')
                else:
                    print(f'copy {file_name} failed: in src={self.has_file(src_path, file_name)}')
        
        
    def remove_files(self, src_path, file_name_list):
        if file_name_list != []:
            for file_name in file_name_list:
                if self.has_file(src_path, file_name):
                    os.remove(os.path.join(src_path, file_name))
