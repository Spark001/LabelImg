#########################################################################
# File Name: install.sh
# Author: Zhen Shen
# mail: spark80231@gmail.com
# Created Time: 2019年06月14日 星期五 17时46分20秒
#########################################################################
#!/bin/bash
pyinstaller -n ChooseTheBest \
	-F labelbest.py ./libs/lib.py ./libs/canvas.py ./libs/toolBar.py \
	./libs/zoomWidget.py ./libs/labelFileBest.py ./libs/singleChoiceWidget.py
