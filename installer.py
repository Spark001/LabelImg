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
    opts=['-F', '-w', '--paths=C:/Users/root/labelImg/Lib/site-packages/python_qt5-0.3.0-py2.7.egg/PyQt5/',
          '--paths=C:/Users/root/labelImg/Lib/site-packages/python_qt5-0.3.0-py2.7.egg/PyQt5/plugins',
          '--paths=./libs', 'labelImg.py']

    run(opts)