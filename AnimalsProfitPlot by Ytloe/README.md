运行前需要运行以下命令安装依赖（打开这个 md 所在文件夹，上面路径输入 cmd）：
原生 python：pip install -i https://mirrors.aliyun.com/pypi/simple/ -r requirements.txt
如果用的 uv：uv sync

这里提供的镜像源默认是阿里云的，可以自己修改
清华源：https://pypi.tuna.tsinghua.edu.cn/simple/
阿里源：https://mirrors.aliyun.com/pypi/simple/
中科大源：https://pypi.mirrors.ustc.edu.cn/simple/
豆瓣：http://pypi.douban.com/simple/
腾讯：http://mirrors.cloud.tencent.com/pypi/simple/
华为：https://repo.huaweicloud.com/repository/pypi/simple
北大：https://mirrors.pku.edu.cn/pypi/web/simple/
哈工大：https://mirrors.hit.edu.cn/pypi/web/simple/
大连东软：https://mirrors.neusoft.edu.cn/pypi/web/simple/
北美：https://pypi.cloudflaremirrors.com/simple/
欧洲：https://pypi.fcio.net/simple/
日韩：https://ftp.jaist.ac.jp/pub/pypi/simple/
东南亚：https://pypi.mirrors.ustc.edu.sg/simple/
python 默认：https://pypi.org/simple/

主程序是 src/AnimalsProfitPlot.py，修改 animal_id 就可以计算不同动物的收益曲线
运行流程：setup_animal_config()设置动物 -> calc_daily_profits()计算数据 -> plot_profit_comparison()绘制图像

setup_animal_config()->输出计算一个动物应该具备的所有基础数值：
支持直接传参，没传的参数会要求输入，这个输入的方法特地设置过防呆防傻和更好的提示词

calc_daily_profits()->该动物 0~1000 好感度共 1001 个(日收益数值+加工日收益数值+大产物概率+品质概率)：
直接生成 1001 个好感度并行计算，基本上公式都定死了，有错只能手动改计算过程，有影响的都会要求输入

plot_profit_comparison()：
可自行修改里面的"颜色"来调整折线和重要好感度值的颜色
可创建 img 文件夹在里面放图片作为背景图（默认读取 bg.jpg，可自行修改）
目前使用背景图时图表会自适应宽高导致导出的图片可能有点难看，可以修改 fig.figimage 的参数
