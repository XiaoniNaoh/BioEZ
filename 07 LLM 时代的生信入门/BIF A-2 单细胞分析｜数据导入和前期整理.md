# 生信入门-单细胞分析 A-2：数据导入和前期整理
#生信 #细胞 #单细胞分析 #预处理 #文库 #测序 #数据库 #预处理 

## 一、数据来源

- 本地来源（CSV/XLSX/TXT）  
- 数据库（各种 SQL 来源）  
- API 调取  
- 标准数据平台（GEO/TCGA）

> [!TIP]
> - **GEO**：
> 	- Microarray Data（微阵列数据，杂交技术）
> 	- RNA-Seq Data（RNA 测序数据，高通量测序）（34）  
> - **TCGA**：
> 	- Genomic Data（WGS 全部和 WES 外显）
> 	- RNA-Seq Data（RNA 测序数据）
> 	- Clinical Data（临床数据）  

---

## 二、数据预处理

### 1. Microarray Data

1. **原始数据（. cel）和注释文件（. txt）导入 R 中**  

2. **背景校正（RMA/MAS5）、归一化、探针汇总**  

3. **用注释包替换探针 ID 为基因符号**（或手动操作）
	- 探针 ID 就是一个结合目标序列的一个序列  
	- 注释包就是一种 R 包，里面包含有一个映射关系，也就是能叫出探针 ID 的基因符号名字，这个 R 包可以把探针 ID 替换为基因符号，有的也可以自己汇总  
	- 另外这个步骤不用注释包也可以手动完成，但是操作有点复杂

4. **提取表达矩阵（行 = 基因，列 = 样本）和样本信息**  

5. **整合实验设计数据**（样本编号+处理条件）  

6. **导出数据**  

> [!NOTE] 
> - **背景校正**：去除非特异性的杂质信号，一般用 RMA 或者 MAS5（待掌握）
> - **归一化**：去除不同芯片中的系统性的差异  
> - **汇总**：就是把多种探针（这些探针可能测的是同一个基因）合并汇总
> - **表达矩阵**：是个表格，行是基因然后列表示样本，中间描述的就是这个基因在这个样本的表达水平，后面用来差异分析聚类分析什么的  
> - **样本信息**：描述每一个样本的来源处理方式

### 2. RNA-Seq Data

1. **导入文件**
	- 一般是 fastq 文件，有些已经被 TPM, FPKM 归一过了

2. **质量控制（FastQC）和修剪（Trimmomatic/Cutadapt）**
	- 用 FastQC 来检查测序数据的质量怎么样  
	- 修剪和清理就是将低质量的序列和接头序列清除掉，一般用 Trimmomatic 或 Cutadapt  
	- 可以显著减少测序错误和偏差。

3. **对齐到参考基因组**
	- 将测序的 RNA 片段（reads）和已知的的基因组序列匹配上去，确定每个读段在基因组中的位置，这样我们可以知道是哪些基因在表达  
	- 一般用 HISAT2 和 STAR 完成然后会生成一个 SAM/BAM（SAM 的二进制版本）格式的文件，里面描述了比对的结果信息  

4. **计算每个基因在样本的表达水平（计数转录本）**  
	- 计数指的是比对到每个基因或者转录本的读段（reads）数量，量化出基因的具体表达水平，一般就是用 BAM 文件来处理  
	- 一般用 featureCounts 和 HTSeq 来处理，这两个都是用来对基因组特征进行计数的  
	- 这样处理后得到的结果就类似于前面出现过的数据矩阵（Data Matrix），行表示基因或转录本，然后列就是样本，中间描述的就是转录水平，出来的数据是 csv 表格  

 5. **整合表达数据和样本信息**  
	 - 把上述的表达数据和样本信息整合在一起  
	 - 如果是用作差异表达分析，可以构建为一个 DESeqDataSet 对象，这个对象含有计数矩阵、样本信息和实验设计内容  

 6. **归一化和差异表达分析**
	 - 归一化就是调整数据，让不同样本之间的基因表达水平可以直接进行比较（毕竟所使用的技术不同，测序深度也可能不同）用中位数比率法或者 TMM 法  
	 - 差异表达分析就是用统计方法找出表达有有显著差异的基因，可以用 DESeq2 包的负二项分布或者 limma 包的线性模型实现，也可以用 edgeR 的广义线性模型

 7. **导出**

### 3. Clinical Data

> 这部分和 RNA-Seq Data 一起处理

1. **导入文件，一般 Clinical 格式是 xml 或 csv**  

2. **和前面一样，把 RNA-Seq Data 处理好**

3. **表达数据和临床数据通过样本 ID 进行关联**  
	- 表达数据就是前面那个*数据矩阵*，就是描述每个基因在不同样本中的表达水平的一个表格  
	- 临床数据就是*描述样本的临床信息*的一个表格，包括患者什么时候病的，什么时候离世的，患者年龄患者性别患者种族等等  
	- 样本 ID 就是每个样本的一个唯一标识符，相当于样本的身份证号  
	- 关联就是把这两个 Data 根据样本 ID 匹配在一起，然后整合为一个大的综合数据集  
	- 这个步骤使用 merge 就可以完成 

4. **导出**

### 4. 数据清洗

处理缺失值和异常值
