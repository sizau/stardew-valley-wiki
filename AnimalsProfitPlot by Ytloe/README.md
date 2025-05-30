主程序是 src/AnimalsProfitPlot.py
运行前需要在命令行运行 pip install -r requirements.txt 安装 numpy 和 matplotlib
可自行修改里面的"颜色"来调整折线和重要好感度值的颜色
可在 img 文件夹里面放图片作为背景图（默认读取 bg.jpg，可自行修改后缀名）
目前使用背景图时图表会自适应宽高导致导出的图片可能有点难看，可以在 plot_profit_comparison 方法中强制宽高
