# DeeplxFile
Easy-to-use, fast, free, unlimited file size, file translation tool based on Deeplx/playwright for very long texts.

[Simplified Chinese](https://github.com/infrost/DeeplxFile)
|
[English](/README_translated.md)

**The English Version is translated by DeeplxFile itself!**

------------------
Click [here to download](https://github.com/infrost/DeeplxFile/releases)

Check out the details at [here](https://blog.infrost.site/2024/08/29/DeeplxFile/)

## Features
### What are the advantages of this software?
At present, the excel translation of complex documents, especially large documents, either costs money, or has bad effect, or simply does not support directly, this software perfectly solves the above problems.
#### translation quality:
Google Translate, complex formula references can not be correctly displayed, while DeeplxFile can correctly display the reference formula.
And using DeepL as the translation source, in most cases, the effect of Chinese and English translation is better than Google.
![HighQuality](/images/deeplxfile_quality.png)

#### Translation File Support
Take Excel as an example, DeepL free version doesn't support Excel translation, Google doesn't support translation of large files over 10MB, DeeplxFile document translation has no size limitation!
![FileSupport](/images/deeplx_file_support.png)

### Translate PDF and convert to editable .docx documents
This feature is now supported, but due to the large size of the PDF conversion feature, please go to the standalone download:
![pdf2docxserver](https://github.com/infrost/pdf2docxserver/releases/)

**Double-click to run this conversion service software after download and keep it open. **

**The conversion service will be called automatically when you use `DeeplxFile` to translate. **
The translation effect is as shown in the picture:
![pdf_translation](/images/pdf_translate.png)

### Playwright mode (Windows)
![playwright.gif](/images/playwright.gif)
> Supported since `v0.5.0`, `Playwright` mode can be enabled in the Settings tab.
> This mode is independent of the project `deeplx` and is based on the implementation of the Microsoft crawler project `Playwright`.
> The `_Lite` version in releases does not include the runtime files (webkit browser kernel) needed for this mode.

In this mode, the program simulates a human opening a browser, copying and pasting the translated content and sending it back to the program. The advantages are compatibility, the ability to translate large amounts of text (no text length limit has been tested so far) and circumventing the `request-heavy` bug introduced by the `deeplx` project kernel.
The disadvantage is that it will take up some system resources and is slow, you can turn on `hidden operation process` to save system resources.

### Direct connection mode
This mode also doesn't rely on `deeplx`, but has lower availability, and is prone to encountering `requests` rejections from the Deepl server. It may be used for lightweight document translation, and is the most resource-efficient and native translation implementation.

### How do I use it?
### Windows
A compiled exe version is provided, just run the installer.

**Recommended** Download `DeeplxFile_setup_windows_Full.exe` and unpack it, this version comes with a full webkit kernel and is more stable in playwright mode.
The `Lite` version doesn't come with webkit kernel, it will call the system's own Edge browser, so it's smaller in size, but the support for edge is still in the testing stage, so if you don't need playwright mode too much, you can use this version.
(You can also specify your own webkit kernel in the settings)

### MacOS

**Playwright mode will be supported soon

Right-click on the extracted folder and select Open New Terminal in Folder.
In the terminal, type
```bash
. /deelxfile
``

### Run from source
You can also download the source code
and run it.
```bash
python deeplxfile_gui.py
```
> If you need to use the Playwright mode translation feature, to keep the repository lean, manually download `playwright-webkit` in the `. /Lib/webkit` directory and run it, or specify the Playwright runtime directory in `Lib/playwright_process.py`.
> If you're not on Windows, you'll need to specify another version of deeplx in `deeplxfile_gui.py`, or go to the bottom of the official deeplx project and download a deeplx to run.


## Versioning

```bash
--------- V0.5.3--------------
Provide login option, when you turn it on in settings, you can login to deepl account first and then translate, with larger word character translation limit.
Supports forced target language specification under Playwright, applicable to multi-language mixed documents.
Support PDF translation (in the form of plug-in, see the instructions).
Supported txt,md document translation.
add an icon for the software, thanks to [openvc](https://github.com/infrost/DeeplxFile/issues/3)

--------- V0.5.2--------------
Provide playwright method to call system edge browser, more lightweight (the full version is more stable)

---------- V0.5.0 ------------
This version provides the full GUI interface, and setting options, more easy to use
Added Playwright mode (in testing).

---------- V0.2.3 ------------
Word, Excel are now fully supported

powerpoint Support translate most of the content

After running the project, config.json will be generated in the directory.
Set `save_original` to `true` to preserve the original text.
``
