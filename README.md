# SIX
![image](https://img.shields.io/badge/python-3.7-blue)
![image](https://img.shields.io/badge/opencv-4.4.0.46-brightgreen)
![image](https://img.shields.io/badge/numpy-1.21-red)
![image](https://img.shields.io/badge/windows-10-informational)
## 这是什么
SIX 是一个跨平台的、可扩展性高、可维护性强的基于机器感知的有限状态机框架。本项目原则为“精简至上”，尽量使用python原生库以保证本项目的可扩展性。
## 安装
```shell
pip install six_python
```
## 使用
本项目提供插件开发接口，详细操作请见[操作文档](doc/manual-zh-cn.md)。
## 开发任务
因为该项目仍处在起步阶段，所以必要时候会对框架做出调整，作者会尽量以兼容的形式做出这些必要的调整。
### core（当前主要开发任务）
- [x] 完成 Observer 和 Actor 的订阅者框架搭建，将图片帧的输入与对图片的操作解耦；
- [x] 完成 Analyzer 基类的构建，使开发者专注对图片帧的分析操作，增加分析代码的复用度；
- [x] 优化订阅者框架的接口，方便插件开发者定义 Action；
- [x] 删除 Analyzer，简化 core 代码，同时增加插件开发者的开发自由度；
- [x] 构建全局配置和局部配置系统
- [x] 构建插件系统
- [x] 优化插件导入接口
- [x] 实现定时 Action
- [x] 实现静态配置设置与导入接口
- [x] 增加日志打印
- [x] 编写操作文档
- [ ] 适配 Linux 平台
- [ ] 适配嵌入式设备
### plugin（陆续开发）
- [ ] 图像识别模型接口插件
- [ ] 强化学习模型接口插件