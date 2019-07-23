# labelImg-Choose Yes or No

Label image list by choosing yes or no.

## Usage

### Compile

Generate .py file from a .qrc file
```
pyrcc5 -o .py .qrc
```

### Steps

1. Click 'Open Dir'
2. Choose the best one by click the radiobutton.

The annotation will be saved to the folder you specify or image folder by default.

### Hotkeys

|    Keys  |                 Function                 |
|----------|------------------------------------------|
| Ctrl + r | Change the default annotation target dir |
| Ctrl + u | open dir                                 |
| s        | Save                                     |
| e        | Next image                               |
| r        | Previous image                           |
| d        | Next image && choose the first label     |
| f        | Next image && choose the second label    |


## Note： 
1. 文件路径不要包含中文字符
2. 自己定义的predifined.txt只包含一行,关键字用逗号分隔,不要包含中文字符
