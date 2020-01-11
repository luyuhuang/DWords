<p align="center"><img src="logo.svg" alt="logo" width="100"></p>
<h1 align="center">DWords</h1>
<p align="center">把单词变成屏幕上的弹幕来帮助你记住单词</p>

[![PyPI version](https://img.shields.io/pypi/v/DWords.svg)](https://pypi.org/project/DWords/)
[![Build Status](https://api.travis-ci.org/luyuhuang/DWords.svg?branch=dev)](https://travis-ci.org/luyuhuang/DWords)
[![codecov](https://codecov.io/gh/luyuhuang/DWords/branch/dev/graph/badge.svg)](https://codecov.io/gh/luyuhuang/DWords)
[![License](https://img.shields.io/github/license/luyuhuang/DWords)](https://github.com/luyuhuang/DWords/blob/dev/LICENSE)

![Screenshot](screenshot.png)

## 介绍

DWords 是一个跨平台工具, 它可以把单词变成弹幕显示在屏幕上来帮助你记住单词. DWords 的主要目的是帮助非英语母语的人学习英语, 但不仅限于英语, 你还可以用它来记住任何你想要记住的东西.

特性:

- 开源跨平台
- 通过随处可见的弹幕在使用电脑的同时记住单词
- 通过电子邮件在多台设备之间同步
- 通过电子邮件用手机添加单词
- 内置词典

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
git checkout master
python3 setup.py install
```

如果你不会 Python, 我们也提供了 Windows 系统的二进制版本. 点击[这里](https://github.com/luyuhuang/DWords/releases)下载. 注意, 二进制版本可能不被杀毒软件信任.

## 使用方法

在终端键入 `DWords` 以启动 DWords. 如果你是下载的二进制版本, 双击 `DWords.exe` 启动.

### 添加单词

点击 "+" 按钮并在下方的输入框中输入单词. 格式如下: 第一行为单词, 第二行为简要释义, 接下来的是详细释义. 简要释义能够直接显示在弹幕上, 但详细释义只能显示在详细面板中. 详细释义是可选的. 比如:

```
word
单词
n. 单词;词;字; eg. Do not write more than 200 words.
```

然后点击 "Commit" 按钮添加它, 或者按下 Ctrl + Enter.

### 使用词典

DWords 内置了词典, 点击 "Setting" 按钮在 "Common" 页签中设置它. 目前仅支持英汉词典, 收录了超过 3 万词. 一旦设置了词典, 在输入单词时按下 Enter 键, 释义就会自动出现.

### 同步

DWords 支持在多个客户端之间同步单词. 为了启用这一功能, 你需要先设置账户. 点击 "Setting" 按钮在 "Account" 页签中设置邮箱地址, 邮箱密码, SMTP 服务器和 POP3 服务器. DWords 会通过发送邮件来同步数据, 所以推荐使用一个不常用的邮箱.

### 通过邮件添加单词

设置好了账户后, 你就可以通过发送邮件来添加单词. 随意使用一个邮件客户端编辑邮件, 主题为 "DWords add", 内容的格式与添加单词类似, 不过可以添加多个单词, 单词之间用三连杠 "---" 或者三逗号 ",,," 分割; 三波浪线 "~~~" 或者三点号 "..." 表示结束. 例如:

```
world
世界
---
word
单词
,,,
hello
你好
...
在 ... 之后的内容都会被忽略
```

然后把这封邮件发送到你设置好的邮箱即可.

如果你已经设置了词典, 就不必指定释义, DWords 会自动查阅词典.

## 贡献

如果你遇到了任何问题, 或者有任何建议, 请提交 [issue](https://github.com/luyuhuang/DWords/issues). 我们也欢迎各种 pull request.

## 许可证

DWords 在 [GPLv3 许可](https://github.com/luyuhuang/DWords/blob/dev/LICENSE)下发布, 因为 PyQt5 是在 GPLv3 下发布的 (所以我们别无选择). 你可以免费使用, 自由修改, 但是当你修改它时你必须使用同样的许可证开源.
