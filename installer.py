#!/usr/bin/env python
# encoding: utf-8

# --------------------------------------------------------
# file: installer.py
# Copyright(c) 2017-2020 SeetaTech
# Written by Zhuang Liu
# 10:34
# --------------------------------------------------------

from PyInstaller.__main__ import run

# -F: pack to a single exe file
# -D: pack to a folder
# -w: without console
# --path: dependencies
# --icon: icon
# --noupx: without upx zip
# --clean: clean temp files

if __name__ == '__main__':
    # for single exe file
    opts_single=['-F', '-w', '--paths=C:/ProgramData/Anaconda2/envs/labelimg-installer3.5/Lib/site-packages/PyQt5/Qt',
          '--paths=C:/ProgramData/Anaconda2/envs/labelimg-installer3.5/Lib/site-packages/PyQt5/Qt/plugins/',
          '--paths=./libs', 'labelImg.py']

    # for folder
    opts_folder=['-D', '-w', '--paths=C:/ProgramData/Anaconda2/envs/labelimg-installer3.5/Lib/site-packages/PyQt5/Qt',
          '--paths=C:/ProgramData/Anaconda2/envs/labelimg-installer3.5/Lib/site-packages/PyQt5/Qt/plugins/',
          '--paths=./libs', 'labelImg.py',
          '--distpath=./dist/labelRBox20210527-folder/']
    run(opts_folder)