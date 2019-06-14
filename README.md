# labelImg-ChooseTheBest

Label image list by choosing the best one.

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
| d        | Next image                               |
| a        | Previous image                           |


## Note： 
1. 文件路径不要包含中文字符
