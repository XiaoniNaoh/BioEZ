# 生信入门-单细胞分析 A-4：数据的深入分析
#生信 #细胞 #单细胞分析 #预处理 #文库 #测序 #数据库 #数据分析 #作图

## 一、探索性数据分析（EDA）

### 1. 相关性分析（COR）（63-65）  

就是计算基因表达和临床特征的相关系数，有点类似于上述的散点图中描述的关系的进一步探索，包括皮尔逊相关系数，还可以包括斯皮尔曼秩相关系数这些  

识别潜在的生物标志物和疾病相关的基因  

### 2. 主成分分析（PCA）（数据降维）（38,66）

可以用于**降噪、特征提取和数据可视化**。通过分析主成分的贡献率，可以确定保留多少主成分。保留主成分后，可以直观地观察到样本之间的差异性和相似性  

具体操作上就是找到一个新的坐标系，在数据只保留更少维度的时候，使得信息损失最小  

>【【中字】主成分分析法（PCA）| 分步步骤解析 看完你就懂了！-哔哩哔哩】 [https://b23.tv/rv5BEbj](https://b23.tv/rv5BEbj)

### 3. 聚类分析

> 一种无监督学习方法，根据数据集的对象的相似程度把它们分成聚类  

- 方法包括 Graph-based 和 K-means 两种，一般以散点图形式表示，根据聚类分析可以探索群体内核群体间的差异 
- 这部分使用 loupebrowser 可以方便快捷地实现探索分析  

---

## 二、差异表达分析（DEG）（8,14,34）  

> 用于找出不同条件下基因表达水平的差异，找出存在显著差异表达的基因

*（以 DESeq2 包为例）*

对 DESeqDataSet 对象使用 **DESeq() 函数**，它会进行因子大小估计、离散度估计、模型拟合以及假设检验操作，然后最后生成一个带有每个基因的差异倍数变化 log fold change（LFC）值和 p 值  

- LFC 就是基因在不同条件下表达量的**相对差异**，越大差异越大  
- 最后得到的差异表达基因列表（DEGs）也是一个表格，会描述有每个基因在不同组之间表现出来的显著差异，每一个基因都会带有 GeneID，LFC，标准误（SE），p-value（就是 p 值），Adjusted p-value（多种校正后的 p 值）  
- 有时候也会带有一些质量报告什么的

---

## 三、功能注释富集分析通路分析

### 1. GO 分析（基因本体分析）（10）

> 用于了解基因在细胞中的作用

需要一个**待分析的基因列表**（通常是实验数据中取得的差异表达基因或者与特定条件相关的基因集合）  

将这一基因列表中的每个基因映射到相应的 **GO 目录**中（一般是用 DAVID、Ensembl 或 AmiGO）这意味着我们知道了每个基因参与哪些生物学过程、执行什么功能以及位于细胞的哪个部位。 

统计一下每个 GO 目录在基因列表中的**富集情况**（计算每个 GO 条目在我们的基因列表中出现的频率是否高于随机预期，这可以帮助我们找到在我们的基因列表中过度代表（富集）的 GO 条目。），方法可以用 *Fisher 精确检验*和 *GSEA 法*  

GO 富集分析设计大量的假设检验，需要**多重比较**校正来减少假阳性情况（把不富集的也当富集了） 

- 一般用图像或者图表来表示哪些 GO 条目是富集的  

### 2. KEGG 分析（10）  

> 用于了解基因在生物体内的带些和信号转导的路径

需要一个**待分析的基因列表**（通常也是实验数据中取得的差异表达基因或者与特定条件相关的基因集合）  

将这一基因列表中的每个基因映射到相应的 **KEGG 通路**上（一般是用 DAVID、KEGG Mapper 或 KOBAS）这意味着我们知道了每个基因参与哪些生物学过程、执行什么功能以及位于细胞的哪个部位。 

计算每个 KEGG 通路在基因列表中的**富集情况**。常用的统计方法包括超几何检验、Fisher精确检验和 GSEA。  

KEGG 分析设计大量的假设检验，需要**多重比较**校正来减少假阳性情况（把不富集的也当富集了）  

- 一般用图像或者图表来表示哪些 KEGG 通路是富集的  

### 3. 基因集富集分析（GSEA、ssGSEA）（12-13,25）

> 用于确定预定义的基因集是否在两种生物状态之间显示出统计学上显著的、一致的差异

需要一个包含所有**基因表达水平数据**的矩阵（一般是 RNA-Seq 或者微阵列来的）  

从功能注释数据库（如 MSigDB）中选取**基因集合**（一组基因的列表，这些基因被认为具有某种共同的功能或参与相同的生物学过程。） 

将基因表达数据根据在两组样本之间的差异表达程度由大到小对所有基因进行**排序**  

计算出每个基因集在排序列表中的**富集分数（ES）**，这个分数反映了该基因集是否倾向于出现在排序列表的前端或后端。 
- 如果这个基因集里的基因大多出现在列表的前端（即表达差异大的基因），那么这个基因集就会有一个较高的 ES 值。  
- 如果这个基因集里的基因大多出现在列表的后端（即表达差异小的基因），那么这个基因集就会有一个较低的 ES 值。  
- 如果这个基因集里的基因均匀分布在列表中，那么 ES 值会接近于 0。  

通过**随机置换样本标签**的方法来评估每个基因集的富集是否显著。这会产生一个 p 值，用来衡量观察到的富集是否可能仅仅是随机发生的。p 值越大差异越小  

因为有多次的假设检验，所以要对 p 值进行校正，以减少假阳性结果的数量。常用的方法是 **FDR 校正**，这样我们可以得到调整后的 p 值。  

通过图表或图像来展示哪些基因集合在两组样本中是不是有比较显著的差异表达（显著富集）

### 4. 生存分析（11）  

- 单因素 Cox 回归（uniCox）（9,54）  
- 多因素 Cox 回归（multiCox）（17,54）  
- 风险预测模型（Nomogram）  

### 5. 聚类与网络分析  

#### 🌿 Graph-based  
 
Graph-based 聚类方法利用**图结构**来表示数据点及其相似性。每个数据点被表示为图中的一个**节点**，节点之间的边表示数据点之间的相似性或距离。通过对图进行划分，将相似的节点聚类到同一个簇中。  

- 基因共表达网络（WGCNA）（37）  
    - 识别基因模块（就是一组共同调节的基因）  
- 蛋白质蛋白质相互作用网络（PPI）（15）  
	- 识别蛋白质之间的相互作用模式，可以用于理解蛋白质如何协同工作来执行细胞功能  

#### 🌿 K-means

用于将数据点**分成 K 个簇**，使得每个簇内的数据点的数据（例如某种基因的表达水平）尽可能相似，而不同簇之间的数据点尽可能不同。需要预设需要的聚类数目  

以将**表达模式相似**的基因（共表达基因）分组，用来进行数据降维，可以预测基因簇  

- **共识聚类**（18）：多次运行 K-means，找到最稳定的一种聚类状态，简而言之就是用于预测出最稳定的聚类数目的一种方法

### 6. 免疫分析（24）  

#### 🌿 细胞组成分析

 **CIBERSORT**（23）
> 用于推断复杂样本包括肿瘤中不同细胞类型的相对丰度  

- 需要 RNA-Seq Data 和 CIBERSORT 的特征基因集（例如 LM22.txt 这种描述了不同的基因表达模式的文件） 

 设定一个合适的迭代次数（一般1000以上）直接使用 CIBERSORT 包处理二者，就可以得到每个样本中不同细胞亚群的比例
 
*可以可视化，条形图、饼图、热图都可以*  

**ESTIMATE**（31）
> 量化基质和基质相关基因表达，评估肿瘤样本中基质细胞和免疫细胞含量的计算方法

- 需要 RNA-Seq Data  

ESTIMATE 算法根据特征基因集和样本基因表达数据来计算样本中基质细胞和免疫细胞的评分  

*可以可视化，一般用条形图或者热图*  

#### 🌿 TIDE （28）

 > 评估肿瘤免疫治疗效果的方法  
 
 基于肿瘤微环境中的基因表达数据来预测患者对免疫检查点抑制剂（如 PD-1/PD-L1 抑制剂）的响应  
 
- 需要一个 RNA-Seq Data，直接用 TIDE 算法计算每个样本的 T 功能障碍评分和 T 细胞排斥评分  
	- **T 细胞功能障碍**：在某些肿瘤中，尽管细胞毒性 T 细胞（CTL）浸润程度高，但这些 T 细胞往往处于功能失调状态，无法有效杀伤肿瘤细胞。  
	- **T 细胞排斥**：在另一些肿瘤中，免疫抑制因子可以祛除浸润在肿瘤组织中的 T 细胞，阻止它们发挥作用。  
*可以可视化*  

#### 🌿 其他方法 （42）

- IPS 等

---

## 四、预测与验证分析

### 1. 套索回归分析（LASSO）（16,56）

> 一种可以预测一个变量和其他变量之间的关系（比如房价和服务地段大小等）的线性回归分析方法

- 需要 RNA-Seq Data（包含基因表达矩阵）和 Clinical Data（包含目标变量值）  

这种方法会将一些不太重要的变量去除（惩罚）可以帮助我们找到多个变量中最重要的变量  

在生信分析中，LASSO 常用于处理高维基因表达数据，以识别与特定生物学过程或疾病状态相关的基因，后序可以用来构建预测模型 

将数据分为**训练集**和**验证集**，使用训练集运行 LASSO 训练出多个正则化参数 λ 不同的 **LASSO 模型**（LASSO 自己会选择出它觉得拿来预测比较好用的一些基因然后和目标变量值进行预测分析），再拿这个验证集去评价每一个训练出来的 LASSO 模型得出均方误差（MSE）或平均绝对误差（MAE）  

- 训练集和验证集就是前者做模型，后者看看哪个模型好用
- 正则化参数 λ 就相当于**惩罚强度**，较小的 λ 值允许更多的特征进入模型，而较大的λ值会导致更多的特征系数被缩减至零。
- 如果模型预测的疾病风险与实际风险之间的差异较大，MSE 会显著增加，提示模型可能需要调整，对离群值敏感。  
- 如果模型预测的疾病风险与实际风险之间的差异较大，MAE 也会增加，但不会像 MSE 那样对离群值敏感。

### 2. 基于机器学习的分类模型（RF、SVM）

- 随机森林（RF）（57）  
- 支持向量机（SVM）（58）

### 3. ROC 评估曲线（19）

> 用来评估分类模型的阈值选择好不好的一个参数，一般通过绘制真阳性率（TPR）和假阳性率（FPR）之间的关系来评估模型的性能  

> [!NOTE]
> - **真阳性率 TPR**：分类中被划为阳性的占所有阳性的比例，ROC 曲线的纵轴  
> - **假阳性率 FPR**：分类中被划为阳性的占所有阴性的比例，ROC 曲线的横轴  
> - **曲线下面积 AUC**：ROC 曲线下面的面积，AUC 越大越好，一般主要看这个  

取得**预测概率**（训练模型对每个样本属于哪一个类别的概率）和**对应样本的真实标签**，将这两个值输入给 pROC 包处理即可得到 ROC 评估曲线
