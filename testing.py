import os
import shutil

for root, dirs, files in os.walk('C:\\Users\\Fabrizio\\Desktop\\imgpics\\unit'):  # replace the . with your starting directory
    for file in files:
        path_file = os.path.join(root, file)
        if path_file[-6:] == '00.png':
            print(path_file)
            shutil.copy(path_file, 'C:/Users/Fabrizio/Desktop/imgpics/pics/'+file)
