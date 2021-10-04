# mymask

<!-- Add buttons here -->

<!-- Describe your project in brief -->

上传图片，选择口罩，点击“处理图片”后，可查看佩戴口罩之后的人物照片，根据合适程度选择保存或者重新处理。保存的图片和原图片在同一路径下，带有后缀with-mask。



# Demo-Preview
![user](https://github.com/2812046929/pictures/blob/main/user.jpg)

![window](https://github.com/2812046929/pictures/blob/main/window.png)

![user_with_mask](https://github.com/2812046929/pictures/blob/main/user-with-mask1.jpg)
# Table of contents

- [mymask](#mymask)
- [Demo-Preview](#demo-preview)
- [Table of contents](#table-of-contents)
- [Installation](#installation)
- [Usage](#usage)
- [Development](#development)
- [Adding new features or fixing bugs](#adding-new-features-or-fixing-bugs)

# Installation
[(Back to top)](#table-of-contents)

首先用以下命令将文件下载到本地：

```git init```

```git clone https://github.com/navendu-pottekkat/nsfw-filter.git```


# Usage
[(Back to top)](#table-of-contents)

运行\mymask\dist\__main__\__main__.exe文件即可执行

# Development
[(Back to top)](#table-of-contents)

主要代码在\mymask\__main__.py文件中。用到的python库有PyQt5(搭建GUI使用)、face_recognition(提取面部信息)、PIL(处理图片)。

maskWindow类：GUI。

FaceMasker类：提取面部信息和处理图片。若提高口罩对不同脸型的适配性，可以修改FaceMasker类。

myQGraphicsScene类：响应鼠标点击事件。


# Adding new features or fixing bugs
[(Back to top)](#table-of-contents)

由于这个程序的应用较为广泛，可以用于微信小程序等场景。
