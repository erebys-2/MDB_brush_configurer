import os
import xml.etree.ElementTree as ET

class xml_handler():
    def __init__(self):
        tree = ET.parse(r"src\\brush_lists\\FireAlpaca_brushes\\BrushNew.xml")
        root = tree.getroot()
        self.brush_list = self.format_brush_list(self.get_brush_list(root))
        #print(self.brush_list)
       
    def get_brush_list(self, root):
        brush_list = []
        for child in root:
            if child.tag == 'Brushes':
                brush_list = [brush.attrib for brush in child]      
        return brush_list  
    
    def specify_file_type(self, file_name):
        key = ''
        if '.bs' in file_name:
            key = 'script'
        elif '.mdp' in file_name or '.png' in file_name:
            key = 'bitmapfile'
        return key
    
    def order_dict(self, input_dict):
        param_order_list = [
            'name',
            'type',
            'group',
            'width',
            'min',
            'opacity',
            'psize',
            'palpha',
            'cloudid',
            'clouduuid'
        ]
        output_dict = {key: input_dict[key] for key in param_order_list if key in input_dict}
        #add remaining keys
        output_dict.update({key: input_dict[key] for key in input_dict if key not in param_order_list})
        
        #update 
        return output_dict
            
    def format_brush_list(self, brush_list):
        rtn_list = []
        param_map = {
            'R': 'width',
            'minR': 'min',
            'alpha': 'opacity',
            'pressWidth': 'psize',
            'pressTrans': 'palpha',
            'softedge': 'pedge'
        }

        for brush in brush_list:
            tempdict = {}
            for param in brush:#translate differences in parameters
                if param in param_map:
                    tempdict[param_map[param]] = str(brush[param])
                elif param == 'file':
                    tempdict[self.specify_file_type(brush[param])] = str(brush[param])
                elif param[:6] == 'option':
                    if param == 'option0':
                        tempdict['option'] = str(brush[param])
                    else:
                        tempdict[f'option{int(param[6:])+1}'] = str(brush[param])
                elif param == 'type':
                    if str(brush[param]) == 'bitmapwc':
                        tempdict[param] = 'bitmapWc'
                    elif str(brush[param]) == 'roller':
                        tempdict[param] = 'bitmap'
                    else:
                        tempdict[param] = str(brush[param])
                elif param in ('name', 'irinuki'):#do not add all FA params
                    tempdict[param] = str(brush[param])
            #add medibang specific params:
            tempdict['cloudid'] = '-1'
            tempdict['clouduuid'] = ''
            tempdict['group'] = '-1'

            #append formatted dict to rtn_list
            rtn_list.append(self.order_dict(tempdict))
            
        return rtn_list

#testing
# xmlh1 = xml_handler()

