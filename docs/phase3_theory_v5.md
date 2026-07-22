# Phase 3 v5 理论说明

## 1. 研究对象

每条原始数据记录记为

\[
z_{i,r}=(I_i,Y^+_{i,r,1},Y^+_{i,r,2},Y^-_{i,r}).
\]

其中，\(I_i\) 是第 \(i\) 张独立图片，\(Y^+_{i,r,1}\) 和
\(Y^+_{i,r,2}\) 是两条语义正确描述，\(Y^-_{i,r}\) 是只改变关键语义的
困难错误描述，\(r\) 是同一图片下的数据记录编号。独立统计单位是图片组
\(I_i\)，不是数据行或文本词元。

## 2. 语义建模依据

概念模型为

\[
I=g(S,N),
\]

其中 \(S\) 是与任务语义有关的因素，\(N\) 是不改变目标语义的无关因素。
本阶段只部分实现该建模：困难错误描述测试模型对语义变化是否敏感，两条正确
描述测试模型对文字表达变化是否稳定；实验没有对图片亮度、裁剪等视觉无关因素
进行干预，因此不能声称测试了完整的视觉不变性。

## 3. 基础 Brier 风险

对图片 \(I\) 和描述 \(Y\)，词元平均 Brier 风险为

\[
b_h(I,Y)=\frac{1}{L}\sum_{t=1}^{L}\sum_{v=1}^{V}
\left(p_h(v\mid I,Y_{<t})-\mathbf 1[v=y_t]\right)^2,
\qquad 0\leq b_h(I,Y)\leq2.
\]

评分采用教师强制，只统计原始描述词元和唯一助手结束词元。

## 4. 一级理论风险一：稳健正确图文风险

定义

\[
\ell_{\mathrm{robust+}}(h,z)=
\max\{b_h(I,Y_1^+),b_h(I,Y_2^+)\},
\qquad 0\leq\ell_{\mathrm{robust+}}\leq2.
\]

两个诊断分量为

\[
\ell_{\mathrm{mean+}}=\frac{b_h(I,Y_1^+)+b_h(I,Y_2^+)}{2},
\qquad
\ell_{\mathrm{disp+}}=\frac{|b_h(I,Y_1^+)-b_h(I,Y_2^+)|}{2}.
\]

对任意实数 \(a,b\)，
\(\max(a,b)=(a+b+|a-b|)/2\)，所以

\[
\ell_{\mathrm{robust+}}=\ell_{\mathrm{mean+}}+
\ell_{\mathrm{disp+}}.
\]

`mean` 表示两个正确表达的平均预测质量，`dispersion` 表示两者风险的不均衡；
它们不是任意选择的两个一级风险，而是最坏正确表达风险的精确分解。

## 5. 一级理论风险二：视觉语义损失

有图与无像素条件下的稳健正负间隔分别为

\[
m_{\mathrm{img}}=b_h(I,Y^-)-\max\{b_h(I,Y_1^+),b_h(I,Y_2^+)\},
\]

\[
m_{\mathrm{none}}=b_h(\varnothing,Y^-)-
\max\{b_h(\varnothing,Y_1^+),b_h(\varnothing,Y_2^+)\}.
\]

视觉增量与越小越好的视觉语义损失为

\[
g_{\mathrm{visual}}=m_{\mathrm{img}}-m_{\mathrm{none}},
\qquad -4\leq g_{\mathrm{visual}}\leq4,
\]

\[
\ell_{\mathrm{visual}}=\frac{4-g_{\mathrm{visual}}}{8},
\qquad 0\leq\ell_{\mathrm{visual}}\leq1.
\]

\(g_{\mathrm{visual}}>0\) 表示真实图片提高了正负语义区分能力；等于零表示
没有可观察的额外区分；小于零表示真实图片反而削弱了区分。该量是图像条件与
描述正确性之间的交互对比，不是严格因果效应，也不能单独证明完整视觉理解。

## 6. 图片组风险

同一图片下先对记录求平均，再对图片组等权平均：

\[
\ell_i=\frac{1}{K_i}\sum_{r=1}^{K_i}\ell(h,z_{i,r}),
\qquad
\widehat R(h)=\frac{1}{m}\sum_{i=1}^{m}\ell_i.
\]

记录较多的图片不得获得更大权重。

## 7. 固定模型 Hoeffding 界

对每项一级风险计算名义上的固定模型 Hoeffding 上界：

\[
R(h)\leq\widehat R(h)+\Delta
\sqrt{\frac{\log(1/\delta')}{2m}}.
\]

稳健正确图文风险使用 \(\Delta=2\)，视觉语义损失使用 \(\Delta=1\)。

## 8. 压缩泛化界

第二阶段压缩适配器的完整 MMS2 文件作为模型描述：

\[
C_{\mathrm{file}}(h)=8\times\text{MMS2 文件字节数}.
\]

十个候选模型的编号另需
\(C_{\mathrm{id}}=\lceil\log_2 10\rceil=4\) 位，因此
\(C(h)=C_{\mathrm{file}}(h)+4\)。名义压缩界为

\[
R(h)\leq\widehat R(h)+\Delta\sqrt{
\frac{C(h)\ln2+2\ln C(h)+\ln(1/\delta')}{2m}}.
\]

输出同时保存未截断原始上界和截断到损失支持区间的展示上界；是否非空只根据
未截断原始上界判断。

## 9. 理论边界与事后分析披露

v5 的风险定义是在 v4 Formal 数值可能已经被查看后确定的。因此公式、失败概率
分配和名义界仍按冻结规则计算并完整报告，但这些数值属于事后分析；不得将其表述
为一次全新预注册实验所提供的同时 95% 覆盖保证。

本阶段研究 SugarCrepe++ 所代表目标分布上的 Brier 风险，条件于项目历史图像重叠
已被排除、独立图片组假设成立，以及十个模型在第三阶段正式数据评估前已经冻结。

本阶段不证明原始未平滑负对数似然的泛化界、所有自然图像上的泛化、完整视觉理解、
图像侧亮度或裁剪等无关因素不变性，也不证明严格因果关系。
