<p align="center"><img src="logo.svg" alt="logo" width="100"></p>
<h1 align="center">DWords</h1>
<p align="center">把单词变成屏幕上的弹幕来帮助你记住单词</p>

[![PyPI version](https://img.shields.io/pypi/v/DWords.svg)](https://pypi.org/project/DWords/)
[![Build Status](https://api.travis-ci.org/luyuhuang/DWords.svg?branch=dev)](https://travis-ci.org/luyuhuang/DWords)
[![License](https://img.shields.io/github/license/luyuhuang/DWords)](https://github.com/luyuhuang/DWords/blob/dev/LICENSE)

> 注意: 这个仓库还在开发中, 暂时没有稳定版本.

![Screenshot](screenshot.png)

## 介绍

DWords 是一个跨平台工具, 它可以把单词变成弹幕显示在屏幕上来帮助你记住单词. DWords 的主要目的是帮助非英语母语的人学习英语, 但不仅限于英语, 你还可以用它来记住任何你想要记住的东西.

特性:

- 开源跨平台
- 在使用电脑的同时记单词
- 通过电子邮件在多台设备之间同步
- 通过电子邮件用手机添加单词

## 安装

DWords 使用 Python3 编写, 我们推荐通过 pip 安装. 先确保你的电脑上已安装好了 Python3.

打开终端运行以下命令, DWords 就安装好了:

```sh
pip3 install DWords
```

你也可以通过源码安装:

```sh
git clone https://github.com/luyuhuang/DWords.git
cd DWords
python3 setup.py install
```

<!-- 如果你不会 Python, 我们也提供了 Windows 系统的二进制版本. 点击[这里]()下载. 注意, 二进制版本可能不被杀毒软件信任. -->

## 使用方法

在终端键入 `DWords` 以启动 DWords. 如果你是下载的二进制版本, 双击 `DWords.exe` 启动.

## 许可证

DWords 在 [GPLv3 许可](https://github.com/luyuhuang/DWords/blob/dev/LICENSE)下发布, 因为 PyQt5 是在 GPLv3 下发布的 (所以我们别无选择). 你可以免费使用, 自由修改, 但是当你修改它时你必须使用同样的许可证开源.
