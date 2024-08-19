# DeeplxFile
基于Deeplx提供的免费，不限制文件大小的文件翻译工具

------------------
点击[这里下载](https://github.com/infrost/DeeplxFile/releases)

## 使用说明

### Windows
提供了编译好的exe版本, 直接双击运行即可

### 从源代码运行
你也可以下载源代码，
然后运行
```bash
python deeplxfile.py
```

### MacOS
右键解压出来的文件夹，选择在文件夹打开新终端，
终端中输入
```bash
./deelxfile
```

## 版本说明
现已完全支持Word，Excel

powerpoint 支持翻译大部分内容

运行项目后会在目录下生成config.json
设置`save_original`为`true`即可保留原文

## 直连模式
该模式不依赖deeplx的内核，使用的是自己实现的请求方法
