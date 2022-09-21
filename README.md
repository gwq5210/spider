<!-- PROJECT SHIELDS -->

[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]

<!-- PROJECT LOGO -->
<br />

<p align="center">
  <a href="https://github.com/gwq5210/spider/">
    <img src="images/logo.jpg" alt="Logo" width="160" height="100">
  </a>

  <h3 align="center">爬虫</h3>
  <p align="center">
    自己写的一些爬虫
    <br />
    <a href="https://github.com/gwq5210/spider"><strong>探索本项目的文档 »</strong></a>
    <br />
    <br />
    <a href="https://github.com/gwq5210/spider">查看Demo</a>
    ·
    <a href="https://github.com/gwq5210/spider/issues">报告Bug</a>
    ·
    <a href="https://github.com/gwq5210/spider/issues">提出新特性</a>
  </p>

</p>

<!-- TABLE OF CONTENTS -->
<details open="open">
  <summary><h2 style="display: inline-block">目录</h2></summary>
  <ol>
    <li>
      <a href="#关于项目">关于项目</a>
    </li>
    <li>
      <a href="#上手指南">上手指南</a>
      <ul>
        <li><a href="#依赖">依赖</a></li>
        <li><a href="#运行步骤">运行步骤</a></li>
      </ul>
    </li>
    <li><a href="#版权说明">版权说明</a></li>
    <li><a href="#联系方式">联系方式</a></li>
    <li><a href="#鸣谢">鸣谢</a></li>
  </ol>
</details>

# 关于项目

爬虫的仓库集合, 会将抓取到的数据保存在[Elasticsearch][Elasticsearch]中

* [spider_911mjw](spider_911mjw)——爬取美剧信息
* [spider_macwk](spider_macwk)——爬取mac软件信息
* [spider_wexyx](spider_wexyx)——爬取nes游戏
* [spider2048](spider2048)——爬取并下载图片

# 上手指南

## 主要依赖

* [Python3](https://www.python.org/)
* [Scrapy](https://scrapy.org/)
* [Elasticsearch][Elasticsearch]

## **运行步骤**

1. 安装依赖

```sh
git clone https://github.com/gwq5210/spider.git
pip3 install -r requirements.txt
```

2. 运行爬虫

```sh
cd spider/spider_911mjw
scrapy crawl videos
cd spider/spider_macwk
scrapy crawl soft
cd spider/spider_wexyx
scrapy crawl nes
cd spider/spider2048
scrapy crawl images

scrapyd-client schedule -p PROJECT_NAME --arg setting=KEY1=VALUE1 --arg setting=KEY2=VALUE2 SPIDER
curl http://localhost:6800/schedule.json -d project=PROJECT_NAME -d spider=SPIDER -d setting=KEY1=VALUE1 -d setting=KEY2=VALUE2
```

# 版权说明

该项目签署了MIT 授权许可，详情请参阅 [LICENSE.txt](https://github.com/gwq5210/spider/blob/master/LICENSE.txt)

# 联系方式

gwq5210@qq.com

<!-- links -->
[your-project-path]:gwq5210/spider
[contributors-shield]: https://img.shields.io/github/contributors/gwq5210/spider.svg?style=flat-square
[contributors-url]: https://github.com/gwq5210/spider/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/gwq5210/spider.svg?style=flat-square
[forks-url]: https://github.com/gwq5210/spider/network/members
[stars-shield]: https://img.shields.io/github/stars/gwq5210/spider.svg?style=flat-square
[stars-url]: https://github.com/gwq5210/spider/stargazers
[issues-shield]: https://img.shields.io/github/issues/gwq5210/spider.svg?style=flat-square
[issues-url]: https://img.shields.io/github/issues/gwq5210/spider.svg
[license-shield]: https://img.shields.io/github/license/gwq5210/spider.svg?style=flat-square
[license-url]: https://github.com/gwq5210/spider/blob/master/LICENSE.txt
[Elasticsearch]: https://www.elastic.co/cn/
