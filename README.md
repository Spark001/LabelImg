# labelImg

Label image list by make a class label.

## BUG!!!
1. 删除一个shape之后，copy和delete按钮没有切换不可点击
2. 当标出的框是一个点时，移动框时不可保存

## Usage

### Compile

Generate .py file from a .qrc file
```
pyrcc5 -o .py .qrc
```

### Steps

1. Click 'Change default saved annotation folder' in Menu/File
2. Click 'Open Dir'
3. Click 'Create RectBox'

The annotation will be saved to the folder you specify.

### Hotkeys

|    Keys  |                 Function                 |
|----------|------------------------------------------|
| Ctrl + r | Change the default annotation target dir |
| Ctrl + s | Save                                     |
| Ctrl + u | open dir                                 |
| Ctrl + s | Save                                     |
| Ctrl + d | Copy a bounding box                      |
| w        | Create a bounding box                    |
| d        | Next image                               |
| a        | Previous image                           |
| Space    | After choosing one label, quick add it   |


## Note： 
1. 文件路径不要包含中文字符