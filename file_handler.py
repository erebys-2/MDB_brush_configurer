import os
import shutil

class file_handler():
    def __init__(self):
        pass
    #notes for implementing import brushes:
    #
    #When you import a brush through medibang it automatically appends an arbitrary 10 digit number infront of the brush name.
    #This is probably to prevent name conflicts for original brushes but can potentially be a pain in the ass.
    #
    #Need to analyze brush scripts to get an idea of how to write a config file section for a brush...
    #
    #Probably create another directory for user provided brushes in \src and update Default.ini on start up
    
    def has_file(self, src_path, file_name):#returns path to file if found
        return file_name in os.listdir(src_path)
    
    def copy_files(self, src_path, dest_path, file_name_list):
        if file_name_list != []:
            for file_name in file_name_list:
                if self.has_file(src_path, file_name) and not self.has_file(dest_path, file_name):
                    shutil.copy(os.path.join(src_path, file_name), dest_path)#shutil copy file to directory
                #     print(f'copy {file_name} success')
                # else:
                #     print(f'copy {file_name} failed: in src={self.has_file(src_path, file_name)}, not in dest={not self.has_file(dest_path, file_name)}')
        
        
    def remove_files(self, src_path, file_name_list):
        if file_name_list != []:
            for file_name in file_name_list:
                if self.has_file(src_path, file_name):
                    os.remove(os.path.join(src_path, file_name))
