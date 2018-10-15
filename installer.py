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
# -w: without console
# --path: dependencies
# --icon: icon
# --noupx: without upx zip
# --clean: clean temp files

if __name__ == '__main__':
    opts=['-F', '-w', '--paths=C:/ProgramData/Anaconda2/envs/labelimg-installer3.5/Lib/site-packages/PyQt5/',
          '--paths=C:/ProgramData/Anaconda2/envs/labelimg-installer3.5/Lib/site-packages/PyQt5/plugins/',
          '--paths=./libs', 'labelImg.py']

    run(opts)