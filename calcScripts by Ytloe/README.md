强烈建议使用 python 3.12.0 以上版本运行，可以避免很多库版本兼容问题
运行前需要运行以下命令安装依赖（打开这个 md 所在文件夹，上面路径输入 cmd）：  
原生 python：pip install -i https://mirrors.aliyun.com/pypi/simple/ -r requirements.txt  
如果用的 uv：uv sync  
这里提供的镜像源默认是阿里云的，可以自己修改

- 清华源：https://pypi.tuna.tsinghua.edu.cn/simple/
- 阿里源：https://mirrors.aliyun.com/pypi/simple/
- 中科大源：https://pypi.mirrors.ustc.edu.cn/simple/
- 豆瓣：http://pypi.douban.com/simple/
- 腾讯：http://mirrors.cloud.tencent.com/pypi/simple/
- 华为：https://repo.huaweicloud.com/repository/pypi/simple
- 北大：https://mirrors.pku.edu.cn/pypi/web/simple/
- 哈工大：https://mirrors.hit.edu.cn/pypi/web/simple/
- 大连东软：https://mirrors.neusoft.edu.cn/pypi/web/simple/
- 北美：https://pypi.cloudflaremirrors.com/simple/
- 欧洲：https://pypi.fcio.net/simple/
- 日韩：https://ftp.jaist.ac.jp/pub/pypi/simple/
- 东南亚：https://pypi.mirrors.ustc.edu.sg/simple/
- python 默认：https://pypi.org/simple/

运行程序都在 src 里面

- animalsProfitPlot.py 是用于绘制动物日收益曲线的，基本上所有操作都在 main 方法里了，可以往 img 里面丢 bg.jpg 替换折线背景图  
  运行流程：

  1. setup_animal_config；得到动物所有基础信息的 dict
  2. calc_daily_profits；根据基础信息使用 numpy 批量计算 0~1000 好感度的常规日收益和加工日收益（附带大产物概率和品质概率）
  3. plot_profit_comparison；传入数据绘制图像，可以自行修改线段颜色和背景图

- calcFishesProb.py 是用于计算钓鱼准确概率的其中一个方法，建议搭配 json 文件夹里的“钓鱼概率解释文档.txt”查看，暂时还不完善
  运行流程：

  1. calc_fishing_prob; 传入[{"ID": fish_id, "Precedence": precedence, "survival_prob": prob, "hook_prob": prob}]这个类型的列表就能获得概率

- readRecipe.py 是用于计算全制造配方的材料需求的
  依赖文件（解包成 json 后放入 json 文件夹里即可）：

  1. Data\BigCraftables.json
  2. Strings\BigCraftables.zh-CN.json
  3. Data\CraftingRecipes.json
  4. Data\Objects.json
  5. Strings\Objects.zh-CN.json

- utils.py 是一些通用的函数
- test.py 测试通用函数用的，可以看看 utils 里面的类和方法都怎么调用

另外学习了一下 commit message 应该怎么写  
用 git 推送代码到 github 需要填写 commit 信息  
commit message 规范：  
类型(作用域)：主题  
正文

类型：

- feat：新增功能
- fix：修正错误/bug
- refactor：代码重构
- docs：改文档
- style：改风格
- test：测试相关的修改
- chore：杂项
- perf：优化性能
- ci：CI/CD 相关改动
- build：改构建系统或依赖
- revert：回滚提交

作用域：具体改了什么地方  
主题：概括这次推送做了什么  
正文：推送修改的细节详情
