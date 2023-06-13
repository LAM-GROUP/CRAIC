import sys
import yaml
from descriptors._base import Descriptor
#from classification._base import Classifier

def createDescriptor(data: dict) -> Descriptor:
    # Check that only one descriptor is defined
    dTypes = ['Steinhardt']
    count = 0
    for key in data:
        if key in dTypes:
            count += 1
    if count > 1: # If more than one defined, exit
        print('More than one descriptor type defined')
        print('Please define only one descriptor in yaml file')
        exit()
    elif count == 0: # If none defined, exit
        print('No descriptor has been defined')
        print('Please define a descriptor in yaml file')
        exit()
    
    # Create the corresponding descriptor type and return it
    if 'Steinhardt' in data:
        from descriptors.steinhardt import Steinhardt
        return Steinhardt(data['Steinhardt'])

# Known top-level keywords
keywords = ['GMM', 'Steinhardt']

def yaml_reader(filename: str) -> None:
    # Read yaml file and create descriptor and classification classes
    with open(filename) as f:
        data = yaml.safe_load(f)

    # Check for undefined keywords
    for key in data:
        if key in keywords:
            pass
        else:
            print('Unknown top-level keyword: ', key)
            exit()
    
    steinhardt = createDescriptor(data)