# LabelTrack

**LabelTrack是为多目标跟踪```MOT```写的一个自动标注工具**

![](./assets/LabelTrack.png)

## 安装
```
git clone https://github.com/DD-DuDa/LabelTrack.git
cd LabelTrack/Tracking
pip install -r requirements.txt
pip install cython
pip install 'git+https://github.com/cocodataset/cocoapi.git#subdirectory=PythonAPI'
pip install cython_bbox
python setup.py develop
```

## 主要功能
* 导入mp4文件或视频帧文件夹
* 手动标注
* 修改标注框，包括大小，标签，ID等信息
* **采用SOTA目标跟踪模型对视频帧进行预跟踪**
* 导出和导入VisDrone格式数据集

## 快捷键
|  键位   | 功能  |
|  ----  | ----  |
| w  | 标注 |
| s, del  | 删除所选标注框 |

## 使用方法
1. 下载[ByteTrack](https://github.com/ifzhang/ByteTrack)模型权重，默认使用```bytetrack_m_mot17```，放入```./Tracking/weights```中
2. 修改```./Tracking/configs```中的yaml文件（exp_file, ckpt）
```
cd LabelTrack
python main.py
```
```./Tracking/videos``` 有demo视频

## 待更新
- [ ] * 当前模型是ByteTrack，只支持```person```
- [ ] 标注图片大小缩放，拖拽
- [ ] 工具栏等按钮完善
- [ ] 操作错误提醒完善
- [ ] 。。。

## 参考
1. https://github.com/tzutalin/labelImg
2. https://github.com/ifzhang/ByteTrack
