---
id: "bif-a-01"
title: "单细胞分析｜样品准备与文库构建"
course: "bioinformatics"
chapter: "单细胞分析"
order: "a-01"
status: "scientific-review"
audience:
  - "undergraduate"
difficulty: 3
importance: 3
estimated_minutes: 5
prerequisites: []
next:
  - "bif-a-02"
tags:
  - "生信"
  - "细胞"
  - "单细胞分析"
  - "预处理"
  - "文库"
  - "测序"
authors:
  - "脆弱的百里橘"
reviewers: []
last_scientific_review: null
summary: "介绍《LLM 时代的生信入门》中的“单细胞分析｜样品准备与文库构建”主题。"
references: []
content_type: "lesson"
---

<!-- BEGIN AUTO-GENERATED NAVIGATION -->
> [!NOTE] 课程导航
> [课程目录](<COURSE_INDEX.md>) · [下一篇：单细胞分析｜数据导入和前期整理 →](<BIF A-2 单细胞分析｜数据导入和前期整理.md>)
<!-- END AUTO-GENERATED NAVIGATION -->

# 生信入门-单细胞分析 A-1：样品准备与文库构建
#生信 #细胞 #单细胞分析 #预处理 #文库 #测序

## 一、样品准备

### 粗略过程

1. **细胞分离**  
   - 将细胞团中的细胞分离出来  
   - **技术方法**：  
     - 荧光激活细胞分选（FACS）（基于流式细胞术）  
     - 微流控芯片技术  

2. **细胞捕获**  
	- **技术方法**：  
	- 微滴技术（10x 平台）  
	- 微孔板法  

### 目的
将每一个细胞分离出来以便后续操作

---

## 二、文库构建和测序（以 Illumina 测序平台为例）

### 粗略过程

1. **提取 RNA**  
   - 从每一个细胞中提取出其中的转录组  
2. **逆转录**  
   - 将 RNA 逆转录为 cDNA  
3. **末端修复**  
   - 把打断的 cDNA 两端修复为平末端  
4. **添加接头**  
   - 加上测序接头  
5. **桥式 PCR 扩增**  
6. **测序**  
   - 边合成边测序（荧光测序） 

### 目的
取得每一个细胞的基因表达情况
