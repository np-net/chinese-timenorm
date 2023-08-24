# chinese-timenorm

中文时间信息规范化表示数据集样例

本存储库包含中文时间信息规范化表示标注数据的样例以及schema，使用[Anafora](https://github.com/weitechen/anafora/) XML格式存储。数据集的详细情况参见论文*基于表达式的中文时间信息规范化表示语料库构建*。

标注样例从全部标注数据中随机抽取了154篇（12.8%）文章，其中包含6.8万字（13.0%），1003个时间短语（12.0%）。目前文章正在评审中，待录用后会发布完整数据集。

数据标注规范改进自Bethard和Parker的TimeNorm规范（*Bethard&Parker. A Semantically Compositional Annotation Scheme for Time Normalization. ELRA2016*），其标注的英文数据为[SCATE](https://github.com/bethard/anafora-annotations)。

## 如何使用样例数据

本样例数据仅包含标注，并不包含标注对应到原文。使用者获取到人民日报标注数据（见[发布链接](https://klcl.pku.edu.cn/gxzy/231686.htm)）后，需首先将原文回填到标注文件目录中：

```bash
python fill_rawtext.py -x RMRB-sample -r path/to/PeoplesDaily/corpus/file.txt -d directory/to/put/complete/corpus
```

之后即可使用完整数据集。数据集文件结构的说明参见Anafora的文档。
