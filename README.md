<div align="center">

# 欧亚学院畅课文件系统

</div>

> 整个目录改了很多内容，还有7z.exe这个二进制文件，git来git去.git文件夹就变大了，懒得重搞。废弃了这个，创建了一个新的  
传送门

## 说明
> 仅作学习使用

挖了个坑，主要是练习用的。  
现在已经实现文件属性获取存入自制的树形数据结构里了，完事之后直链获取也蛮简单的，加上了。  
文件下载会下载到py脚本对应文件夹下的downloads文件夹中，没有加名字去重，如果有重名文件记得先备份，不然就覆盖了

2023-02-27  阴  
昨天加了上传功能但是没来得及写，今天是加了删除功能顺便为了cd功能修改了大部分内容  
把内容加载修改了，以前是进到哪个文件夹才会去请求哪一个文件夹。改成了刚开始就一次性全部递归地给获取完，这会在一开始很费时间，之后会找机会优化一下  
还有登录，加了conf.json用于保存学号和密码，保存的时候会用b64简单编码一下防止不小心看到，input()输入的时候密码也不会显示出来

2023-02-27  阴  21:45  
随便加了个线程后台加载，就当优化了。按理来说我本来的想法是只请求后3层内的所有文件夹，因为怕请求多了会被注意，有被封的风险，不过觉得应该没太大可能。

有机会和时间的话会尽量做出gui


## 效果:
![Snipaste_2023-02-25_17-30-36](https://user-images.githubusercontent.com/96933655/221349911-7ead90de-8206-456f-86ec-a83ff35ccf3b.jpg)

![image](https://user-images.githubusercontent.com/96933655/221360515-a3e2b2d9-0884-4764-954a-648a76189830.png)



## 为什么做这个事情呢... 
如果想把它当网盘用的话，网页端加载不知道为啥总是有些慢，尤其是文件夹加载，而且还得加载很多别的玩意很浪费资源。  
写个这个练练手，之后可能也会想实现本地直接交作业啥的，这个文件系统功能是必要的😰
