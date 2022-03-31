# How to install Chrome Driver

## 1. For mac
- Install chrome
- Check your chrome version [here](chrome://settings/help).
- Download corresponding chrome driver version [here](https://chromedriver.storage.googleapis.com/index.html?path=100.0.4896.60/).
- Unzip the downloaded file, copy `chromedriver` to this project folder (under root directory).
- Run `python Leetcode.py` to see if things work well.

## 2. For Ubuntu (tested on 18.04 x64)
- Install chrome by
```bash
$ sudo apt-get update
$ sudo apt-get install google-chrome-stable
```
- Check chrome version by
```bash
$ google-chrome --version
```
- Download corresponding chrome driver version [here](https://chromedriver.storage.googleapis.com/index.html?path=100.0.4896.60/).
```bash
$ wget <the download link here>
```
- Unzip the downloaded file, copy `chromedriver` to this project folder (under root directory).
```bash
$ sudo apt-get install unzip
$ unzip <downloaded file name>
$ cp chromedriver <root path of this project>
```
- Go inside this project, run `python Leetcode.py` to see if things work well.