# 生信入门-单细胞分析 A-5：绘图描述
#生信 #细胞 #单细胞分析 #预处理 #文库 #测序 #数据库 #数据分析 #作图


| 图表类型               | 用途                                                                 | 工具/包          |
|------------------------|----------------------------------------------------------------------|------------------|
| **热图（Heatmap）**    | 展示基因表达差异或临床特征关联（复合热图）                          | `pheatmap`       |
| **火山图（Volcano）**  | 可视化差异基因（横轴=LFC，纵轴=-log10 (p-value)）                    | `ggplot2`        |
| **生存曲线**           | Kaplan-Meier 曲线（时间 vs 生存概率）                                | `survminer`      |
| **维恩图（Veen）**     | 展示基因列表交集                                                    | `VennDiagram`    |
| **圈图/弦图**          | 复杂关系网络可视化                                                  | `circlize`       |

## 一、热图绘制 （heatmap）（31） 

> 热图可以理解为一种添加了“颜色轴”的三维表格，颜色轴体现在色块上的颜色差异，不同情况下 XY 轴和颜色表示都可以不同  


生信分析中热图也有很多种，功能也随之不同，包括但不限于观察显示健康组织和癌症组织的差异，以及不同聚类间基因表达的差异，比较典型的是下面两种  


1. 行代表不同的细胞聚类，列代表不同的基因，这种热图可以看出这种聚类算法下不同聚类之间差异出现的区域![](https://api2.mubu.com/v3/document_image/26905802_1be653cb-66e6-49ff-d4a8-30a1db2f2365.png) ![](https://api2.mubu.com/v3/document_image/26905802_91651ae0-11df-4a2d-dc50-7187bb3adf9c.png)

2. 这张则是复合热图，用于展示患者的临床特征和基因表达情况。每个代表一个病例 ![](https://api2.mubu.com/v3/document_image/26905802_794678ec-33e9-4c02-f818-2525eb412d0b.png)


## 二、火山图绘制 （volcano）（67）  

横坐标 LFC (log2foldchang)，纵坐标取 p 值（-log10p-value，越大越显著），阈值也可以自己控制  

横线即为显著性水平线，越向上越有统计学意义，两根竖线是差异倍数线，其中左侧竖线代表下调，右侧竖线代表上调；因此一般左上角区域是表达显著下调且差异大，右上角区域是表达显著上调且差异大![](https://api2.mubu.com/v3/document_image/26905802_03fb684e-573b-42a4-c873-036ff7039008.png)

## 三、生存分析曲线 （survival）（Kaplan-Meier 曲线）（11,39）  

> 用来显示患者在不同时间点的生存概率的图表（估计时间到事件（如死亡、复发等）数据的生存概率）曲线的纵轴表示生存概率，横轴表示时间。曲线的每个阶梯下降对应一个事件的发生。  


导入生存时间和事件数据，按照探索的基因的基因表达水平将患者分组，根据这一分组进行曲线绘制  
- 生存曲线中的阶梯状曲线表达不同组的事件发生概率，每一个下降阶梯对应一个事件发生的时间点  
- 风险表（Risk Table）则描述每个时间点上的剩余研究人数  
- p 值（p-value），用于判断不同组的生存曲线是不是显著不同，一般用 Log-Rank Test  

## 四、维恩图 （20）  

## 五、弦图  

## 六、圈图  

## 七、双轴图