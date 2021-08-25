
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 20 22:11:25 2021

@author: yuqian
"""

import tempfile

import pydicom
from pydicom.data import get_testdata_files
import linecache
import pandas as pd
import numpy as np
import os

import shutil


def get_file(path):
    files = []
    if not os.path.exists(path):
        return -1
    for filepath, dirs, names in os.walk(path):
        for filename in names:
                files.append(os.path.join(filepath, filename))
    return files


def get_folders(path):
    folders = []
    if not os.path.exists(path):
        return -1
    for filepath, dirs, names in os.walk(path):
        for name in names:
            if name.endswith('dcm'):
                #print(filepath)
                folder=os.path.join(filepath,name)
                folders.append(folder)
                #print(folder);
            else:
                portion = os.path.splitext(name);
                newname = portion[0] + '.dcm';
                os.rename(os.path.join(filepath,name),os.path.join(filepath, newname))
                folder = os.path.join(filepath,newname);
                folders.append(folder);
                #print("renamed:",folder);            
    return folders

def get_paths(path):
    paths = []
    if not os.path.exists(path):
        return -1
    for filepath, dirs, names in os.walk(path):
        for name in names:
            if name.endswith('dcm'):
                #print(filepath)
                path=filepath
                paths.append(path)
                #print(folder);
    folder_path=pd.DataFrame(columns=('path','a'));
    for path in paths:
        img_dir = path
        row={'path':img_dir}
        folder_path = folder_path.append(row,ignore_index=True);
    return folder_path

def get_metadata(folders):
    df=pd.DataFrame(columns=('img_dir','AcquisitionTime',
                             #'PatientBirthDate','StudyInstanceUID','SeriesInstanceUID','SeriesDescription'
                             ));
    df_error=pd.DataFrame(columns=('error_folder','error_name'));
    for folder in folders:
        #print(folder);
        img_dir = folder;
        dataset = pydicom.dcmread(img_dir);
        print(img_dir,dataset.PatientName);
        # PatientName = dataset.PatientName;
        # StudyInstanceUID = dataset.StudyInstanceUID;
        # PatientBirthDate = dataset.PatientBirthDate;
        # SeriesInstanceUID = dataset.SeriesInstanceUID;
        # SeriesDescription = dataset.SeriesDescription;
        # print(PatientName,PatientBirthDate,SeriesDescription);
        row={'img_dir':img_dir,
        'AcquisitionTime':dataset.AcquisitionTime,
        #'PatientBirthDate':dataset.PatientBirthDate,
        #'PatientName':dataset.PatientName,
        #'SeriesInstanceUID':dataset.SeriesInstanceUID,
        #'SeriesDescription':dataset.SeriesDescription,
        };
        df = df.append(row,ignore_index=True);
    return df

folders = get_folders(r'F:\CT_HVPG_QXL\test');
df = get_metadata(folders);
paths = get_paths(r'F:\CT_HVPG_QXL\test')

tar_path=paths[['path']]
tar_folder=df[['AcquisitionTime']]
tar_filename=tar_path.join(tar_folder)
nonerepeat_tar_filename = tar_filename.drop_duplicates(subset=['AcquisitionTime'], keep='first')
#nonerepeat_paths = paths.drop_duplicates(subset=['AcquisitionTime'], keep='first')

phase_no=nonerepeat_tar_filename.shape[0]

i=0
while i<phase_no:
    path=os.path.join(nonerepeat_tar_filename.iat[i,0],nonerepeat_tar_filename.iat[i,1])
    os.makedirs(path)
    print(path)
    i=i+1

df_down=df.sort_values('AcquisitionTime',axis = 0,ascending = True)
nonerepeat_tar_filename_down = nonerepeat_tar_filename.sort_values('AcquisitionTime',axis = 0,ascending = True)

i=0
n=0
while i<phase_no:
    a = df_down.iat[n,1]
    b = nonerepeat_tar_filename_down.iat[i,1]
    if a==b:
        ori_path=df_down.iat[n,0]
        tar_path=os.path.join(nonerepeat_tar_filename_down.iat[i,0],nonerepeat_tar_filename_down.iat[i,1])
        shutil.move(ori_path,tar_path)
        print(nonerepeat_tar_filename_down.iat[i,1],i,n)
        n=n+1
    else:
        i=i+1
        print(i)
    


#print(df.head())
    
#以患者studyID为索引删掉重复项，一个病人有多个序列改成序列号

#nonerepeat_df = df.drop_duplicates(subset=['SeriesInstanceUID'], keep='first')
#writer = pd.ExcelWriter(r'F:\CT_HVPG_QXL\test\LIST.xlsx')
#nonerepeat_df.to_excel(writer)
#df.to_excel(writer)
#writer.save()