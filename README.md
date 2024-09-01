# DeeplxFile
基于Deeplx/playwright提供的简单易用，快速，免费，不限制文件大小，支持超长文本翻译的文件翻译工具

![简体中文](https://github.com/infrost/DeeplxFile)
![English](/README_translated.md)

------------------
点击[这里下载](https://github.com/infrost/DeeplxFile/releases)

在[这里查看详细介绍](https://blog.infrost.site/2024/08/29/DeeplxFile/)

## 功能介绍
### 这个软件有什么优点？
目前复杂文档，尤其是大文档的excel翻译，要么是要钱，要么是效果不好，要么是干脆直接不支持，该软件完美解决以上问题。
#### 翻译质量：
谷歌翻译,复杂公式引用无法正确显示，而DeeplxFile能正确显示引用公式。
且使用DeepL作为翻译源，大部分情况下中英互译效果优于谷歌。
![HighQuality](/images/deeplxfile_quality.png)

#### 翻译文件支持
以Excel为例，DeepL免费版不支持Excel翻译，谷歌不支持超过10MB的大文件翻译，DeeplxFile文档翻译无大小限制
![FileSupport](/images/deeplx_file_support.png)

### 翻译PDF并转换为可编辑的.docx文档
现已支持该功能，但由于PDF转换功能体积较为庞大，请前往独立下载：
[pdf2docxserver](https://github.com/infrost/pdf2docxserver/releases/)

**下载后双击运行这个转换服务软件，并保持打开状态。**

**使用`DeeplxFile`翻译的时候会自动调用转换服务。**
翻译效果如图：
![pdf_translation](/images/pdf_translate.png)

### Playwright模式（Windows）
![playwright.gif](/images/playwright.gif)
> 从`v0.5.0`版本开始支持，可在设置选项卡中可开启`Playwright`模式。
> 该模式是不依赖项目`deeplx`的，基于微软爬虫项目`Playwright`的实现。
> releases中的`_Lite`版本不包含该模式所需要的运行文件（webkit浏览器内核）。

该模式下，程序会模拟人类打开浏览器，复制粘贴翻译内容，并回传到程序里，优点是兼容性强，可以翻译大量文本（目前没有测试出文本长度限制）并规避`deeplx`项目内核带来的`请求频繁`的错误。
缺点是会稍微占用一些系统资源，且速度较慢，可以开启`隐藏操作过程`以节约系统资源。

### 直连模式
该模式同样不依赖`deeplx`，但是可用性较低，容易遇到Deepl服务器`请求频繁`的拒绝，轻量的文档翻译可能可用，是最节约资源也是最原生的翻译实现。

## 我该如何使用？
### Windows
提供了编译好的exe版本, 运行安装程序即可

**推荐** 下载`DeeplxFile_setup_windows_Full.exe` 解压安装，该版本带有完整webkit内核，playwright模式稳定性更好。
`Lite`版本不带有webkit内核，会调用系统自带的Edge浏览器，因此体积更小，但目前对edge的支持还在测试阶段，如果你不太需要playwright模式，可以用这个版本。
（你也可以设置里自己指定webkit内核）

### MacOS

**即将支持playwright模式**

右键解压出来的文件夹，选择在文件夹打开新终端，
终端中输入
```bash
./deelxfile
```

### 从源代码运行
你也可以下载源代码，
然后运行
```bash
python deeplxfile_gui.py
```
> 如果你需要使用Playwright模式的翻译功能，为了保持仓库的精简性，请手动下载`playwright-webkit`放在`./Lib/webkit`目录下然后运行，或者在`Lib/playwright_process.py`中指定Playwright的运行目录。
> 如果你不是Windows系统，你需要在`deeplxfile_gui.py`中指定其他版本的deeplx，或者去deeplx官方项目下方，下载一个deeplx运行。


## 版本说明

```bash
--------- V0.5.3--------------
提供登录选项,在设置中开启后，可以先登录deepl账号再进行翻译，有更大的单词字符翻译上限。
支持了Playwright下强制指定目标语言，适用于多语言混合文档。
支持PDF翻译（插件形式，见使用说明），
支持了txt,md文档翻译
为软件增加一个图标，感谢[openvc](https://github.com/infrost/DeeplxFile/issues/3)

--------- V0.5.2--------------
提供了调用系统edge浏览器的playwright方法，更加轻量（完整版的更加稳定）

---------- V0.5.0 ------------
该版本提供了完整GUI界面，和设置选项，更加简单易用
增加了Playwright模式（测试中）。

---------- V0.2.3 ------------
现已完全支持Word，Excel

powerpoint 支持翻译大部分内容

运行项目后会在目录下生成config.json
设置`save_original`为`true`即可保留原文
```
