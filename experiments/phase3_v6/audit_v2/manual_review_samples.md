# SugarCrepe++ contrast hull 第二轮自动审计抽查材料

这些样本只供人工复核，不代表已完成人工语义验证。Contrast hull 不是人工语义真值。

固定随机种子：`3407`；每类最多 `30` 条；不同类别允许重复。

## 规范化后变为单块局部编辑

候选 `498` 条，本节抽取 `30` 条。

### 1. `replace_attribute:235`

- 负例类型/范围：`replace_attribute` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A PERSON HOLDING A BLACKBERRY CELL PHONE IN THEIR HAND "
- 原始正描述 2："A person is holding a blackberry cell phone in their hand."
- 原始负描述："A PERSON HOLDING AN ANDROID CELL PHONE IN THEIR HAND."
- 规范化正描述 1："a person holding a blackberry cell phone in their hand"
- 规范化正描述 2："a person is holding a blackberry cell phone in their hand"
- 规范化负描述："a person holding an android cell phone in their hand"
- 正描述 1 选择元组：`[4, 4, 1, 0.2, 0.18518518518518517]`
- 正描述 2 选择元组：`[5, 7, 2, 0.2727272727272727, 0.22807017543859648]`
- 最终比较正描述：`positive_1` / "A PERSON HOLDING A BLACKBERRY CELL PHONE IN THEIR HAND "
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 3, "negative_start": 0, "negative_end": 3, "positive_lexemes": ["a", "person", "holding"], "negative_lexemes": ["a", "person", "holding"]}, {"tag": "replace", "positive_start": 3, "positive_end": 5, "negative_start": 3, "negative_end": 5, "positive_lexemes": ["a", "blackberry"], "negative_lexemes": ["an", "android"]}, {"tag": "equal", "positive_start": 5, "positive_end": 10, "negative_start": 5, "negative_end": 10, "positive_lexemes": ["cell", "phone", "in", "their", "hand"], "negative_lexemes": ["cell", "phone", "in", "their", "hand"]}]`
- 共同前缀：`["a", "person", "holding"]`
- 正确 contrast hull：`["a", "blackberry"]`
- 错误 contrast hull：`["an", "android"]`
- 共同后缀：`["cell", "phone", "in", "their", "hand"]`
- Hull token 覆盖率（正/负/最大）：`[0.29411764705882354, 0.2, 0.29411764705882354]`
- 共同前缀模型 token：`[100, 2198, 429, 2569, 350]`
- 正确 hull 模型 token：IDs `[299, 2597, 1637, 2009, 1557]`；text " a blackberry"
- 错误 hull 模型 token：IDs `[346, 376, 4786]`；text " an android"
- 第一轮/第二轮分类：`complex_edit` / `one_block_local`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 2. `replace_attribute:383`

- 负例类型/范围：`replace_attribute` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："several jet planes flying in unison in a v formation "
- 原始正描述 2："Several jet planes are flying in a V formation in unison."
- 原始负描述："Several propeller planes flying in unison in a V formation."
- 规范化正描述 1："several jet planes flying in unison in a v formation"
- 规范化正描述 2："several jet planes are flying in a v formation in unison"
- 规范化负描述："several propeller planes flying in unison in a v formation"
- 正描述 1 选择元组：`[2, 2, 1, 0.1, 0.13793103448275862]`
- 正描述 2 选择元组：`[9, 19, 4, 0.5454545454545454, 0.5517241379310345]`
- 最终比较正描述：`positive_1` / "several jet planes flying in unison in a v formation "
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 1, "negative_start": 0, "negative_end": 1, "positive_lexemes": ["several"], "negative_lexemes": ["several"]}, {"tag": "replace", "positive_start": 1, "positive_end": 2, "negative_start": 1, "negative_end": 2, "positive_lexemes": ["jet"], "negative_lexemes": ["propeller"]}, {"tag": "equal", "positive_start": 2, "positive_end": 10, "negative_start": 2, "negative_end": 10, "positive_lexemes": ["planes", "flying", "in", "unison", "in", "a", "v", "formation"], "negative_lexemes": ["planes", "flying", "in", "unison", "in", "a", "v", "formation"]}]`
- 共同前缀：`["several"]`
- 正确 contrast hull：`["jet"]`
- 错误 contrast hull：`["propeller"]`
- 共同后缀：`["planes", "flying", "in", "unison", "in", "a", "v", "formation"]`
- Hull token 覆盖率（正/负/最大）：`[0.10526315789473684, 0.19047619047619047, 0.19047619047619047]`
- 共同前缀模型 token：`[573, 652, 352]`
- 正确 hull 模型 token：IDs `[1315, 439]`；text " jet"
- 错误 hull 模型 token：IDs `[540, 115, 1272, 311]`；text " propeller"
- 第一轮/第二轮分类：`complex_edit` / `one_block_local`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 3. `replace_attribute:586`

- 负例类型/范围：`replace_attribute` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："there are many vases on the ground in the street"
- 原始正描述 2："Several vases are positioned on the ground in the street."
- 原始负描述："There are few vases on the ground in the street."
- 规范化正描述 1："there are many vases on the ground in the street"
- 规范化正描述 2："several vases are positioned on the ground in the street"
- 规范化负描述："there are few vases on the ground in the street"
- 正描述 1 选择元组：`[2, 2, 1, 0.1, 0.08333333333333333]`
- 正描述 2 选择元组：`[8, 8, 1, 0.4, 0.3392857142857143]`
- 最终比较正描述：`positive_1` / "there are many vases on the ground in the street"
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 2, "negative_start": 0, "negative_end": 2, "positive_lexemes": ["there", "are"], "negative_lexemes": ["there", "are"]}, {"tag": "replace", "positive_start": 2, "positive_end": 3, "negative_start": 2, "negative_end": 3, "positive_lexemes": ["many"], "negative_lexemes": ["few"]}, {"tag": "equal", "positive_start": 3, "positive_end": 10, "negative_start": 3, "negative_end": 10, "positive_lexemes": ["vases", "on", "the", "ground", "in", "the", "street"], "negative_lexemes": ["vases", "on", "the", "ground", "in", "the", "street"]}]`
- 共同前缀：`["there", "are"]`
- 正确 contrast hull：`["many"]`
- 错误 contrast hull：`["few"]`
- 共同后缀：`["vases", "on", "the", "ground", "in", "the", "street"]`
- Hull token 覆盖率（正/负/最大）：`[0.07142857142857142, 0.07142857142857142, 0.07142857142857142]`
- 共同前缀模型 token：`[119, 2503, 732]`
- 正确 hull 模型 token：IDs `[2547]`；text " many"
- 错误 hull 模型 token：IDs `[4654]`；text " few"
- 第一轮/第二轮分类：`complex_edit` / `one_block_local`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 4. `replace_attribute:649`

- 负例类型/范围：`replace_attribute` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A kid asleep on a large bed under a mosquito net"
- 原始正描述 2："A mosquito net is positioned over a kid sleeping on a large bed."
- 原始负描述："A kid awake on a large bed under a mosquito net."
- 规范化正描述 1："a kid asleep on a large bed under a mosquito net"
- 规范化正描述 2："a mosquito net is positioned over a kid sleeping on a large bed"
- 规范化负描述："a kid awake on a large bed under a mosquito net"
- 正描述 1 选择元组：`[2, 2, 1, 0.09090909090909091, 0.08333333333333333]`
- 正描述 2 选择元组：`[18, 22, 4, 0.7692307692307693, 0.746031746031746]`
- 最终比较正描述：`positive_1` / "A kid asleep on a large bed under a mosquito net"
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 2, "negative_start": 0, "negative_end": 2, "positive_lexemes": ["a", "kid"], "negative_lexemes": ["a", "kid"]}, {"tag": "replace", "positive_start": 2, "positive_end": 3, "negative_start": 2, "negative_end": 3, "positive_lexemes": ["asleep"], "negative_lexemes": ["awake"]}, {"tag": "equal", "positive_start": 3, "positive_end": 11, "negative_start": 3, "negative_end": 11, "positive_lexemes": ["on", "a", "large", "bed", "under", "a", "mosquito", "net"], "negative_lexemes": ["on", "a", "large", "bed", "under", "a", "mosquito", "net"]}]`
- 共同前缀：`["a", "kid"]`
- 正确 contrast hull：`["asleep"]`
- 错误 contrast hull：`["awake"]`
- 共同后缀：`["on", "a", "large", "bed", "under", "a", "mosquito", "net"]`
- Hull token 覆盖率（正/负/最大）：`[0.15, 0.15, 0.15]`
- 共同前缀模型 token：`[100, 914, 460]`
- 正确 hull 模型 token：IDs `[523, 361, 1522]`；text " asleep"
- 错误 hull 模型 token：IDs `[299, 122, 2434]`；text " awake"
- 第一轮/第二轮分类：`complex_edit` / `one_block_local`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 5. `replace_object:1101`

- 负例类型/范围：`replace_object` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："a herd of elephants standing in a water hole with a crowd of people watching "
- 原始正描述 2："A group of individual is observing a group of elephants that are standing in a water hole."
- 原始负描述："A herd of elephants standing in a water hole with a crowd of birds watching."
- 规范化正描述 1："a herd of elephants standing in a water hole with a crowd of people watching"
- 规范化正描述 2："a group of individual is observing a group of elephants that are standing in a water hole"
- 规范化负描述："a herd of elephants standing in a water hole with a crowd of birds watching"
- 正描述 1 选择元组：`[2, 2, 1, 0.06666666666666667, 0.07894736842105263]`
- 正描述 2 选择元组：`[26, 30, 4, 0.8235294117647058, 0.6966292134831461]`
- 最终比较正描述：`positive_1` / "a herd of elephants standing in a water hole with a crowd of people watching "
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 13, "negative_start": 0, "negative_end": 13, "positive_lexemes": ["a", "herd", "of", "elephants", "standing", "in", "a", "water", "hole", "with", "a", "crowd", "of"], "negative_lexemes": ["a", "herd", "of", "elephants", "standing", "in", "a", "water", "hole", "with", "a", "crowd", "of"]}, {"tag": "replace", "positive_start": 13, "positive_end": 14, "negative_start": 13, "negative_end": 14, "positive_lexemes": ["people"], "negative_lexemes": ["birds"]}, {"tag": "equal", "positive_start": 14, "positive_end": 15, "negative_start": 14, "negative_end": 15, "positive_lexemes": ["watching"], "negative_lexemes": ["watching"]}]`
- 共同前缀：`["a", "herd", "of", "elephants", "standing", "in", "a", "water", "hole", "with", "a", "crowd", "of"]`
- 正确 contrast hull：`["people"]`
- 错误 contrast hull：`["birds"]`
- 共同后缀：`["watching"]`
- Hull token 覆盖率（正/负/最大）：`[0.041666666666666664, 0.08, 0.08]`
- 共同前缀模型 token：`[100, 2833, 103, 354, 1905, 1601, 5483, 2823, 350, 353, 299, 3949, 6271, 361, 599, 299, 317, 2079, 103, 354]`
- 正确 hull 模型 token：IDs `[2975]`；text " people"
- 错误 hull 模型 token：IDs `[5231, 1881]`；text " birds"
- 第一轮/第二轮分类：`complex_edit` / `one_block_local`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 6. `replace_object:1113`

- 负例类型/范围：`replace_object` / `{"canonical": true, "pilot": true, "formal": false, "certifying_formal": false}`
- 原始正描述 1："A man holding a tennis racquet in the yard "
- 原始正描述 2："A man is in the yard holding a tennis racquet."
- 原始负描述："A woman holding a tennis racquet in the yard."
- 规范化正描述 1："a man holding a tennis racquet in the yard"
- 规范化正描述 2："a man is in the yard holding a tennis racquet"
- 规范化负描述："a woman holding a tennis racquet in the yard"
- 正描述 1 选择元组：`[2, 2, 1, 0.1111111111111111, 0.045454545454545456]`
- 正描述 2 选择元组：`[9, 17, 3, 0.8, 0.6444444444444445]`
- 最终比较正描述：`positive_1` / "A man holding a tennis racquet in the yard "
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 1, "negative_start": 0, "negative_end": 1, "positive_lexemes": ["a"], "negative_lexemes": ["a"]}, {"tag": "replace", "positive_start": 1, "positive_end": 2, "negative_start": 1, "negative_end": 2, "positive_lexemes": ["man"], "negative_lexemes": ["woman"]}, {"tag": "equal", "positive_start": 2, "positive_end": 9, "negative_start": 2, "negative_end": 9, "positive_lexemes": ["holding", "a", "tennis", "racquet", "in", "the", "yard"], "negative_lexemes": ["holding", "a", "tennis", "racquet", "in", "the", "yard"]}]`
- 共同前缀：`["a"]`
- 正确 contrast hull：`["man"]`
- 错误 contrast hull：`["woman"]`
- 共同后缀：`["holding", "a", "tennis", "racquet", "in", "the", "yard"]`
- Hull token 覆盖率（正/负/最大）：`[0.058823529411764705, 0.15789473684210525, 0.15789473684210525]`
- 共同前缀模型 token：`[100]`
- 正确 hull 模型 token：IDs `[1672]`；text " man"
- 错误 hull 模型 token：IDs `[339, 444, 325]`；text " woman"
- 第一轮/第二轮分类：`complex_edit` / `one_block_local`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 7. `replace_object:1126`

- 负例类型/范围：`replace_object` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A table with a plate, wine-filled glass, and bread, among other items"
- 原始正描述 2："The table contains a plate, bread and glass filled with wine, among other items."
- 原始负描述："A table with a bowl, wine-filled glass, and bread, among other items."
- 规范化正描述 1："a table with a plate , wine-filled glass , and bread , among other items"
- 规范化正描述 2："the table contains a plate , bread and glass filled with wine , among other items"
- 规范化负描述："a table with a bowl , wine-filled glass , and bread , among other items"
- 正描述 1 选择元组：`[2, 2, 1, 0.06666666666666667, 0.06944444444444445]`
- 正描述 2 选择元组：`[15, 23, 6, 0.5, 0.4691358024691358]`
- 最终比较正描述：`positive_1` / "A table with a plate, wine-filled glass, and bread, among other items"
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 4, "negative_start": 0, "negative_end": 4, "positive_lexemes": ["a", "table", "with", "a"], "negative_lexemes": ["a", "table", "with", "a"]}, {"tag": "replace", "positive_start": 4, "positive_end": 5, "negative_start": 4, "negative_end": 5, "positive_lexemes": ["plate"], "negative_lexemes": ["bowl"]}, {"tag": "equal", "positive_start": 5, "positive_end": 15, "negative_start": 5, "negative_end": 15, "positive_lexemes": [",", "wine-filled", "glass", ",", "and", "bread", ",", "among", "other", "items"], "negative_lexemes": [",", "wine-filled", "glass", ",", "and", "bread", ",", "among", "other", "items"]}]`
- 共同前缀：`["a", "table", "with", "a"]`
- 正确 contrast hull：`["plate"]`
- 错误 contrast hull：`["bowl"]`
- 共同后缀：`[",", "wine-filled", "glass", ",", "and", "bread", ",", "among", "other", "items"]`
- Hull token 覆盖率（正/负/最大）：`[0.07142857142857142, 0.10344827586206896, 0.10344827586206896]`
- 共同前缀模型 token：`[100, 2630, 599, 299]`
- 正确 hull 模型 token：IDs `[1219, 557]`；text " plate"
- 错误 hull 模型 token：IDs `[363, 451, 111]`；text " bowl"
- 第一轮/第二轮分类：`complex_edit` / `one_block_local`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 8. `replace_object:1157`

- 负例类型/范围：`replace_object` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："a garbage bag in a white lighted bathroom"
- 原始正描述 2："A white lighted bathroom contains a garbage bag."
- 原始负描述："A flower vase in a white lighted bathroom."
- 规范化正描述 1："a garbage bag in a white lighted bathroom"
- 规范化正描述 2："a white lighted bathroom contains a garbage bag"
- 规范化负描述："a flower vase in a white lighted bathroom"
- 正描述 1 选择元组：`[4, 4, 1, 0.25, 0.24390243902439024]`
- 正描述 2 选择元组：`[14, 14, 1, 0.875, 0.8085106382978723]`
- 最终比较正描述：`positive_1` / "a garbage bag in a white lighted bathroom"
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 1, "negative_start": 0, "negative_end": 1, "positive_lexemes": ["a"], "negative_lexemes": ["a"]}, {"tag": "replace", "positive_start": 1, "positive_end": 3, "negative_start": 1, "negative_end": 3, "positive_lexemes": ["garbage", "bag"], "negative_lexemes": ["flower", "vase"]}, {"tag": "equal", "positive_start": 3, "positive_end": 8, "negative_start": 3, "negative_end": 8, "positive_lexemes": ["in", "a", "white", "lighted", "bathroom"], "negative_lexemes": ["in", "a", "white", "lighted", "bathroom"]}]`
- 共同前缀：`["a"]`
- 正确 contrast hull：`["garbage", "bag"]`
- 错误 contrast hull：`["flower", "vase"]`
- 共同后缀：`["in", "a", "white", "lighted", "bathroom"]`
- Hull token 覆盖率（正/负/最大）：`[0.35294117647058826, 0.26666666666666666, 0.35294117647058826]`
- 共同前缀模型 token：`[100]`
- 正确 hull 模型 token：IDs `[492, 370, 101, 834, 363, 1163]`；text " garbage bag"
- 错误 hull 模型 token：IDs `[5652, 311, 603, 812]`；text " flower vase"
- 第一轮/第二轮分类：`complex_edit` / `one_block_local`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 9. `replace_object:1273`

- 负例类型/范围：`replace_object` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："a young girl making a plate of food."
- 原始正描述 2："A young girl is preparing a food plate."
- 原始负描述："A young boy making a plate of food."
- 规范化正描述 1："a young girl making a plate of food"
- 规范化正描述 2："a young girl is preparing a food plate"
- 规范化负描述："a young boy making a plate of food"
- 正描述 1 选择元组：`[2, 2, 1, 0.125, 0.11428571428571428]`
- 正描述 2 选择元组：`[12, 12, 1, 0.75, 0.631578947368421]`
- 最终比较正描述：`positive_1` / "a young girl making a plate of food."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 2, "negative_start": 0, "negative_end": 2, "positive_lexemes": ["a", "young"], "negative_lexemes": ["a", "young"]}, {"tag": "replace", "positive_start": 2, "positive_end": 3, "negative_start": 2, "negative_end": 3, "positive_lexemes": ["girl"], "negative_lexemes": ["boy"]}, {"tag": "equal", "positive_start": 3, "positive_end": 8, "negative_start": 3, "negative_end": 8, "positive_lexemes": ["making", "a", "plate", "of", "food"], "negative_lexemes": ["making", "a", "plate", "of", "food"]}]`
- 共同前缀：`["a", "young"]`
- 正确 contrast hull：`["girl"]`
- 错误 contrast hull：`["boy"]`
- 共同后缀：`["making", "a", "plate", "of", "food"]`
- Hull token 覆盖率（正/负/最大）：`[0.23076923076923078, 0.16666666666666666, 0.23076923076923078]`
- 共同前缀模型 token：`[100, 401, 1685]`
- 正确 hull 模型 token：IDs `[492, 639, 111]`；text " girl"
- 错误 hull 模型 token：IDs `[1847, 124]`；text " boy"
- 第一轮/第二轮分类：`complex_edit` / `one_block_local`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 10. `replace_object:1310`

- 负例类型/范围：`replace_object` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："a bright kitchen with tulips on the table and plants by the window "
- 原始正描述 2："The kitchen is bright, with tulips on the table and plants by the window."
- 原始负描述："A bright bedroom with tulips on the table and plants by the window."
- 规范化正描述 1："a bright kitchen with tulips on the table and plants by the window"
- 规范化正描述 2："the kitchen is bright , with tulips on the table and plants by the window"
- 规范化负描述："a bright bedroom with tulips on the table and plants by the window"
- 正描述 1 选择元组：`[2, 2, 1, 0.07692307692307693, 0.10606060606060606]`
- 正描述 2 选择元组：`[6, 8, 3, 0.26666666666666666, 0.2602739726027397]`
- 最终比较正描述：`positive_1` / "a bright kitchen with tulips on the table and plants by the window "
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 2, "negative_start": 0, "negative_end": 2, "positive_lexemes": ["a", "bright"], "negative_lexemes": ["a", "bright"]}, {"tag": "replace", "positive_start": 2, "positive_end": 3, "negative_start": 2, "negative_end": 3, "positive_lexemes": ["kitchen"], "negative_lexemes": ["bedroom"]}, {"tag": "equal", "positive_start": 3, "positive_end": 13, "negative_start": 3, "negative_end": 13, "positive_lexemes": ["with", "tulips", "on", "the", "table", "and", "plants", "by", "the", "window"], "negative_lexemes": ["with", "tulips", "on", "the", "table", "and", "plants", "by", "the", "window"]}]`
- 共同前缀：`["a", "bright"]`
- 正确 contrast hull：`["kitchen"]`
- 错误 contrast hull：`["bedroom"]`
- 共同后缀：`["with", "tulips", "on", "the", "table", "and", "plants", "by", "the", "window"]`
- Hull token 覆盖率（正/负/最大）：`[0.18181818181818182, 0.18181818181818182, 0.18181818181818182]`
- 共同前缀模型 token：`[100, 3461, 774]`
- 正确 hull 模型 token：IDs `[914, 338, 102, 2051]`；text " kitchen"
- 错误 hull 模型 token：IDs `[363, 382, 393, 444]`；text " bedroom"
- 第一轮/第二轮分类：`complex_edit` / `one_block_local`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 11. `replace_object:1348`

- 负例类型/范围：`replace_object` / `{"canonical": true, "pilot": true, "formal": false, "certifying_formal": false}`
- 原始正描述 1："There is a cat wearing an elephant hat"
- 原始正描述 2："The elephant hat is worn by the cat."
- 原始负描述："There is a dog wearing an elephant hat."
- 规范化正描述 1："there is a cat wearing an elephant hat"
- 规范化正描述 2："the elephant hat is worn by the cat"
- 规范化负描述："there is a dog wearing an elephant hat"
- 正描述 1 选择元组：`[2, 2, 1, 0.125, 0.07894736842105263]`
- 正描述 2 选择元组：`[16, 16, 1, 1.0, 0.6842105263157895]`
- 最终比较正描述：`positive_1` / "There is a cat wearing an elephant hat"
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 3, "negative_start": 0, "negative_end": 3, "positive_lexemes": ["there", "is", "a"], "negative_lexemes": ["there", "is", "a"]}, {"tag": "replace", "positive_start": 3, "positive_end": 4, "negative_start": 3, "negative_end": 4, "positive_lexemes": ["cat"], "negative_lexemes": ["dog"]}, {"tag": "equal", "positive_start": 4, "positive_end": 8, "negative_start": 4, "negative_end": 8, "positive_lexemes": ["wearing", "an", "elephant", "hat"], "negative_lexemes": ["wearing", "an", "elephant", "hat"]}]`
- 共同前缀：`["there", "is", "a"]`
- 正确 contrast hull：`["cat"]`
- 错误 contrast hull：`["dog"]`
- 共同后缀：`["wearing", "an", "elephant", "hat"]`
- Hull token 覆盖率（正/负/最大）：`[0.07142857142857142, 0.13333333333333333, 0.13333333333333333]`
- 共同前缀模型 token：`[119, 2503, 395, 299]`
- 正确 hull 模型 token：IDs `[3706]`；text " cat"
- 错误 hull 模型 token：IDs `[1041, 106]`；text " dog"
- 第一轮/第二轮分类：`complex_edit` / `one_block_local`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 12. `replace_object:141`

- 负例类型/范围：`replace_object` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："Two sheep and a ram stand next to a fence in the yard "
- 原始正描述 2："The fence is next to two sheep and a ram in the yard."
- 原始负描述："Two geese and a ram stand next to a fence in the yard."
- 规范化正描述 1："two sheep and a ram stand next to a fence in the yard"
- 规范化正描述 2："the fence is next to two sheep and a ram in the yard"
- 规范化负描述："two geese and a ram stand next to a fence in the yard"
- 正描述 1 选择元组：`[2, 2, 1, 0.07692307692307693, 0.07547169811320754]`
- 正描述 2 选择元组：`[18, 20, 2, 0.6923076923076923, 0.5660377358490566]`
- 最终比较正描述：`positive_1` / "Two sheep and a ram stand next to a fence in the yard "
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 1, "negative_start": 0, "negative_end": 1, "positive_lexemes": ["two"], "negative_lexemes": ["two"]}, {"tag": "replace", "positive_start": 1, "positive_end": 2, "negative_start": 1, "negative_end": 2, "positive_lexemes": ["sheep"], "negative_lexemes": ["geese"]}, {"tag": "equal", "positive_start": 2, "positive_end": 13, "negative_start": 2, "negative_end": 13, "positive_lexemes": ["and", "a", "ram", "stand", "next", "to", "a", "fence", "in", "the", "yard"], "negative_lexemes": ["and", "a", "ram", "stand", "next", "to", "a", "fence", "in", "the", "yard"]}]`
- 共同前缀：`["two"]`
- 正确 contrast hull：`["sheep"]`
- 错误 contrast hull：`["geese"]`
- 共同后缀：`["and", "a", "ram", "stand", "next", "to", "a", "fence", "in", "the", "yard"]`
- Hull token 覆盖率（正/负/最大）：`[0.10526315789473684, 0.15, 0.15]`
- 共同前缀模型 token：`[119, 122, 114]`
- 正确 hull 模型 token：IDs `[3191, 1522]`；text " sheep"
- 错误 hull 模型 token：IDs `[492, 104, 2023]`；text " geese"
- 第一轮/第二轮分类：`complex_edit` / `one_block_local`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 13. `replace_object:1498`

- 负例类型/范围：`replace_object` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A group of motorists pass very large buildings in asia."
- 原始正描述 2："A group of motorbike drivers are passing by enormous buildings in Asia."
- 原始负描述："A group of cyclists pass very large buildings in Asia."
- 规范化正描述 1："a group of motorists pass very large buildings in asia"
- 规范化正描述 2："a group of motorbike drivers are passing by enormous buildings in asia"
- 规范化负描述："a group of cyclists pass very large buildings in asia"
- 正描述 1 选择元组：`[2, 2, 1, 0.1, 0.09259259259259259]`
- 正描述 2 选择元组：`[10, 10, 2, 0.5, 0.44285714285714284]`
- 最终比较正描述：`positive_1` / "A group of motorists pass very large buildings in asia."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 3, "negative_start": 0, "negative_end": 3, "positive_lexemes": ["a", "group", "of"], "negative_lexemes": ["a", "group", "of"]}, {"tag": "replace", "positive_start": 3, "positive_end": 4, "negative_start": 3, "negative_end": 4, "positive_lexemes": ["motorists"], "negative_lexemes": ["cyclists"]}, {"tag": "equal", "positive_start": 4, "positive_end": 10, "negative_start": 4, "negative_end": 10, "positive_lexemes": ["pass", "very", "large", "buildings", "in", "asia"], "negative_lexemes": ["pass", "very", "large", "buildings", "in", "asia"]}]`
- 共同前缀：`["a", "group", "of"]`
- 正确 contrast hull：`["motorists"]`
- 错误 contrast hull：`["cyclists"]`
- 共同后缀：`["pass", "very", "large", "buildings", "in", "asia"]`
- Hull token 覆盖率（正/负/最大）：`[0.26666666666666666, 0.21428571428571427, 0.26666666666666666]`
- 共同前缀模型 token：`[100, 4592, 354]`
- 正确 hull 模型 token：IDs `[351, 593, 336, 4638]`；text " motorists"
- 错误 hull 模型 token：IDs `[6284, 1110, 4638]`；text " cyclists"
- 第一轮/第二轮分类：`complex_edit` / `one_block_local`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 14. `replace_object:1623`

- 负例类型/范围：`replace_object` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": false}`
- 原始正描述 1："THERE IS A BATHROOM WITH A SINK AND A MIRROR "
- 原始正描述 2："The sink and mirror are located in a bathroom."
- 原始负描述："There is a bedroom with a sink and a mirror."
- 规范化正描述 1："there is a bathroom with a sink and a mirror"
- 规范化正描述 2："the sink and mirror are located in a bathroom"
- 规范化负描述："there is a bedroom with a sink and a mirror"
- 正描述 1 选择元组：`[2, 2, 1, 0.1, 0.06818181818181818]`
- 正描述 2 选择元组：`[17, 19, 3, 0.9, 0.6888888888888889]`
- 最终比较正描述：`positive_1` / "THERE IS A BATHROOM WITH A SINK AND A MIRROR "
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 3, "negative_start": 0, "negative_end": 3, "positive_lexemes": ["there", "is", "a"], "negative_lexemes": ["there", "is", "a"]}, {"tag": "replace", "positive_start": 3, "positive_end": 4, "negative_start": 3, "negative_end": 4, "positive_lexemes": ["bathroom"], "negative_lexemes": ["bedroom"]}, {"tag": "equal", "positive_start": 4, "positive_end": 10, "negative_start": 4, "negative_end": 10, "positive_lexemes": ["with", "a", "sink", "and", "a", "mirror"], "negative_lexemes": ["with", "a", "sink", "and", "a", "mirror"]}]`
- 共同前缀：`["there", "is", "a"]`
- 正确 contrast hull：`["bathroom"]`
- 错误 contrast hull：`["bedroom"]`
- 共同后缀：`["with", "a", "sink", "and", "a", "mirror"]`
- Hull token 覆盖率（正/负/最大）：`[0.23529411764705882, 0.23529411764705882, 0.23529411764705882]`
- 共同前缀模型 token：`[119, 2503, 395, 299]`
- 正确 hull 模型 token：IDs `[363, 1831, 393, 444]`；text " bathroom"
- 错误 hull 模型 token：IDs `[363, 382, 393, 444]`；text " bedroom"
- 第一轮/第二轮分类：`complex_edit` / `one_block_local`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 15. `replace_object:449`

- 负例类型/范围：`replace_object` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A cow is leashed up to a green pole near the civilians. "
- 原始正描述 2："The green pole is positioned near the civilians, and a cow is leashed up to it."
- 原始负描述："A donkey is leashed up to a green pole near the civilians."
- 规范化正描述 1："a cow is leashed up to a green pole near the civilians"
- 规范化正描述 2："the green pole is positioned near the civilians , and a cow is leashed up to it"
- 规范化负描述："a donkey is leashed up to a green pole near the civilians"
- 正描述 1 选择元组：`[2, 2, 1, 0.08333333333333333, 0.08771929824561403]`
- 正描述 2 选择元组：`[25, 29, 6, 0.8823529411764706, 0.759493670886076]`
- 最终比较正描述：`positive_1` / "A cow is leashed up to a green pole near the civilians. "
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 1, "negative_start": 0, "negative_end": 1, "positive_lexemes": ["a"], "negative_lexemes": ["a"]}, {"tag": "replace", "positive_start": 1, "positive_end": 2, "negative_start": 1, "negative_end": 2, "positive_lexemes": ["cow"], "negative_lexemes": ["donkey"]}, {"tag": "equal", "positive_start": 2, "positive_end": 12, "negative_start": 2, "negative_end": 12, "positive_lexemes": ["is", "leashed", "up", "to", "a", "green", "pole", "near", "the", "civilians"], "negative_lexemes": ["is", "leashed", "up", "to", "a", "green", "pole", "near", "the", "civilians"]}]`
- 共同前缀：`["a"]`
- 正确 contrast hull：`["cow"]`
- 错误 contrast hull：`["donkey"]`
- 共同后缀：`["is", "leashed", "up", "to", "a", "green", "pole", "near", "the", "civilians"]`
- Hull token 覆盖率（正/负/最大）：`[0.09523809523809523, 0.09523809523809523, 0.09523809523809523]`
- 共同前缀模型 token：`[100]`
- 正确 hull 模型 token：IDs `[317, 451]`；text " cow"
- 错误 hull 模型 token：IDs `[2207, 5421]`；text " donkey"
- 第一轮/第二轮分类：`complex_edit` / `one_block_local`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 16. `replace_object:517`

- 负例类型/范围：`replace_object` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："there is a very beautiful zebra that is standing in the shade"
- 原始正描述 2："The zebra that is looking gorgeous is standing in the shade."
- 原始负描述："There is a very beautiful gazelle that is standing in the shade."
- 规范化正描述 1："there is a very beautiful zebra that is standing in the shade"
- 规范化正描述 2："the zebra that is looking gorgeous is standing in the shade"
- 规范化负描述："there is a very beautiful gazelle that is standing in the shade"
- 正描述 1 选择元组：`[2, 2, 1, 0.08333333333333333, 0.07936507936507936]`
- 正描述 2 选择元组：`[13, 13, 2, 0.5833333333333334, 0.47619047619047616]`
- 最终比较正描述：`positive_1` / "there is a very beautiful zebra that is standing in the shade"
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 5, "negative_start": 0, "negative_end": 5, "positive_lexemes": ["there", "is", "a", "very", "beautiful"], "negative_lexemes": ["there", "is", "a", "very", "beautiful"]}, {"tag": "replace", "positive_start": 5, "positive_end": 6, "negative_start": 5, "negative_end": 6, "positive_lexemes": ["zebra"], "negative_lexemes": ["gazelle"]}, {"tag": "equal", "positive_start": 6, "positive_end": 12, "negative_start": 6, "negative_end": 12, "positive_lexemes": ["that", "is", "standing", "in", "the", "shade"], "negative_lexemes": ["that", "is", "standing", "in", "the", "shade"]}]`
- 共同前缀：`["there", "is", "a", "very", "beautiful"]`
- 正确 contrast hull：`["zebra"]`
- 错误 contrast hull：`["gazelle"]`
- 共同后缀：`["that", "is", "standing", "in", "the", "shade"]`
- Hull token 覆盖率（正/负/最大）：`[0.15789473684210525, 0.23809523809523808, 0.23809523809523808]`
- 共同前缀模型 token：`[119, 2503, 395, 299, 4965, 3979, 507, 549]`
- 正确 hull 模型 token：IDs `[3243, 3037, 559]`；text " zebra"
- 错误 hull 模型 token：IDs `[492, 100, 125, 446, 361]`；text " gazelle"
- 第一轮/第二轮分类：`complex_edit` / `one_block_local`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 17. `replace_object:54`

- 负例类型/范围：`replace_object` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："The man is looking into a mirror holding a toothbrush. "
- 原始正描述 2："The man holds a toothbrush while looking into a mirror."
- 原始负描述："The woman is looking into a mirror holding a toothbrush."
- 规范化正描述 1："the man is looking into a mirror holding a toothbrush"
- 规范化正描述 2："the man holds a toothbrush while looking into a mirror"
- 规范化负描述："the woman is looking into a mirror holding a toothbrush"
- 正描述 1 选择元组：`[2, 2, 1, 0.1, 0.03636363636363636]`
- 正描述 2 选择元组：`[16, 18, 2, 0.8, 0.6909090909090909]`
- 最终比较正描述：`positive_1` / "The man is looking into a mirror holding a toothbrush. "
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 1, "negative_start": 0, "negative_end": 1, "positive_lexemes": ["the"], "negative_lexemes": ["the"]}, {"tag": "replace", "positive_start": 1, "positive_end": 2, "negative_start": 1, "negative_end": 2, "positive_lexemes": ["man"], "negative_lexemes": ["woman"]}, {"tag": "equal", "positive_start": 2, "positive_end": 10, "negative_start": 2, "negative_end": 10, "positive_lexemes": ["is", "looking", "into", "a", "mirror", "holding", "a", "toothbrush"], "negative_lexemes": ["is", "looking", "into", "a", "mirror", "holding", "a", "toothbrush"]}]`
- 共同前缀：`["the"]`
- 正确 contrast hull：`["man"]`
- 错误 contrast hull：`["woman"]`
- 共同后缀：`["is", "looking", "into", "a", "mirror", "holding", "a", "toothbrush"]`
- Hull token 覆盖率（正/负/最大）：`[0.05263157894736842, 0.14285714285714285, 0.14285714285714285]`
- 共同前缀模型 token：`[4345]`
- 正确 hull 模型 token：IDs `[1672]`；text " man"
- 错误 hull 模型 token：IDs `[339, 444, 325]`；text " woman"
- 第一轮/第二轮分类：`complex_edit` / `one_block_local`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 18. `replace_object:87`

- 负例类型/范围：`replace_object` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A man on a tennis court holding a racket. "
- 原始正描述 2："A man is holding a racket on a tennis court."
- 原始负描述："A woman on a tennis court holding a racket."
- 规范化正描述 1："a man on a tennis court holding a racket"
- 规范化正描述 2："a man is holding a racket on a tennis court"
- 规范化负描述："a woman on a tennis court holding a racket"
- 正描述 1 选择元组：`[2, 2, 1, 0.1111111111111111, 0.047619047619047616]`
- 正描述 2 选择元组：`[15, 17, 3, 0.8, 0.7441860465116279]`
- 最终比较正描述：`positive_1` / "A man on a tennis court holding a racket. "
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 1, "negative_start": 0, "negative_end": 1, "positive_lexemes": ["a"], "negative_lexemes": ["a"]}, {"tag": "replace", "positive_start": 1, "positive_end": 2, "negative_start": 1, "negative_end": 2, "positive_lexemes": ["man"], "negative_lexemes": ["woman"]}, {"tag": "equal", "positive_start": 2, "positive_end": 9, "negative_start": 2, "negative_end": 9, "positive_lexemes": ["on", "a", "tennis", "court", "holding", "a", "racket"], "negative_lexemes": ["on", "a", "tennis", "court", "holding", "a", "racket"]}]`
- 共同前缀：`["a"]`
- 正确 contrast hull：`["man"]`
- 错误 contrast hull：`["woman"]`
- 共同后缀：`["on", "a", "tennis", "court", "holding", "a", "racket"]`
- Hull token 覆盖率（正/负/最大）：`[0.0625, 0.16666666666666666, 0.16666666666666666]`
- 共同前缀模型 token：`[100]`
- 正确 hull 模型 token：IDs `[1672]`；text " man"
- 错误 hull 模型 token：IDs `[339, 444, 325]`；text " woman"
- 第一轮/第二轮分类：`complex_edit` / `one_block_local`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 19. `replace_object:996`

- 负例类型/范围：`replace_object` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A bus and other cars driving down a multi-laned street ."
- 原始正描述 2："Several cars and a bus are driving down a street with multiple lanes."
- 原始负描述："A motorcycle and other cars driving down a multi-laned street."
- 规范化正描述 1："a bus and other cars driving down a multi-laned street"
- 规范化正描述 2："several cars and a bus are driving down a street with multiple lanes"
- 规范化负描述："a motorcycle and other cars driving down a multi-laned street"
- 正描述 1 选择元组：`[2, 2, 1, 0.1, 0.16393442622950818]`
- 正描述 2 选择元组：`[15, 23, 5, 0.6923076923076923, 0.5882352941176471]`
- 最终比较正描述：`positive_1` / "A bus and other cars driving down a multi-laned street ."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 1, "negative_start": 0, "negative_end": 1, "positive_lexemes": ["a"], "negative_lexemes": ["a"]}, {"tag": "replace", "positive_start": 1, "positive_end": 2, "negative_start": 1, "negative_end": 2, "positive_lexemes": ["bus"], "negative_lexemes": ["motorcycle"]}, {"tag": "equal", "positive_start": 2, "positive_end": 10, "negative_start": 2, "negative_end": 10, "positive_lexemes": ["and", "other", "cars", "driving", "down", "a", "multi-laned", "street"], "negative_lexemes": ["and", "other", "cars", "driving", "down", "a", "multi-laned", "street"]}]`
- 共同前缀：`["a"]`
- 正确 contrast hull：`["bus"]`
- 错误 contrast hull：`["motorcycle"]`
- 共同后缀：`["and", "other", "cars", "driving", "down", "a", "multi-laned", "street"]`
- Hull token 覆盖率（正/负/最大）：`[0.058823529411764705, 0.23809523809523808, 0.23809523809523808]`
- 共同前缀模型 token：`[100]`
- 正确 hull 模型 token：IDs `[2499]`；text " bus"
- 错误 hull 模型 token：IDs `[351, 593, 336, 2863, 2945]`；text " motorcycle"
- 第一轮/第二轮分类：`complex_edit` / `one_block_local`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 20. `replace_relation:1261`

- 负例类型/范围：`replace_relation` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A brown teddy bear sitting on an odd looking chair"
- 原始正描述 2："An unusual chair has the brown teddy bear sitting on it."
- 原始负描述："A brown teddy bear lying under an odd looking chair."
- 规范化正描述 1："a brown teddy bear sitting on an odd looking chair"
- 规范化正描述 2："an unusual chair has the brown teddy bear sitting on it"
- 规范化负描述："a brown teddy bear lying under an odd looking chair"
- 正描述 1 选择元组：`[4, 4, 1, 0.2, 0.1568627450980392]`
- 正描述 2 选择元组：`[21, 21, 2, 1.0, 0.7636363636363637]`
- 最终比较正描述：`positive_1` / "A brown teddy bear sitting on an odd looking chair"
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 4, "negative_start": 0, "negative_end": 4, "positive_lexemes": ["a", "brown", "teddy", "bear"], "negative_lexemes": ["a", "brown", "teddy", "bear"]}, {"tag": "replace", "positive_start": 4, "positive_end": 6, "negative_start": 4, "negative_end": 6, "positive_lexemes": ["sitting", "on"], "negative_lexemes": ["lying", "under"]}, {"tag": "equal", "positive_start": 6, "positive_end": 10, "negative_start": 6, "negative_end": 10, "positive_lexemes": ["an", "odd", "looking", "chair"], "negative_lexemes": ["an", "odd", "looking", "chair"]}]`
- 共同前缀：`["a", "brown", "teddy", "bear"]`
- 正确 contrast hull：`["sitting", "on"]`
- 错误 contrast hull：`["lying", "under"]`
- 共同后缀：`["an", "odd", "looking", "chair"]`
- Hull token 覆盖率（正/负/最大）：`[0.15789473684210525, 0.2, 0.2]`
- 共同前缀模型 token：`[100, 363, 2079, 113, 297, 382, 103, 124, 600, 370]`
- 正确 hull 模型 token：IDs `[5305, 2912, 619]`；text " sitting on"
- 错误 hull 模型 token：IDs `[406, 124, 350, 1943]`；text " lying under"
- 第一轮/第二轮分类：`complex_edit` / `one_block_local`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 21. `replace_relation:1330`

- 负例类型/范围：`replace_relation` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："a lake with a lot of boats on it"
- 原始正描述 2："There are a lot of boats on a lake."
- 原始负描述："A lake with a lot of boats beside it."
- 规范化正描述 1："a lake with a lot of boats on it"
- 规范化正描述 2："there are a lot of boats on a lake"
- 规范化负描述："a lake with a lot of boats beside it"
- 正描述 1 选择元组：`[2, 2, 1, 0.1111111111111111, 0.16666666666666666]`
- 正描述 2 选择元组：`[10, 18, 4, 0.6666666666666666, 0.5]`
- 最终比较正描述：`positive_1` / "a lake with a lot of boats on it"
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 7, "negative_start": 0, "negative_end": 7, "positive_lexemes": ["a", "lake", "with", "a", "lot", "of", "boats"], "negative_lexemes": ["a", "lake", "with", "a", "lot", "of", "boats"]}, {"tag": "replace", "positive_start": 7, "positive_end": 8, "negative_start": 7, "negative_end": 8, "positive_lexemes": ["on"], "negative_lexemes": ["beside"]}, {"tag": "equal", "positive_start": 8, "positive_end": 9, "negative_start": 8, "negative_end": 9, "positive_lexemes": ["it"], "negative_lexemes": ["it"]}]`
- 共同前缀：`["a", "lake", "with", "a", "lot", "of", "boats"]`
- 正确 contrast hull：`["on"]`
- 错误 contrast hull：`["beside"]`
- 共同后缀：`["it"]`
- Hull token 覆盖率（正/负/最大）：`[0.08333333333333333, 0.21428571428571427, 0.21428571428571427]`
- 共同前缀模型 token：`[100, 406, 2434, 599, 299, 406, 593, 354, 1847, 4585]`
- 正确 hull 模型 token：IDs `[619]`；text " on"
- 错误 hull 模型 token：IDs `[363, 329, 688]`；text " beside"
- 第一轮/第二轮分类：`complex_edit` / `one_block_local`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 22. `replace_relation:1340`

- 负例类型/范围：`replace_relation` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A bunch of people gathered inside of a building"
- 原始正描述 2："A gathering of people inside a building."
- 原始负描述："A bunch of people scattered outside of a building."
- 规范化正描述 1："a bunch of people gathered inside of a building"
- 规范化正描述 2："a gathering of people inside a building"
- 规范化负描述："a bunch of people scattered outside of a building"
- 正描述 1 选择元组：`[4, 4, 1, 0.2222222222222222, 0.12244897959183673]`
- 正描述 2 选择元组：`[6, 10, 3, 0.4444444444444444, 0.5102040816326531]`
- 最终比较正描述：`positive_1` / "A bunch of people gathered inside of a building"
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 4, "negative_start": 0, "negative_end": 4, "positive_lexemes": ["a", "bunch", "of", "people"], "negative_lexemes": ["a", "bunch", "of", "people"]}, {"tag": "replace", "positive_start": 4, "positive_end": 6, "negative_start": 4, "negative_end": 6, "positive_lexemes": ["gathered", "inside"], "negative_lexemes": ["scattered", "outside"]}, {"tag": "equal", "positive_start": 6, "positive_end": 9, "negative_start": 6, "negative_end": 9, "positive_lexemes": ["of", "a", "building"], "negative_lexemes": ["of", "a", "building"]}]`
- 共同前缀：`["a", "bunch", "of", "people"]`
- 正确 contrast hull：`["gathered", "inside"]`
- 错误 contrast hull：`["scattered", "outside"]`
- 共同后缀：`["of", "a", "building"]`
- Hull token 覆盖率（正/负/最大）：`[0.375, 0.4117647058823529, 0.4117647058823529]`
- 共同前缀模型 token：`[100, 363, 651, 550, 354, 2975]`
- 正确 hull 模型 token：IDs `[492, 314, 300, 1837, 3470, 688]`；text " gathered inside"
- 错误 hull 模型 token：IDs `[1416, 314, 741, 1837, 1695, 118, 688]`；text " scattered outside"
- 第一轮/第二轮分类：`complex_edit` / `one_block_local`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 23. `replace_relation:182`

- 负例类型/范围：`replace_relation` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A group of basketball players walking on the court"
- 原始正描述 2："On a court, walks a group of basketball players."
- 原始负描述："A group of basketball players playing on the court."
- 规范化正描述 1："a group of basketball players walking on the court"
- 规范化正描述 2："on a court , walks a group of basketball players"
- 规范化负描述："a group of basketball players playing on the court"
- 正描述 1 选择元组：`[2, 2, 1, 0.1111111111111111, 0.08]`
- 正描述 2 选择元组：`[17, 19, 2, 0.9, 0.8]`
- 最终比较正描述：`positive_1` / "A group of basketball players walking on the court"
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 5, "negative_start": 0, "negative_end": 5, "positive_lexemes": ["a", "group", "of", "basketball", "players"], "negative_lexemes": ["a", "group", "of", "basketball", "players"]}, {"tag": "replace", "positive_start": 5, "positive_end": 6, "negative_start": 5, "negative_end": 6, "positive_lexemes": ["walking"], "negative_lexemes": ["playing"]}, {"tag": "equal", "positive_start": 6, "positive_end": 9, "negative_start": 6, "negative_end": 9, "positive_lexemes": ["on", "the", "court"], "negative_lexemes": ["on", "the", "court"]}]`
- 共同前缀：`["a", "group", "of", "basketball", "players"]`
- 正确 contrast hull：`["walking"]`
- 错误 contrast hull：`["playing"]`
- 共同后缀：`["on", "the", "court"]`
- Hull token 覆盖率（正/负/最大）：`[0.17647058823529413, 0.125, 0.17647058823529413]`
- 共同前缀模型 token：`[100, 4592, 354, 5207, 110, 439, 101, 1266, 2865, 496]`
- 正确 hull 模型 token：IDs `[339, 352, 1237]`；text " walking"
- 错误 hull 模型 token：IDs `[2865, 350]`；text " playing"
- 第一轮/第二轮分类：`complex_edit` / `one_block_local`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 24. `replace_relation:337`

- 负例类型/范围：`replace_relation` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："Looking down at the spectators and players during a basketball game"
- 原始正描述 2："Observing the players and the spectators from above during a basketball game."
- 原始负描述："Looking down at the spectators and players after a basketball game."
- 规范化正描述 1："looking down at the spectators and players during a basketball game"
- 规范化正描述 2："observing the players and the spectators from above during a basketball game"
- 规范化负描述："looking down at the spectators and players after a basketball game"
- 正描述 1 选择元组：`[2, 2, 1, 0.09090909090909091, 0.08955223880597014]`
- 正描述 2 选择元组：`[13, 17, 3, 0.5833333333333334, 0.4605263157894737]`
- 最终比较正描述：`positive_1` / "Looking down at the spectators and players during a basketball game"
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 7, "negative_start": 0, "negative_end": 7, "positive_lexemes": ["looking", "down", "at", "the", "spectators", "and", "players"], "negative_lexemes": ["looking", "down", "at", "the", "spectators", "and", "players"]}, {"tag": "replace", "positive_start": 7, "positive_end": 8, "negative_start": 7, "negative_end": 8, "positive_lexemes": ["during"], "negative_lexemes": ["after"]}, {"tag": "equal", "positive_start": 8, "positive_end": 11, "negative_start": 8, "negative_end": 11, "positive_lexemes": ["a", "basketball", "game"], "negative_lexemes": ["a", "basketball", "game"]}]`
- 共同前缀：`["looking", "down", "at", "the", "spectators", "and", "players"]`
- 正确 contrast hull：`["during"]`
- 错误 contrast hull：`["after"]`
- 共同后缀：`["a", "basketball", "game"]`
- Hull token 覆盖率（正/负/最大）：`[0.047619047619047616, 0.047619047619047616, 0.047619047619047616]`
- 共同前缀模型 token：`[722, 114, 1237, 4076, 1248, 309, 946, 426, 314, 1945, 376, 2865, 496]`
- 正确 hull 模型 token：IDs `[4266]`；text " during"
- 错误 hull 模型 token：IDs `[3898]`；text " after"
- 第一轮/第二轮分类：`complex_edit` / `one_block_local`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 25. `replace_relation:469`

- 负例类型/范围：`replace_relation` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A cat sitting on a bench in front of a house"
- 原始正描述 2："A cat is seated on a bench situated before a house."
- 原始负描述："A cat sleeping on a bench in front of a house."
- 规范化正描述 1："a cat sitting on a bench in front of a house"
- 规范化正描述 2："a cat is seated on a bench situated before a house"
- 规范化负描述："a cat sleeping on a bench in front of a house"
- 正描述 1 选择元组：`[2, 2, 1, 0.09090909090909091, 0.08888888888888889]`
- 正描述 2 选择元组：`[8, 14, 4, 0.45454545454545453, 0.4]`
- 最终比较正描述：`positive_1` / "A cat sitting on a bench in front of a house"
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 2, "negative_start": 0, "negative_end": 2, "positive_lexemes": ["a", "cat"], "negative_lexemes": ["a", "cat"]}, {"tag": "replace", "positive_start": 2, "positive_end": 3, "negative_start": 2, "negative_end": 3, "positive_lexemes": ["sitting"], "negative_lexemes": ["sleeping"]}, {"tag": "equal", "positive_start": 3, "positive_end": 11, "negative_start": 3, "negative_end": 11, "positive_lexemes": ["on", "a", "bench", "in", "front", "of", "a", "house"], "negative_lexemes": ["on", "a", "bench", "in", "front", "of", "a", "house"]}]`
- 共同前缀：`["a", "cat"]`
- 正确 contrast hull：`["sitting"]`
- 错误 contrast hull：`["sleeping"]`
- 共同后缀：`["on", "a", "bench", "in", "front", "of", "a", "house"]`
- Hull token 覆盖率（正/负/最大）：`[0.125, 0.2222222222222222, 0.2222222222222222]`
- 共同前缀模型 token：`[100, 3706]`
- 正确 hull 模型 token：IDs `[5305, 2912]`；text " sitting"
- 错误 hull 模型 token：IDs `[316, 361, 1522, 350]`；text " sleeping"
- 第一轮/第二轮分类：`complex_edit` / `one_block_local`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 26. `replace_relation:506`

- 负例类型/范围：`replace_relation` / `{"canonical": true, "pilot": true, "formal": false, "certifying_formal": false}`
- 原始正描述 1："some black cattle are grazing in a green field"
- 原始正描述 2："The green field is where some black cattle are grazing."
- 原始负描述："Some black cattle are running through a green field."
- 规范化正描述 1："some black cattle are grazing in a green field"
- 规范化正描述 2："the green field is where some black cattle are grazing"
- 规范化负描述："some black cattle are running through a green field"
- 正描述 1 选择元组：`[4, 4, 1, 0.2222222222222222, 0.21568627450980393]`
- 正描述 2 选择元组：`[19, 19, 2, 1.0, 0.8333333333333334]`
- 最终比较正描述：`positive_1` / "some black cattle are grazing in a green field"
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 4, "negative_start": 0, "negative_end": 4, "positive_lexemes": ["some", "black", "cattle", "are"], "negative_lexemes": ["some", "black", "cattle", "are"]}, {"tag": "replace", "positive_start": 4, "positive_end": 6, "negative_start": 4, "negative_end": 6, "positive_lexemes": ["grazing", "in"], "negative_lexemes": ["running", "through"]}, {"tag": "equal", "positive_start": 6, "positive_end": 9, "negative_start": 6, "negative_end": 9, "positive_lexemes": ["a", "green", "field"], "negative_lexemes": ["a", "green", "field"]}]`
- 共同前缀：`["some", "black", "cattle", "are"]`
- 正确 contrast hull：`["grazing", "in"]`
- 错误 contrast hull：`["running", "through"]`
- 共同后缀：`["a", "green", "field"]`
- Hull token 覆盖率（正/负/最大）：`[0.2857142857142857, 0.23076923076923078, 0.2857142857142857]`
- 共同前缀模型 token：`[118, 3219, 2597, 1637, 3706, 5395, 732]`
- 正确 hull 模型 token：IDs `[5528, 125, 350, 353]`；text " grazing in"
- 错误 hull 模型 token：IDs `[3161, 1795, 2309]`；text " running through"
- 第一轮/第二轮分类：`complex_edit` / `one_block_local`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 27. `replace_relation:641`

- 负例类型/范围：`replace_relation` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A room with a fire extinguisher, mugs hanging from a shelf and several lights. "
- 原始正描述 2："A room with mugs hanging from a shelf, several lights and a fire extinguisher."
- 原始负描述："A room without a fire extinguisher, mugs hanging from a shelf and several lights."
- 规范化正描述 1："a room with a fire extinguisher , mugs hanging from a shelf and several lights"
- 规范化正描述 2："a room with mugs hanging from a shelf , several lights and a fire extinguisher"
- 规范化负描述："a room without a fire extinguisher , mugs hanging from a shelf and several lights"
- 正描述 1 选择元组：`[2, 2, 1, 0.06666666666666667, 0.037037037037037035]`
- 正描述 2 选择元组：`[12, 26, 4, 0.6666666666666666, 0.6419753086419753]`
- 最终比较正描述：`positive_1` / "A room with a fire extinguisher, mugs hanging from a shelf and several lights. "
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 2, "negative_start": 0, "negative_end": 2, "positive_lexemes": ["a", "room"], "negative_lexemes": ["a", "room"]}, {"tag": "replace", "positive_start": 2, "positive_end": 3, "negative_start": 2, "negative_end": 3, "positive_lexemes": ["with"], "negative_lexemes": ["without"]}, {"tag": "equal", "positive_start": 3, "positive_end": 15, "negative_start": 3, "negative_end": 15, "positive_lexemes": ["a", "fire", "extinguisher", ",", "mugs", "hanging", "from", "a", "shelf", "and", "several", "lights"], "negative_lexemes": ["a", "fire", "extinguisher", ",", "mugs", "hanging", "from", "a", "shelf", "and", "several", "lights"]}]`
- 共同前缀：`["a", "room"]`
- 正确 contrast hull：`["with"]`
- 错误 contrast hull：`["without"]`
- 共同后缀：`["a", "fire", "extinguisher", ",", "mugs", "hanging", "from", "a", "shelf", "and", "several", "lights"]`
- Hull token 覆盖率（正/负/最大）：`[0.034482758620689655, 0.034482758620689655, 0.034482758620689655]`
- 共同前缀模型 token：`[100, 1552, 444]`
- 正确 hull 模型 token：IDs `[599]`；text " with"
- 错误 hull 模型 token：IDs `[4007]`；text " without"
- 第一轮/第二轮分类：`complex_edit` / `one_block_local`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 28. `replace_relation:822`

- 负例类型/范围：`replace_relation` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："Some bananas and strawberries on a large waffle"
- 原始正描述 2："A large waffle has bananas and strawberries on it."
- 原始负描述："Some bananas and strawberries beside a large waffle."
- 规范化正描述 1："some bananas and strawberries on a large waffle"
- 规范化正描述 2："a large waffle has bananas and strawberries on it"
- 规范化负描述："some bananas and strawberries beside a large waffle"
- 正描述 1 选择元组：`[2, 2, 1, 0.125, 0.11764705882352941]`
- 正描述 2 选择元组：`[11, 17, 4, 0.8888888888888888, 0.7254901960784313]`
- 最终比较正描述：`positive_1` / "Some bananas and strawberries on a large waffle"
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 4, "negative_start": 0, "negative_end": 4, "positive_lexemes": ["some", "bananas", "and", "strawberries"], "negative_lexemes": ["some", "bananas", "and", "strawberries"]}, {"tag": "replace", "positive_start": 4, "positive_end": 5, "negative_start": 4, "negative_end": 5, "positive_lexemes": ["on"], "negative_lexemes": ["beside"]}, {"tag": "equal", "positive_start": 5, "positive_end": 8, "negative_start": 5, "negative_end": 8, "positive_lexemes": ["a", "large", "waffle"], "negative_lexemes": ["a", "large", "waffle"]}]`
- 共同前缀：`["some", "bananas", "and", "strawberries"]`
- 正确 contrast hull：`["on"]`
- 错误 contrast hull：`["beside"]`
- 共同后缀：`["a", "large", "waffle"]`
- Hull token 覆盖率（正/负/最大）：`[0.05263157894736842, 0.14285714285714285, 0.14285714285714285]`
- 共同前缀模型 token：`[118, 3219, 363, 325, 325, 390, 376, 580, 559, 122, 2009, 3603]`
- 正确 hull 模型 token：IDs `[619]`；text " on"
- 错误 hull 模型 token：IDs `[363, 329, 688]`；text " beside"
- 第一轮/第二轮分类：`complex_edit` / `one_block_local`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 29. `replace_relation:975`

- 负例类型/范围：`replace_relation` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："Plate of crackers with something spread on them next to a keyboard"
- 原始正描述 2："Next to a keyboard is a plate with crackers having something spread on them."
- 原始负描述："Plate of crackers with something spread on them away from a keyboard."
- 规范化正描述 1："plate of crackers with something spread on them next to a keyboard"
- 规范化正描述 2："next to a keyboard is a plate with crackers having something spread on them"
- 规范化负描述："plate of crackers with something spread on them away from a keyboard"
- 正描述 1 选择元组：`[4, 4, 1, 0.16666666666666666, 0.10294117647058823]`
- 正描述 2 选择元组：`[14, 26, 4, 0.8571428571428571, 0.72]`
- 最终比较正描述：`positive_1` / "Plate of crackers with something spread on them next to a keyboard"
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 8, "negative_start": 0, "negative_end": 8, "positive_lexemes": ["plate", "of", "crackers", "with", "something", "spread", "on", "them"], "negative_lexemes": ["plate", "of", "crackers", "with", "something", "spread", "on", "them"]}, {"tag": "replace", "positive_start": 8, "positive_end": 10, "negative_start": 8, "negative_end": 10, "positive_lexemes": ["next", "to"], "negative_lexemes": ["away", "from"]}, {"tag": "equal", "positive_start": 10, "positive_end": 12, "negative_start": 10, "negative_end": 12, "positive_lexemes": ["a", "keyboard"], "negative_lexemes": ["a", "keyboard"]}]`
- 共同前缀：`["plate", "of", "crackers", "with", "something", "spread", "on", "them"]`
- 正确 contrast hull：`["next", "to"]`
- 错误 contrast hull：`["away", "from"]`
- 共同后缀：`["a", "keyboard"]`
- Hull token 覆盖率（正/负/最大）：`[0.1, 0.14285714285714285, 0.14285714285714285]`
- 共同前缀模型 token：`[992, 557, 354, 317, 559, 892, 496, 599, 2798, 1772, 3489, 619, 2105]`
- 正确 hull 模型 token：IDs `[4658, 364]`；text " next to"
- 错误 hull 模型 token：IDs `[299, 5054, 961]`；text " away from"
- 第一轮/第二轮分类：`complex_edit` / `one_block_local`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 30. `swap_object:187`

- 负例类型/范围：`swap_object` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："People watch a person delivering a lecture on a screen."
- 原始正描述 2："The person delivering a lecture is on a screen, and people are watching him."
- 原始负描述："A person watches people delivering a lecture on a screen."
- 规范化正描述 1："people watch a person delivering a lecture on a screen"
- 规范化正描述 2："the person delivering a lecture is on a screen , and people are watching him"
- 规范化负描述："a person watches people delivering a lecture on a screen"
- 正描述 1 选择元组：`[8, 8, 1, 0.4, 0.21428571428571427]`
- 正描述 2 选择元组：`[11, 25, 4, 0.6666666666666666, 0.6578947368421053]`
- 最终比较正描述：`positive_1` / "People watch a person delivering a lecture on a screen."
- 完整 lexeme 编辑块：`[{"tag": "replace", "positive_start": 0, "positive_end": 4, "negative_start": 0, "negative_end": 4, "positive_lexemes": ["people", "watch", "a", "person"], "negative_lexemes": ["a", "person", "watches", "people"]}, {"tag": "equal", "positive_start": 4, "positive_end": 10, "negative_start": 4, "negative_end": 10, "positive_lexemes": ["delivering", "a", "lecture", "on", "a", "screen"], "negative_lexemes": ["delivering", "a", "lecture", "on", "a", "screen"]}]`
- 共同前缀：`[]`
- 正确 contrast hull：`["people", "watch", "a", "person"]`
- 错误 contrast hull：`["a", "person", "watches", "people"]`
- 共同后缀：`["delivering", "a", "lecture", "on", "a", "screen"]`
- Hull token 覆盖率（正/负/最大）：`[0.3333333333333333, 0.3333333333333333, 0.3333333333333333]`
- 共同前缀模型 token：`[]`
- 正确 hull 模型 token：IDs `[653, 2643, 339, 6131, 299, 2198]`；text "people watch a person"
- 错误 hull 模型 token：IDs `[100, 2198, 339, 314, 4298, 2975]`；text "a person watches people"
- 第一轮/第二轮分类：`complex_edit` / `one_block_local`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

## 两块编辑且 hull 不超过 50%

候选 `1225` 条，本节抽取 `30` 条。

### 1. `replace_attribute:241`

- 负例类型/范围：`replace_attribute` / `{"canonical": true, "pilot": true, "formal": false, "certifying_formal": false}`
- 原始正描述 1："A line of neon colored motorcycles parked in front of a bar."
- 原始正描述 2："Neon-colored motorcycles are lined in the parked area in front of a bar."
- 原始负描述："A line of matte motorcycles parked in front of a bar."
- 规范化正描述 1："a line of neon colored motorcycles parked in front of a bar"
- 规范化正描述 2："neon-colored motorcycles are lined in the parked area in front of a bar"
- 规范化负描述："a line of matte motorcycles parked in front of a bar"
- 正描述 1 选择元组：`[3, 3, 2, 0.16666666666666666, 0.1864406779661017]`
- 正描述 2 选择元组：`[12, 14, 3, 0.5384615384615384, 0.49295774647887325]`
- 最终比较正描述：`positive_1` / "A line of neon colored motorcycles parked in front of a bar."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 3, "negative_start": 0, "negative_end": 3, "positive_lexemes": ["a", "line", "of"], "negative_lexemes": ["a", "line", "of"]}, {"tag": "delete", "positive_start": 3, "positive_end": 4, "negative_start": 3, "negative_end": 3, "positive_lexemes": ["neon"], "negative_lexemes": []}, {"tag": "replace", "positive_start": 4, "positive_end": 5, "negative_start": 3, "negative_end": 4, "positive_lexemes": ["colored"], "negative_lexemes": ["matte"]}, {"tag": "equal", "positive_start": 5, "positive_end": 12, "negative_start": 4, "negative_end": 11, "positive_lexemes": ["motorcycles", "parked", "in", "front", "of", "a", "bar"], "negative_lexemes": ["motorcycles", "parked", "in", "front", "of", "a", "bar"]}]`
- 共同前缀：`["a", "line", "of"]`
- 正确 contrast hull：`["neon", "colored"]`
- 错误 contrast hull：`["matte"]`
- 共同后缀：`["motorcycles", "parked", "in", "front", "of", "a", "bar"]`
- Hull token 覆盖率（正/负/最大）：`[0.2, 0.09090909090909091, 0.2]`
- 共同前缀模型 token：`[100, 2909, 354]`
- 正确 hull 模型 token：IDs `[730, 310, 1683, 1239, 103]`；text " neon colored"
- 错误 hull 模型 token：IDs `[2366, 741]`；text " matte"
- 第一轮/第二轮分类：`unique_alignment` / `multi_block_local_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 2. `replace_attribute:388`

- 负例类型/范围：`replace_attribute` / `{"canonical": true, "pilot": true, "formal": false, "certifying_formal": false}`
- 原始正描述 1："A pizza with vegetables and cheese resting on a board."
- 原始正描述 2："A pizza is positioned on a board with cheese and vegetables."
- 原始负描述："A pizza with vegetables and vegan toppings resting on a board."
- 规范化正描述 1："a pizza with vegetables and cheese resting on a board"
- 规范化正描述 2："a pizza is positioned on a board with cheese and vegetables"
- 规范化负描述："a pizza with vegetables and vegan toppings resting on a board"
- 正描述 1 选择元组：`[3, 3, 2, 0.18181818181818182, 0.22950819672131148]`
- 正描述 2 选择元组：`[18, 18, 1, 0.8181818181818182, 0.7049180327868853]`
- 最终比较正描述：`positive_1` / "A pizza with vegetables and cheese resting on a board."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 5, "negative_start": 0, "negative_end": 5, "positive_lexemes": ["a", "pizza", "with", "vegetables", "and"], "negative_lexemes": ["a", "pizza", "with", "vegetables", "and"]}, {"tag": "insert", "positive_start": 5, "positive_end": 5, "negative_start": 5, "negative_end": 6, "positive_lexemes": [], "negative_lexemes": ["vegan"]}, {"tag": "replace", "positive_start": 5, "positive_end": 6, "negative_start": 6, "negative_end": 7, "positive_lexemes": ["cheese"], "negative_lexemes": ["toppings"]}, {"tag": "equal", "positive_start": 6, "positive_end": 10, "negative_start": 7, "negative_end": 11, "positive_lexemes": ["resting", "on", "a", "board"], "negative_lexemes": ["resting", "on", "a", "board"]}]`
- 共同前缀：`["a", "pizza", "with", "vegetables", "and"]`
- 正确 contrast hull：`["cheese"]`
- 错误 contrast hull：`["vegan", "toppings"]`
- 共同后缀：`["resting", "on", "a", "board"]`
- Hull token 覆盖率（正/负/最大）：`[0.1111111111111111, 0.23809523809523808, 0.23809523809523808]`
- 共同前缀模型 token：`[100, 344, 1028, 125, 100, 599, 4389, 2353, 4880, 376]`
- 正确 hull 模型 token：IDs `[1806, 2023]`；text " cheese"
- 错误 hull 模型 token：IDs `[4389, 3249, 364, 737, 2557]`；text " vegan toppings"
- 第一轮/第二轮分类：`unique_alignment` / `multi_block_local_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 3. `replace_object:1042`

- 负例类型/范围：`replace_object` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A clock suspended on the outside of a brown stone building."
- 原始正描述 2："A clock hanging on the exterior of a brown stone building."
- 原始负描述："A clock suspended on the outside of a skyscraper."
- 规范化正描述 1："a clock suspended on the outside of a brown stone building"
- 规范化正描述 2："a clock hanging on the exterior of a brown stone building"
- 规范化负描述："a clock suspended on the outside of a skyscraper"
- 正描述 1 选择元组：`[4, 4, 2, 0.2727272727272727, 0.3275862068965517]`
- 正描述 2 选择元组：`[8, 16, 4, 0.45454545454545453, 0.5789473684210527]`
- 最终比较正描述：`positive_1` / "A clock suspended on the outside of a brown stone building."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 8, "negative_start": 0, "negative_end": 8, "positive_lexemes": ["a", "clock", "suspended", "on", "the", "outside", "of", "a"], "negative_lexemes": ["a", "clock", "suspended", "on", "the", "outside", "of", "a"]}, {"tag": "delete", "positive_start": 8, "positive_end": 10, "negative_start": 8, "negative_end": 8, "positive_lexemes": ["brown", "stone"], "negative_lexemes": []}, {"tag": "replace", "positive_start": 10, "positive_end": 11, "negative_start": 8, "negative_end": 9, "positive_lexemes": ["building"], "negative_lexemes": ["skyscraper"]}]`
- 共同前缀：`["a", "clock", "suspended", "on", "the", "outside", "of", "a"]`
- 正确 contrast hull：`["brown", "stone", "building"]`
- 错误 contrast hull：`["skyscraper"]`
- 共同后缀：`[]`
- Hull token 覆盖率（正/负/最大）：`[0.3181818181818182, 0.25, 0.3181818181818182]`
- 共同前缀模型 token：`[100, 4414, 892, 316, 832, 115, 901, 382, 619, 309, 1695, 118, 688, 354, 299]`
- 正确 hull 模型 token：IDs `[363, 2079, 113, 580, 1634, 6331, 350]`；text " brown stone building"
- 错误 hull 模型 token：IDs `[2549, 2211, 102, 559, 1067]`；text " skyscraper"
- 第一轮/第二轮分类：`unique_alignment` / `multi_block_local_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 4. `replace_object:1109`

- 负例类型/范围：`replace_object` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A fire hydrant painted exactly as the patriotic flag"
- 原始正描述 2："The patriotic flag is painted on the fire hydrant."
- 原始负描述："A bench painted exactly as the patriotic flag."
- 规范化正描述 1："a fire hydrant painted exactly as the patriotic flag"
- 规范化正描述 2："the patriotic flag is painted on the fire hydrant"
- 规范化负描述："a bench painted exactly as the patriotic flag"
- 正描述 1 选择元组：`[3, 3, 2, 0.2222222222222222, 0.21153846153846154]`
- 正描述 2 选择元组：`[15, 17, 3, 0.8888888888888888, 0.7551020408163265]`
- 最终比较正描述：`positive_1` / "A fire hydrant painted exactly as the patriotic flag"
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 1, "negative_start": 0, "negative_end": 1, "positive_lexemes": ["a"], "negative_lexemes": ["a"]}, {"tag": "delete", "positive_start": 1, "positive_end": 2, "negative_start": 1, "negative_end": 1, "positive_lexemes": ["fire"], "negative_lexemes": []}, {"tag": "replace", "positive_start": 2, "positive_end": 3, "negative_start": 1, "negative_end": 2, "positive_lexemes": ["hydrant"], "negative_lexemes": ["bench"]}, {"tag": "equal", "positive_start": 3, "positive_end": 9, "negative_start": 2, "negative_end": 8, "positive_lexemes": ["painted", "exactly", "as", "the", "patriotic", "flag"], "negative_lexemes": ["painted", "exactly", "as", "the", "patriotic", "flag"]}]`
- 共同前缀：`["a"]`
- 正确 contrast hull：`["fire", "hydrant"]`
- 错误 contrast hull：`["bench"]`
- 共同后缀：`["painted", "exactly", "as", "the", "patriotic", "flag"]`
- Hull token 覆盖率（正/负/最大）：`[0.3157894736842105, 0.13333333333333333, 0.3157894736842105]`
- 共同前缀模型 token：`[100]`
- 正确 hull 模型 token：IDs `[341, 1475, 5548, 103, 117, 811]`；text " fire hydrant"
- 错误 hull 模型 token：IDs `[6141, 550]`；text " bench"
- 第一轮/第二轮分类：`complex_edit` / `multi_block_local_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 5. `replace_object:1171`

- 负例类型/范围：`replace_object` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A man with black hair and a top hat"
- 原始正描述 2："A man with black hair is wearing a top hat."
- 原始负描述："A man with a black moustache and a top hat."
- 规范化正描述 1："a man with black hair and a top hat"
- 规范化正描述 2："a man with black hair is wearing a top hat"
- 规范化负描述："a man with a black moustache and a top hat"
- 正描述 1 选择元组：`[3, 5, 2, 0.2, 0.23809523809523808]`
- 正描述 2 选择元组：`[8, 8, 1, 0.4, 0.35714285714285715]`
- 最终比较正描述：`positive_1` / "A man with black hair and a top hat"
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 3, "negative_start": 0, "negative_end": 3, "positive_lexemes": ["a", "man", "with"], "negative_lexemes": ["a", "man", "with"]}, {"tag": "insert", "positive_start": 3, "positive_end": 3, "negative_start": 3, "negative_end": 4, "positive_lexemes": [], "negative_lexemes": ["a"]}, {"tag": "equal", "positive_start": 3, "positive_end": 4, "negative_start": 4, "negative_end": 5, "positive_lexemes": ["black"], "negative_lexemes": ["black"]}, {"tag": "replace", "positive_start": 4, "positive_end": 5, "negative_start": 5, "negative_end": 6, "positive_lexemes": ["hair"], "negative_lexemes": ["moustache"]}, {"tag": "equal", "positive_start": 5, "positive_end": 9, "negative_start": 6, "negative_end": 10, "positive_lexemes": ["and", "a", "top", "hat"], "negative_lexemes": ["and", "a", "top", "hat"]}]`
- 共同前缀：`["a", "man", "with"]`
- 正确 contrast hull：`["black", "hair"]`
- 错误 contrast hull：`["a", "black", "moustache"]`
- 共同后缀：`["and", "a", "top", "hat"]`
- Hull token 覆盖率（正/负/最大）：`[0.3333333333333333, 0.5, 0.5]`
- 共同前缀模型 token：`[100, 1672, 599]`
- 正确 hull 模型 token：IDs `[2597, 1637, 736, 639]`；text " black hair"
- 错误 hull 模型 token：IDs `[299, 2597, 1637, 351, 326, 432, 1545, 300]`；text " a black moustache"
- 第一轮/第二轮分类：`complex_edit` / `multi_block_local_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 6. `replace_object:1313`

- 负例类型/范围：`replace_object` / `{"canonical": true, "pilot": true, "formal": false, "certifying_formal": false}`
- 原始正描述 1："A display case in a bakery filled with donuts."
- 原始正描述 2："A bakery display case that is filled with donuts."
- 原始负描述："Shelves in a bakery filled with donuts."
- 规范化正描述 1："a display case in a bakery filled with donuts"
- 规范化正描述 2："a bakery display case that is filled with donuts"
- 规范化负描述："shelves in a bakery filled with donuts"
- 正描述 1 选择元组：`[4, 4, 2, 0.3333333333333333, 0.26666666666666666]`
- 正描述 2 选择元组：`[10, 10, 2, 0.6666666666666666, 0.4583333333333333]`
- 最终比较正描述：`positive_1` / "A display case in a bakery filled with donuts."
- 完整 lexeme 编辑块：`[{"tag": "delete", "positive_start": 0, "positive_end": 2, "negative_start": 0, "negative_end": 0, "positive_lexemes": ["a", "display"], "negative_lexemes": []}, {"tag": "replace", "positive_start": 2, "positive_end": 3, "negative_start": 0, "negative_end": 1, "positive_lexemes": ["case"], "negative_lexemes": ["shelves"]}, {"tag": "equal", "positive_start": 3, "positive_end": 9, "negative_start": 1, "negative_end": 7, "positive_lexemes": ["in", "a", "bakery", "filled", "with", "donuts"], "negative_lexemes": ["in", "a", "bakery", "filled", "with", "donuts"]}]`
- 共同前缀：`[]`
- 正确 contrast hull：`["a", "display", "case"]`
- 错误 contrast hull：`["shelves"]`
- 共同后缀：`["in", "a", "bakery", "filled", "with", "donuts"]`
- Hull token 覆盖率（正/负/最大）：`[0.26666666666666666, 0.21428571428571427, 0.26666666666666666]`
- 共同前缀模型 token：`[]`
- 正确 hull 模型 token：IDs `[100, 1981, 4838, 4017]`；text "a display case"
- 错误 hull 模型 token：IDs `[118, 4887, 3843]`；text "shelves"
- 第一轮/第二轮分类：`unique_alignment` / `multi_block_local_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 7. `replace_object:1340`

- 负例类型/范围：`replace_object` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A group of people are playing wii in the living room"
- 原始正描述 2："In the living room, a group of individuals are engaged in playing Wii."
- 原始负描述："A couple is playing wii in the living room."
- 规范化正描述 1："a group of people are playing wii in the living room"
- 规范化正描述 2："in the living room , a group of individuals are engaged in playing wii"
- 规范化负描述："a couple is playing wii in the living room"
- 正描述 1 选择元组：`[6, 6, 2, 0.36363636363636365, 0.25]`
- 正描述 2 选择元组：`[21, 23, 2, 0.9285714285714286, 0.7714285714285715]`
- 最终比较正描述：`positive_1` / "A group of people are playing wii in the living room"
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 1, "negative_start": 0, "negative_end": 1, "positive_lexemes": ["a"], "negative_lexemes": ["a"]}, {"tag": "delete", "positive_start": 1, "positive_end": 3, "negative_start": 1, "negative_end": 1, "positive_lexemes": ["group", "of"], "negative_lexemes": []}, {"tag": "replace", "positive_start": 3, "positive_end": 5, "negative_start": 1, "negative_end": 3, "positive_lexemes": ["people", "are"], "negative_lexemes": ["couple", "is"]}, {"tag": "equal", "positive_start": 5, "positive_end": 11, "negative_start": 3, "negative_end": 9, "positive_lexemes": ["playing", "wii", "in", "the", "living", "room"], "negative_lexemes": ["playing", "wii", "in", "the", "living", "room"]}]`
- 共同前缀：`["a"]`
- 正确 contrast hull：`["group", "of", "people", "are"]`
- 错误 contrast hull：`["couple", "is"]`
- 共同后缀：`["playing", "wii", "in", "the", "living", "room"]`
- Hull token 覆盖率（正/负/最大）：`[0.25, 0.25, 0.25]`
- 共同前缀模型 token：`[100]`
- 正确 hull 模型 token：IDs `[4592, 354, 2975, 732]`；text " group of people are"
- 错误 hull 模型 token：IDs `[317, 326, 833, 395]`；text " couple is"
- 第一轮/第二轮分类：`complex_edit` / `multi_block_local_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 8. `replace_object:1461`

- 负例类型/范围：`replace_object` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："People fill a park area under a cloudy sky while kites pepper the sky."
- 原始正描述 2："The cloudy sky is above the people who fill the park area while kites are scattered in the sky."
- 原始负描述："People fill a mall under a cloudy sky while kites pepper the sky."
- 规范化正描述 1："people fill a park area under a cloudy sky while kites pepper the sky"
- 规范化正描述 2："the cloudy sky is above the people who fill the park area while kites are scattered in the sky"
- 规范化负描述："people fill a mall under a cloudy sky while kites pepper the sky"
- 正描述 1 选择元组：`[3, 3, 2, 0.14285714285714285, 0.11594202898550725]`
- 正描述 2 选择元组：`[24, 28, 4, 0.7894736842105263, 0.6276595744680851]`
- 最终比较正描述：`positive_1` / "People fill a park area under a cloudy sky while kites pepper the sky."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 3, "negative_start": 0, "negative_end": 3, "positive_lexemes": ["people", "fill", "a"], "negative_lexemes": ["people", "fill", "a"]}, {"tag": "delete", "positive_start": 3, "positive_end": 4, "negative_start": 3, "negative_end": 3, "positive_lexemes": ["park"], "negative_lexemes": []}, {"tag": "replace", "positive_start": 4, "positive_end": 5, "negative_start": 3, "negative_end": 4, "positive_lexemes": ["area"], "negative_lexemes": ["mall"]}, {"tag": "equal", "positive_start": 5, "positive_end": 14, "negative_start": 4, "negative_end": 13, "positive_lexemes": ["under", "a", "cloudy", "sky", "while", "kites", "pepper", "the", "sky"], "negative_lexemes": ["under", "a", "cloudy", "sky", "while", "kites", "pepper", "the", "sky"]}]`
- 共同前缀：`["people", "fill", "a"]`
- 正确 contrast hull：`["park", "area"]`
- 错误 contrast hull：`["mall"]`
- 共同后缀：`["under", "a", "cloudy", "sky", "while", "kites", "pepper", "the", "sky"]`
- Hull token 覆盖率（正/负/最大）：`[0.14285714285714285, 0.1, 0.14285714285714285]`
- 共同前缀模型 token：`[653, 2643, 341, 959, 299]`
- 正确 hull 模型 token：IDs `[344, 2000, 2808]`；text " park area"
- 错误 hull 模型 token：IDs `[351, 1266]`；text " mall"
- 第一轮/第二轮分类：`unique_alignment` / `multi_block_local_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 9. `replace_object:277`

- 负例类型/范围：`replace_object` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A room with chair, bicycle, television and a Christmas tree."
- 原始正描述 2："A room contains one chair, a television, a bicycle, and a Christmas tree."
- 原始负描述："A room with chair, bicycle, television and a couch."
- 规范化正描述 1："a room with chair , bicycle , television and a christmas tree"
- 规范化正描述 2："a room contains one chair , a television , a bicycle , and a christmas tree"
- 规范化负描述："a room with chair , bicycle , television and a couch"
- 正描述 1 选择元组：`[3, 3, 2, 0.16666666666666666, 0.21311475409836064]`
- 正描述 2 选择元组：`[13, 23, 8, 0.5625, 0.6133333333333333]`
- 最终比较正描述：`positive_1` / "A room with chair, bicycle, television and a Christmas tree."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 10, "negative_start": 0, "negative_end": 10, "positive_lexemes": ["a", "room", "with", "chair", ",", "bicycle", ",", "television", "and", "a"], "negative_lexemes": ["a", "room", "with", "chair", ",", "bicycle", ",", "television", "and", "a"]}, {"tag": "delete", "positive_start": 10, "positive_end": 11, "negative_start": 10, "negative_end": 10, "positive_lexemes": ["christmas"], "negative_lexemes": []}, {"tag": "replace", "positive_start": 11, "positive_end": 12, "negative_start": 10, "negative_end": 11, "positive_lexemes": ["tree"], "negative_lexemes": ["couch"]}]`
- 共同前缀：`["a", "room", "with", "chair", ",", "bicycle", ",", "television", "and", "a"]`
- 正确 contrast hull：`["christmas", "tree"]`
- 错误 contrast hull：`["couch"]`
- 共同后缀：`[]`
- Hull token 覆盖率（正/负/最大）：`[0.25925925925925924, 0.13043478260869565, 0.25925925925925924]`
- 共同前缀模型 token：`[100, 1552, 444, 599, 890, 3709, 256, 47, 363, 375, 124, 2945, 256, 47, 1047, 361, 121, 5190, 376, 299]`
- 正确 hull 模型 token：IDs `[890, 117, 570, 112, 390, 297, 1382]`；text " christmas tree"
- 错误 hull 模型 token：IDs `[317, 326, 550]`；text " couch"
- 第一轮/第二轮分类：`unique_alignment` / `multi_block_local_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 10. `replace_object:516`

- 负例类型/范围：`replace_object` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A half zebra hybrid is standing in tall grass."
- 原始正描述 2："A hybrid animal with half zebra characteristics is standing within tall grass."
- 原始负描述："A peacock is standing in tall grass."
- 规范化正描述 1："a half zebra hybrid is standing in tall grass"
- 规范化正描述 2："a hybrid animal with half zebra characteristics is standing within tall grass"
- 规范化负描述："a peacock is standing in tall grass"
- 正描述 1 选择元组：`[4, 4, 2, 0.3333333333333333, 0.3333333333333333]`
- 正描述 2 选择元组：`[9, 13, 3, 0.5833333333333334, 0.5844155844155844]`
- 最终比较正描述：`positive_1` / "A half zebra hybrid is standing in tall grass."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 1, "negative_start": 0, "negative_end": 1, "positive_lexemes": ["a"], "negative_lexemes": ["a"]}, {"tag": "delete", "positive_start": 1, "positive_end": 3, "negative_start": 1, "negative_end": 1, "positive_lexemes": ["half", "zebra"], "negative_lexemes": []}, {"tag": "replace", "positive_start": 3, "positive_end": 4, "negative_start": 1, "negative_end": 2, "positive_lexemes": ["hybrid"], "negative_lexemes": ["peacock"]}, {"tag": "equal", "positive_start": 4, "positive_end": 9, "negative_start": 2, "negative_end": 7, "positive_lexemes": ["is", "standing", "in", "tall", "grass"], "negative_lexemes": ["is", "standing", "in", "tall", "grass"]}]`
- 共同前缀：`["a"]`
- 正确 contrast hull：`["half", "zebra", "hybrid"]`
- 错误 contrast hull：`["peacock"]`
- 共同后缀：`["is", "standing", "in", "tall", "grass"]`
- Hull token 覆盖率（正/负/最大）：`[0.5, 0.23076923076923078, 0.5]`
- 共同前缀模型 token：`[100]`
- 正确 hull 模型 token：IDs `[429, 352, 105, 3243, 3037, 559, 5548, 101, 117, 460]`；text " half zebra hybrid"
- 错误 hull 模型 token：IDs `[2188, 1545, 4469]`；text " peacock"
- 第一轮/第二轮分类：`unique_alignment` / `multi_block_local_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 11. `replace_object:903`

- 负例类型/范围：`replace_object` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："a woman swinging her tennis racket while playing tennis"
- 原始正描述 2："A woman is playing tennis and swinging her tennis racket."
- 原始负描述："A man swinging his tennis racket while playing tennis."
- 规范化正描述 1："a woman swinging her tennis racket while playing tennis"
- 规范化正描述 2："a woman is playing tennis and swinging her tennis racket"
- 规范化负描述："a man swinging his tennis racket while playing tennis"
- 正描述 1 选择元组：`[4, 6, 2, 0.2222222222222222, 0.07272727272727272]`
- 正描述 2 选择元组：`[13, 17, 3, 0.7, 0.6428571428571429]`
- 最终比较正描述：`positive_1` / "a woman swinging her tennis racket while playing tennis"
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 1, "negative_start": 0, "negative_end": 1, "positive_lexemes": ["a"], "negative_lexemes": ["a"]}, {"tag": "replace", "positive_start": 1, "positive_end": 2, "negative_start": 1, "negative_end": 2, "positive_lexemes": ["woman"], "negative_lexemes": ["man"]}, {"tag": "equal", "positive_start": 2, "positive_end": 3, "negative_start": 2, "negative_end": 3, "positive_lexemes": ["swinging"], "negative_lexemes": ["swinging"]}, {"tag": "replace", "positive_start": 3, "positive_end": 4, "negative_start": 3, "negative_end": 4, "positive_lexemes": ["her"], "negative_lexemes": ["his"]}, {"tag": "equal", "positive_start": 4, "positive_end": 9, "negative_start": 4, "negative_end": 9, "positive_lexemes": ["tennis", "racket", "while", "playing", "tennis"], "negative_lexemes": ["tennis", "racket", "while", "playing", "tennis"]}]`
- 共同前缀：`["a"]`
- 正确 contrast hull：`["woman", "swinging", "her"]`
- 错误 contrast hull：`["man", "swinging", "his"]`
- 共同后缀：`["tennis", "racket", "while", "playing", "tennis"]`
- Hull token 覆盖率（正/负/最大）：`[0.38095238095238093, 0.3157894736842105, 0.38095238095238093]`
- 共同前缀模型 token：`[100]`
- 正确 hull 模型 token：IDs `[339, 444, 325, 316, 122, 350, 350, 2833]`；text " woman swinging her"
- 错误 hull 模型 token：IDs `[1672, 316, 122, 350, 350, 2049]`；text " man swinging his"
- 第一轮/第二轮分类：`complex_edit` / `multi_block_local_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 12. `replace_object:999`

- 负例类型/范围：`replace_object` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A laptop computer and a desktop computer on a white desk"
- 原始正描述 2："The white desk has a laptop computer and a desktop computer positioned on it."
- 原始负描述："A tablet and a desktop computer on a white desk."
- 规范化正描述 1："a laptop computer and a desktop computer on a white desk"
- 规范化正描述 2："the white desk has a laptop computer and a desktop computer positioned on it"
- 规范化负描述："a tablet and a desktop computer on a white desk"
- 正描述 1 选择元组：`[3, 3, 2, 0.18181818181818182, 0.23214285714285715]`
- 正描述 2 选择元组：`[14, 24, 5, 0.7142857142857143, 0.6052631578947368]`
- 最终比较正描述：`positive_1` / "A laptop computer and a desktop computer on a white desk"
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 1, "negative_start": 0, "negative_end": 1, "positive_lexemes": ["a"], "negative_lexemes": ["a"]}, {"tag": "delete", "positive_start": 1, "positive_end": 2, "negative_start": 1, "negative_end": 1, "positive_lexemes": ["laptop"], "negative_lexemes": []}, {"tag": "replace", "positive_start": 2, "positive_end": 3, "negative_start": 1, "negative_end": 2, "positive_lexemes": ["computer"], "negative_lexemes": ["tablet"]}, {"tag": "equal", "positive_start": 3, "positive_end": 11, "negative_start": 2, "negative_end": 10, "positive_lexemes": ["and", "a", "desktop", "computer", "on", "a", "white", "desk"], "negative_lexemes": ["and", "a", "desktop", "computer", "on", "a", "white", "desk"]}]`
- 共同前缀：`["a"]`
- 正确 contrast hull：`["laptop", "computer"]`
- 错误 contrast hull：`["tablet"]`
- 共同后缀：`["and", "a", "desktop", "computer", "on", "a", "white", "desk"]`
- Hull token 覆盖率（正/负/最大）：`[0.2222222222222222, 0.125, 0.2222222222222222]`
- 共同前缀模型 token：`[100]`
- 正确 hull 模型 token：IDs `[3090, 875, 1506, 4818]`；text " laptop computer"
- 错误 hull 模型 token：IDs `[2630, 119]`；text " tablet"
- 第一轮/第二轮分类：`complex_edit` / `multi_block_local_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 13. `replace_relation:1072`

- 负例类型/范围：`replace_relation` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A stop sign sitting on a pole that is somewhat broken"
- 原始正描述 2："A stop sign is perched on a partially broken pole."
- 原始负描述："A stop sign sitting on a pole that is fixed."
- 规范化正描述 1："a stop sign sitting on a pole that is somewhat broken"
- 规范化正描述 2："a stop sign is perched on a partially broken pole"
- 规范化负描述："a stop sign sitting on a pole that is fixed"
- 正描述 1 选择元组：`[3, 3, 2, 0.18181818181818182, 0.2641509433962264]`
- 正描述 2 选择元组：`[10, 14, 4, 0.6, 0.5510204081632653]`
- 最终比较正描述：`positive_1` / "A stop sign sitting on a pole that is somewhat broken"
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 9, "negative_start": 0, "negative_end": 9, "positive_lexemes": ["a", "stop", "sign", "sitting", "on", "a", "pole", "that", "is"], "negative_lexemes": ["a", "stop", "sign", "sitting", "on", "a", "pole", "that", "is"]}, {"tag": "delete", "positive_start": 9, "positive_end": 10, "negative_start": 9, "negative_end": 9, "positive_lexemes": ["somewhat"], "negative_lexemes": []}, {"tag": "replace", "positive_start": 10, "positive_end": 11, "negative_start": 9, "negative_end": 10, "positive_lexemes": ["broken"], "negative_lexemes": ["fixed"]}]`
- 共同前缀：`["a", "stop", "sign", "sitting", "on", "a", "pole", "that", "is"]`
- 正确 contrast hull：`["somewhat", "broken"]`
- 错误 contrast hull：`["fixed"]`
- 共同后缀：`[]`
- Hull token 覆盖率（正/负/最大）：`[0.3333333333333333, 0.2, 0.3333333333333333]`
- 共同前缀模型 token：`[100, 580, 1506, 2185, 5305, 2912, 619, 299, 927, 361, 591, 395]`
- 正确 hull 模型 token：IDs `[2104, 4465, 314, 5108, 110, 327]`；text " somewhat broken"
- 错误 hull 模型 token：IDs `[341, 2628, 382]`；text " fixed"
- 第一轮/第二轮分类：`unique_alignment` / `multi_block_local_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 14. `replace_relation:1108`

- 负例类型/范围：`replace_relation` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A flock of white birds stands in a parking lot puddle."
- 原始正描述 2："A flock of white birds is positioned in a puddle within a parking lot."
- 原始负描述："A flock of white birds is flying above a parking lot puddle."
- 规范化正描述 1："a flock of white birds stands in a parking lot puddle"
- 规范化正描述 2："a flock of white birds is positioned in a puddle within a parking lot"
- 规范化负描述："a flock of white birds is flying above a parking lot puddle"
- 正描述 1 选择元组：`[5, 5, 2, 0.25, 0.22033898305084745]`
- 正描述 2 选择元组：`[8, 14, 3, 0.42857142857142855, 0.4492753623188406]`
- 最终比较正描述：`positive_1` / "A flock of white birds stands in a parking lot puddle."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 5, "negative_start": 0, "negative_end": 5, "positive_lexemes": ["a", "flock", "of", "white", "birds"], "negative_lexemes": ["a", "flock", "of", "white", "birds"]}, {"tag": "insert", "positive_start": 5, "positive_end": 5, "negative_start": 5, "negative_end": 6, "positive_lexemes": [], "negative_lexemes": ["is"]}, {"tag": "replace", "positive_start": 5, "positive_end": 7, "negative_start": 6, "negative_end": 8, "positive_lexemes": ["stands", "in"], "negative_lexemes": ["flying", "above"]}, {"tag": "equal", "positive_start": 7, "positive_end": 11, "negative_start": 8, "negative_end": 12, "positive_lexemes": ["a", "parking", "lot", "puddle"], "negative_lexemes": ["a", "parking", "lot", "puddle"]}]`
- 共同前缀：`["a", "flock", "of", "white", "birds"]`
- 正确 contrast hull：`["stands", "in"]`
- 错误 contrast hull：`["is", "flying", "above"]`
- 共同后缀：`["a", "parking", "lot", "puddle"]`
- Hull token 覆盖率（正/负/最大）：`[0.15, 0.22727272727272727, 0.22727272727272727]`
- 共同前缀模型 token：`[100, 5796, 892, 354, 654, 1078, 5231, 1881]`
- 正确 hull 模型 token：IDs `[2823, 118, 353]`；text " stands in"
- 错误 hull 模型 token：IDs `[395, 341, 542, 350, 6264]`；text " is flying above"
- 第一轮/第二轮分类：`unique_alignment` / `multi_block_local_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 15. `replace_relation:1112`

- 负例类型/范围：`replace_relation` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A little kid is swinging at a water balloon."
- 原始正描述 2："The child is swinging at a water balloon."
- 原始负描述："A little kid is throwing a water balloon."
- 规范化正描述 1："a little kid is swinging at a water balloon"
- 规范化正描述 2："the child is swinging at a water balloon"
- 规范化负描述："a little kid is throwing a water balloon"
- 正描述 1 选择元组：`[3, 3, 2, 0.2222222222222222, 0.18604651162790697]`
- 正描述 2 选择元组：`[10, 10, 1, 0.625, 0.425]`
- 最终比较正描述：`positive_1` / "A little kid is swinging at a water balloon."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 4, "negative_start": 0, "negative_end": 4, "positive_lexemes": ["a", "little", "kid", "is"], "negative_lexemes": ["a", "little", "kid", "is"]}, {"tag": "delete", "positive_start": 4, "positive_end": 5, "negative_start": 4, "negative_end": 4, "positive_lexemes": ["swinging"], "negative_lexemes": []}, {"tag": "replace", "positive_start": 5, "positive_end": 6, "negative_start": 4, "negative_end": 5, "positive_lexemes": ["at"], "negative_lexemes": ["throwing"]}, {"tag": "equal", "positive_start": 6, "positive_end": 9, "negative_start": 5, "negative_end": 8, "positive_lexemes": ["a", "water", "balloon"], "negative_lexemes": ["a", "water", "balloon"]}]`
- 共同前缀：`["a", "little", "kid", "is"]`
- 正确 contrast hull：`["swinging", "at"]`
- 错误 contrast hull：`["throwing"]`
- 共同后缀：`["a", "water", "balloon"]`
- Hull token 覆盖率（正/负/最大）：`[0.2777777777777778, 0.1875, 0.2777777777777778]`
- 共同前缀模型 token：`[100, 406, 338, 5395, 914, 460, 395]`
- 正确 hull 模型 token：IDs `[316, 122, 350, 350, 1248]`；text " swinging at"
- 错误 hull 模型 token：IDs `[445, 2079, 350]`；text " throwing"
- 第一轮/第二轮分类：`unique_alignment` / `multi_block_local_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 16. `replace_relation:1280`

- 负例类型/范围：`replace_relation` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A large and small giraffe are looking at something while standing next to a log."
- 原始正描述 2："While standing next to the log, the big and small giraffes are observing something."
- 原始负描述："A large and small giraffe are looking at something while lying on a log."
- 规范化正描述 1："a large and small giraffe are looking at something while standing next to a log"
- 规范化正描述 2："while standing next to the log , the big and small giraffes are observing something"
- 规范化负描述："a large and small giraffe are looking at something while lying on a log"
- 正描述 1 选择元组：`[5, 5, 2, 0.2, 0.1518987341772152]`
- 正描述 2 选择元组：`[29, 29, 2, 1.0, 0.7590361445783133]`
- 最终比较正描述：`positive_1` / "A large and small giraffe are looking at something while standing next to a log."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 10, "negative_start": 0, "negative_end": 10, "positive_lexemes": ["a", "large", "and", "small", "giraffe", "are", "looking", "at", "something", "while"], "negative_lexemes": ["a", "large", "and", "small", "giraffe", "are", "looking", "at", "something", "while"]}, {"tag": "delete", "positive_start": 10, "positive_end": 11, "negative_start": 10, "negative_end": 10, "positive_lexemes": ["standing"], "negative_lexemes": []}, {"tag": "replace", "positive_start": 11, "positive_end": 13, "negative_start": 10, "negative_end": 12, "positive_lexemes": ["next", "to"], "negative_lexemes": ["lying", "on"]}, {"tag": "equal", "positive_start": 13, "positive_end": 15, "negative_start": 12, "negative_end": 14, "positive_lexemes": ["a", "log"], "negative_lexemes": ["a", "log"]}]`
- 共同前缀：`["a", "large", "and", "small", "giraffe", "are", "looking", "at", "something", "while"]`
- 正确 contrast hull：`["standing", "next", "to"]`
- 错误 contrast hull：`["lying", "on"]`
- 共同后缀：`["a", "log"]`
- Hull token 覆盖率（正/负/最大）：`[0.2, 0.2, 0.2]`
- 共同前缀模型 token：`[100, 2994, 376, 3436, 492, 108, 559, 1627, 104, 732, 3125, 1248, 2798, 3052]`
- 正确 hull 模型 token：IDs `[2823, 350, 4658, 364]`；text " standing next to"
- 错误 hull 模型 token：IDs `[406, 124, 350, 619]`；text " lying on"
- 第一轮/第二轮分类：`unique_alignment` / `multi_block_local_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 17. `replace_relation:1281`

- 负例类型/范围：`replace_relation` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："An ornate clock on the side of a building next to a tree."
- 原始正描述 2："Next to a tree is a building with an ornate clock on the side."
- 原始负描述："An ornate clock inside a building next to a tree."
- 规范化正描述 1："an ornate clock on the side of a building next to a tree"
- 规范化正描述 2："next to a tree is a building with an ornate clock on the side"
- 规范化负描述："an ornate clock inside a building next to a tree"
- 正描述 1 选择元组：`[5, 5, 2, 0.3076923076923077, 0.16071428571428573]`
- 正描述 2 选择元组：`[20, 24, 4, 0.8571428571428571, 0.6557377049180327]`
- 最终比较正描述：`positive_1` / "An ornate clock on the side of a building next to a tree."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 3, "negative_start": 0, "negative_end": 3, "positive_lexemes": ["an", "ornate", "clock"], "negative_lexemes": ["an", "ornate", "clock"]}, {"tag": "delete", "positive_start": 3, "positive_end": 6, "negative_start": 3, "negative_end": 3, "positive_lexemes": ["on", "the", "side"], "negative_lexemes": []}, {"tag": "replace", "positive_start": 6, "positive_end": 7, "negative_start": 3, "negative_end": 4, "positive_lexemes": ["of"], "negative_lexemes": ["inside"]}, {"tag": "equal", "positive_start": 7, "positive_end": 13, "negative_start": 4, "negative_end": 10, "positive_lexemes": ["a", "building", "next", "to", "a", "tree"], "negative_lexemes": ["a", "building", "next", "to", "a", "tree"]}]`
- 共同前缀：`["an", "ornate", "clock"]`
- 正确 contrast hull：`["on", "the", "side", "of"]`
- 错误 contrast hull：`["inside"]`
- 共同后缀：`["a", "building", "next", "to", "a", "tree"]`
- Hull token 覆盖率（正/负/最大）：`[0.2222222222222222, 0.125, 0.2222222222222222]`
- 共同前缀模型 token：`[325, 522, 113, 557, 4414, 892]`
- 正确 hull 模型 token：IDs `[619, 309, 5046, 354]`；text " on the side of"
- 错误 hull 模型 token：IDs `[3470, 688]`；text " inside"
- 第一轮/第二轮分类：`unique_alignment` / `multi_block_local_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 18. `replace_relation:1328`

- 负例类型/范围：`replace_relation` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："An older person riding a train while sitting under it's window."
- 原始正描述 2："A train is being ridden by an older person sitting under its window."
- 原始负描述："An older person riding a train beside its window."
- 规范化正描述 1："an older person riding a train while sitting under it's window"
- 规范化正描述 2："a train is being ridden by an older person sitting under its window"
- 规范化负描述："an older person riding a train beside its window"
- 正描述 1 选择元组：`[6, 6, 2, 0.36363636363636365, 0.24193548387096775]`
- 正描述 2 选择元组：`[12, 18, 3, 0.7692307692307693, 0.582089552238806]`
- 最终比较正描述：`positive_1` / "An older person riding a train while sitting under it's window."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 6, "negative_start": 0, "negative_end": 6, "positive_lexemes": ["an", "older", "person", "riding", "a", "train"], "negative_lexemes": ["an", "older", "person", "riding", "a", "train"]}, {"tag": "delete", "positive_start": 6, "positive_end": 8, "negative_start": 6, "negative_end": 6, "positive_lexemes": ["while", "sitting"], "negative_lexemes": []}, {"tag": "replace", "positive_start": 8, "positive_end": 10, "negative_start": 6, "negative_end": 8, "positive_lexemes": ["under", "it's"], "negative_lexemes": ["beside", "its"]}, {"tag": "equal", "positive_start": 10, "positive_end": 11, "negative_start": 8, "negative_end": 9, "positive_lexemes": ["window"], "negative_lexemes": ["window"]}]`
- 共同前缀：`["an", "older", "person", "riding", "a", "train"]`
- 正确 contrast hull：`["while", "sitting", "under", "it's"]`
- 错误 contrast hull：`["beside", "its"]`
- 共同后缀：`["window"]`
- Hull token 覆盖率（正/负/最大）：`[0.3333333333333333, 0.25, 0.3333333333333333]`
- 共同前缀模型 token：`[325, 4797, 311, 2198, 757, 460, 350, 299, 1946, 301]`
- 正确 hull 模型 token：IDs `[3052, 5305, 2912, 1943, 563, 628]`；text " while sitting under it's"
- 错误 hull 模型 token：IDs `[363, 329, 688, 1342]`；text " beside its"
- 第一轮/第二轮分类：`unique_alignment` / `multi_block_local_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 19. `replace_relation:176`

- 负例类型/范围：`replace_relation` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A person in black shirt and skirt playing a game of tennis."
- 原始正描述 2："An individual wearing a black shirt and skirt plays a game of tennis."
- 原始负描述："A person in black shirt and skirt is watching a game of tennis."
- 规范化正描述 1："a person in black shirt and skirt playing a game of tennis"
- 规范化正描述 2："an individual wearing a black shirt and skirt plays a game of tennis"
- 规范化负描述："a person in black shirt and skirt is watching a game of tennis"
- 正描述 1 选择元组：`[3, 3, 2, 0.15384615384615385, 0.11290322580645161]`
- 正描述 2 选择元组：`[10, 18, 4, 0.46153846153846156, 0.4117647058823529]`
- 最终比较正描述：`positive_1` / "A person in black shirt and skirt playing a game of tennis."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 7, "negative_start": 0, "negative_end": 7, "positive_lexemes": ["a", "person", "in", "black", "shirt", "and", "skirt"], "negative_lexemes": ["a", "person", "in", "black", "shirt", "and", "skirt"]}, {"tag": "insert", "positive_start": 7, "positive_end": 7, "negative_start": 7, "negative_end": 8, "positive_lexemes": [], "negative_lexemes": ["is"]}, {"tag": "replace", "positive_start": 7, "positive_end": 8, "negative_start": 8, "negative_end": 9, "positive_lexemes": ["playing"], "negative_lexemes": ["watching"]}, {"tag": "equal", "positive_start": 8, "positive_end": 12, "negative_start": 9, "negative_end": 13, "positive_lexemes": ["a", "game", "of", "tennis"], "negative_lexemes": ["a", "game", "of", "tennis"]}]`
- 共同前缀：`["a", "person", "in", "black", "shirt", "and", "skirt"]`
- 正确 contrast hull：`["playing"]`
- 错误 contrast hull：`["is", "watching"]`
- 共同后缀：`["a", "game", "of", "tennis"]`
- Hull token 覆盖率（正/负/最大）：`[0.1111111111111111, 0.2, 0.2]`
- 共同前缀模型 token：`[100, 2198, 353, 2597, 1637, 1128, 4193, 376, 2549, 4193]`
- 正确 hull 模型 token：IDs `[2865, 350]`；text " playing"
- 错误 hull 模型 token：IDs `[395, 339, 6131, 350]`；text " is watching"
- 第一轮/第二轮分类：`unique_alignment` / `multi_block_local_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 20. `replace_relation:449`

- 负例类型/范围：`replace_relation` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："a tall clock tower with bushes and trees in the foreground"
- 原始正描述 2："The tall clock tower is positioned in the background, with bushes and trees in the foreground."
- 原始负描述："A tall clock tower with bushes and trees behind it."
- 规范化正描述 1："a tall clock tower with bushes and trees in the foreground"
- 规范化正描述 2："the tall clock tower is positioned in the background , with bushes and trees in the foreground"
- 规范化负描述："a tall clock tower with bushes and trees behind it"
- 正描述 1 选择元组：`[5, 5, 2, 0.2727272727272727, 0.27586206896551724]`
- 正描述 2 选择元组：`[13, 27, 4, 0.5882352941176471, 0.5638297872340425]`
- 最终比较正描述：`positive_1` / "a tall clock tower with bushes and trees in the foreground"
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 8, "negative_start": 0, "negative_end": 8, "positive_lexemes": ["a", "tall", "clock", "tower", "with", "bushes", "and", "trees"], "negative_lexemes": ["a", "tall", "clock", "tower", "with", "bushes", "and", "trees"]}, {"tag": "delete", "positive_start": 8, "positive_end": 9, "negative_start": 8, "negative_end": 8, "positive_lexemes": ["in"], "negative_lexemes": []}, {"tag": "replace", "positive_start": 9, "positive_end": 11, "negative_start": 8, "negative_end": 10, "positive_lexemes": ["the", "foreground"], "negative_lexemes": ["behind", "it"]}]`
- 共同前缀：`["a", "tall", "clock", "tower", "with", "bushes", "and", "trees"]`
- 正确 contrast hull：`["in", "the", "foreground"]`
- 错误 contrast hull：`["behind", "it"]`
- 共同后缀：`[]`
- Hull token 覆盖率（正/负/最大）：`[0.2631578947368421, 0.17647058823529413, 0.2631578947368421]`
- 共同前缀模型 token：`[100, 297, 1266, 4414, 892, 364, 122, 311, 599, 2499, 2470, 376, 4191, 329]`
- 正确 hull 模型 token：IDs `[353, 309, 4676, 106, 2383]`；text " in the foreground"
- 错误 hull 模型 token：IDs `[5237, 916, 563]`；text " behind it"
- 第一轮/第二轮分类：`complex_edit` / `multi_block_local_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 21. `replace_relation:527`

- 负例类型/范围：`replace_relation` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："Two zebra having a fight on top of a dry grass field."
- 原始正描述 2："Two zebras fight on top of a dry grassy field."
- 原始负描述："Two zebra having a fight beside a dry grass field."
- 规范化正描述 1："two zebra having a fight on top of a dry grass field"
- 规范化正描述 2："two zebras fight on top of a dry grassy field"
- 规范化负描述："two zebra having a fight beside a dry grass field"
- 正描述 1 选择元组：`[4, 4, 2, 0.25, 0.17307692307692307]`
- 正描述 2 选择元组：`[12, 16, 2, 0.6, 0.3877551020408163]`
- 最终比较正描述：`positive_1` / "Two zebra having a fight on top of a dry grass field."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 5, "negative_start": 0, "negative_end": 5, "positive_lexemes": ["two", "zebra", "having", "a", "fight"], "negative_lexemes": ["two", "zebra", "having", "a", "fight"]}, {"tag": "delete", "positive_start": 5, "positive_end": 7, "negative_start": 5, "negative_end": 5, "positive_lexemes": ["on", "top"], "negative_lexemes": []}, {"tag": "replace", "positive_start": 7, "positive_end": 8, "negative_start": 5, "negative_end": 6, "positive_lexemes": ["of"], "negative_lexemes": ["beside"]}, {"tag": "equal", "positive_start": 8, "positive_end": 12, "negative_start": 6, "negative_end": 10, "positive_lexemes": ["a", "dry", "grass", "field"], "negative_lexemes": ["a", "dry", "grass", "field"]}]`
- 共同前缀：`["two", "zebra", "having", "a", "fight"]`
- 正确 contrast hull：`["on", "top", "of"]`
- 错误 contrast hull：`["beside"]`
- 共同后缀：`["a", "dry", "grass", "field"]`
- Hull token 覆盖率（正/负/最大）：`[0.14285714285714285, 0.14285714285714285, 0.14285714285714285]`
- 共同前缀模型 token：`[119, 122, 114, 3243, 3037, 559, 736, 2828, 299, 341, 774]`
- 正确 hull 模型 token：IDs `[619, 2924, 354]`；text " on top of"
- 错误 hull 模型 token：IDs `[363, 329, 688]`；text " beside"
- 第一轮/第二轮分类：`unique_alignment` / `multi_block_local_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 22. `replace_relation:678`

- 负例类型/范围：`replace_relation` / `{"canonical": true, "pilot": true, "formal": false, "certifying_formal": false}`
- 原始正描述 1："A smiling pair of skiers with a huge snow covered mountain behind them."
- 原始正描述 2："A massive snow-covered mountain as the background of a grinning pair of skiers."
- 原始负描述："A smiling pair of skiers with a huge snow covered mountain in front of them."
- 规范化正描述 1："a smiling pair of skiers with a huge snow covered mountain behind them"
- 规范化正描述 2："a massive snow-covered mountain as the background of a grinning pair of skiers"
- 规范化负描述："a smiling pair of skiers with a huge snow covered mountain in front of them"
- 正描述 1 选择元组：`[4, 4, 2, 0.2, 0.13333333333333333]`
- 正描述 2 选择元组：`[24, 26, 3, 0.8666666666666667, 0.7435897435897436]`
- 最终比较正描述：`positive_1` / "A smiling pair of skiers with a huge snow covered mountain behind them."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 11, "negative_start": 0, "negative_end": 11, "positive_lexemes": ["a", "smiling", "pair", "of", "skiers", "with", "a", "huge", "snow", "covered", "mountain"], "negative_lexemes": ["a", "smiling", "pair", "of", "skiers", "with", "a", "huge", "snow", "covered", "mountain"]}, {"tag": "insert", "positive_start": 11, "positive_end": 11, "negative_start": 11, "negative_end": 13, "positive_lexemes": [], "negative_lexemes": ["in", "front"]}, {"tag": "replace", "positive_start": 11, "positive_end": 12, "negative_start": 13, "negative_end": 14, "positive_lexemes": ["behind"], "negative_lexemes": ["of"]}, {"tag": "equal", "positive_start": 12, "positive_end": 13, "negative_start": 14, "negative_end": 15, "positive_lexemes": ["them"], "negative_lexemes": ["them"]}]`
- 共同前缀：`["a", "smiling", "pair", "of", "skiers", "with", "a", "huge", "snow", "covered", "mountain"]`
- 正确 contrast hull：`["behind"]`
- 错误 contrast hull：`["in", "front", "of"]`
- 共同后缀：`["them"]`
- Hull token 覆盖率（正/负/最大）：`[0.08333333333333333, 0.18518518518518517, 0.18518518518518517]`
- 共同前缀模型 token：`[100, 2589, 485, 350, 344, 3709, 354, 2549, 108, 496, 599, 299, 429, 120, 583, 316, 1103, 966, 478, 1837, 5083]`
- 正确 hull 模型 token：IDs `[5237, 916]`；text " behind"
- 错误 hull 模型 token：IDs `[353, 341, 117, 3856, 354]`；text " in front of"
- 第一轮/第二轮分类：`unique_alignment` / `multi_block_local_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 23. `replace_relation:723`

- 负例类型/范围：`replace_relation` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": false}`
- 原始正描述 1："A red Dodge truck is parked near another Dodge."
- 原始正描述 2："Another Dodge is parked close to a red Dodge."
- 原始负描述："A red Dodge truck is driving away from another Dodge."
- 规范化正描述 1："a red dodge truck is parked near another dodge"
- 规范化正描述 2："another dodge is parked close to a red dodge"
- 规范化负描述："a red dodge truck is driving away from another dodge"
- 正描述 1 选择元组：`[5, 5, 2, 0.3, 0.2692307692307692]`
- 正描述 2 选择元组：`[15, 17, 3, 0.8, 0.5961538461538461]`
- 最终比较正描述：`positive_1` / "A red Dodge truck is parked near another Dodge."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 5, "negative_start": 0, "negative_end": 5, "positive_lexemes": ["a", "red", "dodge", "truck", "is"], "negative_lexemes": ["a", "red", "dodge", "truck", "is"]}, {"tag": "insert", "positive_start": 5, "positive_end": 5, "negative_start": 5, "negative_end": 6, "positive_lexemes": [], "negative_lexemes": ["driving"]}, {"tag": "replace", "positive_start": 5, "positive_end": 7, "negative_start": 6, "negative_end": 8, "positive_lexemes": ["parked", "near"], "negative_lexemes": ["away", "from"]}, {"tag": "equal", "positive_start": 7, "positive_end": 9, "negative_start": 8, "negative_end": 10, "positive_lexemes": ["another", "dodge"], "negative_lexemes": ["another", "dodge"]}]`
- 共同前缀：`["a", "red", "dodge", "truck", "is"]`
- 正确 contrast hull：`["parked", "near"]`
- 错误 contrast hull：`["driving", "away", "from"]`
- 共同后缀：`["another", "dodge"]`
- Hull token 覆盖率（正/负/最大）：`[0.2777777777777778, 0.2777777777777778, 0.2777777777777778]`
- 共同前缀模型 token：`[100, 5534, 1041, 103, 583, 1144, 120, 892, 395]`
- 正确 hull 模型 token：IDs `[344, 2000, 382, 730, 370]`；text " parked near"
- 错误 hull 模型 token：IDs `[5893, 4917, 299, 5054, 961]`；text " driving away from"
- 第一轮/第二轮分类：`unique_alignment` / `multi_block_local_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 24. `replace_relation:766`

- 负例类型/范围：`replace_relation` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A person in a yellow shirt is about to catch a white frisbee."
- 原始正描述 2："A white frisbee is about to be caught by a person in a yellow shirt."
- 原始负描述："A person not with a yellow shirt is about to catch a white frisbee."
- 规范化正描述 1："a person in a yellow shirt is about to catch a white frisbee"
- 规范化正描述 2："a white frisbee is about to be caught by a person in a yellow shirt"
- 规范化负描述："a person not with a yellow shirt is about to catch a white frisbee"
- 正描述 1 选择元组：`[3, 3, 2, 0.14285714285714285, 0.10606060606060606]`
- 正描述 2 选择元组：`[25, 27, 3, 0.8666666666666667, 0.8208955223880597]`
- 最终比较正描述：`positive_1` / "A person in a yellow shirt is about to catch a white frisbee."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 2, "negative_start": 0, "negative_end": 2, "positive_lexemes": ["a", "person"], "negative_lexemes": ["a", "person"]}, {"tag": "insert", "positive_start": 2, "positive_end": 2, "negative_start": 2, "negative_end": 3, "positive_lexemes": [], "negative_lexemes": ["not"]}, {"tag": "replace", "positive_start": 2, "positive_end": 3, "negative_start": 3, "negative_end": 4, "positive_lexemes": ["in"], "negative_lexemes": ["with"]}, {"tag": "equal", "positive_start": 3, "positive_end": 13, "negative_start": 4, "negative_end": 14, "positive_lexemes": ["a", "yellow", "shirt", "is", "about", "to", "catch", "a", "white", "frisbee"], "negative_lexemes": ["a", "yellow", "shirt", "is", "about", "to", "catch", "a", "white", "frisbee"]}]`
- 共同前缀：`["a", "person"]`
- 正确 contrast hull：`["in"]`
- 错误 contrast hull：`["not", "with"]`
- 共同后缀：`["a", "yellow", "shirt", "is", "about", "to", "catch", "a", "white", "frisbee"]`
- Hull token 覆盖率（正/负/最大）：`[0.045454545454545456, 0.08695652173913043, 0.08695652173913043]`
- 共同前缀模型 token：`[100, 2198]`
- 正确 hull 模型 token：IDs `[353]`；text " in"
- 错误 hull 模型 token：IDs `[1027, 599]`；text " not with"
- 第一轮/第二轮分类：`unique_alignment` / `multi_block_local_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 25. `replace_relation:844`

- 负例类型/范围：`replace_relation` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："Red flowers sitting in a vase with a red wall behind them."
- 原始正描述 2："A vase holds red flowers with a red wall in the background."
- 原始负描述："Red flowers sitting in a vase beside a red wall."
- 规范化正描述 1："red flowers sitting in a vase with a red wall behind them"
- 规范化正描述 2："a vase holds red flowers with a red wall in the background"
- 规范化负描述："red flowers sitting in a vase beside a red wall"
- 正描述 1 选择元组：`[4, 10, 2, 0.25, 0.2982456140350877]`
- 正描述 2 选择元组：`[16, 22, 4, 0.8333333333333334, 0.6896551724137931]`
- 最终比较正描述：`positive_1` / "Red flowers sitting in a vase with a red wall behind them."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 6, "negative_start": 0, "negative_end": 6, "positive_lexemes": ["red", "flowers", "sitting", "in", "a", "vase"], "negative_lexemes": ["red", "flowers", "sitting", "in", "a", "vase"]}, {"tag": "replace", "positive_start": 6, "positive_end": 7, "negative_start": 6, "negative_end": 7, "positive_lexemes": ["with"], "negative_lexemes": ["beside"]}, {"tag": "equal", "positive_start": 7, "positive_end": 10, "negative_start": 7, "negative_end": 10, "positive_lexemes": ["a", "red", "wall"], "negative_lexemes": ["a", "red", "wall"]}, {"tag": "delete", "positive_start": 10, "positive_end": 12, "negative_start": 10, "negative_end": 10, "positive_lexemes": ["behind", "them"], "negative_lexemes": []}]`
- 共同前缀：`["red", "flowers", "sitting", "in", "a", "vase"]`
- 正确 contrast hull：`["with", "a", "red", "wall", "behind", "them"]`
- 错误 contrast hull：`["beside", "a", "red", "wall"]`
- 共同后缀：`[]`
- Hull token 覆盖率（正/负/最大）：`[0.47058823529411764, 0.4375, 0.47058823529411764]`
- 共同前缀模型 token：`[1837, 5652, 496, 5305, 2912, 353, 299, 603, 812]`
- 正确 hull 模型 token：IDs `[599, 299, 5534, 339, 1266, 5237, 916, 2105]`；text " with a red wall behind them"
- 错误 hull 模型 token：IDs `[363, 329, 688, 299, 5534, 339, 1266]`；text " beside a red wall"
- 第一轮/第二轮分类：`complex_edit` / `multi_block_local_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 26. `swap_atribute:210`

- 负例类型/范围：`swap_atribute` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："Landing strip with two planes, several people and an SUV."
- 原始正描述 2："Two planes, several people, and an SUV are located on a landing strip"
- 原始负描述："Landing strip with several planes, two people and an SUV."
- 规范化正描述 1："landing strip with two planes , several people and an suv"
- 规范化正描述 2："two planes , several people , and an suv are located on a landing strip"
- 规范化负描述："landing strip with several planes , two people and an suv"
- 正描述 1 选择元组：`[4, 8, 2, 0.18181818181818182, 0.24561403508771928]`
- 正描述 2 选择元组：`[14, 26, 5, 0.8, 0.7183098591549296]`
- 最终比较正描述：`positive_1` / "Landing strip with two planes, several people and an SUV."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 3, "negative_start": 0, "negative_end": 3, "positive_lexemes": ["landing", "strip", "with"], "negative_lexemes": ["landing", "strip", "with"]}, {"tag": "replace", "positive_start": 3, "positive_end": 4, "negative_start": 3, "negative_end": 4, "positive_lexemes": ["two"], "negative_lexemes": ["several"]}, {"tag": "equal", "positive_start": 4, "positive_end": 6, "negative_start": 4, "negative_end": 6, "positive_lexemes": ["planes", ","], "negative_lexemes": ["planes", ","]}, {"tag": "replace", "positive_start": 6, "positive_end": 7, "negative_start": 6, "negative_end": 7, "positive_lexemes": ["several"], "negative_lexemes": ["two"]}, {"tag": "equal", "positive_start": 7, "positive_end": 11, "negative_start": 7, "negative_end": 11, "positive_lexemes": ["people", "and", "an", "suv"], "negative_lexemes": ["people", "and", "an", "suv"]}]`
- 共同前缀：`["landing", "strip", "with"]`
- 正确 contrast hull：`["two", "planes", ",", "several"]`
- 错误 contrast hull：`["several", "planes", ",", "two"]`
- 共同后缀：`["people", "and", "an", "suv"]`
- Hull token 覆盖率（正/负/最大）：`[0.35294117647058826, 0.35294117647058826, 0.35294117647058826]`
- 共同前缀模型 token：`[4882, 350, 580, 809, 115, 599]`
- 正确 hull 模型 token：IDs `[2102, 4140, 329, 256, 47, 4920]`；text " two planes , several"
- 错误 hull 模型 token：IDs `[4920, 4140, 329, 256, 47, 2102]`；text " several planes , two"
- 第一轮/第二轮分类：`complex_edit` / `multi_block_local_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 27. `swap_atribute:256`

- 负例类型/范围：`swap_atribute` / `{"canonical": true, "pilot": true, "formal": false, "certifying_formal": false}`
- 原始正描述 1："person in red shirt and black pants standing next to white flatbed truck cab next to a set of new tires."
- 原始正描述 2："The white flatbed truck cab is positioned next to the set of new tires, with the person in red shirt and black pants standing next to the truck cab."
- 原始负描述："person in white shirt and black pants standing next to red flatbed truck cab next to a set of new tires."
- 规范化正描述 1："person in red shirt and black pants standing next to white flatbed truck cab next to a set of new tires"
- 规范化正描述 2："the white flatbed truck cab is positioned next to the set of new tires , with the person in red shirt and black pants standing next to the truck cab"
- 规范化负描述："person in white shirt and black pants standing next to red flatbed truck cab next to a set of new tires"
- 正描述 1 选择元组：`[4, 18, 2, 0.09523809523809523, 0.0970873786407767]`
- 正描述 2 选择元组：`[43, 51, 5, 0.9, 0.7094594594594594]`
- 最终比较正描述：`positive_1` / "person in red shirt and black pants standing next to white flatbed truck cab next to a set of new tires."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 2, "negative_start": 0, "negative_end": 2, "positive_lexemes": ["person", "in"], "negative_lexemes": ["person", "in"]}, {"tag": "replace", "positive_start": 2, "positive_end": 3, "negative_start": 2, "negative_end": 3, "positive_lexemes": ["red"], "negative_lexemes": ["white"]}, {"tag": "equal", "positive_start": 3, "positive_end": 10, "negative_start": 3, "negative_end": 10, "positive_lexemes": ["shirt", "and", "black", "pants", "standing", "next", "to"], "negative_lexemes": ["shirt", "and", "black", "pants", "standing", "next", "to"]}, {"tag": "replace", "positive_start": 10, "positive_end": 11, "negative_start": 10, "negative_end": 11, "positive_lexemes": ["white"], "negative_lexemes": ["red"]}, {"tag": "equal", "positive_start": 11, "positive_end": 21, "negative_start": 11, "negative_end": 21, "positive_lexemes": ["flatbed", "truck", "cab", "next", "to", "a", "set", "of", "new", "tires"], "negative_lexemes": ["flatbed", "truck", "cab", "next", "to", "a", "set", "of", "new", "tires"]}]`
- 共同前缀：`["person", "in"]`
- 正确 contrast hull：`["red", "shirt", "and", "black", "pants", "standing", "next", "to", "white"]`
- 错误 contrast hull：`["white", "shirt", "and", "black", "pants", "standing", "next", "to", "red"]`
- 共同后缀：`["flatbed", "truck", "cab", "next", "to", "a", "set", "of", "new", "tires"]`
- Hull token 覆盖率（正/负/最大）：`[0.4, 0.4, 0.4]`
- 共同前缀模型 token：`[115, 2019, 353]`
- 正确 hull 模型 token：IDs `[5534, 1128, 4193, 376, 2597, 1637, 344, 5483, 2823, 350, 4658, 364, 654, 1078]`；text " red shirt and black pants standing next to white"
- 错误 hull 模型 token：IDs `[654, 1078, 1128, 4193, 376, 2597, 1637, 344, 5483, 2823, 350, 4658, 364, 5534]`；text " white shirt and black pants standing next to red"
- 第一轮/第二轮分类：`complex_edit` / `multi_block_local_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 28. `swap_atribute:44`

- 负例类型/范围：`swap_atribute` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A view of several billboards and two traffic signs on one pole."
- 原始正描述 2："An image of two traffic signs on a single pole along with several billboards."
- 原始负描述："A view of two billboards and several traffic signs on one pole."
- 规范化正描述 1："a view of several billboards and two traffic signs on one pole"
- 规范化正描述 2："an image of two traffic signs on a single pole along with several billboards"
- 规范化负描述："a view of two billboards and several traffic signs on one pole"
- 正描述 1 选择元组：`[4, 8, 2, 0.16666666666666666, 0.22580645161290322]`
- 正描述 2 选择元组：`[14, 26, 5, 0.7857142857142857, 0.7105263157894737]`
- 最终比较正描述：`positive_1` / "A view of several billboards and two traffic signs on one pole."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 3, "negative_start": 0, "negative_end": 3, "positive_lexemes": ["a", "view", "of"], "negative_lexemes": ["a", "view", "of"]}, {"tag": "replace", "positive_start": 3, "positive_end": 4, "negative_start": 3, "negative_end": 4, "positive_lexemes": ["several"], "negative_lexemes": ["two"]}, {"tag": "equal", "positive_start": 4, "positive_end": 6, "negative_start": 4, "negative_end": 6, "positive_lexemes": ["billboards", "and"], "negative_lexemes": ["billboards", "and"]}, {"tag": "replace", "positive_start": 6, "positive_end": 7, "negative_start": 6, "negative_end": 7, "positive_lexemes": ["two"], "negative_lexemes": ["several"]}, {"tag": "equal", "positive_start": 7, "positive_end": 12, "negative_start": 7, "negative_end": 12, "positive_lexemes": ["traffic", "signs", "on", "one", "pole"], "negative_lexemes": ["traffic", "signs", "on", "one", "pole"]}]`
- 共同前缀：`["a", "view", "of"]`
- 正确 contrast hull：`["several", "billboards", "and", "two"]`
- 错误 contrast hull：`["two", "billboards", "and", "several"]`
- 共同后缀：`["traffic", "signs", "on", "one", "pole"]`
- Hull token 覆盖率（正/负/最大）：`[0.4090909090909091, 0.4090909090909091, 0.4090909090909091]`
- 共同前缀模型 token：`[100, 603, 1400, 122, 354]`
- 正确 hull 模型 token：IDs `[4920, 363, 959, 101, 114, 1433, 118, 376, 2102]`；text " several billboards and two"
- 错误 hull 模型 token：IDs `[2102, 363, 959, 101, 114, 1433, 118, 376, 4920]`；text " two billboards and several"
- 第一轮/第二轮分类：`complex_edit` / `multi_block_local_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 29. `swap_atribute:610`

- 负例类型/范围：`swap_atribute` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A wooden table with miniature bananas next to a Malaysian coin from 2009."
- 原始正描述 2："A table made of wood with small bananas placed near a Malaysian coin from 2009."
- 原始负描述："A miniature table with wooden bananas next to a Malaysian coin from 2009."
- 规范化正描述 1："a wooden table with miniature bananas next to a malaysian coin from 2009"
- 规范化正描述 2："a table made of wood with small bananas placed near a malaysian coin from 2009"
- 规范化负描述："a miniature table with wooden bananas next to a malaysian coin from 2009"
- 正描述 1 选择元组：`[4, 8, 2, 0.15384615384615385, 0.25]`
- 正描述 2 选择元组：`[12, 16, 4, 0.4666666666666667, 0.41025641025641024]`
- 最终比较正描述：`positive_1` / "A wooden table with miniature bananas next to a Malaysian coin from 2009."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 1, "negative_start": 0, "negative_end": 1, "positive_lexemes": ["a"], "negative_lexemes": ["a"]}, {"tag": "replace", "positive_start": 1, "positive_end": 2, "negative_start": 1, "negative_end": 2, "positive_lexemes": ["wooden"], "negative_lexemes": ["miniature"]}, {"tag": "equal", "positive_start": 2, "positive_end": 4, "negative_start": 2, "negative_end": 4, "positive_lexemes": ["table", "with"], "negative_lexemes": ["table", "with"]}, {"tag": "replace", "positive_start": 4, "positive_end": 5, "negative_start": 4, "negative_end": 5, "positive_lexemes": ["miniature"], "negative_lexemes": ["wooden"]}, {"tag": "equal", "positive_start": 5, "positive_end": 13, "negative_start": 5, "negative_end": 13, "positive_lexemes": ["bananas", "next", "to", "a", "malaysian", "coin", "from", "2009"], "negative_lexemes": ["bananas", "next", "to", "a", "malaysian", "coin", "from", "2009"]}]`
- 共同前缀：`["a"]`
- 正确 contrast hull：`["wooden", "table", "with", "miniature"]`
- 错误 contrast hull：`["miniature", "table", "with", "wooden"]`
- 共同后缀：`["bananas", "next", "to", "a", "malaysian", "coin", "from", "2009"]`
- Hull token 覆盖率（正/负/最大）：`[0.32, 0.32, 0.32]`
- 共同前缀模型 token：`[100]`
- 正确 hull 模型 token：IDs `[339, 2166, 327, 2630, 599, 2995, 108, 1732]`；text " wooden table with miniature"
- 错误 hull 模型 token：IDs `[2995, 108, 1732, 2630, 599, 339, 2166, 327]`；text " miniature table with wooden"
- 第一轮/第二轮分类：`complex_edit` / `multi_block_local_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 30. `swap_object:67`

- 负例类型/范围：`swap_object` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："Crackers coated with spread, sitting on a plate, ready to eat."
- 原始正描述 2："Crackers positioned on a plate are coated with spread and are ready to be consumed."
- 原始负描述："Spread coated with crackers, sitting on a plate, ready to eat."
- 规范化正描述 1："crackers coated with spread , sitting on a plate , ready to eat"
- 规范化正描述 2："crackers positioned on a plate are coated with spread and are ready to be consumed"
- 规范化负描述："spread coated with crackers , sitting on a plate , ready to eat"
- 正描述 1 选择元组：`[4, 8, 2, 0.15384615384615385, 0.2222222222222222]`
- 正描述 2 选择元组：`[24, 28, 4, 0.8666666666666667, 0.6707317073170732]`
- 最终比较正描述：`positive_1` / "Crackers coated with spread, sitting on a plate, ready to eat."
- 完整 lexeme 编辑块：`[{"tag": "replace", "positive_start": 0, "positive_end": 1, "negative_start": 0, "negative_end": 1, "positive_lexemes": ["crackers"], "negative_lexemes": ["spread"]}, {"tag": "equal", "positive_start": 1, "positive_end": 3, "negative_start": 1, "negative_end": 3, "positive_lexemes": ["coated", "with"], "negative_lexemes": ["coated", "with"]}, {"tag": "replace", "positive_start": 3, "positive_end": 4, "negative_start": 3, "negative_end": 4, "positive_lexemes": ["spread"], "negative_lexemes": ["crackers"]}, {"tag": "equal", "positive_start": 4, "positive_end": 13, "negative_start": 4, "negative_end": 13, "positive_lexemes": [",", "sitting", "on", "a", "plate", ",", "ready", "to", "eat"], "negative_lexemes": [",", "sitting", "on", "a", "plate", ",", "ready", "to", "eat"]}]`
- 共同前缀：`[]`
- 正确 contrast hull：`["crackers", "coated", "with", "spread"]`
- 错误 contrast hull：`["spread", "coated", "with", "crackers"]`
- 共同后缀：`[",", "sitting", "on", "a", "plate", ",", "ready", "to", "eat"]`
- Hull token 覆盖率（正/负/最大）：`[0.375, 0.4, 0.4]`
- 共同前缀模型 token：`[]`
- 正确 hull 模型 token：IDs `[102, 559, 892, 496, 966, 1095, 599, 1772, 3489]`；text "crackers coated with spread"
- 错误 hull 模型 token：IDs `[118, 115, 3489, 966, 1095, 599, 317, 559, 892, 496]`；text "spread coated with crackers"
- 第一轮/第二轮分类：`complex_edit` / `multi_block_local_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

## 三块及以上编辑

候选 `633` 条，本节抽取 `30` 条。

### 1. `replace_attribute:38`

- 负例类型/范围：`replace_attribute` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A wall with several different clocks hanging from it with a mirror next to them."
- 原始正描述 2："A mirror is positioned next to several different clocks hanging from a wall."
- 原始负描述："A wall with a single different clock hanging from it with a mirror next to it."
- 规范化正描述 1："a wall with several different clocks hanging from it with a mirror next to them"
- 规范化正描述 2："a mirror is positioned next to several different clocks hanging from a wall"
- 规范化负描述："a wall with a single different clock hanging from it with a mirror next to it"
- 正描述 1 选择元组：`[7, 25, 4, 0.25, 0.1518987341772152]`
- 正描述 2 选择元组：`[19, 27, 6, 0.8125, 0.7142857142857143]`
- 最终比较正描述：`positive_1` / "A wall with several different clocks hanging from it with a mirror next to them."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 3, "negative_start": 0, "negative_end": 3, "positive_lexemes": ["a", "wall", "with"], "negative_lexemes": ["a", "wall", "with"]}, {"tag": "insert", "positive_start": 3, "positive_end": 3, "negative_start": 3, "negative_end": 4, "positive_lexemes": [], "negative_lexemes": ["a"]}, {"tag": "replace", "positive_start": 3, "positive_end": 4, "negative_start": 4, "negative_end": 5, "positive_lexemes": ["several"], "negative_lexemes": ["single"]}, {"tag": "equal", "positive_start": 4, "positive_end": 5, "negative_start": 5, "negative_end": 6, "positive_lexemes": ["different"], "negative_lexemes": ["different"]}, {"tag": "replace", "positive_start": 5, "positive_end": 6, "negative_start": 6, "negative_end": 7, "positive_lexemes": ["clocks"], "negative_lexemes": ["clock"]}, {"tag": "equal", "positive_start": 6, "positive_end": 14, "negative_start": 7, "negative_end": 15, "positive_lexemes": ["hanging", "from", "it", "with", "a", "mirror", "next", "to"], "negative_lexemes": ["hanging", "from", "it", "with", "a", "mirror", "next", "to"]}, {"tag": "replace", "positive_start": 14, "positive_end": 15, "negative_start": 15, "negative_end": 16, "positive_lexemes": ["them"], "negative_lexemes": ["it"]}]`
- 共同前缀：`["a", "wall", "with"]`
- 正确 contrast hull：`["several", "different", "clocks", "hanging", "from", "it", "with", "a", "mirror", "next", "to", "them"]`
- 错误 contrast hull：`["a", "single", "different", "clock", "hanging", "from", "it", "with", "a", "mirror", "next", "to", "it"]`
- 共同后缀：`[]`
- Hull token 覆盖率（正/负/最大）：`[0.8181818181818182, 0.8181818181818182, 0.8181818181818182]`
- 共同前缀模型 token：`[100, 339, 1266, 599]`
- 正确 hull 模型 token：IDs `[4920, 2301, 4414, 892, 118, 429, 942, 350, 961, 563, 599, 299, 351, 639, 3618, 4658, 364, 2105]`；text " several different clocks hanging from it with a mirror next to them"
- 错误 hull 模型 token：IDs `[299, 4486, 2301, 4414, 892, 429, 942, 350, 961, 563, 599, 299, 351, 639, 3618, 4658, 364, 563]`；text " a single different clock hanging from it with a mirror next to it"
- 第一轮/第二轮分类：`complex_edit` / `large_contrast_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；"maximum_hull_token_coverage_above_75_percent"

### 2. `replace_attribute:493`

- 负例类型/范围：`replace_attribute` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A bathroom is very colorful with blue yellow and red."
- 原始正描述 2："The bathroom is adorned with a vibrant color palette featuring yellow, blue, and red."
- 原始负描述："A bathroom is very drab with blue, yellow, and red."
- 规范化正描述 1："a bathroom is very colorful with blue yellow and red"
- 规范化正描述 2："the bathroom is adorned with a vibrant color palette featuring yellow , blue , and red"
- 规范化负描述："a bathroom is very drab with blue , yellow , and red"
- 正描述 1 选择元组：`[4, 10, 3, 0.25, 0.21153846153846154]`
- 正描述 2 选择元组：`[16, 22, 4, 0.625, 0.5465116279069767]`
- 最终比较正描述：`positive_1` / "A bathroom is very colorful with blue yellow and red."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 4, "negative_start": 0, "negative_end": 4, "positive_lexemes": ["a", "bathroom", "is", "very"], "negative_lexemes": ["a", "bathroom", "is", "very"]}, {"tag": "replace", "positive_start": 4, "positive_end": 5, "negative_start": 4, "negative_end": 5, "positive_lexemes": ["colorful"], "negative_lexemes": ["drab"]}, {"tag": "equal", "positive_start": 5, "positive_end": 7, "negative_start": 5, "negative_end": 7, "positive_lexemes": ["with", "blue"], "negative_lexemes": ["with", "blue"]}, {"tag": "insert", "positive_start": 7, "positive_end": 7, "negative_start": 7, "negative_end": 8, "positive_lexemes": [], "negative_lexemes": [","]}, {"tag": "equal", "positive_start": 7, "positive_end": 8, "negative_start": 8, "negative_end": 9, "positive_lexemes": ["yellow"], "negative_lexemes": ["yellow"]}, {"tag": "insert", "positive_start": 8, "positive_end": 8, "negative_start": 9, "negative_end": 10, "positive_lexemes": [], "negative_lexemes": [","]}, {"tag": "equal", "positive_start": 8, "positive_end": 10, "negative_start": 10, "negative_end": 12, "positive_lexemes": ["and", "red"], "negative_lexemes": ["and", "red"]}]`
- 共同前缀：`["a", "bathroom", "is", "very"]`
- 正确 contrast hull：`["colorful", "with", "blue", "yellow"]`
- 错误 contrast hull：`["drab", "with", "blue", ",", "yellow", ","]`
- 共同后缀：`["and", "red"]`
- Hull token 覆盖率（正/负/最大）：`[0.4375, 0.5714285714285714, 0.5714285714285714]`
- 共同前缀模型 token：`[100, 363, 1831, 393, 444, 395, 4965]`
- 正确 hull 模型 token：IDs `[4987, 1930, 599, 4300, 385, 446, 1030]`；text " colorful with blue yellow"
- 错误 hull 模型 token：IDs `[373, 559, 101, 599, 4300, 256, 47, 385, 446, 1030, 256, 47]`；text " drab with blue , yellow ,"
- 第一轮/第二轮分类：`complex_edit` / `multi_block_local_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 3. `replace_attribute:724`

- 负例类型/范围：`replace_attribute` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A group of baseball players sit with their gear in the dugout."
- 原始正描述 2："The dugout contains a group of baseball players sitting in their gear."
- 原始负描述："A lonely baseball player sits with their gear in the dugout."
- 规范化正描述 1："a group of baseball players sit with their gear in the dugout"
- 规范化正描述 2："the dugout contains a group of baseball players sitting in their gear"
- 规范化负描述："a lonely baseball player sits with their gear in the dugout"
- 正描述 1 选择元组：`[7, 9, 3, 0.3333333333333333, 0.14754098360655737]`
- 正描述 2 选择元组：`[21, 23, 3, 0.9166666666666666, 0.6811594202898551]`
- 最终比较正描述：`positive_1` / "A group of baseball players sit with their gear in the dugout."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 1, "negative_start": 0, "negative_end": 1, "positive_lexemes": ["a"], "negative_lexemes": ["a"]}, {"tag": "delete", "positive_start": 1, "positive_end": 2, "negative_start": 1, "negative_end": 1, "positive_lexemes": ["group"], "negative_lexemes": []}, {"tag": "replace", "positive_start": 2, "positive_end": 3, "negative_start": 1, "negative_end": 2, "positive_lexemes": ["of"], "negative_lexemes": ["lonely"]}, {"tag": "equal", "positive_start": 3, "positive_end": 4, "negative_start": 2, "negative_end": 3, "positive_lexemes": ["baseball"], "negative_lexemes": ["baseball"]}, {"tag": "replace", "positive_start": 4, "positive_end": 6, "negative_start": 3, "negative_end": 5, "positive_lexemes": ["players", "sit"], "negative_lexemes": ["player", "sits"]}, {"tag": "equal", "positive_start": 6, "positive_end": 12, "negative_start": 5, "negative_end": 11, "positive_lexemes": ["with", "their", "gear", "in", "the", "dugout"], "negative_lexemes": ["with", "their", "gear", "in", "the", "dugout"]}]`
- 共同前缀：`["a"]`
- 正确 contrast hull：`["group", "of", "baseball", "players", "sit"]`
- 错误 contrast hull：`["lonely", "baseball", "player", "sits"]`
- 共同后缀：`["with", "their", "gear", "in", "the", "dugout"]`
- Hull token 覆盖率（正/负/最大）：`[0.4444444444444444, 0.5, 0.5]`
- 共同前缀模型 token：`[100]`
- 正确 hull 模型 token：IDs `[4592, 354, 4933, 101, 1266, 2865, 496, 5305]`；text " group of baseball players sit"
- 错误 hull 模型 token：IDs `[406, 310, 1490, 4933, 101, 1266, 2865, 311, 316, 2163]`；text " lonely baseball player sits"
- 第一轮/第二轮分类：`complex_edit` / `multi_block_local_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 4. `replace_object:1211`

- 负例类型/范围：`replace_object` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："two people playing video game while standing one in purple is smiling"
- 原始正描述 2："Two individuals are standing and playing a video game, with one wearing a purple outfit and smiling."
- 原始负描述："Two people playing basketball while standing, one in purple is smiling."
- 规范化正描述 1："two people playing video game while standing one in purple is smiling"
- 规范化正描述 2："two individuals are standing and playing a video game , with one wearing a purple outfit and smiling"
- 规范化负描述："two people playing basketball while standing , one in purple is smiling"
- 正描述 1 选择元组：`[4, 8, 3, 0.25, 0.15492957746478872]`
- 正描述 2 选择元组：`[18, 26, 8, 0.6666666666666666, 0.59]`
- 最终比较正描述：`positive_1` / "two people playing video game while standing one in purple is smiling"
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 3, "negative_start": 0, "negative_end": 3, "positive_lexemes": ["two", "people", "playing"], "negative_lexemes": ["two", "people", "playing"]}, {"tag": "delete", "positive_start": 3, "positive_end": 4, "negative_start": 3, "negative_end": 3, "positive_lexemes": ["video"], "negative_lexemes": []}, {"tag": "replace", "positive_start": 4, "positive_end": 5, "negative_start": 3, "negative_end": 4, "positive_lexemes": ["game"], "negative_lexemes": ["basketball"]}, {"tag": "equal", "positive_start": 5, "positive_end": 7, "negative_start": 4, "negative_end": 6, "positive_lexemes": ["while", "standing"], "negative_lexemes": ["while", "standing"]}, {"tag": "insert", "positive_start": 7, "positive_end": 7, "negative_start": 6, "negative_end": 7, "positive_lexemes": [], "negative_lexemes": [","]}, {"tag": "equal", "positive_start": 7, "positive_end": 12, "negative_start": 7, "negative_end": 12, "positive_lexemes": ["one", "in", "purple", "is", "smiling"], "negative_lexemes": ["one", "in", "purple", "is", "smiling"]}]`
- 共同前缀：`["two", "people", "playing"]`
- 正确 contrast hull：`["video", "game", "while", "standing"]`
- 错误 contrast hull：`["basketball", "while", "standing", ","]`
- 共同后缀：`["one", "in", "purple", "is", "smiling"]`
- Hull token 覆盖率（正/负/最大）：`[0.3333333333333333, 0.4166666666666667, 0.4166666666666667]`
- 共同前缀模型 token：`[119, 122, 114, 2975, 2865, 350]`
- 正确 hull 模型 token：IDs `[603, 688, 114, 4428, 3052, 2823, 350]`；text " video game while standing"
- 错误 hull 模型 token：IDs `[5207, 110, 439, 101, 1266, 3052, 2823, 350, 256, 47]`；text " basketball while standing ,"
- 第一轮/第二轮分类：`complex_edit` / `multi_block_local_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 5. `replace_object:1260`

- 负例类型/范围：`replace_object` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："three yellow  bananas sitting inside of a basket"
- 原始正描述 2："Three bananas that are yellow in color are positioned in the basket."
- 原始负描述："Three yellow bananas sitting on a shelf."
- 规范化正描述 1："three yellow bananas sitting inside of a basket"
- 规范化正描述 2："three bananas that are yellow in color are positioned in the basket"
- 规范化负描述："three yellow bananas sitting on a shelf"
- 正描述 1 选择元组：`[5, 7, 3, 0.375, 0.2765957446808511]`
- 正描述 2 选择元组：`[15, 17, 3, 0.8333333333333334, 0.6417910447761194]`
- 最终比较正描述：`positive_1` / "three yellow  bananas sitting inside of a basket"
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 4, "negative_start": 0, "negative_end": 4, "positive_lexemes": ["three", "yellow", "bananas", "sitting"], "negative_lexemes": ["three", "yellow", "bananas", "sitting"]}, {"tag": "delete", "positive_start": 4, "positive_end": 5, "negative_start": 4, "negative_end": 4, "positive_lexemes": ["inside"], "negative_lexemes": []}, {"tag": "replace", "positive_start": 5, "positive_end": 6, "negative_start": 4, "negative_end": 5, "positive_lexemes": ["of"], "negative_lexemes": ["on"]}, {"tag": "equal", "positive_start": 6, "positive_end": 7, "negative_start": 5, "negative_end": 6, "positive_lexemes": ["a"], "negative_lexemes": ["a"]}, {"tag": "replace", "positive_start": 7, "positive_end": 8, "negative_start": 6, "negative_end": 7, "positive_lexemes": ["basket"], "negative_lexemes": ["shelf"]}]`
- 共同前缀：`["three", "yellow", "bananas", "sitting"]`
- 正确 contrast hull：`["inside", "of", "a", "basket"]`
- 错误 contrast hull：`["on", "a", "shelf"]`
- 共同后缀：`[]`
- Hull token 覆盖率（正/负/最大）：`[0.3888888888888889, 0.3125, 0.3888888888888889]`
- 共同前缀模型 token：`[495, 1382, 385, 446, 1030, 363, 325, 325, 390, 5305, 2912]`
- 正确 hull 模型 token：IDs `[3470, 688, 354, 299, 5207, 110, 439]`；text " inside of a basket"
- 错误 hull 模型 token：IDs `[619, 299, 3191, 111, 105]`；text " on a shelf"
- 第一轮/第二轮分类：`complex_edit` / `multi_block_local_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 6. `replace_object:1597`

- 负例类型/范围：`replace_object` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A large metal chair with a brown teddy bear in it."
- 原始正描述 2："There is a brown teddy bear seated in a large chair made of metal."
- 原始负描述："A brown teddy bear is in a hammock."
- 规范化正描述 1："a large metal chair with a brown teddy bear in it"
- 规范化正描述 2："there is a brown teddy bear seated in a large chair made of metal"
- 规范化负描述："a brown teddy bear is in a hammock"
- 正描述 1 选择元组：`[9, 19, 4, 0.7272727272727273, 0.7142857142857143]`
- 正描述 2 选择元组：`[10, 22, 4, 0.5714285714285714, 0.5538461538461539]`
- 最终比较正描述：`positive_1` / "A large metal chair with a brown teddy bear in it."
- 完整 lexeme 编辑块：`[{"tag": "delete", "positive_start": 0, "positive_end": 5, "negative_start": 0, "negative_end": 0, "positive_lexemes": ["a", "large", "metal", "chair", "with"], "negative_lexemes": []}, {"tag": "equal", "positive_start": 5, "positive_end": 9, "negative_start": 0, "negative_end": 4, "positive_lexemes": ["a", "brown", "teddy", "bear"], "negative_lexemes": ["a", "brown", "teddy", "bear"]}, {"tag": "insert", "positive_start": 9, "positive_end": 9, "negative_start": 4, "negative_end": 5, "positive_lexemes": [], "negative_lexemes": ["is"]}, {"tag": "equal", "positive_start": 9, "positive_end": 10, "negative_start": 5, "negative_end": 6, "positive_lexemes": ["in"], "negative_lexemes": ["in"]}, {"tag": "insert", "positive_start": 10, "positive_end": 10, "negative_start": 6, "negative_end": 7, "positive_lexemes": [], "negative_lexemes": ["a"]}, {"tag": "replace", "positive_start": 10, "positive_end": 11, "negative_start": 7, "negative_end": 8, "positive_lexemes": ["it"], "negative_lexemes": ["hammock"]}]`
- 共同前缀：`[]`
- 正确 contrast hull：`["a", "large", "metal", "chair", "with", "a", "brown", "teddy", "bear", "in", "it"]`
- 错误 contrast hull：`["a", "brown", "teddy", "bear", "is", "in", "a", "hammock"]`
- 共同后缀：`[]`
- Hull token 覆盖率（正/负/最大）：`[1.0, 1.0, 1.0]`
- 共同前缀模型 token：`[]`
- 正确 hull 模型 token：IDs `[100, 2994, 4743, 352, 890, 3709, 599, 299, 363, 2079, 113, 297, 382, 103, 124, 600, 370, 353, 563]`；text "a large metal chair with a brown teddy bear in it"
- 错误 hull 模型 token：IDs `[100, 363, 2079, 113, 297, 382, 103, 124, 600, 370, 395, 353, 299, 429, 497, 112, 4469]`；text "a brown teddy bear is in a hammock"
- 第一轮/第二轮分类：`complex_edit` / `whole_sentence_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；"at_least_one_hull_covers_all_model_tokens"

### 7. `replace_object:990`

- 负例类型/范围：`replace_object` / `{"canonical": true, "pilot": true, "formal": false, "certifying_formal": false}`
- 原始正描述 1："two children wearing sweaters shirts and ties "
- 原始正描述 2："Two children, each wearing a shirt, tie and sweater"
- 原始负描述："Two adults wearing sweaters, shirts, and ties."
- 规范化正描述 1："two children wearing sweaters shirts and ties"
- 规范化正描述 2："two children , each wearing a shirt , tie and sweater"
- 规范化负描述："two adults wearing sweaters , shirts , and ties"
- 正描述 1 选择元组：`[4, 10, 3, 0.3333333333333333, 0.23404255319148937]`
- 正描述 2 选择元组：`[14, 18, 4, 0.7272727272727273, 0.5660377358490566]`
- 最终比较正描述：`positive_1` / "two children wearing sweaters shirts and ties "
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 1, "negative_start": 0, "negative_end": 1, "positive_lexemes": ["two"], "negative_lexemes": ["two"]}, {"tag": "replace", "positive_start": 1, "positive_end": 2, "negative_start": 1, "negative_end": 2, "positive_lexemes": ["children"], "negative_lexemes": ["adults"]}, {"tag": "equal", "positive_start": 2, "positive_end": 4, "negative_start": 2, "negative_end": 4, "positive_lexemes": ["wearing", "sweaters"], "negative_lexemes": ["wearing", "sweaters"]}, {"tag": "insert", "positive_start": 4, "positive_end": 4, "negative_start": 4, "negative_end": 5, "positive_lexemes": [], "negative_lexemes": [","]}, {"tag": "equal", "positive_start": 4, "positive_end": 5, "negative_start": 5, "negative_end": 6, "positive_lexemes": ["shirts"], "negative_lexemes": ["shirts"]}, {"tag": "insert", "positive_start": 5, "positive_end": 5, "negative_start": 6, "negative_end": 7, "positive_lexemes": [], "negative_lexemes": [","]}, {"tag": "equal", "positive_start": 5, "positive_end": 7, "negative_start": 7, "negative_end": 9, "positive_lexemes": ["and", "ties"], "negative_lexemes": ["and", "ties"]}]`
- 共同前缀：`["two"]`
- 正确 contrast hull：`["children", "wearing", "sweaters", "shirts"]`
- 错误 contrast hull：`["adults", "wearing", "sweaters", ",", "shirts", ","]`
- 共同后缀：`["and", "ties"]`
- Hull token 覆盖率（正/负/最大）：`[0.6666666666666666, 0.7391304347826086, 0.7391304347826086]`
- 共同前缀模型 token：`[119, 122, 114]`
- 正确 hull 模型 token：IDs `[6109, 3193, 796, 370, 350, 316, 1747, 314, 496, 1128, 639, 2726]`；text " children wearing sweaters shirts"
- 错误 hull 模型 token：IDs `[1200, 1005, 118, 796, 370, 350, 316, 1747, 314, 496, 256, 47, 1128, 639, 2726, 256, 47]`；text " adults wearing sweaters , shirts ,"
- 第一轮/第二轮分类：`complex_edit` / `multi_block_local_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 8. `replace_relation:1033`

- 负例类型/范围：`replace_relation` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A person in a defensive stance with a tennis racquet."
- 原始正描述 2："A person holding a tennis racquet is in a defensive stance."
- 原始负描述："A person near a tennis court with a tennis racquet in hand."
- 规范化正描述 1："a person in a defensive stance with a tennis racquet"
- 规范化正描述 2："a person holding a tennis racquet is in a defensive stance"
- 规范化负描述："a person near a tennis court with a tennis racquet in hand"
- 正描述 1 选择元组：`[8, 18, 3, 0.4166666666666667, 0.39655172413793105]`
- 正描述 2 选择元组：`[15, 19, 3, 0.6666666666666666, 0.5689655172413793]`
- 最终比较正描述：`positive_1` / "A person in a defensive stance with a tennis racquet."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 2, "negative_start": 0, "negative_end": 2, "positive_lexemes": ["a", "person"], "negative_lexemes": ["a", "person"]}, {"tag": "replace", "positive_start": 2, "positive_end": 3, "negative_start": 2, "negative_end": 3, "positive_lexemes": ["in"], "negative_lexemes": ["near"]}, {"tag": "equal", "positive_start": 3, "positive_end": 4, "negative_start": 3, "negative_end": 4, "positive_lexemes": ["a"], "negative_lexemes": ["a"]}, {"tag": "replace", "positive_start": 4, "positive_end": 6, "negative_start": 4, "negative_end": 6, "positive_lexemes": ["defensive", "stance"], "negative_lexemes": ["tennis", "court"]}, {"tag": "equal", "positive_start": 6, "positive_end": 10, "negative_start": 6, "negative_end": 10, "positive_lexemes": ["with", "a", "tennis", "racquet"], "negative_lexemes": ["with", "a", "tennis", "racquet"]}, {"tag": "insert", "positive_start": 10, "positive_end": 10, "negative_start": 10, "negative_end": 12, "positive_lexemes": [], "negative_lexemes": ["in", "hand"]}]`
- 共同前缀：`["a", "person"]`
- 正确 contrast hull：`["in", "a", "defensive", "stance", "with", "a", "tennis", "racquet"]`
- 错误 contrast hull：`["near", "a", "tennis", "court", "with", "a", "tennis", "racquet", "in", "hand"]`
- 共同后缀：`[]`
- Hull token 覆盖率（正/负/最大）：`[0.8888888888888888, 0.9047619047619048, 0.9047619047619048]`
- 共同前缀模型 token：`[100, 2198]`
- 正确 hull 模型 token：IDs `[353, 299, 2654, 2101, 884, 580, 1079, 599, 299, 297, 6201, 324, 256, 1329, 537, 439]`；text " in a defensive stance with a tennis racquet"
- 错误 hull 模型 token：IDs `[730, 370, 299, 297, 6201, 324, 3759, 119, 599, 299, 297, 6201, 324, 256, 1329, 537, 439, 353, 3319]`；text " near a tennis court with a tennis racquet in hand"
- 第一轮/第二轮分类：`complex_edit` / `large_contrast_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；"maximum_hull_token_coverage_above_75_percent"

### 9. `replace_relation:422`

- 负例类型/范围：`replace_relation` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："What appears to be a beach-side eatery has an outdoor area with a metal railing and high stools, the whole of which rests on a tilted walkway with a sign and  a bench with a logo on it. "
- 原始正描述 2："The outdoor area of the beach-side eatery has a metal railing and high stools, which are positioned on a tilted walkway with a sign and a bench with a logo on it."
- 原始负描述："What appears to be a beach-side eatery doesn't have an outdoor area with a metal railing and high stools, but there is a tilted walkway with a sign and a bench with a logo on it."
- 规范化正描述 1："what appears to be a beach-side eatery has an outdoor area with a metal railing and high stools , the whole of which rests on a tilted walkway with a sign and a bench with a logo on it"
- 规范化正描述 2："the outdoor area of the beach-side eatery has a metal railing and high stools , which are positioned on a tilted walkway with a sign and a bench with a logo on it"
- 规范化负描述："what appears to be a beach-side eatery doesn't have an outdoor area with a metal railing and high stools , but there is a tilted walkway with a sign and a bench with a logo on it"
- 正描述 1 选择元组：`[12, 34, 4, 0.20512820512820512, 0.16847826086956522]`
- 正描述 2 选择元组：`[24, 42, 5, 0.40540540540540543, 0.38202247191011235]`
- 最终比较正描述：`positive_1` / "What appears to be a beach-side eatery has an outdoor area with a metal railing and high stools, the whole of which rests on a tilted walkway with a sign and  a bench with a logo on it. "
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 7, "negative_start": 0, "negative_end": 7, "positive_lexemes": ["what", "appears", "to", "be", "a", "beach-side", "eatery"], "negative_lexemes": ["what", "appears", "to", "be", "a", "beach-side", "eatery"]}, {"tag": "insert", "positive_start": 7, "positive_end": 7, "negative_start": 7, "negative_end": 8, "positive_lexemes": [], "negative_lexemes": ["doesn't"]}, {"tag": "replace", "positive_start": 7, "positive_end": 8, "negative_start": 8, "negative_end": 9, "positive_lexemes": ["has"], "negative_lexemes": ["have"]}, {"tag": "equal", "positive_start": 8, "positive_end": 19, "negative_start": 9, "negative_end": 20, "positive_lexemes": ["an", "outdoor", "area", "with", "a", "metal", "railing", "and", "high", "stools", ","], "negative_lexemes": ["an", "outdoor", "area", "with", "a", "metal", "railing", "and", "high", "stools", ","]}, {"tag": "delete", "positive_start": 19, "positive_end": 22, "negative_start": 20, "negative_end": 20, "positive_lexemes": ["the", "whole", "of"], "negative_lexemes": []}, {"tag": "replace", "positive_start": 22, "positive_end": 25, "negative_start": 20, "negative_end": 23, "positive_lexemes": ["which", "rests", "on"], "negative_lexemes": ["but", "there", "is"]}, {"tag": "equal", "positive_start": 25, "positive_end": 39, "negative_start": 23, "negative_end": 37, "positive_lexemes": ["a", "tilted", "walkway", "with", "a", "sign", "and", "a", "bench", "with", "a", "logo", "on", "it"], "negative_lexemes": ["a", "tilted", "walkway", "with", "a", "sign", "and", "a", "bench", "with", "a", "logo", "on", "it"]}]`
- 共同前缀：`["what", "appears", "to", "be", "a", "beach-side", "eatery"]`
- 正确 contrast hull：`["has", "an", "outdoor", "area", "with", "a", "metal", "railing", "and", "high", "stools", ",", "the", "whole", "of", "which", "rests", "on"]`
- 错误 contrast hull：`["doesn't", "have", "an", "outdoor", "area", "with", "a", "metal", "railing", "and", "high", "stools", ",", "but", "there", "is"]`
- 共同后缀：`["a", "tilted", "walkway", "with", "a", "sign", "and", "a", "bench", "with", "a", "logo", "on", "it"]`
- Hull token 覆盖率（正/负/最大）：`[0.453125, 0.43548387096774194, 0.453125]`
- 共同前缀模型 token：`[4465, 314, 4651, 2546, 364, 600, 299, 600, 1268, 48, 118, 688, 413, 314, 1976]`
- 正确 hull 模型 token：IDs `[1290, 346, 1695, 103, 114, 336, 2808, 599, 299, 4743, 352, 2265, 485, 350, 376, 2844, 580, 114, 4605, 256, 47, 309, 2109, 361, 354, 1045, 5128, 118, 619]`；text " has an outdoor area with a metal railing and high stools , the whole of which rests on"
- 错误 hull 模型 token：IDs `[2310, 113, 1445, 874, 346, 1695, 103, 114, 336, 2808, 599, 299, 4743, 352, 2265, 485, 350, 376, 2844, 580, 114, 4605, 256, 47, 1362, 1975, 395]`；text " doesn't have an outdoor area with a metal railing and high stools , but there is"
- 第一轮/第二轮分类：`complex_edit` / `multi_block_local_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 10. `replace_relation:65`

- 负例类型/范围：`replace_relation` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A messy bedroom has one red brick wall."
- 原始正描述 2："The red brick wall is in a messy bedroom."
- 原始负描述："A messy bedroom doesn't have any red brick walls."
- 规范化正描述 1："a messy bedroom has one red brick wall"
- 规范化正描述 2："the red brick wall is in a messy bedroom"
- 规范化负描述："a messy bedroom doesn't have any red brick walls"
- 正描述 1 选择元组：`[7, 11, 3, 0.4444444444444444, 0.2708333333333333]`
- 正描述 2 选择元组：`[18, 18, 1, 1.0, 0.8125]`
- 最终比较正描述：`positive_1` / "A messy bedroom has one red brick wall."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 3, "negative_start": 0, "negative_end": 3, "positive_lexemes": ["a", "messy", "bedroom"], "negative_lexemes": ["a", "messy", "bedroom"]}, {"tag": "insert", "positive_start": 3, "positive_end": 3, "negative_start": 3, "negative_end": 4, "positive_lexemes": [], "negative_lexemes": ["doesn't"]}, {"tag": "replace", "positive_start": 3, "positive_end": 5, "negative_start": 4, "negative_end": 6, "positive_lexemes": ["has", "one"], "negative_lexemes": ["have", "any"]}, {"tag": "equal", "positive_start": 5, "positive_end": 7, "negative_start": 6, "negative_end": 8, "positive_lexemes": ["red", "brick"], "negative_lexemes": ["red", "brick"]}, {"tag": "replace", "positive_start": 7, "positive_end": 8, "negative_start": 8, "negative_end": 9, "positive_lexemes": ["wall"], "negative_lexemes": ["walls"]}]`
- 共同前缀：`["a", "messy", "bedroom"]`
- 正确 contrast hull：`["has", "one", "red", "brick", "wall"]`
- 错误 contrast hull：`["doesn't", "have", "any", "red", "brick", "walls"]`
- 共同后缀：`[]`
- Hull token 覆盖率（正/负/最大）：`[0.5, 0.6111111111111112, 0.6111111111111112]`
- 共同前缀模型 token：`[100, 3202, 124, 363, 382, 393, 444]`
- 正确 hull 模型 token：IDs `[1290, 1623, 5534, 3461, 2437, 339, 1266]`；text " has one red brick wall"
- 错误 hull 模型 token：IDs `[2310, 113, 1445, 874, 1149, 5534, 3461, 2437, 339, 1266, 118]`；text " doesn't have any red brick walls"
- 第一轮/第二轮分类：`complex_edit` / `multi_block_local_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 11. `replace_relation:659`

- 负例类型/范围：`replace_relation` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A room with a bunch of stainless steel items and other accessories."
- 原始正描述 2："The room is furnished with a variety of stainless steel items and other accessories."
- 原始负描述："A room without any stainless steel items or other accessories."
- 规范化正描述 1："a room with a bunch of stainless steel items and other accessories"
- 规范化正描述 2："the room is furnished with a variety of stainless steel items and other accessories"
- 规范化负描述："a room without any stainless steel items or other accessories"
- 正描述 1 选择元组：`[8, 14, 3, 0.4166666666666667, 0.19696969696969696]`
- 正描述 2 选择元组：`[12, 20, 4, 0.5714285714285714, 0.3614457831325301]`
- 最终比较正描述：`positive_1` / "A room with a bunch of stainless steel items and other accessories."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 2, "negative_start": 0, "negative_end": 2, "positive_lexemes": ["a", "room"], "negative_lexemes": ["a", "room"]}, {"tag": "delete", "positive_start": 2, "positive_end": 4, "negative_start": 2, "negative_end": 2, "positive_lexemes": ["with", "a"], "negative_lexemes": []}, {"tag": "replace", "positive_start": 4, "positive_end": 6, "negative_start": 2, "negative_end": 4, "positive_lexemes": ["bunch", "of"], "negative_lexemes": ["without", "any"]}, {"tag": "equal", "positive_start": 6, "positive_end": 9, "negative_start": 4, "negative_end": 7, "positive_lexemes": ["stainless", "steel", "items"], "negative_lexemes": ["stainless", "steel", "items"]}, {"tag": "replace", "positive_start": 9, "positive_end": 10, "negative_start": 7, "negative_end": 8, "positive_lexemes": ["and"], "negative_lexemes": ["or"]}, {"tag": "equal", "positive_start": 10, "positive_end": 12, "negative_start": 8, "negative_end": 10, "positive_lexemes": ["other", "accessories"], "negative_lexemes": ["other", "accessories"]}]`
- 共同前缀：`["a", "room"]`
- 正确 contrast hull：`["with", "a", "bunch", "of", "stainless", "steel", "items", "and"]`
- 错误 contrast hull：`["without", "any", "stainless", "steel", "items", "or"]`
- 共同后缀：`["other", "accessories"]`
- Hull token 覆盖率（正/负/最大）：`[0.6666666666666666, 0.5882352941176471, 0.6666666666666666]`
- 共同前缀模型 token：`[100, 1552, 444]`
- 正确 hull 模型 token：IDs `[599, 299, 363, 651, 550, 354, 580, 740, 5062, 580, 104, 446, 6015, 376]`；text " with a bunch of stainless steel items and"
- 错误 hull 模型 token：IDs `[4007, 1149, 580, 740, 5062, 580, 104, 446, 6015, 522]`；text " without any stainless steel items or"
- 第一轮/第二轮分类：`complex_edit` / `multi_block_local_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 12. `replace_relation:892`

- 负例类型/范围：`replace_relation` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："Men in blue shirts push carts of luggage in an airport."
- 原始正描述 2："Carts of luggage are pushed by men in blue shirts in an airport."
- 原始负描述："Men outside of the airport push carts of luggage."
- 规范化正描述 1："men in blue shirts push carts of luggage in an airport"
- 规范化正描述 2："carts of luggage are pushed by men in blue shirts in an airport"
- 规范化负描述："men outside of the airport push carts of luggage"
- 正描述 1 选择元组：`[10, 18, 3, 0.6363636363636364, 0.5740740740740741]`
- 正描述 2 选择元组：`[22, 22, 2, 1.0, 0.746031746031746]`
- 最终比较正描述：`positive_1` / "Men in blue shirts push carts of luggage in an airport."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 1, "negative_start": 0, "negative_end": 1, "positive_lexemes": ["men"], "negative_lexemes": ["men"]}, {"tag": "insert", "positive_start": 1, "positive_end": 1, "negative_start": 1, "negative_end": 2, "positive_lexemes": [], "negative_lexemes": ["outside"]}, {"tag": "replace", "positive_start": 1, "positive_end": 4, "negative_start": 2, "negative_end": 5, "positive_lexemes": ["in", "blue", "shirts"], "negative_lexemes": ["of", "the", "airport"]}, {"tag": "equal", "positive_start": 4, "positive_end": 8, "negative_start": 5, "negative_end": 9, "positive_lexemes": ["push", "carts", "of", "luggage"], "negative_lexemes": ["push", "carts", "of", "luggage"]}, {"tag": "delete", "positive_start": 8, "positive_end": 11, "negative_start": 9, "negative_end": 9, "positive_lexemes": ["in", "an", "airport"], "negative_lexemes": []}]`
- 共同前缀：`["men"]`
- 正确 contrast hull：`["in", "blue", "shirts", "push", "carts", "of", "luggage", "in", "an", "airport"]`
- 错误 contrast hull：`["outside", "of", "the", "airport", "push", "carts", "of", "luggage"]`
- 共同后缀：`[]`
- Hull token 覆盖率（正/负/最大）：`[0.9047619047619048, 0.8947368421052632, 0.9047619047619048]`
- 共同前缀模型 token：`[112, 327]`
- 正确 hull 模型 token：IDs `[353, 4300, 1128, 639, 2726, 344, 4923, 317, 913, 118, 354, 406, 3304, 106, 834, 353, 346, 3980, 1426]`；text " in blue shirts push carts of luggage in an airport"
- 错误 hull 模型 token：IDs `[1695, 118, 688, 354, 309, 3980, 1426, 344, 4923, 317, 913, 118, 354, 406, 3304, 106, 834]`；text " outside of the airport push carts of luggage"
- 第一轮/第二轮分类：`complex_edit` / `large_contrast_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；"maximum_hull_token_coverage_above_75_percent"

### 13. `swap_atribute:107`

- 负例类型/范围：`swap_atribute` / `{"canonical": true, "pilot": true, "formal": false, "certifying_formal": false}`
- 原始正描述 1："A white truck with a red car sitting in it's back."
- 原始正描述 2："A red car is positioned in the back of a white truck."
- 原始负描述："A red truck with a white car sitting in its back."
- 规范化正描述 1："a white truck with a red car sitting in it's back"
- 规范化正描述 2："a red car is positioned in the back of a white truck"
- 规范化负描述："a red truck with a white car sitting in its back"
- 正描述 1 选择元组：`[6, 18, 3, 0.2727272727272727, 0.22448979591836735]`
- 正描述 2 选择元组：`[19, 19, 2, 0.8333333333333334, 0.6538461538461539]`
- 最终比较正描述：`positive_1` / "A white truck with a red car sitting in it's back."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 1, "negative_start": 0, "negative_end": 1, "positive_lexemes": ["a"], "negative_lexemes": ["a"]}, {"tag": "replace", "positive_start": 1, "positive_end": 2, "negative_start": 1, "negative_end": 2, "positive_lexemes": ["white"], "negative_lexemes": ["red"]}, {"tag": "equal", "positive_start": 2, "positive_end": 5, "negative_start": 2, "negative_end": 5, "positive_lexemes": ["truck", "with", "a"], "negative_lexemes": ["truck", "with", "a"]}, {"tag": "replace", "positive_start": 5, "positive_end": 6, "negative_start": 5, "negative_end": 6, "positive_lexemes": ["red"], "negative_lexemes": ["white"]}, {"tag": "equal", "positive_start": 6, "positive_end": 9, "negative_start": 6, "negative_end": 9, "positive_lexemes": ["car", "sitting", "in"], "negative_lexemes": ["car", "sitting", "in"]}, {"tag": "replace", "positive_start": 9, "positive_end": 10, "negative_start": 9, "negative_end": 10, "positive_lexemes": ["it's"], "negative_lexemes": ["its"]}, {"tag": "equal", "positive_start": 10, "positive_end": 11, "negative_start": 10, "negative_end": 11, "positive_lexemes": ["back"], "negative_lexemes": ["back"]}]`
- 共同前缀：`["a"]`
- 正确 contrast hull：`["white", "truck", "with", "a", "red", "car", "sitting", "in", "it's"]`
- 错误 contrast hull：`["red", "truck", "with", "a", "white", "car", "sitting", "in", "its"]`
- 共同后缀：`["back"]`
- Hull token 覆盖率（正/负/最大）：`[0.875, 0.8666666666666667, 0.875]`
- 共同前缀模型 token：`[100]`
- 正确 hull 模型 token：IDs `[654, 1078, 1144, 120, 892, 599, 299, 5534, 3751, 5305, 2912, 353, 563, 628]`；text " white truck with a red car sitting in it's"
- 错误 hull 模型 token：IDs `[5534, 1144, 120, 892, 599, 299, 654, 1078, 3751, 5305, 2912, 353, 1342]`；text " red truck with a white car sitting in its"
- 第一轮/第二轮分类：`complex_edit` / `large_contrast_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；"maximum_hull_token_coverage_above_75_percent"

### 14. `swap_atribute:147`

- 负例类型/范围：`swap_atribute` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："Brown and black dog sitting on the brown couch by itself."
- 原始正描述 2："The dog, which is brown and black, is sitting on the brown couch by itself."
- 原始负描述："Black and brown dog sitting on the black couch by itself."
- 规范化正描述 1："brown and black dog sitting on the brown couch by itself"
- 规范化正描述 2："the dog , which is brown and black , is sitting on the brown couch by itself"
- 规范化负描述："black and brown dog sitting on the black couch by itself"
- 正描述 1 选择元组：`[6, 16, 3, 0.2727272727272727, 0.21428571428571427]`
- 正描述 2 选择元组：`[14, 22, 5, 0.5882352941176471, 0.4473684210526316]`
- 最终比较正描述：`positive_1` / "Brown and black dog sitting on the brown couch by itself."
- 完整 lexeme 编辑块：`[{"tag": "replace", "positive_start": 0, "positive_end": 1, "negative_start": 0, "negative_end": 1, "positive_lexemes": ["brown"], "negative_lexemes": ["black"]}, {"tag": "equal", "positive_start": 1, "positive_end": 2, "negative_start": 1, "negative_end": 2, "positive_lexemes": ["and"], "negative_lexemes": ["and"]}, {"tag": "replace", "positive_start": 2, "positive_end": 3, "negative_start": 2, "negative_end": 3, "positive_lexemes": ["black"], "negative_lexemes": ["brown"]}, {"tag": "equal", "positive_start": 3, "positive_end": 7, "negative_start": 3, "negative_end": 7, "positive_lexemes": ["dog", "sitting", "on", "the"], "negative_lexemes": ["dog", "sitting", "on", "the"]}, {"tag": "replace", "positive_start": 7, "positive_end": 8, "negative_start": 7, "negative_end": 8, "positive_lexemes": ["brown"], "negative_lexemes": ["black"]}, {"tag": "equal", "positive_start": 8, "positive_end": 11, "negative_start": 8, "negative_end": 11, "positive_lexemes": ["couch", "by", "itself"], "negative_lexemes": ["couch", "by", "itself"]}]`
- 共同前缀：`[]`
- 正确 contrast hull：`["brown", "and", "black", "dog", "sitting", "on", "the", "brown"]`
- 错误 contrast hull：`["black", "and", "brown", "dog", "sitting", "on", "the", "black"]`
- 共同后缀：`["couch", "by", "itself"]`
- Hull token 覆盖率（正/负/最大）：`[0.7142857142857143, 0.7142857142857143, 0.7142857142857143]`
- 共同前缀模型 token：`[]`
- 正确 hull 模型 token：IDs `[101, 2079, 113, 376, 2597, 1637, 1041, 106, 5305, 2912, 619, 309, 363, 2079, 113]`；text "brown and black dog sitting on the brown"
- 错误 hull 模型 token：IDs `[101, 111, 1637, 376, 363, 2079, 113, 1041, 106, 5305, 2912, 619, 309, 2597, 1637]`；text "black and brown dog sitting on the black"
- 第一轮/第二轮分类：`complex_edit` / `multi_block_local_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 15. `swap_atribute:171`

- 负例类型/范围：`swap_atribute` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："Some flowers are sitting in the white vase in front of the window."
- 原始正描述 2："The white vase is positioned in front of the window, and some flowers are inside it."
- 原始负描述："The white flowers are sitting in a vase in front of the window."
- 规范化正描述 1："some flowers are sitting in the white vase in front of the window"
- 规范化正描述 2："the white vase is positioned in front of the window , and some flowers are inside it"
- 规范化负描述："the white flowers are sitting in a vase in front of the window"
- 正描述 1 选择元组：`[6, 14, 4, 0.3076923076923077, 0.26153846153846155]`
- 正描述 2 选择元组：`[16, 26, 3, 0.7647058823529411, 0.6071428571428571]`
- 最终比较正描述：`positive_1` / "Some flowers are sitting in the white vase in front of the window."
- 完整 lexeme 编辑块：`[{"tag": "insert", "positive_start": 0, "positive_end": 0, "negative_start": 0, "negative_end": 1, "positive_lexemes": [], "negative_lexemes": ["the"]}, {"tag": "replace", "positive_start": 0, "positive_end": 1, "negative_start": 1, "negative_end": 2, "positive_lexemes": ["some"], "negative_lexemes": ["white"]}, {"tag": "equal", "positive_start": 1, "positive_end": 5, "negative_start": 2, "negative_end": 6, "positive_lexemes": ["flowers", "are", "sitting", "in"], "negative_lexemes": ["flowers", "are", "sitting", "in"]}, {"tag": "delete", "positive_start": 5, "positive_end": 6, "negative_start": 6, "negative_end": 6, "positive_lexemes": ["the"], "negative_lexemes": []}, {"tag": "replace", "positive_start": 6, "positive_end": 7, "negative_start": 6, "negative_end": 7, "positive_lexemes": ["white"], "negative_lexemes": ["a"]}, {"tag": "equal", "positive_start": 7, "positive_end": 13, "negative_start": 7, "negative_end": 13, "positive_lexemes": ["vase", "in", "front", "of", "the", "window"], "negative_lexemes": ["vase", "in", "front", "of", "the", "window"]}]`
- 共同前缀：`[]`
- 正确 contrast hull：`["some", "flowers", "are", "sitting", "in", "the", "white"]`
- 错误 contrast hull：`["the", "white", "flowers", "are", "sitting", "in", "a"]`
- 共同后缀：`["vase", "in", "front", "of", "the", "window"]`
- Hull token 覆盖率（正/负/最大）：`[0.5238095238095238, 0.5, 0.5238095238095238]`
- 共同前缀模型 token：`[]`
- 正确 hull 模型 token：IDs `[118, 3219, 5652, 496, 732, 5305, 2912, 353, 309, 654, 1078]`；text "some flowers are sitting in the white"
- 错误 hull 模型 token：IDs `[4345, 654, 1078, 5652, 496, 732, 5305, 2912, 353, 299]`；text "the white flowers are sitting in a"
- 第一轮/第二轮分类：`complex_edit` / `multi_block_local_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 16. `swap_atribute:231`

- 负例类型/范围：`swap_atribute` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A table topped with a white plate covered in three donuts."
- 原始正描述 2："A white plate covered in three donuts is positioned on top of a table."
- 原始负描述："A table topped with three plates covered in white donuts."
- 规范化正描述 1："a table topped with a white plate covered in three donuts"
- 规范化正描述 2："a white plate covered in three donuts is positioned on top of a table"
- 规范化负描述："a table topped with three plates covered in white donuts"
- 正描述 1 选择元组：`[7, 11, 3, 0.36363636363636365, 0.15789473684210525]`
- 正描述 2 选择元组：`[20, 22, 4, 0.8571428571428571, 0.6231884057971014]`
- 最终比较正描述：`positive_1` / "A table topped with a white plate covered in three donuts."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 4, "negative_start": 0, "negative_end": 4, "positive_lexemes": ["a", "table", "topped", "with"], "negative_lexemes": ["a", "table", "topped", "with"]}, {"tag": "delete", "positive_start": 4, "positive_end": 5, "negative_start": 4, "negative_end": 4, "positive_lexemes": ["a"], "negative_lexemes": []}, {"tag": "replace", "positive_start": 5, "positive_end": 7, "negative_start": 4, "negative_end": 6, "positive_lexemes": ["white", "plate"], "negative_lexemes": ["three", "plates"]}, {"tag": "equal", "positive_start": 7, "positive_end": 9, "negative_start": 6, "negative_end": 8, "positive_lexemes": ["covered", "in"], "negative_lexemes": ["covered", "in"]}, {"tag": "replace", "positive_start": 9, "positive_end": 10, "negative_start": 8, "negative_end": 9, "positive_lexemes": ["three"], "negative_lexemes": ["white"]}, {"tag": "equal", "positive_start": 10, "positive_end": 11, "negative_start": 9, "negative_end": 10, "positive_lexemes": ["donuts"], "negative_lexemes": ["donuts"]}]`
- 共同前缀：`["a", "table", "topped", "with"]`
- 正确 contrast hull：`["a", "white", "plate", "covered", "in", "three"]`
- 错误 contrast hull：`["three", "plates", "covered", "in", "white"]`
- 共同后缀：`["donuts"]`
- Hull token 覆盖率（正/负/最大）：`[0.5263157894736842, 0.5, 0.5263157894736842]`
- 共同前缀模型 token：`[100, 2630, 364, 737, 382, 599]`
- 正确 hull 模型 token：IDs `[299, 654, 1078, 1219, 557, 966, 478, 1837, 353, 3785]`；text " a white plate covered in three"
- 错误 hull 模型 token：IDs `[3785, 1219, 1434, 966, 478, 1837, 353, 654, 1078]`；text " three plates covered in white"
- 第一轮/第二轮分类：`complex_edit` / `multi_block_local_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 17. `swap_atribute:241`

- 负例类型/范围：`swap_atribute` / `{"canonical": true, "pilot": true, "formal": false, "certifying_formal": false}`
- 原始正描述 1："A view of a store that sells teddy bears. There is a huge display in the window."
- 原始正描述 2："A store that sells teddy bears is visible in the view. The display in the window is enormous."
- 原始负描述："A view of a store that sells huge bears. There is not a teddy display in the window."
- 规范化正描述 1："a view of a store that sells teddy bears . there is a huge display in the window"
- 规范化正描述 2："a store that sells teddy bears is visible in the view . the display in the window is enormous"
- 规范化负描述："a view of a store that sells huge bears . there is not a teddy display in the window"
- 正描述 1 选择元组：`[5, 15, 3, 0.15789473684210525, 0.16666666666666666]`
- 正描述 2 选择元组：`[20, 38, 5, 0.6842105263157895, 0.5161290322580645]`
- 最终比较正描述：`positive_1` / "A view of a store that sells teddy bears. There is a huge display in the window."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 7, "negative_start": 0, "negative_end": 7, "positive_lexemes": ["a", "view", "of", "a", "store", "that", "sells"], "negative_lexemes": ["a", "view", "of", "a", "store", "that", "sells"]}, {"tag": "replace", "positive_start": 7, "positive_end": 8, "negative_start": 7, "negative_end": 8, "positive_lexemes": ["teddy"], "negative_lexemes": ["huge"]}, {"tag": "equal", "positive_start": 8, "positive_end": 12, "negative_start": 8, "negative_end": 12, "positive_lexemes": ["bears", ".", "there", "is"], "negative_lexemes": ["bears", ".", "there", "is"]}, {"tag": "insert", "positive_start": 12, "positive_end": 12, "negative_start": 12, "negative_end": 13, "positive_lexemes": [], "negative_lexemes": ["not"]}, {"tag": "equal", "positive_start": 12, "positive_end": 13, "negative_start": 13, "negative_end": 14, "positive_lexemes": ["a"], "negative_lexemes": ["a"]}, {"tag": "replace", "positive_start": 13, "positive_end": 14, "negative_start": 14, "negative_end": 15, "positive_lexemes": ["huge"], "negative_lexemes": ["teddy"]}, {"tag": "equal", "positive_start": 14, "positive_end": 18, "negative_start": 15, "negative_end": 19, "positive_lexemes": ["display", "in", "the", "window"], "negative_lexemes": ["display", "in", "the", "window"]}]`
- 共同前缀：`["a", "view", "of", "a", "store", "that", "sells"]`
- 正确 contrast hull：`["teddy", "bears", ".", "there", "is", "a", "huge"]`
- 错误 contrast hull：`["huge", "bears", ".", "there", "is", "not", "a", "teddy"]`
- 共同后缀：`["display", "in", "the", "window"]`
- Hull token 覆盖率（正/负/最大）：`[0.43333333333333335, 0.45161290322580644, 0.45161290322580644]`
- 共同前缀模型 token：`[100, 603, 1400, 122, 354, 299, 5074, 591, 316, 1272, 118]`
- 正确 hull 模型 token：IDs `[297, 382, 103, 124, 600, 2546, 6304, 1975, 395, 299, 429, 120, 583]`；text " teddy bears . there is a huge"
- 错误 hull 模型 token：IDs `[429, 120, 583, 600, 2546, 6304, 1975, 395, 1027, 299, 297, 382, 103, 124]`；text " huge bears . there is not a teddy"
- 第一轮/第二轮分类：`complex_edit` / `multi_block_local_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 18. `swap_atribute:244`

- 负例类型/范围：`swap_atribute` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A Teddy bear sits on a floral patterned chair."
- 原始正描述 2："The floral patterned chair is positioned under the Teddy bear."
- 原始负描述："A floral patterned bear sits on a Teddy chair."
- 规范化正描述 1："a teddy bear sits on a floral patterned chair"
- 规范化正描述 2："the floral patterned chair is positioned under the teddy bear"
- 规范化负描述："a floral patterned bear sits on a teddy chair"
- 正描述 1 选择元组：`[6, 14, 4, 0.4444444444444444, 0.6222222222222222]`
- 正描述 2 选择元组：`[13, 19, 4, 0.7, 0.4262295081967213]`
- 最终比较正描述：`positive_1` / "A Teddy bear sits on a floral patterned chair."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 1, "negative_start": 0, "negative_end": 1, "positive_lexemes": ["a"], "negative_lexemes": ["a"]}, {"tag": "insert", "positive_start": 1, "positive_end": 1, "negative_start": 1, "negative_end": 2, "positive_lexemes": [], "negative_lexemes": ["floral"]}, {"tag": "replace", "positive_start": 1, "positive_end": 2, "negative_start": 2, "negative_end": 3, "positive_lexemes": ["teddy"], "negative_lexemes": ["patterned"]}, {"tag": "equal", "positive_start": 2, "positive_end": 6, "negative_start": 3, "negative_end": 7, "positive_lexemes": ["bear", "sits", "on", "a"], "negative_lexemes": ["bear", "sits", "on", "a"]}, {"tag": "delete", "positive_start": 6, "positive_end": 7, "negative_start": 7, "negative_end": 7, "positive_lexemes": ["floral"], "negative_lexemes": []}, {"tag": "replace", "positive_start": 7, "positive_end": 8, "negative_start": 7, "negative_end": 8, "positive_lexemes": ["patterned"], "negative_lexemes": ["teddy"]}, {"tag": "equal", "positive_start": 8, "positive_end": 9, "negative_start": 8, "negative_end": 9, "positive_lexemes": ["chair"], "negative_lexemes": ["chair"]}]`
- 共同前缀：`["a"]`
- 正确 contrast hull：`["teddy", "bear", "sits", "on", "a", "floral", "patterned"]`
- 错误 contrast hull：`["floral", "patterned", "bear", "sits", "on", "a", "teddy"]`
- 共同后缀：`["chair"]`
- Hull token 覆盖率（正/负/最大）：`[0.8333333333333334, 0.8333333333333334, 0.8333333333333334]`
- 共同前缀模型 token：`[100]`
- 正确 hull 模型 token：IDs `[297, 382, 103, 124, 600, 370, 316, 2163, 619, 299, 3687, 336, 352, 5335, 382]`；text " teddy bear sits on a floral patterned"
- 错误 hull 模型 token：IDs `[3687, 336, 352, 5335, 382, 600, 370, 316, 2163, 619, 299, 297, 382, 103, 124]`；text " floral patterned bear sits on a teddy"
- 第一轮/第二轮分类：`complex_edit` / `large_contrast_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；"maximum_hull_token_coverage_above_75_percent"

### 19. `swap_atribute:344`

- 负例类型/范围：`swap_atribute` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A bus parked outside and below an illuminated Apple sign."
- 原始正描述 2："An illuminated Apple sign is positioned above a bus that is parked outside."
- 原始负描述："An illuminated bus parked below an outside Apple sign."
- 规范化正描述 1："a bus parked outside and below an illuminated apple sign"
- 规范化正描述 2："an illuminated apple sign is positioned above a bus that is parked outside"
- 规范化负描述："an illuminated bus parked below an outside apple sign"
- 正描述 1 选择元组：`[7, 15, 4, 0.5, 0.4642857142857143]`
- 正描述 2 选择元组：`[18, 18, 2, 0.8461538461538461, 0.5945945945945946]`
- 最终比较正描述：`positive_1` / "A bus parked outside and below an illuminated Apple sign."
- 完整 lexeme 编辑块：`[{"tag": "insert", "positive_start": 0, "positive_end": 0, "negative_start": 0, "negative_end": 1, "positive_lexemes": [], "negative_lexemes": ["an"]}, {"tag": "replace", "positive_start": 0, "positive_end": 1, "negative_start": 1, "negative_end": 2, "positive_lexemes": ["a"], "negative_lexemes": ["illuminated"]}, {"tag": "equal", "positive_start": 1, "positive_end": 3, "negative_start": 2, "negative_end": 4, "positive_lexemes": ["bus", "parked"], "negative_lexemes": ["bus", "parked"]}, {"tag": "delete", "positive_start": 3, "positive_end": 5, "negative_start": 4, "negative_end": 4, "positive_lexemes": ["outside", "and"], "negative_lexemes": []}, {"tag": "equal", "positive_start": 5, "positive_end": 7, "negative_start": 4, "negative_end": 6, "positive_lexemes": ["below", "an"], "negative_lexemes": ["below", "an"]}, {"tag": "replace", "positive_start": 7, "positive_end": 8, "negative_start": 6, "negative_end": 7, "positive_lexemes": ["illuminated"], "negative_lexemes": ["outside"]}, {"tag": "equal", "positive_start": 8, "positive_end": 10, "negative_start": 7, "negative_end": 9, "positive_lexemes": ["apple", "sign"], "negative_lexemes": ["apple", "sign"]}]`
- 共同前缀：`[]`
- 正确 contrast hull：`["a", "bus", "parked", "outside", "and", "below", "an", "illuminated"]`
- 错误 contrast hull：`["an", "illuminated", "bus", "parked", "below", "an", "outside"]`
- 共同后缀：`["apple", "sign"]`
- Hull token 覆盖率（正/负/最大）：`[0.85, 0.8421052631578947, 0.85]`
- 共同前缀模型 token：`[]`
- 正确 hull 模型 token：IDs `[100, 2499, 344, 2000, 382, 1695, 118, 688, 376, 4021, 451, 346, 256, 959, 457, 301, 1095]`；text "a bus parked outside and below an illuminated"
- 错误 hull 模型 token：IDs `[325, 256, 959, 457, 301, 1095, 2499, 344, 2000, 382, 4021, 451, 346, 1695, 118, 688]`；text "an illuminated bus parked below an outside"
- 第一轮/第二轮分类：`ambiguous_source` / `large_contrast_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；"maximum_hull_token_coverage_above_75_percent"

### 20. `swap_atribute:354`

- 负例类型/范围：`swap_atribute` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A person feeding four giraffes with grass and leaves."
- 原始正描述 2："A person is positioned next to four giraffes, providing them with grass and leaves."
- 原始负描述："Four persons feeding a giraffe grass and leaves."
- 规范化正描述 1："a person feeding four giraffes with grass and leaves"
- 规范化正描述 2："a person is positioned next to four giraffes , providing them with grass and leaves"
- 规范化负描述："four persons feeding a giraffe grass and leaves"
- 正描述 1 选择元组：`[9, 11, 3, 0.5555555555555556, 0.28846153846153844]`
- 正描述 2 选择元组：`[15, 17, 3, 0.7333333333333333, 0.5783132530120482]`
- 最终比较正描述：`positive_1` / "A person feeding four giraffes with grass and leaves."
- 完整 lexeme 编辑块：`[{"tag": "replace", "positive_start": 0, "positive_end": 2, "negative_start": 0, "negative_end": 2, "positive_lexemes": ["a", "person"], "negative_lexemes": ["four", "persons"]}, {"tag": "equal", "positive_start": 2, "positive_end": 3, "negative_start": 2, "negative_end": 3, "positive_lexemes": ["feeding"], "negative_lexemes": ["feeding"]}, {"tag": "delete", "positive_start": 3, "positive_end": 4, "negative_start": 3, "negative_end": 3, "positive_lexemes": ["four"], "negative_lexemes": []}, {"tag": "replace", "positive_start": 4, "positive_end": 6, "negative_start": 3, "negative_end": 5, "positive_lexemes": ["giraffes", "with"], "negative_lexemes": ["a", "giraffe"]}, {"tag": "equal", "positive_start": 6, "positive_end": 9, "negative_start": 5, "negative_end": 8, "positive_lexemes": ["grass", "and", "leaves"], "negative_lexemes": ["grass", "and", "leaves"]}]`
- 共同前缀：`[]`
- 正确 contrast hull：`["a", "person", "feeding", "four", "giraffes", "with"]`
- 错误 contrast hull：`["four", "persons", "feeding", "a", "giraffe"]`
- 共同后缀：`["grass", "and", "leaves"]`
- Hull token 覆盖率（正/负/最大）：`[0.6666666666666666, 0.6842105263157895, 0.6842105263157895]`
- 共同前缀模型 token：`[]`
- 正确 hull 模型 token：IDs `[100, 2198, 1270, 382, 350, 5701, 492, 108, 559, 1627, 329, 599]`；text "a person feeding four giraffes with"
- 错误 hull 模型 token：IDs `[105, 1084, 2198, 118, 1270, 382, 350, 299, 492, 108, 559, 1627, 104]`；text "four persons feeding a giraffe"
- 第一轮/第二轮分类：`complex_edit` / `multi_block_local_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 21. `swap_atribute:531`

- 负例类型/范围：`swap_atribute` / `{"canonical": true, "pilot": true, "formal": false, "certifying_formal": false}`
- 原始正描述 1："A desk with two computer monitors, two mice, a cup and a keyboard on it."
- 原始正描述 2："There are two computer monitors, two mice, a cup, and a keyboard on the desk. "
- 原始负描述："A desk with a computer monitor, two mice, two cups and a keyboard on it."
- 规范化正描述 1："a desk with two computer monitors , two mice , a cup and a keyboard on it"
- 规范化正描述 2："there are two computer monitors , two mice , a cup , and a keyboard on the desk"
- 规范化负描述："a desk with a computer monitor , two mice , two cups and a keyboard on it"
- 正描述 1 选择元组：`[8, 18, 3, 0.23529411764705882, 0.1095890410958904]`
- 正描述 2 选择元组：`[17, 35, 7, 0.5555555555555556, 0.3291139240506329]`
- 最终比较正描述：`positive_1` / "A desk with two computer monitors, two mice, a cup and a keyboard on it."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 3, "negative_start": 0, "negative_end": 3, "positive_lexemes": ["a", "desk", "with"], "negative_lexemes": ["a", "desk", "with"]}, {"tag": "replace", "positive_start": 3, "positive_end": 4, "negative_start": 3, "negative_end": 4, "positive_lexemes": ["two"], "negative_lexemes": ["a"]}, {"tag": "equal", "positive_start": 4, "positive_end": 5, "negative_start": 4, "negative_end": 5, "positive_lexemes": ["computer"], "negative_lexemes": ["computer"]}, {"tag": "replace", "positive_start": 5, "positive_end": 6, "negative_start": 5, "negative_end": 6, "positive_lexemes": ["monitors"], "negative_lexemes": ["monitor"]}, {"tag": "equal", "positive_start": 6, "positive_end": 10, "negative_start": 6, "negative_end": 10, "positive_lexemes": [",", "two", "mice", ","], "negative_lexemes": [",", "two", "mice", ","]}, {"tag": "replace", "positive_start": 10, "positive_end": 12, "negative_start": 10, "negative_end": 12, "positive_lexemes": ["a", "cup"], "negative_lexemes": ["two", "cups"]}, {"tag": "equal", "positive_start": 12, "positive_end": 17, "negative_start": 12, "negative_end": 17, "positive_lexemes": ["and", "a", "keyboard", "on", "it"], "negative_lexemes": ["and", "a", "keyboard", "on", "it"]}]`
- 共同前缀：`["a", "desk", "with"]`
- 正确 contrast hull：`["two", "computer", "monitors", ",", "two", "mice", ",", "a", "cup"]`
- 错误 contrast hull：`["a", "computer", "monitor", ",", "two", "mice", ",", "two", "cups"]`
- 共同后缀：`["and", "a", "keyboard", "on", "it"]`
- Hull token 覆盖率（正/负/最大）：`[0.5555555555555556, 0.5714285714285714, 0.5714285714285714]`
- 共同前缀模型 token：`[100, 1453, 110, 599]`
- 正确 hull 模型 token：IDs `[2102, 4818, 4036, 338, 1945, 256, 47, 2102, 351, 1126, 256, 47, 299, 317, 2764]`；text " two computer monitors , two mice , a cup"
- 错误 hull 模型 token：IDs `[299, 4818, 4036, 338, 336, 256, 47, 2102, 351, 1126, 256, 47, 2102, 317, 2764, 118]`；text " a computer monitor , two mice , two cups"
- 第一轮/第二轮分类：`complex_edit` / `multi_block_local_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 22. `swap_atribute:655`

- 负例类型/范围：`swap_atribute` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："Two brown bears swimming in a lake next to green and yellow plants."
- 原始正描述 2："Two brown bears swimming in a lake surrounded by green and yellow plants."
- 原始负描述："Two green/yellow bears swimming in a lake next to brown plants."
- 规范化正描述 1："two brown bears swimming in a lake next to green and yellow plants"
- 规范化正描述 2："two brown bears swimming in a lake surrounded by green and yellow plants"
- 规范化负描述："two green / yellow bears swimming in a lake next to brown plants"
- 正描述 1 选择元组：`[8, 22, 4, 0.46153846153846156, 0.3939393939393939]`
- 正描述 2 选择元组：`[12, 22, 4, 0.6153846153846154, 0.5138888888888888]`
- 最终比较正描述：`positive_1` / "Two brown bears swimming in a lake next to green and yellow plants."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 1, "negative_start": 0, "negative_end": 1, "positive_lexemes": ["two"], "negative_lexemes": ["two"]}, {"tag": "insert", "positive_start": 1, "positive_end": 1, "negative_start": 1, "negative_end": 3, "positive_lexemes": [], "negative_lexemes": ["green", "/"]}, {"tag": "replace", "positive_start": 1, "positive_end": 2, "negative_start": 3, "negative_end": 4, "positive_lexemes": ["brown"], "negative_lexemes": ["yellow"]}, {"tag": "equal", "positive_start": 2, "positive_end": 9, "negative_start": 4, "negative_end": 11, "positive_lexemes": ["bears", "swimming", "in", "a", "lake", "next", "to"], "negative_lexemes": ["bears", "swimming", "in", "a", "lake", "next", "to"]}, {"tag": "delete", "positive_start": 9, "positive_end": 11, "negative_start": 11, "negative_end": 11, "positive_lexemes": ["green", "and"], "negative_lexemes": []}, {"tag": "replace", "positive_start": 11, "positive_end": 12, "negative_start": 11, "negative_end": 12, "positive_lexemes": ["yellow"], "negative_lexemes": ["brown"]}, {"tag": "equal", "positive_start": 12, "positive_end": 13, "negative_start": 12, "negative_end": 13, "positive_lexemes": ["plants"], "negative_lexemes": ["plants"]}]`
- 共同前缀：`["two"]`
- 正确 contrast hull：`["brown", "bears", "swimming", "in", "a", "lake", "next", "to", "green", "and", "yellow"]`
- 错误 contrast hull：`["green", "/", "yellow", "bears", "swimming", "in", "a", "lake", "next", "to", "brown"]`
- 共同后缀：`["plants"]`
- Hull token 覆盖率（正/负/最大）：`[0.8, 0.8, 0.8]`
- 共同前缀模型 token：`[119, 122, 114]`
- 正确 hull 模型 token：IDs `[363, 2079, 113, 600, 2546, 316, 122, 467, 3005, 353, 299, 406, 2434, 4658, 364, 5921, 376, 385, 446, 1030]`；text " brown bears swimming in a lake next to green and yellow"
- 错误 hull 模型 token：IDs `[5921, 1947, 385, 446, 1030, 600, 2546, 316, 122, 467, 3005, 353, 299, 406, 2434, 4658, 364, 363, 2079, 113]`；text " green / yellow bears swimming in a lake next to brown"
- 第一轮/第二轮分类：`complex_edit` / `large_contrast_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；"maximum_hull_token_coverage_above_75_percent"

### 23. `swap_atribute:70`

- 负例类型/范围：`swap_atribute` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A stop sign in front of two buildings on a street."
- 原始正描述 2："A stop sign is positioned in front of two buildings on a street."
- 原始负描述："Two stop signs in front of a building on a street."
- 规范化正描述 1："a stop sign in front of two buildings on a street"
- 规范化正描述 2："a stop sign is positioned in front of two buildings on a street"
- 规范化负描述："two stop signs in front of a building on a street"
- 正描述 1 选择元组：`[8, 16, 3, 0.36363636363636365, 0.16326530612244897]`
- 正描述 2 选择元组：`[10, 18, 4, 0.46153846153846156, 0.31746031746031744]`
- 最终比较正描述：`positive_1` / "A stop sign in front of two buildings on a street."
- 完整 lexeme 编辑块：`[{"tag": "replace", "positive_start": 0, "positive_end": 1, "negative_start": 0, "negative_end": 1, "positive_lexemes": ["a"], "negative_lexemes": ["two"]}, {"tag": "equal", "positive_start": 1, "positive_end": 2, "negative_start": 1, "negative_end": 2, "positive_lexemes": ["stop"], "negative_lexemes": ["stop"]}, {"tag": "replace", "positive_start": 2, "positive_end": 3, "negative_start": 2, "negative_end": 3, "positive_lexemes": ["sign"], "negative_lexemes": ["signs"]}, {"tag": "equal", "positive_start": 3, "positive_end": 6, "negative_start": 3, "negative_end": 6, "positive_lexemes": ["in", "front", "of"], "negative_lexemes": ["in", "front", "of"]}, {"tag": "replace", "positive_start": 6, "positive_end": 8, "negative_start": 6, "negative_end": 8, "positive_lexemes": ["two", "buildings"], "negative_lexemes": ["a", "building"]}, {"tag": "equal", "positive_start": 8, "positive_end": 11, "negative_start": 8, "negative_end": 11, "positive_lexemes": ["on", "a", "street"], "negative_lexemes": ["on", "a", "street"]}]`
- 共同前缀：`[]`
- 正确 contrast hull：`["a", "stop", "sign", "in", "front", "of", "two", "buildings"]`
- 错误 contrast hull：`["two", "stop", "signs", "in", "front", "of", "a", "building"]`
- 共同后缀：`["on", "a", "street"]`
- Hull token 覆盖率（正/负/最大）：`[0.75, 0.7894736842105263, 0.7894736842105263]`
- 共同前缀模型 token：`[]`
- 正确 hull 模型 token：IDs `[100, 580, 1506, 2185, 353, 341, 117, 3856, 354, 2102, 6331, 2557]`；text "a stop sign in front of two buildings"
- 错误 hull 模型 token：IDs `[119, 122, 114, 580, 1506, 2185, 118, 353, 341, 117, 3856, 354, 299, 6331, 350]`；text "two stop signs in front of a building"
- 第一轮/第二轮分类：`complex_edit` / `large_contrast_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；"maximum_hull_token_coverage_above_75_percent"

### 24. `swap_atribute:81`

- 负例类型/范围：`swap_atribute` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A red couch next to a brown chair in a living room."
- 原始正描述 2："The red couch is positioned next to the brown chair in the living room."
- 原始负描述："A brown couch is next to a red chair in a living room."
- 规范化正描述 1："a red couch next to a brown chair in a living room"
- 规范化正描述 2："the red couch is positioned next to the brown chair in the living room"
- 规范化负描述："a brown couch is next to a red chair in a living room"
- 正描述 1 选择元组：`[5, 13, 3, 0.23076923076923078, 0.20754716981132076]`
- 正描述 2 选择元组：`[11, 23, 4, 0.42857142857142855, 0.4]`
- 最终比较正描述：`positive_1` / "A red couch next to a brown chair in a living room."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 1, "negative_start": 0, "negative_end": 1, "positive_lexemes": ["a"], "negative_lexemes": ["a"]}, {"tag": "replace", "positive_start": 1, "positive_end": 2, "negative_start": 1, "negative_end": 2, "positive_lexemes": ["red"], "negative_lexemes": ["brown"]}, {"tag": "equal", "positive_start": 2, "positive_end": 3, "negative_start": 2, "negative_end": 3, "positive_lexemes": ["couch"], "negative_lexemes": ["couch"]}, {"tag": "insert", "positive_start": 3, "positive_end": 3, "negative_start": 3, "negative_end": 4, "positive_lexemes": [], "negative_lexemes": ["is"]}, {"tag": "equal", "positive_start": 3, "positive_end": 6, "negative_start": 4, "negative_end": 7, "positive_lexemes": ["next", "to", "a"], "negative_lexemes": ["next", "to", "a"]}, {"tag": "replace", "positive_start": 6, "positive_end": 7, "negative_start": 7, "negative_end": 8, "positive_lexemes": ["brown"], "negative_lexemes": ["red"]}, {"tag": "equal", "positive_start": 7, "positive_end": 12, "negative_start": 8, "negative_end": 13, "positive_lexemes": ["chair", "in", "a", "living", "room"], "negative_lexemes": ["chair", "in", "a", "living", "room"]}]`
- 共同前缀：`["a"]`
- 正确 contrast hull：`["red", "couch", "next", "to", "a", "brown"]`
- 错误 contrast hull：`["brown", "couch", "is", "next", "to", "a", "red"]`
- 共同后缀：`["chair", "in", "a", "living", "room"]`
- Hull token 覆盖率（正/负/最大）：`[0.5263157894736842, 0.55, 0.55]`
- 共同前缀模型 token：`[100]`
- 正确 hull 模型 token：IDs `[5534, 317, 326, 550, 4658, 364, 299, 363, 2079, 113]`；text " red couch next to a brown"
- 错误 hull 模型 token：IDs `[363, 2079, 113, 317, 326, 550, 395, 4658, 364, 299, 5534]`；text " brown couch is next to a red"
- 第一轮/第二轮分类：`complex_edit` / `multi_block_local_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 25. `swap_object:113`

- 负例类型/范围：`swap_object` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："Donuts in a box and a type of meat on a plate."
- 原始正描述 2："a type of meat is on a plate along with donuts in a box."
- 原始负描述："A type of meat in a box and donuts on a plate."
- 规范化正描述 1："donuts in a box and a type of meat on a plate"
- 规范化正描述 2："a type of meat is on a plate along with donuts in a box"
- 规范化负描述："a type of meat in a box and donuts on a plate"
- 正描述 1 选择元组：`[16, 18, 2, 0.6666666666666666, 0.5777777777777777]`
- 正描述 2 选择元组：`[12, 18, 6, 0.5, 0.4]`
- 最终比较正描述：`positive_2` / "a type of meat is on a plate along with donuts in a box."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 4, "negative_start": 0, "negative_end": 4, "positive_lexemes": ["a", "type", "of", "meat"], "negative_lexemes": ["a", "type", "of", "meat"]}, {"tag": "delete", "positive_start": 4, "positive_end": 5, "negative_start": 4, "negative_end": 4, "positive_lexemes": ["is"], "negative_lexemes": []}, {"tag": "replace", "positive_start": 5, "positive_end": 6, "negative_start": 4, "negative_end": 5, "positive_lexemes": ["on"], "negative_lexemes": ["in"]}, {"tag": "equal", "positive_start": 6, "positive_end": 7, "negative_start": 5, "negative_end": 6, "positive_lexemes": ["a"], "negative_lexemes": ["a"]}, {"tag": "delete", "positive_start": 7, "positive_end": 8, "negative_start": 6, "negative_end": 6, "positive_lexemes": ["plate"], "negative_lexemes": []}, {"tag": "replace", "positive_start": 8, "positive_end": 10, "negative_start": 6, "negative_end": 8, "positive_lexemes": ["along", "with"], "negative_lexemes": ["box", "and"]}, {"tag": "equal", "positive_start": 10, "positive_end": 11, "negative_start": 8, "negative_end": 9, "positive_lexemes": ["donuts"], "negative_lexemes": ["donuts"]}, {"tag": "replace", "positive_start": 11, "positive_end": 12, "negative_start": 9, "negative_end": 10, "positive_lexemes": ["in"], "negative_lexemes": ["on"]}, {"tag": "equal", "positive_start": 12, "positive_end": 13, "negative_start": 10, "negative_end": 11, "positive_lexemes": ["a"], "negative_lexemes": ["a"]}, {"tag": "replace", "positive_start": 13, "positive_end": 14, "negative_start": 11, "negative_end": 12, "positive_lexemes": ["box"], "negative_lexemes": ["plate"]}]`
- 共同前缀：`["a", "type", "of", "meat"]`
- 正确 contrast hull：`["is", "on", "a", "plate", "along", "with", "donuts", "in", "a", "box"]`
- 错误 contrast hull：`["in", "a", "box", "and", "donuts", "on", "a", "plate"]`
- 共同后缀：`[]`
- Hull token 覆盖率（正/负/最大）：`[0.7368421052631579, 0.7058823529411765, 0.7368421052631579]`
- 共同前缀模型 token：`[100, 3217, 354, 765, 314]`
- 正确 hull 模型 token：IDs `[395, 619, 299, 1219, 557, 5782, 599, 2207, 501, 118, 353, 299, 1847, 123]`；text " is on a plate along with donuts in a box"
- 错误 hull 模型 token：IDs `[353, 299, 1847, 123, 376, 2207, 501, 118, 619, 299, 1219, 557]`；text " in a box and donuts on a plate"
- 第一轮/第二轮分类：`complex_edit` / `multi_block_local_hull`
- 自动判断："positive_2_selection_tuple_lexicographically_smaller"；null

### 26. `swap_object:116`

- 负例类型/范围：`swap_object` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："a white mug showing pirate skull and bones and a large knife on a counter top."
- 原始正描述 2："A large knife and a white mug displaying a pirate skull and bones are positioned on a countertop."
- 原始负描述："A large knife showing pirate skull and bones on a counter top next to a white mug."
- 规范化正描述 1："a white mug showing pirate skull and bones and a large knife on a counter top"
- 规范化正描述 2："a large knife and a white mug displaying a pirate skull and bones are positioned on a countertop"
- 规范化负描述："a large knife showing pirate skull and bones on a counter top next to a white mug"
- 正描述 1 选择元组：`[17, 31, 5, 0.5294117647058824, 0.41975308641975306]`
- 正描述 2 选择元组：`[19, 29, 6, 0.7777777777777778, 0.5104166666666666]`
- 最终比较正描述：`positive_1` / "a white mug showing pirate skull and bones and a large knife on a counter top."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 1, "negative_start": 0, "negative_end": 1, "positive_lexemes": ["a"], "negative_lexemes": ["a"]}, {"tag": "replace", "positive_start": 1, "positive_end": 3, "negative_start": 1, "negative_end": 3, "positive_lexemes": ["white", "mug"], "negative_lexemes": ["large", "knife"]}, {"tag": "equal", "positive_start": 3, "positive_end": 8, "negative_start": 3, "negative_end": 8, "positive_lexemes": ["showing", "pirate", "skull", "and", "bones"], "negative_lexemes": ["showing", "pirate", "skull", "and", "bones"]}, {"tag": "replace", "positive_start": 8, "positive_end": 9, "negative_start": 8, "negative_end": 9, "positive_lexemes": ["and"], "negative_lexemes": ["on"]}, {"tag": "equal", "positive_start": 9, "positive_end": 10, "negative_start": 9, "negative_end": 10, "positive_lexemes": ["a"], "negative_lexemes": ["a"]}, {"tag": "insert", "positive_start": 10, "positive_end": 10, "negative_start": 10, "negative_end": 11, "positive_lexemes": [], "negative_lexemes": ["counter"]}, {"tag": "replace", "positive_start": 10, "positive_end": 13, "negative_start": 11, "negative_end": 14, "positive_lexemes": ["large", "knife", "on"], "negative_lexemes": ["top", "next", "to"]}, {"tag": "equal", "positive_start": 13, "positive_end": 14, "negative_start": 14, "negative_end": 15, "positive_lexemes": ["a"], "negative_lexemes": ["a"]}, {"tag": "replace", "positive_start": 14, "positive_end": 16, "negative_start": 15, "negative_end": 17, "positive_lexemes": ["counter", "top"], "negative_lexemes": ["white", "mug"]}]`
- 共同前缀：`["a"]`
- 正确 contrast hull：`["white", "mug", "showing", "pirate", "skull", "and", "bones", "and", "a", "large", "knife", "on", "a", "counter", "top"]`
- 错误 contrast hull：`["large", "knife", "showing", "pirate", "skull", "and", "bones", "on", "a", "counter", "top", "next", "to", "a", "white", "mug"]`
- 共同后缀：`[]`
- Hull token 覆盖率（正/负/最大）：`[0.9629629629629629, 0.9642857142857143, 0.9642857142857143]`
- 共同前缀模型 token：`[100]`
- 正确 hull 模型 token：IDs `[654, 1078, 351, 3304, 5950, 350, 344, 639, 557, 2549, 3800, 376, 363, 310, 329, 376, 299, 2994, 914, 113, 2813, 619, 299, 2320, 311, 2924]`；text " white mug showing pirate skull and bones and a large knife on a counter top"
- 错误 hull 模型 token：IDs `[2994, 914, 113, 2813, 5950, 350, 344, 639, 557, 2549, 3800, 376, 363, 310, 329, 619, 299, 2320, 311, 2924, 4658, 364, 299, 654, 1078, 351, 3304]`；text " large knife showing pirate skull and bones on a counter top next to a white mug"
- 第一轮/第二轮分类：`complex_edit` / `large_contrast_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；"maximum_hull_token_coverage_above_75_percent"

### 27. `swap_object:149`

- 负例类型/范围：`swap_object` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A blue vase with an orange floral patters sits in front of a map."
- 原始正描述 2："A map is positioned behind a blue vase with an orange floral pattern."
- 原始负描述："A map with an orange floral pattern sits in front of a blue vase."
- 规范化正描述 1："a blue vase with an orange floral patters sits in front of a map"
- 规范化正描述 2："a map is positioned behind a blue vase with an orange floral pattern"
- 规范化负描述："a map with an orange floral pattern sits in front of a blue vase"
- 正描述 1 选择元组：`[8, 26, 5, 0.35714285714285715, 0.265625]`
- 正描述 2 选择元组：`[23, 23, 2, 0.8571428571428571, 0.6911764705882353]`
- 最终比较正描述：`positive_1` / "A blue vase with an orange floral patters sits in front of a map."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 1, "negative_start": 0, "negative_end": 1, "positive_lexemes": ["a"], "negative_lexemes": ["a"]}, {"tag": "delete", "positive_start": 1, "positive_end": 2, "negative_start": 1, "negative_end": 1, "positive_lexemes": ["blue"], "negative_lexemes": []}, {"tag": "replace", "positive_start": 2, "positive_end": 3, "negative_start": 1, "negative_end": 2, "positive_lexemes": ["vase"], "negative_lexemes": ["map"]}, {"tag": "equal", "positive_start": 3, "positive_end": 7, "negative_start": 2, "negative_end": 6, "positive_lexemes": ["with", "an", "orange", "floral"], "negative_lexemes": ["with", "an", "orange", "floral"]}, {"tag": "replace", "positive_start": 7, "positive_end": 8, "negative_start": 6, "negative_end": 7, "positive_lexemes": ["patters"], "negative_lexemes": ["pattern"]}, {"tag": "equal", "positive_start": 8, "positive_end": 13, "negative_start": 7, "negative_end": 12, "positive_lexemes": ["sits", "in", "front", "of", "a"], "negative_lexemes": ["sits", "in", "front", "of", "a"]}, {"tag": "insert", "positive_start": 13, "positive_end": 13, "negative_start": 12, "negative_end": 13, "positive_lexemes": [], "negative_lexemes": ["blue"]}, {"tag": "replace", "positive_start": 13, "positive_end": 14, "negative_start": 13, "negative_end": 14, "positive_lexemes": ["map"], "negative_lexemes": ["vase"]}]`
- 共同前缀：`["a"]`
- 正确 contrast hull：`["blue", "vase", "with", "an", "orange", "floral", "patters", "sits", "in", "front", "of", "a", "map"]`
- 错误 contrast hull：`["map", "with", "an", "orange", "floral", "pattern", "sits", "in", "front", "of", "a", "blue", "vase"]`
- 共同后缀：`[]`
- Hull token 覆盖率（正/负/最大）：`[0.9565217391304348, 0.9545454545454546, 0.9565217391304348]`
- 共同前缀模型 token：`[100]`
- 正确 hull 模型 token：IDs `[4300, 603, 812, 599, 346, 522, 1285, 3687, 336, 352, 4195, 4271, 316, 2163, 353, 341, 117, 3856, 354, 299, 1034, 115]`；text " blue vase with an orange floral patters sits in front of a map"
- 错误 hull 模型 token：IDs `[1034, 115, 599, 346, 522, 1285, 3687, 336, 352, 5335, 316, 2163, 353, 341, 117, 3856, 354, 299, 4300, 603, 812]`；text " map with an orange floral pattern sits in front of a blue vase"
- 第一轮/第二轮分类：`complex_edit` / `large_contrast_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；"maximum_hull_token_coverage_above_75_percent"

### 28. `swap_object:150`

- 负例类型/范围：`swap_object` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A school bus waits in traffic behind a car."
- 原始正描述 2："A car is in front of a school bus that is waiting in traffic."
- 原始负描述："A car waits in traffic behind a school bus."
- 规范化正描述 1："a school bus waits in traffic behind a car"
- 规范化正描述 2："a car is in front of a school bus that is waiting in traffic"
- 规范化负描述："a car waits in traffic behind a school bus"
- 正描述 1 选择元组：`[6, 16, 4, 0.4444444444444444, 0.42857142857142855]`
- 正描述 2 选择元组：`[11, 19, 3, 0.5714285714285714, 0.7]`
- 最终比较正描述：`positive_1` / "A school bus waits in traffic behind a car."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 1, "negative_start": 0, "negative_end": 1, "positive_lexemes": ["a"], "negative_lexemes": ["a"]}, {"tag": "delete", "positive_start": 1, "positive_end": 2, "negative_start": 1, "negative_end": 1, "positive_lexemes": ["school"], "negative_lexemes": []}, {"tag": "replace", "positive_start": 2, "positive_end": 3, "negative_start": 1, "negative_end": 2, "positive_lexemes": ["bus"], "negative_lexemes": ["car"]}, {"tag": "equal", "positive_start": 3, "positive_end": 8, "negative_start": 2, "negative_end": 7, "positive_lexemes": ["waits", "in", "traffic", "behind", "a"], "negative_lexemes": ["waits", "in", "traffic", "behind", "a"]}, {"tag": "insert", "positive_start": 8, "positive_end": 8, "negative_start": 7, "negative_end": 8, "positive_lexemes": [], "negative_lexemes": ["school"]}, {"tag": "replace", "positive_start": 8, "positive_end": 9, "negative_start": 8, "negative_end": 9, "positive_lexemes": ["car"], "negative_lexemes": ["bus"]}]`
- 共同前缀：`["a"]`
- 正确 contrast hull：`["school", "bus", "waits", "in", "traffic", "behind", "a", "car"]`
- 错误 contrast hull：`["car", "waits", "in", "traffic", "behind", "a", "school", "bus"]`
- 共同后缀：`[]`
- Hull token 覆盖率（正/负/最大）：`[0.9333333333333333, 0.9333333333333333, 0.9333333333333333]`
- 共同前缀模型 token：`[100]`
- 正确 hull 模型 token：IDs `[316, 4165, 500, 2499, 339, 100, 2163, 353, 1946, 5935, 5237, 916, 299, 3751]`；text " school bus waits in traffic behind a car"
- 错误 hull 模型 token：IDs `[3751, 339, 100, 2163, 353, 1946, 5935, 5237, 916, 299, 316, 4165, 500, 2499]`；text " car waits in traffic behind a school bus"
- 第一轮/第二轮分类：`complex_edit` / `large_contrast_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；"maximum_hull_token_coverage_above_75_percent"

### 29. `swap_object:31`

- 负例类型/范围：`swap_object` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："Two sets of hands are each holding a cell phone while another hand in the background is holding a glass."
- 原始正描述 2："Two sets of hands, each holding a cell phone, are positioned in front of another hand in the background that is holding a glass."
- 原始负描述："Two sets of hands are each holding a glass while another hand in the background is holding a cell phone."
- 规范化正描述 1："two sets of hands are each holding a cell phone while another hand in the background is holding a glass"
- 规范化正描述 2："two sets of hands , each holding a cell phone , are positioned in front of another hand in the background that is holding a glass"
- 规范化负描述："two sets of hands are each holding a glass while another hand in the background is holding a cell phone"
- 正描述 1 选择元组：`[6, 24, 4, 0.2, 0.17475728155339806]`
- 正描述 2 选择元组：`[16, 38, 6, 0.46153846153846156, 0.3953488372093023]`
- 最终比较正描述：`positive_1` / "Two sets of hands are each holding a cell phone while another hand in the background is holding a glass."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 8, "negative_start": 0, "negative_end": 8, "positive_lexemes": ["two", "sets", "of", "hands", "are", "each", "holding", "a"], "negative_lexemes": ["two", "sets", "of", "hands", "are", "each", "holding", "a"]}, {"tag": "delete", "positive_start": 8, "positive_end": 9, "negative_start": 8, "negative_end": 8, "positive_lexemes": ["cell"], "negative_lexemes": []}, {"tag": "replace", "positive_start": 9, "positive_end": 10, "negative_start": 8, "negative_end": 9, "positive_lexemes": ["phone"], "negative_lexemes": ["glass"]}, {"tag": "equal", "positive_start": 10, "positive_end": 19, "negative_start": 9, "negative_end": 18, "positive_lexemes": ["while", "another", "hand", "in", "the", "background", "is", "holding", "a"], "negative_lexemes": ["while", "another", "hand", "in", "the", "background", "is", "holding", "a"]}, {"tag": "insert", "positive_start": 19, "positive_end": 19, "negative_start": 18, "negative_end": 19, "positive_lexemes": [], "negative_lexemes": ["cell"]}, {"tag": "replace", "positive_start": 19, "positive_end": 20, "negative_start": 19, "negative_end": 20, "positive_lexemes": ["glass"], "negative_lexemes": ["phone"]}]`
- 共同前缀：`["two", "sets", "of", "hands", "are", "each", "holding", "a"]`
- 正确 contrast hull：`["cell", "phone", "while", "another", "hand", "in", "the", "background", "is", "holding", "a", "glass"]`
- 错误 contrast hull：`["glass", "while", "another", "hand", "in", "the", "background", "is", "holding", "a", "cell", "phone"]`
- 共同后缀：`[]`
- Hull token 覆盖率（正/负/最大）：`[0.5882352941176471, 0.5882352941176471, 0.5882352941176471]`
- 共同前缀模型 token：`[119, 122, 114, 2139, 118, 354, 3319, 118, 732, 1766, 429, 2569, 350, 299]`
- 正确 hull 模型 token：IDs `[317, 1272, 2001, 1634, 3052, 5467, 3319, 353, 309, 3901, 106, 2383, 395, 429, 2569, 350, 299, 492, 111, 1388]`；text " cell phone while another hand in the background is holding a glass"
- 错误 hull 模型 token：IDs `[492, 111, 1388, 3052, 5467, 3319, 353, 309, 3901, 106, 2383, 395, 429, 2569, 350, 299, 317, 1272, 2001, 1634]`；text " glass while another hand in the background is holding a cell phone"
- 第一轮/第二轮分类：`complex_edit` / `multi_block_local_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 30. `swap_object:83`

- 负例类型/范围：`swap_object` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A person of Asian heritage eating a sandwich at a table with two cups of hot beverages."
- 原始正描述 2："A person belonging to Asian heritage is seated at a table with two cups of hot beverages while eating a sandwich."
- 原始负描述："A person of Asian heritage drinking two cups of hot beverages at a table with a sandwich."
- 规范化正描述 1："a person of asian heritage eating a sandwich at a table with two cups of hot beverages"
- 规范化正描述 2："a person belonging to asian heritage is seated at a table with two cups of hot beverages while eating a sandwich"
- 规范化负描述："a person of asian heritage drinking two cups of hot beverages at a table with a sandwich"
- 正描述 1 选择元组：`[16, 24, 4, 0.6470588235294118, 0.5568181818181818]`
- 正描述 2 选择元组：`[16, 30, 6, 0.5714285714285714, 0.41964285714285715]`
- 最终比较正描述：`positive_1` / "A person of Asian heritage eating a sandwich at a table with two cups of hot beverages."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 5, "negative_start": 0, "negative_end": 5, "positive_lexemes": ["a", "person", "of", "asian", "heritage"], "negative_lexemes": ["a", "person", "of", "asian", "heritage"]}, {"tag": "insert", "positive_start": 5, "positive_end": 5, "negative_start": 5, "negative_end": 8, "positive_lexemes": [], "negative_lexemes": ["drinking", "two", "cups"]}, {"tag": "replace", "positive_start": 5, "positive_end": 8, "negative_start": 8, "negative_end": 11, "positive_lexemes": ["eating", "a", "sandwich"], "negative_lexemes": ["of", "hot", "beverages"]}, {"tag": "equal", "positive_start": 8, "positive_end": 12, "negative_start": 11, "negative_end": 15, "positive_lexemes": ["at", "a", "table", "with"], "negative_lexemes": ["at", "a", "table", "with"]}, {"tag": "delete", "positive_start": 12, "positive_end": 15, "negative_start": 15, "negative_end": 15, "positive_lexemes": ["two", "cups", "of"], "negative_lexemes": []}, {"tag": "replace", "positive_start": 15, "positive_end": 17, "negative_start": 15, "negative_end": 17, "positive_lexemes": ["hot", "beverages"], "negative_lexemes": ["a", "sandwich"]}]`
- 共同前缀：`["a", "person", "of", "asian", "heritage"]`
- 正确 contrast hull：`["eating", "a", "sandwich", "at", "a", "table", "with", "two", "cups", "of", "hot", "beverages"]`
- 错误 contrast hull：`["drinking", "two", "cups", "of", "hot", "beverages", "at", "a", "table", "with", "a", "sandwich"]`
- 共同后缀：`[]`
- Hull token 覆盖率（正/负/最大）：`[0.7241379310344828, 0.7333333333333333, 0.7333333333333333]`
- 共同前缀模型 token：`[100, 2198, 354, 523, 2422, 582, 2157, 834]`
- 正确 hull 模型 token：IDs `[413, 1807, 299, 316, 728, 122, 948, 1248, 299, 2630, 599, 2102, 317, 2764, 118, 354, 429, 593, 600, 652, 2455]`；text " eating a sandwich at a table with two cups of hot beverages"
- 错误 hull 模型 token：IDs `[5893, 301, 1237, 2102, 317, 2764, 118, 354, 429, 593, 600, 652, 2455, 1248, 299, 2630, 599, 299, 316, 728, 122, 948]`；text " drinking two cups of hot beverages at a table with a sandwich"
- 第一轮/第二轮分类：`complex_edit` / `multi_block_local_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

## Hull 覆盖 50%–75%

候选 `593` 条，本节抽取 `30` 条。

### 1. `replace_attribute:328`

- 负例类型/范围：`replace_attribute` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A person cooking on an old fashioned stove."
- 原始正描述 2："A person is cooking on a vintage stove."
- 原始负描述："A person cooking on a modern stove."
- 规范化正描述 1："a person cooking on an old fashioned stove"
- 规范化正描述 2："a person is cooking on a vintage stove"
- 规范化负描述："a person cooking on a modern stove"
- 正描述 1 选择元组：`[5, 5, 2, 0.375, 0.2857142857142857]`
- 正描述 2 选择元组：`[3, 9, 2, 0.25, 0.2631578947368421]`
- 最终比较正描述：`positive_2` / "A person is cooking on a vintage stove."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 2, "negative_start": 0, "negative_end": 2, "positive_lexemes": ["a", "person"], "negative_lexemes": ["a", "person"]}, {"tag": "delete", "positive_start": 2, "positive_end": 3, "negative_start": 2, "negative_end": 2, "positive_lexemes": ["is"], "negative_lexemes": []}, {"tag": "equal", "positive_start": 3, "positive_end": 6, "negative_start": 2, "negative_end": 5, "positive_lexemes": ["cooking", "on", "a"], "negative_lexemes": ["cooking", "on", "a"]}, {"tag": "replace", "positive_start": 6, "positive_end": 7, "negative_start": 5, "negative_end": 6, "positive_lexemes": ["vintage"], "negative_lexemes": ["modern"]}, {"tag": "equal", "positive_start": 7, "positive_end": 8, "negative_start": 6, "negative_end": 7, "positive_lexemes": ["stove"], "negative_lexemes": ["stove"]}]`
- 共同前缀：`["a", "person"]`
- 正确 contrast hull：`["is", "cooking", "on", "a", "vintage"]`
- 错误 contrast hull：`["cooking", "on", "a", "modern"]`
- 共同后缀：`["stove"]`
- Hull token 覆盖率（正/负/最大）：`[0.6923076923076923, 0.6, 0.6923076923076923]`
- 共同前缀模型 token：`[100, 2198]`
- 正确 hull 模型 token：IDs `[395, 317, 824, 1237, 619, 299, 603, 806, 834]`；text " is cooking on a vintage"
- 错误 hull 模型 token：IDs `[317, 824, 1237, 619, 299, 6057]`；text " cooking on a modern"
- 第一轮/第二轮分类：`complex_edit` / `multi_block_local_hull`
- 自动判断："positive_2_selection_tuple_lexicographically_smaller"；null

### 2. `replace_attribute:759`

- 负例类型/范围：`replace_attribute` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："Several people on surfboards who are riding a wave."
- 原始正描述 2："Several people riding a wave on their surfboards."
- 原始负描述："A single person on a surfboard who is riding a wave."
- 规范化正描述 1："several people on surfboards who are riding a wave"
- 规范化正描述 2："several people riding a wave on their surfboards"
- 规范化负描述："a single person on a surfboard who is riding a wave"
- 正描述 1 选择元组：`[10, 14, 5, 0.5454545454545454, 0.3333333333333333]`
- 正描述 2 选择元组：`[17, 19, 4, 0.9090909090909091, 0.7843137254901961]`
- 最终比较正描述：`positive_1` / "Several people on surfboards who are riding a wave."
- 完整 lexeme 编辑块：`[{"tag": "insert", "positive_start": 0, "positive_end": 0, "negative_start": 0, "negative_end": 1, "positive_lexemes": [], "negative_lexemes": ["a"]}, {"tag": "replace", "positive_start": 0, "positive_end": 2, "negative_start": 1, "negative_end": 3, "positive_lexemes": ["several", "people"], "negative_lexemes": ["single", "person"]}, {"tag": "equal", "positive_start": 2, "positive_end": 3, "negative_start": 3, "negative_end": 4, "positive_lexemes": ["on"], "negative_lexemes": ["on"]}, {"tag": "insert", "positive_start": 3, "positive_end": 3, "negative_start": 4, "negative_end": 5, "positive_lexemes": [], "negative_lexemes": ["a"]}, {"tag": "replace", "positive_start": 3, "positive_end": 4, "negative_start": 5, "negative_end": 6, "positive_lexemes": ["surfboards"], "negative_lexemes": ["surfboard"]}, {"tag": "equal", "positive_start": 4, "positive_end": 5, "negative_start": 6, "negative_end": 7, "positive_lexemes": ["who"], "negative_lexemes": ["who"]}, {"tag": "replace", "positive_start": 5, "positive_end": 6, "negative_start": 7, "negative_end": 8, "positive_lexemes": ["are"], "negative_lexemes": ["is"]}, {"tag": "equal", "positive_start": 6, "positive_end": 9, "negative_start": 8, "negative_end": 11, "positive_lexemes": ["riding", "a", "wave"], "negative_lexemes": ["riding", "a", "wave"]}]`
- 共同前缀：`[]`
- 正确 contrast hull：`["several", "people", "on", "surfboards", "who", "are"]`
- 错误 contrast hull：`["a", "single", "person", "on", "a", "surfboard", "who", "is"]`
- 共同后缀：`["riding", "a", "wave"]`
- Hull token 覆盖率（正/负/最大）：`[0.6842105263157895, 0.6666666666666666, 0.6842105263157895]`
- 共同前缀模型 token：`[]`
- 正确 hull 模型 token：IDs `[573, 652, 352, 2975, 619, 3946, 105, 101, 114, 1433, 118, 2109, 732]`；text "several people on surfboards who are"
- 错误 hull 模型 token：IDs `[100, 4486, 2198, 619, 299, 3946, 105, 101, 114, 1433, 2109, 395]`；text "a single person on a surfboard who is"
- 第一轮/第二轮分类：`complex_edit` / `multi_block_local_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 3. `replace_object:1220`

- 负例类型/范围：`replace_object` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A passenger jet is flying over some trees."
- 原始正描述 2："The trees are positioned below a passenger jet that is flying over them."
- 原始负描述："A hot air balloon is floating over some trees."
- 规范化正描述 1："a passenger jet is flying over some trees"
- 规范化正描述 2："the trees are positioned below a passenger jet that is flying over them"
- 规范化负描述："a hot air balloon is floating over some trees"
- 正描述 1 选择元组：`[7, 9, 3, 0.4444444444444444, 0.4]`
- 正描述 2 选择元组：`[16, 22, 5, 0.8461538461538461, 0.7464788732394366]`
- 最终比较正描述：`positive_1` / "A passenger jet is flying over some trees."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 1, "negative_start": 0, "negative_end": 1, "positive_lexemes": ["a"], "negative_lexemes": ["a"]}, {"tag": "insert", "positive_start": 1, "positive_end": 1, "negative_start": 1, "negative_end": 2, "positive_lexemes": [], "negative_lexemes": ["hot"]}, {"tag": "replace", "positive_start": 1, "positive_end": 3, "negative_start": 2, "negative_end": 4, "positive_lexemes": ["passenger", "jet"], "negative_lexemes": ["air", "balloon"]}, {"tag": "equal", "positive_start": 3, "positive_end": 4, "negative_start": 4, "negative_end": 5, "positive_lexemes": ["is"], "negative_lexemes": ["is"]}, {"tag": "replace", "positive_start": 4, "positive_end": 5, "negative_start": 5, "negative_end": 6, "positive_lexemes": ["flying"], "negative_lexemes": ["floating"]}, {"tag": "equal", "positive_start": 5, "positive_end": 8, "negative_start": 6, "negative_end": 9, "positive_lexemes": ["over", "some", "trees"], "negative_lexemes": ["over", "some", "trees"]}]`
- 共同前缀：`["a"]`
- 正确 contrast hull：`["passenger", "jet", "is", "flying"]`
- 错误 contrast hull：`["hot", "air", "balloon", "is", "floating"]`
- 共同后缀：`["over", "some", "trees"]`
- Hull token 覆盖率（正/负/最大）：`[0.6428571428571429, 0.6666666666666666, 0.6666666666666666]`
- 共同前缀模型 token：`[100]`
- 正确 hull 模型 token：IDs `[3241, 1979, 311, 1315, 439, 395, 341, 542, 350]`；text " passenger jet is flying"
- 错误 hull 模型 token：IDs `[429, 593, 3980, 363, 352, 722, 310, 395, 5796, 1807]`；text " hot air balloon is floating"
- 第一轮/第二轮分类：`complex_edit` / `multi_block_local_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 4. `replace_object:244`

- 负例类型/范围：`replace_object` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："African animals placidly grazing in a park enclosure."
- 原始正描述 2："African animals are in a park enclosure grazing placidly."
- 原始负描述："Birds chirping in a park enclosure."
- 规范化正描述 1："african animals placidly grazing in a park enclosure"
- 规范化正描述 2："african animals are in a park enclosure grazing placidly"
- 规范化负描述："birds chirping in a park enclosure"
- 正描述 1 选择元组：`[6, 6, 2, 0.5, 0.46153846153846156]`
- 正描述 2 选择元组：`[7, 15, 3, 0.5555555555555556, 0.5892857142857143]`
- 最终比较正描述：`positive_1` / "African animals placidly grazing in a park enclosure."
- 完整 lexeme 编辑块：`[{"tag": "delete", "positive_start": 0, "positive_end": 2, "negative_start": 0, "negative_end": 0, "positive_lexemes": ["african", "animals"], "negative_lexemes": []}, {"tag": "replace", "positive_start": 2, "positive_end": 4, "negative_start": 0, "negative_end": 2, "positive_lexemes": ["placidly", "grazing"], "negative_lexemes": ["birds", "chirping"]}, {"tag": "equal", "positive_start": 4, "positive_end": 8, "negative_start": 2, "negative_end": 6, "positive_lexemes": ["in", "a", "park", "enclosure"], "negative_lexemes": ["in", "a", "park", "enclosure"]}]`
- 共同前缀：`[]`
- 正确 contrast hull：`["african", "animals", "placidly", "grazing"]`
- 错误 contrast hull：`["birds", "chirping"]`
- 共同后缀：`["in", "a", "park", "enclosure"]`
- Hull token 覆盖率（正/负/最大）：`[0.6190476190476191, 0.4666666666666667, 0.6190476190476191]`
- 共同前缀模型 token：`[]`
- 正确 hull 模型 token：IDs `[4249, 3069, 325, 346, 2740, 118, 1219, 1545, 460, 542, 5528, 125, 350]`；text "african animals placidly grazing"
- 错误 hull 模型 token：IDs `[101, 639, 1881, 890, 639, 115, 350]`；text "birds chirping"
- 第一轮/第二轮分类：`unique_alignment` / `multi_block_local_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 5. `replace_object:285`

- 负例类型/范围：`replace_object` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": false}`
- 原始正描述 1："A black and brown dog wearing a chain around it's neck."
- 原始正描述 2："A dog with a black and brown coat and a chain around its neck."
- 原始负描述："A black and brown parrot wearing a chain around its neck."
- 规范化正描述 1："a black and brown dog wearing a chain around it's neck"
- 规范化正描述 2："a dog with a black and brown coat and a chain around its neck"
- 规范化负描述："a black and brown parrot wearing a chain around its neck"
- 正描述 1 选择元组：`[4, 12, 2, 0.18181818181818182, 0.10714285714285714]`
- 正描述 2 选择元组：`[7, 15, 2, 0.35714285714285715, 0.3442622950819672]`
- 最终比较正描述：`positive_1` / "A black and brown dog wearing a chain around it's neck."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 4, "negative_start": 0, "negative_end": 4, "positive_lexemes": ["a", "black", "and", "brown"], "negative_lexemes": ["a", "black", "and", "brown"]}, {"tag": "replace", "positive_start": 4, "positive_end": 5, "negative_start": 4, "negative_end": 5, "positive_lexemes": ["dog"], "negative_lexemes": ["parrot"]}, {"tag": "equal", "positive_start": 5, "positive_end": 9, "negative_start": 5, "negative_end": 9, "positive_lexemes": ["wearing", "a", "chain", "around"], "negative_lexemes": ["wearing", "a", "chain", "around"]}, {"tag": "replace", "positive_start": 9, "positive_end": 10, "negative_start": 9, "negative_end": 10, "positive_lexemes": ["it's"], "negative_lexemes": ["its"]}, {"tag": "equal", "positive_start": 10, "positive_end": 11, "negative_start": 10, "negative_end": 11, "positive_lexemes": ["neck"], "negative_lexemes": ["neck"]}]`
- 共同前缀：`["a", "black", "and", "brown"]`
- 正确 contrast hull：`["dog", "wearing", "a", "chain", "around", "it's"]`
- 错误 contrast hull：`["parrot", "wearing", "a", "chain", "around", "its"]`
- 共同后缀：`["neck"]`
- Hull token 覆盖率（正/负/最大）：`[0.55, 0.55, 0.55]`
- 共同前缀模型 token：`[100, 2597, 1637, 376, 363, 2079, 113]`
- 正确 hull 模型 token：IDs `[1041, 106, 796, 370, 350, 299, 890, 740, 3364, 563, 628]`；text " dog wearing a chain around it's"
- 错误 hull 模型 token：IDs `[2655, 393, 119, 796, 370, 350, 299, 890, 740, 3364, 1342]`；text " parrot wearing a chain around its"
- 第一轮/第二轮分类：`complex_edit` / `multi_block_local_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 6. `replace_object:317`

- 负例类型/范围：`replace_object` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A man standing on a street with a umbrella."
- 原始正描述 2："A man with an umbrella is standing on the street."
- 原始负描述："A woman standing on a street with an umbrella."
- 规范化正描述 1："a man standing on a street with a umbrella"
- 规范化正描述 2："a man with an umbrella is standing on the street"
- 规范化负描述："a woman standing on a street with an umbrella"
- 正描述 1 选择元组：`[4, 14, 2, 0.2222222222222222, 0.06666666666666667]`
- 正描述 2 选择元组：`[17, 17, 2, 0.9, 0.7083333333333334]`
- 最终比较正描述：`positive_1` / "A man standing on a street with a umbrella."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 1, "negative_start": 0, "negative_end": 1, "positive_lexemes": ["a"], "negative_lexemes": ["a"]}, {"tag": "replace", "positive_start": 1, "positive_end": 2, "negative_start": 1, "negative_end": 2, "positive_lexemes": ["man"], "negative_lexemes": ["woman"]}, {"tag": "equal", "positive_start": 2, "positive_end": 7, "negative_start": 2, "negative_end": 7, "positive_lexemes": ["standing", "on", "a", "street", "with"], "negative_lexemes": ["standing", "on", "a", "street", "with"]}, {"tag": "replace", "positive_start": 7, "positive_end": 8, "negative_start": 7, "negative_end": 8, "positive_lexemes": ["a"], "negative_lexemes": ["an"]}, {"tag": "equal", "positive_start": 8, "positive_end": 9, "negative_start": 8, "negative_end": 9, "positive_lexemes": ["umbrella"], "negative_lexemes": ["umbrella"]}]`
- 共同前缀：`["a"]`
- 正确 contrast hull：`["man", "standing", "on", "a", "street", "with", "a"]`
- 错误 contrast hull：`["woman", "standing", "on", "a", "street", "with", "an"]`
- 共同后缀：`["umbrella"]`
- Hull token 覆盖率（正/负/最大）：`[0.6, 0.6470588235294118, 0.6470588235294118]`
- 共同前缀模型 token：`[100]`
- 正确 hull 模型 token：IDs `[1672, 2823, 350, 619, 299, 5941, 439, 599, 299]`；text " man standing on a street with a"
- 错误 hull 模型 token：IDs `[339, 444, 325, 2823, 350, 619, 299, 5941, 439, 599, 346]`；text " woman standing on a street with an"
- 第一轮/第二轮分类：`complex_edit` / `multi_block_local_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 7. `replace_object:398`

- 负例类型/范围：`replace_object` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："An elephant is walking through the green shrubs."
- 原始正描述 2："The green shrubs are being walked through by an elephant."
- 原始负描述："A gazelle is running through the green shrubs."
- 规范化正描述 1："an elephant is walking through the green shrubs"
- 规范化正描述 2："the green shrubs are being walked through by an elephant"
- 规范化负描述："a gazelle is running through the green shrubs"
- 正描述 1 选择元组：`[6, 8, 2, 0.375, 0.2765957446808511]`
- 正描述 2 选择元组：`[16, 18, 3, 0.9, 0.6607142857142857]`
- 最终比较正描述：`positive_1` / "An elephant is walking through the green shrubs."
- 完整 lexeme 编辑块：`[{"tag": "replace", "positive_start": 0, "positive_end": 2, "negative_start": 0, "negative_end": 2, "positive_lexemes": ["an", "elephant"], "negative_lexemes": ["a", "gazelle"]}, {"tag": "equal", "positive_start": 2, "positive_end": 3, "negative_start": 2, "negative_end": 3, "positive_lexemes": ["is"], "negative_lexemes": ["is"]}, {"tag": "replace", "positive_start": 3, "positive_end": 4, "negative_start": 3, "negative_end": 4, "positive_lexemes": ["walking"], "negative_lexemes": ["running"]}, {"tag": "equal", "positive_start": 4, "positive_end": 8, "negative_start": 4, "negative_end": 8, "positive_lexemes": ["through", "the", "green", "shrubs"], "negative_lexemes": ["through", "the", "green", "shrubs"]}]`
- 共同前缀：`[]`
- 正确 contrast hull：`["an", "elephant", "is", "walking"]`
- 错误 contrast hull：`["a", "gazelle", "is", "running"]`
- 共同后缀：`["through", "the", "green", "shrubs"]`
- Hull token 覆盖率（正/负/最大）：`[0.5333333333333333, 0.5625, 0.5625]`
- 共同前缀模型 token：`[]`
- 正确 hull 模型 token：IDs `[325, 1905, 1601, 811, 395, 339, 352, 1237]`；text "an elephant is walking"
- 错误 hull 模型 token：IDs `[100, 492, 100, 125, 446, 361, 395, 3161, 1795]`；text "a gazelle is running"
- 第一轮/第二轮分类：`complex_edit` / `multi_block_local_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 8. `replace_relation:1005`

- 负例类型/范围：`replace_relation` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A red stop sign with paper with writing on top of it."
- 原始正描述 2："Paper with writing is placed on top of a red stop sign."
- 原始负描述："A red stop sign without paper is standing there."
- 规范化正描述 1："a red stop sign with paper with writing on top of it"
- 规范化正描述 2："paper with writing is placed on top of a red stop sign"
- 规范化负描述："a red stop sign without paper is standing there"
- 正描述 1 选择元组：`[11, 13, 3, 0.5833333333333334, 0.4230769230769231]`
- 正描述 2 选择元组：`[21, 21, 2, 1.0, 0.8148148148148148]`
- 最终比较正描述：`positive_1` / "A red stop sign with paper with writing on top of it."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 4, "negative_start": 0, "negative_end": 4, "positive_lexemes": ["a", "red", "stop", "sign"], "negative_lexemes": ["a", "red", "stop", "sign"]}, {"tag": "replace", "positive_start": 4, "positive_end": 5, "negative_start": 4, "negative_end": 5, "positive_lexemes": ["with"], "negative_lexemes": ["without"]}, {"tag": "equal", "positive_start": 5, "positive_end": 6, "negative_start": 5, "negative_end": 6, "positive_lexemes": ["paper"], "negative_lexemes": ["paper"]}, {"tag": "delete", "positive_start": 6, "positive_end": 9, "negative_start": 6, "negative_end": 6, "positive_lexemes": ["with", "writing", "on"], "negative_lexemes": []}, {"tag": "replace", "positive_start": 9, "positive_end": 12, "negative_start": 6, "negative_end": 9, "positive_lexemes": ["top", "of", "it"], "negative_lexemes": ["is", "standing", "there"]}]`
- 共同前缀：`["a", "red", "stop", "sign"]`
- 正确 contrast hull：`["with", "paper", "with", "writing", "on", "top", "of", "it"]`
- 错误 contrast hull：`["without", "paper", "is", "standing", "there"]`
- 共同后缀：`[]`
- Hull token 覆盖率（正/负/最大）：`[0.6428571428571429, 0.5833333333333334, 0.6428571428571429]`
- 共同前缀模型 token：`[100, 5534, 580, 1506, 2185]`
- 正确 hull 模型 token：IDs `[599, 5914, 1067, 599, 5506, 619, 2924, 354, 563]`；text " with paper with writing on top of it"
- 错误 hull 模型 token：IDs `[4007, 5914, 1067, 395, 2823, 350, 1975]`；text " without paper is standing there"
- 第一轮/第二轮分类：`complex_edit` / `multi_block_local_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 9. `replace_relation:1296`

- 负例类型/范围：`replace_relation` / `{"canonical": true, "pilot": true, "formal": false, "certifying_formal": false}`
- 原始正描述 1："The person is riding a bike led by several dogs."
- 原始正描述 2："Numerous dogs are leading a bike that a person is riding."
- 原始负描述："The person is walking a group of dogs."
- 规范化正描述 1："the person is riding a bike led by several dogs"
- 规范化正描述 2："numerous dogs are leading a bike that a person is riding"
- 规范化负描述："the person is walking a group of dogs"
- 正描述 1 选择元组：`[8, 10, 3, 0.5, 0.46808510638297873]`
- 正描述 2 选择元组：`[17, 19, 3, 0.9090909090909091, 0.75]`
- 最终比较正描述：`positive_1` / "The person is riding a bike led by several dogs."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 3, "negative_start": 0, "negative_end": 3, "positive_lexemes": ["the", "person", "is"], "negative_lexemes": ["the", "person", "is"]}, {"tag": "replace", "positive_start": 3, "positive_end": 4, "negative_start": 3, "negative_end": 4, "positive_lexemes": ["riding"], "negative_lexemes": ["walking"]}, {"tag": "equal", "positive_start": 4, "positive_end": 5, "negative_start": 4, "negative_end": 5, "positive_lexemes": ["a"], "negative_lexemes": ["a"]}, {"tag": "delete", "positive_start": 5, "positive_end": 7, "negative_start": 5, "negative_end": 5, "positive_lexemes": ["bike", "led"], "negative_lexemes": []}, {"tag": "replace", "positive_start": 7, "positive_end": 9, "negative_start": 5, "negative_end": 7, "positive_lexemes": ["by", "several"], "negative_lexemes": ["group", "of"]}, {"tag": "equal", "positive_start": 9, "positive_end": 10, "negative_start": 7, "negative_end": 8, "positive_lexemes": ["dogs"], "negative_lexemes": ["dogs"]}]`
- 共同前缀：`["the", "person", "is"]`
- 正确 contrast hull：`["riding", "a", "bike", "led", "by", "several"]`
- 错误 contrast hull：`["walking", "a", "group", "of"]`
- 共同后缀：`["dogs"]`
- Hull token 覆盖率（正/负/最大）：`[0.6666666666666666, 0.5454545454545454, 0.6666666666666666]`
- 共同前缀模型 token：`[4345, 2198, 395]`
- 正确 hull 模型 token：IDs `[757, 460, 350, 299, 363, 1024, 848, 103, 769, 4920]`；text " riding a bike led by several"
- 错误 hull 模型 token：IDs `[339, 352, 1237, 299, 4592, 354]`；text " walking a group of"
- 第一轮/第二轮分类：`complex_edit` / `multi_block_local_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 10. `replace_relation:237`

- 负例类型/范围：`replace_relation` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A person holding a smart device in their left hand."
- 原始正描述 2："A smart device is held in the left hand of a person"
- 原始负描述："A person dropping a smart device from their left hand."
- 规范化正描述 1："a person holding a smart device in their left hand"
- 规范化正描述 2："a smart device is held in the left hand of a person"
- 规范化负描述："a person dropping a smart device from their left hand"
- 正描述 1 选择元组：`[4, 10, 2, 0.2, 0.1509433962264151]`
- 正描述 2 选择元组：`[16, 20, 3, 0.8333333333333334, 0.7735849056603774]`
- 最终比较正描述：`positive_1` / "A person holding a smart device in their left hand."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 2, "negative_start": 0, "negative_end": 2, "positive_lexemes": ["a", "person"], "negative_lexemes": ["a", "person"]}, {"tag": "replace", "positive_start": 2, "positive_end": 3, "negative_start": 2, "negative_end": 3, "positive_lexemes": ["holding"], "negative_lexemes": ["dropping"]}, {"tag": "equal", "positive_start": 3, "positive_end": 6, "negative_start": 3, "negative_end": 6, "positive_lexemes": ["a", "smart", "device"], "negative_lexemes": ["a", "smart", "device"]}, {"tag": "replace", "positive_start": 6, "positive_end": 7, "negative_start": 6, "negative_end": 7, "positive_lexemes": ["in"], "negative_lexemes": ["from"]}, {"tag": "equal", "positive_start": 7, "positive_end": 10, "negative_start": 7, "negative_end": 10, "positive_lexemes": ["their", "left", "hand"], "negative_lexemes": ["their", "left", "hand"]}]`
- 共同前缀：`["a", "person"]`
- 正确 contrast hull：`["holding", "a", "smart", "device", "in"]`
- 错误 contrast hull：`["dropping", "a", "smart", "device", "from"]`
- 共同后缀：`["their", "left", "hand"]`
- Hull token 覆盖率（正/负/最大）：`[0.6428571428571429, 0.6666666666666666, 0.6666666666666666]`
- 共同前缀模型 token：`[100, 2198]`
- 正确 hull 模型 token：IDs `[429, 2569, 350, 299, 2589, 913, 5130, 1126, 353]`；text " holding a smart device in"
- 错误 hull 模型 token：IDs `[373, 393, 737, 350, 299, 2589, 913, 5130, 1126, 961]`；text " dropping a smart device from"
- 第一轮/第二轮分类：`complex_edit` / `multi_block_local_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 11. `replace_relation:319`

- 负例类型/范围：`replace_relation` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": false}`
- 原始正描述 1："Two young women are washing two motorcycles with hoses."
- 原始正描述 2："Two motorcycles is being washed by two women with hoses."
- 原始负描述："Two young women are waxing two motorcycles with cloths."
- 规范化正描述 1："two young women are washing two motorcycles with hoses"
- 规范化正描述 2："two motorcycles is being washed by two women with hoses"
- 规范化负描述："two young women are waxing two motorcycles with cloths"
- 正描述 1 选择元组：`[4, 10, 2, 0.2222222222222222, 0.1111111111111111]`
- 正描述 2 选择元组：`[13, 17, 4, 0.7, 0.6363636363636364]`
- 最终比较正描述：`positive_1` / "Two young women are washing two motorcycles with hoses."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 4, "negative_start": 0, "negative_end": 4, "positive_lexemes": ["two", "young", "women", "are"], "negative_lexemes": ["two", "young", "women", "are"]}, {"tag": "replace", "positive_start": 4, "positive_end": 5, "negative_start": 4, "negative_end": 5, "positive_lexemes": ["washing"], "negative_lexemes": ["waxing"]}, {"tag": "equal", "positive_start": 5, "positive_end": 8, "negative_start": 5, "negative_end": 8, "positive_lexemes": ["two", "motorcycles", "with"], "negative_lexemes": ["two", "motorcycles", "with"]}, {"tag": "replace", "positive_start": 8, "positive_end": 9, "negative_start": 8, "negative_end": 9, "positive_lexemes": ["hoses"], "negative_lexemes": ["cloths"]}]`
- 共同前缀：`["two", "young", "women", "are"]`
- 正确 contrast hull：`["washing", "two", "motorcycles", "with", "hoses"]`
- 错误 contrast hull：`["waxing", "two", "motorcycles", "with", "cloths"]`
- 共同后缀：`[]`
- Hull token 覆盖率（正/负/最大）：`[0.6086956521739131, 0.6086956521739131, 0.6086956521739131]`
- 共同前缀模型 token：`[119, 122, 114, 401, 1685, 339, 444, 327, 732]`
- 正确 hull 模型 token：IDs `[1111, 107, 350, 2102, 351, 593, 336, 2863, 1110, 329, 599, 429, 1312, 329]`；text " washing two motorcycles with hoses"
- 错误 hull 模型 token：IDs `[339, 2521, 350, 2102, 351, 593, 336, 2863, 1110, 329, 599, 4414, 495, 118]`；text " waxing two motorcycles with cloths"
- 第一轮/第二轮分类：`complex_edit` / `multi_block_local_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 12. `replace_relation:558`

- 负例类型/范围：`replace_relation` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A sheep stands idle at the edge of a field"
- 原始正描述 2："The edge of a field is idly stood at by a sheep."
- 原始负描述："A sheep is lying down in the middle of a field."
- 规范化正描述 1："a sheep stands idle at the edge of a field"
- 规范化正描述 2："the edge of a field is idly stood at by a sheep"
- 规范化负描述："a sheep is lying down in the middle of a field"
- 正描述 1 选择元组：`[9, 11, 3, 0.45454545454545453, 0.3695652173913043]`
- 正描述 2 选择元组：`[21, 23, 3, 0.9166666666666666, 0.7446808510638298]`
- 最终比较正描述：`positive_1` / "A sheep stands idle at the edge of a field"
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 2, "negative_start": 0, "negative_end": 2, "positive_lexemes": ["a", "sheep"], "negative_lexemes": ["a", "sheep"]}, {"tag": "insert", "positive_start": 2, "positive_end": 2, "negative_start": 2, "negative_end": 3, "positive_lexemes": [], "negative_lexemes": ["is"]}, {"tag": "replace", "positive_start": 2, "positive_end": 5, "negative_start": 3, "negative_end": 6, "positive_lexemes": ["stands", "idle", "at"], "negative_lexemes": ["lying", "down", "in"]}, {"tag": "equal", "positive_start": 5, "positive_end": 6, "negative_start": 6, "negative_end": 7, "positive_lexemes": ["the"], "negative_lexemes": ["the"]}, {"tag": "replace", "positive_start": 6, "positive_end": 7, "negative_start": 7, "negative_end": 8, "positive_lexemes": ["edge"], "negative_lexemes": ["middle"]}, {"tag": "equal", "positive_start": 7, "positive_end": 10, "negative_start": 8, "negative_end": 11, "positive_lexemes": ["of", "a", "field"], "negative_lexemes": ["of", "a", "field"]}]`
- 共同前缀：`["a", "sheep"]`
- 正确 contrast hull：`["stands", "idle", "at", "the", "edge"]`
- 错误 contrast hull：`["is", "lying", "down", "in", "the", "middle"]`
- 共同后缀：`["of", "a", "field"]`
- Hull token 覆盖率（正/负/最大）：`[0.6, 0.625, 0.625]`
- 共同前缀模型 token：`[100, 3191, 1522]`
- 正确 hull 模型 token：IDs `[2823, 118, 256, 460, 361, 1248, 309, 4452, 583]`；text " stands idle at the edge"
- 错误 hull 模型 token：IDs `[395, 406, 124, 350, 4076, 353, 309, 351, 5032, 361]`；text " is lying down in the middle"
- 第一轮/第二轮分类：`complex_edit` / `multi_block_local_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 13. `replace_relation:628`

- 负例类型/范围：`replace_relation` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A giraffe sticking his head in the sky next to a tree."
- 原始正描述 2："A giraffe is positioned next to a tree with his head sticking upwards into the sky."
- 原始负描述："A giraffe with the head low in the sky away from a tree."
- 规范化正描述 1："a giraffe sticking his head in the sky next to a tree"
- 规范化正描述 2："a giraffe is positioned next to a tree with his head sticking upwards into the sky"
- 规范化负描述："a giraffe with the head low in the sky away from a tree"
- 正描述 1 选择元组：`[9, 17, 3, 0.38461538461538464, 0.38181818181818183]`
- 正描述 2 选择元组：`[25, 25, 2, 0.875, 0.6341463414634146]`
- 最终比较正描述：`positive_1` / "A giraffe sticking his head in the sky next to a tree."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 2, "negative_start": 0, "negative_end": 2, "positive_lexemes": ["a", "giraffe"], "negative_lexemes": ["a", "giraffe"]}, {"tag": "replace", "positive_start": 2, "positive_end": 4, "negative_start": 2, "negative_end": 4, "positive_lexemes": ["sticking", "his"], "negative_lexemes": ["with", "the"]}, {"tag": "equal", "positive_start": 4, "positive_end": 5, "negative_start": 4, "negative_end": 5, "positive_lexemes": ["head"], "negative_lexemes": ["head"]}, {"tag": "insert", "positive_start": 5, "positive_end": 5, "negative_start": 5, "negative_end": 6, "positive_lexemes": [], "negative_lexemes": ["low"]}, {"tag": "equal", "positive_start": 5, "positive_end": 8, "negative_start": 6, "negative_end": 9, "positive_lexemes": ["in", "the", "sky"], "negative_lexemes": ["in", "the", "sky"]}, {"tag": "replace", "positive_start": 8, "positive_end": 10, "negative_start": 9, "negative_end": 11, "positive_lexemes": ["next", "to"], "negative_lexemes": ["away", "from"]}, {"tag": "equal", "positive_start": 10, "positive_end": 12, "negative_start": 11, "negative_end": 13, "positive_lexemes": ["a", "tree"], "negative_lexemes": ["a", "tree"]}]`
- 共同前缀：`["a", "giraffe"]`
- 正确 contrast hull：`["sticking", "his", "head", "in", "the", "sky", "next", "to"]`
- 错误 contrast hull：`["with", "the", "head", "low", "in", "the", "sky", "away", "from"]`
- 共同后缀：`["a", "tree"]`
- Hull token 覆盖率（正/负/最大）：`[0.5263157894736842, 0.55, 0.55]`
- 共同前缀模型 token：`[100, 492, 108, 559, 1627, 104]`
- 正确 hull 模型 token：IDs `[580, 375, 1237, 2049, 5308, 353, 309, 3716, 4658, 364]`；text " sticking his head in the sky next to"
- 错误 hull 模型 token：IDs `[599, 309, 5308, 406, 451, 353, 309, 3716, 299, 5054, 961]`；text " with the head low in the sky away from"
- 第一轮/第二轮分类：`complex_edit` / `multi_block_local_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 14. `swap_atribute:136`

- 负例类型/范围：`swap_atribute` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："The tray has a sandwich and two bowls near a beverage."
- 原始正描述 2："The sandwich and two bowls are positioned near a beverage on the tray."
- 原始负描述："The tray has two sandwiches and a bowl near a beverage."
- 规范化正描述 1："the tray has a sandwich and two bowls near a beverage"
- 规范化正描述 2："the sandwich and two bowls are positioned near a beverage on the tray"
- 规范化负描述："the tray has two sandwiches and a bowl near a beverage"
- 正描述 1 选择元组：`[8, 10, 2, 0.36363636363636365, 0.16666666666666666]`
- 正描述 2 选择元组：`[14, 22, 4, 0.6923076923076923, 0.5942028985507246]`
- 最终比较正描述：`positive_1` / "The tray has a sandwich and two bowls near a beverage."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 3, "negative_start": 0, "negative_end": 3, "positive_lexemes": ["the", "tray", "has"], "negative_lexemes": ["the", "tray", "has"]}, {"tag": "replace", "positive_start": 3, "positive_end": 5, "negative_start": 3, "negative_end": 5, "positive_lexemes": ["a", "sandwich"], "negative_lexemes": ["two", "sandwiches"]}, {"tag": "equal", "positive_start": 5, "positive_end": 6, "negative_start": 5, "negative_end": 6, "positive_lexemes": ["and"], "negative_lexemes": ["and"]}, {"tag": "replace", "positive_start": 6, "positive_end": 8, "negative_start": 6, "negative_end": 8, "positive_lexemes": ["two", "bowls"], "negative_lexemes": ["a", "bowl"]}, {"tag": "equal", "positive_start": 8, "positive_end": 11, "negative_start": 8, "negative_end": 11, "positive_lexemes": ["near", "a", "beverage"], "negative_lexemes": ["near", "a", "beverage"]}]`
- 共同前缀：`["the", "tray", "has"]`
- 正确 contrast hull：`["a", "sandwich", "and", "two", "bowls"]`
- 错误 contrast hull：`["two", "sandwiches", "and", "a", "bowl"]`
- 共同后缀：`["near", "a", "beverage"]`
- Hull token 覆盖率（正/负/最大）：`[0.55, 0.55, 0.55]`
- 共同前缀模型 token：`[4345, 1946, 124, 1290]`
- 正确 hull 模型 token：IDs `[299, 316, 728, 122, 948, 376, 2102, 363, 451, 111, 118]`；text " a sandwich and two bowls"
- 错误 hull 模型 token：IDs `[2102, 316, 728, 122, 375, 2470, 376, 299, 363, 451, 111]`；text " two sandwiches and a bowl"
- 第一轮/第二轮分类：`complex_edit` / `multi_block_local_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 15. `swap_atribute:189`

- 负例类型/范围：`swap_atribute` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A person is eating a gigantic pastry next to a chair."
- 原始正描述 2："The person is eating a gigantic pastry next to a chair."
- 原始负描述："A person is eating a pastry next to a gigantic chair."
- 规范化正描述 1："a person is eating a gigantic pastry next to a chair"
- 规范化正描述 2："the person is eating a gigantic pastry next to a chair"
- 规范化负描述："a person is eating a pastry next to a gigantic chair"
- 正描述 1 选择元组：`[2, 10, 2, 0.18181818181818182, 0.34615384615384615]`
- 正描述 2 选择元组：`[4, 20, 3, 0.2727272727272727, 0.3888888888888889]`
- 最终比较正描述：`positive_1` / "A person is eating a gigantic pastry next to a chair."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 5, "negative_start": 0, "negative_end": 5, "positive_lexemes": ["a", "person", "is", "eating", "a"], "negative_lexemes": ["a", "person", "is", "eating", "a"]}, {"tag": "delete", "positive_start": 5, "positive_end": 6, "negative_start": 5, "negative_end": 5, "positive_lexemes": ["gigantic"], "negative_lexemes": []}, {"tag": "equal", "positive_start": 6, "positive_end": 10, "negative_start": 5, "negative_end": 9, "positive_lexemes": ["pastry", "next", "to", "a"], "negative_lexemes": ["pastry", "next", "to", "a"]}, {"tag": "insert", "positive_start": 10, "positive_end": 10, "negative_start": 9, "negative_end": 10, "positive_lexemes": [], "negative_lexemes": ["gigantic"]}, {"tag": "equal", "positive_start": 10, "positive_end": 11, "negative_start": 10, "negative_end": 11, "positive_lexemes": ["chair"], "negative_lexemes": ["chair"]}]`
- 共同前缀：`["a", "person", "is", "eating", "a"]`
- 正确 contrast hull：`["gigantic", "pastry", "next", "to", "a"]`
- 错误 contrast hull：`["pastry", "next", "to", "a", "gigantic"]`
- 共同后缀：`["chair"]`
- Hull token 覆盖率（正/负/最大）：`[0.5555555555555556, 0.5555555555555556, 0.5555555555555556]`
- 共同前缀模型 token：`[100, 2198, 395, 413, 1807, 299]`
- 正确 hull 模型 token：IDs `[492, 499, 811, 375, 344, 1154, 1557, 4658, 364, 299]`；text " gigantic pastry next to a"
- 错误 hull 模型 token：IDs `[344, 1154, 1557, 4658, 364, 299, 492, 499, 811, 375]`；text " pastry next to a gigantic"
- 第一轮/第二轮分类：`complex_edit` / `multi_block_local_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 16. `swap_atribute:246`

- 负例类型/范围：`swap_atribute` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："Three workers stand next to each other with their baked goods behind them."
- 原始正描述 2："The three workers stand next to each other with their baked goods positioned behind them."
- 原始负描述："Their workers stand next to each other with three baked goods behind them."
- 规范化正描述 1："three workers stand next to each other with their baked goods behind them"
- 规范化正描述 2："the three workers stand next to each other with their baked goods positioned behind them"
- 规范化负描述："their workers stand next to each other with three baked goods behind them"
- 正描述 1 选择元组：`[4, 18, 2, 0.15384615384615385, 0.0821917808219178]`
- 正描述 2 选择元组：`[6, 24, 4, 0.26666666666666666, 0.2159090909090909]`
- 最终比较正描述：`positive_1` / "Three workers stand next to each other with their baked goods behind them."
- 完整 lexeme 编辑块：`[{"tag": "replace", "positive_start": 0, "positive_end": 1, "negative_start": 0, "negative_end": 1, "positive_lexemes": ["three"], "negative_lexemes": ["their"]}, {"tag": "equal", "positive_start": 1, "positive_end": 8, "negative_start": 1, "negative_end": 8, "positive_lexemes": ["workers", "stand", "next", "to", "each", "other", "with"], "negative_lexemes": ["workers", "stand", "next", "to", "each", "other", "with"]}, {"tag": "replace", "positive_start": 8, "positive_end": 9, "negative_start": 8, "negative_end": 9, "positive_lexemes": ["their"], "negative_lexemes": ["three"]}, {"tag": "equal", "positive_start": 9, "positive_end": 13, "negative_start": 9, "negative_end": 13, "positive_lexemes": ["baked", "goods", "behind", "them"], "negative_lexemes": ["baked", "goods", "behind", "them"]}]`
- 共同前缀：`[]`
- 正确 contrast hull：`["three", "workers", "stand", "next", "to", "each", "other", "with", "their"]`
- 错误 contrast hull：`["their", "workers", "stand", "next", "to", "each", "other", "with", "three"]`
- 共同后缀：`["baked", "goods", "behind", "them"]`
- Hull token 覆盖率（正/负/最大）：`[0.55, 0.55, 0.55]`
- 共同前缀模型 token：`[]`
- 正确 hull 模型 token：IDs `[495, 1382, 2943, 496, 2823, 4658, 364, 1766, 1649, 599, 1635]`；text "three workers stand next to each other with their"
- 错误 hull 模型 token：IDs `[4345, 639, 2943, 496, 2823, 4658, 364, 1766, 1649, 599, 3785]`；text "their workers stand next to each other with three"
- 第一轮/第二轮分类：`complex_edit` / `multi_block_local_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 17. `swap_atribute:263`

- 负例类型/范围：`swap_atribute` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A tall vase with red and white tulips in water."
- 原始正描述 2："Red and white tupils are submerged in a water filled vase."
- 原始负描述："A red and white vase with tall tulips in water."
- 规范化正描述 1："a tall vase with red and white tulips in water"
- 规范化正描述 2："red and white tupils are submerged in a water filled vase"
- 规范化负描述："a red and white vase with tall tulips in water"
- 正描述 1 选择元组：`[12, 12, 1, 0.6, 0.45652173913043476]`
- 正描述 2 选择元组：`[13, 21, 3, 0.7272727272727273, 0.6140350877192983]`
- 最终比较正描述：`positive_1` / "A tall vase with red and white tulips in water."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 1, "negative_start": 0, "negative_end": 1, "positive_lexemes": ["a"], "negative_lexemes": ["a"]}, {"tag": "replace", "positive_start": 1, "positive_end": 7, "negative_start": 1, "negative_end": 7, "positive_lexemes": ["tall", "vase", "with", "red", "and", "white"], "negative_lexemes": ["red", "and", "white", "vase", "with", "tall"]}, {"tag": "equal", "positive_start": 7, "positive_end": 10, "negative_start": 7, "negative_end": 10, "positive_lexemes": ["tulips", "in", "water"], "negative_lexemes": ["tulips", "in", "water"]}]`
- 共同前缀：`["a"]`
- 正确 contrast hull：`["tall", "vase", "with", "red", "and", "white"]`
- 错误 contrast hull：`["red", "and", "white", "vase", "with", "tall"]`
- 共同后缀：`["tulips", "in", "water"]`
- Hull token 覆盖率（正/负/最大）：`[0.5625, 0.5625, 0.5625]`
- 共同前缀模型 token：`[100]`
- 正确 hull 模型 token：IDs `[297, 1266, 603, 812, 599, 5534, 376, 654, 1078]`；text " tall vase with red and white"
- 错误 hull 模型 token：IDs `[5534, 376, 654, 1078, 603, 812, 599, 297, 1266]`；text " red and white vase with tall"
- 第一轮/第二轮分类：`complex_edit` / `medium_contrast_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；"single_edit_block_token_coverage_above_50_percent"

### 18. `swap_atribute:316`

- 负例类型/范围：`swap_atribute` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："a white toilet in a black counter bathroom"
- 原始正描述 2："A black counter bathroom with a white toilet positioned on it."
- 原始负描述："a black toilet in a white counter bathroom"
- 规范化正描述 1："a white toilet in a black counter bathroom"
- 规范化正描述 2："a black counter bathroom with a white toilet positioned on it"
- 规范化负描述："a black toilet in a white counter bathroom"
- 正描述 1 选择元组：`[4, 10, 2, 0.25, 0.23809523809523808]`
- 正描述 2 选择元组：`[11, 15, 4, 0.6363636363636364, 0.5737704918032787]`
- 最终比较正描述：`positive_1` / "a white toilet in a black counter bathroom"
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 1, "negative_start": 0, "negative_end": 1, "positive_lexemes": ["a"], "negative_lexemes": ["a"]}, {"tag": "replace", "positive_start": 1, "positive_end": 2, "negative_start": 1, "negative_end": 2, "positive_lexemes": ["white"], "negative_lexemes": ["black"]}, {"tag": "equal", "positive_start": 2, "positive_end": 5, "negative_start": 2, "negative_end": 5, "positive_lexemes": ["toilet", "in", "a"], "negative_lexemes": ["toilet", "in", "a"]}, {"tag": "replace", "positive_start": 5, "positive_end": 6, "negative_start": 5, "negative_end": 6, "positive_lexemes": ["black"], "negative_lexemes": ["white"]}, {"tag": "equal", "positive_start": 6, "positive_end": 8, "negative_start": 6, "negative_end": 8, "positive_lexemes": ["counter", "bathroom"], "negative_lexemes": ["counter", "bathroom"]}]`
- 共同前缀：`["a"]`
- 正确 contrast hull：`["white", "toilet", "in", "a", "black"]`
- 错误 contrast hull：`["black", "toilet", "in", "a", "white"]`
- 共同后缀：`["counter", "bathroom"]`
- Hull token 覆盖率（正/负/最大）：`[0.5625, 0.5625, 0.5625]`
- 共同前缀模型 token：`[100]`
- 正确 hull 模型 token：IDs `[654, 1078, 364, 1299, 119, 353, 299, 2597, 1637]`；text " white toilet in a black"
- 错误 hull 模型 token：IDs `[2597, 1637, 364, 1299, 119, 353, 299, 654, 1078]`；text " black toilet in a white"
- 第一轮/第二轮分类：`complex_edit` / `multi_block_local_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 19. `swap_atribute:372`

- 负例类型/范围：`swap_atribute` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A little child holding a baseball bat on grass."
- 原始正描述 2："A baseball bat is being held by a little child."
- 原始负描述："A baseball child holding a little bat on grass."
- 规范化正描述 1："a little child holding a baseball bat on grass"
- 规范化正描述 2："a baseball bat is being held by a little child"
- 规范化负描述："a baseball child holding a little bat on grass"
- 正描述 1 选择元组：`[4, 10, 2, 0.2222222222222222, 0.30434782608695654]`
- 正描述 2 选择元组：`[15, 15, 2, 0.8, 0.5869565217391305]`
- 最终比较正描述：`positive_1` / "A little child holding a baseball bat on grass."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 1, "negative_start": 0, "negative_end": 1, "positive_lexemes": ["a"], "negative_lexemes": ["a"]}, {"tag": "replace", "positive_start": 1, "positive_end": 2, "negative_start": 1, "negative_end": 2, "positive_lexemes": ["little"], "negative_lexemes": ["baseball"]}, {"tag": "equal", "positive_start": 2, "positive_end": 5, "negative_start": 2, "negative_end": 5, "positive_lexemes": ["child", "holding", "a"], "negative_lexemes": ["child", "holding", "a"]}, {"tag": "replace", "positive_start": 5, "positive_end": 6, "negative_start": 5, "negative_end": 6, "positive_lexemes": ["baseball"], "negative_lexemes": ["little"]}, {"tag": "equal", "positive_start": 6, "positive_end": 9, "negative_start": 6, "negative_end": 9, "positive_lexemes": ["bat", "on", "grass"], "negative_lexemes": ["bat", "on", "grass"]}]`
- 共同前缀：`["a"]`
- 正确 contrast hull：`["little", "child", "holding", "a", "baseball"]`
- 错误 contrast hull：`["baseball", "child", "holding", "a", "little"]`
- 共同后缀：`["bat", "on", "grass"]`
- Hull token 覆盖率（正/负/最大）：`[0.6111111111111112, 0.6111111111111112, 0.6111111111111112]`
- 共同前缀模型 token：`[100]`
- 正确 hull 模型 token：IDs `[406, 338, 5395, 6109, 429, 2569, 350, 299, 4933, 101, 1266]`；text " little child holding a baseball"
- 错误 hull 模型 token：IDs `[4933, 101, 1266, 6109, 429, 2569, 350, 299, 406, 338, 5395]`；text " baseball child holding a little"
- 第一轮/第二轮分类：`complex_edit` / `multi_block_local_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 20. `swap_atribute:379`

- 负例类型/范围：`swap_atribute` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A street sign with flags on it and a building in the background."
- 原始正描述 2："A building with a street sign and flags in the background."
- 原始负描述："A building sign with flags on it and a street in the background."
- 规范化正描述 1："a street sign with flags on it and a building in the background"
- 规范化正描述 2："a building with a street sign and flags in the background"
- 规范化负描述："a building sign with flags on it and a street in the background"
- 正描述 1 选择元组：`[4, 18, 2, 0.15384615384615385, 0.25396825396825395]`
- 正描述 2 选择元组：`[10, 14, 4, 0.46153846153846156, 0.38095238095238093]`
- 最终比较正描述：`positive_1` / "A street sign with flags on it and a building in the background."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 1, "negative_start": 0, "negative_end": 1, "positive_lexemes": ["a"], "negative_lexemes": ["a"]}, {"tag": "replace", "positive_start": 1, "positive_end": 2, "negative_start": 1, "negative_end": 2, "positive_lexemes": ["street"], "negative_lexemes": ["building"]}, {"tag": "equal", "positive_start": 2, "positive_end": 9, "negative_start": 2, "negative_end": 9, "positive_lexemes": ["sign", "with", "flags", "on", "it", "and", "a"], "negative_lexemes": ["sign", "with", "flags", "on", "it", "and", "a"]}, {"tag": "replace", "positive_start": 9, "positive_end": 10, "negative_start": 9, "negative_end": 10, "positive_lexemes": ["building"], "negative_lexemes": ["street"]}, {"tag": "equal", "positive_start": 10, "positive_end": 13, "negative_start": 10, "negative_end": 13, "positive_lexemes": ["in", "the", "background"], "negative_lexemes": ["in", "the", "background"]}]`
- 共同前缀：`["a"]`
- 正确 contrast hull：`["street", "sign", "with", "flags", "on", "it", "and", "a", "building"]`
- 错误 contrast hull：`["building", "sign", "with", "flags", "on", "it", "and", "a", "street"]`
- 共同后缀：`["in", "the", "background"]`
- Hull token 覆盖率（正/负/最大）：`[0.6842105263157895, 0.6842105263157895, 0.6842105263157895]`
- 共同前缀模型 token：`[100]`
- 正确 hull 模型 token：IDs `[5941, 439, 2185, 599, 3687, 1163, 118, 619, 563, 376, 299, 6331, 350]`；text " street sign with flags on it and a building"
- 错误 hull 模型 token：IDs `[6331, 350, 2185, 599, 3687, 1163, 118, 619, 563, 376, 299, 5941, 439]`；text " building sign with flags on it and a street"
- 第一轮/第二轮分类：`complex_edit` / `multi_block_local_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 21. `swap_atribute:384`

- 负例类型/范围：`swap_atribute` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A person is waving a flag at people passing by in a train."
- 原始正描述 2："A flag bearer is waving their flag at the crowds aboard a passing train."
- 原始负描述："A person is passing by people waving a flag in a train."
- 规范化正描述 1："a person is waving a flag at people passing by in a train"
- 规范化正描述 2："a flag bearer is waving their flag at the crowds aboard a passing train"
- 规范化负描述："a person is passing by people waving a flag in a train"
- 正描述 1 选择元组：`[13, 13, 2, 0.5384615384615384, 0.3684210526315789]`
- 正描述 2 选择元组：`[18, 22, 4, 0.7142857142857143, 0.6338028169014085]`
- 最终比较正描述：`positive_1` / "A person is waving a flag at people passing by in a train."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 3, "negative_start": 0, "negative_end": 3, "positive_lexemes": ["a", "person", "is"], "negative_lexemes": ["a", "person", "is"]}, {"tag": "delete", "positive_start": 3, "positive_end": 4, "negative_start": 3, "negative_end": 3, "positive_lexemes": ["waving"], "negative_lexemes": []}, {"tag": "replace", "positive_start": 4, "positive_end": 10, "negative_start": 3, "negative_end": 9, "positive_lexemes": ["a", "flag", "at", "people", "passing", "by"], "negative_lexemes": ["passing", "by", "people", "waving", "a", "flag"]}, {"tag": "equal", "positive_start": 10, "positive_end": 13, "negative_start": 9, "negative_end": 12, "positive_lexemes": ["in", "a", "train"], "negative_lexemes": ["in", "a", "train"]}]`
- 共同前缀：`["a", "person", "is"]`
- 正确 contrast hull：`["waving", "a", "flag", "at", "people", "passing", "by"]`
- 错误 contrast hull：`["passing", "by", "people", "waving", "a", "flag"]`
- 共同后缀：`["in", "a", "train"]`
- Hull token 覆盖率（正/负/最大）：`[0.6111111111111112, 0.5882352941176471, 0.6111111111111112]`
- 共同前缀模型 token：`[100, 2198, 395]`
- 正确 hull 模型 token：IDs `[339, 1113, 350, 299, 3687, 1163, 1248, 2975, 3241, 350, 769]`；text " waving a flag at people passing by"
- 错误 hull 模型 token：IDs `[3241, 350, 769, 2975, 339, 1113, 350, 299, 3687, 1163]`；text " passing by people waving a flag"
- 第一轮/第二轮分类：`complex_edit` / `multi_block_local_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 22. `swap_atribute:388`

- 负例类型/范围：`swap_atribute` / `{"canonical": true, "pilot": true, "formal": false, "certifying_formal": false}`
- 原始正描述 1："Three people are in a small boat in a lake and one person holds a red and yellow umbrella."
- 原始正描述 2："In a small boat in a lake, there are three individuals and one person holds a red and yellow umbrella."
- 原始负描述："Three people are in a red and yellow boat in a large lake and one person holds a small umbrella."
- 规范化正描述 1："three people are in a small boat in a lake and one person holds a red and yellow umbrella"
- 规范化正描述 2："in a small boat in a lake , there are three individuals and one person holds a red and yellow umbrella"
- 规范化负描述："three people are in a red and yellow boat in a large lake and one person holds a small umbrella"
- 正描述 1 选择元组：`[9, 27, 5, 0.35, 0.29473684210526313]`
- 正描述 2 选择元组：`[25, 39, 6, 0.7142857142857143, 0.5490196078431373]`
- 最终比较正描述：`positive_1` / "Three people are in a small boat in a lake and one person holds a red and yellow umbrella."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 5, "negative_start": 0, "negative_end": 5, "positive_lexemes": ["three", "people", "are", "in", "a"], "negative_lexemes": ["three", "people", "are", "in", "a"]}, {"tag": "insert", "positive_start": 5, "positive_end": 5, "negative_start": 5, "negative_end": 7, "positive_lexemes": [], "negative_lexemes": ["red", "and"]}, {"tag": "replace", "positive_start": 5, "positive_end": 6, "negative_start": 7, "negative_end": 8, "positive_lexemes": ["small"], "negative_lexemes": ["yellow"]}, {"tag": "equal", "positive_start": 6, "positive_end": 9, "negative_start": 8, "negative_end": 11, "positive_lexemes": ["boat", "in", "a"], "negative_lexemes": ["boat", "in", "a"]}, {"tag": "insert", "positive_start": 9, "positive_end": 9, "negative_start": 11, "negative_end": 12, "positive_lexemes": [], "negative_lexemes": ["large"]}, {"tag": "equal", "positive_start": 9, "positive_end": 15, "negative_start": 12, "negative_end": 18, "positive_lexemes": ["lake", "and", "one", "person", "holds", "a"], "negative_lexemes": ["lake", "and", "one", "person", "holds", "a"]}, {"tag": "delete", "positive_start": 15, "positive_end": 17, "negative_start": 18, "negative_end": 18, "positive_lexemes": ["red", "and"], "negative_lexemes": []}, {"tag": "replace", "positive_start": 17, "positive_end": 18, "negative_start": 18, "negative_end": 19, "positive_lexemes": ["yellow"], "negative_lexemes": ["small"]}, {"tag": "equal", "positive_start": 18, "positive_end": 19, "negative_start": 19, "negative_end": 20, "positive_lexemes": ["umbrella"], "negative_lexemes": ["umbrella"]}]`
- 共同前缀：`["three", "people", "are", "in", "a"]`
- 正确 contrast hull：`["small", "boat", "in", "a", "lake", "and", "one", "person", "holds", "a", "red", "and", "yellow"]`
- 错误 contrast hull：`["red", "and", "yellow", "boat", "in", "a", "large", "lake", "and", "one", "person", "holds", "a", "small"]`
- 共同后缀：`["umbrella"]`
- Hull token 覆盖率（正/负/最大）：`[0.6333333333333333, 0.6451612903225806, 0.6451612903225806]`
- 共同前缀模型 token：`[495, 1382, 2975, 732, 353, 299]`
- 正确 hull 模型 token：IDs `[3436, 1847, 314, 353, 299, 406, 2434, 376, 1623, 2198, 429, 500, 1881, 299, 5534, 376, 385, 446, 1030]`；text " small boat in a lake and one person holds a red and yellow"
- 错误 hull 模型 token：IDs `[5534, 376, 385, 446, 1030, 1847, 314, 353, 299, 2994, 406, 2434, 376, 1623, 2198, 429, 500, 1881, 299, 3436]`；text " red and yellow boat in a large lake and one person holds a small"
- 第一轮/第二轮分类：`complex_edit` / `multi_block_local_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 23. `swap_atribute:444`

- 负例类型/范围：`swap_atribute` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："Two babies sitting on their potties in the bathroom."
- 原始正描述 2："In the bathroom, two babies are seated on their potties."
- 原始负描述："Their baby is sitting on two potties in the bathroom."
- 规范化正描述 1："two babies sitting on their potties in the bathroom"
- 规范化正描述 2："in the bathroom , two babies are seated on their potties"
- 规范化负描述："their baby is sitting on two potties in the bathroom"
- 正描述 1 选择元组：`[7, 11, 3, 0.4, 0.21153846153846154]`
- 正描述 2 选择元组：`[21, 21, 2, 1.0, 0.7142857142857143]`
- 最终比较正描述：`positive_1` / "Two babies sitting on their potties in the bathroom."
- 完整 lexeme 编辑块：`[{"tag": "insert", "positive_start": 0, "positive_end": 0, "negative_start": 0, "negative_end": 1, "positive_lexemes": [], "negative_lexemes": ["their"]}, {"tag": "replace", "positive_start": 0, "positive_end": 2, "negative_start": 1, "negative_end": 3, "positive_lexemes": ["two", "babies"], "negative_lexemes": ["baby", "is"]}, {"tag": "equal", "positive_start": 2, "positive_end": 4, "negative_start": 3, "negative_end": 5, "positive_lexemes": ["sitting", "on"], "negative_lexemes": ["sitting", "on"]}, {"tag": "replace", "positive_start": 4, "positive_end": 5, "negative_start": 5, "negative_end": 6, "positive_lexemes": ["their"], "negative_lexemes": ["two"]}, {"tag": "equal", "positive_start": 5, "positive_end": 9, "negative_start": 6, "negative_end": 10, "positive_lexemes": ["potties", "in", "the", "bathroom"], "negative_lexemes": ["potties", "in", "the", "bathroom"]}]`
- 共同前缀：`[]`
- 正确 contrast hull：`["two", "babies", "sitting", "on", "their"]`
- 错误 contrast hull：`["their", "baby", "is", "sitting", "on", "two"]`
- 共同后缀：`["potties", "in", "the", "bathroom"]`
- Hull token 覆盖率（正/负/最大）：`[0.5263157894736842, 0.5263157894736842, 0.5263157894736842]`
- 共同前缀模型 token：`[]`
- 正确 hull 模型 token：IDs `[119, 122, 114, 363, 572, 925, 5305, 2912, 619, 1635]`；text "two babies sitting on their"
- 错误 hull 模型 token：IDs `[4345, 639, 363, 572, 124, 395, 5305, 2912, 619, 2102]`；text "their baby is sitting on two"
- 第一轮/第二轮分类：`complex_edit` / `multi_block_local_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 24. `swap_atribute:463`

- 负例类型/范围：`swap_atribute` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："Several cats sitting near a tree and a bird on a fence post."
- 原始正描述 2："Several cats are positioned near a tree, and a bird is situated on a fence post."
- 原始负描述："A cat sitting near a tree and several birds on a fence post."
- 规范化正描述 1："several cats sitting near a tree and a bird on a fence post"
- 规范化正描述 2："several cats are positioned near a tree , and a bird is situated on a fence post"
- 规范化负描述："a cat sitting near a tree and several birds on a fence post"
- 正描述 1 选择元组：`[8, 18, 2, 0.3076923076923077, 0.23728813559322035]`
- 正描述 2 选择元组：`[14, 22, 5, 0.5294117647058824, 0.425]`
- 最终比较正描述：`positive_1` / "Several cats sitting near a tree and a bird on a fence post."
- 完整 lexeme 编辑块：`[{"tag": "replace", "positive_start": 0, "positive_end": 2, "negative_start": 0, "negative_end": 2, "positive_lexemes": ["several", "cats"], "negative_lexemes": ["a", "cat"]}, {"tag": "equal", "positive_start": 2, "positive_end": 7, "negative_start": 2, "negative_end": 7, "positive_lexemes": ["sitting", "near", "a", "tree", "and"], "negative_lexemes": ["sitting", "near", "a", "tree", "and"]}, {"tag": "replace", "positive_start": 7, "positive_end": 9, "negative_start": 7, "negative_end": 9, "positive_lexemes": ["a", "bird"], "negative_lexemes": ["several", "birds"]}, {"tag": "equal", "positive_start": 9, "positive_end": 13, "negative_start": 9, "negative_end": 13, "positive_lexemes": ["on", "a", "fence", "post"], "negative_lexemes": ["on", "a", "fence", "post"]}]`
- 共同前缀：`[]`
- 正确 contrast hull：`["several", "cats", "sitting", "near", "a", "tree", "and", "a", "bird"]`
- 错误 contrast hull：`["a", "cat", "sitting", "near", "a", "tree", "and", "several", "birds"]`
- 共同后缀：`["on", "a", "fence", "post"]`
- Hull token 覆盖率（正/负/最大）：`[0.7272727272727273, 0.6842105263157895, 0.7272727272727273]`
- 共同前缀模型 token：`[]`
- 正确 hull 模型 token：IDs `[573, 652, 352, 3706, 118, 5305, 2912, 730, 370, 299, 297, 1382, 376, 299, 5231, 103]`；text "several cats sitting near a tree and a bird"
- 错误 hull 模型 token：IDs `[100, 3706, 5305, 2912, 730, 370, 299, 297, 1382, 376, 4920, 5231, 1881]`；text "a cat sitting near a tree and several birds"
- 第一轮/第二轮分类：`complex_edit` / `multi_block_local_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 25. `swap_atribute:63`

- 负例类型/范围：`swap_atribute` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："a large screen showing a person wearing a suit"
- 原始正描述 2："A person wearing a suit is displayed on a large screen."
- 原始负描述："A person is not wearing a large suit showing on the screen."
- 规范化正描述 1："a large screen showing a person wearing a suit"
- 规范化正描述 2："a person wearing a suit is displayed on a large screen"
- 规范化负描述："a person is not wearing a large suit showing on the screen"
- 正描述 1 选择元组：`[17, 19, 4, 0.8333333333333334, 0.6551724137931034]`
- 正描述 2 选择元组：`[11, 17, 4, 0.5833333333333334, 0.5]`
- 最终比较正描述：`positive_2` / "A person wearing a suit is displayed on a large screen."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 2, "negative_start": 0, "negative_end": 2, "positive_lexemes": ["a", "person"], "negative_lexemes": ["a", "person"]}, {"tag": "insert", "positive_start": 2, "positive_end": 2, "negative_start": 2, "negative_end": 4, "positive_lexemes": [], "negative_lexemes": ["is", "not"]}, {"tag": "equal", "positive_start": 2, "positive_end": 4, "negative_start": 4, "negative_end": 6, "positive_lexemes": ["wearing", "a"], "negative_lexemes": ["wearing", "a"]}, {"tag": "replace", "positive_start": 4, "positive_end": 7, "negative_start": 6, "negative_end": 9, "positive_lexemes": ["suit", "is", "displayed"], "negative_lexemes": ["large", "suit", "showing"]}, {"tag": "equal", "positive_start": 7, "positive_end": 8, "negative_start": 9, "negative_end": 10, "positive_lexemes": ["on"], "negative_lexemes": ["on"]}, {"tag": "delete", "positive_start": 8, "positive_end": 9, "negative_start": 10, "negative_end": 10, "positive_lexemes": ["a"], "negative_lexemes": []}, {"tag": "replace", "positive_start": 9, "positive_end": 10, "negative_start": 10, "negative_end": 11, "positive_lexemes": ["large"], "negative_lexemes": ["the"]}, {"tag": "equal", "positive_start": 10, "positive_end": 11, "negative_start": 11, "negative_end": 12, "positive_lexemes": ["screen"], "negative_lexemes": ["screen"]}]`
- 共同前缀：`["a", "person"]`
- 正确 contrast hull：`["wearing", "a", "suit", "is", "displayed", "on", "a", "large"]`
- 错误 contrast hull：`["is", "not", "wearing", "a", "large", "suit", "showing", "on", "the"]`
- 共同后缀：`["screen"]`
- Hull token 覆盖率（正/负/最大）：`[0.7222222222222222, 0.7222222222222222, 0.7222222222222222]`
- 共同前缀模型 token：`[100, 2198]`
- 正确 hull 模型 token：IDs `[796, 370, 350, 299, 855, 338, 395, 1981, 4838, 382, 619, 299, 2994]`；text " wearing a suit is displayed on a large"
- 错误 hull 模型 token：IDs `[395, 1027, 796, 370, 350, 299, 2994, 855, 338, 5950, 350, 619, 309]`；text " is not wearing a large suit showing on the"
- 第一轮/第二轮分类：`complex_edit` / `multi_block_local_hull`
- 自动判断："positive_2_selection_tuple_lexicographically_smaller"；null

### 26. `swap_object:108`

- 负例类型/范围：`swap_object` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A person on a motorcycle driving past a group of people behind a fence."
- 原始正描述 2："A person is driving a motorcycle past a group of individuals who are behind a fence."
- 原始负描述："A group of people on motorcycles driving past a person behind a fence."
- 规范化正描述 1："a person on a motorcycle driving past a group of people behind a fence"
- 规范化正描述 2："a person is driving a motorcycle past a group of individuals who are behind a fence"
- 规范化负描述："a group of people on motorcycles driving past a person behind a fence"
- 正描述 1 选择元组：`[13, 19, 4, 0.5714285714285714, 0.4]`
- 正描述 2 选择元组：`[17, 21, 4, 0.6875, 0.5542168674698795]`
- 最终比较正描述：`positive_1` / "A person on a motorcycle driving past a group of people behind a fence."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 1, "negative_start": 0, "negative_end": 1, "positive_lexemes": ["a"], "negative_lexemes": ["a"]}, {"tag": "insert", "positive_start": 1, "positive_end": 1, "negative_start": 1, "negative_end": 2, "positive_lexemes": [], "negative_lexemes": ["group"]}, {"tag": "replace", "positive_start": 1, "positive_end": 5, "negative_start": 2, "negative_end": 6, "positive_lexemes": ["person", "on", "a", "motorcycle"], "negative_lexemes": ["of", "people", "on", "motorcycles"]}, {"tag": "equal", "positive_start": 5, "positive_end": 8, "negative_start": 6, "negative_end": 9, "positive_lexemes": ["driving", "past", "a"], "negative_lexemes": ["driving", "past", "a"]}, {"tag": "delete", "positive_start": 8, "positive_end": 10, "negative_start": 9, "negative_end": 9, "positive_lexemes": ["group", "of"], "negative_lexemes": []}, {"tag": "replace", "positive_start": 10, "positive_end": 11, "negative_start": 9, "negative_end": 10, "positive_lexemes": ["people"], "negative_lexemes": ["person"]}, {"tag": "equal", "positive_start": 11, "positive_end": 14, "negative_start": 10, "negative_end": 13, "positive_lexemes": ["behind", "a", "fence"], "negative_lexemes": ["behind", "a", "fence"]}]`
- 共同前缀：`["a"]`
- 正确 contrast hull：`["person", "on", "a", "motorcycle", "driving", "past", "a", "group", "of", "people"]`
- 错误 contrast hull：`["group", "of", "people", "on", "motorcycles", "driving", "past", "a", "person"]`
- 共同后缀：`["behind", "a", "fence"]`
- Hull token 覆盖率（正/负/最大）：`[0.7272727272727273, 0.7272727272727273, 0.7272727272727273]`
- 共同前缀模型 token：`[100]`
- 正确 hull 模型 token：IDs `[2198, 619, 299, 351, 593, 336, 2863, 2945, 5893, 4917, 344, 1154, 299, 4592, 354, 2975]`；text " person on a motorcycle driving past a group of people"
- 错误 hull 模型 token：IDs `[4592, 354, 2975, 619, 351, 593, 336, 2863, 1110, 329, 5893, 4917, 344, 1154, 299, 2198]`；text " group of people on motorcycles driving past a person"
- 第一轮/第二轮分类：`complex_edit` / `multi_block_local_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 27. `swap_object:225`

- 负例类型/范围：`swap_object` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A train car is open and shows the door on the other side."
- 原始正描述 2："The door on the other side of the train car is visible through the open door."
- 原始负描述："The door is open and shows a train car on the other side."
- 规范化正描述 1："a train car is open and shows the door on the other side"
- 规范化正描述 2："the door on the other side of the train car is visible through the open door"
- 规范化负描述："the door is open and shows a train car on the other side"
- 正描述 1 选择元组：`[10, 18, 4, 0.46153846153846156, 0.32142857142857145]`
- 正描述 2 选择元组：`[19, 25, 5, 0.6875, 0.5657894736842105]`
- 最终比较正描述：`positive_1` / "A train car is open and shows the door on the other side."
- 完整 lexeme 编辑块：`[{"tag": "delete", "positive_start": 0, "positive_end": 1, "negative_start": 0, "negative_end": 0, "positive_lexemes": ["a"], "negative_lexemes": []}, {"tag": "replace", "positive_start": 1, "positive_end": 3, "negative_start": 0, "negative_end": 2, "positive_lexemes": ["train", "car"], "negative_lexemes": ["the", "door"]}, {"tag": "equal", "positive_start": 3, "positive_end": 7, "negative_start": 2, "negative_end": 6, "positive_lexemes": ["is", "open", "and", "shows"], "negative_lexemes": ["is", "open", "and", "shows"]}, {"tag": "insert", "positive_start": 7, "positive_end": 7, "negative_start": 6, "negative_end": 7, "positive_lexemes": [], "negative_lexemes": ["a"]}, {"tag": "replace", "positive_start": 7, "positive_end": 9, "negative_start": 7, "negative_end": 9, "positive_lexemes": ["the", "door"], "negative_lexemes": ["train", "car"]}, {"tag": "equal", "positive_start": 9, "positive_end": 13, "negative_start": 9, "negative_end": 13, "positive_lexemes": ["on", "the", "other", "side"], "negative_lexemes": ["on", "the", "other", "side"]}]`
- 共同前缀：`[]`
- 正确 contrast hull：`["a", "train", "car", "is", "open", "and", "shows", "the", "door"]`
- 错误 contrast hull：`["the", "door", "is", "open", "and", "shows", "a", "train", "car"]`
- 共同后缀：`["on", "the", "other", "side"]`
- Hull token 覆盖率（正/负/最大）：`[0.75, 0.75, 0.75]`
- 共同前缀模型 token：`[]`
- 正确 hull 模型 token：IDs `[100, 1946, 301, 3751, 395, 5102, 376, 1128, 3032, 309, 1041, 336]`；text "a train car is open and shows the door"
- 错误 hull 模型 token：IDs `[4345, 1041, 336, 395, 5102, 376, 1128, 3032, 299, 1946, 301, 3751]`；text "the door is open and shows a train car"
- 第一轮/第二轮分类：`complex_edit` / `multi_block_local_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 28. `swap_object:236`

- 负例类型/范围：`swap_object` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A group of giraffes standing in dirt field with trees in background."
- 原始正描述 2："with trees in the background, a group of giraffes are standing in a dirt field."
- 原始负描述："A group of trees standing in dirt field with giraffes in background."
- 规范化正描述 1："a group of giraffes standing in dirt field with trees in background"
- 规范化正描述 2："with trees in the background , a group of giraffes are standing in a dirt field"
- 规范化负描述："a group of trees standing in dirt field with giraffes in background"
- 正描述 1 选择元组：`[4, 14, 2, 0.16666666666666666, 0.14925373134328357]`
- 正描述 2 选择元组：`[14, 28, 5, 0.8125, 0.7341772151898734]`
- 最终比较正描述：`positive_1` / "A group of giraffes standing in dirt field with trees in background."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 3, "negative_start": 0, "negative_end": 3, "positive_lexemes": ["a", "group", "of"], "negative_lexemes": ["a", "group", "of"]}, {"tag": "replace", "positive_start": 3, "positive_end": 4, "negative_start": 3, "negative_end": 4, "positive_lexemes": ["giraffes"], "negative_lexemes": ["trees"]}, {"tag": "equal", "positive_start": 4, "positive_end": 9, "negative_start": 4, "negative_end": 9, "positive_lexemes": ["standing", "in", "dirt", "field", "with"], "negative_lexemes": ["standing", "in", "dirt", "field", "with"]}, {"tag": "replace", "positive_start": 9, "positive_end": 10, "negative_start": 9, "negative_end": 10, "positive_lexemes": ["trees"], "negative_lexemes": ["giraffes"]}, {"tag": "equal", "positive_start": 10, "positive_end": 12, "negative_start": 10, "negative_end": 12, "positive_lexemes": ["in", "background"], "negative_lexemes": ["in", "background"]}]`
- 共同前缀：`["a", "group", "of"]`
- 正确 contrast hull：`["giraffes", "standing", "in", "dirt", "field", "with", "trees"]`
- 错误 contrast hull：`["trees", "standing", "in", "dirt", "field", "with", "giraffes"]`
- 共同后缀：`["in", "background"]`
- Hull token 覆盖率（正/负/最大）：`[0.6666666666666666, 0.6666666666666666, 0.6666666666666666]`
- 共同前缀模型 token：`[100, 4592, 354]`
- 正确 hull 模型 token：IDs `[492, 108, 559, 1627, 329, 2823, 350, 353, 373, 4193, 4749, 599, 4191, 329]`；text " giraffes standing in dirt field with trees"
- 错误 hull 模型 token：IDs `[4191, 329, 2823, 350, 353, 373, 4193, 4749, 599, 492, 108, 559, 1627, 329]`；text " trees standing in dirt field with giraffes"
- 第一轮/第二轮分类：`complex_edit` / `multi_block_local_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 29. `swap_object:71`

- 负例类型/范围：`swap_object` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："The stop sign is behind the fence instead of on the street."
- 原始正描述 2："instead of on the street, a stop sign is positioned behind the fence."
- 原始负描述："The fence is behind the stop sign instead of on the street."
- 规范化正描述 1："the stop sign is behind the fence instead of on the street"
- 规范化正描述 2："instead of on the street , a stop sign is positioned behind the fence"
- 规范化负描述："the fence is behind the stop sign instead of on the street"
- 正描述 1 选择元组：`[6, 12, 4, 0.3333333333333333, 0.3103448275862069]`
- 正描述 2 选择元组：`[20, 26, 4, 0.7857142857142857, 0.5942028985507246]`
- 最终比较正描述：`positive_1` / "The stop sign is behind the fence instead of on the street."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 1, "negative_start": 0, "negative_end": 1, "positive_lexemes": ["the"], "negative_lexemes": ["the"]}, {"tag": "delete", "positive_start": 1, "positive_end": 2, "negative_start": 1, "negative_end": 1, "positive_lexemes": ["stop"], "negative_lexemes": []}, {"tag": "replace", "positive_start": 2, "positive_end": 3, "negative_start": 1, "negative_end": 2, "positive_lexemes": ["sign"], "negative_lexemes": ["fence"]}, {"tag": "equal", "positive_start": 3, "positive_end": 6, "negative_start": 2, "negative_end": 5, "positive_lexemes": ["is", "behind", "the"], "negative_lexemes": ["is", "behind", "the"]}, {"tag": "insert", "positive_start": 6, "positive_end": 6, "negative_start": 5, "negative_end": 6, "positive_lexemes": [], "negative_lexemes": ["stop"]}, {"tag": "replace", "positive_start": 6, "positive_end": 7, "negative_start": 6, "negative_end": 7, "positive_lexemes": ["fence"], "negative_lexemes": ["sign"]}, {"tag": "equal", "positive_start": 7, "positive_end": 12, "negative_start": 7, "negative_end": 12, "positive_lexemes": ["instead", "of", "on", "the", "street"], "negative_lexemes": ["instead", "of", "on", "the", "street"]}]`
- 共同前缀：`["the"]`
- 正确 contrast hull：`["stop", "sign", "is", "behind", "the", "fence"]`
- 错误 contrast hull：`["fence", "is", "behind", "the", "stop", "sign"]`
- 共同后缀：`["instead", "of", "on", "the", "street"]`
- Hull token 覆盖率（正/负/最大）：`[0.5294117647058824, 0.5294117647058824, 0.5294117647058824]`
- 共同前缀模型 token：`[4345]`
- 正确 hull 模型 token：IDs `[580, 1506, 2185, 395, 5237, 916, 309, 341, 944]`；text " stop sign is behind the fence"
- 错误 hull 模型 token：IDs `[341, 944, 395, 5237, 916, 309, 580, 1506, 2185]`；text " fence is behind the stop sign"
- 第一轮/第二轮分类：`complex_edit` / `multi_block_local_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 30. `swap_object:92`

- 负例类型/范围：`swap_object` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A sculpture of two persons stting on a bench with their purses on the ground while people standing in a line behind them. "
- 原始正描述 2："A bench contains a sculpture of two persons sitting on it with their purses on the ground, while people stand in a line behind them."
- 原始负描述："A sculpture of people standing in a line on a bench with their purses on the ground while two persons sit behind them."
- 规范化正描述 1："a sculpture of two persons stting on a bench with their purses on the ground while people standing in a line behind them"
- 规范化正描述 2："a bench contains a sculpture of two persons sitting on it with their purses on the ground , while people stand in a line behind them"
- 规范化负描述："a sculpture of people standing in a line on a bench with their purses on the ground while two persons sit behind them"
- 正描述 1 选择元组：`[16, 36, 4, 0.43478260869565216, 0.30833333333333335]`
- 正描述 2 选择元组：`[29, 43, 4, 0.6153846153846154, 0.45454545454545453]`
- 最终比较正描述：`positive_1` / "A sculpture of two persons stting on a bench with their purses on the ground while people standing in a line behind them. "
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 3, "negative_start": 0, "negative_end": 3, "positive_lexemes": ["a", "sculpture", "of"], "negative_lexemes": ["a", "sculpture", "of"]}, {"tag": "insert", "positive_start": 3, "positive_end": 3, "negative_start": 3, "negative_end": 5, "positive_lexemes": [], "negative_lexemes": ["people", "standing"]}, {"tag": "replace", "positive_start": 3, "positive_end": 6, "negative_start": 5, "negative_end": 8, "positive_lexemes": ["two", "persons", "stting"], "negative_lexemes": ["in", "a", "line"]}, {"tag": "equal", "positive_start": 6, "positive_end": 16, "negative_start": 8, "negative_end": 18, "positive_lexemes": ["on", "a", "bench", "with", "their", "purses", "on", "the", "ground", "while"], "negative_lexemes": ["on", "a", "bench", "with", "their", "purses", "on", "the", "ground", "while"]}, {"tag": "delete", "positive_start": 16, "positive_end": 18, "negative_start": 18, "negative_end": 18, "positive_lexemes": ["people", "standing"], "negative_lexemes": []}, {"tag": "replace", "positive_start": 18, "positive_end": 21, "negative_start": 18, "negative_end": 21, "positive_lexemes": ["in", "a", "line"], "negative_lexemes": ["two", "persons", "sit"]}, {"tag": "equal", "positive_start": 21, "positive_end": 23, "negative_start": 21, "negative_end": 23, "positive_lexemes": ["behind", "them"], "negative_lexemes": ["behind", "them"]}]`
- 共同前缀：`["a", "sculpture", "of"]`
- 正确 contrast hull：`["two", "persons", "stting", "on", "a", "bench", "with", "their", "purses", "on", "the", "ground", "while", "people", "standing", "in", "a", "line"]`
- 错误 contrast hull：`["people", "standing", "in", "a", "line", "on", "a", "bench", "with", "their", "purses", "on", "the", "ground", "while", "two", "persons", "sit"]`
- 共同后缀：`["behind", "them"]`
- Hull token 覆盖率（正/负/最大）：`[0.7352941176470589, 0.7272727272727273, 0.7352941176470589]`
- 共同前缀模型 token：`[100, 1416, 549, 875, 745, 354]`
- 正确 hull 模型 token：IDs `[2102, 2198, 118, 580, 2912, 619, 299, 6141, 550, 599, 1635, 3315, 118, 329, 619, 309, 492, 2383, 3052, 2975, 2823, 350, 353, 299, 2909]`；text " two persons stting on a bench with their purses on the ground while people standing in a line"
- 错误 hull 模型 token：IDs `[2975, 2823, 350, 353, 299, 2909, 619, 299, 6141, 550, 599, 1635, 3315, 118, 329, 619, 309, 492, 2383, 3052, 2102, 2198, 118, 5305]`；text " people standing in a line on a bench with their purses on the ground while two persons sit"
- 第一轮/第二轮分类：`complex_edit` / `multi_block_local_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

## Hull 覆盖 75%–90%

候选 `282` 条，本节抽取 `30` 条。

### 1. `replace_attribute:155`

- 负例类型/范围：`replace_attribute` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": false}`
- 原始正描述 1："A black and brown dog wearing a chain around it's neck."
- 原始正描述 2："A dog with a brown and black coat and a chain around its neck."
- 原始负描述："A white and brown dog wearing a chain around its neck."
- 规范化正描述 1："a black and brown dog wearing a chain around it's neck"
- 规范化正描述 2："a dog with a brown and black coat and a chain around its neck"
- 规范化负描述："a white and brown dog wearing a chain around its neck"
- 正描述 1 选择元组：`[4, 18, 2, 0.18181818181818182, 0.1111111111111111]`
- 正描述 2 选择元组：`[11, 15, 3, 0.5, 0.36065573770491804]`
- 最终比较正描述：`positive_1` / "A black and brown dog wearing a chain around it's neck."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 1, "negative_start": 0, "negative_end": 1, "positive_lexemes": ["a"], "negative_lexemes": ["a"]}, {"tag": "replace", "positive_start": 1, "positive_end": 2, "negative_start": 1, "negative_end": 2, "positive_lexemes": ["black"], "negative_lexemes": ["white"]}, {"tag": "equal", "positive_start": 2, "positive_end": 9, "negative_start": 2, "negative_end": 9, "positive_lexemes": ["and", "brown", "dog", "wearing", "a", "chain", "around"], "negative_lexemes": ["and", "brown", "dog", "wearing", "a", "chain", "around"]}, {"tag": "replace", "positive_start": 9, "positive_end": 10, "negative_start": 9, "negative_end": 10, "positive_lexemes": ["it's"], "negative_lexemes": ["its"]}, {"tag": "equal", "positive_start": 10, "positive_end": 11, "negative_start": 10, "negative_end": 11, "positive_lexemes": ["neck"], "negative_lexemes": ["neck"]}]`
- 共同前缀：`["a"]`
- 正确 contrast hull：`["black", "and", "brown", "dog", "wearing", "a", "chain", "around", "it's"]`
- 错误 contrast hull：`["white", "and", "brown", "dog", "wearing", "a", "chain", "around", "its"]`
- 共同后缀：`["neck"]`
- Hull token 覆盖率（正/负/最大）：`[0.85, 0.8421052631578947, 0.85]`
- 共同前缀模型 token：`[100]`
- 正确 hull 模型 token：IDs `[2597, 1637, 376, 363, 2079, 113, 1041, 106, 796, 370, 350, 299, 890, 740, 3364, 563, 628]`；text " black and brown dog wearing a chain around it's"
- 错误 hull 模型 token：IDs `[654, 1078, 376, 363, 2079, 113, 1041, 106, 796, 370, 350, 299, 890, 740, 3364, 1342]`；text " white and brown dog wearing a chain around its"
- 第一轮/第二轮分类：`complex_edit` / `large_contrast_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；"maximum_hull_token_coverage_above_75_percent"

### 2. `replace_attribute:708`

- 负例类型/范围：`replace_attribute` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A young person kissing the top of a young person's head."
- 原始正描述 2："A young person is being kissed on the top of their head by another young person."
- 原始负描述："An elderly person kissing the top of an elderly person's head."
- 规范化正描述 1："a young person kissing the top of a young person's head"
- 规范化正描述 2："a young person is being kissed on the top of their head by another young person"
- 规范化负描述："an elderly person kissing the top of an elderly person's head"
- 正描述 1 选择元组：`[8, 18, 2, 0.36363636363636365, 0.26229508196721313]`
- 正描述 2 选择元组：`[19, 27, 5, 0.75, 0.5949367088607594]`
- 最终比较正描述：`positive_1` / "A young person kissing the top of a young person's head."
- 完整 lexeme 编辑块：`[{"tag": "replace", "positive_start": 0, "positive_end": 2, "negative_start": 0, "negative_end": 2, "positive_lexemes": ["a", "young"], "negative_lexemes": ["an", "elderly"]}, {"tag": "equal", "positive_start": 2, "positive_end": 7, "negative_start": 2, "negative_end": 7, "positive_lexemes": ["person", "kissing", "the", "top", "of"], "negative_lexemes": ["person", "kissing", "the", "top", "of"]}, {"tag": "replace", "positive_start": 7, "positive_end": 9, "negative_start": 7, "negative_end": 9, "positive_lexemes": ["a", "young"], "negative_lexemes": ["an", "elderly"]}, {"tag": "equal", "positive_start": 9, "positive_end": 11, "negative_start": 9, "negative_end": 11, "positive_lexemes": ["person's", "head"], "negative_lexemes": ["person's", "head"]}]`
- 共同前缀：`[]`
- 正确 contrast hull：`["a", "young", "person", "kissing", "the", "top", "of", "a", "young"]`
- 错误 contrast hull：`["an", "elderly", "person", "kissing", "the", "top", "of", "an", "elderly"]`
- 共同后缀：`["person's", "head"]`
- Hull token 覆盖率（正/负/最大）：`[0.8125, 0.85, 0.85]`
- 共同前缀模型 token：`[]`
- 正确 hull 模型 token：IDs `[100, 401, 1685, 2198, 914, 3151, 350, 309, 2924, 354, 299, 401, 1685]`；text "a young person kissing the top of a young"
- 错误 hull 模型 token：IDs `[325, 413, 674, 311, 542, 2198, 914, 3151, 350, 309, 2924, 354, 346, 413, 674, 311, 542]`；text "an elderly person kissing the top of an elderly"
- 第一轮/第二轮分类：`complex_edit` / `large_contrast_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；"maximum_hull_token_coverage_above_75_percent"

### 3. `replace_attribute:769`

- 负例类型/范围：`replace_attribute` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A person wearing a skirt shows off their tatttoos"
- 原始正描述 2："A person is wearing a skirt and displaying their tattoos."
- 原始负描述："A person not wearing a skirt shows off their tattoos."
- 规范化正描述 1："a person wearing a skirt shows off their tatttoos"
- 规范化正描述 2："a person is wearing a skirt and displaying their tattoos"
- 规范化负描述："a person not wearing a skirt shows off their tattoos"
- 正描述 1 选择元组：`[3, 15, 2, 0.2, 0.09615384615384616]`
- 正描述 2 选择元组：`[6, 12, 2, 0.3, 0.2857142857142857]`
- 最终比较正描述：`positive_1` / "A person wearing a skirt shows off their tatttoos"
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 2, "negative_start": 0, "negative_end": 2, "positive_lexemes": ["a", "person"], "negative_lexemes": ["a", "person"]}, {"tag": "insert", "positive_start": 2, "positive_end": 2, "negative_start": 2, "negative_end": 3, "positive_lexemes": [], "negative_lexemes": ["not"]}, {"tag": "equal", "positive_start": 2, "positive_end": 8, "negative_start": 3, "negative_end": 9, "positive_lexemes": ["wearing", "a", "skirt", "shows", "off", "their"], "negative_lexemes": ["wearing", "a", "skirt", "shows", "off", "their"]}, {"tag": "replace", "positive_start": 8, "positive_end": 9, "negative_start": 9, "negative_end": 10, "positive_lexemes": ["tatttoos"], "negative_lexemes": ["tattoos"]}]`
- 共同前缀：`["a", "person"]`
- 正确 contrast hull：`["wearing", "a", "skirt", "shows", "off", "their", "tatttoos"]`
- 错误 contrast hull：`["not", "wearing", "a", "skirt", "shows", "off", "their", "tattoos"]`
- 共同后缀：`[]`
- Hull token 覆盖率（正/负/最大）：`[0.8888888888888888, 0.8888888888888888, 0.8888888888888888]`
- 共同前缀模型 token：`[100, 2198]`
- 正确 hull 模型 token：IDs `[796, 370, 350, 299, 2549, 4193, 1128, 3032, 1690, 1635, 297, 314, 119, 119, 824, 118]`；text " wearing a skirt shows off their tatttoos"
- 错误 hull 模型 token：IDs `[1027, 796, 370, 350, 299, 2549, 4193, 1128, 3032, 1690, 1635, 297, 314, 119, 824, 118]`；text " not wearing a skirt shows off their tattoos"
- 第一轮/第二轮分类：`complex_edit` / `large_contrast_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；"maximum_hull_token_coverage_above_75_percent"

### 4. `replace_object:213`

- 负例类型/范围：`replace_object` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A person in a green shirt is taking a picture with his cell phone."
- 原始正描述 2："An individual wearing a green shirt is using his cell phone to take a photo."
- 原始负描述："A woman in a green shirt is taking a picture with her cell phone."
- 规范化正描述 1："a person in a green shirt is taking a picture with his cell phone"
- 规范化正描述 2："an individual wearing a green shirt is using his cell phone to take a photo"
- 规范化负描述："a woman in a green shirt is taking a picture with her cell phone"
- 正描述 1 选择元组：`[4, 22, 2, 0.14285714285714285, 0.1076923076923077]`
- 正描述 2 选择元组：`[21, 29, 3, 0.7333333333333333, 0.5466666666666666]`
- 最终比较正描述：`positive_1` / "A person in a green shirt is taking a picture with his cell phone."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 1, "negative_start": 0, "negative_end": 1, "positive_lexemes": ["a"], "negative_lexemes": ["a"]}, {"tag": "replace", "positive_start": 1, "positive_end": 2, "negative_start": 1, "negative_end": 2, "positive_lexemes": ["person"], "negative_lexemes": ["woman"]}, {"tag": "equal", "positive_start": 2, "positive_end": 11, "negative_start": 2, "negative_end": 11, "positive_lexemes": ["in", "a", "green", "shirt", "is", "taking", "a", "picture", "with"], "negative_lexemes": ["in", "a", "green", "shirt", "is", "taking", "a", "picture", "with"]}, {"tag": "replace", "positive_start": 11, "positive_end": 12, "negative_start": 11, "negative_end": 12, "positive_lexemes": ["his"], "negative_lexemes": ["her"]}, {"tag": "equal", "positive_start": 12, "positive_end": 14, "negative_start": 12, "negative_end": 14, "positive_lexemes": ["cell", "phone"], "negative_lexemes": ["cell", "phone"]}]`
- 共同前缀：`["a"]`
- 正确 contrast hull：`["person", "in", "a", "green", "shirt", "is", "taking", "a", "picture", "with", "his"]`
- 错误 contrast hull：`["woman", "in", "a", "green", "shirt", "is", "taking", "a", "picture", "with", "her"]`
- 共同后缀：`["cell", "phone"]`
- Hull token 覆盖率（正/负/最大）：`[0.75, 0.7727272727272727, 0.7727272727272727]`
- 共同前缀模型 token：`[100]`
- 正确 hull 模型 token：IDs `[2198, 353, 299, 5921, 1128, 4193, 395, 297, 5784, 299, 344, 2030, 745, 599, 2049]`；text " person in a green shirt is taking a picture with his"
- 错误 hull 模型 token：IDs `[339, 444, 325, 353, 299, 5921, 1128, 4193, 395, 297, 5784, 299, 344, 2030, 745, 599, 2833]`；text " woman in a green shirt is taking a picture with her"
- 第一轮/第二轮分类：`complex_edit` / `large_contrast_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；"maximum_hull_token_coverage_above_75_percent"

### 5. `replace_object:26`

- 负例类型/范围：`replace_object` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A woman taking a picture up at the sky with her phone."
- 原始正描述 2："A woman is positioned below the sky with her phone, taking a picture upwards."
- 原始负描述："A man taking a picture up at the sky with his phone."
- 规范化正描述 1："a woman taking a picture up at the sky with her phone"
- 规范化正描述 2："a woman is positioned below the sky with her phone , taking a picture upwards"
- 规范化负描述："a man taking a picture up at the sky with his phone"
- 正描述 1 选择元组：`[4, 20, 2, 0.16666666666666666, 0.07547169811320754]`
- 正描述 2 选择元组：`[17, 25, 4, 0.8, 0.6363636363636364]`
- 最终比较正描述：`positive_1` / "A woman taking a picture up at the sky with her phone."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 1, "negative_start": 0, "negative_end": 1, "positive_lexemes": ["a"], "negative_lexemes": ["a"]}, {"tag": "replace", "positive_start": 1, "positive_end": 2, "negative_start": 1, "negative_end": 2, "positive_lexemes": ["woman"], "negative_lexemes": ["man"]}, {"tag": "equal", "positive_start": 2, "positive_end": 10, "negative_start": 2, "negative_end": 10, "positive_lexemes": ["taking", "a", "picture", "up", "at", "the", "sky", "with"], "negative_lexemes": ["taking", "a", "picture", "up", "at", "the", "sky", "with"]}, {"tag": "replace", "positive_start": 10, "positive_end": 11, "negative_start": 10, "negative_end": 11, "positive_lexemes": ["her"], "negative_lexemes": ["his"]}, {"tag": "equal", "positive_start": 11, "positive_end": 12, "negative_start": 11, "negative_end": 12, "positive_lexemes": ["phone"], "negative_lexemes": ["phone"]}]`
- 共同前缀：`["a"]`
- 正确 contrast hull：`["woman", "taking", "a", "picture", "up", "at", "the", "sky", "with", "her"]`
- 错误 contrast hull：`["man", "taking", "a", "picture", "up", "at", "the", "sky", "with", "his"]`
- 共同后缀：`["phone"]`
- Hull token 覆盖率（正/负/最大）：`[0.8333333333333334, 0.8125, 0.8333333333333334]`
- 共同前缀模型 token：`[100]`
- 正确 hull 模型 token：IDs `[339, 444, 325, 297, 5784, 299, 344, 2030, 745, 1253, 1248, 309, 3716, 599, 2833]`；text " woman taking a picture up at the sky with her"
- 错误 hull 模型 token：IDs `[1672, 297, 5784, 299, 344, 2030, 745, 1253, 1248, 309, 3716, 599, 2049]`；text " man taking a picture up at the sky with his"
- 第一轮/第二轮分类：`complex_edit` / `large_contrast_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；"maximum_hull_token_coverage_above_75_percent"

### 6. `replace_object:43`

- 负例类型/范围：`replace_object` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："a man with a tennis racket gets ready to swing his racket "
- 原始正描述 2："A man with a tennis racket is preparing to swing his racket."
- 原始负描述："A woman with a tennis racket gets ready to swing her racket."
- 规范化正描述 1："a man with a tennis racket gets ready to swing his racket"
- 规范化正描述 2："a man with a tennis racket is preparing to swing his racket"
- 规范化负描述："a woman with a tennis racket gets ready to swing her racket"
- 正描述 1 选择元组：`[4, 20, 2, 0.16666666666666666, 0.06779661016949153]`
- 正描述 2 选择元组：`[8, 20, 3, 0.3333333333333333, 0.22033898305084745]`
- 最终比较正描述：`positive_1` / "a man with a tennis racket gets ready to swing his racket "
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 1, "negative_start": 0, "negative_end": 1, "positive_lexemes": ["a"], "negative_lexemes": ["a"]}, {"tag": "replace", "positive_start": 1, "positive_end": 2, "negative_start": 1, "negative_end": 2, "positive_lexemes": ["man"], "negative_lexemes": ["woman"]}, {"tag": "equal", "positive_start": 2, "positive_end": 10, "negative_start": 2, "negative_end": 10, "positive_lexemes": ["with", "a", "tennis", "racket", "gets", "ready", "to", "swing"], "negative_lexemes": ["with", "a", "tennis", "racket", "gets", "ready", "to", "swing"]}, {"tag": "replace", "positive_start": 10, "positive_end": 11, "negative_start": 10, "negative_end": 11, "positive_lexemes": ["his"], "negative_lexemes": ["her"]}, {"tag": "equal", "positive_start": 11, "positive_end": 12, "negative_start": 11, "negative_end": 12, "positive_lexemes": ["racket"], "negative_lexemes": ["racket"]}]`
- 共同前缀：`["a"]`
- 正确 contrast hull：`["man", "with", "a", "tennis", "racket", "gets", "ready", "to", "swing", "his"]`
- 错误 contrast hull：`["woman", "with", "a", "tennis", "racket", "gets", "ready", "to", "swing", "her"]`
- 共同后缀：`["racket"]`
- Hull token 覆盖率（正/负/最大）：`[0.8181818181818182, 0.8333333333333334, 0.8333333333333334]`
- 共同前缀模型 token：`[100]`
- 正确 hull 模型 token：IDs `[1672, 599, 299, 297, 6201, 324, 2265, 892, 439, 2350, 118, 3094, 124, 364, 316, 122, 350, 2049]`；text " man with a tennis racket gets ready to swing his"
- 错误 hull 模型 token：IDs `[339, 444, 325, 599, 299, 297, 6201, 324, 2265, 892, 439, 2350, 118, 3094, 124, 364, 316, 122, 350, 2833]`；text " woman with a tennis racket gets ready to swing her"
- 第一轮/第二轮分类：`complex_edit` / `large_contrast_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；"maximum_hull_token_coverage_above_75_percent"

### 7. `replace_object:834`

- 负例类型/范围：`replace_object` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："The boats are in the water for a peaceful night."
- 原始正描述 2："The boats are floating peacefully in the water for a tranquil night."
- 原始负描述："The jetskis are in the water for a thrilling night."
- 规范化正描述 1："the boats are in the water for a peaceful night"
- 规范化正描述 2："the boats are floating peacefully in the water for a tranquil night"
- 规范化负描述："the jetskis are in the water for a thrilling night"
- 正描述 1 选择元组：`[4, 16, 2, 0.2, 0.3]`
- 正描述 2 选择元组：`[6, 18, 3, 0.3333333333333333, 0.44776119402985076]`
- 最终比较正描述：`positive_1` / "The boats are in the water for a peaceful night."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 1, "negative_start": 0, "negative_end": 1, "positive_lexemes": ["the"], "negative_lexemes": ["the"]}, {"tag": "replace", "positive_start": 1, "positive_end": 2, "negative_start": 1, "negative_end": 2, "positive_lexemes": ["boats"], "negative_lexemes": ["jetskis"]}, {"tag": "equal", "positive_start": 2, "positive_end": 8, "negative_start": 2, "negative_end": 8, "positive_lexemes": ["are", "in", "the", "water", "for", "a"], "negative_lexemes": ["are", "in", "the", "water", "for", "a"]}, {"tag": "replace", "positive_start": 8, "positive_end": 9, "negative_start": 8, "negative_end": 9, "positive_lexemes": ["peaceful"], "negative_lexemes": ["thrilling"]}, {"tag": "equal", "positive_start": 9, "positive_end": 10, "negative_start": 9, "negative_end": 10, "positive_lexemes": ["night"], "negative_lexemes": ["night"]}]`
- 共同前缀：`["the"]`
- 正确 contrast hull：`["boats", "are", "in", "the", "water", "for", "a", "peaceful"]`
- 错误 contrast hull：`["jetskis", "are", "in", "the", "water", "for", "a", "thrilling"]`
- 共同后缀：`["night"]`
- Hull token 覆盖率（正/负/最大）：`[0.8461538461538461, 0.875, 0.875]`
- 共同前缀模型 token：`[4345]`
- 正确 hull 模型 token：IDs `[1847, 4585, 732, 353, 309, 3949, 503, 299, 2188, 1489, 1930]`；text " boats are in the water for a peaceful"
- 错误 hull 模型 token：IDs `[1315, 3391, 110, 324, 732, 353, 309, 3949, 503, 299, 445, 117, 959, 350]`；text " jetskis are in the water for a thrilling"
- 第一轮/第二轮分类：`complex_edit` / `large_contrast_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；"maximum_hull_token_coverage_above_75_percent"

### 8. `replace_object:876`

- 负例类型/范围：`replace_object` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A man has stick, which is holding some bread, between his fingers."
- 原始正描述 2："The man holds a stick between his fingers, which is holding some bread."
- 原始负描述："A woman has stick, which is holding some bread, between her fingers."
- 规范化正描述 1："a man has stick , which is holding some bread , between his fingers"
- 规范化正描述 2："the man holds a stick between his fingers , which is holding some bread"
- 规范化负描述："a woman has stick , which is holding some bread , between her fingers"
- 正描述 1 选择元组：`[4, 24, 2, 0.14285714285714285, 0.057971014492753624]`
- 正描述 2 选择元组：`[14, 28, 4, 0.7857142857142857, 0.704225352112676]`
- 最终比较正描述：`positive_1` / "A man has stick, which is holding some bread, between his fingers."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 1, "negative_start": 0, "negative_end": 1, "positive_lexemes": ["a"], "negative_lexemes": ["a"]}, {"tag": "replace", "positive_start": 1, "positive_end": 2, "negative_start": 1, "negative_end": 2, "positive_lexemes": ["man"], "negative_lexemes": ["woman"]}, {"tag": "equal", "positive_start": 2, "positive_end": 12, "negative_start": 2, "negative_end": 12, "positive_lexemes": ["has", "stick", ",", "which", "is", "holding", "some", "bread", ",", "between"], "negative_lexemes": ["has", "stick", ",", "which", "is", "holding", "some", "bread", ",", "between"]}, {"tag": "replace", "positive_start": 12, "positive_end": 13, "negative_start": 12, "negative_end": 13, "positive_lexemes": ["his"], "negative_lexemes": ["her"]}, {"tag": "equal", "positive_start": 13, "positive_end": 14, "negative_start": 13, "negative_end": 14, "positive_lexemes": ["fingers"], "negative_lexemes": ["fingers"]}]`
- 共同前缀：`["a"]`
- 正确 contrast hull：`["man", "has", "stick", ",", "which", "is", "holding", "some", "bread", ",", "between", "his"]`
- 错误 contrast hull：`["woman", "has", "stick", ",", "which", "is", "holding", "some", "bread", ",", "between", "her"]`
- 共同后缀：`["fingers"]`
- Hull token 覆盖率（正/负/最大）：`[0.8181818181818182, 0.8333333333333334, 0.8333333333333334]`
- 共同前缀模型 token：`[100]`
- 正确 hull 模型 token：IDs `[1672, 1290, 580, 2437, 256, 47, 1045, 395, 429, 2569, 350, 2104, 3170, 785, 256, 47, 2172, 2049]`；text " man has stick , which is holding some bread , between his"
- 错误 hull 模型 token：IDs `[339, 444, 325, 1290, 580, 2437, 256, 47, 1045, 395, 429, 2569, 350, 2104, 3170, 785, 256, 47, 2172, 2833]`；text " woman has stick , which is holding some bread , between her"
- 第一轮/第二轮分类：`complex_edit` / `large_contrast_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；"maximum_hull_token_coverage_above_75_percent"

### 9. `replace_relation:1362`

- 负例类型/范围：`replace_relation` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A person on skis fly through the sky"
- 原始正描述 2："An individual fly through the sky on skis."
- 原始负描述："A person off skis lands on the ground."
- 规范化正描述 1："a person on skis fly through the sky"
- 规范化正描述 2："an individual fly through the sky on skis"
- 规范化负描述："a person off skis lands on the ground"
- 正描述 1 选择元组：`[8, 12, 3, 0.5, 0.4594594594594595]`
- 正描述 2 选择元组：`[16, 16, 1, 1.0, 0.8048780487804879]`
- 最终比较正描述：`positive_1` / "A person on skis fly through the sky"
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 2, "negative_start": 0, "negative_end": 2, "positive_lexemes": ["a", "person"], "negative_lexemes": ["a", "person"]}, {"tag": "replace", "positive_start": 2, "positive_end": 3, "negative_start": 2, "negative_end": 3, "positive_lexemes": ["on"], "negative_lexemes": ["off"]}, {"tag": "equal", "positive_start": 3, "positive_end": 4, "negative_start": 3, "negative_end": 4, "positive_lexemes": ["skis"], "negative_lexemes": ["skis"]}, {"tag": "replace", "positive_start": 4, "positive_end": 6, "negative_start": 4, "negative_end": 6, "positive_lexemes": ["fly", "through"], "negative_lexemes": ["lands", "on"]}, {"tag": "equal", "positive_start": 6, "positive_end": 7, "negative_start": 6, "negative_end": 7, "positive_lexemes": ["the"], "negative_lexemes": ["the"]}, {"tag": "replace", "positive_start": 7, "positive_end": 8, "negative_start": 7, "negative_end": 8, "positive_lexemes": ["sky"], "negative_lexemes": ["ground"]}]`
- 共同前缀：`["a", "person"]`
- 正确 contrast hull：`["on", "skis", "fly", "through", "the", "sky"]`
- 错误 contrast hull：`["off", "skis", "lands", "on", "the", "ground"]`
- 共同后缀：`[]`
- Hull token 覆盖率（正/负/最大）：`[0.8, 0.8181818181818182, 0.8181818181818182]`
- 共同前缀模型 token：`[100, 2198]`
- 正确 hull 模型 token：IDs `[619, 2549, 324, 341, 542, 2309, 309, 3716]`；text " on skis fly through the sky"
- 错误 hull 模型 token：IDs `[1690, 2549, 324, 4768, 118, 619, 309, 492, 2383]`；text " off skis lands on the ground"
- 第一轮/第二轮分类：`complex_edit` / `large_contrast_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；"maximum_hull_token_coverage_above_75_percent"

### 10. `swap_atribute:154`

- 负例类型/范围：`swap_atribute` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："person on steps with tray of grilled hot dogs on buns."
- 原始正描述 2："The person is standing on the steps with a tray of grilled hot dogs on buns."
- 原始负描述："person not on steps with tray of hot dogs on grilled buns."
- 规范化正描述 1："person on steps with tray of grilled hot dogs on buns"
- 规范化正描述 2："the person is standing on the steps with a tray of grilled hot dogs on buns"
- 规范化负描述："person not on steps with tray of hot dogs on grilled buns"
- 正描述 1 选择元组：`[3, 19, 3, 0.25, 0.3508771929824561]`
- 正描述 2 选择元组：`[8, 26, 7, 0.4375, 0.48]`
- 最终比较正描述：`positive_1` / "person on steps with tray of grilled hot dogs on buns."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 1, "negative_start": 0, "negative_end": 1, "positive_lexemes": ["person"], "negative_lexemes": ["person"]}, {"tag": "insert", "positive_start": 1, "positive_end": 1, "negative_start": 1, "negative_end": 2, "positive_lexemes": [], "negative_lexemes": ["not"]}, {"tag": "equal", "positive_start": 1, "positive_end": 6, "negative_start": 2, "negative_end": 7, "positive_lexemes": ["on", "steps", "with", "tray", "of"], "negative_lexemes": ["on", "steps", "with", "tray", "of"]}, {"tag": "delete", "positive_start": 6, "positive_end": 7, "negative_start": 7, "negative_end": 7, "positive_lexemes": ["grilled"], "negative_lexemes": []}, {"tag": "equal", "positive_start": 7, "positive_end": 10, "negative_start": 7, "negative_end": 10, "positive_lexemes": ["hot", "dogs", "on"], "negative_lexemes": ["hot", "dogs", "on"]}, {"tag": "insert", "positive_start": 10, "positive_end": 10, "negative_start": 10, "negative_end": 11, "positive_lexemes": [], "negative_lexemes": ["grilled"]}, {"tag": "equal", "positive_start": 10, "positive_end": 11, "negative_start": 11, "negative_end": 12, "positive_lexemes": ["buns"], "negative_lexemes": ["buns"]}]`
- 共同前缀：`["person"]`
- 正确 contrast hull：`["on", "steps", "with", "tray", "of", "grilled", "hot", "dogs", "on"]`
- 错误 contrast hull：`["not", "on", "steps", "with", "tray", "of", "hot", "dogs", "on", "grilled"]`
- 共同后缀：`["buns"]`
- Hull token 覆盖率（正/负/最大）：`[0.75, 0.7619047619047619, 0.7619047619047619]`
- 共同前缀模型 token：`[115, 2019]`
- 正确 hull 模型 token：IDs `[619, 5243, 599, 1946, 124, 354, 492, 117, 485, 2003, 429, 593, 1041, 4474, 619]`；text " on steps with tray of grilled hot dogs on"
- 错误 hull 模型 token：IDs `[1027, 619, 5243, 599, 1946, 124, 354, 429, 593, 1041, 4474, 619, 492, 117, 485, 2003]`；text " not on steps with tray of hot dogs on grilled"
- 第一轮/第二轮分类：`complex_edit` / `large_contrast_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；"maximum_hull_token_coverage_above_75_percent"

### 11. `swap_atribute:303`

- 负例类型/范围：`swap_atribute` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A person falling asleep next to another person, who are both sitting down."
- 原始正描述 2："A person is sitting next to another person, both of whom are falling asleep while sitting down."
- 原始负描述："A person sitting down next to another person, who are both falling asleep."
- 规范化正描述 1："a person falling asleep next to another person , who are both sitting down"
- 规范化正描述 2："a person is sitting next to another person , both of whom are falling asleep while sitting down"
- 规范化负描述："a person sitting down next to another person , who are both falling asleep"
- 正描述 1 选择元组：`[8, 24, 2, 0.2857142857142857, 0.2702702702702703]`
- 正描述 2 选择元组：`[14, 28, 4, 0.5, 0.42105263157894735]`
- 最终比较正描述：`positive_1` / "A person falling asleep next to another person, who are both sitting down."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 2, "negative_start": 0, "negative_end": 2, "positive_lexemes": ["a", "person"], "negative_lexemes": ["a", "person"]}, {"tag": "replace", "positive_start": 2, "positive_end": 4, "negative_start": 2, "negative_end": 4, "positive_lexemes": ["falling", "asleep"], "negative_lexemes": ["sitting", "down"]}, {"tag": "equal", "positive_start": 4, "positive_end": 12, "negative_start": 4, "negative_end": 12, "positive_lexemes": ["next", "to", "another", "person", ",", "who", "are", "both"], "negative_lexemes": ["next", "to", "another", "person", ",", "who", "are", "both"]}, {"tag": "replace", "positive_start": 12, "positive_end": 14, "negative_start": 12, "negative_end": 14, "positive_lexemes": ["sitting", "down"], "negative_lexemes": ["falling", "asleep"]}]`
- 共同前缀：`["a", "person"]`
- 正确 contrast hull：`["falling", "asleep", "next", "to", "another", "person", ",", "who", "are", "both", "sitting", "down"]`
- 错误 contrast hull：`["sitting", "down", "next", "to", "another", "person", ",", "who", "are", "both", "falling", "asleep"]`
- 共同后缀：`[]`
- Hull token 覆盖率（正/负/最大）：`[0.8947368421052632, 0.8947368421052632, 0.8947368421052632]`
- 共同前缀模型 token：`[100, 2198]`
- 正确 hull 模型 token：IDs `[6347, 350, 523, 361, 1522, 4658, 364, 5467, 2198, 256, 47, 2109, 732, 2206, 5305, 2912, 4076]`；text " falling asleep next to another person , who are both sitting down"
- 错误 hull 模型 token：IDs `[5305, 2912, 4076, 4658, 364, 5467, 2198, 256, 47, 2109, 732, 2206, 6347, 350, 523, 361, 1522]`；text " sitting down next to another person , who are both falling asleep"
- 第一轮/第二轮分类：`ambiguous_source` / `large_contrast_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；"maximum_hull_token_coverage_above_75_percent"

### 12. `swap_atribute:325`

- 负例类型/范围：`swap_atribute` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A red stop sign sitting on the side of a dark road."
- 原始正描述 2："A red stop sign is positioned on the side of a dark road."
- 原始负描述："A dark stop sign sitting on the side of a red road."
- 规范化正描述 1："a red stop sign sitting on the side of a dark road"
- 规范化正描述 2："a red stop sign is positioned on the side of a dark road"
- 规范化负描述："a dark stop sign sitting on the side of a red road"
- 正描述 1 选择元组：`[4, 20, 2, 0.16666666666666666, 0.16]`
- 正描述 2 选择元组：`[7, 21, 4, 0.3076923076923077, 0.30357142857142855]`
- 最终比较正描述：`positive_1` / "A red stop sign sitting on the side of a dark road."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 1, "negative_start": 0, "negative_end": 1, "positive_lexemes": ["a"], "negative_lexemes": ["a"]}, {"tag": "replace", "positive_start": 1, "positive_end": 2, "negative_start": 1, "negative_end": 2, "positive_lexemes": ["red"], "negative_lexemes": ["dark"]}, {"tag": "equal", "positive_start": 2, "positive_end": 10, "negative_start": 2, "negative_end": 10, "positive_lexemes": ["stop", "sign", "sitting", "on", "the", "side", "of", "a"], "negative_lexemes": ["stop", "sign", "sitting", "on", "the", "side", "of", "a"]}, {"tag": "replace", "positive_start": 10, "positive_end": 11, "negative_start": 10, "negative_end": 11, "positive_lexemes": ["dark"], "negative_lexemes": ["red"]}, {"tag": "equal", "positive_start": 11, "positive_end": 12, "negative_start": 11, "negative_end": 12, "positive_lexemes": ["road"], "negative_lexemes": ["road"]}]`
- 共同前缀：`["a"]`
- 正确 contrast hull：`["red", "stop", "sign", "sitting", "on", "the", "side", "of", "a", "dark"]`
- 错误 contrast hull：`["dark", "stop", "sign", "sitting", "on", "the", "side", "of", "a", "red"]`
- 共同后缀：`["road"]`
- Hull token 覆盖率（正/负/最大）：`[0.8125, 0.8125, 0.8125]`
- 共同前缀模型 token：`[100]`
- 正确 hull 模型 token：IDs `[5534, 580, 1506, 2185, 5305, 2912, 619, 309, 5046, 354, 299, 373, 2000]`；text " red stop sign sitting on the side of a dark"
- 错误 hull 模型 token：IDs `[373, 2000, 580, 1506, 2185, 5305, 2912, 619, 309, 5046, 354, 299, 5534]`；text " dark stop sign sitting on the side of a red"
- 第一轮/第二轮分类：`complex_edit` / `large_contrast_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；"maximum_hull_token_coverage_above_75_percent"

### 13. `swap_atribute:333`

- 负例类型/范围：`swap_atribute` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："Orange and brown cat sitting on top of white shoes."
- 原始正描述 2："The orange and brown cat are sitting on top of white shoes, with the shoes positioned beneath the cat."
- 原始负描述："White and brown cat sitting on top of orange shoes."
- 规范化正描述 1："orange and brown cat sitting on top of white shoes"
- 规范化正描述 2："the orange and brown cat are sitting on top of white shoes , with the shoes positioned beneath the cat"
- 规范化负描述："white and brown cat sitting on top of orange shoes"
- 正描述 1 选择元组：`[4, 18, 2, 0.2, 0.2]`
- 正描述 2 选择元组：`[14, 30, 6, 0.6, 0.5784313725490197]`
- 最终比较正描述：`positive_1` / "Orange and brown cat sitting on top of white shoes."
- 完整 lexeme 编辑块：`[{"tag": "replace", "positive_start": 0, "positive_end": 1, "negative_start": 0, "negative_end": 1, "positive_lexemes": ["orange"], "negative_lexemes": ["white"]}, {"tag": "equal", "positive_start": 1, "positive_end": 8, "negative_start": 1, "negative_end": 8, "positive_lexemes": ["and", "brown", "cat", "sitting", "on", "top", "of"], "negative_lexemes": ["and", "brown", "cat", "sitting", "on", "top", "of"]}, {"tag": "replace", "positive_start": 8, "positive_end": 9, "negative_start": 8, "negative_end": 9, "positive_lexemes": ["white"], "negative_lexemes": ["orange"]}, {"tag": "equal", "positive_start": 9, "positive_end": 10, "negative_start": 9, "negative_end": 10, "positive_lexemes": ["shoes"], "negative_lexemes": ["shoes"]}]`
- 共同前缀：`[]`
- 正确 contrast hull：`["orange", "and", "brown", "cat", "sitting", "on", "top", "of", "white"]`
- 错误 contrast hull：`["white", "and", "brown", "cat", "sitting", "on", "top", "of", "orange"]`
- 共同后缀：`["shoes"]`
- Hull token 覆盖率（正/负/最大）：`[0.8235294117647058, 0.8235294117647058, 0.8235294117647058]`
- 共同前缀模型 token：`[]`
- 正确 hull 模型 token：IDs `[336, 1285, 376, 363, 2079, 113, 3706, 5305, 2912, 619, 2924, 354, 654, 1078]`；text "orange and brown cat sitting on top of white"
- 错误 hull 模型 token：IDs `[4465, 1078, 376, 363, 2079, 113, 3706, 5305, 2912, 619, 2924, 354, 522, 1285]`；text "white and brown cat sitting on top of orange"
- 第一轮/第二轮分类：`complex_edit` / `large_contrast_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；"maximum_hull_token_coverage_above_75_percent"

### 14. `swap_atribute:336`

- 负例类型/范围：`swap_atribute` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："An open-mouthed, leashed dog has its head outside of an unlocked car door window as a blurry park-like vista rushes by."
- 原始正描述 2："The leashed dog with an open mouth is positioned outside of the unlocked car door window, with a blurry park-like vista rushing past it."
- 原始负描述："A blurry, leashed dog has its head outside of an unlocked car door window as an open-mouthed park-like vista rushes by."
- 规范化正描述 1："an open-mouthed , leashed dog has its head outside of an unlocked car door window as a blurry park-like vista rushes by"
- 规范化正描述 2："the leashed dog with an open mouth is positioned outside of the unlocked car door window , with a blurry park-like vista rushing past it"
- 规范化负描述："a blurry , leashed dog has its head outside of an unlocked car door window as an open-mouthed park-like vista rushes by"
- 正描述 1 选择元组：`[8, 36, 2, 0.18181818181818182, 0.20168067226890757]`
- 正描述 2 选择元组：`[31, 47, 7, 0.68, 0.4632352941176471]`
- 最终比较正描述：`positive_1` / "An open-mouthed, leashed dog has its head outside of an unlocked car door window as a blurry park-like vista rushes by."
- 完整 lexeme 编辑块：`[{"tag": "replace", "positive_start": 0, "positive_end": 2, "negative_start": 0, "negative_end": 2, "positive_lexemes": ["an", "open-mouthed"], "negative_lexemes": ["a", "blurry"]}, {"tag": "equal", "positive_start": 2, "positive_end": 16, "negative_start": 2, "negative_end": 16, "positive_lexemes": [",", "leashed", "dog", "has", "its", "head", "outside", "of", "an", "unlocked", "car", "door", "window", "as"], "negative_lexemes": [",", "leashed", "dog", "has", "its", "head", "outside", "of", "an", "unlocked", "car", "door", "window", "as"]}, {"tag": "replace", "positive_start": 16, "positive_end": 18, "negative_start": 16, "negative_end": 18, "positive_lexemes": ["a", "blurry"], "negative_lexemes": ["an", "open-mouthed"]}, {"tag": "equal", "positive_start": 18, "positive_end": 22, "negative_start": 18, "negative_end": 22, "positive_lexemes": ["park-like", "vista", "rushes", "by"], "negative_lexemes": ["park-like", "vista", "rushes", "by"]}]`
- 共同前缀：`[]`
- 正确 contrast hull：`["an", "open-mouthed", ",", "leashed", "dog", "has", "its", "head", "outside", "of", "an", "unlocked", "car", "door", "window", "as", "a", "blurry"]`
- 错误 contrast hull：`["a", "blurry", ",", "leashed", "dog", "has", "its", "head", "outside", "of", "an", "unlocked", "car", "door", "window", "as", "an", "open-mouthed"]`
- 共同后缀：`["park-like", "vista", "rushes", "by"]`
- Hull token 覆盖率（正/负/最大）：`[0.7608695652173914, 0.7608695652173914, 0.7608695652173914]`
- 共同前缀模型 token：`[]`
- 正确 hull 模型 token：IDs `[325, 5102, 48, 112, 955, 3029, 256, 47, 848, 390, 3029, 1041, 106, 1290, 1342, 5308, 1695, 118, 688, 354, 346, 1406, 722, 892, 382, 3751, 1041, 336, 5472, 451, 523, 299, 2597, 543, 1557]`；text "an open-mouthed , leashed dog has its head outside of an unlocked car door window as a blurry"
- 错误 hull 模型 token：IDs `[100, 2597, 543, 1557, 256, 47, 848, 390, 3029, 1041, 106, 1290, 1342, 5308, 1695, 118, 688, 354, 346, 1406, 722, 892, 382, 3751, 1041, 336, 5472, 451, 523, 346, 5102, 48, 112, 955, 3029]`；text "a blurry , leashed dog has its head outside of an unlocked car door window as an open-mouthed"
- 第一轮/第二轮分类：`complex_edit` / `large_contrast_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；"maximum_hull_token_coverage_above_75_percent"

### 15. `swap_atribute:338`

- 负例类型/范围：`swap_atribute` / `{"canonical": true, "pilot": true, "formal": false, "certifying_formal": false}`
- 原始正描述 1："A red bus driving down a street next to a tall building."
- 原始正描述 2："A tall building is situated next to a red bus driving down a street."
- 原始负描述："A tall bus driving down a street next to a red building."
- 规范化正描述 1："a red bus driving down a street next to a tall building"
- 规范化正描述 2："a tall building is situated next to a red bus driving down a street"
- 规范化负描述："a tall bus driving down a street next to a red building"
- 正描述 1 选择元组：`[4, 20, 2, 0.16666666666666666, 0.14545454545454545]`
- 正描述 2 选择元组：`[14, 22, 4, 0.7142857142857143, 0.5223880597014925]`
- 最终比较正描述：`positive_1` / "A red bus driving down a street next to a tall building."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 1, "negative_start": 0, "negative_end": 1, "positive_lexemes": ["a"], "negative_lexemes": ["a"]}, {"tag": "replace", "positive_start": 1, "positive_end": 2, "negative_start": 1, "negative_end": 2, "positive_lexemes": ["red"], "negative_lexemes": ["tall"]}, {"tag": "equal", "positive_start": 2, "positive_end": 10, "negative_start": 2, "negative_end": 10, "positive_lexemes": ["bus", "driving", "down", "a", "street", "next", "to", "a"], "negative_lexemes": ["bus", "driving", "down", "a", "street", "next", "to", "a"]}, {"tag": "replace", "positive_start": 10, "positive_end": 11, "negative_start": 10, "negative_end": 11, "positive_lexemes": ["tall"], "negative_lexemes": ["red"]}, {"tag": "equal", "positive_start": 11, "positive_end": 12, "negative_start": 11, "negative_end": 12, "positive_lexemes": ["building"], "negative_lexemes": ["building"]}]`
- 共同前缀：`["a"]`
- 正确 contrast hull：`["red", "bus", "driving", "down", "a", "street", "next", "to", "a", "tall"]`
- 错误 contrast hull：`["tall", "bus", "driving", "down", "a", "street", "next", "to", "a", "red"]`
- 共同后缀：`["building"]`
- Hull token 覆盖率（正/负/最大）：`[0.8125, 0.8125, 0.8125]`
- 共同前缀模型 token：`[100]`
- 正确 hull 模型 token：IDs `[5534, 2499, 5893, 4917, 4076, 299, 5941, 439, 4658, 364, 299, 297, 1266]`；text " red bus driving down a street next to a tall"
- 错误 hull 模型 token：IDs `[297, 1266, 2499, 5893, 4917, 4076, 299, 5941, 439, 4658, 364, 299, 5534]`；text " tall bus driving down a street next to a red"
- 第一轮/第二轮分类：`complex_edit` / `large_contrast_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；"maximum_hull_token_coverage_above_75_percent"

### 16. `swap_atribute:353`

- 负例类型/范围：`swap_atribute` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A street light in front of a colorful train on a bridge."
- 原始正描述 2："A colorful train is on a bridge with a street light in front of it."
- 原始负描述："A colorful light in front of a train on a street bridge."
- 规范化正描述 1："a street light in front of a colorful train on a bridge"
- 规范化正描述 2："a colorful train is on a bridge with a street light in front of it"
- 规范化负描述："a colorful light in front of a train on a street bridge"
- 正描述 1 选择元组：`[4, 20, 3, 0.25, 0.41818181818181815]`
- 正描述 2 选择元组：`[17, 23, 5, 0.7333333333333333, 0.6060606060606061]`
- 最终比较正描述：`positive_1` / "A street light in front of a colorful train on a bridge."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 1, "negative_start": 0, "negative_end": 1, "positive_lexemes": ["a"], "negative_lexemes": ["a"]}, {"tag": "replace", "positive_start": 1, "positive_end": 2, "negative_start": 1, "negative_end": 2, "positive_lexemes": ["street"], "negative_lexemes": ["colorful"]}, {"tag": "equal", "positive_start": 2, "positive_end": 7, "negative_start": 2, "negative_end": 7, "positive_lexemes": ["light", "in", "front", "of", "a"], "negative_lexemes": ["light", "in", "front", "of", "a"]}, {"tag": "delete", "positive_start": 7, "positive_end": 8, "negative_start": 7, "negative_end": 7, "positive_lexemes": ["colorful"], "negative_lexemes": []}, {"tag": "equal", "positive_start": 8, "positive_end": 11, "negative_start": 7, "negative_end": 10, "positive_lexemes": ["train", "on", "a"], "negative_lexemes": ["train", "on", "a"]}, {"tag": "insert", "positive_start": 11, "positive_end": 11, "negative_start": 10, "negative_end": 11, "positive_lexemes": [], "negative_lexemes": ["street"]}, {"tag": "equal", "positive_start": 11, "positive_end": 12, "negative_start": 11, "negative_end": 12, "positive_lexemes": ["bridge"], "negative_lexemes": ["bridge"]}]`
- 共同前缀：`["a"]`
- 正确 contrast hull：`["street", "light", "in", "front", "of", "a", "colorful", "train", "on", "a"]`
- 错误 contrast hull：`["colorful", "light", "in", "front", "of", "a", "train", "on", "a", "street"]`
- 共同后缀：`["bridge"]`
- Hull token 覆盖率（正/负/最大）：`[0.7894736842105263, 0.7894736842105263, 0.7894736842105263]`
- 共同前缀模型 token：`[100]`
- 正确 hull 模型 token：IDs `[5941, 439, 2795, 353, 341, 117, 3856, 354, 299, 4987, 1930, 1946, 301, 619, 299]`；text " street light in front of a colorful train on a"
- 错误 hull 模型 token：IDs `[4987, 1930, 2795, 353, 341, 117, 3856, 354, 299, 1946, 301, 619, 299, 5941, 439]`；text " colorful light in front of a train on a street"
- 第一轮/第二轮分类：`complex_edit` / `large_contrast_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；"maximum_hull_token_coverage_above_75_percent"

### 17. `swap_atribute:476`

- 负例类型/范围：`swap_atribute` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A chubby bearded person holding an orange beverage."
- 原始正描述 2："A person holding an orange beverage with a chubby face and beard."
- 原始负描述："An orange bearded person holding a chubby beverage."
- 规范化正描述 1："a chubby bearded person holding an orange beverage"
- 规范化正描述 2："a person holding an orange beverage with a chubby face and beard"
- 规范化负描述："an orange bearded person holding a chubby beverage"
- 正描述 1 选择元组：`[8, 14, 2, 0.5, 0.28]`
- 正描述 2 选择元组：`[12, 20, 5, 0.75, 0.640625]`
- 最终比较正描述：`positive_1` / "A chubby bearded person holding an orange beverage."
- 完整 lexeme 编辑块：`[{"tag": "replace", "positive_start": 0, "positive_end": 2, "negative_start": 0, "negative_end": 2, "positive_lexemes": ["a", "chubby"], "negative_lexemes": ["an", "orange"]}, {"tag": "equal", "positive_start": 2, "positive_end": 5, "negative_start": 2, "negative_end": 5, "positive_lexemes": ["bearded", "person", "holding"], "negative_lexemes": ["bearded", "person", "holding"]}, {"tag": "replace", "positive_start": 5, "positive_end": 7, "negative_start": 5, "negative_end": 7, "positive_lexemes": ["an", "orange"], "negative_lexemes": ["a", "chubby"]}, {"tag": "equal", "positive_start": 7, "positive_end": 8, "negative_start": 7, "negative_end": 8, "positive_lexemes": ["beverage"], "negative_lexemes": ["beverage"]}]`
- 共同前缀：`[]`
- 正确 contrast hull：`["a", "chubby", "bearded", "person", "holding", "an", "orange"]`
- 错误 contrast hull：`["an", "orange", "bearded", "person", "holding", "a", "chubby"]`
- 共同后缀：`["beverage"]`
- Hull token 覆盖率（正/负/最大）：`[0.875, 0.875, 0.875]`
- 共同前缀模型 token：`[]`
- 正确 hull 模型 token：IDs `[100, 890, 1352, 5016, 600, 1433, 382, 2198, 429, 2569, 350, 346, 522, 1285]`；text "a chubby bearded person holding an orange"
- 错误 hull 模型 token：IDs `[325, 522, 1285, 600, 1433, 382, 2198, 429, 2569, 350, 299, 890, 1352, 5016]`；text "an orange bearded person holding a chubby"
- 第一轮/第二轮分类：`complex_edit` / `large_contrast_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；"maximum_hull_token_coverage_above_75_percent"

### 18. `swap_atribute:517`

- 负例类型/范围：`swap_atribute` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："The neon purple toilet with lid lifted is in the bathroom with brown tile."
- 原始正描述 2："The neon purple toilet with lid lifted is located in the bathroom with brown tile."
- 原始负描述："The brown toilet with lid lifted is in the bathroom with neon purple tile."
- 规范化正描述 1："the neon purple toilet with lid lifted is in the bathroom with brown tile"
- 规范化正描述 2："the neon purple toilet with lid lifted is located in the bathroom with brown tile"
- 规范化负描述："the brown toilet with lid lifted is in the bathroom with neon purple tile"
- 正描述 1 选择元组：`[6, 24, 4, 0.2857142857142857, 0.273972602739726]`
- 正描述 2 选择元组：`[7, 25, 5, 0.3333333333333333, 0.345679012345679]`
- 最终比较正描述：`positive_1` / "The neon purple toilet with lid lifted is in the bathroom with brown tile."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 1, "negative_start": 0, "negative_end": 1, "positive_lexemes": ["the"], "negative_lexemes": ["the"]}, {"tag": "delete", "positive_start": 1, "positive_end": 2, "negative_start": 1, "negative_end": 1, "positive_lexemes": ["neon"], "negative_lexemes": []}, {"tag": "replace", "positive_start": 2, "positive_end": 3, "negative_start": 1, "negative_end": 2, "positive_lexemes": ["purple"], "negative_lexemes": ["brown"]}, {"tag": "equal", "positive_start": 3, "positive_end": 12, "negative_start": 2, "negative_end": 11, "positive_lexemes": ["toilet", "with", "lid", "lifted", "is", "in", "the", "bathroom", "with"], "negative_lexemes": ["toilet", "with", "lid", "lifted", "is", "in", "the", "bathroom", "with"]}, {"tag": "insert", "positive_start": 12, "positive_end": 12, "negative_start": 11, "negative_end": 12, "positive_lexemes": [], "negative_lexemes": ["neon"]}, {"tag": "replace", "positive_start": 12, "positive_end": 13, "negative_start": 12, "negative_end": 13, "positive_lexemes": ["brown"], "negative_lexemes": ["purple"]}, {"tag": "equal", "positive_start": 13, "positive_end": 14, "negative_start": 13, "negative_end": 14, "positive_lexemes": ["tile"], "negative_lexemes": ["tile"]}]`
- 共同前缀：`["the"]`
- 正确 contrast hull：`["neon", "purple", "toilet", "with", "lid", "lifted", "is", "in", "the", "bathroom", "with", "brown"]`
- 错误 contrast hull：`["brown", "toilet", "with", "lid", "lifted", "is", "in", "the", "bathroom", "with", "neon", "purple"]`
- 共同后缀：`["tile"]`
- Hull token 覆盖率（正/负/最大）：`[0.8888888888888888, 0.8888888888888888, 0.8888888888888888]`
- 共同前缀模型 token：`[4345]`
- 正确 hull 模型 token：IDs `[730, 310, 3315, 833, 364, 1299, 119, 599, 406, 460, 406, 507, 4587, 395, 353, 309, 363, 1831, 393, 444, 599, 363, 2079, 113]`；text " neon purple toilet with lid lifted is in the bathroom with brown"
- 错误 hull 模型 token：IDs `[363, 2079, 113, 364, 1299, 119, 599, 406, 460, 406, 507, 4587, 395, 353, 309, 363, 1831, 393, 444, 599, 730, 310, 3315, 833]`；text " brown toilet with lid lifted is in the bathroom with neon purple"
- 第一轮/第二轮分类：`complex_edit` / `large_contrast_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；"maximum_hull_token_coverage_above_75_percent"

### 19. `swap_atribute:561`

- 负例类型/范围：`swap_atribute` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："Some scrap book scissors are on a brown table."
- 原始正描述 2："The brown table has some scrap book scissors on it."
- 原始负描述："Some brown scissors are on a scrap book table."
- 规范化正描述 1："some scrap book scissors are on a brown table"
- 规范化正描述 2："the brown table has some scrap book scissors on it"
- 规范化负描述："some brown scissors are on a scrap book table"
- 正描述 1 选择元组：`[6, 14, 4, 0.4444444444444444, 0.35555555555555557]`
- 正描述 2 选择元组：`[13, 19, 5, 0.8, 0.64]`
- 最终比较正描述：`positive_1` / "Some scrap book scissors are on a brown table."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 1, "negative_start": 0, "negative_end": 1, "positive_lexemes": ["some"], "negative_lexemes": ["some"]}, {"tag": "delete", "positive_start": 1, "positive_end": 2, "negative_start": 1, "negative_end": 1, "positive_lexemes": ["scrap"], "negative_lexemes": []}, {"tag": "replace", "positive_start": 2, "positive_end": 3, "negative_start": 1, "negative_end": 2, "positive_lexemes": ["book"], "negative_lexemes": ["brown"]}, {"tag": "equal", "positive_start": 3, "positive_end": 7, "negative_start": 2, "negative_end": 6, "positive_lexemes": ["scissors", "are", "on", "a"], "negative_lexemes": ["scissors", "are", "on", "a"]}, {"tag": "insert", "positive_start": 7, "positive_end": 7, "negative_start": 6, "negative_end": 7, "positive_lexemes": [], "negative_lexemes": ["scrap"]}, {"tag": "replace", "positive_start": 7, "positive_end": 8, "negative_start": 7, "negative_end": 8, "positive_lexemes": ["brown"], "negative_lexemes": ["book"]}, {"tag": "equal", "positive_start": 8, "positive_end": 9, "negative_start": 8, "negative_end": 9, "positive_lexemes": ["table"], "negative_lexemes": ["table"]}]`
- 共同前缀：`["some"]`
- 正确 contrast hull：`["scrap", "book", "scissors", "are", "on", "a", "brown"]`
- 错误 contrast hull：`["brown", "scissors", "are", "on", "a", "scrap", "book"]`
- 共同后缀：`["table"]`
- Hull token 覆盖率（正/负/最大）：`[0.8125, 0.8125, 0.8125]`
- 共同前缀模型 token：`[118, 3219]`
- 正确 hull 模型 token：IDs `[1416, 559, 115, 2961, 1416, 3151, 1945, 732, 619, 299, 363, 2079, 113]`；text " scrap book scissors are on a brown"
- 错误 hull 模型 token：IDs `[363, 2079, 113, 1416, 3151, 1945, 732, 619, 299, 1416, 559, 115, 2961]`；text " brown scissors are on a scrap book"
- 第一轮/第二轮分类：`complex_edit` / `large_contrast_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；"maximum_hull_token_coverage_above_75_percent"

### 20. `swap_atribute:586`

- 负例类型/范围：`swap_atribute` / `{"canonical": true, "pilot": true, "formal": false, "certifying_formal": false}`
- 原始正描述 1："A yellow work truck parked in tall grass."
- 原始正描述 2："In tall grass, a yellow truck is parked."
- 原始负描述："A tall work truck parked in yellow grass."
- 规范化正描述 1："a yellow work truck parked in tall grass"
- 规范化正描述 2："in tall grass , a yellow truck is parked"
- 规范化负描述："a tall work truck parked in yellow grass"
- 正描述 1 选择元组：`[4, 12, 2, 0.25, 0.2]`
- 正描述 2 选择元组：`[15, 17, 3, 0.8888888888888888, 0.775]`
- 最终比较正描述：`positive_1` / "A yellow work truck parked in tall grass."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 1, "negative_start": 0, "negative_end": 1, "positive_lexemes": ["a"], "negative_lexemes": ["a"]}, {"tag": "replace", "positive_start": 1, "positive_end": 2, "negative_start": 1, "negative_end": 2, "positive_lexemes": ["yellow"], "negative_lexemes": ["tall"]}, {"tag": "equal", "positive_start": 2, "positive_end": 6, "negative_start": 2, "negative_end": 6, "positive_lexemes": ["work", "truck", "parked", "in"], "negative_lexemes": ["work", "truck", "parked", "in"]}, {"tag": "replace", "positive_start": 6, "positive_end": 7, "negative_start": 6, "negative_end": 7, "positive_lexemes": ["tall"], "negative_lexemes": ["yellow"]}, {"tag": "equal", "positive_start": 7, "positive_end": 8, "negative_start": 7, "negative_end": 8, "positive_lexemes": ["grass"], "negative_lexemes": ["grass"]}]`
- 共同前缀：`["a"]`
- 正确 contrast hull：`["yellow", "work", "truck", "parked", "in", "tall"]`
- 错误 contrast hull：`["tall", "work", "truck", "parked", "in", "yellow"]`
- 共同后缀：`["grass"]`
- Hull token 覆盖率（正/负/最大）：`[0.7647058823529411, 0.7647058823529411, 0.7647058823529411]`
- 共同前缀模型 token：`[100]`
- 正确 hull 模型 token：IDs `[385, 446, 1030, 2943, 1144, 120, 892, 344, 2000, 382, 353, 297, 1266]`；text " yellow work truck parked in tall"
- 错误 hull 模型 token：IDs `[297, 1266, 2943, 1144, 120, 892, 344, 2000, 382, 353, 385, 446, 1030]`；text " tall work truck parked in yellow"
- 第一轮/第二轮分类：`complex_edit` / `large_contrast_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；"maximum_hull_token_coverage_above_75_percent"

### 21. `swap_atribute:602`

- 负例类型/范围：`swap_atribute` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："Bearded person in a suit about to enjoy an adult beverage"
- 原始正描述 2："A person with a beard and wearing a suit is about to consume an alcoholic beverage."
- 原始负描述："An adult person in a suit about to enjoy a bearded beverage."
- 规范化正描述 1："bearded person in a suit about to enjoy an adult beverage"
- 规范化正描述 2："a person with a beard and wearing a suit is about to consume an alcoholic beverage"
- 规范化负描述："an adult person in a suit about to enjoy a bearded beverage"
- 正描述 1 选择元组：`[7, 21, 3, 0.3333333333333333, 0.23728813559322035]`
- 正描述 2 选择元组：`[18, 26, 4, 0.6875, 0.5121951219512195]`
- 最终比较正描述：`positive_1` / "Bearded person in a suit about to enjoy an adult beverage"
- 完整 lexeme 编辑块：`[{"tag": "insert", "positive_start": 0, "positive_end": 0, "negative_start": 0, "negative_end": 1, "positive_lexemes": [], "negative_lexemes": ["an"]}, {"tag": "replace", "positive_start": 0, "positive_end": 1, "negative_start": 1, "negative_end": 2, "positive_lexemes": ["bearded"], "negative_lexemes": ["adult"]}, {"tag": "equal", "positive_start": 1, "positive_end": 8, "negative_start": 2, "negative_end": 9, "positive_lexemes": ["person", "in", "a", "suit", "about", "to", "enjoy"], "negative_lexemes": ["person", "in", "a", "suit", "about", "to", "enjoy"]}, {"tag": "replace", "positive_start": 8, "positive_end": 10, "negative_start": 9, "negative_end": 11, "positive_lexemes": ["an", "adult"], "negative_lexemes": ["a", "bearded"]}, {"tag": "equal", "positive_start": 10, "positive_end": 11, "negative_start": 11, "negative_end": 12, "positive_lexemes": ["beverage"], "negative_lexemes": ["beverage"]}]`
- 共同前缀：`[]`
- 正确 contrast hull：`["bearded", "person", "in", "a", "suit", "about", "to", "enjoy", "an", "adult"]`
- 错误 contrast hull：`["an", "adult", "person", "in", "a", "suit", "about", "to", "enjoy", "a", "bearded"]`
- 共同后缀：`["beverage"]`
- Hull token 覆盖率（正/负/最大）：`[0.8888888888888888, 0.8947368421052632, 0.8947368421052632]`
- 共同前缀模型 token：`[]`
- 正确 hull 模型 token：IDs `[5158, 1433, 382, 2198, 353, 299, 855, 338, 1196, 364, 1057, 109, 4117, 346, 1200, 1005]`；text "bearded person in a suit about to enjoy an adult"
- 错误 hull 模型 token：IDs `[325, 1200, 1005, 2198, 353, 299, 855, 338, 1196, 364, 1057, 109, 4117, 299, 600, 1433, 382]`；text "an adult person in a suit about to enjoy a bearded"
- 第一轮/第二轮分类：`complex_edit` / `large_contrast_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；"maximum_hull_token_coverage_above_75_percent"

### 22. `swap_object:140`

- 负例类型/范围：`swap_object` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："Half an eclair on a plate and a coffee mug on wooden table."
- 原始正描述 2："A coffee mug is on a wooden table and half of an eclair are positioned on a plate."
- 原始负描述："A coffee mug on a plate and half an eclair on wooden table."
- 规范化正描述 1："half an eclair on a plate and a coffee mug on wooden table"
- 规范化正描述 2："a coffee mug is on a wooden table and half of an eclair are positioned on a plate"
- 规范化负描述："a coffee mug on a plate and half an eclair on wooden table"
- 正描述 1 选择元组：`[12, 20, 2, 0.46153846153846156, 0.41379310344827586]`
- 正描述 2 选择元组：`[11, 25, 6, 0.4444444444444444, 0.4074074074074074]`
- 最终比较正描述：`positive_2` / "A coffee mug is on a wooden table and half of an eclair are positioned on a plate."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 3, "negative_start": 0, "negative_end": 3, "positive_lexemes": ["a", "coffee", "mug"], "negative_lexemes": ["a", "coffee", "mug"]}, {"tag": "delete", "positive_start": 3, "positive_end": 4, "negative_start": 3, "negative_end": 3, "positive_lexemes": ["is"], "negative_lexemes": []}, {"tag": "equal", "positive_start": 4, "positive_end": 6, "negative_start": 3, "negative_end": 5, "positive_lexemes": ["on", "a"], "negative_lexemes": ["on", "a"]}, {"tag": "delete", "positive_start": 6, "positive_end": 7, "negative_start": 5, "negative_end": 5, "positive_lexemes": ["wooden"], "negative_lexemes": []}, {"tag": "replace", "positive_start": 7, "positive_end": 8, "negative_start": 5, "negative_end": 6, "positive_lexemes": ["table"], "negative_lexemes": ["plate"]}, {"tag": "equal", "positive_start": 8, "positive_end": 10, "negative_start": 6, "negative_end": 8, "positive_lexemes": ["and", "half"], "negative_lexemes": ["and", "half"]}, {"tag": "delete", "positive_start": 10, "positive_end": 11, "negative_start": 8, "negative_end": 8, "positive_lexemes": ["of"], "negative_lexemes": []}, {"tag": "equal", "positive_start": 11, "positive_end": 13, "negative_start": 8, "negative_end": 10, "positive_lexemes": ["an", "eclair"], "negative_lexemes": ["an", "eclair"]}, {"tag": "delete", "positive_start": 13, "positive_end": 15, "negative_start": 10, "negative_end": 10, "positive_lexemes": ["are", "positioned"], "negative_lexemes": []}, {"tag": "equal", "positive_start": 15, "positive_end": 16, "negative_start": 10, "negative_end": 11, "positive_lexemes": ["on"], "negative_lexemes": ["on"]}, {"tag": "replace", "positive_start": 16, "positive_end": 18, "negative_start": 11, "negative_end": 13, "positive_lexemes": ["a", "plate"], "negative_lexemes": ["wooden", "table"]}]`
- 共同前缀：`["a", "coffee", "mug"]`
- 正确 contrast hull：`["is", "on", "a", "wooden", "table", "and", "half", "of", "an", "eclair", "are", "positioned", "on", "a", "plate"]`
- 错误 contrast hull：`["on", "a", "plate", "and", "half", "an", "eclair", "on", "wooden", "table"]`
- 共同后缀：`[]`
- Hull token 覆盖率（正/负/最大）：`[0.8, 0.7391304347826086, 0.8]`
- 共同前缀模型 token：`[100, 966, 1627, 6044, 351, 3304]`
- 正确 hull 模型 token：IDs `[395, 619, 299, 339, 2166, 327, 2630, 376, 429, 352, 105, 354, 346, 413, 1110, 3709, 732, 2617, 1632, 382, 619, 299, 1219, 557]`；text " is on a wooden table and half of an eclair are positioned on a plate"
- 错误 hull 模型 token：IDs `[619, 299, 1219, 557, 376, 429, 352, 105, 346, 413, 1110, 3709, 619, 339, 2166, 327, 2630]`；text " on a plate and half an eclair on wooden table"
- 第一轮/第二轮分类：`complex_edit` / `large_contrast_hull`
- 自动判断："positive_2_selection_tuple_lexicographically_smaller"；"maximum_hull_token_coverage_above_75_percent"

### 23. `swap_object:183`

- 负例类型/范围：`swap_object` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A person standing behind a person holding a bat."
- 原始正描述 2："The person is holding the bat while another person is standing behind them."
- 原始负描述："A person holding a bat stands behind a person."
- 规范化正描述 1："a person standing behind a person holding a bat"
- 规范化正描述 2："the person is holding the bat while another person is standing behind them"
- 规范化负描述："a person holding a bat stands behind a person"
- 正描述 1 选择元组：`[12, 14, 2, 0.6666666666666666, 0.5957446808510638]`
- 正描述 2 选择元组：`[16, 22, 5, 0.7692307692307693, 0.581081081081081]`
- 最终比较正描述：`positive_1` / "A person standing behind a person holding a bat."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 2, "negative_start": 0, "negative_end": 2, "positive_lexemes": ["a", "person"], "negative_lexemes": ["a", "person"]}, {"tag": "replace", "positive_start": 2, "positive_end": 7, "negative_start": 2, "negative_end": 7, "positive_lexemes": ["standing", "behind", "a", "person", "holding"], "negative_lexemes": ["holding", "a", "bat", "stands", "behind"]}, {"tag": "equal", "positive_start": 7, "positive_end": 8, "negative_start": 7, "negative_end": 8, "positive_lexemes": ["a"], "negative_lexemes": ["a"]}, {"tag": "replace", "positive_start": 8, "positive_end": 9, "negative_start": 8, "negative_end": 9, "positive_lexemes": ["bat"], "negative_lexemes": ["person"]}]`
- 共同前缀：`["a", "person"]`
- 正确 contrast hull：`["standing", "behind", "a", "person", "holding", "a", "bat"]`
- 错误 contrast hull：`["holding", "a", "bat", "stands", "behind", "a", "person"]`
- 共同后缀：`[]`
- Hull token 覆盖率（正/负/最大）：`[0.8571428571428571, 0.8571428571428571, 0.8571428571428571]`
- 共同前缀模型 token：`[100, 2198]`
- 正确 hull 模型 token：IDs `[2823, 350, 5237, 916, 299, 2198, 429, 2569, 350, 299, 363, 314]`；text " standing behind a person holding a bat"
- 错误 hull 模型 token：IDs `[429, 2569, 350, 299, 363, 314, 2823, 118, 5237, 916, 299, 2198]`；text " holding a bat stands behind a person"
- 第一轮/第二轮分类：`complex_edit` / `large_contrast_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；"maximum_hull_token_coverage_above_75_percent"

### 24. `swap_object:200`

- 负例类型/范围：`swap_object` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："Small red plane flying next to motorcycle rider in urban area."
- 原始正描述 2："A small plane that is red in color is flying next to the motorcycle rider in an urban area."
- 原始负描述："Motorcycle rider flying next to small red plane in urban area."
- 规范化正描述 1："small red plane flying next to motorcycle rider in urban area"
- 规范化正描述 2："a small plane that is red in color is flying next to the motorcycle rider in an urban area"
- 规范化负描述："motorcycle rider flying next to small red plane in urban area"
- 正描述 1 选择元组：`[10, 16, 4, 0.5454545454545454, 0.4918032786885246]`
- 正描述 2 选择元组：`[18, 26, 4, 0.6842105263157895, 0.5555555555555556]`
- 最终比较正描述：`positive_1` / "Small red plane flying next to motorcycle rider in urban area."
- 完整 lexeme 编辑块：`[{"tag": "delete", "positive_start": 0, "positive_end": 1, "negative_start": 0, "negative_end": 0, "positive_lexemes": ["small"], "negative_lexemes": []}, {"tag": "replace", "positive_start": 1, "positive_end": 3, "negative_start": 0, "negative_end": 2, "positive_lexemes": ["red", "plane"], "negative_lexemes": ["motorcycle", "rider"]}, {"tag": "equal", "positive_start": 3, "positive_end": 6, "negative_start": 2, "negative_end": 5, "positive_lexemes": ["flying", "next", "to"], "negative_lexemes": ["flying", "next", "to"]}, {"tag": "insert", "positive_start": 6, "positive_end": 6, "negative_start": 5, "negative_end": 6, "positive_lexemes": [], "negative_lexemes": ["small"]}, {"tag": "replace", "positive_start": 6, "positive_end": 8, "negative_start": 6, "negative_end": 8, "positive_lexemes": ["motorcycle", "rider"], "negative_lexemes": ["red", "plane"]}, {"tag": "equal", "positive_start": 8, "positive_end": 11, "negative_start": 8, "negative_end": 11, "positive_lexemes": ["in", "urban", "area"], "negative_lexemes": ["in", "urban", "area"]}]`
- 共同前缀：`[]`
- 正确 contrast hull：`["small", "red", "plane", "flying", "next", "to", "motorcycle", "rider"]`
- 错误 contrast hull：`["motorcycle", "rider", "flying", "next", "to", "small", "red", "plane"]`
- 共同后缀：`["in", "urban", "area"]`
- Hull token 覆盖率（正/负/最大）：`[0.782608695652174, 0.7619047619047619, 0.782608695652174]`
- 共同前缀模型 token：`[]`
- 正确 hull 模型 token：IDs `[118, 112, 1266, 5534, 4140, 104, 341, 542, 350, 4658, 364, 351, 593, 336, 2863, 2945, 757, 4591]`；text "small red plane flying next to motorcycle rider"
- 错误 hull 模型 token：IDs `[112, 593, 336, 2863, 2945, 757, 4591, 341, 542, 350, 4658, 364, 3436, 5534, 4140, 104]`；text "motorcycle rider flying next to small red plane"
- 第一轮/第二轮分类：`complex_edit` / `large_contrast_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；"maximum_hull_token_coverage_above_75_percent"

### 25. `swap_object:209`

- 负例类型/范围：`swap_object` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A person is holding a baby who is wrapped in a towel and holding a toothbrush"
- 原始正描述 2："The baby, who is wrapped in a towel and holding a toothbrush, is being held by a person."
- 原始负描述："A person is holding a toothbrush while the baby wrapped in a towel looks on."
- 规范化正描述 1："a person is holding a baby who is wrapped in a towel and holding a toothbrush"
- 规范化正描述 2："the baby , who is wrapped in a towel and holding a toothbrush , is being held by a person"
- 规范化负描述："a person is holding a toothbrush while the baby wrapped in a towel looks on"
- 正描述 1 选择元组：`[13, 21, 4, 0.5, 0.5324675324675324]`
- 正描述 2 选择元组：`[25, 35, 5, 0.85, 0.7078651685393258]`
- 最终比较正描述：`positive_1` / "A person is holding a baby who is wrapped in a towel and holding a toothbrush"
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 5, "negative_start": 0, "negative_end": 5, "positive_lexemes": ["a", "person", "is", "holding", "a"], "negative_lexemes": ["a", "person", "is", "holding", "a"]}, {"tag": "insert", "positive_start": 5, "positive_end": 5, "negative_start": 5, "negative_end": 6, "positive_lexemes": [], "negative_lexemes": ["toothbrush"]}, {"tag": "replace", "positive_start": 5, "positive_end": 8, "negative_start": 6, "negative_end": 9, "positive_lexemes": ["baby", "who", "is"], "negative_lexemes": ["while", "the", "baby"]}, {"tag": "equal", "positive_start": 8, "positive_end": 12, "negative_start": 9, "negative_end": 13, "positive_lexemes": ["wrapped", "in", "a", "towel"], "negative_lexemes": ["wrapped", "in", "a", "towel"]}, {"tag": "delete", "positive_start": 12, "positive_end": 14, "negative_start": 13, "negative_end": 13, "positive_lexemes": ["and", "holding"], "negative_lexemes": []}, {"tag": "replace", "positive_start": 14, "positive_end": 16, "negative_start": 13, "negative_end": 15, "positive_lexemes": ["a", "toothbrush"], "negative_lexemes": ["looks", "on"]}]`
- 共同前缀：`["a", "person", "is", "holding", "a"]`
- 正确 contrast hull：`["baby", "who", "is", "wrapped", "in", "a", "towel", "and", "holding", "a", "toothbrush"]`
- 错误 contrast hull：`["toothbrush", "while", "the", "baby", "wrapped", "in", "a", "towel", "looks", "on"]`
- 共同后缀：`[]`
- Hull token 覆盖率（正/负/最大）：`[0.78125, 0.7666666666666667, 0.78125]`
- 共同前缀模型 token：`[100, 2198, 395, 429, 2569, 350, 299]`
- 正确 hull 模型 token：IDs `[363, 572, 124, 2109, 395, 339, 559, 737, 382, 353, 299, 364, 122, 446, 376, 429, 2569, 350, 299, 364, 114, 495, 101, 117, 4923]`；text " baby who is wrapped in a towel and holding a toothbrush"
- 错误 hull 模型 token：IDs `[364, 114, 495, 101, 117, 4923, 3052, 309, 363, 572, 124, 339, 559, 737, 382, 353, 299, 364, 122, 446, 1853, 1275, 619]`；text " toothbrush while the baby wrapped in a towel looks on"
- 第一轮/第二轮分类：`complex_edit` / `large_contrast_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；"maximum_hull_token_coverage_above_75_percent"

### 26. `swap_object:217`

- 负例类型/范围：`swap_object` / `{"canonical": true, "pilot": true, "formal": false, "certifying_formal": false}`
- 原始正描述 1："A group of walkers are seen while passengers ride in a train."
- 原始正描述 2："Passengers are riding in a train while a group of walkers is visible."
- 原始负描述："A group of passengers are seen while walkers walk alongside the train."
- 规范化正描述 1："a group of walkers are seen while passengers ride in a train"
- 规范化正描述 2："passengers are riding in a train while a group of walkers is visible"
- 规范化负描述："a group of passengers are seen while walkers walk alongside the train"
- 正描述 1 选择元组：`[10, 16, 2, 0.4166666666666667, 0.37681159420289856]`
- 正描述 2 选择元组：`[23, 25, 3, 0.9230769230769231, 0.7536231884057971]`
- 最终比较正描述：`positive_1` / "A group of walkers are seen while passengers ride in a train."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 3, "negative_start": 0, "negative_end": 3, "positive_lexemes": ["a", "group", "of"], "negative_lexemes": ["a", "group", "of"]}, {"tag": "replace", "positive_start": 3, "positive_end": 4, "negative_start": 3, "negative_end": 4, "positive_lexemes": ["walkers"], "negative_lexemes": ["passengers"]}, {"tag": "equal", "positive_start": 4, "positive_end": 7, "negative_start": 4, "negative_end": 7, "positive_lexemes": ["are", "seen", "while"], "negative_lexemes": ["are", "seen", "while"]}, {"tag": "replace", "positive_start": 7, "positive_end": 11, "negative_start": 7, "negative_end": 11, "positive_lexemes": ["passengers", "ride", "in", "a"], "negative_lexemes": ["walkers", "walk", "alongside", "the"]}, {"tag": "equal", "positive_start": 11, "positive_end": 12, "negative_start": 11, "negative_end": 12, "positive_lexemes": ["train"], "negative_lexemes": ["train"]}]`
- 共同前缀：`["a", "group", "of"]`
- 正确 contrast hull：`["walkers", "are", "seen", "while", "passengers", "ride", "in", "a"]`
- 错误 contrast hull：`["passengers", "are", "seen", "while", "walkers", "walk", "alongside", "the"]`
- 共同后缀：`["train"]`
- Hull token 覆盖率（正/负/最大）：`[0.7368421052631579, 0.7619047619047619, 0.7619047619047619]`
- 共同前缀模型 token：`[100, 4592, 354]`
- 正确 hull 模型 token：IDs `[339, 5864, 496, 732, 762, 327, 3052, 3241, 1979, 496, 757, 688, 353, 299]`；text " walkers are seen while passengers ride in a"
- 错误 hull 模型 token：IDs `[3241, 1979, 496, 732, 762, 327, 3052, 339, 5864, 496, 339, 5864, 5782, 118, 688, 309]`；text " passengers are seen while walkers walk alongside the"
- 第一轮/第二轮分类：`complex_edit` / `large_contrast_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；"maximum_hull_token_coverage_above_75_percent"

### 27. `swap_object:39`

- 负例类型/范围：`swap_object` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A dog is sitting on a neatly made bed while someone looks on. "
- 原始正描述 2："The person is observing a dog sitting on a clean and made bed."
- 原始负描述："Someone is sitting on a neatly made bed while a dog looks on."
- 规范化正描述 1："a dog is sitting on a neatly made bed while someone looks on"
- 规范化正描述 2："the person is observing a dog sitting on a clean and made bed"
- 规范化负描述："someone is sitting on a neatly made bed while a dog looks on"
- 正描述 1 选择元组：`[6, 22, 4, 0.3076923076923077, 0.2]`
- 正描述 2 选择元组：`[24, 26, 2, 0.9230769230769231, 0.7540983606557377]`
- 最终比较正描述：`positive_1` / "A dog is sitting on a neatly made bed while someone looks on. "
- 完整 lexeme 编辑块：`[{"tag": "delete", "positive_start": 0, "positive_end": 1, "negative_start": 0, "negative_end": 0, "positive_lexemes": ["a"], "negative_lexemes": []}, {"tag": "replace", "positive_start": 1, "positive_end": 2, "negative_start": 0, "negative_end": 1, "positive_lexemes": ["dog"], "negative_lexemes": ["someone"]}, {"tag": "equal", "positive_start": 2, "positive_end": 10, "negative_start": 1, "negative_end": 9, "positive_lexemes": ["is", "sitting", "on", "a", "neatly", "made", "bed", "while"], "negative_lexemes": ["is", "sitting", "on", "a", "neatly", "made", "bed", "while"]}, {"tag": "insert", "positive_start": 10, "positive_end": 10, "negative_start": 9, "negative_end": 10, "positive_lexemes": [], "negative_lexemes": ["a"]}, {"tag": "replace", "positive_start": 10, "positive_end": 11, "negative_start": 10, "negative_end": 11, "positive_lexemes": ["someone"], "negative_lexemes": ["dog"]}, {"tag": "equal", "positive_start": 11, "positive_end": 13, "negative_start": 11, "negative_end": 13, "positive_lexemes": ["looks", "on"], "negative_lexemes": ["looks", "on"]}]`
- 共同前缀：`[]`
- 正确 contrast hull：`["a", "dog", "is", "sitting", "on", "a", "neatly", "made", "bed", "while", "someone"]`
- 错误 contrast hull：`["someone", "is", "sitting", "on", "a", "neatly", "made", "bed", "while", "a", "dog"]`
- 共同后缀：`["looks", "on"]`
- Hull token 覆盖率（正/负/最大）：`[0.8421052631578947, 0.8571428571428571, 0.8571428571428571]`
- 共同前缀模型 token：`[]`
- 正确 hull 模型 token：IDs `[100, 1041, 106, 395, 5305, 2912, 619, 299, 730, 314, 542, 4303, 363, 382, 3052, 4779]`；text "a dog is sitting on a neatly made bed while someone"
- 错误 hull 模型 token：IDs `[118, 3219, 1634, 395, 5305, 2912, 619, 299, 730, 314, 542, 4303, 363, 382, 3052, 299, 1041, 106]`；text "someone is sitting on a neatly made bed while a dog"
- 第一轮/第二轮分类：`complex_edit` / `large_contrast_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；"maximum_hull_token_coverage_above_75_percent"

### 28. `swap_object:44`

- 负例类型/范围：`swap_object` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："person flying a kite on the beach while others run along the sand."
- 原始正描述 2："people are running along the sand while a person is flying a kite on the beach."
- 原始负描述："Others flying a kite on the beach while a person runs along the sand."
- 规范化正描述 1："person flying a kite on the beach while others run along the sand"
- 规范化正描述 2："people are running along the sand while a person is flying a kite on the beach"
- 规范化负描述："others flying a kite on the beach while a person runs along the sand"
- 正描述 1 选择元组：`[7, 21, 3, 0.2857142857142857, 0.16176470588235295]`
- 正描述 2 选择元组：`[20, 30, 6, 0.75, 0.5256410256410257]`
- 最终比较正描述：`positive_1` / "person flying a kite on the beach while others run along the sand."
- 完整 lexeme 编辑块：`[{"tag": "replace", "positive_start": 0, "positive_end": 1, "negative_start": 0, "negative_end": 1, "positive_lexemes": ["person"], "negative_lexemes": ["others"]}, {"tag": "equal", "positive_start": 1, "positive_end": 8, "negative_start": 1, "negative_end": 8, "positive_lexemes": ["flying", "a", "kite", "on", "the", "beach", "while"], "negative_lexemes": ["flying", "a", "kite", "on", "the", "beach", "while"]}, {"tag": "insert", "positive_start": 8, "positive_end": 8, "negative_start": 8, "negative_end": 9, "positive_lexemes": [], "negative_lexemes": ["a"]}, {"tag": "replace", "positive_start": 8, "positive_end": 10, "negative_start": 9, "negative_end": 11, "positive_lexemes": ["others", "run"], "negative_lexemes": ["person", "runs"]}, {"tag": "equal", "positive_start": 10, "positive_end": 13, "negative_start": 11, "negative_end": 14, "positive_lexemes": ["along", "the", "sand"], "negative_lexemes": ["along", "the", "sand"]}]`
- 共同前缀：`[]`
- 正确 contrast hull：`["person", "flying", "a", "kite", "on", "the", "beach", "while", "others", "run"]`
- 错误 contrast hull：`["others", "flying", "a", "kite", "on", "the", "beach", "while", "a", "person", "runs"]`
- 共同后缀：`["along", "the", "sand"]`
- Hull token 覆盖率（正/负/最大）：`[0.8, 0.8095238095238095, 0.8095238095238095]`
- 共同前缀模型 token：`[]`
- 正确 hull 模型 token：IDs `[115, 2019, 341, 542, 350, 299, 914, 1078, 619, 309, 600, 1268, 3052, 1649, 118, 3161]`；text "person flying a kite on the beach while others run"
- 错误 hull 模型 token：IDs `[3861, 118, 341, 542, 350, 299, 914, 1078, 619, 309, 600, 1268, 3052, 299, 2198, 3161, 118]`；text "others flying a kite on the beach while a person runs"
- 第一轮/第二轮分类：`complex_edit` / `large_contrast_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；"maximum_hull_token_coverage_above_75_percent"

### 29. `swap_object:51`

- 负例类型/范围：`swap_object` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A woman sits at a counter while a man looks at her through a window."
- 原始正描述 2："A woman is seated at a counter while a man observes her through a window."
- 原始负描述："A man sits at a counter while a woman looks at him through a window."
- 规范化正描述 1："a woman sits at a counter while a man looks at her through a window"
- 规范化正描述 2："a woman is seated at a counter while a man observes her through a window"
- 规范化负描述："a man sits at a counter while a woman looks at him through a window"
- 正描述 1 选择元组：`[6, 22, 3, 0.2, 0.08955223880597014]`
- 正描述 2 选择元组：`[12, 22, 4, 0.4666666666666667, 0.2916666666666667]`
- 最终比较正描述：`positive_1` / "A woman sits at a counter while a man looks at her through a window."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 1, "negative_start": 0, "negative_end": 1, "positive_lexemes": ["a"], "negative_lexemes": ["a"]}, {"tag": "replace", "positive_start": 1, "positive_end": 2, "negative_start": 1, "negative_end": 2, "positive_lexemes": ["woman"], "negative_lexemes": ["man"]}, {"tag": "equal", "positive_start": 2, "positive_end": 8, "negative_start": 2, "negative_end": 8, "positive_lexemes": ["sits", "at", "a", "counter", "while", "a"], "negative_lexemes": ["sits", "at", "a", "counter", "while", "a"]}, {"tag": "replace", "positive_start": 8, "positive_end": 9, "negative_start": 8, "negative_end": 9, "positive_lexemes": ["man"], "negative_lexemes": ["woman"]}, {"tag": "equal", "positive_start": 9, "positive_end": 11, "negative_start": 9, "negative_end": 11, "positive_lexemes": ["looks", "at"], "negative_lexemes": ["looks", "at"]}, {"tag": "replace", "positive_start": 11, "positive_end": 12, "negative_start": 11, "negative_end": 12, "positive_lexemes": ["her"], "negative_lexemes": ["him"]}, {"tag": "equal", "positive_start": 12, "positive_end": 15, "negative_start": 12, "negative_end": 15, "positive_lexemes": ["through", "a", "window"], "negative_lexemes": ["through", "a", "window"]}]`
- 共同前缀：`["a"]`
- 正确 contrast hull：`["woman", "sits", "at", "a", "counter", "while", "a", "man", "looks", "at", "her"]`
- 错误 contrast hull：`["man", "sits", "at", "a", "counter", "while", "a", "woman", "looks", "at", "him"]`
- 共同后缀：`["through", "a", "window"]`
- Hull token 覆盖率（正/负/最大）：`[0.7619047619047619, 0.7727272727272727, 0.7727272727272727]`
- 共同前缀模型 token：`[100]`
- 正确 hull 模型 token：IDs `[339, 444, 325, 316, 2163, 1248, 299, 2320, 311, 3052, 299, 1672, 1853, 1275, 1248, 2833]`；text " woman sits at a counter while a man looks at her"
- 错误 hull 模型 token：IDs `[1672, 316, 2163, 1248, 299, 2320, 311, 3052, 299, 339, 444, 325, 1853, 1275, 1248, 429, 467]`；text " man sits at a counter while a woman looks at him"
- 第一轮/第二轮分类：`complex_edit` / `large_contrast_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；"maximum_hull_token_coverage_above_75_percent"

### 30. `swap_object:80`

- 负例类型/范围：`swap_object` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A person sitting at a wooden bench and table with an open umbrella sitting on the table."
- 原始正描述 2："an umbrella that is placed on a table where a person is seated on a wooden bench."
- 原始负描述："A person sitting at a table and bench with an open umbrella sitting on the bench."
- 规范化正描述 1："a person sitting at a wooden bench and table with an open umbrella sitting on the table"
- 规范化正描述 2："an umbrella that is placed on a table where a person is seated on a wooden bench"
- 规范化负描述："a person sitting at a table and bench with an open umbrella sitting on the bench"
- 正描述 1 选择元组：`[7, 23, 4, 0.23529411764705882, 0.2413793103448276]`
- 正描述 2 选择元组：`[27, 31, 4, 0.8823529411764706, 0.725]`
- 最终比较正描述：`positive_1` / "A person sitting at a wooden bench and table with an open umbrella sitting on the table."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 5, "negative_start": 0, "negative_end": 5, "positive_lexemes": ["a", "person", "sitting", "at", "a"], "negative_lexemes": ["a", "person", "sitting", "at", "a"]}, {"tag": "delete", "positive_start": 5, "positive_end": 6, "negative_start": 5, "negative_end": 5, "positive_lexemes": ["wooden"], "negative_lexemes": []}, {"tag": "replace", "positive_start": 6, "positive_end": 7, "negative_start": 5, "negative_end": 6, "positive_lexemes": ["bench"], "negative_lexemes": ["table"]}, {"tag": "equal", "positive_start": 7, "positive_end": 8, "negative_start": 6, "negative_end": 7, "positive_lexemes": ["and"], "negative_lexemes": ["and"]}, {"tag": "replace", "positive_start": 8, "positive_end": 9, "negative_start": 7, "negative_end": 8, "positive_lexemes": ["table"], "negative_lexemes": ["bench"]}, {"tag": "equal", "positive_start": 9, "positive_end": 16, "negative_start": 8, "negative_end": 15, "positive_lexemes": ["with", "an", "open", "umbrella", "sitting", "on", "the"], "negative_lexemes": ["with", "an", "open", "umbrella", "sitting", "on", "the"]}, {"tag": "replace", "positive_start": 16, "positive_end": 17, "negative_start": 15, "negative_end": 16, "positive_lexemes": ["table"], "negative_lexemes": ["bench"]}]`
- 共同前缀：`["a", "person", "sitting", "at", "a"]`
- 正确 contrast hull：`["wooden", "bench", "and", "table", "with", "an", "open", "umbrella", "sitting", "on", "the", "table"]`
- 错误 contrast hull：`["table", "and", "bench", "with", "an", "open", "umbrella", "sitting", "on", "the", "bench"]`
- 共同后缀：`[]`
- Hull token 覆盖率（正/负/最大）：`[0.7692307692307693, 0.75, 0.7692307692307693]`
- 共同前缀模型 token：`[100, 2198, 5305, 2912, 1248, 299]`
- 正确 hull 模型 token：IDs `[339, 2166, 327, 6141, 550, 376, 2630, 599, 346, 5102, 256, 714, 306, 1989, 100, 5305, 2912, 619, 309, 2630]`；text " wooden bench and table with an open umbrella sitting on the table"
- 错误 hull 模型 token：IDs `[2630, 376, 6141, 550, 599, 346, 5102, 256, 714, 306, 1989, 100, 5305, 2912, 619, 309, 6141, 550]`；text " table and bench with an open umbrella sitting on the bench"
- 第一轮/第二轮分类：`complex_edit` / `large_contrast_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；"maximum_hull_token_coverage_above_75_percent"

## Hull 超过 90%

候选 `211` 条，本节抽取 `30` 条。

### 1. `replace_attribute:271`

- 负例类型/范围：`replace_attribute` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A american flag painted fire hydrant with chains hanging at it side."
- 原始正描述 2："An American flag is painted on a fire hydrant, with chains hanging from its side."
- 原始负描述："A British flag painted fire hydrant with chains hanging at its side."
- 规范化正描述 1："a american flag painted fire hydrant with chains hanging at it side"
- 规范化正描述 2："an american flag is painted on a fire hydrant , with chains hanging from its side"
- 规范化负描述："a british flag painted fire hydrant with chains hanging at its side"
- 正描述 1 选择元组：`[4, 20, 2, 0.16666666666666666, 0.11940298507462686]`
- 正描述 2 选择元组：`[10, 24, 5, 0.4375, 0.2716049382716049]`
- 最终比较正描述：`positive_1` / "A american flag painted fire hydrant with chains hanging at it side."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 1, "negative_start": 0, "negative_end": 1, "positive_lexemes": ["a"], "negative_lexemes": ["a"]}, {"tag": "replace", "positive_start": 1, "positive_end": 2, "negative_start": 1, "negative_end": 2, "positive_lexemes": ["american"], "negative_lexemes": ["british"]}, {"tag": "equal", "positive_start": 2, "positive_end": 10, "negative_start": 2, "negative_end": 10, "positive_lexemes": ["flag", "painted", "fire", "hydrant", "with", "chains", "hanging", "at"], "negative_lexemes": ["flag", "painted", "fire", "hydrant", "with", "chains", "hanging", "at"]}, {"tag": "replace", "positive_start": 10, "positive_end": 11, "negative_start": 10, "negative_end": 11, "positive_lexemes": ["it"], "negative_lexemes": ["its"]}, {"tag": "equal", "positive_start": 11, "positive_end": 12, "negative_start": 11, "negative_end": 12, "positive_lexemes": ["side"], "negative_lexemes": ["side"]}]`
- 共同前缀：`["a"]`
- 正确 contrast hull：`["american", "flag", "painted", "fire", "hydrant", "with", "chains", "hanging", "at", "it"]`
- 错误 contrast hull：`["british", "flag", "painted", "fire", "hydrant", "with", "chains", "hanging", "at", "its"]`
- 共同后缀：`["side"]`
- Hull token 覆盖率（正/负/最大）：`[0.92, 0.9166666666666666, 0.92]`
- 共同前缀模型 token：`[100]`
- 正确 hull 模型 token：IDs `[1746, 311, 375, 325, 3687, 1163, 5063, 4587, 341, 1475, 5548, 103, 117, 811, 599, 890, 740, 118, 429, 942, 350, 1248, 563]`；text " american flag painted fire hydrant with chains hanging at it"
- 错误 hull 模型 token：IDs `[363, 2157, 1689, 3687, 1163, 5063, 4587, 341, 1475, 5548, 103, 117, 811, 599, 890, 740, 118, 429, 942, 350, 1248, 1342]`；text " british flag painted fire hydrant with chains hanging at its"
- 第一轮/第二轮分类：`complex_edit` / `large_contrast_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；"maximum_hull_token_coverage_above_75_percent"

### 2. `replace_object:1134`

- 负例类型/范围：`replace_object` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A green fruit tree yields fruit not yet ready for harvest."
- 原始正描述 2："The fruit tree, which is green, produces fruit that is not yet ready for harvest."
- 原始负描述："A green flowering bush yields flowers not yet ready for picking."
- 规范化正描述 1："a green fruit tree yields fruit not yet ready for harvest"
- 规范化正描述 2："the fruit tree , which is green , produces fruit that is not yet ready for harvest"
- 规范化负描述："a green flowering bush yields flowers not yet ready for picking"
- 正描述 1 选择元组：`[8, 18, 3, 0.36363636363636365, 0.38095238095238093]`
- 正描述 2 选择元组：`[18, 28, 5, 0.7058823529411765, 0.6219512195121951]`
- 最终比较正描述：`positive_1` / "A green fruit tree yields fruit not yet ready for harvest."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 2, "negative_start": 0, "negative_end": 2, "positive_lexemes": ["a", "green"], "negative_lexemes": ["a", "green"]}, {"tag": "replace", "positive_start": 2, "positive_end": 4, "negative_start": 2, "negative_end": 4, "positive_lexemes": ["fruit", "tree"], "negative_lexemes": ["flowering", "bush"]}, {"tag": "equal", "positive_start": 4, "positive_end": 5, "negative_start": 4, "negative_end": 5, "positive_lexemes": ["yields"], "negative_lexemes": ["yields"]}, {"tag": "replace", "positive_start": 5, "positive_end": 6, "negative_start": 5, "negative_end": 6, "positive_lexemes": ["fruit"], "negative_lexemes": ["flowers"]}, {"tag": "equal", "positive_start": 6, "positive_end": 10, "negative_start": 6, "negative_end": 10, "positive_lexemes": ["not", "yet", "ready", "for"], "negative_lexemes": ["not", "yet", "ready", "for"]}, {"tag": "replace", "positive_start": 10, "positive_end": 11, "negative_start": 10, "negative_end": 11, "positive_lexemes": ["harvest"], "negative_lexemes": ["picking"]}]`
- 共同前缀：`["a", "green"]`
- 正确 contrast hull：`["fruit", "tree", "yields", "fruit", "not", "yet", "ready", "for", "harvest"]`
- 错误 contrast hull：`["flowering", "bush", "yields", "flowers", "not", "yet", "ready", "for", "picking"]`
- 共同后缀：`[]`
- Hull token 覆盖率（正/负/最大）：`[0.9130434782608695, 0.9, 0.9130434782608695]`
- 共同前缀模型 token：`[100, 5921]`
- 正确 hull 模型 token：IDs `[341, 1737, 338, 297, 1382, 385, 2729, 1881, 341, 1737, 338, 1027, 385, 439, 3094, 124, 503, 429, 370, 121, 611]`；text " fruit tree yields fruit not yet ready for harvest"
- 错误 hull 模型 token：IDs `[5652, 3906, 2499, 107, 385, 2729, 1881, 5652, 496, 1027, 385, 439, 3094, 124, 503, 344, 375, 1237]`；text " flowering bush yields flowers not yet ready for picking"
- 第一轮/第二轮分类：`complex_edit` / `large_contrast_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；"maximum_hull_token_coverage_above_75_percent"

### 3. `replace_object:1143`

- 负例类型/范围：`replace_object` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A baseball player pitching a ball on a field,"
- 原始正描述 2："A baseball player is on a field pitching a ball"
- 原始负描述："A soccer player kicking a ball on a field."
- 规范化正描述 1："a baseball player pitching a ball on a field ,"
- 规范化正描述 2："a baseball player is on a field pitching a ball"
- 规范化负描述："a soccer player kicking a ball on a field"
- 正描述 1 选择元组：`[5, 17, 3, 0.3, 0.2608695652173913]`
- 正描述 2 选择元组：`[11, 17, 5, 0.6, 0.574468085106383]`
- 最终比较正描述：`positive_1` / "A baseball player pitching a ball on a field,"
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 1, "negative_start": 0, "negative_end": 1, "positive_lexemes": ["a"], "negative_lexemes": ["a"]}, {"tag": "replace", "positive_start": 1, "positive_end": 2, "negative_start": 1, "negative_end": 2, "positive_lexemes": ["baseball"], "negative_lexemes": ["soccer"]}, {"tag": "equal", "positive_start": 2, "positive_end": 3, "negative_start": 2, "negative_end": 3, "positive_lexemes": ["player"], "negative_lexemes": ["player"]}, {"tag": "replace", "positive_start": 3, "positive_end": 4, "negative_start": 3, "negative_end": 4, "positive_lexemes": ["pitching"], "negative_lexemes": ["kicking"]}, {"tag": "equal", "positive_start": 4, "positive_end": 9, "negative_start": 4, "negative_end": 9, "positive_lexemes": ["a", "ball", "on", "a", "field"], "negative_lexemes": ["a", "ball", "on", "a", "field"]}, {"tag": "delete", "positive_start": 9, "positive_end": 10, "negative_start": 9, "negative_end": 9, "positive_lexemes": [","], "negative_lexemes": []}]`
- 共同前缀：`["a"]`
- 正确 contrast hull：`["baseball", "player", "pitching", "a", "ball", "on", "a", "field", ","]`
- 错误 contrast hull：`["soccer", "player", "kicking", "a", "ball", "on", "a", "field"]`
- 共同后缀：`[]`
- Hull token 覆盖率（正/负/最大）：`[0.9444444444444444, 0.9333333333333333, 0.9444444444444444]`
- 共同前缀模型 token：`[100]`
- 正确 hull 模型 token：IDs `[4933, 101, 1266, 2865, 311, 344, 338, 550, 350, 299, 363, 1266, 619, 299, 4749, 256, 47]`；text " baseball player pitching a ball on a field ,"
- 错误 hull 模型 token：IDs `[1122, 1130, 311, 2865, 311, 914, 375, 1237, 299, 363, 1266, 619, 299, 4749]`；text " soccer player kicking a ball on a field"
- 第一轮/第二轮分类：`complex_edit` / `large_contrast_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；"maximum_hull_token_coverage_above_75_percent"

### 4. `replace_object:1426`

- 负例类型/范围：`replace_object` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A herd of giraffes are playing in a field."
- 原始正描述 2："In the field, a group of giraffes are engaged in play."
- 原始负描述："A flock of seagulls are playing on a beach."
- 规范化正描述 1："a herd of giraffes are playing in a field"
- 规范化正描述 2："in the field , a group of giraffes are engaged in play"
- 规范化负描述："a flock of seagulls are playing on a beach"
- 正描述 1 选择元组：`[8, 16, 4, 0.4444444444444444, 0.42857142857142855]`
- 正描述 2 选择元组：`[15, 21, 5, 0.8333333333333334, 0.7222222222222222]`
- 最终比较正描述：`positive_1` / "A herd of giraffes are playing in a field."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 1, "negative_start": 0, "negative_end": 1, "positive_lexemes": ["a"], "negative_lexemes": ["a"]}, {"tag": "replace", "positive_start": 1, "positive_end": 2, "negative_start": 1, "negative_end": 2, "positive_lexemes": ["herd"], "negative_lexemes": ["flock"]}, {"tag": "equal", "positive_start": 2, "positive_end": 3, "negative_start": 2, "negative_end": 3, "positive_lexemes": ["of"], "negative_lexemes": ["of"]}, {"tag": "replace", "positive_start": 3, "positive_end": 4, "negative_start": 3, "negative_end": 4, "positive_lexemes": ["giraffes"], "negative_lexemes": ["seagulls"]}, {"tag": "equal", "positive_start": 4, "positive_end": 6, "negative_start": 4, "negative_end": 6, "positive_lexemes": ["are", "playing"], "negative_lexemes": ["are", "playing"]}, {"tag": "replace", "positive_start": 6, "positive_end": 7, "negative_start": 6, "negative_end": 7, "positive_lexemes": ["in"], "negative_lexemes": ["on"]}, {"tag": "equal", "positive_start": 7, "positive_end": 8, "negative_start": 7, "negative_end": 8, "positive_lexemes": ["a"], "negative_lexemes": ["a"]}, {"tag": "replace", "positive_start": 8, "positive_end": 9, "negative_start": 8, "negative_end": 9, "positive_lexemes": ["field"], "negative_lexemes": ["beach"]}]`
- 共同前缀：`["a"]`
- 正确 contrast hull：`["herd", "of", "giraffes", "are", "playing", "in", "a", "field"]`
- 错误 contrast hull：`["flock", "of", "seagulls", "are", "playing", "on", "a", "beach"]`
- 共同后缀：`[]`
- Hull token 覆盖率（正/负/最大）：`[0.9333333333333333, 0.9333333333333333, 0.9333333333333333]`
- 共同前缀模型 token：`[100]`
- 正确 hull 模型 token：IDs `[2833, 103, 354, 492, 108, 559, 1627, 329, 732, 2865, 350, 353, 299, 4749]`；text " herd of giraffes are playing in a field"
- 错误 hull 模型 token：IDs `[5796, 892, 354, 762, 1163, 3800, 118, 732, 2865, 350, 619, 299, 600, 1268]`；text " flock of seagulls are playing on a beach"
- 第一轮/第二轮分类：`complex_edit` / `large_contrast_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；"maximum_hull_token_coverage_above_75_percent"

### 5. `replace_object:1597`

- 负例类型/范围：`replace_object` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A large metal chair with a brown teddy bear in it."
- 原始正描述 2："There is a brown teddy bear seated in a large chair made of metal."
- 原始负描述："A brown teddy bear is in a hammock."
- 规范化正描述 1："a large metal chair with a brown teddy bear in it"
- 规范化正描述 2："there is a brown teddy bear seated in a large chair made of metal"
- 规范化负描述："a brown teddy bear is in a hammock"
- 正描述 1 选择元组：`[9, 19, 4, 0.7272727272727273, 0.7142857142857143]`
- 正描述 2 选择元组：`[10, 22, 4, 0.5714285714285714, 0.5538461538461539]`
- 最终比较正描述：`positive_1` / "A large metal chair with a brown teddy bear in it."
- 完整 lexeme 编辑块：`[{"tag": "delete", "positive_start": 0, "positive_end": 5, "negative_start": 0, "negative_end": 0, "positive_lexemes": ["a", "large", "metal", "chair", "with"], "negative_lexemes": []}, {"tag": "equal", "positive_start": 5, "positive_end": 9, "negative_start": 0, "negative_end": 4, "positive_lexemes": ["a", "brown", "teddy", "bear"], "negative_lexemes": ["a", "brown", "teddy", "bear"]}, {"tag": "insert", "positive_start": 9, "positive_end": 9, "negative_start": 4, "negative_end": 5, "positive_lexemes": [], "negative_lexemes": ["is"]}, {"tag": "equal", "positive_start": 9, "positive_end": 10, "negative_start": 5, "negative_end": 6, "positive_lexemes": ["in"], "negative_lexemes": ["in"]}, {"tag": "insert", "positive_start": 10, "positive_end": 10, "negative_start": 6, "negative_end": 7, "positive_lexemes": [], "negative_lexemes": ["a"]}, {"tag": "replace", "positive_start": 10, "positive_end": 11, "negative_start": 7, "negative_end": 8, "positive_lexemes": ["it"], "negative_lexemes": ["hammock"]}]`
- 共同前缀：`[]`
- 正确 contrast hull：`["a", "large", "metal", "chair", "with", "a", "brown", "teddy", "bear", "in", "it"]`
- 错误 contrast hull：`["a", "brown", "teddy", "bear", "is", "in", "a", "hammock"]`
- 共同后缀：`[]`
- Hull token 覆盖率（正/负/最大）：`[1.0, 1.0, 1.0]`
- 共同前缀模型 token：`[]`
- 正确 hull 模型 token：IDs `[100, 2994, 4743, 352, 890, 3709, 599, 299, 363, 2079, 113, 297, 382, 103, 124, 600, 370, 353, 563]`；text "a large metal chair with a brown teddy bear in it"
- 错误 hull 模型 token：IDs `[100, 363, 2079, 113, 297, 382, 103, 124, 600, 370, 395, 353, 299, 429, 497, 112, 4469]`；text "a brown teddy bear is in a hammock"
- 第一轮/第二轮分类：`complex_edit` / `whole_sentence_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；"at_least_one_hull_covers_all_model_tokens"

### 6. `replace_object:626`

- 负例类型/范围：`replace_object` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A man is cutting into a cake as someone hugs him."
- 原始正描述 2："Someone is hugging a man as he cutting a cake."
- 原始负描述："A child is cutting into a cake as someone hugs them."
- 规范化正描述 1："a man is cutting into a cake as someone hugs him"
- 规范化正描述 2："someone is hugging a man as he cutting a cake"
- 规范化负描述："a child is cutting into a cake as someone hugs them"
- 正描述 1 选择元组：`[4, 20, 2, 0.18181818181818182, 0.13725490196078433]`
- 正描述 2 选择元组：`[15, 21, 7, 0.8181818181818182, 0.6666666666666666]`
- 最终比较正描述：`positive_1` / "A man is cutting into a cake as someone hugs him."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 1, "negative_start": 0, "negative_end": 1, "positive_lexemes": ["a"], "negative_lexemes": ["a"]}, {"tag": "replace", "positive_start": 1, "positive_end": 2, "negative_start": 1, "negative_end": 2, "positive_lexemes": ["man"], "negative_lexemes": ["child"]}, {"tag": "equal", "positive_start": 2, "positive_end": 10, "negative_start": 2, "negative_end": 10, "positive_lexemes": ["is", "cutting", "into", "a", "cake", "as", "someone", "hugs"], "negative_lexemes": ["is", "cutting", "into", "a", "cake", "as", "someone", "hugs"]}, {"tag": "replace", "positive_start": 10, "positive_end": 11, "negative_start": 10, "negative_end": 11, "positive_lexemes": ["him"], "negative_lexemes": ["them"]}]`
- 共同前缀：`["a"]`
- 正确 contrast hull：`["man", "is", "cutting", "into", "a", "cake", "as", "someone", "hugs", "him"]`
- 错误 contrast hull：`["child", "is", "cutting", "into", "a", "cake", "as", "someone", "hugs", "them"]`
- 共同后缀：`[]`
- Hull token 覆盖率（正/负/最大）：`[0.9375, 0.9333333333333333, 0.9375]`
- 共同前缀模型 token：`[100]`
- 正确 hull 模型 token：IDs `[1672, 395, 5431, 2912, 1669, 299, 317, 2434, 523, 4779, 429, 3304, 118, 429, 467]`；text " man is cutting into a cake as someone hugs him"
- 错误 hull 模型 token：IDs `[6109, 395, 5431, 2912, 1669, 299, 317, 2434, 523, 4779, 429, 3304, 118, 2105]`；text " child is cutting into a cake as someone hugs them"
- 第一轮/第二轮分类：`complex_edit` / `large_contrast_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；"maximum_hull_token_coverage_above_75_percent"

### 7. `replace_object:737`

- 负例类型/范围：`replace_object` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A man cuting a piece of cake while a person in costume stands behind him."
- 原始正描述 2："A person in costume stands behind a man who is cutting a piece of cake."
- 原始负描述："A woman cutting a piece of cake while a person in costume stands behind her."
- 规范化正描述 1："a man cuting a piece of cake while a person in costume stands behind him"
- 规范化正描述 2："a person in costume stands behind a man who is cutting a piece of cake"
- 规范化负描述："a woman cutting a piece of cake while a person in costume stands behind her"
- 正描述 1 选择元组：`[6, 28, 2, 0.2, 0.06666666666666667]`
- 正描述 2 选择元组：`[28, 28, 1, 0.9333333333333333, 0.7333333333333333]`
- 最终比较正描述：`positive_1` / "A man cuting a piece of cake while a person in costume stands behind him."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 1, "negative_start": 0, "negative_end": 1, "positive_lexemes": ["a"], "negative_lexemes": ["a"]}, {"tag": "replace", "positive_start": 1, "positive_end": 3, "negative_start": 1, "negative_end": 3, "positive_lexemes": ["man", "cuting"], "negative_lexemes": ["woman", "cutting"]}, {"tag": "equal", "positive_start": 3, "positive_end": 14, "negative_start": 3, "negative_end": 14, "positive_lexemes": ["a", "piece", "of", "cake", "while", "a", "person", "in", "costume", "stands", "behind"], "negative_lexemes": ["a", "piece", "of", "cake", "while", "a", "person", "in", "costume", "stands", "behind"]}, {"tag": "replace", "positive_start": 14, "positive_end": 15, "negative_start": 14, "negative_end": 15, "positive_lexemes": ["him"], "negative_lexemes": ["her"]}]`
- 共同前缀：`["a"]`
- 正确 contrast hull：`["man", "cuting", "a", "piece", "of", "cake", "while", "a", "person", "in", "costume", "stands", "behind", "him"]`
- 错误 contrast hull：`["woman", "cutting", "a", "piece", "of", "cake", "while", "a", "person", "in", "costume", "stands", "behind", "her"]`
- 共同后缀：`[]`
- Hull token 覆盖率（正/负/最大）：`[0.9545454545454546, 0.9565217391304348, 0.9565217391304348]`
- 共同前缀模型 token：`[100]`
- 正确 hull 模型 token：IDs `[1672, 5431, 350, 299, 5690, 473, 354, 317, 2434, 3052, 299, 2198, 353, 3756, 4557, 2823, 118, 5237, 916, 429, 467]`；text " man cuting a piece of cake while a person in costume stands behind him"
- 错误 hull 模型 token：IDs `[339, 444, 325, 5431, 2912, 299, 5690, 473, 354, 317, 2434, 3052, 299, 2198, 353, 3756, 4557, 2823, 118, 5237, 916, 2833]`；text " woman cutting a piece of cake while a person in costume stands behind her"
- 第一轮/第二轮分类：`complex_edit` / `large_contrast_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；"maximum_hull_token_coverage_above_75_percent"

### 8. `replace_object:793`

- 负例类型/范围：`replace_object` / `{"canonical": true, "pilot": true, "formal": false, "certifying_formal": false}`
- 原始正描述 1："A man on a cellphone sticking his finger in his ear."
- 原始正描述 2："A man is holding a cellphone and sticking his finger in his ear."
- 原始负描述："A woman on a cellphone sticking her finger in her ear."
- 规范化正描述 1："a man on a cellphone sticking his finger in his ear"
- 规范化正描述 2："a man is holding a cellphone and sticking his finger in his ear"
- 规范化负描述："a woman on a cellphone sticking her finger in her ear"
- 正描述 1 选择元组：`[6, 18, 3, 0.2727272727272727, 0.11320754716981132]`
- 正描述 2 选择元组：`[10, 20, 5, 0.46153846153846156, 0.2857142857142857]`
- 最终比较正描述：`positive_1` / "A man on a cellphone sticking his finger in his ear."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 1, "negative_start": 0, "negative_end": 1, "positive_lexemes": ["a"], "negative_lexemes": ["a"]}, {"tag": "replace", "positive_start": 1, "positive_end": 2, "negative_start": 1, "negative_end": 2, "positive_lexemes": ["man"], "negative_lexemes": ["woman"]}, {"tag": "equal", "positive_start": 2, "positive_end": 6, "negative_start": 2, "negative_end": 6, "positive_lexemes": ["on", "a", "cellphone", "sticking"], "negative_lexemes": ["on", "a", "cellphone", "sticking"]}, {"tag": "replace", "positive_start": 6, "positive_end": 7, "negative_start": 6, "negative_end": 7, "positive_lexemes": ["his"], "negative_lexemes": ["her"]}, {"tag": "equal", "positive_start": 7, "positive_end": 9, "negative_start": 7, "negative_end": 9, "positive_lexemes": ["finger", "in"], "negative_lexemes": ["finger", "in"]}, {"tag": "replace", "positive_start": 9, "positive_end": 10, "negative_start": 9, "negative_end": 10, "positive_lexemes": ["his"], "negative_lexemes": ["her"]}, {"tag": "equal", "positive_start": 10, "positive_end": 11, "negative_start": 10, "negative_end": 11, "positive_lexemes": ["ear"], "negative_lexemes": ["ear"]}]`
- 共同前缀：`["a"]`
- 正确 contrast hull：`["man", "on", "a", "cellphone", "sticking", "his", "finger", "in", "his"]`
- 错误 contrast hull：`["woman", "on", "a", "cellphone", "sticking", "her", "finger", "in", "her"]`
- 共同后缀：`["ear"]`
- Hull token 覆盖率（正/负/最大）：`[0.8947368421052632, 0.9047619047619048, 0.9047619047619048]`
- 共同前缀模型 token：`[100]`
- 正确 hull 模型 token：IDs `[1672, 619, 299, 317, 446, 823, 107, 1634, 580, 375, 1237, 2049, 341, 350, 311, 353, 2049]`；text " man on a cellphone sticking his finger in his"
- 错误 hull 模型 token：IDs `[339, 444, 325, 619, 299, 317, 446, 823, 107, 1634, 580, 375, 1237, 2833, 341, 350, 311, 353, 2833]`；text " woman on a cellphone sticking her finger in her"
- 第一轮/第二轮分类：`complex_edit` / `large_contrast_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；"maximum_hull_token_coverage_above_75_percent"

### 9. `replace_relation:416`

- 负例类型/范围：`replace_relation` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A person holds a phone in a car with the window rolled down"
- 原始正描述 2："A phone is held by a person in a car with the window rolled down."
- 原始负描述："A person is outside a car with the window rolled down, holding a phone."
- 规范化正描述 1："a person holds a phone in a car with the window rolled down"
- 规范化正描述 2："a phone is held by a person in a car with the window rolled down"
- 规范化负描述："a person is outside a car with the window rolled down , holding a phone"
- 正描述 1 选择元组：`[10, 24, 3, 0.5333333333333333, 0.43661971830985913]`
- 正描述 2 选择元组：`[12, 28, 4, 0.6666666666666666, 0.5633802816901409]`
- 最终比较正描述：`positive_1` / "A person holds a phone in a car with the window rolled down"
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 2, "negative_start": 0, "negative_end": 2, "positive_lexemes": ["a", "person"], "negative_lexemes": ["a", "person"]}, {"tag": "delete", "positive_start": 2, "positive_end": 4, "negative_start": 2, "negative_end": 2, "positive_lexemes": ["holds", "a"], "negative_lexemes": []}, {"tag": "replace", "positive_start": 4, "positive_end": 6, "negative_start": 2, "negative_end": 4, "positive_lexemes": ["phone", "in"], "negative_lexemes": ["is", "outside"]}, {"tag": "equal", "positive_start": 6, "positive_end": 13, "negative_start": 4, "negative_end": 11, "positive_lexemes": ["a", "car", "with", "the", "window", "rolled", "down"], "negative_lexemes": ["a", "car", "with", "the", "window", "rolled", "down"]}, {"tag": "insert", "positive_start": 13, "positive_end": 13, "negative_start": 11, "negative_end": 15, "positive_lexemes": [], "negative_lexemes": [",", "holding", "a", "phone"]}]`
- 共同前缀：`["a", "person"]`
- 正确 contrast hull：`["holds", "a", "phone", "in", "a", "car", "with", "the", "window", "rolled", "down"]`
- 错误 contrast hull：`["is", "outside", "a", "car", "with", "the", "window", "rolled", "down", ",", "holding", "a", "phone"]`
- 共同后缀：`[]`
- Hull token 覆盖率（正/负/最大）：`[0.8947368421052632, 0.9166666666666666, 0.9166666666666666]`
- 共同前缀模型 token：`[100, 2198]`
- 正确 hull 模型 token：IDs `[429, 500, 1881, 299, 2001, 1634, 353, 299, 3751, 599, 309, 5472, 451, 1552, 111, 2003, 4076]`；text " holds a phone in a car with the window rolled down"
- 错误 hull 模型 token：IDs `[395, 1695, 118, 688, 299, 3751, 599, 309, 5472, 451, 1552, 111, 2003, 4076, 256, 47, 429, 2569, 350, 299, 2001, 1634]`；text " is outside a car with the window rolled down , holding a phone"
- 第一轮/第二轮分类：`complex_edit` / `large_contrast_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；"maximum_hull_token_coverage_above_75_percent"

### 10. `replace_relation:495`

- 负例类型/范围：`replace_relation` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A person grabbing a slice of pizza from a pizza box."
- 原始正描述 2："An individual seizes a pizza slice from a pizza box."
- 原始负描述："A person setting down a slice of pizza onto a plate."
- 规范化正描述 1："a person grabbing a slice of pizza from a pizza box"
- 规范化正描述 2："an individual seizes a pizza slice from a pizza box"
- 规范化负描述："a person setting down a slice of pizza onto a plate"
- 正描述 1 选择元组：`[8, 18, 5, 0.45454545454545453, 0.4117647058823529]`
- 正描述 2 选择元组：`[19, 21, 3, 0.9090909090909091, 0.7450980392156863]`
- 最终比较正描述：`positive_1` / "A person grabbing a slice of pizza from a pizza box."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 2, "negative_start": 0, "negative_end": 2, "positive_lexemes": ["a", "person"], "negative_lexemes": ["a", "person"]}, {"tag": "insert", "positive_start": 2, "positive_end": 2, "negative_start": 2, "negative_end": 3, "positive_lexemes": [], "negative_lexemes": ["setting"]}, {"tag": "replace", "positive_start": 2, "positive_end": 3, "negative_start": 3, "negative_end": 4, "positive_lexemes": ["grabbing"], "negative_lexemes": ["down"]}, {"tag": "equal", "positive_start": 3, "positive_end": 7, "negative_start": 4, "negative_end": 8, "positive_lexemes": ["a", "slice", "of", "pizza"], "negative_lexemes": ["a", "slice", "of", "pizza"]}, {"tag": "replace", "positive_start": 7, "positive_end": 8, "negative_start": 8, "negative_end": 9, "positive_lexemes": ["from"], "negative_lexemes": ["onto"]}, {"tag": "equal", "positive_start": 8, "positive_end": 9, "negative_start": 9, "negative_end": 10, "positive_lexemes": ["a"], "negative_lexemes": ["a"]}, {"tag": "delete", "positive_start": 9, "positive_end": 10, "negative_start": 10, "negative_end": 10, "positive_lexemes": ["pizza"], "negative_lexemes": []}, {"tag": "replace", "positive_start": 10, "positive_end": 11, "negative_start": 10, "negative_end": 11, "positive_lexemes": ["box"], "negative_lexemes": ["plate"]}]`
- 共同前缀：`["a", "person"]`
- 正确 contrast hull：`["grabbing", "a", "slice", "of", "pizza", "from", "a", "pizza", "box"]`
- 错误 contrast hull：`["setting", "down", "a", "slice", "of", "pizza", "onto", "a", "plate"]`
- 共同后缀：`[]`
- Hull token 覆盖率（正/负/最大）：`[0.9130434782608695, 0.8947368421052632, 0.9130434782608695]`
- 共同前缀模型 token：`[100, 2198]`
- 正确 hull 模型 token：IDs `[5528, 101, 101, 350, 299, 316, 111, 1126, 354, 344, 1028, 125, 100, 961, 299, 344, 1028, 125, 100, 1847, 123]`；text " grabbing a slice of pizza from a pizza box"
- 错误 hull 模型 token：IDs `[2139, 2912, 4076, 299, 316, 111, 1126, 354, 344, 1028, 125, 100, 619, 2263, 299, 1219, 557]`；text " setting down a slice of pizza onto a plate"
- 第一轮/第二轮分类：`complex_edit` / `large_contrast_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；"maximum_hull_token_coverage_above_75_percent"

### 11. `swap_atribute:120`

- 负例类型/范围：`swap_atribute` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："a couple is sitting on a statue of a horse, next to some plants"
- 原始正描述 2："A couple is seated on a statue of a horse, next to some plants."
- 原始负描述："Some couples are sitting on a statue of a horse next to a plant."
- 规范化正描述 1："a couple is sitting on a statue of a horse , next to some plants"
- 规范化正描述 2："a couple is seated on a statue of a horse , next to some plants"
- 规范化负描述："some couples are sitting on a statue of a horse next to a plant"
- 正描述 1 选择元组：`[11, 29, 3, 0.4, 0.234375]`
- 正描述 2 选择元组：`[13, 29, 3, 0.4666666666666667, 0.31746031746031744]`
- 最终比较正描述：`positive_1` / "a couple is sitting on a statue of a horse, next to some plants"
- 完整 lexeme 编辑块：`[{"tag": "replace", "positive_start": 0, "positive_end": 3, "negative_start": 0, "negative_end": 3, "positive_lexemes": ["a", "couple", "is"], "negative_lexemes": ["some", "couples", "are"]}, {"tag": "equal", "positive_start": 3, "positive_end": 10, "negative_start": 3, "negative_end": 10, "positive_lexemes": ["sitting", "on", "a", "statue", "of", "a", "horse"], "negative_lexemes": ["sitting", "on", "a", "statue", "of", "a", "horse"]}, {"tag": "delete", "positive_start": 10, "positive_end": 11, "negative_start": 10, "negative_end": 10, "positive_lexemes": [","], "negative_lexemes": []}, {"tag": "equal", "positive_start": 11, "positive_end": 13, "negative_start": 10, "negative_end": 12, "positive_lexemes": ["next", "to"], "negative_lexemes": ["next", "to"]}, {"tag": "replace", "positive_start": 13, "positive_end": 15, "negative_start": 12, "negative_end": 14, "positive_lexemes": ["some", "plants"], "negative_lexemes": ["a", "plant"]}]`
- 共同前缀：`[]`
- 正确 contrast hull：`["a", "couple", "is", "sitting", "on", "a", "statue", "of", "a", "horse", ",", "next", "to", "some", "plants"]`
- 错误 contrast hull：`["some", "couples", "are", "sitting", "on", "a", "statue", "of", "a", "horse", "next", "to", "a", "plant"]`
- 共同后缀：`[]`
- Hull token 覆盖率（正/负/最大）：`[1.0, 1.0, 1.0]`
- 共同前缀模型 token：`[]`
- 正确 hull 模型 token：IDs `[100, 317, 326, 833, 395, 5305, 2912, 619, 299, 5643, 922, 354, 299, 429, 336, 573, 256, 47, 4658, 364, 2104, 1219, 5483]`；text "a couple is sitting on a statue of a horse , next to some plants"
- 错误 hull 模型 token：IDs `[118, 3219, 317, 326, 4711, 732, 5305, 2912, 619, 299, 5643, 922, 354, 299, 429, 336, 573, 4658, 364, 299, 1219, 811]`；text "some couples are sitting on a statue of a horse next to a plant"
- 第一轮/第二轮分类：`complex_edit` / `whole_sentence_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；"at_least_one_hull_covers_all_model_tokens"

### 12. `swap_atribute:130`

- 负例类型/范围：`swap_atribute` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："An old rusted fire hydrant is on the ground near a painted wall."
- 原始正描述 2："The painted wall is adjacent to the ground where an old rusted fire hydrant is positioned."
- 原始负描述："A painted fire hydrant is on the ground near an old rusted wall."
- 规范化正描述 1："an old rusted fire hydrant is on the ground near a painted wall"
- 规范化正描述 2："the painted wall is adjacent to the ground where an old rusted fire hydrant is positioned"
- 规范化负描述："a painted fire hydrant is on the ground near an old rusted wall"
- 正描述 1 选择元组：`[10, 24, 4, 0.46153846153846156, 0.25396825396825395]`
- 正描述 2 选择元组：`[17, 29, 5, 0.625, 0.5280898876404494]`
- 最终比较正描述：`positive_1` / "An old rusted fire hydrant is on the ground near a painted wall."
- 完整 lexeme 编辑块：`[{"tag": "delete", "positive_start": 0, "positive_end": 1, "negative_start": 0, "negative_end": 0, "positive_lexemes": ["an"], "negative_lexemes": []}, {"tag": "replace", "positive_start": 1, "positive_end": 3, "negative_start": 0, "negative_end": 2, "positive_lexemes": ["old", "rusted"], "negative_lexemes": ["a", "painted"]}, {"tag": "equal", "positive_start": 3, "positive_end": 10, "negative_start": 2, "negative_end": 9, "positive_lexemes": ["fire", "hydrant", "is", "on", "the", "ground", "near"], "negative_lexemes": ["fire", "hydrant", "is", "on", "the", "ground", "near"]}, {"tag": "insert", "positive_start": 10, "positive_end": 10, "negative_start": 9, "negative_end": 10, "positive_lexemes": [], "negative_lexemes": ["an"]}, {"tag": "replace", "positive_start": 10, "positive_end": 12, "negative_start": 10, "negative_end": 12, "positive_lexemes": ["a", "painted"], "negative_lexemes": ["old", "rusted"]}, {"tag": "equal", "positive_start": 12, "positive_end": 13, "negative_start": 12, "negative_end": 13, "positive_lexemes": ["wall"], "negative_lexemes": ["wall"]}]`
- 共同前缀：`[]`
- 正确 contrast hull：`["an", "old", "rusted", "fire", "hydrant", "is", "on", "the", "ground", "near", "a", "painted"]`
- 错误 contrast hull：`["a", "painted", "fire", "hydrant", "is", "on", "the", "ground", "near", "an", "old", "rusted"]`
- 共同后缀：`["wall"]`
- Hull token 覆盖率（正/负/最大）：`[0.9130434782608695, 0.9130434782608695, 0.9130434782608695]`
- 共同前缀模型 token：`[]`
- 正确 hull 模型 token：IDs `[325, 4797, 757, 1076, 382, 341, 1475, 5548, 103, 117, 811, 395, 619, 309, 492, 2383, 730, 370, 299, 5063, 4587]`；text "an old rusted fire hydrant is on the ground near a painted"
- 错误 hull 模型 token：IDs `[100, 5063, 4587, 341, 1475, 5548, 103, 117, 811, 395, 619, 309, 492, 2383, 730, 370, 346, 4797, 757, 1076, 382]`；text "a painted fire hydrant is on the ground near an old rusted"
- 第一轮/第二轮分类：`complex_edit` / `large_contrast_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；"maximum_hull_token_coverage_above_75_percent"

### 13. `swap_atribute:215`

- 负例类型/范围：`swap_atribute` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A couple of detour signs sitting on either side of an orange cone."
- 原始正描述 2："A couple of detour signs are positioned on both sides of an orange cone"
- 原始负描述："An orange detour sign sitting on either side of a couple of cones."
- 规范化正描述 1："a couple of detour signs sitting on either side of an orange cone"
- 规范化正描述 2："a couple of detour signs are positioned on both sides of an orange cone"
- 规范化负描述："an orange detour sign sitting on either side of a couple of cones"
- 正描述 1 选择元组：`[14, 26, 5, 0.6153846153846154, 0.3076923076923077]`
- 正描述 2 选择元组：`[21, 27, 7, 0.8571428571428571, 0.49295774647887325]`
- 最终比较正描述：`positive_1` / "A couple of detour signs sitting on either side of an orange cone."
- 完整 lexeme 编辑块：`[{"tag": "delete", "positive_start": 0, "positive_end": 1, "negative_start": 0, "negative_end": 0, "positive_lexemes": ["a"], "negative_lexemes": []}, {"tag": "replace", "positive_start": 1, "positive_end": 3, "negative_start": 0, "negative_end": 2, "positive_lexemes": ["couple", "of"], "negative_lexemes": ["an", "orange"]}, {"tag": "equal", "positive_start": 3, "positive_end": 4, "negative_start": 2, "negative_end": 3, "positive_lexemes": ["detour"], "negative_lexemes": ["detour"]}, {"tag": "replace", "positive_start": 4, "positive_end": 5, "negative_start": 3, "negative_end": 4, "positive_lexemes": ["signs"], "negative_lexemes": ["sign"]}, {"tag": "equal", "positive_start": 5, "positive_end": 10, "negative_start": 4, "negative_end": 9, "positive_lexemes": ["sitting", "on", "either", "side", "of"], "negative_lexemes": ["sitting", "on", "either", "side", "of"]}, {"tag": "insert", "positive_start": 10, "positive_end": 10, "negative_start": 9, "negative_end": 10, "positive_lexemes": [], "negative_lexemes": ["a"]}, {"tag": "replace", "positive_start": 10, "positive_end": 13, "negative_start": 10, "negative_end": 13, "positive_lexemes": ["an", "orange", "cone"], "negative_lexemes": ["couple", "of", "cones"]}]`
- 共同前缀：`[]`
- 正确 contrast hull：`["a", "couple", "of", "detour", "signs", "sitting", "on", "either", "side", "of", "an", "orange", "cone"]`
- 错误 contrast hull：`["an", "orange", "detour", "sign", "sitting", "on", "either", "side", "of", "a", "couple", "of", "cones"]`
- 共同后缀：`[]`
- Hull token 覆盖率（正/负/最大）：`[1.0, 1.0, 1.0]`
- 共同前缀模型 token：`[]`
- 正确 hull 模型 token：IDs `[100, 317, 326, 833, 354, 1503, 1084, 2185, 118, 5305, 2912, 619, 413, 338, 771, 5046, 354, 346, 522, 1285, 614, 104]`；text "a couple of detour signs sitting on either side of an orange cone"
- 错误 hull 模型 token：IDs `[325, 522, 1285, 1503, 1084, 2185, 5305, 2912, 619, 413, 338, 771, 5046, 354, 299, 317, 326, 833, 354, 614, 329]`；text "an orange detour sign sitting on either side of a couple of cones"
- 第一轮/第二轮分类：`complex_edit` / `whole_sentence_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；"at_least_one_hull_covers_all_model_tokens"

### 14. `swap_atribute:271`

- 负例类型/范围：`swap_atribute` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："Four surfers are trying to catch a wave as they stand."
- 原始正描述 2："Four surfers are standing while trying to catch a wave."
- 原始负描述："Trying to catch four waves, surfers stand."
- 规范化正描述 1："four surfers are trying to catch a wave as they stand"
- 规范化正描述 2："four surfers are standing while trying to catch a wave"
- 规范化负描述："trying to catch four waves , surfers stand"
- 正描述 1 选择元组：`[11, 17, 2, 0.6363636363636364, 0.5471698113207547]`
- 正描述 2 选择元组：`[18, 18, 2, 1.0, 0.8333333333333334]`
- 最终比较正描述：`positive_1` / "Four surfers are trying to catch a wave as they stand."
- 完整 lexeme 编辑块：`[{"tag": "delete", "positive_start": 0, "positive_end": 3, "negative_start": 0, "negative_end": 0, "positive_lexemes": ["four", "surfers", "are"], "negative_lexemes": []}, {"tag": "equal", "positive_start": 3, "positive_end": 6, "negative_start": 0, "negative_end": 3, "positive_lexemes": ["trying", "to", "catch"], "negative_lexemes": ["trying", "to", "catch"]}, {"tag": "replace", "positive_start": 6, "positive_end": 10, "negative_start": 3, "negative_end": 7, "positive_lexemes": ["a", "wave", "as", "they"], "negative_lexemes": ["four", "waves", ",", "surfers"]}, {"tag": "equal", "positive_start": 10, "positive_end": 11, "negative_start": 7, "negative_end": 8, "positive_lexemes": ["stand"], "negative_lexemes": ["stand"]}]`
- 共同前缀：`[]`
- 正确 contrast hull：`["four", "surfers", "are", "trying", "to", "catch", "a", "wave", "as", "they"]`
- 错误 contrast hull：`["trying", "to", "catch", "four", "waves", ",", "surfers"]`
- 共同后缀：`["stand"]`
- Hull token 覆盖率（正/负/最大）：`[0.9375, 0.9333333333333333, 0.9375]`
- 共同前缀模型 token：`[]`
- 正确 hull 模型 token：IDs `[105, 1084, 3946, 105, 496, 732, 3616, 364, 3706, 550, 299, 339, 4014, 523, 2110]`；text "four surfers are trying to catch a wave as they"
- 错误 hull 模型 token：IDs `[119, 1557, 350, 364, 3706, 550, 5701, 339, 3923, 256, 47, 3946, 105, 496]`；text "trying to catch four waves , surfers"
- 第一轮/第二轮分类：`complex_edit` / `large_contrast_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；"maximum_hull_token_coverage_above_75_percent"

### 15. `swap_atribute:410`

- 负例类型/范围：`swap_atribute` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："Two persons sitting on ledge looking at a cellphone."
- 原始正描述 2："Two persons are seated on a ledge, facing a cellphone."
- 原始负描述："A person sitting on a ledge looking at two cellphones."
- 规范化正描述 1："two persons sitting on ledge looking at a cellphone"
- 规范化正描述 2："two persons are seated on a ledge , facing a cellphone"
- 规范化负描述："a person sitting on a ledge looking at two cellphones"
- 正描述 1 选择元组：`[9, 19, 3, 0.5, 0.18867924528301888]`
- 正描述 2 选择元组：`[15, 21, 3, 0.7272727272727273, 0.4444444444444444]`
- 最终比较正描述：`positive_1` / "Two persons sitting on ledge looking at a cellphone."
- 完整 lexeme 编辑块：`[{"tag": "replace", "positive_start": 0, "positive_end": 2, "negative_start": 0, "negative_end": 2, "positive_lexemes": ["two", "persons"], "negative_lexemes": ["a", "person"]}, {"tag": "equal", "positive_start": 2, "positive_end": 4, "negative_start": 2, "negative_end": 4, "positive_lexemes": ["sitting", "on"], "negative_lexemes": ["sitting", "on"]}, {"tag": "insert", "positive_start": 4, "positive_end": 4, "negative_start": 4, "negative_end": 5, "positive_lexemes": [], "negative_lexemes": ["a"]}, {"tag": "equal", "positive_start": 4, "positive_end": 7, "negative_start": 5, "negative_end": 8, "positive_lexemes": ["ledge", "looking", "at"], "negative_lexemes": ["ledge", "looking", "at"]}, {"tag": "replace", "positive_start": 7, "positive_end": 9, "negative_start": 8, "negative_end": 10, "positive_lexemes": ["a", "cellphone"], "negative_lexemes": ["two", "cellphones"]}]`
- 共同前缀：`[]`
- 正确 contrast hull：`["two", "persons", "sitting", "on", "ledge", "looking", "at", "a", "cellphone"]`
- 错误 contrast hull：`["a", "person", "sitting", "on", "a", "ledge", "looking", "at", "two", "cellphones"]`
- 共同后缀：`[]`
- Hull token 覆盖率（正/负/最大）：`[1.0, 1.0, 1.0]`
- 共同前缀模型 token：`[]`
- 正确 hull 模型 token：IDs `[119, 122, 114, 2198, 118, 5305, 2912, 619, 848, 103, 583, 3125, 1248, 299, 317, 446, 823, 107, 1634]`；text "two persons sitting on ledge looking at a cellphone"
- 错误 hull 模型 token：IDs `[100, 2198, 5305, 2912, 619, 299, 848, 103, 583, 3125, 1248, 2102, 317, 446, 823, 107, 310, 329]`；text "a person sitting on a ledge looking at two cellphones"
- 第一轮/第二轮分类：`complex_edit` / `whole_sentence_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；"at_least_one_hull_covers_all_model_tokens"

### 16. `swap_atribute:420`

- 负例类型/范围：`swap_atribute` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："Some street signs near a road with a truck."
- 原始正描述 2："A truck is near some street signs on a road."
- 原始负描述："A street sign near a road with some trucks."
- 规范化正描述 1："some street signs near a road with a truck"
- 规范化正描述 2："a truck is near some street signs on a road"
- 规范化负描述："a street sign near a road with some trucks"
- 正描述 1 选择元组：`[8, 18, 3, 0.4444444444444444, 0.23809523809523808]`
- 正描述 2 选择元组：`[15, 17, 3, 0.8, 0.6744186046511628]`
- 最终比较正描述：`positive_1` / "Some street signs near a road with a truck."
- 完整 lexeme 编辑块：`[{"tag": "replace", "positive_start": 0, "positive_end": 1, "negative_start": 0, "negative_end": 1, "positive_lexemes": ["some"], "negative_lexemes": ["a"]}, {"tag": "equal", "positive_start": 1, "positive_end": 2, "negative_start": 1, "negative_end": 2, "positive_lexemes": ["street"], "negative_lexemes": ["street"]}, {"tag": "replace", "positive_start": 2, "positive_end": 3, "negative_start": 2, "negative_end": 3, "positive_lexemes": ["signs"], "negative_lexemes": ["sign"]}, {"tag": "equal", "positive_start": 3, "positive_end": 7, "negative_start": 3, "negative_end": 7, "positive_lexemes": ["near", "a", "road", "with"], "negative_lexemes": ["near", "a", "road", "with"]}, {"tag": "replace", "positive_start": 7, "positive_end": 9, "negative_start": 7, "negative_end": 9, "positive_lexemes": ["a", "truck"], "negative_lexemes": ["some", "trucks"]}]`
- 共同前缀：`[]`
- 正确 contrast hull：`["some", "street", "signs", "near", "a", "road", "with", "a", "truck"]`
- 错误 contrast hull：`["a", "street", "sign", "near", "a", "road", "with", "some", "trucks"]`
- 共同后缀：`[]`
- Hull token 覆盖率（正/负/最大）：`[1.0, 1.0, 1.0]`
- 共同前缀模型 token：`[]`
- 正确 hull 模型 token：IDs `[118, 3219, 5941, 439, 2185, 118, 730, 370, 299, 1552, 785, 599, 299, 1144, 120, 892]`；text "some street signs near a road with a truck"
- 错误 hull 模型 token：IDs `[100, 5941, 439, 2185, 730, 370, 299, 1552, 785, 599, 2104, 1144, 120, 892, 118]`；text "a street sign near a road with some trucks"
- 第一轮/第二轮分类：`complex_edit` / `whole_sentence_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；"at_least_one_hull_covers_all_model_tokens"

### 17. `swap_atribute:425`

- 负例类型/范围：`swap_atribute` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："An airplane is parked next to a domed tower."
- 原始正描述 2："The domed tower is positioned next to the parked airplane."
- 原始负描述："A domed airplane tower is next to a parked building."
- 规范化正描述 1："an airplane is parked next to a domed tower"
- 规范化正描述 2："the domed tower is positioned next to the parked airplane"
- 规范化负描述："a domed airplane tower is next to a parked building"
- 正描述 1 选择元组：`[11, 19, 4, 0.6, 0.5098039215686274]`
- 正描述 2 选择元组：`[8, 20, 5, 0.5, 0.5263157894736842]`
- 最终比较正描述：`positive_2` / "The domed tower is positioned next to the parked airplane."
- 完整 lexeme 编辑块：`[{"tag": "replace", "positive_start": 0, "positive_end": 1, "negative_start": 0, "negative_end": 1, "positive_lexemes": ["the"], "negative_lexemes": ["a"]}, {"tag": "equal", "positive_start": 1, "positive_end": 2, "negative_start": 1, "negative_end": 2, "positive_lexemes": ["domed"], "negative_lexemes": ["domed"]}, {"tag": "insert", "positive_start": 2, "positive_end": 2, "negative_start": 2, "negative_end": 3, "positive_lexemes": [], "negative_lexemes": ["airplane"]}, {"tag": "equal", "positive_start": 2, "positive_end": 4, "negative_start": 3, "negative_end": 5, "positive_lexemes": ["tower", "is"], "negative_lexemes": ["tower", "is"]}, {"tag": "delete", "positive_start": 4, "positive_end": 5, "negative_start": 5, "negative_end": 5, "positive_lexemes": ["positioned"], "negative_lexemes": []}, {"tag": "equal", "positive_start": 5, "positive_end": 7, "negative_start": 5, "negative_end": 7, "positive_lexemes": ["next", "to"], "negative_lexemes": ["next", "to"]}, {"tag": "replace", "positive_start": 7, "positive_end": 8, "negative_start": 7, "negative_end": 8, "positive_lexemes": ["the"], "negative_lexemes": ["a"]}, {"tag": "equal", "positive_start": 8, "positive_end": 9, "negative_start": 8, "negative_end": 9, "positive_lexemes": ["parked"], "negative_lexemes": ["parked"]}, {"tag": "replace", "positive_start": 9, "positive_end": 10, "negative_start": 9, "negative_end": 10, "positive_lexemes": ["airplane"], "negative_lexemes": ["building"]}]`
- 共同前缀：`[]`
- 正确 contrast hull：`["the", "domed", "tower", "is", "positioned", "next", "to", "the", "parked", "airplane"]`
- 错误 contrast hull：`["a", "domed", "airplane", "tower", "is", "next", "to", "a", "parked", "building"]`
- 共同后缀：`[]`
- Hull token 覆盖率（正/负/最大）：`[1.0, 1.0, 1.0]`
- 共同前缀模型 token：`[]`
- 正确 hull 模型 token：IDs `[4345, 373, 444, 382, 364, 122, 311, 395, 2617, 1632, 382, 4658, 364, 309, 344, 2000, 382, 3980, 992, 4875]`；text "the domed tower is positioned next to the parked airplane"
- 错误 hull 模型 token：IDs `[100, 373, 444, 382, 3980, 992, 4875, 364, 122, 311, 395, 4658, 364, 299, 344, 2000, 382, 6331, 350]`；text "a domed airplane tower is next to a parked building"
- 第一轮/第二轮分类：`ambiguous_source` / `whole_sentence_hull`
- 自动判断："positive_2_selection_tuple_lexicographically_smaller"；"at_least_one_hull_covers_all_model_tokens"

### 18. `swap_atribute:438`

- 负例类型/范围：`swap_atribute` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A couple of children sitting in front of a blanket."
- 原始正描述 2："A blanket is in front of a couple of children."
- 原始负描述："Children in front of a couple of blankets are sitting."
- 规范化正描述 1："a couple of children sitting in front of a blanket"
- 规范化正描述 2："a blanket is in front of a couple of children"
- 规范化负描述："children in front of a couple of blankets are sitting"
- 正描述 1 选择元组：`[10, 20, 4, 0.9, 0.8113207547169812]`
- 正描述 2 选择元组：`[8, 20, 4, 0.6, 0.5094339622641509]`
- 最终比较正描述：`positive_2` / "A blanket is in front of a couple of children."
- 完整 lexeme 编辑块：`[{"tag": "delete", "positive_start": 0, "positive_end": 2, "negative_start": 0, "negative_end": 0, "positive_lexemes": ["a", "blanket"], "negative_lexemes": []}, {"tag": "replace", "positive_start": 2, "positive_end": 3, "negative_start": 0, "negative_end": 1, "positive_lexemes": ["is"], "negative_lexemes": ["children"]}, {"tag": "equal", "positive_start": 3, "positive_end": 9, "negative_start": 1, "negative_end": 7, "positive_lexemes": ["in", "front", "of", "a", "couple", "of"], "negative_lexemes": ["in", "front", "of", "a", "couple", "of"]}, {"tag": "insert", "positive_start": 9, "positive_end": 9, "negative_start": 7, "negative_end": 9, "positive_lexemes": [], "negative_lexemes": ["blankets", "are"]}, {"tag": "replace", "positive_start": 9, "positive_end": 10, "negative_start": 9, "negative_end": 10, "positive_lexemes": ["children"], "negative_lexemes": ["sitting"]}]`
- 共同前缀：`[]`
- 正确 contrast hull：`["a", "blanket", "is", "in", "front", "of", "a", "couple", "of", "children"]`
- 错误 contrast hull：`["children", "in", "front", "of", "a", "couple", "of", "blankets", "are", "sitting"]`
- 共同后缀：`[]`
- Hull token 覆盖率（正/负/最大）：`[1.0, 1.0, 1.0]`
- 共同前缀模型 token：`[]`
- 正确 hull 模型 token：IDs `[100, 2597, 3938, 439, 395, 353, 341, 117, 3856, 354, 299, 317, 326, 833, 354, 6109, 3193]`；text "a blanket is in front of a couple of children"
- 错误 hull 模型 token：IDs `[550, 2873, 3193, 353, 341, 117, 3856, 354, 299, 317, 326, 833, 354, 2597, 3938, 3391, 732, 5305, 2912]`；text "children in front of a couple of blankets are sitting"
- 第一轮/第二轮分类：`complex_edit` / `whole_sentence_hull`
- 自动判断："positive_2_selection_tuple_lexicographically_smaller"；"at_least_one_hull_covers_all_model_tokens"

### 19. `swap_atribute:587`

- 负例类型/范围：`swap_atribute` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："two people stand in behind of a motorcycle"
- 原始正描述 2："The motorcycle is in front of the two people."
- 原始负描述："A person stands in front of two motorcycles."
- 规范化正描述 1："two people stand in behind of a motorcycle"
- 规范化正描述 2："the motorcycle is in front of the two people"
- 规范化负描述："a person stands in front of two motorcycles"
- 正描述 1 选择元组：`[12, 16, 3, 0.75, 0.3953488372093023]`
- 正描述 2 选择元组：`[9, 17, 3, 0.5555555555555556, 0.5909090909090909]`
- 最终比较正描述：`positive_2` / "The motorcycle is in front of the two people."
- 完整 lexeme 编辑块：`[{"tag": "replace", "positive_start": 0, "positive_end": 3, "negative_start": 0, "negative_end": 3, "positive_lexemes": ["the", "motorcycle", "is"], "negative_lexemes": ["a", "person", "stands"]}, {"tag": "equal", "positive_start": 3, "positive_end": 6, "negative_start": 3, "negative_end": 6, "positive_lexemes": ["in", "front", "of"], "negative_lexemes": ["in", "front", "of"]}, {"tag": "delete", "positive_start": 6, "positive_end": 7, "negative_start": 6, "negative_end": 6, "positive_lexemes": ["the"], "negative_lexemes": []}, {"tag": "equal", "positive_start": 7, "positive_end": 8, "negative_start": 6, "negative_end": 7, "positive_lexemes": ["two"], "negative_lexemes": ["two"]}, {"tag": "replace", "positive_start": 8, "positive_end": 9, "negative_start": 7, "negative_end": 8, "positive_lexemes": ["people"], "negative_lexemes": ["motorcycles"]}]`
- 共同前缀：`[]`
- 正确 contrast hull：`["the", "motorcycle", "is", "in", "front", "of", "the", "two", "people"]`
- 错误 contrast hull：`["a", "person", "stands", "in", "front", "of", "two", "motorcycles"]`
- 共同后缀：`[]`
- Hull token 覆盖率（正/负/最大）：`[1.0, 1.0, 1.0]`
- 共同前缀模型 token：`[]`
- 正确 hull 模型 token：IDs `[4345, 351, 593, 336, 2863, 2945, 395, 353, 341, 117, 3856, 354, 309, 2102, 2975]`；text "the motorcycle is in front of the two people"
- 错误 hull 模型 token：IDs `[100, 2198, 2823, 118, 353, 341, 117, 3856, 354, 2102, 351, 593, 336, 2863, 1110, 329]`；text "a person stands in front of two motorcycles"
- 第一轮/第二轮分类：`complex_edit` / `whole_sentence_hull`
- 自动判断："positive_2_selection_tuple_lexicographically_smaller"；"at_least_one_hull_covers_all_model_tokens"

### 20. `swap_atribute:631`

- 负例类型/范围：`swap_atribute` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A group of people standing around a sidewalk together."
- 原始正描述 2："A group of people are gathered around a sidewalk together."
- 原始负描述："people standing alone on different sidewalks."
- 规范化正描述 1："a group of people standing around a sidewalk together"
- 规范化正描述 2："a group of people are gathered around a sidewalk together"
- 规范化负描述："people standing alone on different sidewalks"
- 正描述 1 选择元组：`[11, 15, 2, 0.7777777777777778, 0.5849056603773585]`
- 正描述 2 选择元组：`[14, 16, 3, 0.9, 0.7368421052631579]`
- 最终比较正描述：`positive_1` / "A group of people standing around a sidewalk together."
- 完整 lexeme 编辑块：`[{"tag": "delete", "positive_start": 0, "positive_end": 3, "negative_start": 0, "negative_end": 0, "positive_lexemes": ["a", "group", "of"], "negative_lexemes": []}, {"tag": "equal", "positive_start": 3, "positive_end": 5, "negative_start": 0, "negative_end": 2, "positive_lexemes": ["people", "standing"], "negative_lexemes": ["people", "standing"]}, {"tag": "replace", "positive_start": 5, "positive_end": 9, "negative_start": 2, "negative_end": 6, "positive_lexemes": ["around", "a", "sidewalk", "together"], "negative_lexemes": ["alone", "on", "different", "sidewalks"]}]`
- 共同前缀：`[]`
- 正确 contrast hull：`["a", "group", "of", "people", "standing", "around", "a", "sidewalk", "together"]`
- 错误 contrast hull：`["people", "standing", "alone", "on", "different", "sidewalks"]`
- 共同后缀：`[]`
- Hull token 覆盖率（正/负/最大）：`[1.0, 1.0, 1.0]`
- 共同前缀模型 token：`[]`
- 正确 hull 模型 token：IDs `[100, 4592, 354, 2975, 2823, 350, 3364, 299, 5046, 122, 5864, 5169]`；text "a group of people standing around a sidewalk together"
- 错误 hull 模型 token：IDs `[653, 2643, 2823, 350, 789, 1634, 619, 2301, 5046, 122, 352, 1275]`；text "people standing alone on different sidewalks"
- 第一轮/第二轮分类：`complex_edit` / `whole_sentence_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；"at_least_one_hull_covers_all_model_tokens"

### 21. `swap_atribute:7`

- 负例类型/范围：`swap_atribute` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A large elephant standing next to a bunch of trees."
- 原始正描述 2："A large elephant is positioned next to a group of trees."
- 原始负描述："A bunch of elephants standing next to a large tree."
- 规范化正描述 1："a large elephant standing next to a bunch of trees"
- 规范化正描述 2："a large elephant is positioned next to a group of trees"
- 规范化负描述："a bunch of elephants standing next to a large tree"
- 正描述 1 选择元组：`[10, 18, 4, 0.6, 0.36]`
- 正描述 2 选择元组：`[13, 19, 3, 0.6363636363636364, 0.4909090909090909]`
- 最终比较正描述：`positive_1` / "A large elephant standing next to a bunch of trees."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 1, "negative_start": 0, "negative_end": 1, "positive_lexemes": ["a"], "negative_lexemes": ["a"]}, {"tag": "insert", "positive_start": 1, "positive_end": 1, "negative_start": 1, "negative_end": 2, "positive_lexemes": [], "negative_lexemes": ["bunch"]}, {"tag": "replace", "positive_start": 1, "positive_end": 3, "negative_start": 2, "negative_end": 4, "positive_lexemes": ["large", "elephant"], "negative_lexemes": ["of", "elephants"]}, {"tag": "equal", "positive_start": 3, "positive_end": 7, "negative_start": 4, "negative_end": 8, "positive_lexemes": ["standing", "next", "to", "a"], "negative_lexemes": ["standing", "next", "to", "a"]}, {"tag": "delete", "positive_start": 7, "positive_end": 8, "negative_start": 8, "negative_end": 8, "positive_lexemes": ["bunch"], "negative_lexemes": []}, {"tag": "replace", "positive_start": 8, "positive_end": 10, "negative_start": 8, "negative_end": 10, "positive_lexemes": ["of", "trees"], "negative_lexemes": ["large", "tree"]}]`
- 共同前缀：`["a"]`
- 正确 contrast hull：`["large", "elephant", "standing", "next", "to", "a", "bunch", "of", "trees"]`
- 错误 contrast hull：`["bunch", "of", "elephants", "standing", "next", "to", "a", "large", "tree"]`
- 共同后缀：`[]`
- Hull token 覆盖率（正/负/最大）：`[0.9375, 0.9375, 0.9375]`
- 共同前缀模型 token：`[100]`
- 正确 hull 模型 token：IDs `[2994, 1905, 1601, 811, 2823, 350, 4658, 364, 299, 363, 651, 550, 354, 4191, 329]`；text " large elephant standing next to a bunch of trees"
- 错误 hull 模型 token：IDs `[363, 651, 550, 354, 1905, 1601, 5483, 2823, 350, 4658, 364, 299, 2994, 297, 1382]`；text " bunch of elephants standing next to a large tree"
- 第一轮/第二轮分类：`complex_edit` / `large_contrast_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；"maximum_hull_token_coverage_above_75_percent"

### 22. `swap_atribute:75`

- 负例类型/范围：`swap_atribute` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A white frosted cake sitting in front of some white flowers."
- 原始正描述 2："The white flowers are positioned behind the white frosted cake."
- 原始负描述："Some white frosted flowers sitting in front of a white cake."
- 规范化正描述 1："a white frosted cake sitting in front of some white flowers"
- 规范化正描述 2："the white flowers are positioned behind the white frosted cake"
- 规范化负描述："some white frosted flowers sitting in front of a white cake"
- 正描述 1 选择元组：`[8, 22, 4, 0.36363636363636365, 0.3389830508474576]`
- 正描述 2 选择元组：`[15, 19, 3, 0.7272727272727273, 0.6129032258064516]`
- 最终比较正描述：`positive_1` / "A white frosted cake sitting in front of some white flowers."
- 完整 lexeme 编辑块：`[{"tag": "replace", "positive_start": 0, "positive_end": 1, "negative_start": 0, "negative_end": 1, "positive_lexemes": ["a"], "negative_lexemes": ["some"]}, {"tag": "equal", "positive_start": 1, "positive_end": 3, "negative_start": 1, "negative_end": 3, "positive_lexemes": ["white", "frosted"], "negative_lexemes": ["white", "frosted"]}, {"tag": "replace", "positive_start": 3, "positive_end": 4, "negative_start": 3, "negative_end": 4, "positive_lexemes": ["cake"], "negative_lexemes": ["flowers"]}, {"tag": "equal", "positive_start": 4, "positive_end": 8, "negative_start": 4, "negative_end": 8, "positive_lexemes": ["sitting", "in", "front", "of"], "negative_lexemes": ["sitting", "in", "front", "of"]}, {"tag": "replace", "positive_start": 8, "positive_end": 9, "negative_start": 8, "negative_end": 9, "positive_lexemes": ["some"], "negative_lexemes": ["a"]}, {"tag": "equal", "positive_start": 9, "positive_end": 10, "negative_start": 9, "negative_end": 10, "positive_lexemes": ["white"], "negative_lexemes": ["white"]}, {"tag": "replace", "positive_start": 10, "positive_end": 11, "negative_start": 10, "negative_end": 11, "positive_lexemes": ["flowers"], "negative_lexemes": ["cake"]}]`
- 共同前缀：`[]`
- 正确 contrast hull：`["a", "white", "frosted", "cake", "sitting", "in", "front", "of", "some", "white", "flowers"]`
- 错误 contrast hull：`["some", "white", "frosted", "flowers", "sitting", "in", "front", "of", "a", "white", "cake"]`
- 共同后缀：`[]`
- Hull token 覆盖率（正/负/最大）：`[1.0, 1.0, 1.0]`
- 共同前缀模型 token：`[]`
- 正确 hull 模型 token：IDs `[100, 654, 1078, 341, 393, 432, 382, 317, 2434, 5305, 2912, 353, 341, 117, 3856, 354, 2104, 654, 1078, 5652, 496]`；text "a white frosted cake sitting in front of some white flowers"
- 错误 hull 模型 token：IDs `[118, 3219, 654, 1078, 341, 393, 432, 382, 5652, 496, 5305, 2912, 353, 341, 117, 3856, 354, 299, 654, 1078, 317, 2434]`；text "some white frosted flowers sitting in front of a white cake"
- 第一轮/第二轮分类：`complex_edit` / `whole_sentence_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；"at_least_one_hull_covers_all_model_tokens"

### 23. `swap_object:194`

- 负例类型/范围：`swap_object` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A person is holding a baby with another young child beside the person."
- 原始正描述 2："A young child is standing beside a person who is holding a baby."
- 原始负描述："A young child is holding a baby with another person beside the child."
- 规范化正描述 1："a person is holding a baby with another young child beside the person"
- 规范化正描述 2："a young child is standing beside a person who is holding a baby"
- 规范化负描述："a young child is holding a baby with another person beside the child"
- 正描述 1 选择元组：`[8, 24, 5, 0.38461538461538464, 0.4057971014492754]`
- 正描述 2 选择元组：`[18, 18, 1, 0.6923076923076923, 0.5588235294117647]`
- 最终比较正描述：`positive_1` / "A person is holding a baby with another young child beside the person."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 1, "negative_start": 0, "negative_end": 1, "positive_lexemes": ["a"], "negative_lexemes": ["a"]}, {"tag": "insert", "positive_start": 1, "positive_end": 1, "negative_start": 1, "negative_end": 2, "positive_lexemes": [], "negative_lexemes": ["young"]}, {"tag": "replace", "positive_start": 1, "positive_end": 2, "negative_start": 2, "negative_end": 3, "positive_lexemes": ["person"], "negative_lexemes": ["child"]}, {"tag": "equal", "positive_start": 2, "positive_end": 8, "negative_start": 3, "negative_end": 9, "positive_lexemes": ["is", "holding", "a", "baby", "with", "another"], "negative_lexemes": ["is", "holding", "a", "baby", "with", "another"]}, {"tag": "delete", "positive_start": 8, "positive_end": 9, "negative_start": 9, "negative_end": 9, "positive_lexemes": ["young"], "negative_lexemes": []}, {"tag": "replace", "positive_start": 9, "positive_end": 10, "negative_start": 9, "negative_end": 10, "positive_lexemes": ["child"], "negative_lexemes": ["person"]}, {"tag": "equal", "positive_start": 10, "positive_end": 12, "negative_start": 10, "negative_end": 12, "positive_lexemes": ["beside", "the"], "negative_lexemes": ["beside", "the"]}, {"tag": "replace", "positive_start": 12, "positive_end": 13, "negative_start": 12, "negative_end": 13, "positive_lexemes": ["person"], "negative_lexemes": ["child"]}]`
- 共同前缀：`["a"]`
- 正确 contrast hull：`["person", "is", "holding", "a", "baby", "with", "another", "young", "child", "beside", "the", "person"]`
- 错误 contrast hull：`["young", "child", "is", "holding", "a", "baby", "with", "another", "person", "beside", "the", "child"]`
- 共同后缀：`[]`
- Hull token 覆盖率（正/负/最大）：`[0.95, 0.95, 0.95]`
- 共同前缀模型 token：`[100]`
- 正确 hull 模型 token：IDs `[2198, 395, 429, 2569, 350, 299, 363, 572, 124, 599, 5467, 401, 1685, 6109, 363, 329, 688, 309, 2198]`；text " person is holding a baby with another young child beside the person"
- 错误 hull 模型 token：IDs `[401, 1685, 6109, 395, 429, 2569, 350, 299, 363, 572, 124, 599, 5467, 2198, 363, 329, 688, 309, 6109]`；text " young child is holding a baby with another person beside the child"
- 第一轮/第二轮分类：`complex_edit` / `large_contrast_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；"maximum_hull_token_coverage_above_75_percent"

### 24. `swap_object:195`

- 负例类型/范围：`swap_object` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："Two brown horses pull a plow, steered by a person behind."
- 原始正描述 2："The person steers two brown horses from behind that pull a plow."
- 原始负描述："A person pulls a plow, steered by two brown horses in front."
- 规范化正描述 1："two brown horses pull a plow , steered by a person behind"
- 规范化正描述 2："the person steers two brown horses from behind that pull a plow"
- 规范化负描述："a person pulls a plow , steered by two brown horses in front"
- 正描述 1 选择元组：`[15, 25, 4, 0.6923076923076923, 0.55]`
- 正描述 2 选择元组：`[23, 25, 3, 0.9230769230769231, 0.7142857142857143]`
- 最终比较正描述：`positive_1` / "Two brown horses pull a plow, steered by a person behind."
- 完整 lexeme 编辑块：`[{"tag": "delete", "positive_start": 0, "positive_end": 1, "negative_start": 0, "negative_end": 0, "positive_lexemes": ["two"], "negative_lexemes": []}, {"tag": "replace", "positive_start": 1, "positive_end": 4, "negative_start": 0, "negative_end": 3, "positive_lexemes": ["brown", "horses", "pull"], "negative_lexemes": ["a", "person", "pulls"]}, {"tag": "equal", "positive_start": 4, "positive_end": 9, "negative_start": 3, "negative_end": 8, "positive_lexemes": ["a", "plow", ",", "steered", "by"], "negative_lexemes": ["a", "plow", ",", "steered", "by"]}, {"tag": "insert", "positive_start": 9, "positive_end": 9, "negative_start": 8, "negative_end": 10, "positive_lexemes": [], "negative_lexemes": ["two", "brown"]}, {"tag": "replace", "positive_start": 9, "positive_end": 12, "negative_start": 10, "negative_end": 13, "positive_lexemes": ["a", "person", "behind"], "negative_lexemes": ["horses", "in", "front"]}]`
- 共同前缀：`[]`
- 正确 contrast hull：`["two", "brown", "horses", "pull", "a", "plow", ",", "steered", "by", "a", "person", "behind"]`
- 错误 contrast hull：`["a", "person", "pulls", "a", "plow", ",", "steered", "by", "two", "brown", "horses", "in", "front"]`
- 共同后缀：`[]`
- Hull token 覆盖率（正/负/最大）：`[1.0, 1.0, 1.0]`
- 共同前缀模型 token：`[]`
- 正确 hull 模型 token：IDs `[119, 122, 114, 363, 2079, 113, 429, 1945, 329, 344, 3800, 299, 344, 1030, 256, 47, 580, 104, 964, 103, 769, 299, 2198, 5237, 916]`；text "two brown horses pull a plow , steered by a person behind"
- 错误 hull 模型 token：IDs `[100, 2198, 344, 3800, 118, 299, 344, 1030, 256, 47, 580, 104, 964, 103, 769, 2102, 363, 2079, 113, 429, 1945, 329, 353, 341, 117, 3856]`；text "a person pulls a plow , steered by two brown horses in front"
- 第一轮/第二轮分类：`ambiguous_source` / `whole_sentence_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；"at_least_one_hull_covers_all_model_tokens"

### 25. `swap_object:213`

- 负例类型/范围：`swap_object` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A person preparing food on a large old oven."
- 原始正描述 2："A person is preparing food on a large old oven."
- 原始负描述："A large old oven preparing food with a person standing next to it."
- 规范化正描述 1："a person preparing food on a large old oven"
- 规范化正描述 2："a person is preparing food on a large old oven"
- 规范化负描述："a large old oven preparing food with a person standing next to it"
- 正描述 1 选择元组：`[14, 20, 5, 0.6923076923076923, 0.5538461538461539]`
- 正描述 2 选择元组：`[15, 21, 5, 0.6923076923076923, 0.5538461538461539]`
- 最终比较正描述：`positive_1` / "A person preparing food on a large old oven."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 1, "negative_start": 0, "negative_end": 1, "positive_lexemes": ["a"], "negative_lexemes": ["a"]}, {"tag": "insert", "positive_start": 1, "positive_end": 1, "negative_start": 1, "negative_end": 3, "positive_lexemes": [], "negative_lexemes": ["large", "old"]}, {"tag": "replace", "positive_start": 1, "positive_end": 2, "negative_start": 3, "negative_end": 4, "positive_lexemes": ["person"], "negative_lexemes": ["oven"]}, {"tag": "equal", "positive_start": 2, "positive_end": 4, "negative_start": 4, "negative_end": 6, "positive_lexemes": ["preparing", "food"], "negative_lexemes": ["preparing", "food"]}, {"tag": "replace", "positive_start": 4, "positive_end": 5, "negative_start": 6, "negative_end": 7, "positive_lexemes": ["on"], "negative_lexemes": ["with"]}, {"tag": "equal", "positive_start": 5, "positive_end": 6, "negative_start": 7, "negative_end": 8, "positive_lexemes": ["a"], "negative_lexemes": ["a"]}, {"tag": "insert", "positive_start": 6, "positive_end": 6, "negative_start": 8, "negative_end": 10, "positive_lexemes": [], "negative_lexemes": ["person", "standing"]}, {"tag": "replace", "positive_start": 6, "positive_end": 9, "negative_start": 10, "negative_end": 13, "positive_lexemes": ["large", "old", "oven"], "negative_lexemes": ["next", "to", "it"]}]`
- 共同前缀：`["a"]`
- 正确 contrast hull：`["person", "preparing", "food", "on", "a", "large", "old", "oven"]`
- 错误 contrast hull：`["large", "old", "oven", "preparing", "food", "with", "a", "person", "standing", "next", "to", "it"]`
- 共同后缀：`[]`
- Hull token 覆盖率（正/负/最大）：`[0.9230769230769231, 0.9444444444444444, 0.9444444444444444]`
- 共同前缀模型 token：`[100]`
- 正确 hull 模型 token：IDs `[2198, 2165, 4671, 350, 341, 2166, 619, 299, 2994, 4797, 319, 3273]`；text " person preparing food on a large old oven"
- 错误 hull 模型 token：IDs `[2994, 4797, 319, 3273, 2165, 4671, 350, 341, 2166, 599, 299, 2198, 2823, 350, 4658, 364, 563]`；text " large old oven preparing food with a person standing next to it"
- 第一轮/第二轮分类：`ambiguous_source` / `large_contrast_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；"maximum_hull_token_coverage_above_75_percent"

### 26. `swap_object:24`

- 负例类型/范围：`swap_object` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："Small child getting their hair dried with a person standing behind them. "
- 原始正描述 2："A person stands behind a small child as she gets their hair dried."
- 原始负描述："A person getting his hair dried with a small child standing behind him."
- 规范化正描述 1："small child getting their hair dried with a person standing behind them"
- 规范化正描述 2："a person stands behind a small child as she gets their hair dried"
- 规范化负描述："a person getting his hair dried with a small child standing behind him"
- 正描述 1 选择元组：`[11, 25, 5, 0.46153846153846156, 0.36619718309859156]`
- 正描述 2 选择元组：`[22, 22, 1, 0.8461538461538461, 0.6142857142857143]`
- 最终比较正描述：`positive_1` / "Small child getting their hair dried with a person standing behind them. "
- 完整 lexeme 编辑块：`[{"tag": "replace", "positive_start": 0, "positive_end": 2, "negative_start": 0, "negative_end": 2, "positive_lexemes": ["small", "child"], "negative_lexemes": ["a", "person"]}, {"tag": "equal", "positive_start": 2, "positive_end": 3, "negative_start": 2, "negative_end": 3, "positive_lexemes": ["getting"], "negative_lexemes": ["getting"]}, {"tag": "replace", "positive_start": 3, "positive_end": 4, "negative_start": 3, "negative_end": 4, "positive_lexemes": ["their"], "negative_lexemes": ["his"]}, {"tag": "equal", "positive_start": 4, "positive_end": 8, "negative_start": 4, "negative_end": 8, "positive_lexemes": ["hair", "dried", "with", "a"], "negative_lexemes": ["hair", "dried", "with", "a"]}, {"tag": "insert", "positive_start": 8, "positive_end": 8, "negative_start": 8, "negative_end": 9, "positive_lexemes": [], "negative_lexemes": ["small"]}, {"tag": "replace", "positive_start": 8, "positive_end": 9, "negative_start": 9, "negative_end": 10, "positive_lexemes": ["person"], "negative_lexemes": ["child"]}, {"tag": "equal", "positive_start": 9, "positive_end": 11, "negative_start": 10, "negative_end": 12, "positive_lexemes": ["standing", "behind"], "negative_lexemes": ["standing", "behind"]}, {"tag": "replace", "positive_start": 11, "positive_end": 12, "negative_start": 12, "negative_end": 13, "positive_lexemes": ["them"], "negative_lexemes": ["him"]}]`
- 共同前缀：`[]`
- 正确 contrast hull：`["small", "child", "getting", "their", "hair", "dried", "with", "a", "person", "standing", "behind", "them"]`
- 错误 contrast hull：`["a", "person", "getting", "his", "hair", "dried", "with", "a", "small", "child", "standing", "behind", "him"]`
- 共同后缀：`[]`
- Hull token 覆盖率（正/负/最大）：`[1.0, 1.0, 1.0]`
- 共同前缀模型 token：`[]`
- 正确 hull 模型 token：IDs `[118, 112, 1266, 6109, 2350, 2912, 1635, 736, 639, 373, 809, 382, 599, 299, 2198, 2823, 350, 5237, 916, 2105]`；text "small child getting their hair dried with a person standing behind them"
- 错误 hull 模型 token：IDs `[100, 2198, 2350, 2912, 2049, 736, 639, 373, 809, 382, 599, 299, 3436, 6109, 2823, 350, 5237, 916, 429, 467]`；text "a person getting his hair dried with a small child standing behind him"
- 第一轮/第二轮分类：`complex_edit` / `whole_sentence_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；"at_least_one_hull_covers_all_model_tokens"

### 27. `swap_object:59`

- 负例类型/范围：`swap_object` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A tall tower with a clock stands in front of a skyscraper."
- 原始正描述 2："A tall tower that contains a clock is positioned in front of a skyscraper."
- 原始负描述："A skyscraper with a clock stands in front of a tall tower."
- 规范化正描述 1："a tall tower with a clock stands in front of a skyscraper"
- 规范化正描述 2："a tall tower that contains a clock is positioned in front of a skyscraper"
- 规范化负描述："a skyscraper with a clock stands in front of a tall tower"
- 正描述 1 选择元组：`[6, 22, 4, 0.3333333333333333, 0.2807017543859649]`
- 正描述 2 选择元组：`[12, 24, 6, 0.5714285714285714, 0.5205479452054794]`
- 最终比较正描述：`positive_1` / "A tall tower with a clock stands in front of a skyscraper."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 1, "negative_start": 0, "negative_end": 1, "positive_lexemes": ["a"], "negative_lexemes": ["a"]}, {"tag": "delete", "positive_start": 1, "positive_end": 2, "negative_start": 1, "negative_end": 1, "positive_lexemes": ["tall"], "negative_lexemes": []}, {"tag": "replace", "positive_start": 2, "positive_end": 3, "negative_start": 1, "negative_end": 2, "positive_lexemes": ["tower"], "negative_lexemes": ["skyscraper"]}, {"tag": "equal", "positive_start": 3, "positive_end": 11, "negative_start": 2, "negative_end": 10, "positive_lexemes": ["with", "a", "clock", "stands", "in", "front", "of", "a"], "negative_lexemes": ["with", "a", "clock", "stands", "in", "front", "of", "a"]}, {"tag": "insert", "positive_start": 11, "positive_end": 11, "negative_start": 10, "negative_end": 11, "positive_lexemes": [], "negative_lexemes": ["tall"]}, {"tag": "replace", "positive_start": 11, "positive_end": 12, "negative_start": 11, "negative_end": 12, "positive_lexemes": ["skyscraper"], "negative_lexemes": ["tower"]}]`
- 共同前缀：`["a"]`
- 正确 contrast hull：`["tall", "tower", "with", "a", "clock", "stands", "in", "front", "of", "a", "skyscraper"]`
- 错误 contrast hull：`["skyscraper", "with", "a", "clock", "stands", "in", "front", "of", "a", "tall", "tower"]`
- 共同后缀：`[]`
- Hull token 覆盖率（正/负/最大）：`[0.9565217391304348, 0.9565217391304348, 0.9565217391304348]`
- 共同前缀模型 token：`[100]`
- 正确 hull 模型 token：IDs `[297, 1266, 364, 122, 311, 599, 299, 4414, 892, 2823, 118, 353, 341, 117, 3856, 354, 299, 2549, 2211, 102, 559, 1067]`；text " tall tower with a clock stands in front of a skyscraper"
- 错误 hull 模型 token：IDs `[2549, 2211, 102, 559, 1067, 599, 299, 4414, 892, 2823, 118, 353, 341, 117, 3856, 354, 299, 297, 1266, 364, 122, 311]`；text " skyscraper with a clock stands in front of a tall tower"
- 第一轮/第二轮分类：`complex_edit` / `large_contrast_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；"maximum_hull_token_coverage_above_75_percent"

### 28. `swap_object:61`

- 负例类型/范围：`swap_object` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："Military people are holding awards while standing next to a person in a suit."
- 原始正描述 2："The person wearing suit is adjacent to military people who are standing and holding awards."
- 原始负描述："A person in a suit is holding awards while standing next to military people."
- 规范化正描述 1："military people are holding awards while standing next to a person in a suit"
- 规范化正描述 2："the person wearing suit is adjacent to military people who are standing and holding awards"
- 规范化负描述："a person in a suit is holding awards while standing next to military people"
- 正描述 1 选择元组：`[16, 28, 4, 0.7857142857142857, 0.4868421052631579]`
- 正描述 2 选择元组：`[23, 29, 5, 0.8666666666666667, 0.6111111111111112]`
- 最终比较正描述：`positive_1` / "Military people are holding awards while standing next to a person in a suit."
- 完整 lexeme 编辑块：`[{"tag": "insert", "positive_start": 0, "positive_end": 0, "negative_start": 0, "negative_end": 3, "positive_lexemes": [], "negative_lexemes": ["a", "person", "in"]}, {"tag": "replace", "positive_start": 0, "positive_end": 3, "negative_start": 3, "negative_end": 6, "positive_lexemes": ["military", "people", "are"], "negative_lexemes": ["a", "suit", "is"]}, {"tag": "equal", "positive_start": 3, "positive_end": 9, "negative_start": 6, "negative_end": 12, "positive_lexemes": ["holding", "awards", "while", "standing", "next", "to"], "negative_lexemes": ["holding", "awards", "while", "standing", "next", "to"]}, {"tag": "delete", "positive_start": 9, "positive_end": 12, "negative_start": 12, "negative_end": 12, "positive_lexemes": ["a", "person", "in"], "negative_lexemes": []}, {"tag": "replace", "positive_start": 12, "positive_end": 14, "negative_start": 12, "negative_end": 14, "positive_lexemes": ["a", "suit"], "negative_lexemes": ["military", "people"]}]`
- 共同前缀：`[]`
- 正确 contrast hull：`["military", "people", "are", "holding", "awards", "while", "standing", "next", "to", "a", "person", "in", "a", "suit"]`
- 错误 contrast hull：`["a", "person", "in", "a", "suit", "is", "holding", "awards", "while", "standing", "next", "to", "military", "people"]`
- 共同后缀：`[]`
- Hull token 覆盖率（正/负/最大）：`[1.0, 1.0, 1.0]`
- 共同前缀模型 token：`[]`
- 正确 hull 模型 token：IDs `[112, 485, 338, 1156, 2975, 732, 429, 2569, 350, 299, 3588, 118, 3052, 2823, 350, 4658, 364, 299, 2198, 353, 299, 855, 338]`；text "military people are holding awards while standing next to a person in a suit"
- 错误 hull 模型 token：IDs `[100, 2198, 353, 299, 855, 338, 395, 429, 2569, 350, 299, 3588, 118, 3052, 2823, 350, 4658, 364, 3839, 338, 1156, 2975]`；text "a person in a suit is holding awards while standing next to military people"
- 第一轮/第二轮分类：`complex_edit` / `whole_sentence_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；"at_least_one_hull_covers_all_model_tokens"

### 29. `swap_object:82`

- 负例类型/范围：`swap_object` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A video screen with faces of a couple of persons on it."
- 原始正描述 2："A video screen displaying the faces of a couple of individuals."
- 原始负描述："Faces of a couple of persons with a video screen behind them."
- 规范化正描述 1："a video screen with faces of a couple of persons on it"
- 规范化正描述 2："a video screen displaying the faces of a couple of individuals"
- 规范化负描述："faces of a couple of persons with a video screen behind them"
- 正描述 1 选择元组：`[12, 24, 3, 0.8333333333333334, 0.7666666666666667]`
- 正描述 2 选择元组：`[21, 23, 3, 0.9166666666666666, 0.8064516129032258]`
- 最终比较正描述：`positive_1` / "A video screen with faces of a couple of persons on it."
- 完整 lexeme 编辑块：`[{"tag": "delete", "positive_start": 0, "positive_end": 4, "negative_start": 0, "negative_end": 0, "positive_lexemes": ["a", "video", "screen", "with"], "negative_lexemes": []}, {"tag": "equal", "positive_start": 4, "positive_end": 10, "negative_start": 0, "negative_end": 6, "positive_lexemes": ["faces", "of", "a", "couple", "of", "persons"], "negative_lexemes": ["faces", "of", "a", "couple", "of", "persons"]}, {"tag": "insert", "positive_start": 10, "positive_end": 10, "negative_start": 6, "negative_end": 10, "positive_lexemes": [], "negative_lexemes": ["with", "a", "video", "screen"]}, {"tag": "replace", "positive_start": 10, "positive_end": 12, "negative_start": 10, "negative_end": 12, "positive_lexemes": ["on", "it"], "negative_lexemes": ["behind", "them"]}]`
- 共同前缀：`[]`
- 正确 contrast hull：`["a", "video", "screen", "with", "faces", "of", "a", "couple", "of", "persons", "on", "it"]`
- 错误 contrast hull：`["faces", "of", "a", "couple", "of", "persons", "with", "a", "video", "screen", "behind", "them"]`
- 共同后缀：`[]`
- Hull token 覆盖率（正/负/最大）：`[1.0, 1.0, 1.0]`
- 共同前缀模型 token：`[]`
- 正确 hull 模型 token：IDs `[100, 603, 688, 114, 1416, 306, 327, 599, 341, 4985, 354, 299, 317, 326, 833, 354, 2198, 118, 619, 563]`；text "a video screen with faces of a couple of persons on it"
- 错误 hull 模型 token：IDs `[105, 4985, 354, 299, 317, 326, 833, 354, 2198, 118, 599, 299, 603, 688, 114, 1416, 306, 327, 5237, 916, 2105]`；text "faces of a couple of persons with a video screen behind them"
- 第一轮/第二轮分类：`complex_edit` / `whole_sentence_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；"at_least_one_hull_covers_all_model_tokens"

### 30. `swap_object:99`

- 负例类型/范围：`swap_object` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："Four people play a game of mixed doubles tennis while another person looks on."
- 原始正描述 2："while a person observes, four other individuals engage in a game of mixed doubles tennis."
- 原始负描述："A person plays a game of mixed doubles tennis while another four people look on."
- 规范化正描述 1："four people play a game of mixed doubles tennis while another person looks on"
- 规范化正描述 2："while a person observes , four other individuals engage in a game of mixed doubles tennis"
- 规范化负描述："a person plays a game of mixed doubles tennis while another four people look on"
- 正描述 1 选择元组：`[11, 27, 3, 0.4, 0.24050632911392406]`
- 正描述 2 选择元组：`[27, 31, 2, 0.875, 0.7191011235955056]`
- 最终比较正描述：`positive_1` / "Four people play a game of mixed doubles tennis while another person looks on."
- 完整 lexeme 编辑块：`[{"tag": "replace", "positive_start": 0, "positive_end": 3, "negative_start": 0, "negative_end": 3, "positive_lexemes": ["four", "people", "play"], "negative_lexemes": ["a", "person", "plays"]}, {"tag": "equal", "positive_start": 3, "positive_end": 11, "negative_start": 3, "negative_end": 11, "positive_lexemes": ["a", "game", "of", "mixed", "doubles", "tennis", "while", "another"], "negative_lexemes": ["a", "game", "of", "mixed", "doubles", "tennis", "while", "another"]}, {"tag": "insert", "positive_start": 11, "positive_end": 11, "negative_start": 11, "negative_end": 12, "positive_lexemes": [], "negative_lexemes": ["four"]}, {"tag": "replace", "positive_start": 11, "positive_end": 13, "negative_start": 12, "negative_end": 14, "positive_lexemes": ["person", "looks"], "negative_lexemes": ["people", "look"]}, {"tag": "equal", "positive_start": 13, "positive_end": 14, "negative_start": 14, "negative_end": 15, "positive_lexemes": ["on"], "negative_lexemes": ["on"]}]`
- 共同前缀：`[]`
- 正确 contrast hull：`["four", "people", "play", "a", "game", "of", "mixed", "doubles", "tennis", "while", "another", "person", "looks"]`
- 错误 contrast hull：`["a", "person", "plays", "a", "game", "of", "mixed", "doubles", "tennis", "while", "another", "four", "people", "look"]`
- 共同后缀：`["on"]`
- Hull token 覆盖率（正/负/最大）：`[0.9545454545454546, 0.9545454545454546, 0.9545454545454546]`
- 共同前缀模型 token：`[]`
- 正确 hull 模型 token：IDs `[105, 1084, 2975, 2865, 299, 4428, 354, 5418, 382, 373, 326, 101, 1907, 297, 6201, 324, 3052, 5467, 2198, 1853, 1275]`；text "four people play a game of mixed doubles tennis while another person looks"
- 错误 hull 模型 token：IDs `[100, 2198, 1219, 2012, 299, 4428, 354, 5418, 382, 373, 326, 101, 1907, 297, 6201, 324, 3052, 5467, 5701, 2975, 4741]`；text "a person plays a game of mixed doubles tennis while another four people look"
- 第一轮/第二轮分类：`complex_edit` / `large_contrast_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；"maximum_hull_token_coverage_above_75_percent"

## 整句 hull

候选 `106` 条，本节抽取 `30` 条。

### 1. `replace_attribute:568`

- 负例类型/范围：`replace_attribute` / `{"canonical": true, "pilot": true, "formal": false, "certifying_formal": false}`
- 原始正描述 1："Several desserts sitting behind a glass window with display cards in front of them."
- 原始正描述 2："Several desserts with display cards in front of them are positioned behind a glass window."
- 原始负描述："A singular dessert sitting behind a glass window with a display card in front of it."
- 规范化正描述 1："several desserts sitting behind a glass window with display cards in front of them"
- 规范化正描述 2："several desserts with display cards in front of them are positioned behind a glass window"
- 规范化负描述："a singular dessert sitting behind a glass window with a display card in front of it"
- 正描述 1 选择元组：`[10, 30, 5, 0.375, 0.1927710843373494]`
- 正描述 2 选择元组：`[31, 31, 2, 1.0, 0.7303370786516854]`
- 最终比较正描述：`positive_1` / "Several desserts sitting behind a glass window with display cards in front of them."
- 完整 lexeme 编辑块：`[{"tag": "insert", "positive_start": 0, "positive_end": 0, "negative_start": 0, "negative_end": 1, "positive_lexemes": [], "negative_lexemes": ["a"]}, {"tag": "replace", "positive_start": 0, "positive_end": 2, "negative_start": 1, "negative_end": 3, "positive_lexemes": ["several", "desserts"], "negative_lexemes": ["singular", "dessert"]}, {"tag": "equal", "positive_start": 2, "positive_end": 8, "negative_start": 3, "negative_end": 9, "positive_lexemes": ["sitting", "behind", "a", "glass", "window", "with"], "negative_lexemes": ["sitting", "behind", "a", "glass", "window", "with"]}, {"tag": "insert", "positive_start": 8, "positive_end": 8, "negative_start": 9, "negative_end": 10, "positive_lexemes": [], "negative_lexemes": ["a"]}, {"tag": "equal", "positive_start": 8, "positive_end": 9, "negative_start": 10, "negative_end": 11, "positive_lexemes": ["display"], "negative_lexemes": ["display"]}, {"tag": "replace", "positive_start": 9, "positive_end": 10, "negative_start": 11, "negative_end": 12, "positive_lexemes": ["cards"], "negative_lexemes": ["card"]}, {"tag": "equal", "positive_start": 10, "positive_end": 13, "negative_start": 12, "negative_end": 15, "positive_lexemes": ["in", "front", "of"], "negative_lexemes": ["in", "front", "of"]}, {"tag": "replace", "positive_start": 13, "positive_end": 14, "negative_start": 15, "negative_end": 16, "positive_lexemes": ["them"], "negative_lexemes": ["it"]}]`
- 共同前缀：`[]`
- 正确 contrast hull：`["several", "desserts", "sitting", "behind", "a", "glass", "window", "with", "display", "cards", "in", "front", "of", "them"]`
- 错误 contrast hull：`["a", "singular", "dessert", "sitting", "behind", "a", "glass", "window", "with", "a", "display", "card", "in", "front", "of", "it"]`
- 共同后缀：`[]`
- Hull token 覆盖率（正/负/最大）：`[1.0, 1.0, 1.0]`
- 共同前缀模型 token：`[]`
- 正确 hull 模型 token：IDs `[573, 652, 352, 373, 781, 311, 2726, 5305, 2912, 5237, 916, 299, 492, 111, 1388, 5472, 451, 599, 1981, 4838, 317, 1433, 118, 353, 341, 117, 3856, 354, 2105]`；text "several desserts sitting behind a glass window with display cards in front of them"
- 错误 hull 模型 token：IDs `[100, 3634, 2055, 373, 781, 3066, 5305, 2912, 5237, 916, 299, 492, 111, 1388, 5472, 451, 599, 299, 1981, 4838, 317, 1433, 353, 341, 117, 3856, 354, 563]`；text "a singular dessert sitting behind a glass window with a display card in front of it"
- 第一轮/第二轮分类：`complex_edit` / `whole_sentence_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；"at_least_one_hull_covers_all_model_tokens"

### 2. `replace_object:1223`

- 负例类型/范围：`replace_object` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："An hand pets a cat in a suitcase.  "
- 原始正描述 2："A cat is being petted by a hand inside a suitcase."
- 原始负描述："A hand pets a cat in a backpack."
- 规范化正描述 1："an hand pets a cat in a suitcase"
- 规范化正描述 2："a cat is being petted by a hand inside a suitcase"
- 规范化负描述："a hand pets a cat in a backpack"
- 正描述 1 选择元组：`[4, 16, 2, 0.25, 0.25]`
- 正描述 2 选择元组：`[13, 17, 4, 0.7272727272727273, 0.6122448979591837]`
- 最终比较正描述：`positive_1` / "An hand pets a cat in a suitcase.  "
- 完整 lexeme 编辑块：`[{"tag": "replace", "positive_start": 0, "positive_end": 1, "negative_start": 0, "negative_end": 1, "positive_lexemes": ["an"], "negative_lexemes": ["a"]}, {"tag": "equal", "positive_start": 1, "positive_end": 7, "negative_start": 1, "negative_end": 7, "positive_lexemes": ["hand", "pets", "a", "cat", "in", "a"], "negative_lexemes": ["hand", "pets", "a", "cat", "in", "a"]}, {"tag": "replace", "positive_start": 7, "positive_end": 8, "negative_start": 7, "negative_end": 8, "positive_lexemes": ["suitcase"], "negative_lexemes": ["backpack"]}]`
- 共同前缀：`[]`
- 正确 contrast hull：`["an", "hand", "pets", "a", "cat", "in", "a", "suitcase"]`
- 错误 contrast hull：`["a", "hand", "pets", "a", "cat", "in", "a", "backpack"]`
- 共同后缀：`[]`
- Hull token 覆盖率（正/负/最大）：`[1.0, 1.0, 1.0]`
- 共同前缀模型 token：`[]`
- 正确 hull 模型 token：IDs `[325, 3319, 344, 3391, 299, 3706, 353, 299, 855, 338, 4220]`；text "an hand pets a cat in a suitcase"
- 错误 hull 模型 token：IDs `[100, 3319, 344, 3391, 299, 3706, 353, 299, 3901, 115, 1637]`；text "a hand pets a cat in a backpack"
- 第一轮/第二轮分类：`complex_edit` / `whole_sentence_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；"at_least_one_hull_covers_all_model_tokens"

### 3. `replace_object:1572`

- 负例类型/范围：`replace_object` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："Elephants with large tusks, standing around behind a fence."
- 原始正描述 2："Large tusked Elephants are positioned behind a fence, standing around."
- 原始负描述："Tourists with cameras, standing around behind a fence, watching elephants."
- 规范化正描述 1："elephants with large tusks , standing around behind a fence"
- 规范化正描述 2："large tusked elephants are positioned behind a fence , standing around"
- 规范化负描述："tourists with cameras , standing around behind a fence , watching elephants"
- 正描述 1 选择元组：`[8, 22, 4, 0.5, 0.48]`
- 正描述 2 选择元组：`[15, 23, 3, 0.6666666666666666, 0.6133333333333333]`
- 最终比较正描述：`positive_1` / "Elephants with large tusks, standing around behind a fence."
- 完整 lexeme 编辑块：`[{"tag": "replace", "positive_start": 0, "positive_end": 1, "negative_start": 0, "negative_end": 1, "positive_lexemes": ["elephants"], "negative_lexemes": ["tourists"]}, {"tag": "equal", "positive_start": 1, "positive_end": 2, "negative_start": 1, "negative_end": 2, "positive_lexemes": ["with"], "negative_lexemes": ["with"]}, {"tag": "delete", "positive_start": 2, "positive_end": 3, "negative_start": 2, "negative_end": 2, "positive_lexemes": ["large"], "negative_lexemes": []}, {"tag": "replace", "positive_start": 3, "positive_end": 4, "negative_start": 2, "negative_end": 3, "positive_lexemes": ["tusks"], "negative_lexemes": ["cameras"]}, {"tag": "equal", "positive_start": 4, "positive_end": 10, "negative_start": 3, "negative_end": 9, "positive_lexemes": [",", "standing", "around", "behind", "a", "fence"], "negative_lexemes": [",", "standing", "around", "behind", "a", "fence"]}, {"tag": "insert", "positive_start": 10, "positive_end": 10, "negative_start": 9, "negative_end": 12, "positive_lexemes": [], "negative_lexemes": [",", "watching", "elephants"]}]`
- 共同前缀：`[]`
- 正确 contrast hull：`["elephants", "with", "large", "tusks", ",", "standing", "around", "behind", "a", "fence"]`
- 错误 contrast hull：`["tourists", "with", "cameras", ",", "standing", "around", "behind", "a", "fence", ",", "watching", "elephants"]`
- 共同后缀：`[]`
- Hull token 覆盖率（正/负/最大）：`[1.0, 1.0, 1.0]`
- 共同前缀模型 token：`[]`
- 正确 hull 模型 token：IDs `[4244, 1601, 5483, 599, 2994, 297, 832, 1275, 256, 47, 2823, 350, 3364, 5237, 916, 299, 341, 944]`；text "elephants with large tusks , standing around behind a fence"
- 错误 hull 模型 token：IDs `[119, 1084, 4638, 599, 317, 497, 311, 390, 256, 47, 2823, 350, 3364, 5237, 916, 299, 341, 944, 256, 47, 339, 6131, 350, 1905, 1601, 5483]`；text "tourists with cameras , standing around behind a fence , watching elephants"
- 第一轮/第二轮分类：`complex_edit` / `whole_sentence_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；"at_least_one_hull_covers_all_model_tokens"

### 4. `replace_object:1597`

- 负例类型/范围：`replace_object` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A large metal chair with a brown teddy bear in it."
- 原始正描述 2："There is a brown teddy bear seated in a large chair made of metal."
- 原始负描述："A brown teddy bear is in a hammock."
- 规范化正描述 1："a large metal chair with a brown teddy bear in it"
- 规范化正描述 2："there is a brown teddy bear seated in a large chair made of metal"
- 规范化负描述："a brown teddy bear is in a hammock"
- 正描述 1 选择元组：`[9, 19, 4, 0.7272727272727273, 0.7142857142857143]`
- 正描述 2 选择元组：`[10, 22, 4, 0.5714285714285714, 0.5538461538461539]`
- 最终比较正描述：`positive_1` / "A large metal chair with a brown teddy bear in it."
- 完整 lexeme 编辑块：`[{"tag": "delete", "positive_start": 0, "positive_end": 5, "negative_start": 0, "negative_end": 0, "positive_lexemes": ["a", "large", "metal", "chair", "with"], "negative_lexemes": []}, {"tag": "equal", "positive_start": 5, "positive_end": 9, "negative_start": 0, "negative_end": 4, "positive_lexemes": ["a", "brown", "teddy", "bear"], "negative_lexemes": ["a", "brown", "teddy", "bear"]}, {"tag": "insert", "positive_start": 9, "positive_end": 9, "negative_start": 4, "negative_end": 5, "positive_lexemes": [], "negative_lexemes": ["is"]}, {"tag": "equal", "positive_start": 9, "positive_end": 10, "negative_start": 5, "negative_end": 6, "positive_lexemes": ["in"], "negative_lexemes": ["in"]}, {"tag": "insert", "positive_start": 10, "positive_end": 10, "negative_start": 6, "negative_end": 7, "positive_lexemes": [], "negative_lexemes": ["a"]}, {"tag": "replace", "positive_start": 10, "positive_end": 11, "negative_start": 7, "negative_end": 8, "positive_lexemes": ["it"], "negative_lexemes": ["hammock"]}]`
- 共同前缀：`[]`
- 正确 contrast hull：`["a", "large", "metal", "chair", "with", "a", "brown", "teddy", "bear", "in", "it"]`
- 错误 contrast hull：`["a", "brown", "teddy", "bear", "is", "in", "a", "hammock"]`
- 共同后缀：`[]`
- Hull token 覆盖率（正/负/最大）：`[1.0, 1.0, 1.0]`
- 共同前缀模型 token：`[]`
- 正确 hull 模型 token：IDs `[100, 2994, 4743, 352, 890, 3709, 599, 299, 363, 2079, 113, 297, 382, 103, 124, 600, 370, 353, 563]`；text "a large metal chair with a brown teddy bear in it"
- 错误 hull 模型 token：IDs `[100, 363, 2079, 113, 297, 382, 103, 124, 600, 370, 395, 353, 299, 429, 497, 112, 4469]`；text "a brown teddy bear is in a hammock"
- 第一轮/第二轮分类：`complex_edit` / `whole_sentence_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；"at_least_one_hull_covers_all_model_tokens"

### 5. `replace_relation:818`

- 负例类型/范围：`replace_relation` / `{"canonical": true, "pilot": true, "formal": false, "certifying_formal": false}`
- 原始正描述 1："there is some type of flat bread with topping on the top of it"
- 原始正描述 2："The topping is on top of  some type of flat bread."
- 原始负描述："There is some type of flat bread next to a topping."
- 规范化正描述 1："there is some type of flat bread with topping on the top of it"
- 规范化正描述 2："the topping is on top of some type of flat bread"
- 规范化负描述："there is some type of flat bread next to a topping"
- 正描述 1 选择元组：`[11, 11, 2, 0.5, 0.3387096774193548]`
- 正描述 2 选择元组：`[10, 22, 4, 0.8181818181818182, 0.72]`
- 最终比较正描述：`positive_2` / "The topping is on top of  some type of flat bread."
- 完整 lexeme 编辑块：`[{"tag": "delete", "positive_start": 0, "positive_end": 1, "negative_start": 0, "negative_end": 0, "positive_lexemes": ["the"], "negative_lexemes": []}, {"tag": "replace", "positive_start": 1, "positive_end": 2, "negative_start": 0, "negative_end": 1, "positive_lexemes": ["topping"], "negative_lexemes": ["there"]}, {"tag": "equal", "positive_start": 2, "positive_end": 3, "negative_start": 1, "negative_end": 2, "positive_lexemes": ["is"], "negative_lexemes": ["is"]}, {"tag": "delete", "positive_start": 3, "positive_end": 6, "negative_start": 2, "negative_end": 2, "positive_lexemes": ["on", "top", "of"], "negative_lexemes": []}, {"tag": "equal", "positive_start": 6, "positive_end": 11, "negative_start": 2, "negative_end": 7, "positive_lexemes": ["some", "type", "of", "flat", "bread"], "negative_lexemes": ["some", "type", "of", "flat", "bread"]}, {"tag": "insert", "positive_start": 11, "positive_end": 11, "negative_start": 7, "negative_end": 11, "positive_lexemes": [], "negative_lexemes": ["next", "to", "a", "topping"]}]`
- 共同前缀：`[]`
- 正确 contrast hull：`["the", "topping", "is", "on", "top", "of", "some", "type", "of", "flat", "bread"]`
- 错误 contrast hull：`["there", "is", "some", "type", "of", "flat", "bread", "next", "to", "a", "topping"]`
- 共同后缀：`[]`
- Hull token 覆盖率（正/负/最大）：`[1.0, 1.0, 1.0]`
- 共同前缀模型 token：`[]`
- 正确 hull 模型 token：IDs `[4345, 364, 737, 350, 395, 619, 2924, 354, 2104, 3217, 354, 3687, 314, 3170, 785]`；text "the topping is on top of some type of flat bread"
- 错误 hull 模型 token：IDs `[119, 2503, 395, 2104, 3217, 354, 3687, 314, 3170, 785, 4658, 364, 299, 364, 737, 350]`；text "there is some type of flat bread next to a topping"
- 第一轮/第二轮分类：`complex_edit` / `whole_sentence_hull`
- 自动判断："positive_2_selection_tuple_lexicographically_smaller"；"at_least_one_hull_covers_all_model_tokens"

### 6. `swap_atribute:117`

- 负例类型/范围：`swap_atribute` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": false}`
- 原始正描述 1："Group of people play video games at bestbuy"
- 原始正描述 2："At best buy, group of people are playing video games."
- 原始负描述："Video games play a group of people at Best Buy."
- 规范化正描述 1："group of people play video games at bestbuy"
- 规范化正描述 2："at best buy , group of people are playing video games"
- 规范化负描述："video games play a group of people at best buy"
- 正描述 1 选择元组：`[12, 18, 3, 0.9, 0.6086956521739131]`
- 正描述 2 选择元组：`[15, 21, 3, 0.7272727272727273, 0.6226415094339622]`
- 最终比较正描述：`positive_1` / "Group of people play video games at bestbuy"
- 完整 lexeme 编辑块：`[{"tag": "insert", "positive_start": 0, "positive_end": 0, "negative_start": 0, "negative_end": 4, "positive_lexemes": [], "negative_lexemes": ["video", "games", "play", "a"]}, {"tag": "equal", "positive_start": 0, "positive_end": 3, "negative_start": 4, "negative_end": 7, "positive_lexemes": ["group", "of", "people"], "negative_lexemes": ["group", "of", "people"]}, {"tag": "delete", "positive_start": 3, "positive_end": 5, "negative_start": 7, "negative_end": 7, "positive_lexemes": ["play", "video"], "negative_lexemes": []}, {"tag": "replace", "positive_start": 5, "positive_end": 8, "negative_start": 7, "negative_end": 10, "positive_lexemes": ["games", "at", "bestbuy"], "negative_lexemes": ["at", "best", "buy"]}]`
- 共同前缀：`[]`
- 正确 contrast hull：`["group", "of", "people", "play", "video", "games", "at", "bestbuy"]`
- 错误 contrast hull：`["video", "games", "play", "a", "group", "of", "people", "at", "best", "buy"]`
- 共同后缀：`[]`
- Hull token 覆盖率（正/负/最大）：`[1.0, 1.0, 1.0]`
- 共同前缀模型 token：`[]`
- 正确 hull 模型 token：IDs `[106, 2018, 354, 2975, 2865, 603, 688, 114, 492, 4674, 1248, 2927, 101, 120, 124]`；text "group of people play video games at bestbuy"
- 错误 hull 模型 token：IDs `[121, 688, 114, 492, 4674, 2865, 299, 4592, 354, 2975, 1248, 2927, 3044, 124]`；text "video games play a group of people at best buy"
- 第一轮/第二轮分类：`ambiguous_source` / `whole_sentence_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；"at_least_one_hull_covers_all_model_tokens"

### 7. `swap_atribute:120`

- 负例类型/范围：`swap_atribute` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："a couple is sitting on a statue of a horse, next to some plants"
- 原始正描述 2："A couple is seated on a statue of a horse, next to some plants."
- 原始负描述："Some couples are sitting on a statue of a horse next to a plant."
- 规范化正描述 1："a couple is sitting on a statue of a horse , next to some plants"
- 规范化正描述 2："a couple is seated on a statue of a horse , next to some plants"
- 规范化负描述："some couples are sitting on a statue of a horse next to a plant"
- 正描述 1 选择元组：`[11, 29, 3, 0.4, 0.234375]`
- 正描述 2 选择元组：`[13, 29, 3, 0.4666666666666667, 0.31746031746031744]`
- 最终比较正描述：`positive_1` / "a couple is sitting on a statue of a horse, next to some plants"
- 完整 lexeme 编辑块：`[{"tag": "replace", "positive_start": 0, "positive_end": 3, "negative_start": 0, "negative_end": 3, "positive_lexemes": ["a", "couple", "is"], "negative_lexemes": ["some", "couples", "are"]}, {"tag": "equal", "positive_start": 3, "positive_end": 10, "negative_start": 3, "negative_end": 10, "positive_lexemes": ["sitting", "on", "a", "statue", "of", "a", "horse"], "negative_lexemes": ["sitting", "on", "a", "statue", "of", "a", "horse"]}, {"tag": "delete", "positive_start": 10, "positive_end": 11, "negative_start": 10, "negative_end": 10, "positive_lexemes": [","], "negative_lexemes": []}, {"tag": "equal", "positive_start": 11, "positive_end": 13, "negative_start": 10, "negative_end": 12, "positive_lexemes": ["next", "to"], "negative_lexemes": ["next", "to"]}, {"tag": "replace", "positive_start": 13, "positive_end": 15, "negative_start": 12, "negative_end": 14, "positive_lexemes": ["some", "plants"], "negative_lexemes": ["a", "plant"]}]`
- 共同前缀：`[]`
- 正确 contrast hull：`["a", "couple", "is", "sitting", "on", "a", "statue", "of", "a", "horse", ",", "next", "to", "some", "plants"]`
- 错误 contrast hull：`["some", "couples", "are", "sitting", "on", "a", "statue", "of", "a", "horse", "next", "to", "a", "plant"]`
- 共同后缀：`[]`
- Hull token 覆盖率（正/负/最大）：`[1.0, 1.0, 1.0]`
- 共同前缀模型 token：`[]`
- 正确 hull 模型 token：IDs `[100, 317, 326, 833, 395, 5305, 2912, 619, 299, 5643, 922, 354, 299, 429, 336, 573, 256, 47, 4658, 364, 2104, 1219, 5483]`；text "a couple is sitting on a statue of a horse , next to some plants"
- 错误 hull 模型 token：IDs `[118, 3219, 317, 326, 4711, 732, 5305, 2912, 619, 299, 5643, 922, 354, 299, 429, 336, 573, 4658, 364, 299, 1219, 811]`；text "some couples are sitting on a statue of a horse next to a plant"
- 第一轮/第二轮分类：`complex_edit` / `whole_sentence_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；"at_least_one_hull_covers_all_model_tokens"

### 8. `swap_atribute:178`

- 负例类型/范围：`swap_atribute` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A tall clear glass window with two cats sitting at the base of it."
- 原始正描述 2："The tall clear glass window has two cats sitting at its base."
- 原始负描述："Two tall clear glass windows with a cat sitting at the base of each."
- 规范化正描述 1："a tall clear glass window with two cats sitting at the base of it"
- 规范化正描述 2："the tall clear glass window has two cats sitting at its base"
- 规范化负描述："two tall clear glass windows with a cat sitting at the base of each"
- 正描述 1 选择元组：`[10, 28, 4, 0.35714285714285715, 0.1791044776119403]`
- 正描述 2 选择元组：`[14, 26, 4, 0.5714285714285714, 0.3283582089552239]`
- 最终比较正描述：`positive_1` / "A tall clear glass window with two cats sitting at the base of it."
- 完整 lexeme 编辑块：`[{"tag": "replace", "positive_start": 0, "positive_end": 1, "negative_start": 0, "negative_end": 1, "positive_lexemes": ["a"], "negative_lexemes": ["two"]}, {"tag": "equal", "positive_start": 1, "positive_end": 4, "negative_start": 1, "negative_end": 4, "positive_lexemes": ["tall", "clear", "glass"], "negative_lexemes": ["tall", "clear", "glass"]}, {"tag": "replace", "positive_start": 4, "positive_end": 5, "negative_start": 4, "negative_end": 5, "positive_lexemes": ["window"], "negative_lexemes": ["windows"]}, {"tag": "equal", "positive_start": 5, "positive_end": 6, "negative_start": 5, "negative_end": 6, "positive_lexemes": ["with"], "negative_lexemes": ["with"]}, {"tag": "replace", "positive_start": 6, "positive_end": 8, "negative_start": 6, "negative_end": 8, "positive_lexemes": ["two", "cats"], "negative_lexemes": ["a", "cat"]}, {"tag": "equal", "positive_start": 8, "positive_end": 13, "negative_start": 8, "negative_end": 13, "positive_lexemes": ["sitting", "at", "the", "base", "of"], "negative_lexemes": ["sitting", "at", "the", "base", "of"]}, {"tag": "replace", "positive_start": 13, "positive_end": 14, "negative_start": 13, "negative_end": 14, "positive_lexemes": ["it"], "negative_lexemes": ["each"]}]`
- 共同前缀：`[]`
- 正确 contrast hull：`["a", "tall", "clear", "glass", "window", "with", "two", "cats", "sitting", "at", "the", "base", "of", "it"]`
- 错误 contrast hull：`["two", "tall", "clear", "glass", "windows", "with", "a", "cat", "sitting", "at", "the", "base", "of", "each"]`
- 共同后缀：`[]`
- Hull token 覆盖率（正/负/最大）：`[1.0, 1.0, 1.0]`
- 共同前缀模型 token：`[]`
- 正确 hull 模型 token：IDs `[100, 297, 1266, 4829, 492, 111, 1388, 5472, 451, 599, 2102, 3706, 118, 5305, 2912, 1248, 309, 4933, 354, 563]`；text "a tall clear glass window with two cats sitting at the base of it"
- 错误 hull 模型 token：IDs `[119, 122, 114, 297, 1266, 4829, 492, 111, 1388, 339, 4310, 599, 299, 3706, 5305, 2912, 1248, 309, 4933, 354, 1766]`；text "two tall clear glass windows with a cat sitting at the base of each"
- 第一轮/第二轮分类：`complex_edit` / `whole_sentence_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；"at_least_one_hull_covers_all_model_tokens"

### 9. `swap_atribute:188`

- 负例类型/范围：`swap_atribute` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A person sits in a chair in a living room next to some windows."
- 原始正描述 2："A person is seated in a chair in a living room adjacent to some windows."
- 原始负描述："Some people sit in chairs in a living room next to a window."
- 规范化正描述 1："a person sits in a chair in a living room next to some windows"
- 规范化正描述 2："a person is seated in a chair in a living room adjacent to some windows"
- 规范化负描述："some people sit in chairs in a living room next to a window"
- 正描述 1 选择元组：`[13, 27, 4, 0.5, 0.27419354838709675]`
- 正描述 2 选择元组：`[16, 28, 6, 0.6, 0.39436619718309857]`
- 最终比较正描述：`positive_1` / "A person sits in a chair in a living room next to some windows."
- 完整 lexeme 编辑块：`[{"tag": "replace", "positive_start": 0, "positive_end": 3, "negative_start": 0, "negative_end": 3, "positive_lexemes": ["a", "person", "sits"], "negative_lexemes": ["some", "people", "sit"]}, {"tag": "equal", "positive_start": 3, "positive_end": 4, "negative_start": 3, "negative_end": 4, "positive_lexemes": ["in"], "negative_lexemes": ["in"]}, {"tag": "delete", "positive_start": 4, "positive_end": 5, "negative_start": 4, "negative_end": 4, "positive_lexemes": ["a"], "negative_lexemes": []}, {"tag": "replace", "positive_start": 5, "positive_end": 6, "negative_start": 4, "negative_end": 5, "positive_lexemes": ["chair"], "negative_lexemes": ["chairs"]}, {"tag": "equal", "positive_start": 6, "positive_end": 12, "negative_start": 5, "negative_end": 11, "positive_lexemes": ["in", "a", "living", "room", "next", "to"], "negative_lexemes": ["in", "a", "living", "room", "next", "to"]}, {"tag": "replace", "positive_start": 12, "positive_end": 14, "negative_start": 11, "negative_end": 13, "positive_lexemes": ["some", "windows"], "negative_lexemes": ["a", "window"]}]`
- 共同前缀：`[]`
- 正确 contrast hull：`["a", "person", "sits", "in", "a", "chair", "in", "a", "living", "room", "next", "to", "some", "windows"]`
- 错误 contrast hull：`["some", "people", "sit", "in", "chairs", "in", "a", "living", "room", "next", "to", "a", "window"]`
- 共同后缀：`[]`
- Hull token 覆盖率（正/负/最大）：`[1.0, 1.0, 1.0]`
- 共同前缀模型 token：`[]`
- 正确 hull 模型 token：IDs `[100, 2198, 316, 2163, 353, 299, 890, 3709, 353, 299, 406, 4917, 1552, 444, 4658, 364, 2104, 339, 4310]`；text "a person sits in a chair in a living room next to some windows"
- 错误 hull 模型 token：IDs `[118, 3219, 2975, 5305, 353, 890, 3709, 118, 353, 299, 406, 4917, 1552, 444, 4658, 364, 299, 5472, 451]`；text "some people sit in chairs in a living room next to a window"
- 第一轮/第二轮分类：`complex_edit` / `whole_sentence_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；"at_least_one_hull_covers_all_model_tokens"

### 10. `swap_atribute:208`

- 负例类型/范围：`swap_atribute` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："a black goat standing next to two white goats"
- 原始正描述 2："A black goat is positioned next to two white goats."
- 原始负描述："Two black goats standing next to a white goat."
- 规范化正描述 1："a black goat standing next to two white goats"
- 规范化正描述 2："a black goat is positioned next to two white goats"
- 规范化负描述："two black goats standing next to a white goat"
- 正描述 1 选择元组：`[8, 18, 4, 0.4444444444444444, 0.17777777777777778]`
- 正描述 2 选择元组：`[11, 19, 5, 0.6, 0.34]`
- 最终比较正描述：`positive_1` / "a black goat standing next to two white goats"
- 完整 lexeme 编辑块：`[{"tag": "replace", "positive_start": 0, "positive_end": 1, "negative_start": 0, "negative_end": 1, "positive_lexemes": ["a"], "negative_lexemes": ["two"]}, {"tag": "equal", "positive_start": 1, "positive_end": 2, "negative_start": 1, "negative_end": 2, "positive_lexemes": ["black"], "negative_lexemes": ["black"]}, {"tag": "replace", "positive_start": 2, "positive_end": 3, "negative_start": 2, "negative_end": 3, "positive_lexemes": ["goat"], "negative_lexemes": ["goats"]}, {"tag": "equal", "positive_start": 3, "positive_end": 6, "negative_start": 3, "negative_end": 6, "positive_lexemes": ["standing", "next", "to"], "negative_lexemes": ["standing", "next", "to"]}, {"tag": "replace", "positive_start": 6, "positive_end": 7, "negative_start": 6, "negative_end": 7, "positive_lexemes": ["two"], "negative_lexemes": ["a"]}, {"tag": "equal", "positive_start": 7, "positive_end": 8, "negative_start": 7, "negative_end": 8, "positive_lexemes": ["white"], "negative_lexemes": ["white"]}, {"tag": "replace", "positive_start": 8, "positive_end": 9, "negative_start": 8, "negative_end": 9, "positive_lexemes": ["goats"], "negative_lexemes": ["goat"]}]`
- 共同前缀：`[]`
- 正确 contrast hull：`["a", "black", "goat", "standing", "next", "to", "two", "white", "goats"]`
- 错误 contrast hull：`["two", "black", "goats", "standing", "next", "to", "a", "white", "goat"]`
- 共同后缀：`[]`
- Hull token 覆盖率（正/负/最大）：`[1.0, 1.0, 1.0]`
- 共同前缀模型 token：`[]`
- 正确 hull 模型 token：IDs `[100, 2597, 1637, 2379, 314, 2823, 350, 4658, 364, 2102, 654, 1078, 2379, 4585]`；text "a black goat standing next to two white goats"
- 错误 hull 模型 token：IDs `[119, 122, 114, 2597, 1637, 2379, 4585, 2823, 350, 4658, 364, 299, 654, 1078, 2379, 314]`；text "two black goats standing next to a white goat"
- 第一轮/第二轮分类：`complex_edit` / `whole_sentence_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；"at_least_one_hull_covers_all_model_tokens"

### 11. `swap_atribute:215`

- 负例类型/范围：`swap_atribute` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A couple of detour signs sitting on either side of an orange cone."
- 原始正描述 2："A couple of detour signs are positioned on both sides of an orange cone"
- 原始负描述："An orange detour sign sitting on either side of a couple of cones."
- 规范化正描述 1："a couple of detour signs sitting on either side of an orange cone"
- 规范化正描述 2："a couple of detour signs are positioned on both sides of an orange cone"
- 规范化负描述："an orange detour sign sitting on either side of a couple of cones"
- 正描述 1 选择元组：`[14, 26, 5, 0.6153846153846154, 0.3076923076923077]`
- 正描述 2 选择元组：`[21, 27, 7, 0.8571428571428571, 0.49295774647887325]`
- 最终比较正描述：`positive_1` / "A couple of detour signs sitting on either side of an orange cone."
- 完整 lexeme 编辑块：`[{"tag": "delete", "positive_start": 0, "positive_end": 1, "negative_start": 0, "negative_end": 0, "positive_lexemes": ["a"], "negative_lexemes": []}, {"tag": "replace", "positive_start": 1, "positive_end": 3, "negative_start": 0, "negative_end": 2, "positive_lexemes": ["couple", "of"], "negative_lexemes": ["an", "orange"]}, {"tag": "equal", "positive_start": 3, "positive_end": 4, "negative_start": 2, "negative_end": 3, "positive_lexemes": ["detour"], "negative_lexemes": ["detour"]}, {"tag": "replace", "positive_start": 4, "positive_end": 5, "negative_start": 3, "negative_end": 4, "positive_lexemes": ["signs"], "negative_lexemes": ["sign"]}, {"tag": "equal", "positive_start": 5, "positive_end": 10, "negative_start": 4, "negative_end": 9, "positive_lexemes": ["sitting", "on", "either", "side", "of"], "negative_lexemes": ["sitting", "on", "either", "side", "of"]}, {"tag": "insert", "positive_start": 10, "positive_end": 10, "negative_start": 9, "negative_end": 10, "positive_lexemes": [], "negative_lexemes": ["a"]}, {"tag": "replace", "positive_start": 10, "positive_end": 13, "negative_start": 10, "negative_end": 13, "positive_lexemes": ["an", "orange", "cone"], "negative_lexemes": ["couple", "of", "cones"]}]`
- 共同前缀：`[]`
- 正确 contrast hull：`["a", "couple", "of", "detour", "signs", "sitting", "on", "either", "side", "of", "an", "orange", "cone"]`
- 错误 contrast hull：`["an", "orange", "detour", "sign", "sitting", "on", "either", "side", "of", "a", "couple", "of", "cones"]`
- 共同后缀：`[]`
- Hull token 覆盖率（正/负/最大）：`[1.0, 1.0, 1.0]`
- 共同前缀模型 token：`[]`
- 正确 hull 模型 token：IDs `[100, 317, 326, 833, 354, 1503, 1084, 2185, 118, 5305, 2912, 619, 413, 338, 771, 5046, 354, 346, 522, 1285, 614, 104]`；text "a couple of detour signs sitting on either side of an orange cone"
- 错误 hull 模型 token：IDs `[325, 522, 1285, 1503, 1084, 2185, 5305, 2912, 619, 413, 338, 771, 5046, 354, 299, 317, 326, 833, 354, 614, 329]`；text "an orange detour sign sitting on either side of a couple of cones"
- 第一轮/第二轮分类：`complex_edit` / `whole_sentence_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；"at_least_one_hull_covers_all_model_tokens"

### 12. `swap_atribute:398`

- 负例类型/范围：`swap_atribute` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A child petting two dogs on the side of the street"
- 原始正描述 2：" Two dogs are being pet on the side of the street by a small child."
- 原始负描述："Two children are petting a dog on the street corner."
- 规范化正描述 1："a child petting two dogs on the side of the street"
- 规范化正描述 2："two dogs are being pet on the side of the street by a small child"
- 规范化负描述："two children are petting a dog on the street corner"
- 正描述 1 选择元组：`[15, 21, 5, 0.8181818181818182, 0.5098039215686274]`
- 正描述 2 选择元组：`[17, 23, 5, 0.7333333333333333, 0.6]`
- 最终比较正描述：`positive_1` / "A child petting two dogs on the side of the street"
- 完整 lexeme 编辑块：`[{"tag": "insert", "positive_start": 0, "positive_end": 0, "negative_start": 0, "negative_end": 1, "positive_lexemes": [], "negative_lexemes": ["two"]}, {"tag": "replace", "positive_start": 0, "positive_end": 2, "negative_start": 1, "negative_end": 3, "positive_lexemes": ["a", "child"], "negative_lexemes": ["children", "are"]}, {"tag": "equal", "positive_start": 2, "positive_end": 3, "negative_start": 3, "negative_end": 4, "positive_lexemes": ["petting"], "negative_lexemes": ["petting"]}, {"tag": "replace", "positive_start": 3, "positive_end": 5, "negative_start": 4, "negative_end": 6, "positive_lexemes": ["two", "dogs"], "negative_lexemes": ["a", "dog"]}, {"tag": "equal", "positive_start": 5, "positive_end": 7, "negative_start": 6, "negative_end": 8, "positive_lexemes": ["on", "the"], "negative_lexemes": ["on", "the"]}, {"tag": "delete", "positive_start": 7, "positive_end": 9, "negative_start": 8, "negative_end": 8, "positive_lexemes": ["side", "of"], "negative_lexemes": []}, {"tag": "replace", "positive_start": 9, "positive_end": 11, "negative_start": 8, "negative_end": 10, "positive_lexemes": ["the", "street"], "negative_lexemes": ["street", "corner"]}]`
- 共同前缀：`[]`
- 正确 contrast hull：`["a", "child", "petting", "two", "dogs", "on", "the", "side", "of", "the", "street"]`
- 错误 contrast hull：`["two", "children", "are", "petting", "a", "dog", "on", "the", "street", "corner"]`
- 共同后缀：`[]`
- Hull token 覆盖率（正/负/最大）：`[1.0, 1.0, 1.0]`
- 共同前缀模型 token：`[]`
- 正确 hull 模型 token：IDs `[100, 6109, 344, 439, 2912, 2102, 1041, 4474, 619, 309, 5046, 354, 309, 5941, 439]`；text "a child petting two dogs on the side of the street"
- 错误 hull 模型 token：IDs `[119, 122, 114, 6109, 3193, 732, 344, 439, 2912, 299, 1041, 106, 619, 309, 5941, 439, 2376, 4056]`；text "two children are petting a dog on the street corner"
- 第一轮/第二轮分类：`ambiguous_source` / `whole_sentence_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；"at_least_one_hull_covers_all_model_tokens"

### 13. `swap_atribute:400`

- 负例类型/范围：`swap_atribute` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A plane flies by next to some power lines"
- 原始正描述 2："A plane is positioned nearby some power lines while flying."
- 原始负描述："Some planes fly by next to a power line."
- 规范化正描述 1："a plane flies by next to some power lines"
- 规范化正描述 2："a plane is positioned nearby some power lines while flying"
- 规范化负描述："some planes fly by next to a power line"
- 正描述 1 选择元组：`[10, 18, 3, 0.5555555555555556, 0.3170731707317073]`
- 正描述 2 选择元组：`[19, 19, 2, 1.0, 0.6379310344827587]`
- 最终比较正描述：`positive_1` / "A plane flies by next to some power lines"
- 完整 lexeme 编辑块：`[{"tag": "replace", "positive_start": 0, "positive_end": 3, "negative_start": 0, "negative_end": 3, "positive_lexemes": ["a", "plane", "flies"], "negative_lexemes": ["some", "planes", "fly"]}, {"tag": "equal", "positive_start": 3, "positive_end": 6, "negative_start": 3, "negative_end": 6, "positive_lexemes": ["by", "next", "to"], "negative_lexemes": ["by", "next", "to"]}, {"tag": "replace", "positive_start": 6, "positive_end": 7, "negative_start": 6, "negative_end": 7, "positive_lexemes": ["some"], "negative_lexemes": ["a"]}, {"tag": "equal", "positive_start": 7, "positive_end": 8, "negative_start": 7, "negative_end": 8, "positive_lexemes": ["power"], "negative_lexemes": ["power"]}, {"tag": "replace", "positive_start": 8, "positive_end": 9, "negative_start": 8, "negative_end": 9, "positive_lexemes": ["lines"], "negative_lexemes": ["line"]}]`
- 共同前缀：`[]`
- 正确 contrast hull：`["a", "plane", "flies", "by", "next", "to", "some", "power", "lines"]`
- 错误 contrast hull：`["some", "planes", "fly", "by", "next", "to", "a", "power", "line"]`
- 共同后缀：`[]`
- Hull token 覆盖率（正/负/最大）：`[1.0, 1.0, 1.0]`
- 共同前缀模型 token：`[]`
- 正确 hull 模型 token：IDs `[100, 4140, 104, 3687, 925, 769, 4658, 364, 2104, 3277, 406, 3445]`；text "a plane flies by next to some power lines"
- 错误 hull 模型 token：IDs `[118, 3219, 4140, 329, 341, 542, 769, 4658, 364, 299, 3277, 2909]`；text "some planes fly by next to a power line"
- 第一轮/第二轮分类：`complex_edit` / `whole_sentence_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；"at_least_one_hull_covers_all_model_tokens"

### 14. `swap_atribute:420`

- 负例类型/范围：`swap_atribute` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："Some street signs near a road with a truck."
- 原始正描述 2："A truck is near some street signs on a road."
- 原始负描述："A street sign near a road with some trucks."
- 规范化正描述 1："some street signs near a road with a truck"
- 规范化正描述 2："a truck is near some street signs on a road"
- 规范化负描述："a street sign near a road with some trucks"
- 正描述 1 选择元组：`[8, 18, 3, 0.4444444444444444, 0.23809523809523808]`
- 正描述 2 选择元组：`[15, 17, 3, 0.8, 0.6744186046511628]`
- 最终比较正描述：`positive_1` / "Some street signs near a road with a truck."
- 完整 lexeme 编辑块：`[{"tag": "replace", "positive_start": 0, "positive_end": 1, "negative_start": 0, "negative_end": 1, "positive_lexemes": ["some"], "negative_lexemes": ["a"]}, {"tag": "equal", "positive_start": 1, "positive_end": 2, "negative_start": 1, "negative_end": 2, "positive_lexemes": ["street"], "negative_lexemes": ["street"]}, {"tag": "replace", "positive_start": 2, "positive_end": 3, "negative_start": 2, "negative_end": 3, "positive_lexemes": ["signs"], "negative_lexemes": ["sign"]}, {"tag": "equal", "positive_start": 3, "positive_end": 7, "negative_start": 3, "negative_end": 7, "positive_lexemes": ["near", "a", "road", "with"], "negative_lexemes": ["near", "a", "road", "with"]}, {"tag": "replace", "positive_start": 7, "positive_end": 9, "negative_start": 7, "negative_end": 9, "positive_lexemes": ["a", "truck"], "negative_lexemes": ["some", "trucks"]}]`
- 共同前缀：`[]`
- 正确 contrast hull：`["some", "street", "signs", "near", "a", "road", "with", "a", "truck"]`
- 错误 contrast hull：`["a", "street", "sign", "near", "a", "road", "with", "some", "trucks"]`
- 共同后缀：`[]`
- Hull token 覆盖率（正/负/最大）：`[1.0, 1.0, 1.0]`
- 共同前缀模型 token：`[]`
- 正确 hull 模型 token：IDs `[118, 3219, 5941, 439, 2185, 118, 730, 370, 299, 1552, 785, 599, 299, 1144, 120, 892]`；text "some street signs near a road with a truck"
- 错误 hull 模型 token：IDs `[100, 5941, 439, 2185, 730, 370, 299, 1552, 785, 599, 2104, 1144, 120, 892, 118]`；text "a street sign near a road with some trucks"
- 第一轮/第二轮分类：`complex_edit` / `whole_sentence_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；"at_least_one_hull_covers_all_model_tokens"

### 15. `swap_atribute:425`

- 负例类型/范围：`swap_atribute` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："An airplane is parked next to a domed tower."
- 原始正描述 2："The domed tower is positioned next to the parked airplane."
- 原始负描述："A domed airplane tower is next to a parked building."
- 规范化正描述 1："an airplane is parked next to a domed tower"
- 规范化正描述 2："the domed tower is positioned next to the parked airplane"
- 规范化负描述："a domed airplane tower is next to a parked building"
- 正描述 1 选择元组：`[11, 19, 4, 0.6, 0.5098039215686274]`
- 正描述 2 选择元组：`[8, 20, 5, 0.5, 0.5263157894736842]`
- 最终比较正描述：`positive_2` / "The domed tower is positioned next to the parked airplane."
- 完整 lexeme 编辑块：`[{"tag": "replace", "positive_start": 0, "positive_end": 1, "negative_start": 0, "negative_end": 1, "positive_lexemes": ["the"], "negative_lexemes": ["a"]}, {"tag": "equal", "positive_start": 1, "positive_end": 2, "negative_start": 1, "negative_end": 2, "positive_lexemes": ["domed"], "negative_lexemes": ["domed"]}, {"tag": "insert", "positive_start": 2, "positive_end": 2, "negative_start": 2, "negative_end": 3, "positive_lexemes": [], "negative_lexemes": ["airplane"]}, {"tag": "equal", "positive_start": 2, "positive_end": 4, "negative_start": 3, "negative_end": 5, "positive_lexemes": ["tower", "is"], "negative_lexemes": ["tower", "is"]}, {"tag": "delete", "positive_start": 4, "positive_end": 5, "negative_start": 5, "negative_end": 5, "positive_lexemes": ["positioned"], "negative_lexemes": []}, {"tag": "equal", "positive_start": 5, "positive_end": 7, "negative_start": 5, "negative_end": 7, "positive_lexemes": ["next", "to"], "negative_lexemes": ["next", "to"]}, {"tag": "replace", "positive_start": 7, "positive_end": 8, "negative_start": 7, "negative_end": 8, "positive_lexemes": ["the"], "negative_lexemes": ["a"]}, {"tag": "equal", "positive_start": 8, "positive_end": 9, "negative_start": 8, "negative_end": 9, "positive_lexemes": ["parked"], "negative_lexemes": ["parked"]}, {"tag": "replace", "positive_start": 9, "positive_end": 10, "negative_start": 9, "negative_end": 10, "positive_lexemes": ["airplane"], "negative_lexemes": ["building"]}]`
- 共同前缀：`[]`
- 正确 contrast hull：`["the", "domed", "tower", "is", "positioned", "next", "to", "the", "parked", "airplane"]`
- 错误 contrast hull：`["a", "domed", "airplane", "tower", "is", "next", "to", "a", "parked", "building"]`
- 共同后缀：`[]`
- Hull token 覆盖率（正/负/最大）：`[1.0, 1.0, 1.0]`
- 共同前缀模型 token：`[]`
- 正确 hull 模型 token：IDs `[4345, 373, 444, 382, 364, 122, 311, 395, 2617, 1632, 382, 4658, 364, 309, 344, 2000, 382, 3980, 992, 4875]`；text "the domed tower is positioned next to the parked airplane"
- 错误 hull 模型 token：IDs `[100, 373, 444, 382, 3980, 992, 4875, 364, 122, 311, 395, 4658, 364, 299, 344, 2000, 382, 6331, 350]`；text "a domed airplane tower is next to a parked building"
- 第一轮/第二轮分类：`ambiguous_source` / `whole_sentence_hull`
- 自动判断："positive_2_selection_tuple_lexicographically_smaller"；"at_least_one_hull_covers_all_model_tokens"

### 16. `swap_atribute:461`

- 负例类型/范围：`swap_atribute` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："a computer desk with multiple computers and screens\n"
- 原始正描述 2："Multiple computers and screens on a computer desk."
- 原始负描述："Multiple computer desks with a screen on each."
- 规范化正描述 1："a computer desk with multiple computers and screens"
- 规范化正描述 2："multiple computers and screens on a computer desk"
- 规范化负描述："multiple computer desks with a screen on each"
- 正描述 1 选择元组：`[12, 16, 3, 0.75, 0.6470588235294118]`
- 正描述 2 选择元组：`[14, 14, 1, 0.875, 0.5102040816326531]`
- 最终比较正描述：`positive_1` / "a computer desk with multiple computers and screens\n"
- 完整 lexeme 编辑块：`[{"tag": "replace", "positive_start": 0, "positive_end": 1, "negative_start": 0, "negative_end": 1, "positive_lexemes": ["a"], "negative_lexemes": ["multiple"]}, {"tag": "equal", "positive_start": 1, "positive_end": 2, "negative_start": 1, "negative_end": 2, "positive_lexemes": ["computer"], "negative_lexemes": ["computer"]}, {"tag": "replace", "positive_start": 2, "positive_end": 3, "negative_start": 2, "negative_end": 3, "positive_lexemes": ["desk"], "negative_lexemes": ["desks"]}, {"tag": "equal", "positive_start": 3, "positive_end": 4, "negative_start": 3, "negative_end": 4, "positive_lexemes": ["with"], "negative_lexemes": ["with"]}, {"tag": "replace", "positive_start": 4, "positive_end": 8, "negative_start": 4, "negative_end": 8, "positive_lexemes": ["multiple", "computers", "and", "screens"], "negative_lexemes": ["a", "screen", "on", "each"]}]`
- 共同前缀：`[]`
- 正确 contrast hull：`["a", "computer", "desk", "with", "multiple", "computers", "and", "screens"]`
- 错误 contrast hull：`["multiple", "computer", "desks", "with", "a", "screen", "on", "each"]`
- 共同后缀：`[]`
- Hull token 覆盖率（正/负/最大）：`[1.0, 1.0, 1.0]`
- 共同前缀模型 token：`[]`
- 正确 hull 模型 token：IDs `[100, 4818, 1453, 110, 599, 4503, 2078, 496, 376, 1416, 306, 2101]`；text "a computer desk with multiple computers and screens"
- 错误 hull 模型 token：IDs `[112, 1005, 108, 833, 4818, 1453, 1275, 599, 299, 1416, 306, 327, 619, 1766]`；text "multiple computer desks with a screen on each"
- 第一轮/第二轮分类：`complex_edit` / `whole_sentence_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；"at_least_one_hull_covers_all_model_tokens"

### 17. `swap_atribute:514`

- 负例类型/范围：`swap_atribute` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A panoramic shot of several people standing near a plane."
- 原始正描述 2："A photograph capturing a wide-angle view of multiple individuals positioned near an aircraft."
- 原始负描述："Several planes are near a person standing in a panoramic shot."
- 规范化正描述 1："a panoramic shot of several people standing near a plane"
- 规范化正描述 2："a photograph capturing a wide-angle view of multiple individuals positioned near an aircraft"
- 规范化负描述："several planes are near a person standing in a panoramic shot"
- 正描述 1 选择元组：`[17, 21, 4, 0.8181818181818182, 0.6721311475409836]`
- 正描述 2 选择元组：`[24, 24, 2, 1.0, 0.7391304347826086]`
- 最终比较正描述：`positive_1` / "A panoramic shot of several people standing near a plane."
- 完整 lexeme 编辑块：`[{"tag": "replace", "positive_start": 0, "positive_end": 6, "negative_start": 0, "negative_end": 6, "positive_lexemes": ["a", "panoramic", "shot", "of", "several", "people"], "negative_lexemes": ["several", "planes", "are", "near", "a", "person"]}, {"tag": "equal", "positive_start": 6, "positive_end": 7, "negative_start": 6, "negative_end": 7, "positive_lexemes": ["standing"], "negative_lexemes": ["standing"]}, {"tag": "replace", "positive_start": 7, "positive_end": 8, "negative_start": 7, "negative_end": 8, "positive_lexemes": ["near"], "negative_lexemes": ["in"]}, {"tag": "equal", "positive_start": 8, "positive_end": 9, "negative_start": 8, "negative_end": 9, "positive_lexemes": ["a"], "negative_lexemes": ["a"]}, {"tag": "insert", "positive_start": 9, "positive_end": 9, "negative_start": 9, "negative_end": 10, "positive_lexemes": [], "negative_lexemes": ["panoramic"]}, {"tag": "replace", "positive_start": 9, "positive_end": 10, "negative_start": 10, "negative_end": 11, "positive_lexemes": ["plane"], "negative_lexemes": ["shot"]}]`
- 共同前缀：`[]`
- 正确 contrast hull：`["a", "panoramic", "shot", "of", "several", "people", "standing", "near", "a", "plane"]`
- 错误 contrast hull：`["several", "planes", "are", "near", "a", "person", "standing", "in", "a", "panoramic", "shot"]`
- 共同后缀：`[]`
- Hull token 覆盖率（正/负/最大）：`[1.0, 1.0, 1.0]`
- 共同前缀模型 token：`[]`
- 正确 hull 模型 token：IDs `[100, 344, 325, 336, 497, 375, 1128, 593, 354, 4920, 2975, 2823, 350, 730, 370, 299, 4140, 104]`；text "a panoramic shot of several people standing near a plane"
- 错误 hull 模型 token：IDs `[573, 652, 352, 4140, 329, 732, 730, 370, 299, 2198, 2823, 350, 353, 299, 344, 325, 336, 497, 375, 1128, 593]`；text "several planes are near a person standing in a panoramic shot"
- 第一轮/第二轮分类：`complex_edit` / `whole_sentence_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；"at_least_one_hull_covers_all_model_tokens"

### 18. `swap_atribute:520`

- 负例类型/范围：`swap_atribute` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："TWO GIRAFFES STANDING IN THE SHADE OF A TREE."
- 原始正描述 2："In the shade of a tree, the two giraffes are standing."
- 原始负描述："A giraffe standing in the shade of two trees."
- 规范化正描述 1："two giraffes standing in the shade of a tree"
- 规范化正描述 2："in the shade of a tree , the two giraffes are standing"
- 规范化负描述："a giraffe standing in the shade of two trees"
- 正描述 1 选择元组：`[8, 18, 2, 0.4444444444444444, 0.18181818181818182]`
- 正描述 2 选择元组：`[11, 21, 4, 0.8333333333333334, 0.7592592592592593]`
- 最终比较正描述：`positive_1` / "TWO GIRAFFES STANDING IN THE SHADE OF A TREE."
- 完整 lexeme 编辑块：`[{"tag": "replace", "positive_start": 0, "positive_end": 2, "negative_start": 0, "negative_end": 2, "positive_lexemes": ["two", "giraffes"], "negative_lexemes": ["a", "giraffe"]}, {"tag": "equal", "positive_start": 2, "positive_end": 7, "negative_start": 2, "negative_end": 7, "positive_lexemes": ["standing", "in", "the", "shade", "of"], "negative_lexemes": ["standing", "in", "the", "shade", "of"]}, {"tag": "replace", "positive_start": 7, "positive_end": 9, "negative_start": 7, "negative_end": 9, "positive_lexemes": ["a", "tree"], "negative_lexemes": ["two", "trees"]}]`
- 共同前缀：`[]`
- 正确 contrast hull：`["two", "giraffes", "standing", "in", "the", "shade", "of", "a", "tree"]`
- 错误 contrast hull：`["a", "giraffe", "standing", "in", "the", "shade", "of", "two", "trees"]`
- 共同后缀：`[]`
- Hull token 覆盖率（正/负/最大）：`[1.0, 1.0, 1.0]`
- 共同前缀模型 token：`[]`
- 正确 hull 模型 token：IDs `[119, 122, 114, 492, 108, 559, 1627, 329, 2823, 350, 353, 309, 1128, 5170, 354, 299, 297, 1382]`；text "two giraffes standing in the shade of a tree"
- 错误 hull 模型 token：IDs `[100, 492, 108, 559, 1627, 104, 2823, 350, 353, 309, 1128, 5170, 354, 2102, 4191, 329]`；text "a giraffe standing in the shade of two trees"
- 第一轮/第二轮分类：`complex_edit` / `whole_sentence_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；"at_least_one_hull_covers_all_model_tokens"

### 19. `swap_atribute:543`

- 负例类型/范围：`swap_atribute` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："a couple of people that are walking in some grass"
- 原始正描述 2："A group of individuals are strolling in a grassy area."
- 原始负描述："Some people are walking in a couple of grassy fields."
- 规范化正描述 1："a couple of people that are walking in some grass"
- 规范化正描述 2："a group of individuals are strolling in a grassy area"
- 规范化负描述："some people are walking in a couple of grassy fields"
- 正描述 1 选择元组：`[12, 20, 5, 0.9, 0.5961538461538461]`
- 正描述 2 选择元组：`[12, 20, 5, 0.8, 0.7358490566037735]`
- 最终比较正描述：`positive_2` / "A group of individuals are strolling in a grassy area."
- 完整 lexeme 编辑块：`[{"tag": "delete", "positive_start": 0, "positive_end": 2, "negative_start": 0, "negative_end": 0, "positive_lexemes": ["a", "group"], "negative_lexemes": []}, {"tag": "replace", "positive_start": 2, "positive_end": 4, "negative_start": 0, "negative_end": 2, "positive_lexemes": ["of", "individuals"], "negative_lexemes": ["some", "people"]}, {"tag": "equal", "positive_start": 4, "positive_end": 5, "negative_start": 2, "negative_end": 3, "positive_lexemes": ["are"], "negative_lexemes": ["are"]}, {"tag": "replace", "positive_start": 5, "positive_end": 6, "negative_start": 3, "negative_end": 4, "positive_lexemes": ["strolling"], "negative_lexemes": ["walking"]}, {"tag": "equal", "positive_start": 6, "positive_end": 8, "negative_start": 4, "negative_end": 6, "positive_lexemes": ["in", "a"], "negative_lexemes": ["in", "a"]}, {"tag": "insert", "positive_start": 8, "positive_end": 8, "negative_start": 6, "negative_end": 8, "positive_lexemes": [], "negative_lexemes": ["couple", "of"]}, {"tag": "equal", "positive_start": 8, "positive_end": 9, "negative_start": 8, "negative_end": 9, "positive_lexemes": ["grassy"], "negative_lexemes": ["grassy"]}, {"tag": "replace", "positive_start": 9, "positive_end": 10, "negative_start": 9, "negative_end": 10, "positive_lexemes": ["area"], "negative_lexemes": ["fields"]}]`
- 共同前缀：`[]`
- 正确 contrast hull：`["a", "group", "of", "individuals", "are", "strolling", "in", "a", "grassy", "area"]`
- 错误 contrast hull：`["some", "people", "are", "walking", "in", "a", "couple", "of", "grassy", "fields"]`
- 共同后缀：`[]`
- Hull token 覆盖率（正/负/最大）：`[1.0, 1.0, 1.0]`
- 共同前缀模型 token：`[]`
- 正确 hull 模型 token：IDs `[100, 4592, 354, 6203, 732, 580, 393, 1989, 350, 353, 299, 492, 117, 1388, 124, 2808]`；text "a group of individuals are strolling in a grassy area"
- 错误 hull 模型 token：IDs `[118, 3219, 2975, 732, 339, 352, 1237, 353, 299, 317, 326, 833, 354, 492, 117, 1388, 124, 3848, 1881]`；text "some people are walking in a couple of grassy fields"
- 第一轮/第二轮分类：`ambiguous_source` / `whole_sentence_hull`
- 自动判断："positive_2_selection_tuple_lexicographically_smaller"；"at_least_one_hull_covers_all_model_tokens"

### 20. `swap_atribute:634`

- 负例类型/范围：`swap_atribute` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："a blue suitcase sits on the floor in front of 2 pair of shoes"
- 原始正描述 2：" Two pairs of shoes are behind the blue suitcase is positioned on the floor."
- 原始负描述："2 pair of suitcases sit on the floor in front of a blue shoe."
- 规范化正描述 1："a blue suitcase sits on the floor in front of 2 pair of shoes"
- 规范化正描述 2："two pairs of shoes are behind the blue suitcase is positioned on the floor"
- 规范化负描述："2 pair of suitcases sit on the floor in front of a blue shoe"
- 正描述 1 选择元组：`[16, 28, 4, 0.6428571428571429, 0.3114754098360656]`
- 正描述 2 选择元组：`[24, 28, 3, 0.8571428571428571, 0.6351351351351351]`
- 最终比较正描述：`positive_1` / "a blue suitcase sits on the floor in front of 2 pair of shoes"
- 完整 lexeme 编辑块：`[{"tag": "insert", "positive_start": 0, "positive_end": 0, "negative_start": 0, "negative_end": 1, "positive_lexemes": [], "negative_lexemes": ["2"]}, {"tag": "replace", "positive_start": 0, "positive_end": 4, "negative_start": 1, "negative_end": 5, "positive_lexemes": ["a", "blue", "suitcase", "sits"], "negative_lexemes": ["pair", "of", "suitcases", "sit"]}, {"tag": "equal", "positive_start": 4, "positive_end": 10, "negative_start": 5, "negative_end": 11, "positive_lexemes": ["on", "the", "floor", "in", "front", "of"], "negative_lexemes": ["on", "the", "floor", "in", "front", "of"]}, {"tag": "delete", "positive_start": 10, "positive_end": 11, "negative_start": 11, "negative_end": 11, "positive_lexemes": ["2"], "negative_lexemes": []}, {"tag": "replace", "positive_start": 11, "positive_end": 14, "negative_start": 11, "negative_end": 14, "positive_lexemes": ["pair", "of", "shoes"], "negative_lexemes": ["a", "blue", "shoe"]}]`
- 共同前缀：`[]`
- 正确 contrast hull：`["a", "blue", "suitcase", "sits", "on", "the", "floor", "in", "front", "of", "2", "pair", "of", "shoes"]`
- 错误 contrast hull：`["2", "pair", "of", "suitcases", "sit", "on", "the", "floor", "in", "front", "of", "a", "blue", "shoe"]`
- 共同后缀：`[]`
- Hull token 覆盖率（正/负/最大）：`[1.0, 1.0, 1.0]`
- 共同前缀模型 token：`[]`
- 正确 hull 模型 token：IDs `[100, 4300, 855, 338, 4220, 316, 2163, 619, 309, 5796, 336, 353, 341, 117, 3856, 354, 546, 344, 3709, 354, 1128, 114, 329]`；text "a blue suitcase sits on the floor in front of 2 pair of shoes"
- 错误 hull 模型 token：IDs `[53, 344, 3709, 354, 855, 338, 102, 3164, 5305, 619, 309, 5796, 336, 353, 341, 117, 3856, 354, 299, 4300, 1128, 114, 104]`；text "2 pair of suitcases sit on the floor in front of a blue shoe"
- 第一轮/第二轮分类：`complex_edit` / `whole_sentence_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；"at_least_one_hull_covers_all_model_tokens"

### 21. `swap_atribute:75`

- 负例类型/范围：`swap_atribute` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A white frosted cake sitting in front of some white flowers."
- 原始正描述 2："The white flowers are positioned behind the white frosted cake."
- 原始负描述："Some white frosted flowers sitting in front of a white cake."
- 规范化正描述 1："a white frosted cake sitting in front of some white flowers"
- 规范化正描述 2："the white flowers are positioned behind the white frosted cake"
- 规范化负描述："some white frosted flowers sitting in front of a white cake"
- 正描述 1 选择元组：`[8, 22, 4, 0.36363636363636365, 0.3389830508474576]`
- 正描述 2 选择元组：`[15, 19, 3, 0.7272727272727273, 0.6129032258064516]`
- 最终比较正描述：`positive_1` / "A white frosted cake sitting in front of some white flowers."
- 完整 lexeme 编辑块：`[{"tag": "replace", "positive_start": 0, "positive_end": 1, "negative_start": 0, "negative_end": 1, "positive_lexemes": ["a"], "negative_lexemes": ["some"]}, {"tag": "equal", "positive_start": 1, "positive_end": 3, "negative_start": 1, "negative_end": 3, "positive_lexemes": ["white", "frosted"], "negative_lexemes": ["white", "frosted"]}, {"tag": "replace", "positive_start": 3, "positive_end": 4, "negative_start": 3, "negative_end": 4, "positive_lexemes": ["cake"], "negative_lexemes": ["flowers"]}, {"tag": "equal", "positive_start": 4, "positive_end": 8, "negative_start": 4, "negative_end": 8, "positive_lexemes": ["sitting", "in", "front", "of"], "negative_lexemes": ["sitting", "in", "front", "of"]}, {"tag": "replace", "positive_start": 8, "positive_end": 9, "negative_start": 8, "negative_end": 9, "positive_lexemes": ["some"], "negative_lexemes": ["a"]}, {"tag": "equal", "positive_start": 9, "positive_end": 10, "negative_start": 9, "negative_end": 10, "positive_lexemes": ["white"], "negative_lexemes": ["white"]}, {"tag": "replace", "positive_start": 10, "positive_end": 11, "negative_start": 10, "negative_end": 11, "positive_lexemes": ["flowers"], "negative_lexemes": ["cake"]}]`
- 共同前缀：`[]`
- 正确 contrast hull：`["a", "white", "frosted", "cake", "sitting", "in", "front", "of", "some", "white", "flowers"]`
- 错误 contrast hull：`["some", "white", "frosted", "flowers", "sitting", "in", "front", "of", "a", "white", "cake"]`
- 共同后缀：`[]`
- Hull token 覆盖率（正/负/最大）：`[1.0, 1.0, 1.0]`
- 共同前缀模型 token：`[]`
- 正确 hull 模型 token：IDs `[100, 654, 1078, 341, 393, 432, 382, 317, 2434, 5305, 2912, 353, 341, 117, 3856, 354, 2104, 654, 1078, 5652, 496]`；text "a white frosted cake sitting in front of some white flowers"
- 错误 hull 模型 token：IDs `[118, 3219, 654, 1078, 341, 393, 432, 382, 5652, 496, 5305, 2912, 353, 341, 117, 3856, 354, 299, 654, 1078, 317, 2434]`；text "some white frosted flowers sitting in front of a white cake"
- 第一轮/第二轮分类：`complex_edit` / `whole_sentence_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；"at_least_one_hull_covers_all_model_tokens"

### 22. `swap_object:128`

- 负例类型/范围：`swap_object` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A white plate on top of a table topped with fruits and vegetables."
- 原始正描述 2："The table has a white plate on top of it, with fruits and vegetables arranged on top of the plate."
- 原始负描述："Fruits and vegetables on top of a table topped with a white plate."
- 规范化正描述 1："a white plate on top of a table topped with fruits and vegetables"
- 规范化正描述 2："the table has a white plate on top of it , with fruits and vegetables arranged on top of the plate"
- 规范化负描述："fruits and vegetables on top of a table topped with a white plate"
- 正描述 1 选择元组：`[12, 26, 2, 0.46153846153846156, 0.5230769230769231]`
- 正描述 2 选择元组：`[26, 32, 4, 0.8095238095238095, 0.6326530612244898]`
- 最终比较正描述：`positive_1` / "A white plate on top of a table topped with fruits and vegetables."
- 完整 lexeme 编辑块：`[{"tag": "replace", "positive_start": 0, "positive_end": 3, "negative_start": 0, "negative_end": 3, "positive_lexemes": ["a", "white", "plate"], "negative_lexemes": ["fruits", "and", "vegetables"]}, {"tag": "equal", "positive_start": 3, "positive_end": 10, "negative_start": 3, "negative_end": 10, "positive_lexemes": ["on", "top", "of", "a", "table", "topped", "with"], "negative_lexemes": ["on", "top", "of", "a", "table", "topped", "with"]}, {"tag": "replace", "positive_start": 10, "positive_end": 13, "negative_start": 10, "negative_end": 13, "positive_lexemes": ["fruits", "and", "vegetables"], "negative_lexemes": ["a", "white", "plate"]}]`
- 共同前缀：`[]`
- 正确 contrast hull：`["a", "white", "plate", "on", "top", "of", "a", "table", "topped", "with", "fruits", "and", "vegetables"]`
- 错误 contrast hull：`["fruits", "and", "vegetables", "on", "top", "of", "a", "table", "topped", "with", "a", "white", "plate"]`
- 共同后缀：`[]`
- Hull token 覆盖率（正/负/最大）：`[1.0, 1.0, 1.0]`
- 共同前缀模型 token：`[]`
- 正确 hull 模型 token：IDs `[100, 654, 1078, 1219, 557, 619, 2924, 354, 299, 2630, 364, 737, 382, 599, 341, 1737, 2163, 376, 4389, 2353, 4880]`；text "a white plate on top of a table topped with fruits and vegetables"
- 错误 hull 模型 token：IDs `[105, 1737, 2163, 376, 4389, 2353, 4880, 619, 2924, 354, 299, 2630, 364, 737, 382, 599, 299, 654, 1078, 1219, 557]`；text "fruits and vegetables on top of a table topped with a white plate"
- 第一轮/第二轮分类：`complex_edit` / `whole_sentence_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；"at_least_one_hull_covers_all_model_tokens"

### 23. `swap_object:133`

- 负例类型/范围：`swap_object` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A person sitting in front of the Eiffel tower near pigeons."
- 原始正描述 2："A person is surrounded by pigeons while sitting in front of the Eiffel tower, ."
- 原始负描述："Pigeons sitting in front of the Eiffel tower near a person."
- 规范化正描述 1："a person sitting in front of the eiffel tower near pigeons"
- 规范化正描述 2："a person is surrounded by pigeons while sitting in front of the eiffel tower ,"
- 规范化负描述："pigeons sitting in front of the eiffel tower near a person"
- 正描述 1 选择元组：`[6, 22, 4, 0.36363636363636365, 0.20689655172413793]`
- 正描述 2 选择元组：`[10, 26, 4, 0.6, 0.5769230769230769]`
- 最终比较正描述：`positive_1` / "A person sitting in front of the Eiffel tower near pigeons."
- 完整 lexeme 编辑块：`[{"tag": "delete", "positive_start": 0, "positive_end": 1, "negative_start": 0, "negative_end": 0, "positive_lexemes": ["a"], "negative_lexemes": []}, {"tag": "replace", "positive_start": 1, "positive_end": 2, "negative_start": 0, "negative_end": 1, "positive_lexemes": ["person"], "negative_lexemes": ["pigeons"]}, {"tag": "equal", "positive_start": 2, "positive_end": 10, "negative_start": 1, "negative_end": 9, "positive_lexemes": ["sitting", "in", "front", "of", "the", "eiffel", "tower", "near"], "negative_lexemes": ["sitting", "in", "front", "of", "the", "eiffel", "tower", "near"]}, {"tag": "insert", "positive_start": 10, "positive_end": 10, "negative_start": 9, "negative_end": 10, "positive_lexemes": [], "negative_lexemes": ["a"]}, {"tag": "replace", "positive_start": 10, "positive_end": 11, "negative_start": 10, "negative_end": 11, "positive_lexemes": ["pigeons"], "negative_lexemes": ["person"]}]`
- 共同前缀：`[]`
- 正确 contrast hull：`["a", "person", "sitting", "in", "front", "of", "the", "eiffel", "tower", "near", "pigeons"]`
- 错误 contrast hull：`["pigeons", "sitting", "in", "front", "of", "the", "eiffel", "tower", "near", "a", "person"]`
- 共同后缀：`[]`
- Hull token 覆盖率（正/负/最大）：`[1.0, 1.0, 1.0]`
- 共同前缀模型 token：`[]`
- 正确 hull 模型 token：IDs `[100, 2198, 5305, 2912, 353, 341, 117, 3856, 354, 309, 413, 507, 105, 446, 364, 122, 311, 730, 370, 344, 499, 104, 3070]`；text "a person sitting in front of the eiffel tower near pigeons"
- 错误 hull 模型 token：IDs `[115, 499, 104, 3070, 5305, 2912, 353, 341, 117, 3856, 354, 309, 413, 507, 105, 446, 364, 122, 311, 730, 370, 299, 2198]`；text "pigeons sitting in front of the eiffel tower near a person"
- 第一轮/第二轮分类：`complex_edit` / `whole_sentence_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；"at_least_one_hull_covers_all_model_tokens"

### 24. `swap_object:137`

- 负例类型/范围：`swap_object` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："Four persons playing Ultimate Frisbee in a park."
- 原始正描述 2："Four persons are in a park playing Ultimate Frisbee."
- 原始负描述："A park playing Ultimate Frisbee with four persons."
- 规范化正描述 1："four persons playing ultimate frisbee in a park"
- 规范化正描述 2："four persons are in a park playing ultimate frisbee"
- 规范化负描述："a park playing ultimate frisbee with four persons"
- 正描述 1 选择元组：`[10, 16, 2, 0.625, 0.42857142857142855]`
- 正描述 2 选择元组：`[7, 17, 2, 0.7777777777777778, 0.7450980392156863]`
- 最终比较正描述：`positive_2` / "Four persons are in a park playing Ultimate Frisbee."
- 完整 lexeme 编辑块：`[{"tag": "delete", "positive_start": 0, "positive_end": 4, "negative_start": 0, "negative_end": 0, "positive_lexemes": ["four", "persons", "are", "in"], "negative_lexemes": []}, {"tag": "equal", "positive_start": 4, "positive_end": 9, "negative_start": 0, "negative_end": 5, "positive_lexemes": ["a", "park", "playing", "ultimate", "frisbee"], "negative_lexemes": ["a", "park", "playing", "ultimate", "frisbee"]}, {"tag": "insert", "positive_start": 9, "positive_end": 9, "negative_start": 5, "negative_end": 8, "positive_lexemes": [], "negative_lexemes": ["with", "four", "persons"]}]`
- 共同前缀：`[]`
- 正确 contrast hull：`["four", "persons", "are", "in", "a", "park", "playing", "ultimate", "frisbee"]`
- 错误 contrast hull：`["a", "park", "playing", "ultimate", "frisbee", "with", "four", "persons"]`
- 共同后缀：`[]`
- Hull token 覆盖率（正/负/最大）：`[1.0, 1.0, 1.0]`
- 共同前缀模型 token：`[]`
- 正确 hull 模型 token：IDs `[105, 1084, 2198, 118, 732, 353, 299, 344, 2000, 2865, 350, 483, 111, 119, 4489, 341, 117, 324, 5158, 104]`；text "four persons are in a park playing ultimate frisbee"
- 错误 hull 模型 token：IDs `[100, 344, 2000, 2865, 350, 483, 111, 119, 4489, 341, 117, 324, 5158, 104, 599, 5701, 2198, 118]`；text "a park playing ultimate frisbee with four persons"
- 第一轮/第二轮分类：`complex_edit` / `whole_sentence_hull`
- 自动判断："positive_2_selection_tuple_lexicographically_smaller"；"at_least_one_hull_covers_all_model_tokens"

### 25. `swap_object:18`

- 负例类型/范围：`swap_object` / `{"canonical": true, "pilot": true, "formal": false, "certifying_formal": false}`
- 原始正描述 1："Luggage is arranged in groups  on a concrete  platform."
- 原始正描述 2："Luggage is placed on a concrete platform and is organized in groups."
- 原始负描述："A concrete platform is arranged in groups with luggage on it."
- 规范化正描述 1："luggage is arranged in groups on a concrete platform"
- 规范化正描述 2："luggage is placed on a concrete platform and is organized in groups"
- 规范化负描述："a concrete platform is arranged in groups with luggage on it"
- 正描述 1 选择元组：`[12, 20, 3, 0.6363636363636364, 0.6166666666666667]`
- 正描述 2 选择元组：`[11, 23, 4, 0.8333333333333334, 0.7164179104477612]`
- 最终比较正描述：`positive_2` / "Luggage is placed on a concrete platform and is organized in groups."
- 完整 lexeme 编辑块：`[{"tag": "delete", "positive_start": 0, "positive_end": 4, "negative_start": 0, "negative_end": 0, "positive_lexemes": ["luggage", "is", "placed", "on"], "negative_lexemes": []}, {"tag": "equal", "positive_start": 4, "positive_end": 7, "negative_start": 0, "negative_end": 3, "positive_lexemes": ["a", "concrete", "platform"], "negative_lexemes": ["a", "concrete", "platform"]}, {"tag": "delete", "positive_start": 7, "positive_end": 8, "negative_start": 3, "negative_end": 3, "positive_lexemes": ["and"], "negative_lexemes": []}, {"tag": "equal", "positive_start": 8, "positive_end": 9, "negative_start": 3, "negative_end": 4, "positive_lexemes": ["is"], "negative_lexemes": ["is"]}, {"tag": "replace", "positive_start": 9, "positive_end": 10, "negative_start": 4, "negative_end": 5, "positive_lexemes": ["organized"], "negative_lexemes": ["arranged"]}, {"tag": "equal", "positive_start": 10, "positive_end": 12, "negative_start": 5, "negative_end": 7, "positive_lexemes": ["in", "groups"], "negative_lexemes": ["in", "groups"]}, {"tag": "insert", "positive_start": 12, "positive_end": 12, "negative_start": 7, "negative_end": 11, "positive_lexemes": [], "negative_lexemes": ["with", "luggage", "on", "it"]}]`
- 共同前缀：`[]`
- 正确 contrast hull：`["luggage", "is", "placed", "on", "a", "concrete", "platform", "and", "is", "organized", "in", "groups"]`
- 错误 contrast hull：`["a", "concrete", "platform", "is", "arranged", "in", "groups", "with", "luggage", "on", "it"]`
- 共同后缀：`[]`
- Hull token 覆盖率（正/负/最大）：`[1.0, 1.0, 1.0]`
- 共同前缀模型 token：`[]`
- 正确 hull 模型 token：IDs `[111, 3304, 106, 834, 395, 1219, 1545, 382, 619, 299, 614, 2395, 741, 3887, 376, 395, 4296, 2754, 353, 4592, 118]`；text "luggage is placed on a concrete platform and is organized in groups"
- 错误 hull 模型 token：IDs `[100, 614, 2395, 741, 3887, 395, 3562, 942, 382, 353, 4592, 118, 599, 406, 3304, 106, 834, 619, 563]`；text "a concrete platform is arranged in groups with luggage on it"
- 第一轮/第二轮分类：`complex_edit` / `whole_sentence_hull`
- 自动判断："positive_2_selection_tuple_lexicographically_smaller"；"at_least_one_hull_covers_all_model_tokens"

### 26. `swap_object:184`

- 负例类型/范围：`swap_object` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A bluebery cake is on a plate and is topped with butter."
- 原始正描述 2："The blueberry cake that is topped with butter is placed on a plate."
- 原始负描述："Butter is on a plate and is topped with a blueberry cake."
- 规范化正描述 1："a bluebery cake is on a plate and is topped with butter"
- 规范化正描述 2："the blueberry cake that is topped with butter is placed on a plate"
- 规范化负描述："butter is on a plate and is topped with a blueberry cake"
- 正描述 1 选择元组：`[8, 24, 4, 0.5, 0.4107142857142857]`
- 正描述 2 选择元组：`[19, 25, 4, 0.9230769230769231, 0.6212121212121212]`
- 最终比较正描述：`positive_1` / "A bluebery cake is on a plate and is topped with butter."
- 完整 lexeme 编辑块：`[{"tag": "delete", "positive_start": 0, "positive_end": 2, "negative_start": 0, "negative_end": 0, "positive_lexemes": ["a", "bluebery"], "negative_lexemes": []}, {"tag": "replace", "positive_start": 2, "positive_end": 3, "negative_start": 0, "negative_end": 1, "positive_lexemes": ["cake"], "negative_lexemes": ["butter"]}, {"tag": "equal", "positive_start": 3, "positive_end": 11, "negative_start": 1, "negative_end": 9, "positive_lexemes": ["is", "on", "a", "plate", "and", "is", "topped", "with"], "negative_lexemes": ["is", "on", "a", "plate", "and", "is", "topped", "with"]}, {"tag": "insert", "positive_start": 11, "positive_end": 11, "negative_start": 9, "negative_end": 11, "positive_lexemes": [], "negative_lexemes": ["a", "blueberry"]}, {"tag": "replace", "positive_start": 11, "positive_end": 12, "negative_start": 11, "negative_end": 12, "positive_lexemes": ["butter"], "negative_lexemes": ["cake"]}]`
- 共同前缀：`[]`
- 正确 contrast hull：`["a", "bluebery", "cake", "is", "on", "a", "plate", "and", "is", "topped", "with", "butter"]`
- 错误 contrast hull：`["butter", "is", "on", "a", "plate", "and", "is", "topped", "with", "a", "blueberry", "cake"]`
- 共同后缀：`[]`
- Hull token 覆盖率（正/负/最大）：`[1.0, 1.0, 1.0]`
- 共同前缀模型 token：`[]`
- 正确 hull 模型 token：IDs `[100, 4300, 101, 1976, 317, 2434, 395, 619, 299, 1219, 557, 376, 395, 364, 737, 382, 599, 1362, 887]`；text "a bluebery cake is on a plate and is topped with butter"
- 错误 hull 模型 token：IDs `[101, 501, 887, 395, 619, 299, 1219, 557, 376, 395, 364, 737, 382, 599, 299, 4300, 2009, 1557, 317, 2434]`；text "butter is on a plate and is topped with a blueberry cake"
- 第一轮/第二轮分类：`complex_edit` / `whole_sentence_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；"at_least_one_hull_covers_all_model_tokens"

### 27. `swap_object:197`

- 负例类型/范围：`swap_object` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A car on a road passes a standing elephant."
- 原始正描述 2："A standing elephant is positioned on the road, and a car on the road passes it."
- 原始负描述："An elephant on a road passes a standing car."
- 规范化正描述 1："a car on a road passes a standing elephant"
- 规范化正描述 2："a standing elephant is positioned on the road , and a car on the road passes it"
- 规范化负描述："an elephant on a road passes a standing car"
- 正描述 1 选择元组：`[6, 18, 2, 0.3333333333333333, 0.3488372093023256]`
- 正描述 2 选择元组：`[18, 26, 8, 0.7647058823529411, 0.6455696202531646]`
- 最终比较正描述：`positive_1` / "A car on a road passes a standing elephant."
- 完整 lexeme 编辑块：`[{"tag": "replace", "positive_start": 0, "positive_end": 2, "negative_start": 0, "negative_end": 2, "positive_lexemes": ["a", "car"], "negative_lexemes": ["an", "elephant"]}, {"tag": "equal", "positive_start": 2, "positive_end": 8, "negative_start": 2, "negative_end": 8, "positive_lexemes": ["on", "a", "road", "passes", "a", "standing"], "negative_lexemes": ["on", "a", "road", "passes", "a", "standing"]}, {"tag": "replace", "positive_start": 8, "positive_end": 9, "negative_start": 8, "negative_end": 9, "positive_lexemes": ["elephant"], "negative_lexemes": ["car"]}]`
- 共同前缀：`[]`
- 正确 contrast hull：`["a", "car", "on", "a", "road", "passes", "a", "standing", "elephant"]`
- 错误 contrast hull：`["an", "elephant", "on", "a", "road", "passes", "a", "standing", "car"]`
- 共同后缀：`[]`
- Hull token 覆盖率（正/负/最大）：`[1.0, 1.0, 1.0]`
- 共同前缀模型 token：`[]`
- 正确 hull 模型 token：IDs `[100, 3751, 619, 299, 1552, 785, 3241, 329, 299, 2823, 350, 1905, 1601, 811]`；text "a car on a road passes a standing elephant"
- 错误 hull 模型 token：IDs `[325, 1905, 1601, 811, 619, 299, 1552, 785, 3241, 329, 299, 2823, 350, 3751]`；text "an elephant on a road passes a standing car"
- 第一轮/第二轮分类：`complex_edit` / `whole_sentence_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；"at_least_one_hull_covers_all_model_tokens"

### 28. `swap_object:230`

- 负例类型/范围：`swap_object` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A snowboarder is flying in the air over snow."
- 原始正描述 2："A person on skis above snow is flying in the air."
- 原始负描述："Snow is flying in the air over a snowboarder."
- 规范化正描述 1："a snowboarder is flying in the air over snow"
- 规范化正描述 2："a person on skis above snow is flying in the air"
- 规范化负描述："snow is flying in the air over a snowboarder"
- 正描述 1 选择元组：`[6, 18, 4, 0.4444444444444444, 0.4090909090909091]`
- 正描述 2 选择元组：`[8, 20, 2, 0.7272727272727273, 0.7916666666666666]`
- 最终比较正描述：`positive_1` / "A snowboarder is flying in the air over snow."
- 完整 lexeme 编辑块：`[{"tag": "delete", "positive_start": 0, "positive_end": 1, "negative_start": 0, "negative_end": 0, "positive_lexemes": ["a"], "negative_lexemes": []}, {"tag": "replace", "positive_start": 1, "positive_end": 2, "negative_start": 0, "negative_end": 1, "positive_lexemes": ["snowboarder"], "negative_lexemes": ["snow"]}, {"tag": "equal", "positive_start": 2, "positive_end": 8, "negative_start": 1, "negative_end": 7, "positive_lexemes": ["is", "flying", "in", "the", "air", "over"], "negative_lexemes": ["is", "flying", "in", "the", "air", "over"]}, {"tag": "insert", "positive_start": 8, "positive_end": 8, "negative_start": 7, "negative_end": 8, "positive_lexemes": [], "negative_lexemes": ["a"]}, {"tag": "replace", "positive_start": 8, "positive_end": 9, "negative_start": 8, "negative_end": 9, "positive_lexemes": ["snow"], "negative_lexemes": ["snowboarder"]}]`
- 共同前缀：`[]`
- 正确 contrast hull：`["a", "snowboarder", "is", "flying", "in", "the", "air", "over", "snow"]`
- 错误 contrast hull：`["snow", "is", "flying", "in", "the", "air", "over", "a", "snowboarder"]`
- 共同后缀：`[]`
- Hull token 覆盖率（正/负/最大）：`[1.0, 1.0, 1.0]`
- 共同前缀模型 token：`[]`
- 正确 hull 模型 token：IDs `[100, 316, 1103, 101, 114, 1433, 311, 395, 341, 542, 350, 353, 309, 3980, 2141, 316, 1103]`；text "a snowboarder is flying in the air over snow"
- 错误 hull 模型 token：IDs `[118, 1103, 395, 341, 542, 350, 353, 309, 3980, 2141, 299, 316, 1103, 101, 114, 1433, 311]`；text "snow is flying in the air over a snowboarder"
- 第一轮/第二轮分类：`complex_edit` / `whole_sentence_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；"at_least_one_hull_covers_all_model_tokens"

### 29. `swap_object:63`

- 负例类型/范围：`swap_object` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A person in a white shirt and gray pants walks toward a grassy area as kids in baseball uniforms and an umpire are near him."
- 原始正描述 2："kids in baseball uniforms and an umpire are close to a person wearing gray pants and white shirt walks toward a grassy area."
- 原始负描述："Kids in a white shirt and gray pants walk toward a grassy area as a person in baseball uniforms and an umpire are near them."
- 规范化正描述 1："a person in a white shirt and gray pants walks toward a grassy area as kids in baseball uniforms and an umpire are near him"
- 规范化正描述 2："kids in baseball uniforms and an umpire are close to a person wearing gray pants and white shirt walks toward a grassy area"
- 规范化负描述："kids in a white shirt and gray pants walk toward a grassy area as a person in baseball uniforms and an umpire are near them"
- 正描述 1 选择元组：`[10, 50, 6, 0.24, 0.13821138211382114]`
- 正描述 2 选择元组：`[36, 44, 7, 0.84, 0.6991869918699187]`
- 最终比较正描述：`positive_1` / "A person in a white shirt and gray pants walks toward a grassy area as kids in baseball uniforms and an umpire are near him."
- 完整 lexeme 编辑块：`[{"tag": "delete", "positive_start": 0, "positive_end": 1, "negative_start": 0, "negative_end": 0, "positive_lexemes": ["a"], "negative_lexemes": []}, {"tag": "replace", "positive_start": 1, "positive_end": 2, "negative_start": 0, "negative_end": 1, "positive_lexemes": ["person"], "negative_lexemes": ["kids"]}, {"tag": "equal", "positive_start": 2, "positive_end": 9, "negative_start": 1, "negative_end": 8, "positive_lexemes": ["in", "a", "white", "shirt", "and", "gray", "pants"], "negative_lexemes": ["in", "a", "white", "shirt", "and", "gray", "pants"]}, {"tag": "replace", "positive_start": 9, "positive_end": 10, "negative_start": 8, "negative_end": 9, "positive_lexemes": ["walks"], "negative_lexemes": ["walk"]}, {"tag": "equal", "positive_start": 10, "positive_end": 15, "negative_start": 9, "negative_end": 14, "positive_lexemes": ["toward", "a", "grassy", "area", "as"], "negative_lexemes": ["toward", "a", "grassy", "area", "as"]}, {"tag": "insert", "positive_start": 15, "positive_end": 15, "negative_start": 14, "negative_end": 15, "positive_lexemes": [], "negative_lexemes": ["a"]}, {"tag": "replace", "positive_start": 15, "positive_end": 16, "negative_start": 15, "negative_end": 16, "positive_lexemes": ["kids"], "negative_lexemes": ["person"]}, {"tag": "equal", "positive_start": 16, "positive_end": 24, "negative_start": 16, "negative_end": 24, "positive_lexemes": ["in", "baseball", "uniforms", "and", "an", "umpire", "are", "near"], "negative_lexemes": ["in", "baseball", "uniforms", "and", "an", "umpire", "are", "near"]}, {"tag": "replace", "positive_start": 24, "positive_end": 25, "negative_start": 24, "negative_end": 25, "positive_lexemes": ["him"], "negative_lexemes": ["them"]}]`
- 共同前缀：`[]`
- 正确 contrast hull：`["a", "person", "in", "a", "white", "shirt", "and", "gray", "pants", "walks", "toward", "a", "grassy", "area", "as", "kids", "in", "baseball", "uniforms", "and", "an", "umpire", "are", "near", "him"]`
- 错误 contrast hull：`["kids", "in", "a", "white", "shirt", "and", "gray", "pants", "walk", "toward", "a", "grassy", "area", "as", "a", "person", "in", "baseball", "uniforms", "and", "an", "umpire", "are", "near", "them"]`
- 共同后缀：`[]`
- Hull token 覆盖率（正/负/最大）：`[1.0, 1.0, 1.0]`
- 共同前缀模型 token：`[]`
- 正确 hull 模型 token：IDs `[100, 2198, 353, 299, 654, 1078, 1128, 4193, 376, 492, 1982, 344, 5483, 339, 352, 1275, 364, 3588, 299, 492, 117, 1388, 124, 2808, 523, 914, 460, 118, 353, 4933, 101, 1266, 1406, 507, 5713, 118, 376, 346, 256, 457, 115, 1475, 732, 730, 370, 429, 467]`；text "a person in a white shirt and gray pants walks toward a grassy area as kids in baseball uniforms and an umpire are near him"
- 错误 hull 模型 token：IDs `[110, 460, 118, 353, 299, 654, 1078, 1128, 4193, 376, 492, 1982, 344, 5483, 339, 5864, 364, 3588, 299, 492, 117, 1388, 124, 2808, 523, 299, 2198, 353, 4933, 101, 1266, 1406, 507, 5713, 118, 376, 346, 256, 457, 115, 1475, 732, 730, 370, 2105]`；text "kids in a white shirt and gray pants walk toward a grassy area as a person in baseball uniforms and an umpire are near them"
- 第一轮/第二轮分类：`complex_edit` / `whole_sentence_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；"at_least_one_hull_covers_all_model_tokens"

### 30. `swap_object:87`

- 负例类型/范围：`swap_object` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："Many children sit around a person in a Santa costume."
- 原始正描述 2："A person is in a Santa costume and is surrounded by many children who are sitting."
- 原始负描述："A person in a Santa costume sits around many children."
- 规范化正描述 1："many children sit around a person in a santa costume"
- 规范化正描述 2："a person is in a santa costume and is surrounded by many children who are sitting"
- 规范化负描述："a person in a santa costume sits around many children"
- 正描述 1 选择元组：`[8, 20, 2, 0.8, 0.7735849056603774]`
- 正描述 2 选择元组：`[10, 22, 4, 0.5, 0.3950617283950617]`
- 最终比较正描述：`positive_1` / "Many children sit around a person in a Santa costume."
- 完整 lexeme 编辑块：`[{"tag": "delete", "positive_start": 0, "positive_end": 4, "negative_start": 0, "negative_end": 0, "positive_lexemes": ["many", "children", "sit", "around"], "negative_lexemes": []}, {"tag": "equal", "positive_start": 4, "positive_end": 10, "negative_start": 0, "negative_end": 6, "positive_lexemes": ["a", "person", "in", "a", "santa", "costume"], "negative_lexemes": ["a", "person", "in", "a", "santa", "costume"]}, {"tag": "insert", "positive_start": 10, "positive_end": 10, "negative_start": 6, "negative_end": 10, "positive_lexemes": [], "negative_lexemes": ["sits", "around", "many", "children"]}]`
- 共同前缀：`[]`
- 正确 contrast hull：`["many", "children", "sit", "around", "a", "person", "in", "a", "santa", "costume"]`
- 错误 contrast hull：`["a", "person", "in", "a", "santa", "costume", "sits", "around", "many", "children"]`
- 共同后缀：`[]`
- Hull token 覆盖率（正/负/最大）：`[1.0, 1.0, 1.0]`
- 共同前缀模型 token：`[]`
- 正确 hull 模型 token：IDs `[5257, 124, 6109, 3193, 5305, 3364, 299, 2198, 353, 299, 316, 811, 100, 3756, 4557]`；text "many children sit around a person in a santa costume"
- 错误 hull 模型 token：IDs `[100, 2198, 353, 299, 316, 811, 100, 3756, 4557, 316, 2163, 3364, 2547, 6109, 3193]`；text "a person in a santa costume sits around many children"
- 第一轮/第二轮分类：`complex_edit` / `whole_sentence_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；"at_least_one_hull_covers_all_model_tokens"

## swap_atribute

候选 `666` 条，本节抽取 `30` 条。

### 1. `swap_atribute:147`

- 负例类型/范围：`swap_atribute` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："Brown and black dog sitting on the brown couch by itself."
- 原始正描述 2："The dog, which is brown and black, is sitting on the brown couch by itself."
- 原始负描述："Black and brown dog sitting on the black couch by itself."
- 规范化正描述 1："brown and black dog sitting on the brown couch by itself"
- 规范化正描述 2："the dog , which is brown and black , is sitting on the brown couch by itself"
- 规范化负描述："black and brown dog sitting on the black couch by itself"
- 正描述 1 选择元组：`[6, 16, 3, 0.2727272727272727, 0.21428571428571427]`
- 正描述 2 选择元组：`[14, 22, 5, 0.5882352941176471, 0.4473684210526316]`
- 最终比较正描述：`positive_1` / "Brown and black dog sitting on the brown couch by itself."
- 完整 lexeme 编辑块：`[{"tag": "replace", "positive_start": 0, "positive_end": 1, "negative_start": 0, "negative_end": 1, "positive_lexemes": ["brown"], "negative_lexemes": ["black"]}, {"tag": "equal", "positive_start": 1, "positive_end": 2, "negative_start": 1, "negative_end": 2, "positive_lexemes": ["and"], "negative_lexemes": ["and"]}, {"tag": "replace", "positive_start": 2, "positive_end": 3, "negative_start": 2, "negative_end": 3, "positive_lexemes": ["black"], "negative_lexemes": ["brown"]}, {"tag": "equal", "positive_start": 3, "positive_end": 7, "negative_start": 3, "negative_end": 7, "positive_lexemes": ["dog", "sitting", "on", "the"], "negative_lexemes": ["dog", "sitting", "on", "the"]}, {"tag": "replace", "positive_start": 7, "positive_end": 8, "negative_start": 7, "negative_end": 8, "positive_lexemes": ["brown"], "negative_lexemes": ["black"]}, {"tag": "equal", "positive_start": 8, "positive_end": 11, "negative_start": 8, "negative_end": 11, "positive_lexemes": ["couch", "by", "itself"], "negative_lexemes": ["couch", "by", "itself"]}]`
- 共同前缀：`[]`
- 正确 contrast hull：`["brown", "and", "black", "dog", "sitting", "on", "the", "brown"]`
- 错误 contrast hull：`["black", "and", "brown", "dog", "sitting", "on", "the", "black"]`
- 共同后缀：`["couch", "by", "itself"]`
- Hull token 覆盖率（正/负/最大）：`[0.7142857142857143, 0.7142857142857143, 0.7142857142857143]`
- 共同前缀模型 token：`[]`
- 正确 hull 模型 token：IDs `[101, 2079, 113, 376, 2597, 1637, 1041, 106, 5305, 2912, 619, 309, 363, 2079, 113]`；text "brown and black dog sitting on the brown"
- 错误 hull 模型 token：IDs `[101, 111, 1637, 376, 363, 2079, 113, 1041, 106, 5305, 2912, 619, 309, 2597, 1637]`；text "black and brown dog sitting on the black"
- 第一轮/第二轮分类：`complex_edit` / `multi_block_local_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 2. `swap_atribute:173`

- 负例类型/范围：`swap_atribute` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："Cows are grazing in a wet pasture with birds."
- 原始正描述 2："The cows are grazing in a wet pasture with birds."
- 原始负描述："Cows are grazing in a pasture with wet birds."
- 规范化正描述 1："cows are grazing in a wet pasture with birds"
- 规范化正描述 2："the cows are grazing in a wet pasture with birds"
- 规范化负描述："cows are grazing in a pasture with wet birds"
- 正描述 1 选择元组：`[2, 6, 2, 0.2222222222222222, 0.18181818181818182]`
- 正描述 2 选择元组：`[3, 17, 3, 0.3, 0.25]`
- 最终比较正描述：`positive_1` / "Cows are grazing in a wet pasture with birds."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 5, "negative_start": 0, "negative_end": 5, "positive_lexemes": ["cows", "are", "grazing", "in", "a"], "negative_lexemes": ["cows", "are", "grazing", "in", "a"]}, {"tag": "delete", "positive_start": 5, "positive_end": 6, "negative_start": 5, "negative_end": 5, "positive_lexemes": ["wet"], "negative_lexemes": []}, {"tag": "equal", "positive_start": 6, "positive_end": 8, "negative_start": 5, "negative_end": 7, "positive_lexemes": ["pasture", "with"], "negative_lexemes": ["pasture", "with"]}, {"tag": "insert", "positive_start": 8, "positive_end": 8, "negative_start": 7, "negative_end": 8, "positive_lexemes": [], "negative_lexemes": ["wet"]}, {"tag": "equal", "positive_start": 8, "positive_end": 9, "negative_start": 8, "negative_end": 9, "positive_lexemes": ["birds"], "negative_lexemes": ["birds"]}]`
- 共同前缀：`["cows", "are", "grazing", "in", "a"]`
- 正确 contrast hull：`["wet", "pasture", "with"]`
- 错误 contrast hull：`["pasture", "with", "wet"]`
- 共同后缀：`["birds"]`
- Hull token 覆盖率（正/负/最大）：`[0.375, 0.375, 0.375]`
- 共同前缀模型 token：`[102, 3032, 732, 5528, 125, 350, 353, 299]`
- 正确 hull 模型 token：IDs `[339, 439, 344, 1154, 745, 599]`；text " wet pasture with"
- 错误 hull 模型 token：IDs `[344, 1154, 745, 599, 339, 439]`；text " pasture with wet"
- 第一轮/第二轮分类：`complex_edit` / `multi_block_local_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 3. `swap_atribute:205`

- 负例类型/范围：`swap_atribute` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A tower of a gray and white building has a weather vane and two clocks."
- 原始正描述 2："The gray and white building has a tower with a weather vane and two clocks positioned on top of it."
- 原始负描述："A tower of a gray and white building has two weather vanes and a clock."
- 规范化正描述 1："a tower of a gray and white building has a weather vane and two clocks"
- 规范化正描述 2："the gray and white building has a tower with a weather vane and two clocks positioned on top of it"
- 规范化负描述："a tower of a gray and white building has two weather vanes and a clock"
- 正描述 1 选择元组：`[8, 12, 3, 0.26666666666666666, 0.11428571428571428]`
- 正描述 2 选择元组：`[21, 35, 7, 0.8, 0.5204081632653061]`
- 最终比较正描述：`positive_1` / "A tower of a gray and white building has a weather vane and two clocks."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 9, "negative_start": 0, "negative_end": 9, "positive_lexemes": ["a", "tower", "of", "a", "gray", "and", "white", "building", "has"], "negative_lexemes": ["a", "tower", "of", "a", "gray", "and", "white", "building", "has"]}, {"tag": "replace", "positive_start": 9, "positive_end": 10, "negative_start": 9, "negative_end": 10, "positive_lexemes": ["a"], "negative_lexemes": ["two"]}, {"tag": "equal", "positive_start": 10, "positive_end": 11, "negative_start": 10, "negative_end": 11, "positive_lexemes": ["weather"], "negative_lexemes": ["weather"]}, {"tag": "replace", "positive_start": 11, "positive_end": 12, "negative_start": 11, "negative_end": 12, "positive_lexemes": ["vane"], "negative_lexemes": ["vanes"]}, {"tag": "equal", "positive_start": 12, "positive_end": 13, "negative_start": 12, "negative_end": 13, "positive_lexemes": ["and"], "negative_lexemes": ["and"]}, {"tag": "replace", "positive_start": 13, "positive_end": 15, "negative_start": 13, "negative_end": 15, "positive_lexemes": ["two", "clocks"], "negative_lexemes": ["a", "clock"]}]`
- 共同前缀：`["a", "tower", "of", "a", "gray", "and", "white", "building", "has"]`
- 正确 contrast hull：`["a", "weather", "vane", "and", "two", "clocks"]`
- 错误 contrast hull：`["two", "weather", "vanes", "and", "a", "clock"]`
- 共同后缀：`[]`
- Hull token 覆盖率（正/负/最大）：`[0.391304347826087, 0.391304347826087, 0.391304347826087]`
- 共同前缀模型 token：`[100, 364, 122, 311, 354, 299, 492, 1982, 376, 654, 1078, 6331, 350, 1290]`
- 正确 hull 模型 token：IDs `[299, 2730, 603, 4875, 376, 2102, 4414, 892, 118]`；text " a weather vane and two clocks"
- 错误 hull 模型 token：IDs `[2102, 2730, 603, 325, 329, 376, 299, 4414, 892]`；text " two weather vanes and a clock"
- 第一轮/第二轮分类：`complex_edit` / `multi_block_local_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 4. `swap_atribute:241`

- 负例类型/范围：`swap_atribute` / `{"canonical": true, "pilot": true, "formal": false, "certifying_formal": false}`
- 原始正描述 1："A view of a store that sells teddy bears. There is a huge display in the window."
- 原始正描述 2："A store that sells teddy bears is visible in the view. The display in the window is enormous."
- 原始负描述："A view of a store that sells huge bears. There is not a teddy display in the window."
- 规范化正描述 1："a view of a store that sells teddy bears . there is a huge display in the window"
- 规范化正描述 2："a store that sells teddy bears is visible in the view . the display in the window is enormous"
- 规范化负描述："a view of a store that sells huge bears . there is not a teddy display in the window"
- 正描述 1 选择元组：`[5, 15, 3, 0.15789473684210525, 0.16666666666666666]`
- 正描述 2 选择元组：`[20, 38, 5, 0.6842105263157895, 0.5161290322580645]`
- 最终比较正描述：`positive_1` / "A view of a store that sells teddy bears. There is a huge display in the window."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 7, "negative_start": 0, "negative_end": 7, "positive_lexemes": ["a", "view", "of", "a", "store", "that", "sells"], "negative_lexemes": ["a", "view", "of", "a", "store", "that", "sells"]}, {"tag": "replace", "positive_start": 7, "positive_end": 8, "negative_start": 7, "negative_end": 8, "positive_lexemes": ["teddy"], "negative_lexemes": ["huge"]}, {"tag": "equal", "positive_start": 8, "positive_end": 12, "negative_start": 8, "negative_end": 12, "positive_lexemes": ["bears", ".", "there", "is"], "negative_lexemes": ["bears", ".", "there", "is"]}, {"tag": "insert", "positive_start": 12, "positive_end": 12, "negative_start": 12, "negative_end": 13, "positive_lexemes": [], "negative_lexemes": ["not"]}, {"tag": "equal", "positive_start": 12, "positive_end": 13, "negative_start": 13, "negative_end": 14, "positive_lexemes": ["a"], "negative_lexemes": ["a"]}, {"tag": "replace", "positive_start": 13, "positive_end": 14, "negative_start": 14, "negative_end": 15, "positive_lexemes": ["huge"], "negative_lexemes": ["teddy"]}, {"tag": "equal", "positive_start": 14, "positive_end": 18, "negative_start": 15, "negative_end": 19, "positive_lexemes": ["display", "in", "the", "window"], "negative_lexemes": ["display", "in", "the", "window"]}]`
- 共同前缀：`["a", "view", "of", "a", "store", "that", "sells"]`
- 正确 contrast hull：`["teddy", "bears", ".", "there", "is", "a", "huge"]`
- 错误 contrast hull：`["huge", "bears", ".", "there", "is", "not", "a", "teddy"]`
- 共同后缀：`["display", "in", "the", "window"]`
- Hull token 覆盖率（正/负/最大）：`[0.43333333333333335, 0.45161290322580644, 0.45161290322580644]`
- 共同前缀模型 token：`[100, 603, 1400, 122, 354, 299, 5074, 591, 316, 1272, 118]`
- 正确 hull 模型 token：IDs `[297, 382, 103, 124, 600, 2546, 6304, 1975, 395, 299, 429, 120, 583]`；text " teddy bears . there is a huge"
- 错误 hull 模型 token：IDs `[429, 120, 583, 600, 2546, 6304, 1975, 395, 1027, 299, 297, 382, 103, 124]`；text " huge bears . there is not a teddy"
- 第一轮/第二轮分类：`complex_edit` / `multi_block_local_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 5. `swap_atribute:248`

- 负例类型/范围：`swap_atribute` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："Several children watch while a child in a pink sweatshirt plays with a Wii remote while another person with a little child on their lap snuggle in a chair in the background."
- 原始正描述 2："A group of children observe as one child, clad in a pink sweatshirt, engages with a Wii remote. In the background, another individual cuddles a small child on their lap, seated in a chair."
- 原始负描述："Several children watch while a child in a little sweatshirt plays with a Wii remote while another person with a pink child on their lap snuggle in a chair in the background."
- 规范化正描述 1："several children watch while a child in a pink sweatshirt plays with a wii remote while another person with a little child on their lap snuggle in a chair in the background"
- 规范化正描述 2："a group of children observe as one child , clad in a pink sweatshirt , engages with a wii remote . in the background , another individual cuddles a small child on their lap , seated in a chair"
- 规范化负描述："several children watch while a child in a little sweatshirt plays with a wii remote while another person with a pink child on their lap snuggle in a chair in the background"
- 正描述 1 选择元组：`[4, 26, 2, 0.0625, 0.05813953488372093]`
- 正描述 2 选择元组：`[35, 71, 14, 0.6153846153846154, 0.5572916666666666]`
- 最终比较正描述：`positive_1` / "Several children watch while a child in a pink sweatshirt plays with a Wii remote while another person with a little child on their lap snuggle in a chair in the background."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 8, "negative_start": 0, "negative_end": 8, "positive_lexemes": ["several", "children", "watch", "while", "a", "child", "in", "a"], "negative_lexemes": ["several", "children", "watch", "while", "a", "child", "in", "a"]}, {"tag": "replace", "positive_start": 8, "positive_end": 9, "negative_start": 8, "negative_end": 9, "positive_lexemes": ["pink"], "negative_lexemes": ["little"]}, {"tag": "equal", "positive_start": 9, "positive_end": 20, "negative_start": 9, "negative_end": 20, "positive_lexemes": ["sweatshirt", "plays", "with", "a", "wii", "remote", "while", "another", "person", "with", "a"], "negative_lexemes": ["sweatshirt", "plays", "with", "a", "wii", "remote", "while", "another", "person", "with", "a"]}, {"tag": "replace", "positive_start": 20, "positive_end": 21, "negative_start": 20, "negative_end": 21, "positive_lexemes": ["little"], "negative_lexemes": ["pink"]}, {"tag": "equal", "positive_start": 21, "positive_end": 32, "negative_start": 21, "negative_end": 32, "positive_lexemes": ["child", "on", "their", "lap", "snuggle", "in", "a", "chair", "in", "the", "background"], "negative_lexemes": ["child", "on", "their", "lap", "snuggle", "in", "a", "chair", "in", "the", "background"]}]`
- 共同前缀：`["several", "children", "watch", "while", "a", "child", "in", "a"]`
- 正确 contrast hull：`["pink", "sweatshirt", "plays", "with", "a", "wii", "remote", "while", "another", "person", "with", "a", "little"]`
- 错误 contrast hull：`["little", "sweatshirt", "plays", "with", "a", "wii", "remote", "while", "another", "person", "with", "a", "pink"]`
- 共同后缀：`["child", "on", "their", "lap", "snuggle", "in", "a", "chair", "in", "the", "background"]`
- Hull token 覆盖率（正/负/最大）：`[0.4528301886792453, 0.4528301886792453, 0.4528301886792453]`
- 共同前缀模型 token：`[573, 652, 352, 6109, 3193, 339, 6131, 3052, 299, 6109, 353, 299]`
- 正确 hull 模型 token：IDs `[344, 3010, 316, 1747, 314, 3807, 4193, 1219, 2012, 599, 299, 339, 108, 108, 2428, 3850, 3052, 5467, 2198, 599, 299, 406, 338, 5395]`；text " pink sweatshirt plays with a wii remote while another person with a little"
- 错误 hull 模型 token：IDs `[406, 338, 5395, 316, 1747, 314, 3807, 4193, 1219, 2012, 599, 299, 339, 108, 108, 2428, 3850, 3052, 5467, 2198, 599, 299, 344, 3010]`；text " little sweatshirt plays with a wii remote while another person with a pink"
- 第一轮/第二轮分类：`complex_edit` / `multi_block_local_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 6. `swap_atribute:252`

- 负例类型/范围：`swap_atribute` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A grey motorcycle on dirt road next to a building."
- 原始正描述 2："A grey motorcycle is positioned on a dirt road adjacent to a building."
- 原始负描述："A dirt motorcycle on grey road next to a building."
- 规范化正描述 1："a grey motorcycle on dirt road next to a building"
- 规范化正描述 2："a grey motorcycle is positioned on a dirt road adjacent to a building"
- 规范化负描述："a dirt motorcycle on grey road next to a building"
- 正描述 1 选择元组：`[4, 8, 2, 0.2, 0.16326530612244897]`
- 正描述 2 选择元组：`[9, 15, 5, 0.46153846153846156, 0.43478260869565216]`
- 最终比较正描述：`positive_1` / "A grey motorcycle on dirt road next to a building."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 1, "negative_start": 0, "negative_end": 1, "positive_lexemes": ["a"], "negative_lexemes": ["a"]}, {"tag": "replace", "positive_start": 1, "positive_end": 2, "negative_start": 1, "negative_end": 2, "positive_lexemes": ["grey"], "negative_lexemes": ["dirt"]}, {"tag": "equal", "positive_start": 2, "positive_end": 4, "negative_start": 2, "negative_end": 4, "positive_lexemes": ["motorcycle", "on"], "negative_lexemes": ["motorcycle", "on"]}, {"tag": "replace", "positive_start": 4, "positive_end": 5, "negative_start": 4, "negative_end": 5, "positive_lexemes": ["dirt"], "negative_lexemes": ["grey"]}, {"tag": "equal", "positive_start": 5, "positive_end": 10, "negative_start": 5, "negative_end": 10, "positive_lexemes": ["road", "next", "to", "a", "building"], "negative_lexemes": ["road", "next", "to", "a", "building"]}]`
- 共同前缀：`["a"]`
- 正确 contrast hull：`["grey", "motorcycle", "on", "dirt"]`
- 错误 contrast hull：`["dirt", "motorcycle", "on", "grey"]`
- 共同后缀：`["road", "next", "to", "a", "building"]`
- Hull token 覆盖率（正/负/最大）：`[0.5555555555555556, 0.5555555555555556, 0.5555555555555556]`
- 共同前缀模型 token：`[100]`
- 正确 hull 模型 token：IDs `[2273, 124, 351, 593, 336, 2863, 2945, 619, 373, 4193]`；text " grey motorcycle on dirt"
- 错误 hull 模型 token：IDs `[373, 4193, 351, 593, 336, 2863, 2945, 619, 2273, 124]`；text " dirt motorcycle on grey"
- 第一轮/第二轮分类：`complex_edit` / `multi_block_local_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 7. `swap_atribute:261`

- 负例类型/范围：`swap_atribute` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A small vase of flowers sit on a wooden table near magazines."
- 原始正描述 2："A small vase of flowers is positioned on a wooden table near magazines."
- 原始负描述："A wooden vase of flowers sit on a small table near magazines."
- 规范化正描述 1："a small vase of flowers sit on a wooden table near magazines"
- 规范化正描述 2："a small vase of flowers is positioned on a wooden table near magazines"
- 规范化负描述："a wooden vase of flowers sit on a small table near magazines"
- 正描述 1 选择元组：`[4, 16, 2, 0.16666666666666666, 0.2]`
- 正描述 2 选择元组：`[7, 17, 4, 0.3076923076923077, 0.3142857142857143]`
- 最终比较正描述：`positive_1` / "A small vase of flowers sit on a wooden table near magazines."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 1, "negative_start": 0, "negative_end": 1, "positive_lexemes": ["a"], "negative_lexemes": ["a"]}, {"tag": "replace", "positive_start": 1, "positive_end": 2, "negative_start": 1, "negative_end": 2, "positive_lexemes": ["small"], "negative_lexemes": ["wooden"]}, {"tag": "equal", "positive_start": 2, "positive_end": 8, "negative_start": 2, "negative_end": 8, "positive_lexemes": ["vase", "of", "flowers", "sit", "on", "a"], "negative_lexemes": ["vase", "of", "flowers", "sit", "on", "a"]}, {"tag": "replace", "positive_start": 8, "positive_end": 9, "negative_start": 8, "negative_end": 9, "positive_lexemes": ["wooden"], "negative_lexemes": ["small"]}, {"tag": "equal", "positive_start": 9, "positive_end": 12, "negative_start": 9, "negative_end": 12, "positive_lexemes": ["table", "near", "magazines"], "negative_lexemes": ["table", "near", "magazines"]}]`
- 共同前缀：`["a"]`
- 正确 contrast hull：`["small", "vase", "of", "flowers", "sit", "on", "a", "wooden"]`
- 错误 contrast hull：`["wooden", "vase", "of", "flowers", "sit", "on", "a", "small"]`
- 共同后缀：`["table", "near", "magazines"]`
- Hull token 覆盖率（正/负/最大）：`[0.5714285714285714, 0.5714285714285714, 0.5714285714285714]`
- 共同前缀模型 token：`[100]`
- 正确 hull 模型 token：IDs `[3436, 603, 812, 354, 5652, 496, 5305, 619, 299, 339, 2166, 327]`；text " small vase of flowers sit on a wooden"
- 错误 hull 模型 token：IDs `[339, 2166, 327, 603, 812, 354, 5652, 496, 5305, 619, 299, 3436]`；text " wooden vase of flowers sit on a small"
- 第一轮/第二轮分类：`complex_edit` / `multi_block_local_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 8. `swap_atribute:281`

- 负例类型/范围：`swap_atribute` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A white toilet with a black seat on top of a tiled floor."
- 原始正描述 2："A black seat sits on top of a white toilet, which is positioned on a tiled floor."
- 原始负描述："A black toilet with a white seat on top of a tiled floor."
- 规范化正描述 1："a white toilet with a black seat on top of a tiled floor"
- 规范化正描述 2："a black seat sits on top of a white toilet , which is positioned on a tiled floor"
- 规范化负描述："a black toilet with a white seat on top of a tiled floor"
- 正描述 1 选择元组：`[4, 10, 2, 0.15384615384615385, 0.17857142857142858]`
- 正描述 2 选择元组：`[17, 21, 4, 0.6111111111111112, 0.49382716049382713]`
- 最终比较正描述：`positive_1` / "A white toilet with a black seat on top of a tiled floor."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 1, "negative_start": 0, "negative_end": 1, "positive_lexemes": ["a"], "negative_lexemes": ["a"]}, {"tag": "replace", "positive_start": 1, "positive_end": 2, "negative_start": 1, "negative_end": 2, "positive_lexemes": ["white"], "negative_lexemes": ["black"]}, {"tag": "equal", "positive_start": 2, "positive_end": 5, "negative_start": 2, "negative_end": 5, "positive_lexemes": ["toilet", "with", "a"], "negative_lexemes": ["toilet", "with", "a"]}, {"tag": "replace", "positive_start": 5, "positive_end": 6, "negative_start": 5, "negative_end": 6, "positive_lexemes": ["black"], "negative_lexemes": ["white"]}, {"tag": "equal", "positive_start": 6, "positive_end": 13, "negative_start": 6, "negative_end": 13, "positive_lexemes": ["seat", "on", "top", "of", "a", "tiled", "floor"], "negative_lexemes": ["seat", "on", "top", "of", "a", "tiled", "floor"]}]`
- 共同前缀：`["a"]`
- 正确 contrast hull：`["white", "toilet", "with", "a", "black"]`
- 错误 contrast hull：`["black", "toilet", "with", "a", "white"]`
- 共同后缀：`["seat", "on", "top", "of", "a", "tiled", "floor"]`
- Hull token 覆盖率（正/负/最大）：`[0.45, 0.45, 0.45]`
- 共同前缀模型 token：`[100]`
- 正确 hull 模型 token：IDs `[654, 1078, 364, 1299, 119, 599, 299, 2597, 1637]`；text " white toilet with a black"
- 错误 hull 模型 token：IDs `[2597, 1637, 364, 1299, 119, 599, 299, 654, 1078]`；text " black toilet with a white"
- 第一轮/第二轮分类：`complex_edit` / `multi_block_local_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 9. `swap_atribute:301`

- 负例类型/范围：`swap_atribute` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A bathroom has red walls with yellow accents."
- 原始正描述 2："The bathroom has yellow accents on red walls."
- 原始负描述："A bathroom has yellow walls with red accents."
- 规范化正描述 1："a bathroom has red walls with yellow accents"
- 规范化正描述 2："the bathroom has yellow accents on red walls"
- 规范化负描述："a bathroom has yellow walls with red accents"
- 正描述 1 选择元组：`[4, 8, 2, 0.25, 0.22727272727272727]`
- 正描述 2 选择元组：`[8, 16, 3, 0.5, 0.4318181818181818]`
- 最终比较正描述：`positive_1` / "A bathroom has red walls with yellow accents."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 3, "negative_start": 0, "negative_end": 3, "positive_lexemes": ["a", "bathroom", "has"], "negative_lexemes": ["a", "bathroom", "has"]}, {"tag": "replace", "positive_start": 3, "positive_end": 4, "negative_start": 3, "negative_end": 4, "positive_lexemes": ["red"], "negative_lexemes": ["yellow"]}, {"tag": "equal", "positive_start": 4, "positive_end": 6, "negative_start": 4, "negative_end": 6, "positive_lexemes": ["walls", "with"], "negative_lexemes": ["walls", "with"]}, {"tag": "replace", "positive_start": 6, "positive_end": 7, "negative_start": 6, "negative_end": 7, "positive_lexemes": ["yellow"], "negative_lexemes": ["red"]}, {"tag": "equal", "positive_start": 7, "positive_end": 8, "negative_start": 7, "negative_end": 8, "positive_lexemes": ["accents"], "negative_lexemes": ["accents"]}]`
- 共同前缀：`["a", "bathroom", "has"]`
- 正确 contrast hull：`["red", "walls", "with", "yellow"]`
- 错误 contrast hull：`["yellow", "walls", "with", "red"]`
- 共同后缀：`["accents"]`
- Hull token 覆盖率（正/负/最大）：`[0.5, 0.5, 0.5]`
- 共同前缀模型 token：`[100, 363, 1831, 393, 444, 1290]`
- 正确 hull 模型 token：IDs `[5534, 339, 1266, 118, 599, 385, 446, 1030]`；text " red walls with yellow"
- 错误 hull 模型 token：IDs `[385, 446, 1030, 339, 1266, 118, 599, 5534]`；text " yellow walls with red"
- 第一轮/第二轮分类：`complex_edit` / `multi_block_local_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 10. `swap_atribute:309`

- 负例类型/范围：`swap_atribute` / `{"canonical": true, "pilot": true, "formal": false, "certifying_formal": false}`
- 原始正描述 1："A clock sits above green bushes under a blue sky."
- 原始正描述 2："The clock is positioned above green bushes, which are situated under a blue sky."
- 原始负描述："A clock sits above blue bushes under a green sky."
- 规范化正描述 1："a clock sits above green bushes under a blue sky"
- 规范化正描述 2："the clock is positioned above green bushes , which are situated under a blue sky"
- 规范化负描述："a clock sits above blue bushes under a green sky"
- 正描述 1 选择元组：`[4, 10, 2, 0.2, 0.16666666666666666]`
- 正描述 2 选择元组：`[13, 23, 6, 0.6, 0.525]`
- 最终比较正描述：`positive_1` / "A clock sits above green bushes under a blue sky."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 4, "negative_start": 0, "negative_end": 4, "positive_lexemes": ["a", "clock", "sits", "above"], "negative_lexemes": ["a", "clock", "sits", "above"]}, {"tag": "replace", "positive_start": 4, "positive_end": 5, "negative_start": 4, "negative_end": 5, "positive_lexemes": ["green"], "negative_lexemes": ["blue"]}, {"tag": "equal", "positive_start": 5, "positive_end": 8, "negative_start": 5, "negative_end": 8, "positive_lexemes": ["bushes", "under", "a"], "negative_lexemes": ["bushes", "under", "a"]}, {"tag": "replace", "positive_start": 8, "positive_end": 9, "negative_start": 8, "negative_end": 9, "positive_lexemes": ["blue"], "negative_lexemes": ["green"]}, {"tag": "equal", "positive_start": 9, "positive_end": 10, "negative_start": 9, "negative_end": 10, "positive_lexemes": ["sky"], "negative_lexemes": ["sky"]}]`
- 共同前缀：`["a", "clock", "sits", "above"]`
- 正确 contrast hull：`["green", "bushes", "under", "a", "blue"]`
- 错误 contrast hull：`["blue", "bushes", "under", "a", "green"]`
- 共同后缀：`["sky"]`
- Hull token 覆盖率（正/负/最大）：`[0.46153846153846156, 0.46153846153846156, 0.46153846153846156]`
- 共同前缀模型 token：`[100, 4414, 892, 316, 2163, 6264]`
- 正确 hull 模型 token：IDs `[5921, 2499, 2470, 1943, 299, 4300]`；text " green bushes under a blue"
- 错误 hull 模型 token：IDs `[4300, 2499, 2470, 1943, 299, 5921]`；text " blue bushes under a green"
- 第一轮/第二轮分类：`complex_edit` / `multi_block_local_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 11. `swap_atribute:346`

- 负例类型/范围：`swap_atribute` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A person in a red shirt tossing a white frisbee."
- 原始正描述 2："A white frisbee is being tossed by a person in a red shirt."
- 原始负描述："A person in a white shirt tossing a red frisbee."
- 规范化正描述 1："a person in a red shirt tossing a white frisbee"
- 规范化正描述 2："a white frisbee is being tossed by a person in a red shirt"
- 规范化负描述："a person in a white shirt tossing a red frisbee"
- 正描述 1 选择元组：`[4, 10, 2, 0.2, 0.2127659574468085]`
- 正描述 2 选择元组：`[17, 21, 3, 0.7692307692307693, 0.6724137931034483]`
- 最终比较正描述：`positive_1` / "A person in a red shirt tossing a white frisbee."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 4, "negative_start": 0, "negative_end": 4, "positive_lexemes": ["a", "person", "in", "a"], "negative_lexemes": ["a", "person", "in", "a"]}, {"tag": "replace", "positive_start": 4, "positive_end": 5, "negative_start": 4, "negative_end": 5, "positive_lexemes": ["red"], "negative_lexemes": ["white"]}, {"tag": "equal", "positive_start": 5, "positive_end": 8, "negative_start": 5, "negative_end": 8, "positive_lexemes": ["shirt", "tossing", "a"], "negative_lexemes": ["shirt", "tossing", "a"]}, {"tag": "replace", "positive_start": 8, "positive_end": 9, "negative_start": 8, "negative_end": 9, "positive_lexemes": ["white"], "negative_lexemes": ["red"]}, {"tag": "equal", "positive_start": 9, "positive_end": 10, "negative_start": 9, "negative_end": 10, "positive_lexemes": ["frisbee"], "negative_lexemes": ["frisbee"]}]`
- 共同前缀：`["a", "person", "in", "a"]`
- 正确 contrast hull：`["red", "shirt", "tossing", "a", "white"]`
- 错误 contrast hull：`["white", "shirt", "tossing", "a", "red"]`
- 共同后缀：`["frisbee"]`
- Hull token 覆盖率（正/负/最大）：`[0.5, 0.5, 0.5]`
- 共同前缀模型 token：`[100, 2198, 353, 299]`
- 正确 hull 模型 token：IDs `[5534, 1128, 4193, 364, 1843, 350, 299, 654, 1078]`；text " red shirt tossing a white"
- 错误 hull 模型 token：IDs `[654, 1078, 1128, 4193, 364, 1843, 350, 299, 5534]`；text " white shirt tossing a red"
- 第一轮/第二轮分类：`complex_edit` / `multi_block_local_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 12. `swap_atribute:347`

- 负例类型/范围：`swap_atribute` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A person in blue sweater holding two cellphones while wearing headphones."
- 原始正描述 2："A person in a blue sweater is holding two cellphones while wearing headphones."
- 原始负描述："A person holding two blue cellphones while wearing headphones."
- 规范化正描述 1："a person in blue sweater holding two cellphones while wearing headphones"
- 规范化正描述 2："a person in a blue sweater is holding two cellphones while wearing headphones"
- 规范化负描述："a person holding two blue cellphones while wearing headphones"
- 正描述 1 选择元组：`[4, 8, 2, 0.36363636363636365, 0.2916666666666667]`
- 正描述 2 选择元组：`[8, 10, 2, 0.46153846153846156, 0.33766233766233766]`
- 最终比较正描述：`positive_1` / "A person in blue sweater holding two cellphones while wearing headphones."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 2, "negative_start": 0, "negative_end": 2, "positive_lexemes": ["a", "person"], "negative_lexemes": ["a", "person"]}, {"tag": "delete", "positive_start": 2, "positive_end": 5, "negative_start": 2, "negative_end": 2, "positive_lexemes": ["in", "blue", "sweater"], "negative_lexemes": []}, {"tag": "equal", "positive_start": 5, "positive_end": 7, "negative_start": 2, "negative_end": 4, "positive_lexemes": ["holding", "two"], "negative_lexemes": ["holding", "two"]}, {"tag": "insert", "positive_start": 7, "positive_end": 7, "negative_start": 4, "negative_end": 5, "positive_lexemes": [], "negative_lexemes": ["blue"]}, {"tag": "equal", "positive_start": 7, "positive_end": 11, "negative_start": 5, "negative_end": 9, "positive_lexemes": ["cellphones", "while", "wearing", "headphones"], "negative_lexemes": ["cellphones", "while", "wearing", "headphones"]}]`
- 共同前缀：`["a", "person"]`
- 正确 contrast hull：`["in", "blue", "sweater", "holding", "two"]`
- 错误 contrast hull：`["holding", "two", "blue"]`
- 共同后缀：`["cellphones", "while", "wearing", "headphones"]`
- Hull token 覆盖率（正/负/最大）：`[0.36, 0.23809523809523808, 0.36]`
- 共同前缀模型 token：`[100, 2198]`
- 正确 hull 模型 token：IDs `[353, 4300, 316, 1747, 2137, 429, 2569, 350, 2102]`；text " in blue sweater holding two"
- 错误 hull 模型 token：IDs `[429, 2569, 350, 2102, 4300]`；text " holding two blue"
- 第一轮/第二轮分类：`complex_edit` / `multi_block_local_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 13. `swap_atribute:351`

- 负例类型/范围：`swap_atribute` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A black dog running with a red round frisbee."
- 原始正描述 2："A black dog runs, clutching a red, round frisbee in its mouth."
- 原始负描述："A red dog running with a black round frisbee."
- 规范化正描述 1："a black dog running with a red round frisbee"
- 规范化正描述 2："a black dog runs , clutching a red , round frisbee in its mouth"
- 规范化负描述："a red dog running with a black round frisbee"
- 正描述 1 选择元组：`[4, 12, 2, 0.2222222222222222, 0.22727272727272727]`
- 正描述 2 选择元组：`[13, 21, 6, 0.6428571428571429, 0.5396825396825397]`
- 最终比较正描述：`positive_1` / "A black dog running with a red round frisbee."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 1, "negative_start": 0, "negative_end": 1, "positive_lexemes": ["a"], "negative_lexemes": ["a"]}, {"tag": "replace", "positive_start": 1, "positive_end": 2, "negative_start": 1, "negative_end": 2, "positive_lexemes": ["black"], "negative_lexemes": ["red"]}, {"tag": "equal", "positive_start": 2, "positive_end": 6, "negative_start": 2, "negative_end": 6, "positive_lexemes": ["dog", "running", "with", "a"], "negative_lexemes": ["dog", "running", "with", "a"]}, {"tag": "replace", "positive_start": 6, "positive_end": 7, "negative_start": 6, "negative_end": 7, "positive_lexemes": ["red"], "negative_lexemes": ["black"]}, {"tag": "equal", "positive_start": 7, "positive_end": 9, "negative_start": 7, "negative_end": 9, "positive_lexemes": ["round", "frisbee"], "negative_lexemes": ["round", "frisbee"]}]`
- 共同前缀：`["a"]`
- 正确 contrast hull：`["black", "dog", "running", "with", "a", "red"]`
- 错误 contrast hull：`["red", "dog", "running", "with", "a", "black"]`
- 共同后缀：`["round", "frisbee"]`
- Hull token 覆盖率（正/负/最大）：`[0.5294117647058824, 0.5294117647058824, 0.5294117647058824]`
- 共同前缀模型 token：`[100]`
- 正确 hull 模型 token：IDs `[2597, 1637, 1041, 106, 3161, 1795, 599, 299, 5534]`；text " black dog running with a red"
- 错误 hull 模型 token：IDs `[5534, 1041, 106, 3161, 1795, 599, 299, 2597, 1637]`；text " red dog running with a black"
- 第一轮/第二轮分类：`complex_edit` / `multi_block_local_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 14. `swap_atribute:360`

- 负例类型/范围：`swap_atribute` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A cow standing next to a white wall and bright blue door."
- 原始正描述 2："A white wall and bright blue door are positioned next to a cow."
- 原始负描述："A cow standing next to a bright blue wall and white door."
- 规范化正描述 1："a cow standing next to a white wall and bright blue door"
- 规范化正描述 2："a white wall and bright blue door are positioned next to a cow"
- 规范化负描述："a cow standing next to a bright blue wall and white door"
- 正描述 1 选择元组：`[6, 10, 4, 0.3333333333333333, 0.2857142857142857]`
- 正描述 2 选择元组：`[23, 23, 2, 0.9230769230769231, 0.6774193548387096]`
- 最终比较正描述：`positive_1` / "A cow standing next to a white wall and bright blue door."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 6, "negative_start": 0, "negative_end": 6, "positive_lexemes": ["a", "cow", "standing", "next", "to", "a"], "negative_lexemes": ["a", "cow", "standing", "next", "to", "a"]}, {"tag": "insert", "positive_start": 6, "positive_end": 6, "negative_start": 6, "negative_end": 7, "positive_lexemes": [], "negative_lexemes": ["bright"]}, {"tag": "replace", "positive_start": 6, "positive_end": 7, "negative_start": 7, "negative_end": 8, "positive_lexemes": ["white"], "negative_lexemes": ["blue"]}, {"tag": "equal", "positive_start": 7, "positive_end": 9, "negative_start": 8, "negative_end": 10, "positive_lexemes": ["wall", "and"], "negative_lexemes": ["wall", "and"]}, {"tag": "delete", "positive_start": 9, "positive_end": 10, "negative_start": 10, "negative_end": 10, "positive_lexemes": ["bright"], "negative_lexemes": []}, {"tag": "replace", "positive_start": 10, "positive_end": 11, "negative_start": 10, "negative_end": 11, "positive_lexemes": ["blue"], "negative_lexemes": ["white"]}, {"tag": "equal", "positive_start": 11, "positive_end": 12, "negative_start": 11, "negative_end": 12, "positive_lexemes": ["door"], "negative_lexemes": ["door"]}]`
- 共同前缀：`["a", "cow", "standing", "next", "to", "a"]`
- 正确 contrast hull：`["white", "wall", "and", "bright", "blue"]`
- 错误 contrast hull：`["bright", "blue", "wall", "and", "white"]`
- 共同后缀：`["door"]`
- Hull token 覆盖率（正/负/最大）：`[0.4444444444444444, 0.4444444444444444, 0.4444444444444444]`
- 共同前缀模型 token：`[100, 317, 451, 2823, 350, 4658, 364, 299]`
- 正确 hull 模型 token：IDs `[654, 1078, 339, 1266, 376, 3461, 774, 4300]`；text " white wall and bright blue"
- 错误 hull 模型 token：IDs `[3461, 774, 4300, 339, 1266, 376, 654, 1078]`；text " bright blue wall and white"
- 第一轮/第二轮分类：`complex_edit` / `multi_block_local_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 15. `swap_atribute:394`

- 负例类型/范围：`swap_atribute` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A wooden table with a purple laptop and orange pen."
- 原始正描述 2："A table made of wood with a laptop that is purple and a pen that is orange on it."
- 原始负描述："A wooden table with an orange laptop and purple pen."
- 规范化正描述 1："a wooden table with a purple laptop and orange pen"
- 规范化正描述 2："a table made of wood with a laptop that is purple and a pen that is orange on it"
- 规范化负描述："a wooden table with an orange laptop and purple pen"
- 正描述 1 选择元组：`[6, 10, 2, 0.3, 0.21568627450980393]`
- 正描述 2 选择元组：`[21, 27, 6, 0.7894736842105263, 0.675]`
- 最终比较正描述：`positive_1` / "A wooden table with a purple laptop and orange pen."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 4, "negative_start": 0, "negative_end": 4, "positive_lexemes": ["a", "wooden", "table", "with"], "negative_lexemes": ["a", "wooden", "table", "with"]}, {"tag": "replace", "positive_start": 4, "positive_end": 6, "negative_start": 4, "negative_end": 6, "positive_lexemes": ["a", "purple"], "negative_lexemes": ["an", "orange"]}, {"tag": "equal", "positive_start": 6, "positive_end": 8, "negative_start": 6, "negative_end": 8, "positive_lexemes": ["laptop", "and"], "negative_lexemes": ["laptop", "and"]}, {"tag": "replace", "positive_start": 8, "positive_end": 9, "negative_start": 8, "negative_end": 9, "positive_lexemes": ["orange"], "negative_lexemes": ["purple"]}, {"tag": "equal", "positive_start": 9, "positive_end": 10, "negative_start": 9, "negative_end": 10, "positive_lexemes": ["pen"], "negative_lexemes": ["pen"]}]`
- 共同前缀：`["a", "wooden", "table", "with"]`
- 正确 contrast hull：`["a", "purple", "laptop", "and", "orange"]`
- 错误 contrast hull：`["an", "orange", "laptop", "and", "purple"]`
- 共同后缀：`["pen"]`
- Hull token 覆盖率（正/负/最大）：`[0.5294117647058824, 0.5294117647058824, 0.5294117647058824]`
- 共同前缀模型 token：`[100, 339, 2166, 327, 2630, 599]`
- 正确 hull 模型 token：IDs `[299, 3315, 833, 3090, 875, 1506, 376, 522, 1285]`；text " a purple laptop and orange"
- 错误 hull 模型 token：IDs `[346, 522, 1285, 3090, 875, 1506, 376, 3315, 833]`；text " an orange laptop and purple"
- 第一轮/第二轮分类：`complex_edit` / `multi_block_local_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 16. `swap_atribute:409`

- 负例类型/范围：`swap_atribute` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A person sitting at a wooden bench and table with an open umbrella sitting on the table."
- 原始正描述 2："A person is seated on a wooden bench and table with an open umbrella positioned on the table."
- 原始负描述："A person sitting at an open bench and table with a wooden umbrella sitting on the table."
- 规范化正描述 1："a person sitting at a wooden bench and table with an open umbrella sitting on the table"
- 规范化正描述 2："a person is seated on a wooden bench and table with an open umbrella positioned on the table"
- 规范化负描述："a person sitting at an open bench and table with a wooden umbrella sitting on the table"
- 正描述 1 选择元组：`[8, 16, 2, 0.23529411764705882, 0.09195402298850575]`
- 正描述 2 选择元组：`[15, 25, 4, 0.4444444444444444, 0.2608695652173913]`
- 最终比较正描述：`positive_1` / "A person sitting at a wooden bench and table with an open umbrella sitting on the table."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 4, "negative_start": 0, "negative_end": 4, "positive_lexemes": ["a", "person", "sitting", "at"], "negative_lexemes": ["a", "person", "sitting", "at"]}, {"tag": "replace", "positive_start": 4, "positive_end": 6, "negative_start": 4, "negative_end": 6, "positive_lexemes": ["a", "wooden"], "negative_lexemes": ["an", "open"]}, {"tag": "equal", "positive_start": 6, "positive_end": 10, "negative_start": 6, "negative_end": 10, "positive_lexemes": ["bench", "and", "table", "with"], "negative_lexemes": ["bench", "and", "table", "with"]}, {"tag": "replace", "positive_start": 10, "positive_end": 12, "negative_start": 10, "negative_end": 12, "positive_lexemes": ["an", "open"], "negative_lexemes": ["a", "wooden"]}, {"tag": "equal", "positive_start": 12, "positive_end": 17, "negative_start": 12, "negative_end": 17, "positive_lexemes": ["umbrella", "sitting", "on", "the", "table"], "negative_lexemes": ["umbrella", "sitting", "on", "the", "table"]}]`
- 共同前缀：`["a", "person", "sitting", "at"]`
- 正确 contrast hull：`["a", "wooden", "bench", "and", "table", "with", "an", "open"]`
- 错误 contrast hull：`["an", "open", "bench", "and", "table", "with", "a", "wooden"]`
- 共同后缀：`["umbrella", "sitting", "on", "the", "table"]`
- Hull token 覆盖率（正/负/最大）：`[0.4230769230769231, 0.4230769230769231, 0.4230769230769231]`
- 共同前缀模型 token：`[100, 2198, 5305, 2912, 1248]`
- 正确 hull 模型 token：IDs `[299, 339, 2166, 327, 6141, 550, 376, 2630, 599, 346, 5102]`；text " a wooden bench and table with an open"
- 错误 hull 模型 token：IDs `[346, 5102, 6141, 550, 376, 2630, 599, 299, 339, 2166, 327]`；text " an open bench and table with a wooden"
- 第一轮/第二轮分类：`complex_edit` / `multi_block_local_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 17. `swap_atribute:433`

- 负例类型/范围：`swap_atribute` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："Different platters of food are set in the kitchen."
- 原始正描述 2："Different platters of food are arranged in the kitchen."
- 原始负描述："Platters of food are set in different kitchens."
- 规范化正描述 1："different platters of food are set in the kitchen"
- 规范化正描述 2："different platters of food are arranged in the kitchen"
- 规范化负描述："platters of food are set in different kitchens"
- 正描述 1 选择元组：`[5, 17, 2, 0.3333333333333333, 0.3877551020408163]`
- 正描述 2 选择元组：`[7, 17, 3, 0.4444444444444444, 0.46296296296296297]`
- 最终比较正描述：`positive_1` / "Different platters of food are set in the kitchen."
- 完整 lexeme 编辑块：`[{"tag": "delete", "positive_start": 0, "positive_end": 1, "negative_start": 0, "negative_end": 0, "positive_lexemes": ["different"], "negative_lexemes": []}, {"tag": "equal", "positive_start": 1, "positive_end": 7, "negative_start": 0, "negative_end": 6, "positive_lexemes": ["platters", "of", "food", "are", "set", "in"], "negative_lexemes": ["platters", "of", "food", "are", "set", "in"]}, {"tag": "replace", "positive_start": 7, "positive_end": 9, "negative_start": 6, "negative_end": 8, "positive_lexemes": ["the", "kitchen"], "negative_lexemes": ["different", "kitchens"]}]`
- 共同前缀：`[]`
- 正确 contrast hull：`["different", "platters", "of", "food", "are", "set", "in", "the", "kitchen"]`
- 错误 contrast hull：`["platters", "of", "food", "are", "set", "in", "different", "kitchens"]`
- 共同后缀：`[]`
- Hull token 覆盖率（正/负/最大）：`[1.0, 1.0, 1.0]`
- 共同前缀模型 token：`[]`
- 正确 hull 模型 token：IDs `[103, 507, 1617, 694, 1219, 314, 4271, 354, 341, 2166, 732, 2139, 353, 309, 914, 338, 102, 2051]`；text "different platters of food are set in the kitchen"
- 错误 hull 模型 token：IDs `[992, 314, 4271, 354, 341, 2166, 732, 2139, 353, 2301, 914, 338, 102, 2051, 118]`；text "platters of food are set in different kitchens"
- 第一轮/第二轮分类：`complex_edit` / `whole_sentence_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；"at_least_one_hull_covers_all_model_tokens"

### 18. `swap_atribute:442`

- 负例类型/范围：`swap_atribute` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："there is a red fire hydrant on a street between two identical white poles"
- 原始正描述 2："The red fire hydrant is positioned between two identical white poles on a street."
- 原始负描述："there is a white fire hydrant on a street between two identical red poles."
- 规范化正描述 1："there is a red fire hydrant on a street between two identical white poles"
- 规范化正描述 2："the red fire hydrant is positioned between two identical white poles on a street"
- 规范化负描述："there is a white fire hydrant on a street between two identical red poles"
- 正描述 1 选择元组：`[4, 20, 2, 0.14285714285714285, 0.136986301369863]`
- 正描述 2 选择元组：`[16, 28, 6, 0.7857142857142857, 0.475]`
- 最终比较正描述：`positive_1` / "there is a red fire hydrant on a street between two identical white poles"
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 3, "negative_start": 0, "negative_end": 3, "positive_lexemes": ["there", "is", "a"], "negative_lexemes": ["there", "is", "a"]}, {"tag": "replace", "positive_start": 3, "positive_end": 4, "negative_start": 3, "negative_end": 4, "positive_lexemes": ["red"], "negative_lexemes": ["white"]}, {"tag": "equal", "positive_start": 4, "positive_end": 12, "negative_start": 4, "negative_end": 12, "positive_lexemes": ["fire", "hydrant", "on", "a", "street", "between", "two", "identical"], "negative_lexemes": ["fire", "hydrant", "on", "a", "street", "between", "two", "identical"]}, {"tag": "replace", "positive_start": 12, "positive_end": 13, "negative_start": 12, "negative_end": 13, "positive_lexemes": ["white"], "negative_lexemes": ["red"]}, {"tag": "equal", "positive_start": 13, "positive_end": 14, "negative_start": 13, "negative_end": 14, "positive_lexemes": ["poles"], "negative_lexemes": ["poles"]}]`
- 共同前缀：`["there", "is", "a"]`
- 正确 contrast hull：`["red", "fire", "hydrant", "on", "a", "street", "between", "two", "identical", "white"]`
- 错误 contrast hull：`["white", "fire", "hydrant", "on", "a", "street", "between", "two", "identical", "red"]`
- 共同后缀：`["poles"]`
- Hull token 覆盖率（正/负/最大）：`[0.7391304347826086, 0.7391304347826086, 0.7391304347826086]`
- 共同前缀模型 token：`[119, 2503, 395, 299]`
- 正确 hull 模型 token：IDs `[5534, 341, 1475, 5548, 103, 117, 811, 619, 299, 5941, 439, 2172, 2102, 3566, 1096, 654, 1078]`；text " red fire hydrant on a street between two identical white"
- 错误 hull 模型 token：IDs `[654, 1078, 341, 1475, 5548, 103, 117, 811, 619, 299, 5941, 439, 2172, 2102, 3566, 1096, 5534]`；text " white fire hydrant on a street between two identical red"
- 第一轮/第二轮分类：`complex_edit` / `multi_block_local_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 19. `swap_atribute:472`

- 负例类型/范围：`swap_atribute` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A beautiful person sitting at a table with two pizzas."
- 原始正描述 2："There are two pizzas in a table where a beautiful person is seated."
- 原始负描述："Two persons sitting at a table with a beautiful pizza."
- 规范化正描述 1："a beautiful person sitting at a table with two pizzas"
- 规范化正描述 2："there are two pizzas in a table where a beautiful person is seated"
- 规范化负描述："two persons sitting at a table with a beautiful pizza"
- 正描述 1 选择元组：`[10, 20, 4, 0.6, 0.41509433962264153]`
- 正描述 2 选择元组：`[15, 23, 5, 0.6923076923076923, 0.5454545454545454]`
- 最终比较正描述：`positive_1` / "A beautiful person sitting at a table with two pizzas."
- 完整 lexeme 编辑块：`[{"tag": "delete", "positive_start": 0, "positive_end": 1, "negative_start": 0, "negative_end": 0, "positive_lexemes": ["a"], "negative_lexemes": []}, {"tag": "replace", "positive_start": 1, "positive_end": 3, "negative_start": 0, "negative_end": 2, "positive_lexemes": ["beautiful", "person"], "negative_lexemes": ["two", "persons"]}, {"tag": "equal", "positive_start": 3, "positive_end": 8, "negative_start": 2, "negative_end": 7, "positive_lexemes": ["sitting", "at", "a", "table", "with"], "negative_lexemes": ["sitting", "at", "a", "table", "with"]}, {"tag": "insert", "positive_start": 8, "positive_end": 8, "negative_start": 7, "negative_end": 8, "positive_lexemes": [], "negative_lexemes": ["a"]}, {"tag": "replace", "positive_start": 8, "positive_end": 10, "negative_start": 8, "negative_end": 10, "positive_lexemes": ["two", "pizzas"], "negative_lexemes": ["beautiful", "pizza"]}]`
- 共同前缀：`[]`
- 正确 contrast hull：`["a", "beautiful", "person", "sitting", "at", "a", "table", "with", "two", "pizzas"]`
- 错误 contrast hull：`["two", "persons", "sitting", "at", "a", "table", "with", "a", "beautiful", "pizza"]`
- 共同后缀：`[]`
- Hull token 覆盖率（正/负/最大）：`[1.0, 1.0, 1.0]`
- 共同前缀模型 token：`[]`
- 正确 hull 模型 token：IDs `[100, 3979, 507, 549, 2198, 5305, 2912, 1248, 299, 2630, 599, 2102, 344, 1028, 125, 390]`；text "a beautiful person sitting at a table with two pizzas"
- 错误 hull 模型 token：IDs `[119, 122, 114, 2198, 118, 5305, 2912, 1248, 299, 2630, 599, 299, 3979, 507, 549, 344, 1028, 125, 100]`；text "two persons sitting at a table with a beautiful pizza"
- 第一轮/第二轮分类：`complex_edit` / `whole_sentence_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；"at_least_one_hull_covers_all_model_tokens"

### 20. `swap_atribute:477`

- 负例类型/范围：`swap_atribute` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："two persons are cutting and preparing a pizza"
- 原始正描述 2："A pizza is being prepared and cut by two person."
- 原始负描述："A person is cutting and preparing two pizzas."
- 规范化正描述 1："two persons are cutting and preparing a pizza"
- 规范化正描述 2："a pizza is being prepared and cut by two person"
- 规范化负描述："a person is cutting and preparing two pizzas"
- 正描述 1 选择元组：`[10, 16, 2, 0.625, 0.24444444444444444]`
- 正描述 2 选择元组：`[10, 16, 6, 0.6, 0.6382978723404256]`
- 最终比较正描述：`positive_1` / "two persons are cutting and preparing a pizza"
- 完整 lexeme 编辑块：`[{"tag": "replace", "positive_start": 0, "positive_end": 3, "negative_start": 0, "negative_end": 3, "positive_lexemes": ["two", "persons", "are"], "negative_lexemes": ["a", "person", "is"]}, {"tag": "equal", "positive_start": 3, "positive_end": 6, "negative_start": 3, "negative_end": 6, "positive_lexemes": ["cutting", "and", "preparing"], "negative_lexemes": ["cutting", "and", "preparing"]}, {"tag": "replace", "positive_start": 6, "positive_end": 8, "negative_start": 6, "negative_end": 8, "positive_lexemes": ["a", "pizza"], "negative_lexemes": ["two", "pizzas"]}]`
- 共同前缀：`[]`
- 正确 contrast hull：`["two", "persons", "are", "cutting", "and", "preparing", "a", "pizza"]`
- 错误 contrast hull：`["a", "person", "is", "cutting", "and", "preparing", "two", "pizzas"]`
- 共同后缀：`[]`
- Hull token 覆盖率（正/负/最大）：`[1.0, 1.0, 1.0]`
- 共同前缀模型 token：`[]`
- 正确 hull 模型 token：IDs `[119, 122, 114, 2198, 118, 732, 5431, 2912, 376, 2165, 4671, 350, 299, 344, 1028, 125, 100]`；text "two persons are cutting and preparing a pizza"
- 错误 hull 模型 token：IDs `[100, 2198, 395, 5431, 2912, 376, 2165, 4671, 350, 2102, 344, 1028, 125, 390]`；text "a person is cutting and preparing two pizzas"
- 第一轮/第二轮分类：`complex_edit` / `whole_sentence_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；"at_least_one_hull_covers_all_model_tokens"

### 21. `swap_atribute:50`

- 负例类型/范围：`swap_atribute` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A salad made with yellow pepper strips and green sprouts sits on a square white plate."
- 原始正描述 2："The square white plate has a salad made with yellow pepper strips and green sprouts on it."
- 原始负描述："A salad made with green pepper strips and yellow sprouts sits on a square white plate."
- 规范化正描述 1："a salad made with yellow pepper strips and green sprouts sits on a square white plate"
- 规范化正描述 2："the square white plate has a salad made with yellow pepper strips and green sprouts on it"
- 规范化负描述："a salad made with green pepper strips and yellow sprouts sits on a square white plate"
- 正描述 1 选择元组：`[4, 10, 2, 0.125, 0.1411764705882353]`
- 正描述 2 选择元组：`[15, 33, 6, 0.7058823529411765, 0.6966292134831461]`
- 最终比较正描述：`positive_1` / "A salad made with yellow pepper strips and green sprouts sits on a square white plate."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 4, "negative_start": 0, "negative_end": 4, "positive_lexemes": ["a", "salad", "made", "with"], "negative_lexemes": ["a", "salad", "made", "with"]}, {"tag": "replace", "positive_start": 4, "positive_end": 5, "negative_start": 4, "negative_end": 5, "positive_lexemes": ["yellow"], "negative_lexemes": ["green"]}, {"tag": "equal", "positive_start": 5, "positive_end": 8, "negative_start": 5, "negative_end": 8, "positive_lexemes": ["pepper", "strips", "and"], "negative_lexemes": ["pepper", "strips", "and"]}, {"tag": "replace", "positive_start": 8, "positive_end": 9, "negative_start": 8, "negative_end": 9, "positive_lexemes": ["green"], "negative_lexemes": ["yellow"]}, {"tag": "equal", "positive_start": 9, "positive_end": 16, "negative_start": 9, "negative_end": 16, "positive_lexemes": ["sprouts", "sits", "on", "a", "square", "white", "plate"], "negative_lexemes": ["sprouts", "sits", "on", "a", "square", "white", "plate"]}]`
- 共同前缀：`["a", "salad", "made", "with"]`
- 正确 contrast hull：`["yellow", "pepper", "strips", "and", "green"]`
- 错误 contrast hull：`["green", "pepper", "strips", "and", "yellow"]`
- 共同后缀：`["sprouts", "sits", "on", "a", "square", "white", "plate"]`
- Hull token 覆盖率（正/负/最大）：`[0.35714285714285715, 0.35714285714285715, 0.35714285714285715]`
- 共同前缀模型 token：`[100, 4019, 785, 4303, 599]`
- 正确 hull 模型 token：IDs `[385, 446, 1030, 2188, 4534, 580, 809, 3385, 376, 5921]`；text " yellow pepper strips and green"
- 错误 hull 模型 token：IDs `[5921, 2188, 4534, 580, 809, 3385, 376, 385, 446, 1030]`；text " green pepper strips and yellow"
- 第一轮/第二轮分类：`complex_edit` / `multi_block_local_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 22. `swap_atribute:511`

- 负例类型/范围：`swap_atribute` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A small carry-on bag, strapped to the handle of a larger suitcase from the same set of luggage."
- 原始正描述 2："To the handle of a larger suitcase from the same set of luggage, a small carry-on bag is attached."
- 原始负描述："A larger carry-on bag, strapped to the handle of a small suitcase from the same set of luggage."
- 规范化正描述 1："a small carry-on bag , strapped to the handle of a larger suitcase from the same set of luggage"
- 规范化正描述 2："to the handle of a larger suitcase from the same set of luggage , a small carry-on bag is attached"
- 规范化负描述："a larger carry-on bag , strapped to the handle of a small suitcase from the same set of luggage"
- 正描述 1 选择元组：`[4, 22, 2, 0.10526315789473684, 0.12631578947368421]`
- 正描述 2 选择元组：`[15, 39, 3, 0.7, 0.7448979591836735]`
- 最终比较正描述：`positive_1` / "A small carry-on bag, strapped to the handle of a larger suitcase from the same set of luggage."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 1, "negative_start": 0, "negative_end": 1, "positive_lexemes": ["a"], "negative_lexemes": ["a"]}, {"tag": "replace", "positive_start": 1, "positive_end": 2, "negative_start": 1, "negative_end": 2, "positive_lexemes": ["small"], "negative_lexemes": ["larger"]}, {"tag": "equal", "positive_start": 2, "positive_end": 11, "negative_start": 2, "negative_end": 11, "positive_lexemes": ["carry-on", "bag", ",", "strapped", "to", "the", "handle", "of", "a"], "negative_lexemes": ["carry-on", "bag", ",", "strapped", "to", "the", "handle", "of", "a"]}, {"tag": "replace", "positive_start": 11, "positive_end": 12, "negative_start": 11, "negative_end": 12, "positive_lexemes": ["larger"], "negative_lexemes": ["small"]}, {"tag": "equal", "positive_start": 12, "positive_end": 19, "negative_start": 12, "negative_end": 19, "positive_lexemes": ["suitcase", "from", "the", "same", "set", "of", "luggage"], "negative_lexemes": ["suitcase", "from", "the", "same", "set", "of", "luggage"]}]`
- 共同前缀：`["a"]`
- 正确 contrast hull：`["small", "carry-on", "bag", ",", "strapped", "to", "the", "handle", "of", "a", "larger"]`
- 错误 contrast hull：`["larger", "carry-on", "bag", ",", "strapped", "to", "the", "handle", "of", "a", "small"]`
- 共同后缀：`["suitcase", "from", "the", "same", "set", "of", "luggage"]`
- Hull token 覆盖率（正/负/最大）：`[0.6176470588235294, 0.6176470588235294, 0.6176470588235294]`
- 共同前缀模型 token：`[100]`
- 正确 hull 模型 token：IDs `[3436, 3751, 1557, 48, 310, 363, 1163, 256, 47, 580, 559, 737, 382, 364, 309, 3319, 361, 354, 299, 1823, 4105]`；text " small carry-on bag , strapped to the handle of a larger"
- 错误 hull 模型 token：IDs `[1823, 4105, 3751, 1557, 48, 310, 363, 1163, 256, 47, 580, 559, 737, 382, 364, 309, 3319, 361, 354, 299, 3436]`；text " larger carry-on bag , strapped to the handle of a small"
- 第一轮/第二轮分类：`complex_edit` / `multi_block_local_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 23. `swap_atribute:530`

- 负例类型/范围：`swap_atribute` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A person in a striped suit stands in front of palm trees."
- 原始正描述 2："In front of palm trees, the person in the striped suit stands."
- 原始负描述："A person in a palm suit stands in front of striped trees."
- 规范化正描述 1："a person in a striped suit stands in front of palm trees"
- 规范化正描述 2："in front of palm trees , the person in the striped suit stands"
- 规范化负描述："a person in a palm suit stands in front of striped trees"
- 正描述 1 选择元组：`[4, 14, 2, 0.16666666666666666, 0.25]`
- 正描述 2 选择元组：`[23, 25, 3, 0.9230769230769231, 0.6612903225806451]`
- 最终比较正描述：`positive_1` / "A person in a striped suit stands in front of palm trees."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 4, "negative_start": 0, "negative_end": 4, "positive_lexemes": ["a", "person", "in", "a"], "negative_lexemes": ["a", "person", "in", "a"]}, {"tag": "replace", "positive_start": 4, "positive_end": 5, "negative_start": 4, "negative_end": 5, "positive_lexemes": ["striped"], "negative_lexemes": ["palm"]}, {"tag": "equal", "positive_start": 5, "positive_end": 10, "negative_start": 5, "negative_end": 10, "positive_lexemes": ["suit", "stands", "in", "front", "of"], "negative_lexemes": ["suit", "stands", "in", "front", "of"]}, {"tag": "replace", "positive_start": 10, "positive_end": 11, "negative_start": 10, "negative_end": 11, "positive_lexemes": ["palm"], "negative_lexemes": ["striped"]}, {"tag": "equal", "positive_start": 11, "positive_end": 12, "negative_start": 11, "negative_end": 12, "positive_lexemes": ["trees"], "negative_lexemes": ["trees"]}]`
- 共同前缀：`["a", "person", "in", "a"]`
- 正确 contrast hull：`["striped", "suit", "stands", "in", "front", "of", "palm"]`
- 错误 contrast hull：`["palm", "suit", "stands", "in", "front", "of", "striped"]`
- 共同后缀：`["trees"]`
- Hull token 覆盖率（正/负/最大）：`[0.7272727272727273, 0.7272727272727273, 0.7272727272727273]`
- 共同前缀模型 token：`[100, 2198, 353, 299]`
- 正确 hull 模型 token：IDs `[580, 809, 115, 382, 855, 338, 2823, 118, 353, 341, 117, 3856, 354, 344, 352, 112]`；text " striped suit stands in front of palm"
- 错误 hull 模型 token：IDs `[344, 352, 112, 855, 338, 2823, 118, 353, 341, 117, 3856, 354, 580, 809, 115, 382]`；text " palm suit stands in front of striped"
- 第一轮/第二轮分类：`complex_edit` / `multi_block_local_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 24. `swap_atribute:553`

- 负例类型/范围：`swap_atribute` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A child skis in a lot of snow."
- 原始正描述 2："A lot of snow surrounds the skiing child."
- 原始负描述："A lot of children ski in the snow."
- 规范化正描述 1："a child skis in a lot of snow"
- 规范化正描述 2："a lot of snow surrounds the skiing child"
- 规范化负描述："a lot of children ski in the snow"
- 正描述 1 选择元组：`[12, 12, 1, 0.75, 0.5454545454545454]`
- 正描述 2 选择元组：`[10, 10, 1, 0.625, 0.625]`
- 最终比较正描述：`positive_2` / "A lot of snow surrounds the skiing child."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 3, "negative_start": 0, "negative_end": 3, "positive_lexemes": ["a", "lot", "of"], "negative_lexemes": ["a", "lot", "of"]}, {"tag": "replace", "positive_start": 3, "positive_end": 8, "negative_start": 3, "negative_end": 8, "positive_lexemes": ["snow", "surrounds", "the", "skiing", "child"], "negative_lexemes": ["children", "ski", "in", "the", "snow"]}]`
- 共同前缀：`["a", "lot", "of"]`
- 正确 contrast hull：`["snow", "surrounds", "the", "skiing", "child"]`
- 错误 contrast hull：`["children", "ski", "in", "the", "snow"]`
- 共同后缀：`[]`
- Hull token 覆盖率（正/负/最大）：`[0.7142857142857143, 0.6666666666666666, 0.7142857142857143]`
- 共同前缀模型 token：`[100, 406, 593, 354]`
- 正确 hull 模型 token：IDs `[316, 1103, 3946, 2383, 118, 309, 2549, 108, 350, 6109]`；text " snow surrounds the skiing child"
- 错误 hull 模型 token：IDs `[6109, 3193, 2549, 108, 353, 309, 316, 1103]`；text " children ski in the snow"
- 第一轮/第二轮分类：`ambiguous_source` / `medium_contrast_hull`
- 自动判断："positive_2_selection_tuple_lexicographically_smaller"；"single_edit_block_token_coverage_above_50_percent"

### 25. `swap_atribute:578`

- 负例类型/范围：`swap_atribute` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A bedroom with two beds placed next to one another with a desk to one side and a small window on the opposite side."
- 原始正描述 2："A bedroom featuring two beds side by side, a desk on one side, and a small window on the opposite wall."
- 原始负描述："A bedroom with a small bed placed next to a desk and a two windows on the opposite side."
- 规范化正描述 1："a bedroom with two beds placed next to one another with a desk to one side and a small window on the opposite side"
- 规范化正描述 2："a bedroom featuring two beds side by side , a desk on one side , and a small window on the opposite wall"
- 规范化负描述："a bedroom with a small bed placed next to a desk and a two windows on the opposite side"
- 正描述 1 选择元组：`[15, 29, 5, 0.4583333333333333, 0.37719298245614036]`
- 正描述 2 选择元组：`[24, 38, 4, 0.6086956521739131, 0.4807692307692308]`
- 最终比较正描述：`positive_1` / "A bedroom with two beds placed next to one another with a desk to one side and a small window on the opposite side."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 3, "negative_start": 0, "negative_end": 3, "positive_lexemes": ["a", "bedroom", "with"], "negative_lexemes": ["a", "bedroom", "with"]}, {"tag": "insert", "positive_start": 3, "positive_end": 3, "negative_start": 3, "negative_end": 4, "positive_lexemes": [], "negative_lexemes": ["a"]}, {"tag": "replace", "positive_start": 3, "positive_end": 5, "negative_start": 4, "negative_end": 6, "positive_lexemes": ["two", "beds"], "negative_lexemes": ["small", "bed"]}, {"tag": "equal", "positive_start": 5, "positive_end": 8, "negative_start": 6, "negative_end": 9, "positive_lexemes": ["placed", "next", "to"], "negative_lexemes": ["placed", "next", "to"]}, {"tag": "delete", "positive_start": 8, "positive_end": 11, "negative_start": 9, "negative_end": 9, "positive_lexemes": ["one", "another", "with"], "negative_lexemes": []}, {"tag": "equal", "positive_start": 11, "positive_end": 13, "negative_start": 9, "negative_end": 11, "positive_lexemes": ["a", "desk"], "negative_lexemes": ["a", "desk"]}, {"tag": "delete", "positive_start": 13, "positive_end": 16, "negative_start": 11, "negative_end": 11, "positive_lexemes": ["to", "one", "side"], "negative_lexemes": []}, {"tag": "equal", "positive_start": 16, "positive_end": 18, "negative_start": 11, "negative_end": 13, "positive_lexemes": ["and", "a"], "negative_lexemes": ["and", "a"]}, {"tag": "replace", "positive_start": 18, "positive_end": 20, "negative_start": 13, "negative_end": 15, "positive_lexemes": ["small", "window"], "negative_lexemes": ["two", "windows"]}, {"tag": "equal", "positive_start": 20, "positive_end": 24, "negative_start": 15, "negative_end": 19, "positive_lexemes": ["on", "the", "opposite", "side"], "negative_lexemes": ["on", "the", "opposite", "side"]}]`
- 共同前缀：`["a", "bedroom", "with"]`
- 正确 contrast hull：`["two", "beds", "placed", "next", "to", "one", "another", "with", "a", "desk", "to", "one", "side", "and", "a", "small", "window"]`
- 错误 contrast hull：`["a", "small", "bed", "placed", "next", "to", "a", "desk", "and", "a", "two", "windows"]`
- 共同后缀：`["on", "the", "opposite", "side"]`
- Hull token 覆盖率（正/负/最大）：`[0.6388888888888888, 0.5666666666666667, 0.6388888888888888]`
- 共同前缀模型 token：`[100, 363, 382, 393, 444, 599]`
- 正确 hull 模型 token：IDs `[2102, 363, 382, 118, 1219, 1545, 382, 4658, 364, 1623, 5467, 599, 299, 1453, 110, 364, 1623, 5046, 376, 299, 3436, 5472, 451]`；text " two beds placed next to one another with a desk to one side and a small window"
- 错误 hull 模型 token：IDs `[299, 3436, 363, 382, 1219, 1545, 382, 4658, 364, 299, 1453, 110, 376, 299, 2102, 339, 4310]`；text " a small bed placed next to a desk and a two windows"
- 第一轮/第二轮分类：`complex_edit` / `multi_block_local_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 26. `swap_atribute:598`

- 负例类型/范围：`swap_atribute` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A red car is parked at a traffic light."
- 原始正描述 2："The traffic light is positioned above the red car that is parked at it."
- 原始负描述："A traffic car is parked at a red light."
- 规范化正描述 1："a red car is parked at a traffic light"
- 规范化正描述 2："the traffic light is positioned above the red car that is parked at it"
- 规范化负描述："a traffic car is parked at a red light"
- 正描述 1 选择元组：`[4, 14, 2, 0.2222222222222222, 0.3157894736842105]`
- 正描述 2 选择元组：`[17, 23, 5, 0.7857142857142857, 0.6142857142857143]`
- 最终比较正描述：`positive_1` / "A red car is parked at a traffic light."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 1, "negative_start": 0, "negative_end": 1, "positive_lexemes": ["a"], "negative_lexemes": ["a"]}, {"tag": "replace", "positive_start": 1, "positive_end": 2, "negative_start": 1, "negative_end": 2, "positive_lexemes": ["red"], "negative_lexemes": ["traffic"]}, {"tag": "equal", "positive_start": 2, "positive_end": 7, "negative_start": 2, "negative_end": 7, "positive_lexemes": ["car", "is", "parked", "at", "a"], "negative_lexemes": ["car", "is", "parked", "at", "a"]}, {"tag": "replace", "positive_start": 7, "positive_end": 8, "negative_start": 7, "negative_end": 8, "positive_lexemes": ["traffic"], "negative_lexemes": ["red"]}, {"tag": "equal", "positive_start": 8, "positive_end": 9, "negative_start": 8, "negative_end": 9, "positive_lexemes": ["light"], "negative_lexemes": ["light"]}]`
- 共同前缀：`["a"]`
- 正确 contrast hull：`["red", "car", "is", "parked", "at", "a", "traffic"]`
- 错误 contrast hull：`["traffic", "car", "is", "parked", "at", "a", "red"]`
- 共同后缀：`["light"]`
- Hull token 覆盖率（正/负/最大）：`[0.8333333333333334, 0.8333333333333334, 0.8333333333333334]`
- 共同前缀模型 token：`[100]`
- 正确 hull 模型 token：IDs `[5534, 3751, 395, 344, 2000, 382, 1248, 299, 1946, 5935]`；text " red car is parked at a traffic"
- 错误 hull 模型 token：IDs `[1946, 5935, 3751, 395, 344, 2000, 382, 1248, 299, 5534]`；text " traffic car is parked at a red"
- 第一轮/第二轮分类：`complex_edit` / `large_contrast_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；"maximum_hull_token_coverage_above_75_percent"

### 27. `swap_atribute:612`

- 负例类型/范围：`swap_atribute` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A cheese pizza sitting on top of white paper and a large plate."
- 原始正描述 2："A large plate is positioned below of a white paper, with a cheese pizza sitting on top of it."
- 原始负描述："A white pizza sitting on top of cheese paper and a large plate."
- 规范化正描述 1："a cheese pizza sitting on top of white paper and a large plate"
- 规范化正描述 2："a large plate is positioned below of a white paper , with a cheese pizza sitting on top of it"
- 规范化负描述："a white pizza sitting on top of cheese paper and a large plate"
- 正描述 1 选择元组：`[4, 14, 2, 0.15384615384615385, 0.12903225806451613]`
- 正描述 2 选择元组：`[25, 31, 7, 0.8, 0.6666666666666666]`
- 最终比较正描述：`positive_1` / "A cheese pizza sitting on top of white paper and a large plate."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 1, "negative_start": 0, "negative_end": 1, "positive_lexemes": ["a"], "negative_lexemes": ["a"]}, {"tag": "replace", "positive_start": 1, "positive_end": 2, "negative_start": 1, "negative_end": 2, "positive_lexemes": ["cheese"], "negative_lexemes": ["white"]}, {"tag": "equal", "positive_start": 2, "positive_end": 7, "negative_start": 2, "negative_end": 7, "positive_lexemes": ["pizza", "sitting", "on", "top", "of"], "negative_lexemes": ["pizza", "sitting", "on", "top", "of"]}, {"tag": "replace", "positive_start": 7, "positive_end": 8, "negative_start": 7, "negative_end": 8, "positive_lexemes": ["white"], "negative_lexemes": ["cheese"]}, {"tag": "equal", "positive_start": 8, "positive_end": 13, "negative_start": 8, "negative_end": 13, "positive_lexemes": ["paper", "and", "a", "large", "plate"], "negative_lexemes": ["paper", "and", "a", "large", "plate"]}]`
- 共同前缀：`["a"]`
- 正确 contrast hull：`["cheese", "pizza", "sitting", "on", "top", "of", "white"]`
- 错误 contrast hull：`["white", "pizza", "sitting", "on", "top", "of", "cheese"]`
- 共同后缀：`["paper", "and", "a", "large", "plate"]`
- Hull token 覆盖率（正/负/最大）：`[0.6190476190476191, 0.6190476190476191, 0.6190476190476191]`
- 共同前缀模型 token：`[100]`
- 正确 hull 模型 token：IDs `[1806, 2023, 344, 1028, 125, 100, 5305, 2912, 619, 2924, 354, 654, 1078]`；text " cheese pizza sitting on top of white"
- 错误 hull 模型 token：IDs `[654, 1078, 344, 1028, 125, 100, 5305, 2912, 619, 2924, 354, 1806, 2023]`；text " white pizza sitting on top of cheese"
- 第一轮/第二轮分类：`complex_edit` / `multi_block_local_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 28. `swap_atribute:66`

- 负例类型/范围：`swap_atribute` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A person in a blue dress poses on a weird chair"
- 原始正描述 2："A person in a blue dress is positioned on a weird chair."
- 原始负描述："A person in a weird dress poses on a blue chair."
- 规范化正描述 1："a person in a blue dress poses on a weird chair"
- 规范化正描述 2："a person in a blue dress is positioned on a weird chair"
- 规范化负描述："a person in a weird dress poses on a blue chair"
- 正描述 1 选择元组：`[4, 12, 2, 0.18181818181818182, 0.2127659574468085]`
- 正描述 2 选择元组：`[7, 13, 4, 0.3333333333333333, 0.34545454545454546]`
- 最终比较正描述：`positive_1` / "A person in a blue dress poses on a weird chair"
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 4, "negative_start": 0, "negative_end": 4, "positive_lexemes": ["a", "person", "in", "a"], "negative_lexemes": ["a", "person", "in", "a"]}, {"tag": "replace", "positive_start": 4, "positive_end": 5, "negative_start": 4, "negative_end": 5, "positive_lexemes": ["blue"], "negative_lexemes": ["weird"]}, {"tag": "equal", "positive_start": 5, "positive_end": 9, "negative_start": 5, "negative_end": 9, "positive_lexemes": ["dress", "poses", "on", "a"], "negative_lexemes": ["dress", "poses", "on", "a"]}, {"tag": "replace", "positive_start": 9, "positive_end": 10, "negative_start": 9, "negative_end": 10, "positive_lexemes": ["weird"], "negative_lexemes": ["blue"]}, {"tag": "equal", "positive_start": 10, "positive_end": 11, "negative_start": 10, "negative_end": 11, "positive_lexemes": ["chair"], "negative_lexemes": ["chair"]}]`
- 共同前缀：`["a", "person", "in", "a"]`
- 正确 contrast hull：`["blue", "dress", "poses", "on", "a", "weird"]`
- 错误 contrast hull：`["weird", "dress", "poses", "on", "a", "blue"]`
- 共同后缀：`["chair"]`
- Hull token 覆盖率（正/负/最大）：`[0.6, 0.6, 0.6]`
- 共同前缀模型 token：`[100, 2198, 353, 299]`
- 正确 hull 模型 token：IDs `[4300, 373, 1592, 2617, 329, 619, 299, 796, 6064]`；text " blue dress poses on a weird"
- 错误 hull 模型 token：IDs `[796, 6064, 373, 1592, 2617, 329, 619, 299, 4300]`；text " weird dress poses on a blue"
- 第一轮/第二轮分类：`complex_edit` / `multi_block_local_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 29. `swap_atribute:662`

- 负例类型/范围：`swap_atribute` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："Several vehicles and a horse drawn cart pull up outside of a building."
- 原始正描述 2："Outside of a building, several vehicles and a horse-drawn cart arrive."
- 原始负描述："A horse drawn vehicle and several carts pull up outside of a building."
- 规范化正描述 1："several vehicles and a horse drawn cart pull up outside of a building"
- 规范化正描述 2："outside of a building , several vehicles and a horse-drawn cart arrive"
- 规范化负描述："a horse drawn vehicle and several carts pull up outside of a building"
- 正描述 1 选择元组：`[14, 14, 1, 0.5384615384615384, 0.2898550724637681]`
- 正描述 2 选择元组：`[23, 25, 3, 0.9230769230769231, 0.7428571428571429]`
- 最终比较正描述：`positive_1` / "Several vehicles and a horse drawn cart pull up outside of a building."
- 完整 lexeme 编辑块：`[{"tag": "replace", "positive_start": 0, "positive_end": 7, "negative_start": 0, "negative_end": 7, "positive_lexemes": ["several", "vehicles", "and", "a", "horse", "drawn", "cart"], "negative_lexemes": ["a", "horse", "drawn", "vehicle", "and", "several", "carts"]}, {"tag": "equal", "positive_start": 7, "positive_end": 13, "negative_start": 7, "negative_end": 13, "positive_lexemes": ["pull", "up", "outside", "of", "a", "building"], "negative_lexemes": ["pull", "up", "outside", "of", "a", "building"]}]`
- 共同前缀：`[]`
- 正确 contrast hull：`["several", "vehicles", "and", "a", "horse", "drawn", "cart"]`
- 错误 contrast hull：`["a", "horse", "drawn", "vehicle", "and", "several", "carts"]`
- 共同后缀：`["pull", "up", "outside", "of", "a", "building"]`
- Hull token 覆盖率（正/负/最大）：`[0.6296296296296297, 0.6153846153846154, 0.6296296296296297]`
- 共同前缀模型 token：`[]`
- 正确 hull 模型 token：IDs `[573, 652, 352, 4389, 107, 375, 1907, 376, 299, 429, 336, 573, 373, 559, 3200, 317, 913]`；text "several vehicles and a horse drawn cart"
- 错误 hull 模型 token：IDs `[100, 429, 336, 573, 373, 559, 3200, 4389, 107, 375, 361, 376, 4920, 317, 913, 118]`；text "a horse drawn vehicle and several carts"
- 第一轮/第二轮分类：`complex_edit` / `medium_contrast_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；"single_edit_block_token_coverage_above_50_percent"

### 30. `swap_atribute:7`

- 负例类型/范围：`swap_atribute` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A large elephant standing next to a bunch of trees."
- 原始正描述 2："A large elephant is positioned next to a group of trees."
- 原始负描述："A bunch of elephants standing next to a large tree."
- 规范化正描述 1："a large elephant standing next to a bunch of trees"
- 规范化正描述 2："a large elephant is positioned next to a group of trees"
- 规范化负描述："a bunch of elephants standing next to a large tree"
- 正描述 1 选择元组：`[10, 18, 4, 0.6, 0.36]`
- 正描述 2 选择元组：`[13, 19, 3, 0.6363636363636364, 0.4909090909090909]`
- 最终比较正描述：`positive_1` / "A large elephant standing next to a bunch of trees."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 1, "negative_start": 0, "negative_end": 1, "positive_lexemes": ["a"], "negative_lexemes": ["a"]}, {"tag": "insert", "positive_start": 1, "positive_end": 1, "negative_start": 1, "negative_end": 2, "positive_lexemes": [], "negative_lexemes": ["bunch"]}, {"tag": "replace", "positive_start": 1, "positive_end": 3, "negative_start": 2, "negative_end": 4, "positive_lexemes": ["large", "elephant"], "negative_lexemes": ["of", "elephants"]}, {"tag": "equal", "positive_start": 3, "positive_end": 7, "negative_start": 4, "negative_end": 8, "positive_lexemes": ["standing", "next", "to", "a"], "negative_lexemes": ["standing", "next", "to", "a"]}, {"tag": "delete", "positive_start": 7, "positive_end": 8, "negative_start": 8, "negative_end": 8, "positive_lexemes": ["bunch"], "negative_lexemes": []}, {"tag": "replace", "positive_start": 8, "positive_end": 10, "negative_start": 8, "negative_end": 10, "positive_lexemes": ["of", "trees"], "negative_lexemes": ["large", "tree"]}]`
- 共同前缀：`["a"]`
- 正确 contrast hull：`["large", "elephant", "standing", "next", "to", "a", "bunch", "of", "trees"]`
- 错误 contrast hull：`["bunch", "of", "elephants", "standing", "next", "to", "a", "large", "tree"]`
- 共同后缀：`[]`
- Hull token 覆盖率（正/负/最大）：`[0.9375, 0.9375, 0.9375]`
- 共同前缀模型 token：`[100]`
- 正确 hull 模型 token：IDs `[2994, 1905, 1601, 811, 2823, 350, 4658, 364, 299, 363, 651, 550, 354, 4191, 329]`；text " large elephant standing next to a bunch of trees"
- 错误 hull 模型 token：IDs `[363, 651, 550, 354, 1905, 1601, 5483, 2823, 350, 4658, 364, 299, 2994, 297, 1382]`；text " bunch of elephants standing next to a large tree"
- 第一轮/第二轮分类：`complex_edit` / `large_contrast_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；"maximum_hull_token_coverage_above_75_percent"

## swap_object

候选 `245` 条，本节抽取 `30` 条。

### 1. `swap_object:111`

- 负例类型/范围：`swap_object` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A young child standing in front of a plate of food."
- 原始正描述 2："A plate filled with food is positioned in front of a small child."
- 原始负描述："A plate of food standing in front of a young child."
- 规范化正描述 1："a young child standing in front of a plate of food"
- 规范化正描述 2："a plate filled with food is positioned in front of a small child"
- 规范化负描述："a plate of food standing in front of a young child"
- 正描述 1 选择元组：`[10, 20, 4, 0.5454545454545454, 0.44]`
- 正描述 2 选择元组：`[8, 18, 5, 0.38461538461538464, 0.40625]`
- 最终比较正描述：`positive_2` / "A plate filled with food is positioned in front of a small child."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 2, "negative_start": 0, "negative_end": 2, "positive_lexemes": ["a", "plate"], "negative_lexemes": ["a", "plate"]}, {"tag": "delete", "positive_start": 2, "positive_end": 3, "negative_start": 2, "negative_end": 2, "positive_lexemes": ["filled"], "negative_lexemes": []}, {"tag": "replace", "positive_start": 3, "positive_end": 4, "negative_start": 2, "negative_end": 3, "positive_lexemes": ["with"], "negative_lexemes": ["of"]}, {"tag": "equal", "positive_start": 4, "positive_end": 5, "negative_start": 3, "negative_end": 4, "positive_lexemes": ["food"], "negative_lexemes": ["food"]}, {"tag": "delete", "positive_start": 5, "positive_end": 6, "negative_start": 4, "negative_end": 4, "positive_lexemes": ["is"], "negative_lexemes": []}, {"tag": "replace", "positive_start": 6, "positive_end": 7, "negative_start": 4, "negative_end": 5, "positive_lexemes": ["positioned"], "negative_lexemes": ["standing"]}, {"tag": "equal", "positive_start": 7, "positive_end": 11, "negative_start": 5, "negative_end": 9, "positive_lexemes": ["in", "front", "of", "a"], "negative_lexemes": ["in", "front", "of", "a"]}, {"tag": "replace", "positive_start": 11, "positive_end": 12, "negative_start": 9, "negative_end": 10, "positive_lexemes": ["small"], "negative_lexemes": ["young"]}, {"tag": "equal", "positive_start": 12, "positive_end": 13, "negative_start": 10, "negative_end": 11, "positive_lexemes": ["child"], "negative_lexemes": ["child"]}]`
- 共同前缀：`["a", "plate"]`
- 正确 contrast hull：`["filled", "with", "food", "is", "positioned", "in", "front", "of", "a", "small"]`
- 错误 contrast hull：`["of", "food", "standing", "in", "front", "of", "a", "young"]`
- 共同后缀：`["child"]`
- Hull token 覆盖率（正/负/最大）：`[0.8, 0.7647058823529411, 0.8]`
- 共同前缀模型 token：`[100, 1219, 557]`
- 正确 hull 模型 token：IDs `[2608, 2003, 599, 341, 2166, 395, 2617, 1632, 382, 353, 341, 117, 3856, 354, 299, 3436]`；text " filled with food is positioned in front of a small"
- 错误 hull 模型 token：IDs `[354, 341, 2166, 2823, 350, 353, 341, 117, 3856, 354, 299, 401, 1685]`；text " of food standing in front of a young"
- 第一轮/第二轮分类：`complex_edit` / `large_contrast_hull`
- 自动判断："positive_2_selection_tuple_lexicographically_smaller"；"maximum_hull_token_coverage_above_75_percent"

### 2. `swap_object:12`

- 负例类型/范围：`swap_object` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A person taking a photo with his right hand and eating food with his left hand."
- 原始正描述 2："A person is simultaneously eating food with their left hand and taking a photo with their right hand."
- 原始负描述："A person taking a photo with his left hand and eating food with his right hand."
- 规范化正描述 1："a person taking a photo with his right hand and eating food with his left hand"
- 规范化正描述 2："a person is simultaneously eating food with their left hand and taking a photo with their right hand"
- 规范化负描述："a person taking a photo with his left hand and eating food with his right hand"
- 正描述 1 选择元组：`[4, 16, 2, 0.125, 0.10256410256410256]`
- 正描述 2 选择元组：`[16, 26, 6, 0.5, 0.38]`
- 最终比较正描述：`positive_1` / "A person taking a photo with his right hand and eating food with his left hand."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 7, "negative_start": 0, "negative_end": 7, "positive_lexemes": ["a", "person", "taking", "a", "photo", "with", "his"], "negative_lexemes": ["a", "person", "taking", "a", "photo", "with", "his"]}, {"tag": "replace", "positive_start": 7, "positive_end": 8, "negative_start": 7, "negative_end": 8, "positive_lexemes": ["right"], "negative_lexemes": ["left"]}, {"tag": "equal", "positive_start": 8, "positive_end": 14, "negative_start": 8, "negative_end": 14, "positive_lexemes": ["hand", "and", "eating", "food", "with", "his"], "negative_lexemes": ["hand", "and", "eating", "food", "with", "his"]}, {"tag": "replace", "positive_start": 14, "positive_end": 15, "negative_start": 14, "negative_end": 15, "positive_lexemes": ["left"], "negative_lexemes": ["right"]}, {"tag": "equal", "positive_start": 15, "positive_end": 16, "negative_start": 15, "negative_end": 16, "positive_lexemes": ["hand"], "negative_lexemes": ["hand"]}]`
- 共同前缀：`["a", "person", "taking", "a", "photo", "with", "his"]`
- 正确 contrast hull：`["right", "hand", "and", "eating", "food", "with", "his", "left"]`
- 错误 contrast hull：`["left", "hand", "and", "eating", "food", "with", "his", "right"]`
- 共同后缀：`["hand"]`
- Hull token 覆盖率（正/负/最大）：`[0.47619047619047616, 0.47619047619047616, 0.47619047619047616]`
- 共同前缀模型 token：`[100, 2198, 297, 5784, 299, 2001, 593, 114, 599, 2049]`
- 正确 hull 模型 token：IDs `[3690, 3319, 376, 413, 1807, 341, 2166, 599, 2049, 4299]`；text " right hand and eating food with his left"
- 错误 hull 模型 token：IDs `[4299, 3319, 376, 413, 1807, 341, 2166, 599, 2049, 3690]`；text " left hand and eating food with his right"
- 第一轮/第二轮分类：`complex_edit` / `multi_block_local_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 3. `swap_object:121`

- 负例类型/范围：`swap_object` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A large orbital vase sits next to a candle on a table."
- 原始正描述 2："A large orbital vase is positioned next to a candle on a table."
- 原始负描述："A large orbital candle sits next to a vase on a table."
- 规范化正描述 1："a large orbital vase sits next to a candle on a table"
- 规范化正描述 2："a large orbital vase is positioned next to a candle on a table"
- 规范化负描述："a large orbital candle sits next to a vase on a table"
- 正描述 1 选择元组：`[4, 12, 2, 0.16666666666666666, 0.1509433962264151]`
- 正描述 2 选择元组：`[7, 13, 3, 0.3076923076923077, 0.27419354838709675]`
- 最终比较正描述：`positive_1` / "A large orbital vase sits next to a candle on a table."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 3, "negative_start": 0, "negative_end": 3, "positive_lexemes": ["a", "large", "orbital"], "negative_lexemes": ["a", "large", "orbital"]}, {"tag": "replace", "positive_start": 3, "positive_end": 4, "negative_start": 3, "negative_end": 4, "positive_lexemes": ["vase"], "negative_lexemes": ["candle"]}, {"tag": "equal", "positive_start": 4, "positive_end": 8, "negative_start": 4, "negative_end": 8, "positive_lexemes": ["sits", "next", "to", "a"], "negative_lexemes": ["sits", "next", "to", "a"]}, {"tag": "replace", "positive_start": 8, "positive_end": 9, "negative_start": 8, "negative_end": 9, "positive_lexemes": ["candle"], "negative_lexemes": ["vase"]}, {"tag": "equal", "positive_start": 9, "positive_end": 12, "negative_start": 9, "negative_end": 12, "positive_lexemes": ["on", "a", "table"], "negative_lexemes": ["on", "a", "table"]}]`
- 共同前缀：`["a", "large", "orbital"]`
- 正确 contrast hull：`["vase", "sits", "next", "to", "a", "candle"]`
- 错误 contrast hull：`["candle", "sits", "next", "to", "a", "vase"]`
- 共同后缀：`["on", "a", "table"]`
- Hull token 覆盖率（正/负/最大）：`[0.5555555555555556, 0.5555555555555556, 0.5555555555555556]`
- 共同前缀模型 token：`[100, 2994, 522, 101, 1998]`
- 正确 hull 模型 token：IDs `[603, 812, 316, 2163, 4658, 364, 299, 541, 103, 361]`；text " vase sits next to a candle"
- 错误 hull 模型 token：IDs `[541, 103, 361, 316, 2163, 4658, 364, 299, 603, 812]`；text " candle sits next to a vase"
- 第一轮/第二轮分类：`complex_edit` / `multi_block_local_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 4. `swap_object:125`

- 负例类型/范围：`swap_object` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A bowl full of food sitting on a table next to a fork that rests on top of a circular disk."
- 原始正描述 2："A circular disk is below a fork that is positioned adjacent to a bowl full of food that is situated on a table."
- 原始负描述："A fork full of food sitting on a table next to a bowl that rests on top of a circular disk."
- 规范化正描述 1："a bowl full of food sitting on a table next to a fork that rests on top of a circular disk"
- 规范化正描述 2："a circular disk is below a fork that is positioned adjacent to a bowl full of food that is situated on a table"
- 规范化负描述："a fork full of food sitting on a table next to a bowl that rests on top of a circular disk"
- 正描述 1 选择元组：`[4, 24, 2, 0.09523809523809523, 0.06666666666666667]`
- 正描述 2 选择元组：`[36, 42, 4, 0.8260869565217391, 0.6909090909090909]`
- 最终比较正描述：`positive_1` / "A bowl full of food sitting on a table next to a fork that rests on top of a circular disk."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 1, "negative_start": 0, "negative_end": 1, "positive_lexemes": ["a"], "negative_lexemes": ["a"]}, {"tag": "replace", "positive_start": 1, "positive_end": 2, "negative_start": 1, "negative_end": 2, "positive_lexemes": ["bowl"], "negative_lexemes": ["fork"]}, {"tag": "equal", "positive_start": 2, "positive_end": 12, "negative_start": 2, "negative_end": 12, "positive_lexemes": ["full", "of", "food", "sitting", "on", "a", "table", "next", "to", "a"], "negative_lexemes": ["full", "of", "food", "sitting", "on", "a", "table", "next", "to", "a"]}, {"tag": "replace", "positive_start": 12, "positive_end": 13, "negative_start": 12, "negative_end": 13, "positive_lexemes": ["fork"], "negative_lexemes": ["bowl"]}, {"tag": "equal", "positive_start": 13, "positive_end": 21, "negative_start": 13, "negative_end": 21, "positive_lexemes": ["that", "rests", "on", "top", "of", "a", "circular", "disk"], "negative_lexemes": ["that", "rests", "on", "top", "of", "a", "circular", "disk"]}]`
- 共同前缀：`["a"]`
- 正确 contrast hull：`["bowl", "full", "of", "food", "sitting", "on", "a", "table", "next", "to", "a", "fork"]`
- 错误 contrast hull：`["fork", "full", "of", "food", "sitting", "on", "a", "table", "next", "to", "a", "bowl"]`
- 共同后缀：`["that", "rests", "on", "top", "of", "a", "circular", "disk"]`
- Hull token 覆盖率（正/负/最大）：`[0.5666666666666667, 0.5666666666666667, 0.5666666666666667]`
- 共同前缀模型 token：`[100]`
- 正确 hull 模型 token：IDs `[363, 451, 111, 5840, 354, 341, 2166, 5305, 2912, 619, 299, 2630, 4658, 364, 299, 503, 110]`；text " bowl full of food sitting on a table next to a fork"
- 错误 hull 模型 token：IDs `[503, 110, 5840, 354, 341, 2166, 5305, 2912, 619, 299, 2630, 4658, 364, 299, 363, 451, 111]`；text " fork full of food sitting on a table next to a bowl"
- 第一轮/第二轮分类：`complex_edit` / `multi_block_local_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 5. `swap_object:132`

- 负例类型/范围：`swap_object` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A city street with a rainbow in the background "
- 原始正描述 2："A rainbow visible in the background of a city street."
- 原始负描述："A rainbow with a city street in the background."
- 规范化正描述 1："a city street with a rainbow in the background"
- 规范化正描述 2："a rainbow visible in the background of a city street"
- 规范化负描述："a rainbow with a city street in the background"
- 正描述 1 选择元组：`[6, 10, 4, 0.4444444444444444, 0.4782608695652174]`
- 正描述 2 选择元组：`[15, 15, 2, 0.8, 0.6153846153846154]`
- 最终比较正描述：`positive_1` / "A city street with a rainbow in the background "
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 1, "negative_start": 0, "negative_end": 1, "positive_lexemes": ["a"], "negative_lexemes": ["a"]}, {"tag": "delete", "positive_start": 1, "positive_end": 2, "negative_start": 1, "negative_end": 1, "positive_lexemes": ["city"], "negative_lexemes": []}, {"tag": "replace", "positive_start": 2, "positive_end": 3, "negative_start": 1, "negative_end": 2, "positive_lexemes": ["street"], "negative_lexemes": ["rainbow"]}, {"tag": "equal", "positive_start": 3, "positive_end": 5, "negative_start": 2, "negative_end": 4, "positive_lexemes": ["with", "a"], "negative_lexemes": ["with", "a"]}, {"tag": "insert", "positive_start": 5, "positive_end": 5, "negative_start": 4, "negative_end": 5, "positive_lexemes": [], "negative_lexemes": ["city"]}, {"tag": "replace", "positive_start": 5, "positive_end": 6, "negative_start": 5, "negative_end": 6, "positive_lexemes": ["rainbow"], "negative_lexemes": ["street"]}, {"tag": "equal", "positive_start": 6, "positive_end": 9, "negative_start": 6, "negative_end": 9, "positive_lexemes": ["in", "the", "background"], "negative_lexemes": ["in", "the", "background"]}]`
- 共同前缀：`["a"]`
- 正确 contrast hull：`["city", "street", "with", "a", "rainbow"]`
- 错误 contrast hull：`["rainbow", "with", "a", "city", "street"]`
- 共同后缀：`["in", "the", "background"]`
- Hull token 覆盖率（正/负/最大）：`[0.6, 0.6, 0.6]`
- 共同前缀模型 token：`[100]`
- 正确 hull 模型 token：IDs `[3972, 5941, 439, 599, 299, 2265, 301, 101, 451]`；text " city street with a rainbow"
- 错误 hull 模型 token：IDs `[2265, 301, 101, 451, 599, 299, 3972, 5941, 439]`；text " rainbow with a city street"
- 第一轮/第二轮分类：`ambiguous_source` / `multi_block_local_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 6. `swap_object:15`

- 负例类型/范围：`swap_object` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A street scene with a horse pulling a white carriage."
- 原始正描述 2："A white carriage is being pulled by a horse on a street."
- 原始负描述："A street scene with a white carriage pulling a horse."
- 规范化正描述 1："a street scene with a horse pulling a white carriage"
- 规范化正描述 2："a white carriage is being pulled by a horse on a street"
- 规范化负描述："a street scene with a white carriage pulling a horse"
- 正描述 1 选择元组：`[6, 10, 4, 0.4, 0.4230769230769231]`
- 正描述 2 选择元组：`[18, 20, 3, 0.8333333333333334, 0.7636363636363637]`
- 最终比较正描述：`positive_1` / "A street scene with a horse pulling a white carriage."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 5, "negative_start": 0, "negative_end": 5, "positive_lexemes": ["a", "street", "scene", "with", "a"], "negative_lexemes": ["a", "street", "scene", "with", "a"]}, {"tag": "insert", "positive_start": 5, "positive_end": 5, "negative_start": 5, "negative_end": 6, "positive_lexemes": [], "negative_lexemes": ["white"]}, {"tag": "replace", "positive_start": 5, "positive_end": 6, "negative_start": 6, "negative_end": 7, "positive_lexemes": ["horse"], "negative_lexemes": ["carriage"]}, {"tag": "equal", "positive_start": 6, "positive_end": 8, "negative_start": 7, "negative_end": 9, "positive_lexemes": ["pulling", "a"], "negative_lexemes": ["pulling", "a"]}, {"tag": "delete", "positive_start": 8, "positive_end": 9, "negative_start": 9, "negative_end": 9, "positive_lexemes": ["white"], "negative_lexemes": []}, {"tag": "replace", "positive_start": 9, "positive_end": 10, "negative_start": 9, "negative_end": 10, "positive_lexemes": ["carriage"], "negative_lexemes": ["horse"]}]`
- 共同前缀：`["a", "street", "scene", "with", "a"]`
- 正确 contrast hull：`["horse", "pulling", "a", "white", "carriage"]`
- 错误 contrast hull：`["white", "carriage", "pulling", "a", "horse"]`
- 共同后缀：`[]`
- Hull token 覆盖率（正/负/最大）：`[0.631578947368421, 0.631578947368421, 0.631578947368421]`
- 共同前缀模型 token：`[100, 5941, 439, 1416, 4975, 599, 299]`
- 正确 hull 模型 token：IDs `[429, 336, 573, 344, 3800, 350, 299, 654, 1078, 3751, 809, 834]`；text " horse pulling a white carriage"
- 错误 hull 模型 token：IDs `[654, 1078, 3751, 809, 834, 344, 3800, 350, 299, 429, 336, 573]`；text " white carriage pulling a horse"
- 第一轮/第二轮分类：`complex_edit` / `multi_block_local_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 7. `swap_object:150`

- 负例类型/范围：`swap_object` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A school bus waits in traffic behind a car."
- 原始正描述 2："A car is in front of a school bus that is waiting in traffic."
- 原始负描述："A car waits in traffic behind a school bus."
- 规范化正描述 1："a school bus waits in traffic behind a car"
- 规范化正描述 2："a car is in front of a school bus that is waiting in traffic"
- 规范化负描述："a car waits in traffic behind a school bus"
- 正描述 1 选择元组：`[6, 16, 4, 0.4444444444444444, 0.42857142857142855]`
- 正描述 2 选择元组：`[11, 19, 3, 0.5714285714285714, 0.7]`
- 最终比较正描述：`positive_1` / "A school bus waits in traffic behind a car."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 1, "negative_start": 0, "negative_end": 1, "positive_lexemes": ["a"], "negative_lexemes": ["a"]}, {"tag": "delete", "positive_start": 1, "positive_end": 2, "negative_start": 1, "negative_end": 1, "positive_lexemes": ["school"], "negative_lexemes": []}, {"tag": "replace", "positive_start": 2, "positive_end": 3, "negative_start": 1, "negative_end": 2, "positive_lexemes": ["bus"], "negative_lexemes": ["car"]}, {"tag": "equal", "positive_start": 3, "positive_end": 8, "negative_start": 2, "negative_end": 7, "positive_lexemes": ["waits", "in", "traffic", "behind", "a"], "negative_lexemes": ["waits", "in", "traffic", "behind", "a"]}, {"tag": "insert", "positive_start": 8, "positive_end": 8, "negative_start": 7, "negative_end": 8, "positive_lexemes": [], "negative_lexemes": ["school"]}, {"tag": "replace", "positive_start": 8, "positive_end": 9, "negative_start": 8, "negative_end": 9, "positive_lexemes": ["car"], "negative_lexemes": ["bus"]}]`
- 共同前缀：`["a"]`
- 正确 contrast hull：`["school", "bus", "waits", "in", "traffic", "behind", "a", "car"]`
- 错误 contrast hull：`["car", "waits", "in", "traffic", "behind", "a", "school", "bus"]`
- 共同后缀：`[]`
- Hull token 覆盖率（正/负/最大）：`[0.9333333333333333, 0.9333333333333333, 0.9333333333333333]`
- 共同前缀模型 token：`[100]`
- 正确 hull 模型 token：IDs `[316, 4165, 500, 2499, 339, 100, 2163, 353, 1946, 5935, 5237, 916, 299, 3751]`；text " school bus waits in traffic behind a car"
- 错误 hull 模型 token：IDs `[3751, 339, 100, 2163, 353, 1946, 5935, 5237, 916, 299, 316, 4165, 500, 2499]`；text " car waits in traffic behind a school bus"
- 第一轮/第二轮分类：`complex_edit` / `large_contrast_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；"maximum_hull_token_coverage_above_75_percent"

### 8. `swap_object:168`

- 负例类型/范围：`swap_object` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A well-lit and well-decorated living room shows a glimpse of a glass front door through the corridor. "
- 原始正描述 2："A glimpse of a glass front door can be seen through the corridor in a well-decorated and well-lit living room."
- 原始负描述："A well-lit and well-decorated glass front door shows a glimpse of a living room through the corridor."
- 规范化正描述 1："a well-lit and well-decorated living room shows a glimpse of a glass front door through the corridor"
- 规范化正描述 2："a glimpse of a glass front door can be seen through the corridor in a well-decorated and well-lit living room"
- 规范化负描述："a well-lit and well-decorated glass front door shows a glimpse of a living room through the corridor"
- 正描述 1 选择元组：`[10, 20, 4, 0.35294117647058826, 0.22]`
- 正描述 2 选择元组：`[27, 35, 4, 0.75, 0.7889908256880734]`
- 最终比较正描述：`positive_1` / "A well-lit and well-decorated living room shows a glimpse of a glass front door through the corridor. "
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 4, "negative_start": 0, "negative_end": 4, "positive_lexemes": ["a", "well-lit", "and", "well-decorated"], "negative_lexemes": ["a", "well-lit", "and", "well-decorated"]}, {"tag": "insert", "positive_start": 4, "positive_end": 4, "negative_start": 4, "negative_end": 5, "positive_lexemes": [], "negative_lexemes": ["glass"]}, {"tag": "replace", "positive_start": 4, "positive_end": 6, "negative_start": 5, "negative_end": 7, "positive_lexemes": ["living", "room"], "negative_lexemes": ["front", "door"]}, {"tag": "equal", "positive_start": 6, "positive_end": 11, "negative_start": 7, "negative_end": 12, "positive_lexemes": ["shows", "a", "glimpse", "of", "a"], "negative_lexemes": ["shows", "a", "glimpse", "of", "a"]}, {"tag": "delete", "positive_start": 11, "positive_end": 12, "negative_start": 12, "negative_end": 12, "positive_lexemes": ["glass"], "negative_lexemes": []}, {"tag": "replace", "positive_start": 12, "positive_end": 14, "negative_start": 12, "negative_end": 14, "positive_lexemes": ["front", "door"], "negative_lexemes": ["living", "room"]}, {"tag": "equal", "positive_start": 14, "positive_end": 17, "negative_start": 14, "negative_end": 17, "positive_lexemes": ["through", "the", "corridor"], "negative_lexemes": ["through", "the", "corridor"]}]`
- 共同前缀：`["a", "well-lit", "and", "well-decorated"]`
- 正确 contrast hull：`["living", "room", "shows", "a", "glimpse", "of", "a", "glass", "front", "door"]`
- 错误 contrast hull：`["glass", "front", "door", "shows", "a", "glimpse", "of", "a", "living", "room"]`
- 共同后缀：`["through", "the", "corridor"]`
- Hull token 覆盖率（正/负/最大）：`[0.55, 0.55, 0.55]`
- 共同前缀模型 token：`[100, 3101, 48, 111, 338, 376, 3101, 48, 713, 102, 336, 1095]`
- 正确 hull 模型 token：IDs `[406, 4917, 1552, 444, 1128, 3032, 299, 492, 111, 467, 115, 573, 354, 299, 492, 111, 1388, 341, 117, 3856, 1041, 336]`；text " living room shows a glimpse of a glass front door"
- 错误 hull 模型 token：IDs `[492, 111, 1388, 341, 117, 3856, 1041, 336, 1128, 3032, 299, 492, 111, 467, 115, 573, 354, 299, 406, 4917, 1552, 444]`；text " glass front door shows a glimpse of a living room"
- 第一轮/第二轮分类：`complex_edit` / `multi_block_local_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 9. `swap_object:172`

- 负例类型/范围：`swap_object` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A person sits on a bench as people walk down a sidewalk. "
- 原始正描述 2："People walk down a sidewalk while a person sits on a bench."
- 原始负描述："People sit on a bench as a person walks down a sidewalk."
- 规范化正描述 1："a person sits on a bench as people walk down a sidewalk"
- 规范化正描述 2："people walk down a sidewalk while a person sits on a bench"
- 规范化负描述："people sit on a bench as a person walks down a sidewalk"
- 正描述 1 选择元组：`[10, 18, 4, 0.5, 0.2545454545454545]`
- 正描述 2 选择元组：`[14, 22, 4, 0.5833333333333334, 0.5344827586206896]`
- 最终比较正描述：`positive_1` / "A person sits on a bench as people walk down a sidewalk. "
- 完整 lexeme 编辑块：`[{"tag": "delete", "positive_start": 0, "positive_end": 1, "negative_start": 0, "negative_end": 0, "positive_lexemes": ["a"], "negative_lexemes": []}, {"tag": "replace", "positive_start": 1, "positive_end": 3, "negative_start": 0, "negative_end": 2, "positive_lexemes": ["person", "sits"], "negative_lexemes": ["people", "sit"]}, {"tag": "equal", "positive_start": 3, "positive_end": 7, "negative_start": 2, "negative_end": 6, "positive_lexemes": ["on", "a", "bench", "as"], "negative_lexemes": ["on", "a", "bench", "as"]}, {"tag": "insert", "positive_start": 7, "positive_end": 7, "negative_start": 6, "negative_end": 7, "positive_lexemes": [], "negative_lexemes": ["a"]}, {"tag": "replace", "positive_start": 7, "positive_end": 9, "negative_start": 7, "negative_end": 9, "positive_lexemes": ["people", "walk"], "negative_lexemes": ["person", "walks"]}, {"tag": "equal", "positive_start": 9, "positive_end": 12, "negative_start": 9, "negative_end": 12, "positive_lexemes": ["down", "a", "sidewalk"], "negative_lexemes": ["down", "a", "sidewalk"]}]`
- 共同前缀：`[]`
- 正确 contrast hull：`["a", "person", "sits", "on", "a", "bench", "as", "people", "walk"]`
- 错误 contrast hull：`["people", "sit", "on", "a", "bench", "as", "a", "person", "walks"]`
- 共同后缀：`["down", "a", "sidewalk"]`
- Hull token 覆盖率（正/负/最大）：`[0.7058823529411765, 0.7222222222222222, 0.7222222222222222]`
- 共同前缀模型 token：`[]`
- 正确 hull 模型 token：IDs `[100, 2198, 316, 2163, 619, 299, 6141, 550, 523, 2975, 339, 5864]`；text "a person sits on a bench as people walk"
- 错误 hull 模型 token：IDs `[653, 2643, 5305, 619, 299, 6141, 550, 523, 299, 2198, 339, 352, 1275]`；text "people sit on a bench as a person walks"
- 第一轮/第二轮分类：`complex_edit` / `multi_block_local_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 10. `swap_object:178`

- 负例类型/范围：`swap_object` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："a white horse pulling a carriage with a person on it."
- 原始正描述 2："A person is riding in a carriage that is being pulled by a white horse."
- 原始负描述："A person pulling a carriage with a white horse on it."
- 规范化正描述 1："a white horse pulling a carriage with a person on it"
- 规范化正描述 2："a person is riding in a carriage that is being pulled by a white horse"
- 规范化负描述："a person pulling a carriage with a white horse on it"
- 正描述 1 选择元组：`[6, 16, 4, 0.36363636363636365, 0.34615384615384615]`
- 正描述 2 选择元组：`[12, 22, 5, 0.6666666666666666, 0.5285714285714286]`
- 最终比较正描述：`positive_1` / "a white horse pulling a carriage with a person on it."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 1, "negative_start": 0, "negative_end": 1, "positive_lexemes": ["a"], "negative_lexemes": ["a"]}, {"tag": "delete", "positive_start": 1, "positive_end": 2, "negative_start": 1, "negative_end": 1, "positive_lexemes": ["white"], "negative_lexemes": []}, {"tag": "replace", "positive_start": 2, "positive_end": 3, "negative_start": 1, "negative_end": 2, "positive_lexemes": ["horse"], "negative_lexemes": ["person"]}, {"tag": "equal", "positive_start": 3, "positive_end": 8, "negative_start": 2, "negative_end": 7, "positive_lexemes": ["pulling", "a", "carriage", "with", "a"], "negative_lexemes": ["pulling", "a", "carriage", "with", "a"]}, {"tag": "insert", "positive_start": 8, "positive_end": 8, "negative_start": 7, "negative_end": 8, "positive_lexemes": [], "negative_lexemes": ["white"]}, {"tag": "replace", "positive_start": 8, "positive_end": 9, "negative_start": 8, "negative_end": 9, "positive_lexemes": ["person"], "negative_lexemes": ["horse"]}, {"tag": "equal", "positive_start": 9, "positive_end": 11, "negative_start": 9, "negative_end": 11, "positive_lexemes": ["on", "it"], "negative_lexemes": ["on", "it"]}]`
- 共同前缀：`["a"]`
- 正确 contrast hull：`["white", "horse", "pulling", "a", "carriage", "with", "a", "person"]`
- 错误 contrast hull：`["person", "pulling", "a", "carriage", "with", "a", "white", "horse"]`
- 共同后缀：`["on", "it"]`
- Hull token 覆盖率（正/负/最大）：`[0.8333333333333334, 0.8333333333333334, 0.8333333333333334]`
- 共同前缀模型 token：`[100]`
- 正确 hull 模型 token：IDs `[654, 1078, 429, 336, 573, 344, 3800, 350, 299, 3751, 809, 834, 599, 299, 2198]`；text " white horse pulling a carriage with a person"
- 错误 hull 模型 token：IDs `[2198, 344, 3800, 350, 299, 3751, 809, 834, 599, 299, 654, 1078, 429, 336, 573]`；text " person pulling a carriage with a white horse"
- 第一轮/第二轮分类：`ambiguous_source` / `large_contrast_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；"maximum_hull_token_coverage_above_75_percent"

### 11. `swap_object:182`

- 负例类型/范围：`swap_object` / `{"canonical": true, "pilot": true, "formal": false, "certifying_formal": false}`
- 原始正描述 1："Vase full of feathers sitting on a table next to a floral drape."
- 原始正描述 2："The floral drape is positioned adjacent to the table, which has a vase full of feathers sitting on it."
- 原始负描述："A floral drape full of feathers sitting on a table next to a vase."
- 规范化正描述 1："vase full of feathers sitting on a table next to a floral drape"
- 规范化正描述 2："the floral drape is positioned adjacent to the table , which has a vase full of feathers sitting on it"
- 规范化负描述："a floral drape full of feathers sitting on a table next to a vase"
- 正描述 1 选择元组：`[7, 27, 4, 0.35714285714285715, 0.3384615384615385]`
- 正描述 2 选择元组：`[26, 34, 3, 0.8, 0.6666666666666666]`
- 最终比较正描述：`positive_1` / "Vase full of feathers sitting on a table next to a floral drape."
- 完整 lexeme 编辑块：`[{"tag": "insert", "positive_start": 0, "positive_end": 0, "negative_start": 0, "negative_end": 2, "positive_lexemes": [], "negative_lexemes": ["a", "floral"]}, {"tag": "replace", "positive_start": 0, "positive_end": 1, "negative_start": 2, "negative_end": 3, "positive_lexemes": ["vase"], "negative_lexemes": ["drape"]}, {"tag": "equal", "positive_start": 1, "positive_end": 11, "negative_start": 3, "negative_end": 13, "positive_lexemes": ["full", "of", "feathers", "sitting", "on", "a", "table", "next", "to", "a"], "negative_lexemes": ["full", "of", "feathers", "sitting", "on", "a", "table", "next", "to", "a"]}, {"tag": "delete", "positive_start": 11, "positive_end": 12, "negative_start": 13, "negative_end": 13, "positive_lexemes": ["floral"], "negative_lexemes": []}, {"tag": "replace", "positive_start": 12, "positive_end": 13, "negative_start": 13, "negative_end": 14, "positive_lexemes": ["drape"], "negative_lexemes": ["vase"]}]`
- 共同前缀：`[]`
- 正确 contrast hull：`["vase", "full", "of", "feathers", "sitting", "on", "a", "table", "next", "to", "a", "floral", "drape"]`
- 错误 contrast hull：`["a", "floral", "drape", "full", "of", "feathers", "sitting", "on", "a", "table", "next", "to", "a", "vase"]`
- 共同后缀：`[]`
- Hull token 覆盖率（正/负/最大）：`[1.0, 1.0, 1.0]`
- 共同前缀模型 token：`[]`
- 正确 hull 模型 token：IDs `[121, 812, 5840, 354, 1270, 2132, 118, 5305, 2912, 619, 299, 2630, 4658, 364, 299, 3687, 336, 352, 373, 559, 653]`；text "vase full of feathers sitting on a table next to a floral drape"
- 错误 hull 模型 token：IDs `[100, 3687, 336, 352, 373, 559, 653, 5840, 354, 1270, 2132, 118, 5305, 2912, 619, 299, 2630, 4658, 364, 299, 603, 812]`；text "a floral drape full of feathers sitting on a table next to a vase"
- 第一轮/第二轮分类：`complex_edit` / `whole_sentence_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；"at_least_one_hull_covers_all_model_tokens"

### 12. `swap_object:189`

- 负例类型/范围：`swap_object` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A camera sits on a tripod connected to a laptop."
- 原始正描述 2："The laptop is connected to a tripod with a camera positioned on top of it."
- 原始负描述："A laptop sits on a tripod connected to a camera."
- 规范化正描述 1："a camera sits on a tripod connected to a laptop"
- 规范化正描述 2："the laptop is connected to a tripod with a camera positioned on top of it"
- 规范化负描述："a laptop sits on a tripod connected to a camera"
- 正描述 1 选择元组：`[4, 18, 2, 0.2, 0.2127659574468085]`
- 正描述 2 选择元组：`[15, 25, 6, 0.7333333333333333, 0.6164383561643836]`
- 最终比较正描述：`positive_1` / "A camera sits on a tripod connected to a laptop."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 1, "negative_start": 0, "negative_end": 1, "positive_lexemes": ["a"], "negative_lexemes": ["a"]}, {"tag": "replace", "positive_start": 1, "positive_end": 2, "negative_start": 1, "negative_end": 2, "positive_lexemes": ["camera"], "negative_lexemes": ["laptop"]}, {"tag": "equal", "positive_start": 2, "positive_end": 9, "negative_start": 2, "negative_end": 9, "positive_lexemes": ["sits", "on", "a", "tripod", "connected", "to", "a"], "negative_lexemes": ["sits", "on", "a", "tripod", "connected", "to", "a"]}, {"tag": "replace", "positive_start": 9, "positive_end": 10, "negative_start": 9, "negative_end": 10, "positive_lexemes": ["laptop"], "negative_lexemes": ["camera"]}]`
- 共同前缀：`["a"]`
- 正确 contrast hull：`["camera", "sits", "on", "a", "tripod", "connected", "to", "a", "laptop"]`
- 错误 contrast hull：`["laptop", "sits", "on", "a", "tripod", "connected", "to", "a", "camera"]`
- 共同后缀：`[]`
- Hull token 覆盖率（正/负/最大）：`[0.95, 0.95, 0.95]`
- 共同前缀模型 token：`[100]`
- 正确 hull 模型 token：IDs `[317, 497, 311, 100, 316, 2163, 619, 299, 4429, 115, 1318, 614, 6049, 382, 364, 299, 3090, 875, 1506]`；text " camera sits on a tripod connected to a laptop"
- 错误 hull 模型 token：IDs `[3090, 875, 1506, 316, 2163, 619, 299, 4429, 115, 1318, 614, 6049, 382, 364, 299, 317, 497, 311, 100]`；text " laptop sits on a tripod connected to a camera"
- 第一轮/第二轮分类：`complex_edit` / `large_contrast_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；"maximum_hull_token_coverage_above_75_percent"

### 13. `swap_object:194`

- 负例类型/范围：`swap_object` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A person is holding a baby with another young child beside the person."
- 原始正描述 2："A young child is standing beside a person who is holding a baby."
- 原始负描述："A young child is holding a baby with another person beside the child."
- 规范化正描述 1："a person is holding a baby with another young child beside the person"
- 规范化正描述 2："a young child is standing beside a person who is holding a baby"
- 规范化负描述："a young child is holding a baby with another person beside the child"
- 正描述 1 选择元组：`[8, 24, 5, 0.38461538461538464, 0.4057971014492754]`
- 正描述 2 选择元组：`[18, 18, 1, 0.6923076923076923, 0.5588235294117647]`
- 最终比较正描述：`positive_1` / "A person is holding a baby with another young child beside the person."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 1, "negative_start": 0, "negative_end": 1, "positive_lexemes": ["a"], "negative_lexemes": ["a"]}, {"tag": "insert", "positive_start": 1, "positive_end": 1, "negative_start": 1, "negative_end": 2, "positive_lexemes": [], "negative_lexemes": ["young"]}, {"tag": "replace", "positive_start": 1, "positive_end": 2, "negative_start": 2, "negative_end": 3, "positive_lexemes": ["person"], "negative_lexemes": ["child"]}, {"tag": "equal", "positive_start": 2, "positive_end": 8, "negative_start": 3, "negative_end": 9, "positive_lexemes": ["is", "holding", "a", "baby", "with", "another"], "negative_lexemes": ["is", "holding", "a", "baby", "with", "another"]}, {"tag": "delete", "positive_start": 8, "positive_end": 9, "negative_start": 9, "negative_end": 9, "positive_lexemes": ["young"], "negative_lexemes": []}, {"tag": "replace", "positive_start": 9, "positive_end": 10, "negative_start": 9, "negative_end": 10, "positive_lexemes": ["child"], "negative_lexemes": ["person"]}, {"tag": "equal", "positive_start": 10, "positive_end": 12, "negative_start": 10, "negative_end": 12, "positive_lexemes": ["beside", "the"], "negative_lexemes": ["beside", "the"]}, {"tag": "replace", "positive_start": 12, "positive_end": 13, "negative_start": 12, "negative_end": 13, "positive_lexemes": ["person"], "negative_lexemes": ["child"]}]`
- 共同前缀：`["a"]`
- 正确 contrast hull：`["person", "is", "holding", "a", "baby", "with", "another", "young", "child", "beside", "the", "person"]`
- 错误 contrast hull：`["young", "child", "is", "holding", "a", "baby", "with", "another", "person", "beside", "the", "child"]`
- 共同后缀：`[]`
- Hull token 覆盖率（正/负/最大）：`[0.95, 0.95, 0.95]`
- 共同前缀模型 token：`[100]`
- 正确 hull 模型 token：IDs `[2198, 395, 429, 2569, 350, 299, 363, 572, 124, 599, 5467, 401, 1685, 6109, 363, 329, 688, 309, 2198]`；text " person is holding a baby with another young child beside the person"
- 错误 hull 模型 token：IDs `[401, 1685, 6109, 395, 429, 2569, 350, 299, 363, 572, 124, 599, 5467, 2198, 363, 329, 688, 309, 6109]`；text " young child is holding a baby with another person beside the child"
- 第一轮/第二轮分类：`complex_edit` / `large_contrast_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；"maximum_hull_token_coverage_above_75_percent"

### 14. `swap_object:195`

- 负例类型/范围：`swap_object` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："Two brown horses pull a plow, steered by a person behind."
- 原始正描述 2："The person steers two brown horses from behind that pull a plow."
- 原始负描述："A person pulls a plow, steered by two brown horses in front."
- 规范化正描述 1："two brown horses pull a plow , steered by a person behind"
- 规范化正描述 2："the person steers two brown horses from behind that pull a plow"
- 规范化负描述："a person pulls a plow , steered by two brown horses in front"
- 正描述 1 选择元组：`[15, 25, 4, 0.6923076923076923, 0.55]`
- 正描述 2 选择元组：`[23, 25, 3, 0.9230769230769231, 0.7142857142857143]`
- 最终比较正描述：`positive_1` / "Two brown horses pull a plow, steered by a person behind."
- 完整 lexeme 编辑块：`[{"tag": "delete", "positive_start": 0, "positive_end": 1, "negative_start": 0, "negative_end": 0, "positive_lexemes": ["two"], "negative_lexemes": []}, {"tag": "replace", "positive_start": 1, "positive_end": 4, "negative_start": 0, "negative_end": 3, "positive_lexemes": ["brown", "horses", "pull"], "negative_lexemes": ["a", "person", "pulls"]}, {"tag": "equal", "positive_start": 4, "positive_end": 9, "negative_start": 3, "negative_end": 8, "positive_lexemes": ["a", "plow", ",", "steered", "by"], "negative_lexemes": ["a", "plow", ",", "steered", "by"]}, {"tag": "insert", "positive_start": 9, "positive_end": 9, "negative_start": 8, "negative_end": 10, "positive_lexemes": [], "negative_lexemes": ["two", "brown"]}, {"tag": "replace", "positive_start": 9, "positive_end": 12, "negative_start": 10, "negative_end": 13, "positive_lexemes": ["a", "person", "behind"], "negative_lexemes": ["horses", "in", "front"]}]`
- 共同前缀：`[]`
- 正确 contrast hull：`["two", "brown", "horses", "pull", "a", "plow", ",", "steered", "by", "a", "person", "behind"]`
- 错误 contrast hull：`["a", "person", "pulls", "a", "plow", ",", "steered", "by", "two", "brown", "horses", "in", "front"]`
- 共同后缀：`[]`
- Hull token 覆盖率（正/负/最大）：`[1.0, 1.0, 1.0]`
- 共同前缀模型 token：`[]`
- 正确 hull 模型 token：IDs `[119, 122, 114, 363, 2079, 113, 429, 1945, 329, 344, 3800, 299, 344, 1030, 256, 47, 580, 104, 964, 103, 769, 299, 2198, 5237, 916]`；text "two brown horses pull a plow , steered by a person behind"
- 错误 hull 模型 token：IDs `[100, 2198, 344, 3800, 118, 299, 344, 1030, 256, 47, 580, 104, 964, 103, 769, 2102, 363, 2079, 113, 429, 1945, 329, 353, 341, 117, 3856]`；text "a person pulls a plow , steered by two brown horses in front"
- 第一轮/第二轮分类：`ambiguous_source` / `whole_sentence_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；"at_least_one_hull_covers_all_model_tokens"

### 15. `swap_object:205`

- 负例类型/范围：`swap_object` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": false}`
- 原始正描述 1："A boy getting ready to blow out birthday candles with a girl watching."
- 原始正描述 2："A girl is watching a boy getting ready to blow out birthday candles."
- 原始负描述："A girl getting ready to blow out birthday candles with a boy watching."
- 规范化正描述 1："a boy getting ready to blow out birthday candles with a girl watching"
- 规范化正描述 2："a girl is watching a boy getting ready to blow out birthday candles"
- 规范化负描述："a girl getting ready to blow out birthday candles with a boy watching"
- 正描述 1 选择元组：`[4, 22, 2, 0.15384615384615385, 0.11594202898550725]`
- 正描述 2 选择元组：`[8, 22, 2, 0.6153846153846154, 0.5507246376811594]`
- 最终比较正描述：`positive_1` / "A boy getting ready to blow out birthday candles with a girl watching."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 1, "negative_start": 0, "negative_end": 1, "positive_lexemes": ["a"], "negative_lexemes": ["a"]}, {"tag": "replace", "positive_start": 1, "positive_end": 2, "negative_start": 1, "negative_end": 2, "positive_lexemes": ["boy"], "negative_lexemes": ["girl"]}, {"tag": "equal", "positive_start": 2, "positive_end": 11, "negative_start": 2, "negative_end": 11, "positive_lexemes": ["getting", "ready", "to", "blow", "out", "birthday", "candles", "with", "a"], "negative_lexemes": ["getting", "ready", "to", "blow", "out", "birthday", "candles", "with", "a"]}, {"tag": "replace", "positive_start": 11, "positive_end": 12, "negative_start": 11, "negative_end": 12, "positive_lexemes": ["girl"], "negative_lexemes": ["boy"]}, {"tag": "equal", "positive_start": 12, "positive_end": 13, "negative_start": 12, "negative_end": 13, "positive_lexemes": ["watching"], "negative_lexemes": ["watching"]}]`
- 共同前缀：`["a"]`
- 正确 contrast hull：`["boy", "getting", "ready", "to", "blow", "out", "birthday", "candles", "with", "a", "girl"]`
- 错误 contrast hull：`["girl", "getting", "ready", "to", "blow", "out", "birthday", "candles", "with", "a", "boy"]`
- 共同后缀：`["watching"]`
- Hull token 覆盖率（正/负/最大）：`[0.84, 0.84, 0.84]`
- 共同前缀模型 token：`[100]`
- 正确 hull 模型 token：IDs `[1847, 124, 2350, 2912, 3094, 124, 364, 363, 1030, 1695, 5231, 495, 1753, 541, 103, 1907, 599, 299, 492, 639, 111]`；text " boy getting ready to blow out birthday candles with a girl"
- 错误 hull 模型 token：IDs `[492, 639, 111, 2350, 2912, 3094, 124, 364, 363, 1030, 1695, 5231, 495, 1753, 541, 103, 1907, 599, 299, 1847, 124]`；text " girl getting ready to blow out birthday candles with a boy"
- 第一轮/第二轮分类：`complex_edit` / `large_contrast_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；"maximum_hull_token_coverage_above_75_percent"

### 16. `swap_object:210`

- 负例类型/范围：`swap_object` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": false}`
- 原始正描述 1："Two persons play the Nintendo Wii console while others watch"
- 原始正描述 2："The Nintendo Wii console is being played by two persons while other people watch."
- 原始负描述："Others play the Nintendo Wii console while two persons watch."
- 规范化正描述 1："two persons play the nintendo wii console while others watch"
- 规范化正描述 2："the nintendo wii console is being played by two persons while other people watch"
- 规范化负描述："others play the nintendo wii console while two persons watch"
- 正描述 1 选择元组：`[6, 18, 4, 0.4, 0.23333333333333334]`
- 正描述 2 选择元组：`[10, 22, 4, 0.6428571428571429, 0.575]`
- 最终比较正描述：`positive_1` / "Two persons play the Nintendo Wii console while others watch"
- 完整 lexeme 编辑块：`[{"tag": "delete", "positive_start": 0, "positive_end": 1, "negative_start": 0, "negative_end": 0, "positive_lexemes": ["two"], "negative_lexemes": []}, {"tag": "replace", "positive_start": 1, "positive_end": 2, "negative_start": 0, "negative_end": 1, "positive_lexemes": ["persons"], "negative_lexemes": ["others"]}, {"tag": "equal", "positive_start": 2, "positive_end": 8, "negative_start": 1, "negative_end": 7, "positive_lexemes": ["play", "the", "nintendo", "wii", "console", "while"], "negative_lexemes": ["play", "the", "nintendo", "wii", "console", "while"]}, {"tag": "insert", "positive_start": 8, "positive_end": 8, "negative_start": 7, "negative_end": 8, "positive_lexemes": [], "negative_lexemes": ["two"]}, {"tag": "replace", "positive_start": 8, "positive_end": 9, "negative_start": 8, "negative_end": 9, "positive_lexemes": ["others"], "negative_lexemes": ["persons"]}, {"tag": "equal", "positive_start": 9, "positive_end": 10, "negative_start": 9, "negative_end": 10, "positive_lexemes": ["watch"], "negative_lexemes": ["watch"]}]`
- 共同前缀：`[]`
- 正确 contrast hull：`["two", "persons", "play", "the", "nintendo", "wii", "console", "while", "others"]`
- 错误 contrast hull：`["others", "play", "the", "nintendo", "wii", "console", "while", "two", "persons"]`
- 共同后缀：`["watch"]`
- Hull token 覆盖率（正/负/最大）：`[0.9, 0.8888888888888888, 0.9]`
- 共同前缀模型 token：`[]`
- 正确 hull 模型 token：IDs `[119, 122, 114, 2198, 118, 2865, 309, 399, 806, 901, 114, 339, 108, 108, 6160, 3052, 1649, 118]`；text "two persons play the nintendo wii console while others"
- 错误 hull 模型 token：IDs `[3861, 118, 2865, 309, 399, 806, 901, 114, 339, 108, 108, 6160, 3052, 2102, 2198, 118]`；text "others play the nintendo wii console while two persons"
- 第一轮/第二轮分类：`complex_edit` / `large_contrast_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；"maximum_hull_token_coverage_above_75_percent"

### 17. `swap_object:235`

- 负例类型/范围：`swap_object` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："Two persons biting a surfboard with a shark on it."
- 原始正描述 2："A couple of persons are biting a surfboard that has a shark on it."
- 原始负描述："A shark biting a surfboard with two persons on it."
- 规范化正描述 1："two persons biting a surfboard with a shark on it"
- 规范化正描述 2："a couple of persons are biting a surfboard that has a shark on it"
- 规范化负描述："a shark biting a surfboard with two persons on it"
- 正描述 1 选择元组：`[8, 16, 2, 0.4, 0.40816326530612246]`
- 正描述 2 选择元组：`[12, 18, 4, 0.5714285714285714, 0.49230769230769234]`
- 最终比较正描述：`positive_1` / "Two persons biting a surfboard with a shark on it."
- 完整 lexeme 编辑块：`[{"tag": "replace", "positive_start": 0, "positive_end": 2, "negative_start": 0, "negative_end": 2, "positive_lexemes": ["two", "persons"], "negative_lexemes": ["a", "shark"]}, {"tag": "equal", "positive_start": 2, "positive_end": 6, "negative_start": 2, "negative_end": 6, "positive_lexemes": ["biting", "a", "surfboard", "with"], "negative_lexemes": ["biting", "a", "surfboard", "with"]}, {"tag": "replace", "positive_start": 6, "positive_end": 8, "negative_start": 6, "negative_end": 8, "positive_lexemes": ["a", "shark"], "negative_lexemes": ["two", "persons"]}, {"tag": "equal", "positive_start": 8, "positive_end": 10, "negative_start": 8, "negative_end": 10, "positive_lexemes": ["on", "it"], "negative_lexemes": ["on", "it"]}]`
- 共同前缀：`[]`
- 正确 contrast hull：`["two", "persons", "biting", "a", "surfboard", "with", "a", "shark"]`
- 错误 contrast hull：`["a", "shark", "biting", "a", "surfboard", "with", "two", "persons"]`
- 共同后缀：`["on", "it"]`
- Hull token 覆盖率（正/负/最大）：`[0.8947368421052632, 0.8823529411764706, 0.8947368421052632]`
- 共同前缀模型 token：`[]`
- 正确 hull 模型 token：IDs `[119, 122, 114, 2198, 118, 4003, 350, 299, 3946, 105, 101, 114, 1433, 599, 299, 1128, 2000]`；text "two persons biting a surfboard with a shark"
- 错误 hull 模型 token：IDs `[100, 1128, 2000, 4003, 350, 299, 3946, 105, 101, 114, 1433, 599, 2102, 2198, 118]`；text "a shark biting a surfboard with two persons"
- 第一轮/第二轮分类：`complex_edit` / `large_contrast_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；"maximum_hull_token_coverage_above_75_percent"

### 18. `swap_object:238`

- 负例类型/范围：`swap_object` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A brown and black cat laying on laptop next to a chair."
- 原始正描述 2："A cat, which is black and brown, is positioned on top of a laptop that is adjacent to a chair."
- 原始负描述："A brown and black cat laying on a chair next to a laptop."
- 规范化正描述 1："a brown and black cat laying on laptop next to a chair"
- 规范化正描述 2："a cat , which is black and brown , is positioned on top of a laptop that is adjacent to a chair"
- 规范化负描述："a brown and black cat laying on a chair next to a laptop"
- 正描述 1 选择元组：`[5, 11, 3, 0.23076923076923078, 0.23214285714285715]`
- 正描述 2 选择元组：`[23, 33, 8, 0.7272727272727273, 0.6842105263157895]`
- 最终比较正描述：`positive_1` / "A brown and black cat laying on laptop next to a chair."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 7, "negative_start": 0, "negative_end": 7, "positive_lexemes": ["a", "brown", "and", "black", "cat", "laying", "on"], "negative_lexemes": ["a", "brown", "and", "black", "cat", "laying", "on"]}, {"tag": "insert", "positive_start": 7, "positive_end": 7, "negative_start": 7, "negative_end": 8, "positive_lexemes": [], "negative_lexemes": ["a"]}, {"tag": "replace", "positive_start": 7, "positive_end": 8, "negative_start": 8, "negative_end": 9, "positive_lexemes": ["laptop"], "negative_lexemes": ["chair"]}, {"tag": "equal", "positive_start": 8, "positive_end": 11, "negative_start": 9, "negative_end": 12, "positive_lexemes": ["next", "to", "a"], "negative_lexemes": ["next", "to", "a"]}, {"tag": "replace", "positive_start": 11, "positive_end": 12, "negative_start": 12, "negative_end": 13, "positive_lexemes": ["chair"], "negative_lexemes": ["laptop"]}]`
- 共同前缀：`["a", "brown", "and", "black", "cat", "laying", "on"]`
- 正确 contrast hull：`["laptop", "next", "to", "a", "chair"]`
- 错误 contrast hull：`["a", "chair", "next", "to", "a", "laptop"]`
- 共同后缀：`[]`
- Hull token 覆盖率（正/负/最大）：`[0.4, 0.42857142857142855, 0.42857142857142855]`
- 共同前缀模型 token：`[100, 363, 2079, 113, 376, 2597, 1637, 3706, 406, 655, 350, 619]`
- 正确 hull 模型 token：IDs `[3090, 875, 1506, 4658, 364, 299, 890, 3709]`；text " laptop next to a chair"
- 错误 hull 模型 token：IDs `[299, 890, 3709, 4658, 364, 299, 3090, 875, 1506]`；text " a chair next to a laptop"
- 第一轮/第二轮分类：`complex_edit` / `multi_block_local_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 19. `swap_object:239`

- 负例类型/范围：`swap_object` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A statue is sitting on a bench and a person sits on a cement block."
- 原始正描述 2："A person is sitting on a cement block while a statue is positioned on a bench."
- 原始负描述："A person is sitting on a bench and a statue sits on a cement block."
- 规范化正描述 1："a statue is sitting on a bench and a person sits on a cement block"
- 规范化正描述 2："a person is sitting on a cement block while a statue is positioned on a bench"
- 规范化负描述："a person is sitting on a bench and a statue sits on a cement block"
- 正描述 1 选择元组：`[4, 18, 2, 0.13333333333333333, 0.18181818181818182]`
- 正描述 2 选择元组：`[11, 19, 6, 0.4375, 0.4025974025974026]`
- 最终比较正描述：`positive_1` / "A statue is sitting on a bench and a person sits on a cement block."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 1, "negative_start": 0, "negative_end": 1, "positive_lexemes": ["a"], "negative_lexemes": ["a"]}, {"tag": "replace", "positive_start": 1, "positive_end": 2, "negative_start": 1, "negative_end": 2, "positive_lexemes": ["statue"], "negative_lexemes": ["person"]}, {"tag": "equal", "positive_start": 2, "positive_end": 9, "negative_start": 2, "negative_end": 9, "positive_lexemes": ["is", "sitting", "on", "a", "bench", "and", "a"], "negative_lexemes": ["is", "sitting", "on", "a", "bench", "and", "a"]}, {"tag": "replace", "positive_start": 9, "positive_end": 10, "negative_start": 9, "negative_end": 10, "positive_lexemes": ["person"], "negative_lexemes": ["statue"]}, {"tag": "equal", "positive_start": 10, "positive_end": 15, "negative_start": 10, "negative_end": 15, "positive_lexemes": ["sits", "on", "a", "cement", "block"], "negative_lexemes": ["sits", "on", "a", "cement", "block"]}]`
- 共同前缀：`["a"]`
- 正确 contrast hull：`["statue", "is", "sitting", "on", "a", "bench", "and", "a", "person"]`
- 错误 contrast hull：`["person", "is", "sitting", "on", "a", "bench", "and", "a", "statue"]`
- 共同后缀：`["sits", "on", "a", "cement", "block"]`
- Hull token 覆盖率（正/负/最大）：`[0.5454545454545454, 0.5454545454545454, 0.5454545454545454]`
- 共同前缀模型 token：`[100]`
- 正确 hull 模型 token：IDs `[5643, 922, 395, 5305, 2912, 619, 299, 6141, 550, 376, 299, 2198]`；text " statue is sitting on a bench and a person"
- 错误 hull 模型 token：IDs `[2198, 395, 5305, 2912, 619, 299, 6141, 550, 376, 299, 5643, 922]`；text " person is sitting on a bench and a statue"
- 第一轮/第二轮分类：`complex_edit` / `multi_block_local_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 20. `swap_object:28`

- 负例类型/范围：`swap_object` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A vintage red car in front of a vintage army prop plane."
- 原始正描述 2："A vintage car that is red in color is parked in front of a vintage army prop plane."
- 原始负描述："A vintage army prop plane in front of a vintage red car."
- 规范化正描述 1："a vintage red car in front of a vintage army prop plane"
- 规范化正描述 2："a vintage car that is red in color is parked in front of a vintage army prop plane"
- 规范化负描述："a vintage army prop plane in front of a vintage red car"
- 正描述 1 选择元组：`[10, 20, 4, 0.5, 0.43636363636363634]`
- 正描述 2 选择元组：`[16, 26, 4, 0.6111111111111112, 0.4634146341463415]`
- 最终比较正描述：`positive_1` / "A vintage red car in front of a vintage army prop plane."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 2, "negative_start": 0, "negative_end": 2, "positive_lexemes": ["a", "vintage"], "negative_lexemes": ["a", "vintage"]}, {"tag": "insert", "positive_start": 2, "positive_end": 2, "negative_start": 2, "negative_end": 3, "positive_lexemes": [], "negative_lexemes": ["army"]}, {"tag": "replace", "positive_start": 2, "positive_end": 4, "negative_start": 3, "negative_end": 5, "positive_lexemes": ["red", "car"], "negative_lexemes": ["prop", "plane"]}, {"tag": "equal", "positive_start": 4, "positive_end": 9, "negative_start": 5, "negative_end": 10, "positive_lexemes": ["in", "front", "of", "a", "vintage"], "negative_lexemes": ["in", "front", "of", "a", "vintage"]}, {"tag": "delete", "positive_start": 9, "positive_end": 10, "negative_start": 10, "negative_end": 10, "positive_lexemes": ["army"], "negative_lexemes": []}, {"tag": "replace", "positive_start": 10, "positive_end": 12, "negative_start": 10, "negative_end": 12, "positive_lexemes": ["prop", "plane"], "negative_lexemes": ["red", "car"]}]`
- 共同前缀：`["a", "vintage"]`
- 正确 contrast hull：`["red", "car", "in", "front", "of", "a", "vintage", "army", "prop", "plane"]`
- 错误 contrast hull：`["army", "prop", "plane", "in", "front", "of", "a", "vintage", "red", "car"]`
- 共同后缀：`[]`
- Hull token 覆盖率（正/负/最大）：`[0.8095238095238095, 0.8095238095238095, 0.8095238095238095]`
- 共同前缀模型 token：`[100, 603, 806, 834]`
- 正确 hull 模型 token：IDs `[5534, 3751, 353, 341, 117, 3856, 354, 299, 603, 806, 834, 1225, 3309, 540, 115, 4140, 104]`；text " red car in front of a vintage army prop plane"
- 错误 hull 模型 token：IDs `[1225, 3309, 540, 115, 4140, 104, 353, 341, 117, 3856, 354, 299, 603, 806, 834, 5534, 3751]`；text " army prop plane in front of a vintage red car"
- 第一轮/第二轮分类：`ambiguous_source` / `large_contrast_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；"maximum_hull_token_coverage_above_75_percent"

### 21. `swap_object:44`

- 负例类型/范围：`swap_object` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："person flying a kite on the beach while others run along the sand."
- 原始正描述 2："people are running along the sand while a person is flying a kite on the beach."
- 原始负描述："Others flying a kite on the beach while a person runs along the sand."
- 规范化正描述 1："person flying a kite on the beach while others run along the sand"
- 规范化正描述 2："people are running along the sand while a person is flying a kite on the beach"
- 规范化负描述："others flying a kite on the beach while a person runs along the sand"
- 正描述 1 选择元组：`[7, 21, 3, 0.2857142857142857, 0.16176470588235295]`
- 正描述 2 选择元组：`[20, 30, 6, 0.75, 0.5256410256410257]`
- 最终比较正描述：`positive_1` / "person flying a kite on the beach while others run along the sand."
- 完整 lexeme 编辑块：`[{"tag": "replace", "positive_start": 0, "positive_end": 1, "negative_start": 0, "negative_end": 1, "positive_lexemes": ["person"], "negative_lexemes": ["others"]}, {"tag": "equal", "positive_start": 1, "positive_end": 8, "negative_start": 1, "negative_end": 8, "positive_lexemes": ["flying", "a", "kite", "on", "the", "beach", "while"], "negative_lexemes": ["flying", "a", "kite", "on", "the", "beach", "while"]}, {"tag": "insert", "positive_start": 8, "positive_end": 8, "negative_start": 8, "negative_end": 9, "positive_lexemes": [], "negative_lexemes": ["a"]}, {"tag": "replace", "positive_start": 8, "positive_end": 10, "negative_start": 9, "negative_end": 11, "positive_lexemes": ["others", "run"], "negative_lexemes": ["person", "runs"]}, {"tag": "equal", "positive_start": 10, "positive_end": 13, "negative_start": 11, "negative_end": 14, "positive_lexemes": ["along", "the", "sand"], "negative_lexemes": ["along", "the", "sand"]}]`
- 共同前缀：`[]`
- 正确 contrast hull：`["person", "flying", "a", "kite", "on", "the", "beach", "while", "others", "run"]`
- 错误 contrast hull：`["others", "flying", "a", "kite", "on", "the", "beach", "while", "a", "person", "runs"]`
- 共同后缀：`["along", "the", "sand"]`
- Hull token 覆盖率（正/负/最大）：`[0.8, 0.8095238095238095, 0.8095238095238095]`
- 共同前缀模型 token：`[]`
- 正确 hull 模型 token：IDs `[115, 2019, 341, 542, 350, 299, 914, 1078, 619, 309, 600, 1268, 3052, 1649, 118, 3161]`；text "person flying a kite on the beach while others run"
- 错误 hull 模型 token：IDs `[3861, 118, 341, 542, 350, 299, 914, 1078, 619, 309, 600, 1268, 3052, 299, 2198, 3161, 118]`；text "others flying a kite on the beach while a person runs"
- 第一轮/第二轮分类：`complex_edit` / `large_contrast_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；"maximum_hull_token_coverage_above_75_percent"

### 22. `swap_object:49`

- 负例类型/范围：`swap_object` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A large giraffe looks at a smaller giraffe looking over a fence."
- 原始正描述 2："A smaller giraffe is looking over a fence while a larger giraffe looks at it."
- 原始负描述："A smaller giraffe looks at a larger giraffe looking over a fence."
- 规范化正描述 1："a large giraffe looks at a smaller giraffe looking over a fence"
- 规范化正描述 2："a smaller giraffe is looking over a fence while a larger giraffe looks at it"
- 规范化负描述："a smaller giraffe looks at a larger giraffe looking over a fence"
- 正描述 1 选择元组：`[4, 12, 2, 0.16666666666666666, 0.140625]`
- 正描述 2 选择元组：`[15, 21, 4, 0.6666666666666666, 0.4868421052631579]`
- 最终比较正描述：`positive_1` / "A large giraffe looks at a smaller giraffe looking over a fence."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 1, "negative_start": 0, "negative_end": 1, "positive_lexemes": ["a"], "negative_lexemes": ["a"]}, {"tag": "replace", "positive_start": 1, "positive_end": 2, "negative_start": 1, "negative_end": 2, "positive_lexemes": ["large"], "negative_lexemes": ["smaller"]}, {"tag": "equal", "positive_start": 2, "positive_end": 6, "negative_start": 2, "negative_end": 6, "positive_lexemes": ["giraffe", "looks", "at", "a"], "negative_lexemes": ["giraffe", "looks", "at", "a"]}, {"tag": "replace", "positive_start": 6, "positive_end": 7, "negative_start": 6, "negative_end": 7, "positive_lexemes": ["smaller"], "negative_lexemes": ["larger"]}, {"tag": "equal", "positive_start": 7, "positive_end": 12, "negative_start": 7, "negative_end": 12, "positive_lexemes": ["giraffe", "looking", "over", "a", "fence"], "negative_lexemes": ["giraffe", "looking", "over", "a", "fence"]}]`
- 共同前缀：`["a"]`
- 正确 contrast hull：`["large", "giraffe", "looks", "at", "a", "smaller"]`
- 错误 contrast hull：`["smaller", "giraffe", "looks", "at", "a", "larger"]`
- 共同后缀：`["giraffe", "looking", "over", "a", "fence"]`
- Hull token 覆盖率（正/负/最大）：`[0.5217391304347826, 0.5416666666666666, 0.5416666666666666]`
- 共同前缀模型 token：`[100]`
- 正确 hull 模型 token：IDs `[2994, 492, 108, 559, 1627, 104, 1853, 1275, 1248, 299, 3436, 311]`；text " large giraffe looks at a smaller"
- 错误 hull 模型 token：IDs `[3436, 311, 492, 108, 559, 1627, 104, 1853, 1275, 1248, 299, 1823, 4105]`；text " smaller giraffe looks at a larger"
- 第一轮/第二轮分类：`complex_edit` / `multi_block_local_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 23. `swap_object:6`

- 负例类型/范围：`swap_object` / `{"canonical": true, "pilot": true, "formal": false, "certifying_formal": false}`
- 原始正描述 1："A painting of a vase with a sunflower on a table."
- 原始正描述 2："A vase containing a sunflower is positioned on a table in a painting."
- 原始负描述："A painting of a sunflower with a vase on a table."
- 规范化正描述 1："a painting of a vase with a sunflower on a table"
- 规范化正描述 2："a vase containing a sunflower is positioned on a table in a painting"
- 规范化负描述："a painting of a sunflower with a vase on a table"
- 正描述 1 选择元组：`[4, 8, 2, 0.18181818181818182, 0.3333333333333333]`
- 正描述 2 选择元组：`[14, 22, 5, 0.6153846153846154, 0.5294117647058824]`
- 最终比较正描述：`positive_1` / "A painting of a vase with a sunflower on a table."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 4, "negative_start": 0, "negative_end": 4, "positive_lexemes": ["a", "painting", "of", "a"], "negative_lexemes": ["a", "painting", "of", "a"]}, {"tag": "replace", "positive_start": 4, "positive_end": 5, "negative_start": 4, "negative_end": 5, "positive_lexemes": ["vase"], "negative_lexemes": ["sunflower"]}, {"tag": "equal", "positive_start": 5, "positive_end": 7, "negative_start": 5, "negative_end": 7, "positive_lexemes": ["with", "a"], "negative_lexemes": ["with", "a"]}, {"tag": "replace", "positive_start": 7, "positive_end": 8, "negative_start": 7, "negative_end": 8, "positive_lexemes": ["sunflower"], "negative_lexemes": ["vase"]}, {"tag": "equal", "positive_start": 8, "positive_end": 11, "negative_start": 8, "negative_end": 11, "positive_lexemes": ["on", "a", "table"], "negative_lexemes": ["on", "a", "table"]}]`
- 共同前缀：`["a", "painting", "of", "a"]`
- 正确 contrast hull：`["vase", "with", "a", "sunflower"]`
- 错误 contrast hull：`["sunflower", "with", "a", "vase"]`
- 共同后缀：`["on", "a", "table"]`
- Hull token 覆盖率（正/负/最大）：`[0.5, 0.5, 0.5]`
- 共同前缀模型 token：`[100, 5063, 2912, 354, 299]`
- 正确 hull 模型 token：IDs `[603, 812, 599, 299, 3150, 105, 1030, 311]`；text " vase with a sunflower"
- 错误 hull 模型 token：IDs `[3150, 105, 1030, 311, 599, 299, 603, 812]`；text " sunflower with a vase"
- 第一轮/第二轮分类：`complex_edit` / `multi_block_local_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 24. `swap_object:65`

- 负例类型/范围：`swap_object` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A person holding a baby while standing in front of a mirror."
- 原始正描述 2："The person is standing in front of a mirror while holding a baby."
- 原始负描述："A baby holding a person while standing in front of a mirror."
- 规范化正描述 1："a person holding a baby while standing in front of a mirror"
- 规范化正描述 2："the person is standing in front of a mirror while holding a baby"
- 规范化负描述："a baby holding a person while standing in front of a mirror"
- 正描述 1 选择元组：`[4, 8, 2, 0.16666666666666666, 0.2033898305084746]`
- 正描述 2 选择元组：`[11, 25, 4, 0.6923076923076923, 0.625]`
- 最终比较正描述：`positive_1` / "A person holding a baby while standing in front of a mirror."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 1, "negative_start": 0, "negative_end": 1, "positive_lexemes": ["a"], "negative_lexemes": ["a"]}, {"tag": "replace", "positive_start": 1, "positive_end": 2, "negative_start": 1, "negative_end": 2, "positive_lexemes": ["person"], "negative_lexemes": ["baby"]}, {"tag": "equal", "positive_start": 2, "positive_end": 4, "negative_start": 2, "negative_end": 4, "positive_lexemes": ["holding", "a"], "negative_lexemes": ["holding", "a"]}, {"tag": "replace", "positive_start": 4, "positive_end": 5, "negative_start": 4, "negative_end": 5, "positive_lexemes": ["baby"], "negative_lexemes": ["person"]}, {"tag": "equal", "positive_start": 5, "positive_end": 12, "negative_start": 5, "negative_end": 12, "positive_lexemes": ["while", "standing", "in", "front", "of", "a", "mirror"], "negative_lexemes": ["while", "standing", "in", "front", "of", "a", "mirror"]}]`
- 共同前缀：`["a"]`
- 正确 contrast hull：`["person", "holding", "a", "baby"]`
- 错误 contrast hull：`["baby", "holding", "a", "person"]`
- 共同后缀：`["while", "standing", "in", "front", "of", "a", "mirror"]`
- Hull token 覆盖率（正/负/最大）：`[0.38095238095238093, 0.38095238095238093, 0.38095238095238093]`
- 共同前缀模型 token：`[100]`
- 正确 hull 模型 token：IDs `[2198, 429, 2569, 350, 299, 363, 572, 124]`；text " person holding a baby"
- 错误 hull 模型 token：IDs `[363, 572, 124, 429, 2569, 350, 299, 2198]`；text " baby holding a person"
- 第一轮/第二轮分类：`complex_edit` / `multi_block_local_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 25. `swap_object:66`

- 负例类型/范围：`swap_object` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A person cutting a pizza next to a salad and bottles of wine on wooden table."
- 原始正描述 2："A person is slicing pizza adjacent to bottles of wine and a salad on a table made of wood."
- 原始负描述："A person cutting a salad next to a pizza and bottles of wine on wooden table."
- 规范化正描述 1："a person cutting a pizza next to a salad and bottles of wine on wooden table"
- 规范化正描述 2："a person is slicing pizza adjacent to bottles of wine and a salad on a table made of wood"
- 规范化负描述："a person cutting a salad next to a pizza and bottles of wine on wooden table"
- 正描述 1 选择元组：`[4, 10, 2, 0.125, 0.13157894736842105]`
- 正描述 2 选择元组：`[25, 31, 4, 0.7368421052631579, 0.5955056179775281]`
- 最终比较正描述：`positive_1` / "A person cutting a pizza next to a salad and bottles of wine on wooden table."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 4, "negative_start": 0, "negative_end": 4, "positive_lexemes": ["a", "person", "cutting", "a"], "negative_lexemes": ["a", "person", "cutting", "a"]}, {"tag": "replace", "positive_start": 4, "positive_end": 5, "negative_start": 4, "negative_end": 5, "positive_lexemes": ["pizza"], "negative_lexemes": ["salad"]}, {"tag": "equal", "positive_start": 5, "positive_end": 8, "negative_start": 5, "negative_end": 8, "positive_lexemes": ["next", "to", "a"], "negative_lexemes": ["next", "to", "a"]}, {"tag": "replace", "positive_start": 8, "positive_end": 9, "negative_start": 8, "negative_end": 9, "positive_lexemes": ["salad"], "negative_lexemes": ["pizza"]}, {"tag": "equal", "positive_start": 9, "positive_end": 16, "negative_start": 9, "negative_end": 16, "positive_lexemes": ["and", "bottles", "of", "wine", "on", "wooden", "table"], "negative_lexemes": ["and", "bottles", "of", "wine", "on", "wooden", "table"]}]`
- 共同前缀：`["a", "person", "cutting", "a"]`
- 正确 contrast hull：`["pizza", "next", "to", "a", "salad"]`
- 错误 contrast hull：`["salad", "next", "to", "a", "pizza"]`
- 共同后缀：`["and", "bottles", "of", "wine", "on", "wooden", "table"]`
- Hull token 覆盖率（正/负/最大）：`[0.3333333333333333, 0.3333333333333333, 0.3333333333333333]`
- 共同前缀模型 token：`[100, 2198, 5431, 2912, 299]`
- 正确 hull 模型 token：IDs `[344, 1028, 125, 100, 4658, 364, 299, 4019, 785]`；text " pizza next to a salad"
- 错误 hull 模型 token：IDs `[4019, 785, 4658, 364, 299, 344, 1028, 125, 100]`；text " salad next to a pizza"
- 第一轮/第二轮分类：`complex_edit` / `multi_block_local_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 26. `swap_object:75`

- 负例类型/范围：`swap_object` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": false}`
- 原始正描述 1："A herd of cattle walking down a road being followed by a cowboy."
- 原始正描述 2："A cowboy is following a herd of cattle walking down a road."
- 原始负描述："A cowboy walking down a road being followed by a herd of cattle."
- 规范化正描述 1："a herd of cattle walking down a road being followed by a cowboy"
- 规范化正描述 2："a cowboy is following a herd of cattle walking down a road"
- 规范化负描述："a cowboy walking down a road being followed by a herd of cattle"
- 正描述 1 选择元组：`[8, 24, 4, 0.46153846153846156, 0.4126984126984127]`
- 正描述 2 选择元组：`[19, 21, 3, 0.7692307692307693, 0.6825396825396826]`
- 最终比较正描述：`positive_1` / "A herd of cattle walking down a road being followed by a cowboy."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 1, "negative_start": 0, "negative_end": 1, "positive_lexemes": ["a"], "negative_lexemes": ["a"]}, {"tag": "delete", "positive_start": 1, "positive_end": 3, "negative_start": 1, "negative_end": 1, "positive_lexemes": ["herd", "of"], "negative_lexemes": []}, {"tag": "replace", "positive_start": 3, "positive_end": 4, "negative_start": 1, "negative_end": 2, "positive_lexemes": ["cattle"], "negative_lexemes": ["cowboy"]}, {"tag": "equal", "positive_start": 4, "positive_end": 12, "negative_start": 2, "negative_end": 10, "positive_lexemes": ["walking", "down", "a", "road", "being", "followed", "by", "a"], "negative_lexemes": ["walking", "down", "a", "road", "being", "followed", "by", "a"]}, {"tag": "insert", "positive_start": 12, "positive_end": 12, "negative_start": 10, "negative_end": 12, "positive_lexemes": [], "negative_lexemes": ["herd", "of"]}, {"tag": "replace", "positive_start": 12, "positive_end": 13, "negative_start": 12, "negative_end": 13, "positive_lexemes": ["cowboy"], "negative_lexemes": ["cattle"]}]`
- 共同前缀：`["a"]`
- 正确 contrast hull：`["herd", "of", "cattle", "walking", "down", "a", "road", "being", "followed", "by", "a", "cowboy"]`
- 错误 contrast hull：`["cowboy", "walking", "down", "a", "road", "being", "followed", "by", "a", "herd", "of", "cattle"]`
- 共同后缀：`[]`
- Hull token 覆盖率（正/负/最大）：`[0.9545454545454546, 0.9545454545454546, 0.9545454545454546]`
- 共同前缀模型 token：`[100]`
- 正确 hull 模型 token：IDs `[2833, 103, 354, 3706, 5395, 339, 352, 1237, 4076, 299, 1552, 785, 4016, 1502, 382, 769, 299, 317, 451, 101, 4117]`；text " herd of cattle walking down a road being followed by a cowboy"
- 错误 hull 模型 token：IDs `[317, 451, 101, 4117, 339, 352, 1237, 4076, 299, 1552, 785, 4016, 1502, 382, 769, 299, 2833, 103, 354, 3706, 5395]`；text " cowboy walking down a road being followed by a herd of cattle"
- 第一轮/第二轮分类：`complex_edit` / `large_contrast_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；"maximum_hull_token_coverage_above_75_percent"

### 27. `swap_object:78`

- 负例类型/范围：`swap_object` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A traffic light on a metal pole by a tree."
- 原始正描述 2："A traffic light is placed on a metal pole adjacent to a tree."
- 原始负描述："A traffic light on a tree by a metal pole."
- 规范化正描述 1："a traffic light on a metal pole by a tree"
- 规范化正描述 2："a traffic light is placed on a metal pole adjacent to a tree"
- 规范化负描述："a traffic light on a tree by a metal pole"
- 正描述 1 选择元组：`[6, 10, 4, 0.4, 0.3902439024390244]`
- 正描述 2 选择元组：`[13, 17, 3, 0.6153846153846154, 0.4666666666666667]`
- 最终比较正描述：`positive_1` / "A traffic light on a metal pole by a tree."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 5, "negative_start": 0, "negative_end": 5, "positive_lexemes": ["a", "traffic", "light", "on", "a"], "negative_lexemes": ["a", "traffic", "light", "on", "a"]}, {"tag": "delete", "positive_start": 5, "positive_end": 6, "negative_start": 5, "negative_end": 5, "positive_lexemes": ["metal"], "negative_lexemes": []}, {"tag": "replace", "positive_start": 6, "positive_end": 7, "negative_start": 5, "negative_end": 6, "positive_lexemes": ["pole"], "negative_lexemes": ["tree"]}, {"tag": "equal", "positive_start": 7, "positive_end": 9, "negative_start": 6, "negative_end": 8, "positive_lexemes": ["by", "a"], "negative_lexemes": ["by", "a"]}, {"tag": "insert", "positive_start": 9, "positive_end": 9, "negative_start": 8, "negative_end": 9, "positive_lexemes": [], "negative_lexemes": ["metal"]}, {"tag": "replace", "positive_start": 9, "positive_end": 10, "negative_start": 9, "negative_end": 10, "positive_lexemes": ["tree"], "negative_lexemes": ["pole"]}]`
- 共同前缀：`["a", "traffic", "light", "on", "a"]`
- 正确 contrast hull：`["metal", "pole", "by", "a", "tree"]`
- 错误 contrast hull：`["tree", "by", "a", "metal", "pole"]`
- 共同后缀：`[]`
- Hull token 覆盖率（正/负/最大）：`[0.5714285714285714, 0.5714285714285714, 0.5714285714285714]`
- 共同前缀模型 token：`[100, 1946, 5935, 2795, 619, 299]`
- 正确 hull 模型 token：IDs `[4743, 352, 927, 361, 769, 299, 297, 1382]`；text " metal pole by a tree"
- 错误 hull 模型 token：IDs `[297, 1382, 769, 299, 4743, 352, 927, 361]`；text " tree by a metal pole"
- 第一轮/第二轮分类：`complex_edit` / `multi_block_local_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 28. `swap_object:84`

- 负例类型/范围：`swap_object` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："this lady is using controllers and those men are watching"
- 原始正描述 2："Controllers are being used by this lady and those men are watching her."
- 原始负描述："Those men are using controllers and this lady is watching."
- 规范化正描述 1："this lady is using controllers and those men are watching"
- 规范化正描述 2："controllers are being used by this lady and those men are watching her"
- 规范化负描述："those men are using controllers and this lady is watching"
- 正描述 1 选择元组：`[12, 18, 2, 0.6, 0.3157894736842105]`
- 正描述 2 选择元组：`[15, 23, 6, 0.7692307692307693, 0.5714285714285714]`
- 最终比较正描述：`positive_1` / "this lady is using controllers and those men are watching"
- 完整 lexeme 编辑块：`[{"tag": "replace", "positive_start": 0, "positive_end": 3, "negative_start": 0, "negative_end": 3, "positive_lexemes": ["this", "lady", "is"], "negative_lexemes": ["those", "men", "are"]}, {"tag": "equal", "positive_start": 3, "positive_end": 6, "negative_start": 3, "negative_end": 6, "positive_lexemes": ["using", "controllers", "and"], "negative_lexemes": ["using", "controllers", "and"]}, {"tag": "replace", "positive_start": 6, "positive_end": 9, "negative_start": 6, "negative_end": 9, "positive_lexemes": ["those", "men", "are"], "negative_lexemes": ["this", "lady", "is"]}, {"tag": "equal", "positive_start": 9, "positive_end": 10, "negative_start": 9, "negative_end": 10, "positive_lexemes": ["watching"], "negative_lexemes": ["watching"]}]`
- 共同前缀：`[]`
- 正确 contrast hull：`["this", "lady", "is", "using", "controllers", "and", "those", "men", "are"]`
- 错误 contrast hull：`["those", "men", "are", "using", "controllers", "and", "this", "lady", "is"]`
- 共同后缀：`["watching"]`
- Hull token 覆盖率（正/负/最大）：`[0.8421052631578947, 0.8421052631578947, 0.8421052631578947]`
- 共同前缀模型 token：`[]`
- 正确 hull 模型 token：IDs `[495, 324, 406, 785, 124, 395, 1651, 1684, 393, 1989, 496, 376, 4876, 351, 327, 732]`；text "this lady is using controllers and those men are"
- 错误 hull 模型 token：IDs `[495, 2518, 351, 327, 732, 1651, 1684, 393, 1989, 496, 376, 1003, 406, 785, 124, 395]`；text "those men are using controllers and this lady is"
- 第一轮/第二轮分类：`complex_edit` / `large_contrast_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；"maximum_hull_token_coverage_above_75_percent"

### 29. `swap_object:85`

- 负例类型/范围：`swap_object` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": false}`
- 原始正描述 1："A picture of a bathroom with a fern plant near the sink and a photo of a city above the toilet. "
- 原始正描述 2："A photograph of a bathroom featuring a sink with a fern plant nearby, and a depiction of a city situated above the toilet."
- 原始负描述："A picture of a bathroom with a photo of a city near the sink and a fern plant above the toilet."
- 规范化正描述 1："a picture of a bathroom with a fern plant near the sink and a photo of a city above the toilet"
- 规范化正描述 2："a photograph of a bathroom featuring a sink with a fern plant nearby , and a depiction of a city situated above the toilet"
- 规范化负描述："a picture of a bathroom with a photo of a city near the sink and a fern plant above the toilet"
- 正描述 1 选择元组：`[12, 22, 4, 0.38095238095238093, 0.2553191489361702]`
- 正描述 2 选择元组：`[23, 37, 6, 0.5416666666666666, 0.5163934426229508]`
- 最终比较正描述：`positive_1` / "A picture of a bathroom with a fern plant near the sink and a photo of a city above the toilet. "
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 7, "negative_start": 0, "negative_end": 7, "positive_lexemes": ["a", "picture", "of", "a", "bathroom", "with", "a"], "negative_lexemes": ["a", "picture", "of", "a", "bathroom", "with", "a"]}, {"tag": "insert", "positive_start": 7, "positive_end": 7, "negative_start": 7, "negative_end": 9, "positive_lexemes": [], "negative_lexemes": ["photo", "of"]}, {"tag": "replace", "positive_start": 7, "positive_end": 9, "negative_start": 9, "negative_end": 11, "positive_lexemes": ["fern", "plant"], "negative_lexemes": ["a", "city"]}, {"tag": "equal", "positive_start": 9, "positive_end": 14, "negative_start": 11, "negative_end": 16, "positive_lexemes": ["near", "the", "sink", "and", "a"], "negative_lexemes": ["near", "the", "sink", "and", "a"]}, {"tag": "delete", "positive_start": 14, "positive_end": 16, "negative_start": 16, "negative_end": 16, "positive_lexemes": ["photo", "of"], "negative_lexemes": []}, {"tag": "replace", "positive_start": 16, "positive_end": 18, "negative_start": 16, "negative_end": 18, "positive_lexemes": ["a", "city"], "negative_lexemes": ["fern", "plant"]}, {"tag": "equal", "positive_start": 18, "positive_end": 21, "negative_start": 18, "negative_end": 21, "positive_lexemes": ["above", "the", "toilet"], "negative_lexemes": ["above", "the", "toilet"]}]`
- 共同前缀：`["a", "picture", "of", "a", "bathroom", "with", "a"]`
- 正确 contrast hull：`["fern", "plant", "near", "the", "sink", "and", "a", "photo", "of", "a", "city"]`
- 错误 contrast hull：`["photo", "of", "a", "city", "near", "the", "sink", "and", "a", "fern", "plant"]`
- 共同后缀：`["above", "the", "toilet"]`
- Hull token 覆盖率（正/负/最大）：`[0.5, 0.5, 0.5]`
- 共同前缀模型 token：`[100, 344, 2030, 745, 354, 299, 363, 1831, 393, 444, 599, 299]`
- 正确 hull 模型 token：IDs `[341, 2107, 1219, 811, 730, 370, 309, 316, 3010, 376, 299, 2001, 593, 114, 354, 299, 3972]`；text " fern plant near the sink and a photo of a city"
- 错误 hull 模型 token：IDs `[2001, 593, 114, 354, 299, 3972, 730, 370, 309, 316, 3010, 376, 299, 341, 2107, 1219, 811]`；text " photo of a city near the sink and a fern plant"
- 第一轮/第二轮分类：`complex_edit` / `multi_block_local_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 30. `swap_object:9`

- 负例类型/范围：`swap_object` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A person with a ball facing a child with a racquet."
- 原始正描述 2："A person holding a ball is standing in front of a child holding a racquet."
- 原始负描述："A child with a ball facing a person with a racquet."
- 规范化正描述 1："a person with a ball facing a child with a racquet"
- 规范化正描述 2："a person holding a ball is standing in front of a child holding a racquet"
- 规范化负描述："a child with a ball facing a person with a racquet"
- 正描述 1 选择元组：`[4, 14, 2, 0.18181818181818182, 0.24]`
- 正描述 2 选择元组：`[14, 20, 4, 0.6, 0.5616438356164384]`
- 最终比较正描述：`positive_1` / "A person with a ball facing a child with a racquet."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 1, "negative_start": 0, "negative_end": 1, "positive_lexemes": ["a"], "negative_lexemes": ["a"]}, {"tag": "replace", "positive_start": 1, "positive_end": 2, "negative_start": 1, "negative_end": 2, "positive_lexemes": ["person"], "negative_lexemes": ["child"]}, {"tag": "equal", "positive_start": 2, "positive_end": 7, "negative_start": 2, "negative_end": 7, "positive_lexemes": ["with", "a", "ball", "facing", "a"], "negative_lexemes": ["with", "a", "ball", "facing", "a"]}, {"tag": "replace", "positive_start": 7, "positive_end": 8, "negative_start": 7, "negative_end": 8, "positive_lexemes": ["child"], "negative_lexemes": ["person"]}, {"tag": "equal", "positive_start": 8, "positive_end": 11, "negative_start": 8, "negative_end": 11, "positive_lexemes": ["with", "a", "racquet"], "negative_lexemes": ["with", "a", "racquet"]}]`
- 共同前缀：`["a"]`
- 正确 contrast hull：`["person", "with", "a", "ball", "facing", "a", "child"]`
- 错误 contrast hull：`["child", "with", "a", "ball", "facing", "a", "person"]`
- 共同后缀：`["with", "a", "racquet"]`
- Hull token 覆盖率（正/负/最大）：`[0.5625, 0.5625, 0.5625]`
- 共同前缀模型 token：`[100]`
- 正确 hull 模型 token：IDs `[2198, 599, 299, 363, 1266, 5875, 350, 299, 6109]`；text " person with a ball facing a child"
- 错误 hull 模型 token：IDs `[6109, 599, 299, 363, 1266, 5875, 350, 299, 2198]`；text " child with a ball facing a person"
- 第一轮/第二轮分类：`complex_edit` / `multi_block_local_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

## Comparison positive 歧义

候选 `0` 条，本节抽取 `0` 条。

本类别没有可抽取样本。

## 两条正描述规范化等价

候选 `2` 条，本节抽取 `2` 条。

### 1. `replace_attribute:14`

- 负例类型/范围：`replace_attribute` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A small tiled bathroom stall with a black toilet seat."
- 原始正描述 2："A small tiled bathroom stall with a black toilet seat."
- 原始负描述："A small tiled bathroom stall with a white toilet seat."
- 规范化正描述 1："a small tiled bathroom stall with a black toilet seat"
- 规范化正描述 2："a small tiled bathroom stall with a black toilet seat"
- 规范化负描述："a small tiled bathroom stall with a white toilet seat"
- 正描述 1 选择元组：`[2, 2, 1, 0.1, 0.09433962264150944]`
- 正描述 2 选择元组：`[2, 2, 1, 0.1, 0.09433962264150944]`
- 最终比较正描述：`positive_1` / "A small tiled bathroom stall with a black toilet seat."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 7, "negative_start": 0, "negative_end": 7, "positive_lexemes": ["a", "small", "tiled", "bathroom", "stall", "with", "a"], "negative_lexemes": ["a", "small", "tiled", "bathroom", "stall", "with", "a"]}, {"tag": "replace", "positive_start": 7, "positive_end": 8, "negative_start": 7, "negative_end": 8, "positive_lexemes": ["black"], "negative_lexemes": ["white"]}, {"tag": "equal", "positive_start": 8, "positive_end": 10, "negative_start": 8, "negative_end": 10, "positive_lexemes": ["toilet", "seat"], "negative_lexemes": ["toilet", "seat"]}]`
- 共同前缀：`["a", "small", "tiled", "bathroom", "stall", "with", "a"]`
- 正确 contrast hull：`["black"]`
- 错误 contrast hull：`["white"]`
- 共同后缀：`["toilet", "seat"]`
- Hull token 覆盖率（正/负/最大）：`[0.10526315789473684, 0.10526315789473684, 0.10526315789473684]`
- 共同前缀模型 token：`[100, 3436, 297, 4598, 363, 1831, 393, 444, 580, 1266, 599, 299]`
- 正确 hull 模型 token：IDs `[2597, 1637]`；text " black"
- 错误 hull 模型 token：IDs `[654, 1078]`；text " white"
- 第一轮/第二轮分类：`ambiguous_source` / `equivalent_positive_sources`
- 自动判断："equal_tuples_equivalent_alignment_views_choose_positive_1"；"positive_alignment_views_and_selection_tuples_are_equivalent"

### 2. `replace_relation:369`

- 负例类型/范围：`replace_relation` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A  group of kids in suits holding a chalkboard."
- 原始正描述 2："A group of kids in suits holding a chalkboard."
- 原始负描述："A group of kids in suits throwing a chalkboard."
- 规范化正描述 1："a group of kids in suits holding a chalkboard"
- 规范化正描述 2："a group of kids in suits holding a chalkboard"
- 规范化负描述："a group of kids in suits throwing a chalkboard"
- 正描述 1 选择元组：`[2, 2, 1, 0.1111111111111111, 0.08695652173913043]`
- 正描述 2 选择元组：`[2, 2, 1, 0.1111111111111111, 0.08695652173913043]`
- 最终比较正描述：`positive_1` / "A  group of kids in suits holding a chalkboard."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 6, "negative_start": 0, "negative_end": 6, "positive_lexemes": ["a", "group", "of", "kids", "in", "suits"], "negative_lexemes": ["a", "group", "of", "kids", "in", "suits"]}, {"tag": "replace", "positive_start": 6, "positive_end": 7, "negative_start": 6, "negative_end": 7, "positive_lexemes": ["holding"], "negative_lexemes": ["throwing"]}, {"tag": "equal", "positive_start": 7, "positive_end": 9, "negative_start": 7, "negative_end": 9, "positive_lexemes": ["a", "chalkboard"], "negative_lexemes": ["a", "chalkboard"]}]`
- 共同前缀：`["a", "group", "of", "kids", "in", "suits"]`
- 正确 contrast hull：`["holding"]`
- 错误 contrast hull：`["throwing"]`
- 共同后缀：`["a", "chalkboard"]`
- Hull token 覆盖率（正/负/最大）：`[0.16666666666666666, 0.16666666666666666, 0.16666666666666666]`
- 共同前缀模型 token：`[100, 4592, 354, 914, 460, 118, 353, 855, 2163]`
- 正确 hull 模型 token：IDs `[429, 2569, 350]`；text " holding"
- 错误 hull 模型 token：IDs `[445, 2079, 350]`；text " throwing"
- 第一轮/第二轮分类：`unique_alignment` / `equivalent_positive_sources`
- 自动判断："equal_tuples_equivalent_alignment_views_choose_positive_1"；"positive_alignment_views_and_selection_tuples_are_equivalent"

## 第一轮与第二轮来源选择不一致

候选 `73` 条，本节抽取 `30` 条。

### 1. `replace_object:1073`

- 负例类型/范围：`replace_object` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："THERE IS A RED TRUCK THAT IS ON THE STREET "
- 原始正描述 2："The red truck is positioned on the street."
- 原始负描述："There is a red bike that is on the street."
- 规范化正描述 1："there is a red truck that is on the street"
- 规范化正描述 2："the red truck is positioned on the street"
- 规范化负描述："there is a red bike that is on the street"
- 正描述 1 选择元组：`[2, 2, 1, 0.1, 0.11904761904761904]`
- 正描述 2 选择元组：`[10, 12, 3, 0.6, 0.5121951219512195]`
- 最终比较正描述：`positive_1` / "THERE IS A RED TRUCK THAT IS ON THE STREET "
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 4, "negative_start": 0, "negative_end": 4, "positive_lexemes": ["there", "is", "a", "red"], "negative_lexemes": ["there", "is", "a", "red"]}, {"tag": "replace", "positive_start": 4, "positive_end": 5, "negative_start": 4, "negative_end": 5, "positive_lexemes": ["truck"], "negative_lexemes": ["bike"]}, {"tag": "equal", "positive_start": 5, "positive_end": 10, "negative_start": 5, "negative_end": 10, "positive_lexemes": ["that", "is", "on", "the", "street"], "negative_lexemes": ["that", "is", "on", "the", "street"]}]`
- 共同前缀：`["there", "is", "a", "red"]`
- 正确 contrast hull：`["truck"]`
- 错误 contrast hull：`["bike"]`
- 共同后缀：`["that", "is", "on", "the", "street"]`
- Hull token 覆盖率（正/负/最大）：`[0.21428571428571427, 0.15384615384615385, 0.21428571428571427]`
- 共同前缀模型 token：`[119, 2503, 395, 299, 5534]`
- 正确 hull 模型 token：IDs `[1144, 120, 892]`；text " truck"
- 错误 hull 模型 token：IDs `[363, 1024]`；text " bike"
- 第一轮/第二轮分类：`complex_edit` / `one_block_local`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 2. `replace_object:1084`

- 负例类型/范围：`replace_object` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："LOTS OF BROKEN TOILETS SITTING OUT ON A LAWN"
- 原始正描述 2："Several broken toilets are scattered on a lawn."
- 原始负描述："Lots of broken bicycles sitting out on a lawn."
- 规范化正描述 1："lots of broken toilets sitting out on a lawn"
- 规范化正描述 2："several broken toilets are scattered on a lawn"
- 规范化负描述："lots of broken bicycles sitting out on a lawn"
- 正描述 1 选择元组：`[2, 2, 1, 0.1111111111111111, 0.13333333333333333]`
- 正描述 2 选择元组：`[9, 11, 3, 0.5555555555555556, 0.5652173913043478]`
- 最终比较正描述：`positive_1` / "LOTS OF BROKEN TOILETS SITTING OUT ON A LAWN"
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 3, "negative_start": 0, "negative_end": 3, "positive_lexemes": ["lots", "of", "broken"], "negative_lexemes": ["lots", "of", "broken"]}, {"tag": "replace", "positive_start": 3, "positive_end": 4, "negative_start": 3, "negative_end": 4, "positive_lexemes": ["toilets"], "negative_lexemes": ["bicycles"]}, {"tag": "equal", "positive_start": 4, "positive_end": 9, "negative_start": 4, "negative_end": 9, "positive_lexemes": ["sitting", "out", "on", "a", "lawn"], "negative_lexemes": ["sitting", "out", "on", "a", "lawn"]}]`
- 共同前缀：`["lots", "of", "broken"]`
- 正确 contrast hull：`["toilets"]`
- 错误 contrast hull：`["bicycles"]`
- 共同后缀：`["sitting", "out", "on", "a", "lawn"]`
- Hull token 覆盖率（正/负/最大）：`[0.17647058823529413, 0.2631578947368421, 0.2631578947368421]`
- 共同前缀模型 token：`[111, 593, 118, 354, 5108, 110, 327]`
- 正确 hull 模型 token：IDs `[364, 1299, 2726]`；text " toilets"
- 错误 hull 模型 token：IDs `[363, 375, 124, 1110, 329]`；text " bicycles"
- 第一轮/第二轮分类：`complex_edit` / `one_block_local`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 3. `replace_object:1176`

- 负例类型/范围：`replace_object` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："MAN ON A CONTRAPTION, SURROUNDED BY A BICYCLE AND ANOTHER PERSON"
- 原始正描述 2："A person surrounded by a bicycle and another person is on a contraption."
- 原始负描述："A man on a contraption, surrounded by a car and another person."
- 规范化正描述 1："man on a contraption , surrounded by a bicycle and another person"
- 规范化正描述 2："a person surrounded by a bicycle and another person is on a contraption"
- 规范化负描述："a man on a contraption , surrounded by a car and another person"
- 正描述 1 选择元组：`[3, 19, 2, 0.15384615384615385, 0.12307692307692308]`
- 正描述 2 选择元组：`[12, 26, 5, 0.7692307692307693, 0.6338028169014085]`
- 最终比较正描述：`positive_1` / "MAN ON A CONTRAPTION, SURROUNDED BY A BICYCLE AND ANOTHER PERSON"
- 完整 lexeme 编辑块：`[{"tag": "insert", "positive_start": 0, "positive_end": 0, "negative_start": 0, "negative_end": 1, "positive_lexemes": [], "negative_lexemes": ["a"]}, {"tag": "equal", "positive_start": 0, "positive_end": 8, "negative_start": 1, "negative_end": 9, "positive_lexemes": ["man", "on", "a", "contraption", ",", "surrounded", "by", "a"], "negative_lexemes": ["man", "on", "a", "contraption", ",", "surrounded", "by", "a"]}, {"tag": "replace", "positive_start": 8, "positive_end": 9, "negative_start": 9, "negative_end": 10, "positive_lexemes": ["bicycle"], "negative_lexemes": ["car"]}, {"tag": "equal", "positive_start": 9, "positive_end": 12, "negative_start": 10, "negative_end": 13, "positive_lexemes": ["and", "another", "person"], "negative_lexemes": ["and", "another", "person"]}]`
- 共同前缀：`[]`
- 正确 contrast hull：`["man", "on", "a", "contraption", ",", "surrounded", "by", "a", "bicycle"]`
- 错误 contrast hull：`["a", "man", "on", "a", "contraption", ",", "surrounded", "by", "a", "car"]`
- 共同后缀：`["and", "another", "person"]`
- Hull token 覆盖率（正/负/最大）：`[0.8571428571428571, 0.8421052631578947, 0.8571428571428571]`
- 共同前缀模型 token：`[]`
- 正确 hull 模型 token：IDs `[5257, 619, 299, 1684, 559, 875, 371, 256, 47, 3946, 2383, 382, 769, 299, 363, 375, 124, 2945]`；text "man on a contraption , surrounded by a bicycle"
- 错误 hull 模型 token：IDs `[100, 1672, 619, 299, 1684, 559, 875, 371, 256, 47, 3946, 2383, 382, 769, 299, 3751]`；text "a man on a contraption , surrounded by a car"
- 第一轮/第二轮分类：`complex_edit` / `large_contrast_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；"maximum_hull_token_coverage_above_75_percent"

### 4. `replace_object:1566`

- 负例类型/范围：`replace_object` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："THERE ARE WOMEN THAT ARE LAUGHING UNDER THE UMBRELLA."
- 原始正描述 2："Women are under the umbrella, laughing."
- 原始负描述："There are children that are laughing under the umbrella."
- 规范化正描述 1："there are women that are laughing under the umbrella"
- 规范化正描述 2："women are under the umbrella , laughing"
- 规范化负描述："there are children that are laughing under the umbrella"
- 正描述 1 选择元组：`[2, 2, 1, 0.1111111111111111, 0.10909090909090909]`
- 正描述 2 选择元组：`[8, 16, 4, 0.7777777777777778, 0.7090909090909091]`
- 最终比较正描述：`positive_1` / "THERE ARE WOMEN THAT ARE LAUGHING UNDER THE UMBRELLA."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 2, "negative_start": 0, "negative_end": 2, "positive_lexemes": ["there", "are"], "negative_lexemes": ["there", "are"]}, {"tag": "replace", "positive_start": 2, "positive_end": 3, "negative_start": 2, "negative_end": 3, "positive_lexemes": ["women"], "negative_lexemes": ["children"]}, {"tag": "equal", "positive_start": 3, "positive_end": 9, "negative_start": 3, "negative_end": 9, "positive_lexemes": ["that", "are", "laughing", "under", "the", "umbrella"], "negative_lexemes": ["that", "are", "laughing", "under", "the", "umbrella"]}]`
- 共同前缀：`["there", "are"]`
- 正确 contrast hull：`["women"]`
- 错误 contrast hull：`["children"]`
- 共同后缀：`["that", "are", "laughing", "under", "the", "umbrella"]`
- Hull token 覆盖率（正/负/最大）：`[0.15789473684210525, 0.1111111111111111, 0.15789473684210525]`
- 共同前缀模型 token：`[119, 2503, 732]`
- 正确 hull 模型 token：IDs `[339, 444, 327]`；text " women"
- 错误 hull 模型 token：IDs `[6109, 3193]`；text " children"
- 第一轮/第二轮分类：`complex_edit` / `one_block_local`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 5. `replace_object:1623`

- 负例类型/范围：`replace_object` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": false}`
- 原始正描述 1："THERE IS A BATHROOM WITH A SINK AND A MIRROR "
- 原始正描述 2："The sink and mirror are located in a bathroom."
- 原始负描述："There is a bedroom with a sink and a mirror."
- 规范化正描述 1："there is a bathroom with a sink and a mirror"
- 规范化正描述 2："the sink and mirror are located in a bathroom"
- 规范化负描述："there is a bedroom with a sink and a mirror"
- 正描述 1 选择元组：`[2, 2, 1, 0.1, 0.06818181818181818]`
- 正描述 2 选择元组：`[17, 19, 3, 0.9, 0.6888888888888889]`
- 最终比较正描述：`positive_1` / "THERE IS A BATHROOM WITH A SINK AND A MIRROR "
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 3, "negative_start": 0, "negative_end": 3, "positive_lexemes": ["there", "is", "a"], "negative_lexemes": ["there", "is", "a"]}, {"tag": "replace", "positive_start": 3, "positive_end": 4, "negative_start": 3, "negative_end": 4, "positive_lexemes": ["bathroom"], "negative_lexemes": ["bedroom"]}, {"tag": "equal", "positive_start": 4, "positive_end": 10, "negative_start": 4, "negative_end": 10, "positive_lexemes": ["with", "a", "sink", "and", "a", "mirror"], "negative_lexemes": ["with", "a", "sink", "and", "a", "mirror"]}]`
- 共同前缀：`["there", "is", "a"]`
- 正确 contrast hull：`["bathroom"]`
- 错误 contrast hull：`["bedroom"]`
- 共同后缀：`["with", "a", "sink", "and", "a", "mirror"]`
- Hull token 覆盖率（正/负/最大）：`[0.23529411764705882, 0.23529411764705882, 0.23529411764705882]`
- 共同前缀模型 token：`[119, 2503, 395, 299]`
- 正确 hull 模型 token：IDs `[363, 1831, 393, 444]`；text " bathroom"
- 错误 hull 模型 token：IDs `[363, 382, 393, 444]`；text " bedroom"
- 第一轮/第二轮分类：`complex_edit` / `one_block_local`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 6. `replace_object:663`

- 负例类型/范围：`replace_object` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A WOMAN IS STANDING LOOKING AT SOMETHING."
- 原始正描述 2："A woman is standing and gazing at something."
- 原始负描述："A man is standing looking at something."
- 规范化正描述 1："a woman is standing looking at something"
- 规范化正描述 2："a woman is standing and gazing at something"
- 规范化负描述："a man is standing looking at something"
- 正描述 1 选择元组：`[2, 2, 1, 0.14285714285714285, 0.05]`
- 正描述 2 选择元组：`[5, 9, 3, 0.375, 0.20930232558139536]`
- 最终比较正描述：`positive_1` / "A WOMAN IS STANDING LOOKING AT SOMETHING."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 1, "negative_start": 0, "negative_end": 1, "positive_lexemes": ["a"], "negative_lexemes": ["a"]}, {"tag": "replace", "positive_start": 1, "positive_end": 2, "negative_start": 1, "negative_end": 2, "positive_lexemes": ["woman"], "negative_lexemes": ["man"]}, {"tag": "equal", "positive_start": 2, "positive_end": 7, "negative_start": 2, "negative_end": 7, "positive_lexemes": ["is", "standing", "looking", "at", "something"], "negative_lexemes": ["is", "standing", "looking", "at", "something"]}]`
- 共同前缀：`["a"]`
- 正确 contrast hull：`["woman"]`
- 错误 contrast hull：`["man"]`
- 共同后缀：`["is", "standing", "looking", "at", "something"]`
- Hull token 覆盖率（正/负/最大）：`[0.3, 0.125, 0.3]`
- 共同前缀模型 token：`[100]`
- 正确 hull 模型 token：IDs `[339, 444, 325]`；text " woman"
- 错误 hull 模型 token：IDs `[1672]`；text " man"
- 第一轮/第二轮分类：`complex_edit` / `one_block_local`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 7. `replace_object:667`

- 负例类型/范围：`replace_object` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："THERE IS A BUS PARKED ON THE SIDE OF THE STREET"
- 原始正描述 2："The bus is parked on the side of the street."
- 原始负描述："There is a truck parked on the side of the street."
- 规范化正描述 1："there is a bus parked on the side of the street"
- 规范化正描述 2："the bus is parked on the side of the street"
- 规范化负描述："there is a truck parked on the side of the street"
- 正描述 1 选择元组：`[2, 2, 1, 0.09090909090909091, 0.08163265306122448]`
- 正描述 2 选择元组：`[7, 7, 2, 0.36363636363636365, 0.22448979591836735]`
- 最终比较正描述：`positive_1` / "THERE IS A BUS PARKED ON THE SIDE OF THE STREET"
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 3, "negative_start": 0, "negative_end": 3, "positive_lexemes": ["there", "is", "a"], "negative_lexemes": ["there", "is", "a"]}, {"tag": "replace", "positive_start": 3, "positive_end": 4, "negative_start": 3, "negative_end": 4, "positive_lexemes": ["bus"], "negative_lexemes": ["truck"]}, {"tag": "equal", "positive_start": 4, "positive_end": 11, "negative_start": 4, "negative_end": 11, "positive_lexemes": ["parked", "on", "the", "side", "of", "the", "street"], "negative_lexemes": ["parked", "on", "the", "side", "of", "the", "street"]}]`
- 共同前缀：`["there", "is", "a"]`
- 正确 contrast hull：`["bus"]`
- 错误 contrast hull：`["truck"]`
- 共同后缀：`["parked", "on", "the", "side", "of", "the", "street"]`
- Hull token 覆盖率（正/负/最大）：`[0.06666666666666667, 0.17647058823529413, 0.17647058823529413]`
- 共同前缀模型 token：`[119, 2503, 395, 299]`
- 正确 hull 模型 token：IDs `[2499]`；text " bus"
- 错误 hull 模型 token：IDs `[1144, 120, 892]`；text " truck"
- 第一轮/第二轮分类：`complex_edit` / `one_block_local`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 8. `replace_relation:112`

- 负例类型/范围：`replace_relation` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A young person stands over a lap top computer screen."
- 原始正描述 2："A young person is positioned above a lap top computer screen."
- 原始负描述："A young person sits next to a laptop computer screen."
- 规范化正描述 1："a young person stands over a lap top computer screen"
- 规范化正描述 2："a young person is positioned above a lap top computer screen"
- 规范化负描述："a young person sits next to a laptop computer screen"
- 正描述 1 选择元组：`[10, 10, 1, 0.5, 0.21153846153846154]`
- 正描述 2 选择元组：`[9, 11, 3, 0.45454545454545453, 0.23333333333333334]`
- 最终比较正描述：`positive_2` / "A young person is positioned above a lap top computer screen."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 3, "negative_start": 0, "negative_end": 3, "positive_lexemes": ["a", "young", "person"], "negative_lexemes": ["a", "young", "person"]}, {"tag": "replace", "positive_start": 3, "positive_end": 6, "negative_start": 3, "negative_end": 6, "positive_lexemes": ["is", "positioned", "above"], "negative_lexemes": ["sits", "next", "to"]}, {"tag": "equal", "positive_start": 6, "positive_end": 7, "negative_start": 6, "negative_end": 7, "positive_lexemes": ["a"], "negative_lexemes": ["a"]}, {"tag": "delete", "positive_start": 7, "positive_end": 8, "negative_start": 7, "negative_end": 7, "positive_lexemes": ["lap"], "negative_lexemes": []}, {"tag": "replace", "positive_start": 8, "positive_end": 9, "negative_start": 7, "negative_end": 8, "positive_lexemes": ["top"], "negative_lexemes": ["laptop"]}, {"tag": "equal", "positive_start": 9, "positive_end": 11, "negative_start": 8, "negative_end": 10, "positive_lexemes": ["computer", "screen"], "negative_lexemes": ["computer", "screen"]}]`
- 共同前缀：`["a", "young", "person"]`
- 正确 contrast hull：`["is", "positioned", "above", "a", "lap", "top"]`
- 错误 contrast hull：`["sits", "next", "to", "a", "laptop"]`
- 共同后缀：`["computer", "screen"]`
- Hull token 覆盖率（正/负/最大）：`[0.5294117647058824, 0.5, 0.5294117647058824]`
- 共同前缀模型 token：`[100, 401, 1685, 2198]`
- 正确 hull 模型 token：IDs `[395, 2617, 1632, 382, 6264, 299, 406, 1175, 2924]`；text " is positioned above a lap top"
- 错误 hull 模型 token：IDs `[316, 2163, 4658, 364, 299, 3090, 875, 1506]`；text " sits next to a laptop"
- 第一轮/第二轮分类：`complex_edit` / `multi_block_local_hull`
- 自动判断："positive_2_selection_tuple_lexicographically_smaller"；null

### 9. `replace_relation:1196`

- 负例类型/范围：`replace_relation` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："THERE ARE PEOPLE RIDING ON AN ELEPHANT BACK"
- 原始正描述 2："The people are riding on the back of the elephant."
- 原始负描述："People are watching from afar as an elephant walks by."
- 规范化正描述 1："there are people riding on an elephant back"
- 规范化正描述 2："the people are riding on the back of the elephant"
- 规范化负描述："people are watching from afar as an elephant walks by"
- 正描述 1 选择元组：`[12, 18, 5, 0.7, 0.5471698113207547]`
- 正描述 2 选择元组：`[16, 20, 3, 0.9, 0.6226415094339622]`
- 最终比较正描述：`positive_1` / "THERE ARE PEOPLE RIDING ON AN ELEPHANT BACK"
- 完整 lexeme 编辑块：`[{"tag": "replace", "positive_start": 0, "positive_end": 1, "negative_start": 0, "negative_end": 1, "positive_lexemes": ["there"], "negative_lexemes": ["people"]}, {"tag": "equal", "positive_start": 1, "positive_end": 2, "negative_start": 1, "negative_end": 2, "positive_lexemes": ["are"], "negative_lexemes": ["are"]}, {"tag": "insert", "positive_start": 2, "positive_end": 2, "negative_start": 2, "negative_end": 3, "positive_lexemes": [], "negative_lexemes": ["watching"]}, {"tag": "replace", "positive_start": 2, "positive_end": 5, "negative_start": 3, "negative_end": 6, "positive_lexemes": ["people", "riding", "on"], "negative_lexemes": ["from", "afar", "as"]}, {"tag": "equal", "positive_start": 5, "positive_end": 7, "negative_start": 6, "negative_end": 8, "positive_lexemes": ["an", "elephant"], "negative_lexemes": ["an", "elephant"]}, {"tag": "insert", "positive_start": 7, "positive_end": 7, "negative_start": 8, "negative_end": 9, "positive_lexemes": [], "negative_lexemes": ["walks"]}, {"tag": "replace", "positive_start": 7, "positive_end": 8, "negative_start": 9, "negative_end": 10, "positive_lexemes": ["back"], "negative_lexemes": ["by"]}]`
- 共同前缀：`[]`
- 正确 contrast hull：`["there", "are", "people", "riding", "on", "an", "elephant", "back"]`
- 错误 contrast hull：`["people", "are", "watching", "from", "afar", "as", "an", "elephant", "walks", "by"]`
- 共同后缀：`[]`
- Hull token 覆盖率（正/负/最大）：`[1.0, 1.0, 1.0]`
- 共同前缀模型 token：`[]`
- 正确 hull 模型 token：IDs `[119, 2503, 732, 2975, 757, 460, 350, 619, 346, 1905, 1601, 811, 3901]`；text "there are people riding on an elephant back"
- 错误 hull 模型 token：IDs `[653, 2643, 732, 339, 6131, 350, 961, 299, 105, 370, 523, 346, 1905, 1601, 811, 339, 352, 1275, 769]`；text "people are watching from afar as an elephant walks by"
- 第一轮/第二轮分类：`complex_edit` / `whole_sentence_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；"at_least_one_hull_covers_all_model_tokens"

### 10. `replace_relation:133`

- 负例类型/范围：`replace_relation` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A couple of traffic lights sitting on the side of a road."
- 原始正描述 2："A couple of traffic lights are situated alongside the road."
- 原始负描述："A couple of traffic lights hanging above a road."
- 规范化正描述 1："a couple of traffic lights sitting on the side of a road"
- 规范化正描述 2："a couple of traffic lights are situated alongside the road"
- 规范化负描述："a couple of traffic lights hanging above a road"
- 正描述 1 选择元组：`[7, 7, 2, 0.4166666666666667, 0.30357142857142855]`
- 正描述 2 选择元组：`[7, 7, 2, 0.4, 0.3448275862068966]`
- 最终比较正描述：`positive_2` / "A couple of traffic lights are situated alongside the road."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 5, "negative_start": 0, "negative_end": 5, "positive_lexemes": ["a", "couple", "of", "traffic", "lights"], "negative_lexemes": ["a", "couple", "of", "traffic", "lights"]}, {"tag": "delete", "positive_start": 5, "positive_end": 6, "negative_start": 5, "negative_end": 5, "positive_lexemes": ["are"], "negative_lexemes": []}, {"tag": "replace", "positive_start": 6, "positive_end": 9, "negative_start": 5, "negative_end": 8, "positive_lexemes": ["situated", "alongside", "the"], "negative_lexemes": ["hanging", "above", "a"]}, {"tag": "equal", "positive_start": 9, "positive_end": 10, "negative_start": 8, "negative_end": 9, "positive_lexemes": ["road"], "negative_lexemes": ["road"]}]`
- 共同前缀：`["a", "couple", "of", "traffic", "lights"]`
- 正确 contrast hull：`["are", "situated", "alongside", "the"]`
- 错误 contrast hull：`["hanging", "above", "a"]`
- 共同后缀：`["road"]`
- Hull token 覆盖率（正/负/最大）：`[0.42105263157894735, 0.3125, 0.42105263157894735]`
- 共同前缀模型 token：`[100, 317, 326, 833, 354, 1946, 5935, 2795, 118]`
- 正确 hull 模型 token：IDs `[732, 5305, 120, 1095, 5782, 118, 688, 309]`；text " are situated alongside the"
- 错误 hull 模型 token：IDs `[429, 942, 350, 6264, 299]`；text " hanging above a"
- 第一轮/第二轮分类：`unique_alignment` / `multi_block_local_hull`
- 自动判断："positive_2_selection_tuple_lexicographically_smaller"；null

### 11. `replace_relation:2`

- 负例类型/范围：`replace_relation` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："THERE ARE WOMEN THAT ARE LAUGHING UNDER THE UMBRELLA"
- 原始正描述 2："The women are laughing under the umbrella."
- 原始负描述："There are women that are laughing next to the umbrella."
- 规范化正描述 1："there are women that are laughing under the umbrella"
- 规范化正描述 2："the women are laughing under the umbrella"
- 规范化负描述："there are women that are laughing next to the umbrella"
- 正描述 1 选择元组：`[3, 3, 2, 0.2, 0.12962962962962962]`
- 正描述 2 选择元组：`[7, 13, 5, 0.5, 0.3333333333333333]`
- 最终比较正描述：`positive_1` / "THERE ARE WOMEN THAT ARE LAUGHING UNDER THE UMBRELLA"
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 6, "negative_start": 0, "negative_end": 6, "positive_lexemes": ["there", "are", "women", "that", "are", "laughing"], "negative_lexemes": ["there", "are", "women", "that", "are", "laughing"]}, {"tag": "insert", "positive_start": 6, "positive_end": 6, "negative_start": 6, "negative_end": 7, "positive_lexemes": [], "negative_lexemes": ["next"]}, {"tag": "replace", "positive_start": 6, "positive_end": 7, "negative_start": 7, "negative_end": 8, "positive_lexemes": ["under"], "negative_lexemes": ["to"]}, {"tag": "equal", "positive_start": 7, "positive_end": 9, "negative_start": 8, "negative_end": 10, "positive_lexemes": ["the", "umbrella"], "negative_lexemes": ["the", "umbrella"]}]`
- 共同前缀：`["there", "are", "women", "that", "are", "laughing"]`
- 正确 contrast hull：`["under"]`
- 错误 contrast hull：`["next", "to"]`
- 共同后缀：`["the", "umbrella"]`
- Hull token 覆盖率（正/负/最大）：`[0.05263157894736842, 0.1, 0.1]`
- 共同前缀模型 token：`[119, 2503, 732, 339, 444, 327, 591, 732, 406, 1900, 1518, 350]`
- 正确 hull 模型 token：IDs `[1943]`；text " under"
- 错误 hull 模型 token：IDs `[4658, 364]`；text " next to"
- 第一轮/第二轮分类：`complex_edit` / `multi_block_local_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 12. `replace_relation:210`

- 负例类型/范围：`replace_relation` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："Hot dog with mustard on it sitting on a white napkin."
- 原始正描述 2："A hot dog with mustard is placed on a white napkin."
- 原始负描述："A hot dog with mustard on it is standing on a white napkin."
- 规范化正描述 1："hot dog with mustard on it sitting on a white napkin"
- 规范化正描述 2："a hot dog with mustard is placed on a white napkin"
- 规范化负描述："a hot dog with mustard on it is standing on a white napkin"
- 正描述 1 选择元组：`[4, 16, 3, 0.23076923076923078, 0.13793103448275862]`
- 正描述 2 选择元组：`[4, 6, 2, 0.23076923076923078, 0.22413793103448276]`
- 最终比较正描述：`positive_2` / "A hot dog with mustard is placed on a white napkin."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 5, "negative_start": 0, "negative_end": 5, "positive_lexemes": ["a", "hot", "dog", "with", "mustard"], "negative_lexemes": ["a", "hot", "dog", "with", "mustard"]}, {"tag": "insert", "positive_start": 5, "positive_end": 5, "negative_start": 5, "negative_end": 7, "positive_lexemes": [], "negative_lexemes": ["on", "it"]}, {"tag": "equal", "positive_start": 5, "positive_end": 6, "negative_start": 7, "negative_end": 8, "positive_lexemes": ["is"], "negative_lexemes": ["is"]}, {"tag": "replace", "positive_start": 6, "positive_end": 7, "negative_start": 8, "negative_end": 9, "positive_lexemes": ["placed"], "negative_lexemes": ["standing"]}, {"tag": "equal", "positive_start": 7, "positive_end": 11, "negative_start": 9, "negative_end": 13, "positive_lexemes": ["on", "a", "white", "napkin"], "negative_lexemes": ["on", "a", "white", "napkin"]}]`
- 共同前缀：`["a", "hot", "dog", "with", "mustard"]`
- 正确 contrast hull：`["is", "placed"]`
- 错误 contrast hull：`["on", "it", "is", "standing"]`
- 共同后缀：`["on", "a", "white", "napkin"]`
- Hull token 覆盖率（正/负/最大）：`[0.2, 0.23809523809523808, 0.23809523809523808]`
- 共同前缀模型 token：`[100, 429, 593, 1041, 106, 599, 5385, 1433]`
- 正确 hull 模型 token：IDs `[395, 1219, 1545, 382]`；text " is placed"
- 错误 hull 模型 token：IDs `[619, 563, 395, 2823, 350]`；text " on it is standing"
- 第一轮/第二轮分类：`complex_edit` / `multi_block_local_hull`
- 自动判断："positive_2_selection_tuple_lexicographically_smaller"；null

### 13. `replace_relation:377`

- 负例类型/范围：`replace_relation` / `{"canonical": true, "pilot": true, "formal": false, "certifying_formal": false}`
- 原始正描述 1："aerial view of suitcases grouped together waiting on a sidewalk"
- 原始正描述 2："The aerial view shows suitcases arranged together on a sidewalk."
- 原始负描述："Aerial view of suitcases scattered on a sidewalk."
- 规范化正描述 1："aerial view of suitcases grouped together waiting on a sidewalk"
- 规范化正描述 2："the aerial view shows suitcases arranged together on a sidewalk"
- 规范化负描述："aerial view of suitcases scattered on a sidewalk"
- 正描述 1 选择元组：`[4, 4, 2, 0.3, 0.31746031746031744]`
- 正描述 2 选择元组：`[6, 12, 4, 0.4, 0.3333333333333333]`
- 最终比较正描述：`positive_1` / "aerial view of suitcases grouped together waiting on a sidewalk"
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 4, "negative_start": 0, "negative_end": 4, "positive_lexemes": ["aerial", "view", "of", "suitcases"], "negative_lexemes": ["aerial", "view", "of", "suitcases"]}, {"tag": "delete", "positive_start": 4, "positive_end": 6, "negative_start": 4, "negative_end": 4, "positive_lexemes": ["grouped", "together"], "negative_lexemes": []}, {"tag": "replace", "positive_start": 6, "positive_end": 7, "negative_start": 4, "negative_end": 5, "positive_lexemes": ["waiting"], "negative_lexemes": ["scattered"]}, {"tag": "equal", "positive_start": 7, "positive_end": 10, "negative_start": 5, "negative_end": 8, "positive_lexemes": ["on", "a", "sidewalk"], "negative_lexemes": ["on", "a", "sidewalk"]}]`
- 共同前缀：`["aerial", "view", "of", "suitcases"]`
- 正确 contrast hull：`["grouped", "together", "waiting"]`
- 错误 contrast hull：`["scattered"]`
- 共同后缀：`["on", "a", "sidewalk"]`
- Hull token 覆盖率（正/负/最大）：`[0.2727272727272727, 0.2, 0.2727272727272727]`
- 共同前缀模型 token：`[100, 311, 926, 603, 1400, 122, 354, 855, 338, 102, 3164]`
- 正确 hull 模型 token：IDs `[4592, 382, 5169, 339, 100, 5945]`；text " grouped together waiting"
- 错误 hull 模型 token：IDs `[1416, 314, 741, 1837]`；text " scattered"
- 第一轮/第二轮分类：`complex_edit` / `multi_block_local_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 14. `replace_relation:407`

- 负例类型/范围：`replace_relation` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A person sitting on top of a bus over a billboard."
- 原始正描述 2："A person sits atop a bus above a billboard."
- 原始负描述："A person sitting beside a bus near a billboard."
- 规范化正描述 1："a person sitting on top of a bus over a billboard"
- 规范化正描述 2："a person sits atop a bus above a billboard"
- 规范化负描述："a person sitting beside a bus near a billboard"
- 正描述 1 选择元组：`[6, 10, 3, 0.36363636363636365, 0.24489795918367346]`
- 正描述 2 选择元组：`[6, 10, 2, 0.3333333333333333, 0.32608695652173914]`
- 最终比较正描述：`positive_2` / "A person sits atop a bus above a billboard."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 2, "negative_start": 0, "negative_end": 2, "positive_lexemes": ["a", "person"], "negative_lexemes": ["a", "person"]}, {"tag": "replace", "positive_start": 2, "positive_end": 4, "negative_start": 2, "negative_end": 4, "positive_lexemes": ["sits", "atop"], "negative_lexemes": ["sitting", "beside"]}, {"tag": "equal", "positive_start": 4, "positive_end": 6, "negative_start": 4, "negative_end": 6, "positive_lexemes": ["a", "bus"], "negative_lexemes": ["a", "bus"]}, {"tag": "replace", "positive_start": 6, "positive_end": 7, "negative_start": 6, "negative_end": 7, "positive_lexemes": ["above"], "negative_lexemes": ["near"]}, {"tag": "equal", "positive_start": 7, "positive_end": 9, "negative_start": 7, "negative_end": 9, "positive_lexemes": ["a", "billboard"], "negative_lexemes": ["a", "billboard"]}]`
- 共同前缀：`["a", "person"]`
- 正确 contrast hull：`["sits", "atop", "a", "bus", "above"]`
- 错误 contrast hull：`["sitting", "beside", "a", "bus", "near"]`
- 共同后缀：`["a", "billboard"]`
- Hull token 覆盖率（正/负/最大）：`[0.4666666666666667, 0.5294117647058824, 0.5294117647058824]`
- 共同前缀模型 token：`[100, 2198]`
- 正确 hull 模型 token：IDs `[316, 2163, 1248, 1506, 299, 2499, 6264]`；text " sits atop a bus above"
- 错误 hull 模型 token：IDs `[5305, 2912, 363, 329, 688, 299, 2499, 730, 370]`；text " sitting beside a bus near"
- 第一轮/第二轮分类：`complex_edit` / `multi_block_local_hull`
- 自动判断："positive_2_selection_tuple_lexicographically_smaller"；null

### 15. `replace_relation:424`

- 负例类型/范围：`replace_relation` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A airplane that is sitting on a runway."
- 原始正描述 2："The airplane is situated on the runway."
- 原始负描述："An airplane that is soaring above the clouds."
- 规范化正描述 1："a airplane that is sitting on a runway"
- 规范化正描述 2："the airplane is situated on the runway"
- 规范化负描述："an airplane that is soaring above the clouds"
- 正描述 1 选择元组：`[10, 16, 2, 0.625, 0.38636363636363635]`
- 正描述 2 选择元组：`[9, 15, 4, 0.625, 0.5681818181818182]`
- 最终比较正描述：`positive_2` / "The airplane is situated on the runway."
- 完整 lexeme 编辑块：`[{"tag": "replace", "positive_start": 0, "positive_end": 1, "negative_start": 0, "negative_end": 1, "positive_lexemes": ["the"], "negative_lexemes": ["an"]}, {"tag": "equal", "positive_start": 1, "positive_end": 2, "negative_start": 1, "negative_end": 2, "positive_lexemes": ["airplane"], "negative_lexemes": ["airplane"]}, {"tag": "insert", "positive_start": 2, "positive_end": 2, "negative_start": 2, "negative_end": 3, "positive_lexemes": [], "negative_lexemes": ["that"]}, {"tag": "equal", "positive_start": 2, "positive_end": 3, "negative_start": 3, "negative_end": 4, "positive_lexemes": ["is"], "negative_lexemes": ["is"]}, {"tag": "replace", "positive_start": 3, "positive_end": 5, "negative_start": 4, "negative_end": 6, "positive_lexemes": ["situated", "on"], "negative_lexemes": ["soaring", "above"]}, {"tag": "equal", "positive_start": 5, "positive_end": 6, "negative_start": 6, "negative_end": 7, "positive_lexemes": ["the"], "negative_lexemes": ["the"]}, {"tag": "replace", "positive_start": 6, "positive_end": 7, "negative_start": 7, "negative_end": 8, "positive_lexemes": ["runway"], "negative_lexemes": ["clouds"]}]`
- 共同前缀：`[]`
- 正确 contrast hull：`["the", "airplane", "is", "situated", "on", "the", "runway"]`
- 错误 contrast hull：`["an", "airplane", "that", "is", "soaring", "above", "the", "clouds"]`
- 共同后缀：`[]`
- Hull token 覆盖率（正/负/最大）：`[1.0, 1.0, 1.0]`
- 共同前缀模型 token：`[]`
- 正确 hull 模型 token：IDs `[4345, 3980, 992, 4875, 395, 5305, 120, 1095, 619, 309, 3161, 5054]`；text "the airplane is situated on the runway"
- 错误 hull 模型 token：IDs `[325, 3980, 992, 4875, 591, 395, 1122, 370, 350, 6264, 309, 2751, 118]`；text "an airplane that is soaring above the clouds"
- 第一轮/第二轮分类：`complex_edit` / `whole_sentence_hull`
- 自动判断："positive_2_selection_tuple_lexicographically_smaller"；"at_least_one_hull_covers_all_model_tokens"

### 16. `replace_relation:645`

- 负例类型/范围：`replace_relation` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："Cowboy riding a horse in a huge pasture..\n"
- 原始正描述 2："A cowboy is mounted on a horse in a vast pasture."
- 原始负描述："A cowboy is talking to a horse in a huge pasture."
- 规范化正描述 1："cowboy riding a horse in a huge pasture"
- 规范化正描述 2："a cowboy is mounted on a horse in a vast pasture"
- 规范化负描述："a cowboy is talking to a horse in a huge pasture"
- 正描述 1 选择元组：`[5, 7, 3, 0.36363636363636365, 0.25]`
- 正描述 2 选择元组：`[6, 14, 2, 0.2727272727272727, 0.2708333333333333]`
- 最终比较正描述：`positive_1` / "Cowboy riding a horse in a huge pasture..\n"
- 完整 lexeme 编辑块：`[{"tag": "insert", "positive_start": 0, "positive_end": 0, "negative_start": 0, "negative_end": 1, "positive_lexemes": [], "negative_lexemes": ["a"]}, {"tag": "equal", "positive_start": 0, "positive_end": 1, "negative_start": 1, "negative_end": 2, "positive_lexemes": ["cowboy"], "negative_lexemes": ["cowboy"]}, {"tag": "insert", "positive_start": 1, "positive_end": 1, "negative_start": 2, "negative_end": 4, "positive_lexemes": [], "negative_lexemes": ["is", "talking"]}, {"tag": "replace", "positive_start": 1, "positive_end": 2, "negative_start": 4, "negative_end": 5, "positive_lexemes": ["riding"], "negative_lexemes": ["to"]}, {"tag": "equal", "positive_start": 2, "positive_end": 8, "negative_start": 5, "negative_end": 11, "positive_lexemes": ["a", "horse", "in", "a", "huge", "pasture"], "negative_lexemes": ["a", "horse", "in", "a", "huge", "pasture"]}]`
- 共同前缀：`[]`
- 正确 contrast hull：`["cowboy", "riding"]`
- 错误 contrast hull：`["a", "cowboy", "is", "talking", "to"]`
- 共同后缀：`["a", "horse", "in", "a", "huge", "pasture"]`
- Hull token 覆盖率（正/负/最大）：`[0.3684210526315789, 0.45454545454545453, 0.45454545454545453]`
- 共同前缀模型 token：`[]`
- 正确 hull 模型 token：IDs `[102, 451, 101, 4117, 757, 460, 350]`；text "cowboy riding"
- 错误 hull 模型 token：IDs `[100, 317, 451, 101, 4117, 395, 297, 352, 1237, 364]`；text "a cowboy is talking to"
- 第一轮/第二轮分类：`complex_edit` / `multi_block_local_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 17. `replace_relation:961`

- 负例类型/范围：`replace_relation` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："THERE IS A FIRE BURNING IN THE FIREPLACE IN A SITTING ROOM"
- 原始正描述 2："The fireplace is located in the sitting room, and a fire is burning within it."
- 原始负描述："The fire in the fireplace in a sitting room has been extinguished."
- 规范化正描述 1："there is a fire burning in the fireplace in a sitting room"
- 规范化正描述 2："the fireplace is located in the sitting room , and a fire is burning within it"
- 规范化负描述："the fire in the fireplace in a sitting room has been extinguished"
- 正描述 1 选择元组：`[8, 24, 4, 0.5833333333333334, 0.5692307692307692]`
- 正描述 2 选择元组：`[20, 26, 5, 0.75, 0.5256410256410257]`
- 最终比较正描述：`positive_1` / "THERE IS A FIRE BURNING IN THE FIREPLACE IN A SITTING ROOM"
- 完整 lexeme 编辑块：`[{"tag": "delete", "positive_start": 0, "positive_end": 2, "negative_start": 0, "negative_end": 0, "positive_lexemes": ["there", "is"], "negative_lexemes": []}, {"tag": "replace", "positive_start": 2, "positive_end": 3, "negative_start": 0, "negative_end": 1, "positive_lexemes": ["a"], "negative_lexemes": ["the"]}, {"tag": "equal", "positive_start": 3, "positive_end": 4, "negative_start": 1, "negative_end": 2, "positive_lexemes": ["fire"], "negative_lexemes": ["fire"]}, {"tag": "delete", "positive_start": 4, "positive_end": 5, "negative_start": 2, "negative_end": 2, "positive_lexemes": ["burning"], "negative_lexemes": []}, {"tag": "equal", "positive_start": 5, "positive_end": 12, "negative_start": 2, "negative_end": 9, "positive_lexemes": ["in", "the", "fireplace", "in", "a", "sitting", "room"], "negative_lexemes": ["in", "the", "fireplace", "in", "a", "sitting", "room"]}, {"tag": "insert", "positive_start": 12, "positive_end": 12, "negative_start": 9, "negative_end": 12, "positive_lexemes": [], "negative_lexemes": ["has", "been", "extinguished"]}]`
- 共同前缀：`[]`
- 正确 contrast hull：`["there", "is", "a", "fire", "burning", "in", "the", "fireplace", "in", "a", "sitting", "room"]`
- 错误 contrast hull：`["the", "fire", "in", "the", "fireplace", "in", "a", "sitting", "room", "has", "been", "extinguished"]`
- 共同后缀：`[]`
- Hull token 覆盖率（正/负/最大）：`[1.0, 1.0, 1.0]`
- 共同前缀模型 token：`[]`
- 正确 hull 模型 token：IDs `[119, 2503, 395, 299, 341, 1475, 363, 1262, 350, 353, 309, 341, 1475, 4256, 353, 299, 5305, 2912, 1552, 444]`；text "there is a fire burning in the fireplace in a sitting room"
- 错误 hull 模型 token：IDs `[4345, 341, 1475, 353, 309, 341, 1475, 4256, 353, 299, 5305, 2912, 1552, 444, 1290, 2433, 719, 2912, 120, 4840]`；text "the fire in the fireplace in a sitting room has been extinguished"
- 第一轮/第二轮分类：`complex_edit` / `whole_sentence_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；"at_least_one_hull_covers_all_model_tokens"

### 18. `swap_atribute:161`

- 负例类型/范围：`swap_atribute` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": false}`
- 原始正描述 1："a black person wearing white attire and shoes running on a tennis court,"
- 原始正描述 2："A black person wearing white attire and shoes is running on a tennis court."
- 原始负描述："a white person wearing black attire and shoes running on a tennis court."
- 规范化正描述 1："a black person wearing white attire and shoes running on a tennis court ,"
- 规范化正描述 2："a black person wearing white attire and shoes is running on a tennis court"
- 规范化负描述："a white person wearing black attire and shoes running on a tennis court"
- 正描述 1 选择元组：`[5, 25, 3, 0.21428571428571427, 0.1643835616438356]`
- 正描述 2 选择元组：`[5, 15, 3, 0.21428571428571427, 0.17567567567567569]`
- 最终比较正描述：`positive_2` / "A black person wearing white attire and shoes is running on a tennis court."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 1, "negative_start": 0, "negative_end": 1, "positive_lexemes": ["a"], "negative_lexemes": ["a"]}, {"tag": "replace", "positive_start": 1, "positive_end": 2, "negative_start": 1, "negative_end": 2, "positive_lexemes": ["black"], "negative_lexemes": ["white"]}, {"tag": "equal", "positive_start": 2, "positive_end": 4, "negative_start": 2, "negative_end": 4, "positive_lexemes": ["person", "wearing"], "negative_lexemes": ["person", "wearing"]}, {"tag": "replace", "positive_start": 4, "positive_end": 5, "negative_start": 4, "negative_end": 5, "positive_lexemes": ["white"], "negative_lexemes": ["black"]}, {"tag": "equal", "positive_start": 5, "positive_end": 8, "negative_start": 5, "negative_end": 8, "positive_lexemes": ["attire", "and", "shoes"], "negative_lexemes": ["attire", "and", "shoes"]}, {"tag": "delete", "positive_start": 8, "positive_end": 9, "negative_start": 8, "negative_end": 8, "positive_lexemes": ["is"], "negative_lexemes": []}, {"tag": "equal", "positive_start": 9, "positive_end": 14, "negative_start": 8, "negative_end": 13, "positive_lexemes": ["running", "on", "a", "tennis", "court"], "negative_lexemes": ["running", "on", "a", "tennis", "court"]}]`
- 共同前缀：`["a"]`
- 正确 contrast hull：`["black", "person", "wearing", "white", "attire", "and", "shoes", "is"]`
- 错误 contrast hull：`["white", "person", "wearing", "black", "attire", "and", "shoes"]`
- 共同后缀：`["running", "on", "a", "tennis", "court"]`
- Hull token 覆盖率（正/负/最大）：`[0.6, 0.5833333333333334, 0.6]`
- 共同前缀模型 token：`[100]`
- 正确 hull 模型 token：IDs `[2597, 1637, 2198, 796, 370, 350, 654, 1078, 3783, 1475, 376, 1128, 114, 329, 395]`；text " black person wearing white attire and shoes is"
- 错误 hull 模型 token：IDs `[654, 1078, 2198, 796, 370, 350, 2597, 1637, 3783, 1475, 376, 1128, 114, 329]`；text " white person wearing black attire and shoes"
- 第一轮/第二轮分类：`complex_edit` / `multi_block_local_hull`
- 自动判断："positive_2_selection_tuple_lexicographically_smaller"；null

### 19. `swap_atribute:285`

- 负例类型/范围：`swap_atribute` / `{"canonical": true, "pilot": true, "formal": false, "certifying_formal": false}`
- 原始正描述 1："Two people standing next to a life size replica of a suitcase."
- 原始正描述 2："Two individuals are positioned adjacent to a full-scale representation of a suitcase."
- 原始负描述："A life size replica of two people standing next to a suitcase."
- 规范化正描述 1："two people standing next to a life size replica of a suitcase"
- 规范化正描述 2："two individuals are positioned adjacent to a full-scale representation of a suitcase"
- 规范化负描述："a life size replica of two people standing next to a suitcase"
- 正描述 1 选择元组：`[20, 20, 1, 0.8333333333333334, 0.6557377049180327]`
- 正描述 2 选择元组：`[20, 20, 1, 0.8333333333333334, 0.6547619047619048]`
- 最终比较正描述：`positive_2` / "Two individuals are positioned adjacent to a full-scale representation of a suitcase."
- 完整 lexeme 编辑块：`[{"tag": "replace", "positive_start": 0, "positive_end": 10, "negative_start": 0, "negative_end": 10, "positive_lexemes": ["two", "individuals", "are", "positioned", "adjacent", "to", "a", "full-scale", "representation", "of"], "negative_lexemes": ["a", "life", "size", "replica", "of", "two", "people", "standing", "next", "to"]}, {"tag": "equal", "positive_start": 10, "positive_end": 12, "negative_start": 10, "negative_end": 12, "positive_lexemes": ["a", "suitcase"], "negative_lexemes": ["a", "suitcase"]}]`
- 共同前缀：`[]`
- 正确 contrast hull：`["two", "individuals", "are", "positioned", "adjacent", "to", "a", "full-scale", "representation", "of"]`
- 错误 contrast hull：`["a", "life", "size", "replica", "of", "two", "people", "standing", "next", "to"]`
- 共同后缀：`["a", "suitcase"]`
- Hull token 覆盖率（正/负/最大）：`[0.84, 0.7647058823529411, 0.84]`
- 共同前缀模型 token：`[]`
- 正确 hull 模型 token：IDs `[119, 122, 114, 6203, 732, 2617, 1632, 382, 1200, 109, 1545, 425, 364, 299, 5840, 48, 4223, 3675, 4400, 489, 354]`；text "two individuals are positioned adjacent to a full-scale representation of"
- 错误 hull 模型 token：IDs `[100, 3327, 4639, 422, 4504, 100, 354, 2102, 2975, 2823, 350, 4658, 364]`；text "a life size replica of two people standing next to"
- 第一轮/第二轮分类：`complex_edit` / `large_contrast_hull`
- 自动判断："positive_2_selection_tuple_lexicographically_smaller"；"maximum_hull_token_coverage_above_75_percent"

### 20. `swap_atribute:365`

- 负例类型/范围：`swap_atribute` / `{"canonical": true, "pilot": true, "formal": false, "certifying_formal": false}`
- 原始正描述 1："A dime surrounded by a bunch of stones with holes in them"
- 原始正描述 2："A dime is surrounded by a group of stones with holes in them."
- 原始负描述："A bunch of dimes surrounded by a stone with a hole in it."
- 规范化正描述 1："a dime surrounded by a bunch of stones with holes in them"
- 规范化正描述 2："a dime is surrounded by a group of stones with holes in them"
- 规范化负描述："a bunch of dimes surrounded by a stone with a hole in it"
- 正描述 1 选择元组：`[15, 23, 5, 0.6923076923076923, 0.47368421052631576]`
- 正描述 2 选择元组：`[16, 24, 5, 0.6923076923076923, 0.4666666666666667]`
- 最终比较正描述：`positive_1` / "A dime surrounded by a bunch of stones with holes in them"
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 1, "negative_start": 0, "negative_end": 1, "positive_lexemes": ["a"], "negative_lexemes": ["a"]}, {"tag": "insert", "positive_start": 1, "positive_end": 1, "negative_start": 1, "negative_end": 3, "positive_lexemes": [], "negative_lexemes": ["bunch", "of"]}, {"tag": "replace", "positive_start": 1, "positive_end": 2, "negative_start": 3, "negative_end": 4, "positive_lexemes": ["dime"], "negative_lexemes": ["dimes"]}, {"tag": "equal", "positive_start": 2, "positive_end": 5, "negative_start": 4, "negative_end": 7, "positive_lexemes": ["surrounded", "by", "a"], "negative_lexemes": ["surrounded", "by", "a"]}, {"tag": "delete", "positive_start": 5, "positive_end": 6, "negative_start": 7, "negative_end": 7, "positive_lexemes": ["bunch"], "negative_lexemes": []}, {"tag": "replace", "positive_start": 6, "positive_end": 10, "negative_start": 7, "negative_end": 11, "positive_lexemes": ["of", "stones", "with", "holes"], "negative_lexemes": ["stone", "with", "a", "hole"]}, {"tag": "equal", "positive_start": 10, "positive_end": 11, "negative_start": 11, "negative_end": 12, "positive_lexemes": ["in"], "negative_lexemes": ["in"]}, {"tag": "replace", "positive_start": 11, "positive_end": 12, "negative_start": 12, "negative_end": 13, "positive_lexemes": ["them"], "negative_lexemes": ["it"]}]`
- 共同前缀：`["a"]`
- 正确 contrast hull：`["dime", "surrounded", "by", "a", "bunch", "of", "stones", "with", "holes", "in", "them"]`
- 错误 contrast hull：`["bunch", "of", "dimes", "surrounded", "by", "a", "stone", "with", "a", "hole", "in", "it"]`
- 共同后缀：`[]`
- Hull token 覆盖率（正/负/最大）：`[0.9523809523809523, 0.95, 0.9523809523809523]`
- 共同前缀模型 token：`[100]`
- 正确 hull 模型 token：IDs `[373, 1174, 3946, 2383, 382, 769, 299, 363, 651, 550, 354, 580, 310, 329, 599, 429, 500, 329, 353, 2105]`；text " dime surrounded by a bunch of stones with holes in them"
- 错误 hull 模型 token：IDs `[363, 651, 550, 354, 373, 1608, 3946, 2383, 382, 769, 299, 580, 1634, 599, 299, 6271, 361, 353, 563]`；text " bunch of dimes surrounded by a stone with a hole in it"
- 第一轮/第二轮分类：`complex_edit` / `large_contrast_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；"maximum_hull_token_coverage_above_75_percent"

### 21. `swap_atribute:453`

- 负例类型/范围：`swap_atribute` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A bunch of different foods on display on  a counter."
- 原始正描述 2："A variety of foods are displayed on a counter."
- 原始负描述："Different foods are on display on a bunch of counters."
- 规范化正描述 1："a bunch of different foods on display on a counter"
- 规范化正描述 2："a variety of foods are displayed on a counter"
- 规范化负描述："different foods are on display on a bunch of counters"
- 正描述 1 选择元组：`[8, 20, 4, 0.7, 0.4716981132075472]`
- 正描述 2 选择元组：`[11, 19, 6, 0.8, 0.49056603773584906]`
- 最终比较正描述：`positive_1` / "A bunch of different foods on display on  a counter."
- 完整 lexeme 编辑块：`[{"tag": "delete", "positive_start": 0, "positive_end": 3, "negative_start": 0, "negative_end": 0, "positive_lexemes": ["a", "bunch", "of"], "negative_lexemes": []}, {"tag": "equal", "positive_start": 3, "positive_end": 5, "negative_start": 0, "negative_end": 2, "positive_lexemes": ["different", "foods"], "negative_lexemes": ["different", "foods"]}, {"tag": "insert", "positive_start": 5, "positive_end": 5, "negative_start": 2, "negative_end": 3, "positive_lexemes": [], "negative_lexemes": ["are"]}, {"tag": "equal", "positive_start": 5, "positive_end": 9, "negative_start": 3, "negative_end": 7, "positive_lexemes": ["on", "display", "on", "a"], "negative_lexemes": ["on", "display", "on", "a"]}, {"tag": "insert", "positive_start": 9, "positive_end": 9, "negative_start": 7, "negative_end": 9, "positive_lexemes": [], "negative_lexemes": ["bunch", "of"]}, {"tag": "replace", "positive_start": 9, "positive_end": 10, "negative_start": 9, "negative_end": 10, "positive_lexemes": ["counter"], "negative_lexemes": ["counters"]}]`
- 共同前缀：`[]`
- 正确 contrast hull：`["a", "bunch", "of", "different", "foods", "on", "display", "on", "a", "counter"]`
- 错误 contrast hull：`["different", "foods", "are", "on", "display", "on", "a", "bunch", "of", "counters"]`
- 共同后缀：`[]`
- Hull token 覆盖率（正/负/最大）：`[1.0, 1.0, 1.0]`
- 共同前缀模型 token：`[]`
- 正确 hull 模型 token：IDs `[100, 363, 651, 550, 354, 2301, 341, 824, 1881, 619, 1981, 4838, 619, 299, 2320, 311]`；text "a bunch of different foods on display on a counter"
- 错误 hull 模型 token：IDs `[103, 507, 1617, 694, 341, 824, 1881, 732, 619, 1981, 4838, 619, 299, 363, 651, 550, 354, 2320, 496]`；text "different foods are on display on a bunch of counters"
- 第一轮/第二轮分类：`complex_edit` / `whole_sentence_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；"at_least_one_hull_covers_all_model_tokens"

### 22. `swap_atribute:460`

- 负例类型/范围：`swap_atribute` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A couple of people that are standing near a train."
- 原始正描述 2："Near a train, a couple of people stand."
- 原始负描述："Near a couple of trains, people are standing."
- 规范化正描述 1："a couple of people that are standing near a train"
- 规范化正描述 2："near a train , a couple of people stand"
- 规范化负描述："near a couple of trains , people are standing"
- 正描述 1 选择元组：`[9, 19, 4, 0.7, 0.6530612244897959]`
- 正描述 2 选择元组：`[14, 14, 1, 0.7777777777777778, 0.5333333333333333]`
- 最终比较正描述：`positive_1` / "A couple of people that are standing near a train."
- 完整 lexeme 编辑块：`[{"tag": "insert", "positive_start": 0, "positive_end": 0, "negative_start": 0, "negative_end": 1, "positive_lexemes": [], "negative_lexemes": ["near"]}, {"tag": "equal", "positive_start": 0, "positive_end": 3, "negative_start": 1, "negative_end": 4, "positive_lexemes": ["a", "couple", "of"], "negative_lexemes": ["a", "couple", "of"]}, {"tag": "insert", "positive_start": 3, "positive_end": 3, "negative_start": 4, "negative_end": 5, "positive_lexemes": [], "negative_lexemes": ["trains"]}, {"tag": "replace", "positive_start": 3, "positive_end": 5, "negative_start": 5, "negative_end": 7, "positive_lexemes": ["people", "that"], "negative_lexemes": [",", "people"]}, {"tag": "equal", "positive_start": 5, "positive_end": 7, "negative_start": 7, "negative_end": 9, "positive_lexemes": ["are", "standing"], "negative_lexemes": ["are", "standing"]}, {"tag": "delete", "positive_start": 7, "positive_end": 10, "negative_start": 9, "negative_end": 9, "positive_lexemes": ["near", "a", "train"], "negative_lexemes": []}]`
- 共同前缀：`[]`
- 正确 contrast hull：`["a", "couple", "of", "people", "that", "are", "standing", "near", "a", "train"]`
- 错误 contrast hull：`["near", "a", "couple", "of", "trains", ",", "people", "are", "standing"]`
- 共同后缀：`[]`
- Hull token 覆盖率（正/负/最大）：`[1.0, 1.0, 1.0]`
- 共同前缀模型 token：`[]`
- 正确 hull 模型 token：IDs `[100, 317, 326, 833, 354, 2975, 591, 732, 2823, 350, 730, 370, 299, 1946, 301]`；text "a couple of people that are standing near a train"
- 错误 hull 模型 token：IDs `[113, 1655, 299, 317, 326, 833, 354, 1946, 4444, 256, 47, 2975, 732, 2823, 350]`；text "near a couple of trains , people are standing"
- 第一轮/第二轮分类：`complex_edit` / `whole_sentence_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；"at_least_one_hull_covers_all_model_tokens"

### 23. `swap_atribute:592`

- 负例类型/范围：`swap_atribute` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A very big work station with a bunch of computers."
- 原始正描述 2："A large workspace with numerous computers."
- 原始负描述："A bunch of work stations with a very big computer."
- 规范化正描述 1："a very big work station with a bunch of computers"
- 规范化正描述 2："a large workspace with numerous computers"
- 规范化负描述："a bunch of work stations with a very big computer"
- 正描述 1 选择元组：`[12, 18, 3, 0.6, 0.3673469387755102]`
- 正描述 2 选择元组：`[12, 14, 4, 0.8, 0.4897959183673469]`
- 最终比较正描述：`positive_2` / "A large workspace with numerous computers."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 1, "negative_start": 0, "negative_end": 1, "positive_lexemes": ["a"], "negative_lexemes": ["a"]}, {"tag": "insert", "positive_start": 1, "positive_end": 1, "negative_start": 1, "negative_end": 3, "positive_lexemes": [], "negative_lexemes": ["bunch", "of"]}, {"tag": "replace", "positive_start": 1, "positive_end": 3, "negative_start": 3, "negative_end": 5, "positive_lexemes": ["large", "workspace"], "negative_lexemes": ["work", "stations"]}, {"tag": "equal", "positive_start": 3, "positive_end": 4, "negative_start": 5, "negative_end": 6, "positive_lexemes": ["with"], "negative_lexemes": ["with"]}, {"tag": "insert", "positive_start": 4, "positive_end": 4, "negative_start": 6, "negative_end": 8, "positive_lexemes": [], "negative_lexemes": ["a", "very"]}, {"tag": "replace", "positive_start": 4, "positive_end": 6, "negative_start": 8, "negative_end": 10, "positive_lexemes": ["numerous", "computers"], "negative_lexemes": ["big", "computer"]}]`
- 共同前缀：`["a"]`
- 正确 contrast hull：`["large", "workspace", "with", "numerous", "computers"]`
- 错误 contrast hull：`["bunch", "of", "work", "stations", "with", "a", "very", "big", "computer"]`
- 共同后缀：`[]`
- Hull token 覆盖率（正/负/最大）：`[0.9, 0.9285714285714286, 0.9285714285714286]`
- 共同前缀模型 token：`[100]`
- 正确 hull 模型 token：IDs `[2994, 5775, 115, 1489, 599, 5636, 1301, 2078, 496]`；text " large workspace with numerous computers"
- 错误 hull 模型 token：IDs `[363, 651, 550, 354, 2943, 580, 1242, 599, 299, 4965, 363, 499, 4818]`；text " bunch of work stations with a very big computer"
- 第一轮/第二轮分类：`complex_edit` / `large_contrast_hull`
- 自动判断："positive_2_selection_tuple_lexicographically_smaller"；"maximum_hull_token_coverage_above_75_percent"

### 24. `swap_object:0`

- 负例类型/范围：`swap_object` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A cat sits on its hind legs, and swats at the plant."
- 原始正描述 2："The cat swats at the plant while sitting on its hind legs."
- 原始负描述："A cat sits on the plant, and swats at its hind legs."
- 规范化正描述 1："a cat sits on its hind legs , and swats at the plant"
- 规范化正描述 2："the cat swats at the plant while sitting on its hind legs"
- 规范化负描述："a cat sits on the plant , and swats at its hind legs"
- 正描述 1 选择元组：`[10, 18, 4, 0.46153846153846156, 0.38461538461538464]`
- 正描述 2 选择元组：`[13, 19, 4, 0.5384615384615384, 0.3333333333333333]`
- 最终比较正描述：`positive_1` / "A cat sits on its hind legs, and swats at the plant."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 4, "negative_start": 0, "negative_end": 4, "positive_lexemes": ["a", "cat", "sits", "on"], "negative_lexemes": ["a", "cat", "sits", "on"]}, {"tag": "delete", "positive_start": 4, "positive_end": 5, "negative_start": 4, "negative_end": 4, "positive_lexemes": ["its"], "negative_lexemes": []}, {"tag": "replace", "positive_start": 5, "positive_end": 7, "negative_start": 4, "negative_end": 6, "positive_lexemes": ["hind", "legs"], "negative_lexemes": ["the", "plant"]}, {"tag": "equal", "positive_start": 7, "positive_end": 11, "negative_start": 6, "negative_end": 10, "positive_lexemes": [",", "and", "swats", "at"], "negative_lexemes": [",", "and", "swats", "at"]}, {"tag": "insert", "positive_start": 11, "positive_end": 11, "negative_start": 10, "negative_end": 11, "positive_lexemes": [], "negative_lexemes": ["its"]}, {"tag": "replace", "positive_start": 11, "positive_end": 13, "negative_start": 11, "negative_end": 13, "positive_lexemes": ["the", "plant"], "negative_lexemes": ["hind", "legs"]}]`
- 共同前缀：`["a", "cat", "sits", "on"]`
- 正确 contrast hull：`["its", "hind", "legs", ",", "and", "swats", "at", "the", "plant"]`
- 错误 contrast hull：`["the", "plant", ",", "and", "swats", "at", "its", "hind", "legs"]`
- 共同后缀：`[]`
- Hull token 覆盖率（正/负/最大）：`[0.75, 0.75, 0.75]`
- 共同前缀模型 token：`[100, 3706, 316, 2163, 619]`
- 正确 hull 模型 token：IDs `[1342, 429, 916, 848, 4474, 256, 47, 376, 316, 122, 4585, 1248, 309, 1219, 811]`；text " its hind legs , and swats at the plant"
- 错误 hull 模型 token：IDs `[309, 1219, 811, 256, 47, 376, 316, 122, 4585, 1248, 1342, 429, 916, 848, 4474]`；text " the plant , and swats at its hind legs"
- 第一轮/第二轮分类：`complex_edit` / `multi_block_local_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 25. `swap_object:123`

- 负例类型/范围：`swap_object` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："a small television in front of a bookshelf"
- 原始正描述 2："The bookshelf is positioned behind the small television."
- 原始负描述："A bookshelf in front of a small television."
- 规范化正描述 1："a small television in front of a bookshelf"
- 规范化正描述 2："the bookshelf is positioned behind the small television"
- 规范化负描述："a bookshelf in front of a small television"
- 正描述 1 选择元组：`[6, 14, 4, 0.5, 0.6666666666666666]`
- 正描述 2 选择元组：`[10, 12, 2, 0.625, 0.38181818181818183]`
- 最终比较正描述：`positive_1` / "a small television in front of a bookshelf"
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 1, "negative_start": 0, "negative_end": 1, "positive_lexemes": ["a"], "negative_lexemes": ["a"]}, {"tag": "delete", "positive_start": 1, "positive_end": 2, "negative_start": 1, "negative_end": 1, "positive_lexemes": ["small"], "negative_lexemes": []}, {"tag": "replace", "positive_start": 2, "positive_end": 3, "negative_start": 1, "negative_end": 2, "positive_lexemes": ["television"], "negative_lexemes": ["bookshelf"]}, {"tag": "equal", "positive_start": 3, "positive_end": 7, "negative_start": 2, "negative_end": 6, "positive_lexemes": ["in", "front", "of", "a"], "negative_lexemes": ["in", "front", "of", "a"]}, {"tag": "insert", "positive_start": 7, "positive_end": 7, "negative_start": 6, "negative_end": 7, "positive_lexemes": [], "negative_lexemes": ["small"]}, {"tag": "replace", "positive_start": 7, "positive_end": 8, "negative_start": 7, "negative_end": 8, "positive_lexemes": ["bookshelf"], "negative_lexemes": ["television"]}]`
- 共同前缀：`["a"]`
- 正确 contrast hull：`["small", "television", "in", "front", "of", "a", "bookshelf"]`
- 错误 contrast hull：`["bookshelf", "in", "front", "of", "a", "small", "television"]`
- 共同后缀：`[]`
- Hull token 覆盖率（正/负/最大）：`[0.9333333333333333, 0.9333333333333333, 0.9333333333333333]`
- 共同前缀模型 token：`[100]`
- 正确 hull 模型 token：IDs `[3436, 1047, 361, 121, 5190, 353, 341, 117, 3856, 354, 299, 5826, 4887, 105]`；text " small television in front of a bookshelf"
- 错误 hull 模型 token：IDs `[5826, 4887, 105, 353, 341, 117, 3856, 354, 299, 3436, 1047, 361, 121, 5190]`；text " bookshelf in front of a small television"
- 第一轮/第二轮分类：`complex_edit` / `large_contrast_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；"maximum_hull_token_coverage_above_75_percent"

### 26. `swap_object:155`

- 负例类型/范围：`swap_object` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A person carries his surfboard near incoming waves."
- 原始正描述 2："The surfboard is carried by a person close to incoming waves."
- 原始负描述："His surfboard carries a person near incoming waves."
- 规范化正描述 1："a person carries his surfboard near incoming waves"
- 规范化正描述 2："the surfboard is carried by a person close to incoming waves"
- 规范化负描述："his surfboard carries a person near incoming waves"
- 正描述 1 选择元组：`[8, 10, 2, 0.5, 0.4]`
- 正描述 2 选择元组：`[9, 15, 5, 0.5454545454545454, 0.2833333333333333]`
- 最终比较正描述：`positive_1` / "A person carries his surfboard near incoming waves."
- 完整 lexeme 编辑块：`[{"tag": "replace", "positive_start": 0, "positive_end": 2, "negative_start": 0, "negative_end": 2, "positive_lexemes": ["a", "person"], "negative_lexemes": ["his", "surfboard"]}, {"tag": "equal", "positive_start": 2, "positive_end": 3, "negative_start": 2, "negative_end": 3, "positive_lexemes": ["carries"], "negative_lexemes": ["carries"]}, {"tag": "replace", "positive_start": 3, "positive_end": 5, "negative_start": 3, "negative_end": 5, "positive_lexemes": ["his", "surfboard"], "negative_lexemes": ["a", "person"]}, {"tag": "equal", "positive_start": 5, "positive_end": 8, "negative_start": 5, "negative_end": 8, "positive_lexemes": ["near", "incoming", "waves"], "negative_lexemes": ["near", "incoming", "waves"]}]`
- 共同前缀：`[]`
- 正确 contrast hull：`["a", "person", "carries", "his", "surfboard"]`
- 错误 contrast hull：`["his", "surfboard", "carries", "a", "person"]`
- 共同后缀：`["near", "incoming", "waves"]`
- Hull token 覆盖率（正/负/最大）：`[0.5882352941176471, 0.5882352941176471, 0.5882352941176471]`
- 共同前缀模型 token：`[]`
- 正确 hull 模型 token：IDs `[100, 2198, 3751, 3603, 2049, 3946, 105, 101, 114, 1433]`；text "a person carries his surfboard"
- 错误 hull 模型 token：IDs `[999, 3946, 105, 101, 114, 1433, 3751, 3603, 299, 2198]`；text "his surfboard carries a person"
- 第一轮/第二轮分类：`complex_edit` / `multi_block_local_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 27. `swap_object:163`

- 负例类型/范围：`swap_object` / `{"canonical": true, "pilot": true, "formal": false, "certifying_formal": false}`
- 原始正描述 1："There is a banana on a beach chair with a small umbrella"
- 原始正描述 2："The small umbrella is positioned on a beach chair with a banana."
- 原始负描述："There is a small umbrella on a beach chair with a banana."
- 规范化正描述 1："there is a banana on a beach chair with a small umbrella"
- 规范化正描述 2："the small umbrella is positioned on a beach chair with a banana"
- 规范化负描述："there is a small umbrella on a beach chair with a banana"
- 正描述 1 选择元组：`[6, 18, 4, 0.3333333333333333, 0.42857142857142855]`
- 正描述 2 选择元组：`[10, 10, 1, 0.4166666666666667, 0.3333333333333333]`
- 最终比较正描述：`positive_1` / "There is a banana on a beach chair with a small umbrella"
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 3, "negative_start": 0, "negative_end": 3, "positive_lexemes": ["there", "is", "a"], "negative_lexemes": ["there", "is", "a"]}, {"tag": "insert", "positive_start": 3, "positive_end": 3, "negative_start": 3, "negative_end": 4, "positive_lexemes": [], "negative_lexemes": ["small"]}, {"tag": "replace", "positive_start": 3, "positive_end": 4, "negative_start": 4, "negative_end": 5, "positive_lexemes": ["banana"], "negative_lexemes": ["umbrella"]}, {"tag": "equal", "positive_start": 4, "positive_end": 10, "negative_start": 5, "negative_end": 11, "positive_lexemes": ["on", "a", "beach", "chair", "with", "a"], "negative_lexemes": ["on", "a", "beach", "chair", "with", "a"]}, {"tag": "delete", "positive_start": 10, "positive_end": 11, "negative_start": 11, "negative_end": 11, "positive_lexemes": ["small"], "negative_lexemes": []}, {"tag": "replace", "positive_start": 11, "positive_end": 12, "negative_start": 11, "negative_end": 12, "positive_lexemes": ["umbrella"], "negative_lexemes": ["banana"]}]`
- 共同前缀：`["there", "is", "a"]`
- 正确 contrast hull：`["banana", "on", "a", "beach", "chair", "with", "a", "small", "umbrella"]`
- 错误 contrast hull：`["small", "umbrella", "on", "a", "beach", "chair", "with", "a", "banana"]`
- 共同后缀：`[]`
- Hull token 覆盖率（正/负/最大）：`[0.8095238095238095, 0.8095238095238095, 0.8095238095238095]`
- 共同前缀模型 token：`[119, 2503, 395, 299]`
- 正确 hull 模型 token：IDs `[363, 325, 5491, 619, 299, 600, 1268, 890, 3709, 599, 299, 3436, 256, 714, 306, 1989, 100]`；text " banana on a beach chair with a small umbrella"
- 错误 hull 模型 token：IDs `[3436, 256, 714, 306, 1989, 100, 619, 299, 600, 1268, 890, 3709, 599, 299, 363, 325, 5491]`；text " small umbrella on a beach chair with a banana"
- 第一轮/第二轮分类：`complex_edit` / `large_contrast_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；"maximum_hull_token_coverage_above_75_percent"

### 28. `swap_object:183`

- 负例类型/范围：`swap_object` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A person standing behind a person holding a bat."
- 原始正描述 2："The person is holding the bat while another person is standing behind them."
- 原始负描述："A person holding a bat stands behind a person."
- 规范化正描述 1："a person standing behind a person holding a bat"
- 规范化正描述 2："the person is holding the bat while another person is standing behind them"
- 规范化负描述："a person holding a bat stands behind a person"
- 正描述 1 选择元组：`[12, 14, 2, 0.6666666666666666, 0.5957446808510638]`
- 正描述 2 选择元组：`[16, 22, 5, 0.7692307692307693, 0.581081081081081]`
- 最终比较正描述：`positive_1` / "A person standing behind a person holding a bat."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 2, "negative_start": 0, "negative_end": 2, "positive_lexemes": ["a", "person"], "negative_lexemes": ["a", "person"]}, {"tag": "replace", "positive_start": 2, "positive_end": 7, "negative_start": 2, "negative_end": 7, "positive_lexemes": ["standing", "behind", "a", "person", "holding"], "negative_lexemes": ["holding", "a", "bat", "stands", "behind"]}, {"tag": "equal", "positive_start": 7, "positive_end": 8, "negative_start": 7, "negative_end": 8, "positive_lexemes": ["a"], "negative_lexemes": ["a"]}, {"tag": "replace", "positive_start": 8, "positive_end": 9, "negative_start": 8, "negative_end": 9, "positive_lexemes": ["bat"], "negative_lexemes": ["person"]}]`
- 共同前缀：`["a", "person"]`
- 正确 contrast hull：`["standing", "behind", "a", "person", "holding", "a", "bat"]`
- 错误 contrast hull：`["holding", "a", "bat", "stands", "behind", "a", "person"]`
- 共同后缀：`[]`
- Hull token 覆盖率（正/负/最大）：`[0.8571428571428571, 0.8571428571428571, 0.8571428571428571]`
- 共同前缀模型 token：`[100, 2198]`
- 正确 hull 模型 token：IDs `[2823, 350, 5237, 916, 299, 2198, 429, 2569, 350, 299, 363, 314]`；text " standing behind a person holding a bat"
- 错误 hull 模型 token：IDs `[429, 2569, 350, 299, 363, 314, 2823, 118, 5237, 916, 299, 2198]`；text " holding a bat stands behind a person"
- 第一轮/第二轮分类：`complex_edit` / `large_contrast_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；"maximum_hull_token_coverage_above_75_percent"

### 29. `swap_object:219`

- 负例类型/范围：`swap_object` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："a couple is sitting on a statue of a horse and some plants"
- 原始正描述 2："some plants are close to a couple that is sitting on a statue of a horse."
- 原始负描述："Some plants are sitting on a statue of a horse and a couple."
- 规范化正描述 1："a couple is sitting on a statue of a horse and some plants"
- 规范化正描述 2："some plants are close to a couple that is sitting on a statue of a horse"
- 规范化负描述："some plants are sitting on a statue of a horse and a couple"
- 正描述 1 选择元组：`[10, 26, 2, 0.38461538461538464, 0.3559322033898305]`
- 正描述 2 选择元组：`[9, 23, 2, 0.5625, 0.5138888888888888]`
- 最终比较正描述：`positive_2` / "some plants are close to a couple that is sitting on a statue of a horse."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 3, "negative_start": 0, "negative_end": 3, "positive_lexemes": ["some", "plants", "are"], "negative_lexemes": ["some", "plants", "are"]}, {"tag": "delete", "positive_start": 3, "positive_end": 9, "negative_start": 3, "negative_end": 3, "positive_lexemes": ["close", "to", "a", "couple", "that", "is"], "negative_lexemes": []}, {"tag": "equal", "positive_start": 9, "positive_end": 16, "negative_start": 3, "negative_end": 10, "positive_lexemes": ["sitting", "on", "a", "statue", "of", "a", "horse"], "negative_lexemes": ["sitting", "on", "a", "statue", "of", "a", "horse"]}, {"tag": "insert", "positive_start": 16, "positive_end": 16, "negative_start": 10, "negative_end": 13, "positive_lexemes": [], "negative_lexemes": ["and", "a", "couple"]}]`
- 共同前缀：`["some", "plants", "are"]`
- 正确 contrast hull：`["close", "to", "a", "couple", "that", "is", "sitting", "on", "a", "statue", "of", "a", "horse"]`
- 错误 contrast hull：`["sitting", "on", "a", "statue", "of", "a", "horse", "and", "a", "couple"]`
- 共同后缀：`[]`
- Hull token 覆盖率（正/负/最大）：`[0.8, 0.7619047619047619, 0.8]`
- 共同前缀模型 token：`[118, 3219, 1219, 5483, 732]`
- 正确 hull 模型 token：IDs `[4414, 573, 364, 299, 317, 326, 833, 591, 395, 5305, 2912, 619, 299, 5643, 922, 354, 299, 429, 336, 573]`；text " close to a couple that is sitting on a statue of a horse"
- 错误 hull 模型 token：IDs `[5305, 2912, 619, 299, 5643, 922, 354, 299, 429, 336, 573, 376, 299, 317, 326, 833]`；text " sitting on a statue of a horse and a couple"
- 第一轮/第二轮分类：`complex_edit` / `large_contrast_hull`
- 自动判断："positive_2_selection_tuple_lexicographically_smaller"；"maximum_hull_token_coverage_above_75_percent"

### 30. `swap_object:83`

- 负例类型/范围：`swap_object` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A person of Asian heritage eating a sandwich at a table with two cups of hot beverages."
- 原始正描述 2："A person belonging to Asian heritage is seated at a table with two cups of hot beverages while eating a sandwich."
- 原始负描述："A person of Asian heritage drinking two cups of hot beverages at a table with a sandwich."
- 规范化正描述 1："a person of asian heritage eating a sandwich at a table with two cups of hot beverages"
- 规范化正描述 2："a person belonging to asian heritage is seated at a table with two cups of hot beverages while eating a sandwich"
- 规范化负描述："a person of asian heritage drinking two cups of hot beverages at a table with a sandwich"
- 正描述 1 选择元组：`[16, 24, 4, 0.6470588235294118, 0.5568181818181818]`
- 正描述 2 选择元组：`[16, 30, 6, 0.5714285714285714, 0.41964285714285715]`
- 最终比较正描述：`positive_1` / "A person of Asian heritage eating a sandwich at a table with two cups of hot beverages."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 5, "negative_start": 0, "negative_end": 5, "positive_lexemes": ["a", "person", "of", "asian", "heritage"], "negative_lexemes": ["a", "person", "of", "asian", "heritage"]}, {"tag": "insert", "positive_start": 5, "positive_end": 5, "negative_start": 5, "negative_end": 8, "positive_lexemes": [], "negative_lexemes": ["drinking", "two", "cups"]}, {"tag": "replace", "positive_start": 5, "positive_end": 8, "negative_start": 8, "negative_end": 11, "positive_lexemes": ["eating", "a", "sandwich"], "negative_lexemes": ["of", "hot", "beverages"]}, {"tag": "equal", "positive_start": 8, "positive_end": 12, "negative_start": 11, "negative_end": 15, "positive_lexemes": ["at", "a", "table", "with"], "negative_lexemes": ["at", "a", "table", "with"]}, {"tag": "delete", "positive_start": 12, "positive_end": 15, "negative_start": 15, "negative_end": 15, "positive_lexemes": ["two", "cups", "of"], "negative_lexemes": []}, {"tag": "replace", "positive_start": 15, "positive_end": 17, "negative_start": 15, "negative_end": 17, "positive_lexemes": ["hot", "beverages"], "negative_lexemes": ["a", "sandwich"]}]`
- 共同前缀：`["a", "person", "of", "asian", "heritage"]`
- 正确 contrast hull：`["eating", "a", "sandwich", "at", "a", "table", "with", "two", "cups", "of", "hot", "beverages"]`
- 错误 contrast hull：`["drinking", "two", "cups", "of", "hot", "beverages", "at", "a", "table", "with", "a", "sandwich"]`
- 共同后缀：`[]`
- Hull token 覆盖率（正/负/最大）：`[0.7241379310344828, 0.7333333333333333, 0.7333333333333333]`
- 共同前缀模型 token：`[100, 2198, 354, 523, 2422, 582, 2157, 834]`
- 正确 hull 模型 token：IDs `[413, 1807, 299, 316, 728, 122, 948, 1248, 299, 2630, 599, 2102, 317, 2764, 118, 354, 429, 593, 600, 652, 2455]`；text " eating a sandwich at a table with two cups of hot beverages"
- 错误 hull 模型 token：IDs `[5893, 301, 1237, 2102, 317, 2764, 118, 354, 429, 593, 600, 652, 2455, 1248, 299, 2630, 599, 299, 316, 728, 122, 948]`；text " drinking two cups of hot beverages at a table with a sandwich"
- 第一轮/第二轮分类：`complex_edit` / `multi_block_local_hull`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

## Tokenizer 边界映射失败

候选 `20` 条，本节抽取 `20` 条。

### 1. `replace_attribute:36`

- 负例类型/范围：`replace_attribute` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："Plates of Pizza with silverware next to ketchup and other condiments. "
- 原始正描述 2："The plates of pizza are placed alongside silverware, and the ketchup and other condiments are located nearby."
- 原始负描述："Plates of Vegan Pizza with silverware next to ketchup and other condiments."
- 规范化正描述 1："plates of pizza with silverware next to ketchup and other condiments"
- 规范化正描述 2："the plates of pizza are placed alongside silverware , and the ketchup and other condiments are located nearby"
- 规范化负描述："plates of vegan pizza with silverware next to ketchup and other condiments"
- 正描述 1 选择元组：`[1, 1, 1, 0.08333333333333333, 0.08108108108108109]`
- 正描述 2 选择元组：`[16, 30, 6, 0.6111111111111112, 0.46788990825688076]`
- 最终比较正描述：`positive_1` / "Plates of Pizza with silverware next to ketchup and other condiments. "
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 2, "negative_start": 0, "negative_end": 2, "positive_lexemes": ["plates", "of"], "negative_lexemes": ["plates", "of"]}, {"tag": "insert", "positive_start": 2, "positive_end": 2, "negative_start": 2, "negative_end": 3, "positive_lexemes": [], "negative_lexemes": ["vegan"]}, {"tag": "equal", "positive_start": 2, "positive_end": 11, "negative_start": 3, "negative_end": 12, "positive_lexemes": ["pizza", "with", "silverware", "next", "to", "ketchup", "and", "other", "condiments"], "negative_lexemes": ["pizza", "with", "silverware", "next", "to", "ketchup", "and", "other", "condiments"]}]`
- 共同前缀：`["plates", "of"]`
- 正确 contrast hull：`[]`
- 错误 contrast hull：`["vegan"]`
- 共同后缀：`["pizza", "with", "silverware", "next", "to", "ketchup", "and", "other", "condiments"]`
- Hull token 覆盖率（正/负/最大）：`[0.0, 0.08333333333333333, 0.08333333333333333]`
- 共同前缀模型 token：`[992, 1434, 354]`
- 正确 hull 模型 token：IDs `[]`；text ""
- 错误 hull 模型 token：IDs `[4389, 3249]`；text " vegan"
- 第一轮/第二轮分类：`complex_edit` / `token_mapping_problem`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；"positive_hull_not_mappable_to_token_boundaries;one_or_both_hulls_have_no_scorable_token"

### 2. `replace_attribute:556`

- 负例类型/范围：`replace_attribute` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A catcher is ready to catch the ball after it crosses the plate."
- 原始正描述 2："The ball is positioned above the plate, and a catcher is ready to catch it after it crosses the plate."
- 原始负描述："A catcher is not ready to catch the ball after it crosses the plate."
- 规范化正描述 1："a catcher is ready to catch the ball after it crosses the plate"
- 规范化正描述 2："the ball is positioned above the plate , and a catcher is ready to catch it after it crosses the plate"
- 规范化负描述："a catcher is not ready to catch the ball after it crosses the plate"
- 正描述 1 选择元组：`[1, 1, 1, 0.07142857142857142, 0.05970149253731343]`
- 正描述 2 选择元组：`[13, 25, 4, 0.5714285714285714, 0.5392156862745098]`
- 最终比较正描述：`positive_1` / "A catcher is ready to catch the ball after it crosses the plate."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 3, "negative_start": 0, "negative_end": 3, "positive_lexemes": ["a", "catcher", "is"], "negative_lexemes": ["a", "catcher", "is"]}, {"tag": "insert", "positive_start": 3, "positive_end": 3, "negative_start": 3, "negative_end": 4, "positive_lexemes": [], "negative_lexemes": ["not"]}, {"tag": "equal", "positive_start": 3, "positive_end": 13, "negative_start": 4, "negative_end": 14, "positive_lexemes": ["ready", "to", "catch", "the", "ball", "after", "it", "crosses", "the", "plate"], "negative_lexemes": ["ready", "to", "catch", "the", "ball", "after", "it", "crosses", "the", "plate"]}]`
- 共同前缀：`["a", "catcher", "is"]`
- 正确 contrast hull：`[]`
- 错误 contrast hull：`["not"]`
- 共同后缀：`["ready", "to", "catch", "the", "ball", "after", "it", "crosses", "the", "plate"]`
- Hull token 覆盖率（正/负/最大）：`[0.0, 0.045454545454545456, 0.045454545454545456]`
- 共同前缀模型 token：`[100, 3706, 102, 771, 395]`
- 正确 hull 模型 token：IDs `[]`；text ""
- 错误 hull 模型 token：IDs `[1027]`；text " not"
- 第一轮/第二轮分类：`unique_alignment` / `token_mapping_problem`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；"positive_hull_not_mappable_to_token_boundaries;one_or_both_hulls_have_no_scorable_token"

### 3. `replace_object:716`

- 负例类型/范围：`replace_object` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："two soccer teams going after the soccer ball"
- 原始正描述 2："The soccer ball is being pursued by two soccer teams."
- 原始负描述："The referee watching two soccer teams going after the soccer ball."
- 规范化正描述 1："two soccer teams going after the soccer ball"
- 规范化正描述 2："the soccer ball is being pursued by two soccer teams"
- 规范化负描述："the referee watching two soccer teams going after the soccer ball"
- 正描述 1 选择元组：`[3, 3, 1, 0.2727272727272727, 0.3230769230769231]`
- 正描述 2 选择元组：`[17, 19, 3, 0.8181818181818182, 0.6615384615384615]`
- 最终比较正描述：`positive_1` / "two soccer teams going after the soccer ball"
- 完整 lexeme 编辑块：`[{"tag": "insert", "positive_start": 0, "positive_end": 0, "negative_start": 0, "negative_end": 3, "positive_lexemes": [], "negative_lexemes": ["the", "referee", "watching"]}, {"tag": "equal", "positive_start": 0, "positive_end": 8, "negative_start": 3, "negative_end": 11, "positive_lexemes": ["two", "soccer", "teams", "going", "after", "the", "soccer", "ball"], "negative_lexemes": ["two", "soccer", "teams", "going", "after", "the", "soccer", "ball"]}]`
- 共同前缀：`[]`
- 正确 contrast hull：`[]`
- 错误 contrast hull：`["the", "referee", "watching"]`
- 共同后缀：`["two", "soccer", "teams", "going", "after", "the", "soccer", "ball"]`
- Hull token 覆盖率（正/负/最大）：`[0.17647058823529413, 0.36363636363636365, 0.36363636363636365]`
- 共同前缀模型 token：`[]`
- 正确 hull 模型 token：IDs `[119, 122, 114]`；text "two"
- 错误 hull 模型 token：IDs `[4345, 422, 1617, 104, 339, 6131, 350, 2102]`；text "the referee watching two"
- 第一轮/第二轮分类：`complex_edit` / `token_mapping_problem`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；"positive_hull_not_mappable_to_token_boundaries"

### 4. `replace_relation:1144`

- 负例类型/范围：`replace_relation` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A corner of a restroom with a cookie and coffee."
- 原始正描述 2："Coffee and a cookie are at one of the corner of a restroom."
- 原始负描述："A corner outside of a restroom with a cookie and coffee."
- 规范化正描述 1："a corner of a restroom with a cookie and coffee"
- 规范化正描述 2："coffee and a cookie are at one of the corner of a restroom"
- 规范化负描述："a corner outside of a restroom with a cookie and coffee"
- 正描述 1 选择元组：`[1, 1, 1, 0.09090909090909091, 0.14545454545454545]`
- 正描述 2 选择元组：`[22, 24, 2, 0.9230769230769231, 0.7413793103448276]`
- 最终比较正描述：`positive_1` / "A corner of a restroom with a cookie and coffee."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 2, "negative_start": 0, "negative_end": 2, "positive_lexemes": ["a", "corner"], "negative_lexemes": ["a", "corner"]}, {"tag": "insert", "positive_start": 2, "positive_end": 2, "negative_start": 2, "negative_end": 3, "positive_lexemes": [], "negative_lexemes": ["outside"]}, {"tag": "equal", "positive_start": 2, "positive_end": 10, "negative_start": 3, "negative_end": 11, "positive_lexemes": ["of", "a", "restroom", "with", "a", "cookie", "and", "coffee"], "negative_lexemes": ["of", "a", "restroom", "with", "a", "cookie", "and", "coffee"]}]`
- 共同前缀：`["a", "corner"]`
- 正确 contrast hull：`[]`
- 错误 contrast hull：`["outside"]`
- 共同后缀：`["of", "a", "restroom", "with", "a", "cookie", "and", "coffee"]`
- Hull token 覆盖率（正/负/最大）：`[0.0, 0.15, 0.15]`
- 共同前缀模型 token：`[100, 2376, 4056]`
- 正确 hull 模型 token：IDs `[]`；text ""
- 错误 hull 模型 token：IDs `[1695, 118, 688]`；text " outside"
- 第一轮/第二轮分类：`unique_alignment` / `token_mapping_problem`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；"positive_hull_not_mappable_to_token_boundaries;one_or_both_hulls_have_no_scorable_token"

### 5. `replace_relation:1271`

- 负例类型/范围：`replace_relation` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A black-and white picture of a rack full of doughnuts."
- 原始正描述 2："A picture of a rack of full of doughnuts is black and white."
- 原始负描述："A black-and white picture in front of a rack full of doughnuts."
- 规范化正描述 1："a black-and white picture of a rack full of doughnuts"
- 规范化正描述 2："a picture of a rack of full of doughnuts is black and white"
- 规范化负描述："a black-and white picture in front of a rack full of doughnuts"
- 正描述 1 选择元组：`[2, 2, 1, 0.16666666666666666, 0.14516129032258066]`
- 正描述 2 选择元组：`[9, 23, 4, 0.6923076923076923, 0.7580645161290323]`
- 最终比较正描述：`positive_1` / "A black-and white picture of a rack full of doughnuts."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 4, "negative_start": 0, "negative_end": 4, "positive_lexemes": ["a", "black-and", "white", "picture"], "negative_lexemes": ["a", "black-and", "white", "picture"]}, {"tag": "insert", "positive_start": 4, "positive_end": 4, "negative_start": 4, "negative_end": 6, "positive_lexemes": [], "negative_lexemes": ["in", "front"]}, {"tag": "equal", "positive_start": 4, "positive_end": 10, "negative_start": 6, "negative_end": 12, "positive_lexemes": ["of", "a", "rack", "full", "of", "doughnuts"], "negative_lexemes": ["of", "a", "rack", "full", "of", "doughnuts"]}]`
- 共同前缀：`["a", "black-and", "white", "picture"]`
- 正确 contrast hull：`[]`
- 错误 contrast hull：`["in", "front"]`
- 共同后缀：`["of", "a", "rack", "full", "of", "doughnuts"]`
- Hull token 覆盖率（正/负/最大）：`[0.0, 0.16, 0.16]`
- 共同前缀模型 token：`[100, 2597, 1637, 48, 728, 654, 1078, 344, 2030, 745]`
- 正确 hull 模型 token：IDs `[]`；text ""
- 错误 hull 模型 token：IDs `[353, 341, 117, 3856]`；text " in front"
- 第一轮/第二轮分类：`unique_alignment` / `token_mapping_problem`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；"positive_hull_not_mappable_to_token_boundaries;one_or_both_hulls_have_no_scorable_token"

### 6. `replace_relation:1349`

- 负例类型/范围：`replace_relation` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："a tv in a bathroom mirror next to sinks"
- 原始正描述 2："A bathroom mirror next to sinks has a TV in it."
- 原始负描述："A TV not in a bathroom mirror next to sinks."
- 规范化正描述 1："a tv in a bathroom mirror next to sinks"
- 规范化正描述 2："a bathroom mirror next to sinks has a tv in it"
- 规范化负描述："a tv not in a bathroom mirror next to sinks"
- 正描述 1 选择元组：`[1, 1, 1, 0.1, 0.09302325581395349]`
- 正描述 2 选择元组：`[9, 21, 2, 0.8181818181818182, 0.5869565217391305]`
- 最终比较正描述：`positive_1` / "a tv in a bathroom mirror next to sinks"
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 2, "negative_start": 0, "negative_end": 2, "positive_lexemes": ["a", "tv"], "negative_lexemes": ["a", "tv"]}, {"tag": "insert", "positive_start": 2, "positive_end": 2, "negative_start": 2, "negative_end": 3, "positive_lexemes": [], "negative_lexemes": ["not"]}, {"tag": "equal", "positive_start": 2, "positive_end": 9, "negative_start": 3, "negative_end": 10, "positive_lexemes": ["in", "a", "bathroom", "mirror", "next", "to", "sinks"], "negative_lexemes": ["in", "a", "bathroom", "mirror", "next", "to", "sinks"]}]`
- 共同前缀：`["a", "tv"]`
- 正确 contrast hull：`[]`
- 错误 contrast hull：`["not"]`
- 共同后缀：`["in", "a", "bathroom", "mirror", "next", "to", "sinks"]`
- Hull token 覆盖率（正/负/最大）：`[0.0, 0.05555555555555555, 0.05555555555555555]`
- 共同前缀模型 token：`[100, 297, 121]`
- 正确 hull 模型 token：IDs `[]`；text ""
- 错误 hull 模型 token：IDs `[1027]`；text " not"
- 第一轮/第二轮分类：`complex_edit` / `token_mapping_problem`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；"positive_hull_not_mappable_to_token_boundaries;one_or_both_hulls_have_no_scorable_token"

### 7. `replace_relation:167`

- 负例类型/范围：`replace_relation` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A baseball player in a red shirt is ready to hit the ball."
- 原始正描述 2："A baseball player wearing a red shirt is poised to strike the ball."
- 原始负描述："A baseball player outside in a red shirt is ready to hit the ball."
- 规范化正描述 1："a baseball player in a red shirt is ready to hit the ball"
- 规范化正描述 2："a baseball player wearing a red shirt is poised to strike the ball"
- 规范化负描述："a baseball player outside in a red shirt is ready to hit the ball"
- 正描述 1 选择元组：`[1, 1, 1, 0.07142857142857142, 0.12307692307692308]`
- 正描述 2 选择元组：`[7, 17, 4, 0.2857142857142857, 0.30303030303030304]`
- 最终比较正描述：`positive_1` / "A baseball player in a red shirt is ready to hit the ball."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 3, "negative_start": 0, "negative_end": 3, "positive_lexemes": ["a", "baseball", "player"], "negative_lexemes": ["a", "baseball", "player"]}, {"tag": "insert", "positive_start": 3, "positive_end": 3, "negative_start": 3, "negative_end": 4, "positive_lexemes": [], "negative_lexemes": ["outside"]}, {"tag": "equal", "positive_start": 3, "positive_end": 13, "negative_start": 4, "negative_end": 14, "positive_lexemes": ["in", "a", "red", "shirt", "is", "ready", "to", "hit", "the", "ball"], "negative_lexemes": ["in", "a", "red", "shirt", "is", "ready", "to", "hit", "the", "ball"]}]`
- 共同前缀：`["a", "baseball", "player"]`
- 正确 contrast hull：`[]`
- 错误 contrast hull：`["outside"]`
- 共同后缀：`["in", "a", "red", "shirt", "is", "ready", "to", "hit", "the", "ball"]`
- Hull token 覆盖率（正/负/最大）：`[0.0, 0.13043478260869565, 0.13043478260869565]`
- 共同前缀模型 token：`[100, 4933, 101, 1266, 2865, 311]`
- 正确 hull 模型 token：IDs `[]`；text ""
- 错误 hull 模型 token：IDs `[1695, 118, 688]`；text " outside"
- 第一轮/第二轮分类：`unique_alignment` / `token_mapping_problem`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；"positive_hull_not_mappable_to_token_boundaries;one_or_both_hulls_have_no_scorable_token"

### 8. `replace_relation:252`

- 负例类型/范围：`replace_relation` / `{"canonical": true, "pilot": true, "formal": false, "certifying_formal": false}`
- 原始正描述 1："A little child holding a white Nintendo Wii game controller."
- 原始正描述 2："A white Nintendo Wii game controller is being held by a little kid."
- 原始负描述："A little child is not holding a white Nintendo Wii game controller."
- 规范化正描述 1："a little child holding a white nintendo wii game controller"
- 规范化正描述 2："a white nintendo wii game controller is being held by a little kid"
- 规范化负描述："a little child is not holding a white nintendo wii game controller"
- 正描述 1 选择元组：`[2, 2, 1, 0.16666666666666666, 0.10606060606060606]`
- 正描述 2 选择元组：`[23, 23, 2, 0.9230769230769231, 0.7727272727272727]`
- 最终比较正描述：`positive_1` / "A little child holding a white Nintendo Wii game controller."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 3, "negative_start": 0, "negative_end": 3, "positive_lexemes": ["a", "little", "child"], "negative_lexemes": ["a", "little", "child"]}, {"tag": "insert", "positive_start": 3, "positive_end": 3, "negative_start": 3, "negative_end": 5, "positive_lexemes": [], "negative_lexemes": ["is", "not"]}, {"tag": "equal", "positive_start": 3, "positive_end": 10, "negative_start": 5, "negative_end": 12, "positive_lexemes": ["holding", "a", "white", "nintendo", "wii", "game", "controller"], "negative_lexemes": ["holding", "a", "white", "nintendo", "wii", "game", "controller"]}]`
- 共同前缀：`["a", "little", "child"]`
- 正确 contrast hull：`[]`
- 错误 contrast hull：`["is", "not"]`
- 共同后缀：`["holding", "a", "white", "nintendo", "wii", "game", "controller"]`
- Hull token 覆盖率（正/负/最大）：`[0.0, 0.08, 0.08]`
- 共同前缀模型 token：`[100, 406, 338, 5395, 6109]`
- 正确 hull 模型 token：IDs `[]`；text ""
- 错误 hull 模型 token：IDs `[395, 1027]`；text " is not"
- 第一轮/第二轮分类：`unique_alignment` / `token_mapping_problem`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；"positive_hull_not_mappable_to_token_boundaries;one_or_both_hulls_have_no_scorable_token"

### 9. `replace_relation:271`

- 负例类型/范围：`replace_relation` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A person is staring at something in his hand."
- 原始正描述 2："The object in the person's hand is the focus of his gaze."
- 原始负描述："A person is not staring at something in his hand."
- 规范化正描述 1："a person is staring at something in his hand"
- 规范化正描述 2："the object in the person's hand is the focus of his gaze"
- 规范化负描述："a person is not staring at something in his hand"
- 正描述 1 选择元组：`[1, 1, 1, 0.1, 0.08333333333333333]`
- 正描述 2 选择元组：`[20, 22, 3, 0.9166666666666666, 0.6785714285714286]`
- 最终比较正描述：`positive_1` / "A person is staring at something in his hand."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 3, "negative_start": 0, "negative_end": 3, "positive_lexemes": ["a", "person", "is"], "negative_lexemes": ["a", "person", "is"]}, {"tag": "insert", "positive_start": 3, "positive_end": 3, "negative_start": 3, "negative_end": 4, "positive_lexemes": [], "negative_lexemes": ["not"]}, {"tag": "equal", "positive_start": 3, "positive_end": 9, "negative_start": 4, "negative_end": 10, "positive_lexemes": ["staring", "at", "something", "in", "his", "hand"], "negative_lexemes": ["staring", "at", "something", "in", "his", "hand"]}]`
- 共同前缀：`["a", "person", "is"]`
- 正确 contrast hull：`[]`
- 错误 contrast hull：`["not"]`
- 共同后缀：`["staring", "at", "something", "in", "his", "hand"]`
- Hull token 覆盖率（正/负/最大）：`[0.0, 0.08333333333333333, 0.08333333333333333]`
- 共同前缀模型 token：`[100, 2198, 395]`
- 正确 hull 模型 token：IDs `[]`；text ""
- 错误 hull 模型 token：IDs `[1027]`；text " not"
- 第一轮/第二轮分类：`unique_alignment` / `token_mapping_problem`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；"positive_hull_not_mappable_to_token_boundaries;one_or_both_hulls_have_no_scorable_token"

### 10. `replace_relation:305`

- 负例类型/范围：`replace_relation` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A lower shot of someone riding their skateboard."
- 原始正描述 2："Shot of someone riding their skateboard from a  lower angle."
- 原始负描述："A lower shot of someone not riding their skateboard."
- 规范化正描述 1："a lower shot of someone riding their skateboard"
- 规范化正描述 2："shot of someone riding their skateboard from a lower angle"
- 规范化负描述："a lower shot of someone not riding their skateboard"
- 正描述 1 选择元组：`[1, 1, 1, 0.1111111111111111, 0.0784313725490196]`
- 正描述 2 选择元组：`[7, 19, 3, 0.7, 0.5344827586206896]`
- 最终比较正描述：`positive_1` / "A lower shot of someone riding their skateboard."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 5, "negative_start": 0, "negative_end": 5, "positive_lexemes": ["a", "lower", "shot", "of", "someone"], "negative_lexemes": ["a", "lower", "shot", "of", "someone"]}, {"tag": "insert", "positive_start": 5, "positive_end": 5, "negative_start": 5, "negative_end": 6, "positive_lexemes": [], "negative_lexemes": ["not"]}, {"tag": "equal", "positive_start": 5, "positive_end": 8, "negative_start": 6, "negative_end": 9, "positive_lexemes": ["riding", "their", "skateboard"], "negative_lexemes": ["riding", "their", "skateboard"]}]`
- 共同前缀：`["a", "lower", "shot", "of", "someone"]`
- 正确 contrast hull：`[]`
- 错误 contrast hull：`["not"]`
- 共同后缀：`["riding", "their", "skateboard"]`
- Hull token 覆盖率（正/负/最大）：`[0.0, 0.0625, 0.0625]`
- 共同前缀模型 token：`[100, 5474, 1128, 593, 354, 4779]`
- 正确 hull 模型 token：IDs `[]`；text ""
- 错误 hull 模型 token：IDs `[1027]`；text " not"
- 第一轮/第二轮分类：`unique_alignment` / `token_mapping_problem`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；"positive_hull_not_mappable_to_token_boundaries;one_or_both_hulls_have_no_scorable_token"

### 11. `replace_relation:340`

- 负例类型/范围：`replace_relation` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A person is flying a kite at the beach."
- 原始正描述 2："At the beach, a person is flying a kite."
- 原始负描述："A person is not flying a kite at the beach."
- 规范化正描述 1："a person is flying a kite at the beach"
- 规范化正描述 2："at the beach , a person is flying a kite"
- 规范化负描述："a person is not flying a kite at the beach"
- 正描述 1 选择元组：`[1, 1, 1, 0.1, 0.09523809523809523]`
- 正描述 2 选择元组：`[8, 20, 3, 0.8, 0.7619047619047619]`
- 最终比较正描述：`positive_1` / "A person is flying a kite at the beach."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 3, "negative_start": 0, "negative_end": 3, "positive_lexemes": ["a", "person", "is"], "negative_lexemes": ["a", "person", "is"]}, {"tag": "insert", "positive_start": 3, "positive_end": 3, "negative_start": 3, "negative_end": 4, "positive_lexemes": [], "negative_lexemes": ["not"]}, {"tag": "equal", "positive_start": 3, "positive_end": 9, "negative_start": 4, "negative_end": 10, "positive_lexemes": ["flying", "a", "kite", "at", "the", "beach"], "negative_lexemes": ["flying", "a", "kite", "at", "the", "beach"]}]`
- 共同前缀：`["a", "person", "is"]`
- 正确 contrast hull：`[]`
- 错误 contrast hull：`["not"]`
- 共同后缀：`["flying", "a", "kite", "at", "the", "beach"]`
- Hull token 覆盖率（正/负/最大）：`[0.0, 0.07142857142857142, 0.07142857142857142]`
- 共同前缀模型 token：`[100, 2198, 395]`
- 正确 hull 模型 token：IDs `[]`；text ""
- 错误 hull 模型 token：IDs `[1027]`；text " not"
- 第一轮/第二轮分类：`unique_alignment` / `token_mapping_problem`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；"positive_hull_not_mappable_to_token_boundaries;one_or_both_hulls_have_no_scorable_token"

### 12. `replace_relation:457`

- 负例类型/范围：`replace_relation` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A child wearing yellow is holding a pizza in a box."
- 原始正描述 2："A child in a yellow outfit is holding a pizza in a box."
- 原始负描述："A child not wearing yellow is holding a pizza in a box."
- 规范化正描述 1："a child wearing yellow is holding a pizza in a box"
- 规范化正描述 2："a child in a yellow outfit is holding a pizza in a box"
- 规范化负描述："a child not wearing yellow is holding a pizza in a box"
- 正描述 1 选择元组：`[1, 1, 1, 0.08333333333333333, 0.07407407407407407]`
- 正描述 2 选择元组：`[5, 7, 2, 0.23076923076923078, 0.2777777777777778]`
- 最终比较正描述：`positive_1` / "A child wearing yellow is holding a pizza in a box."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 2, "negative_start": 0, "negative_end": 2, "positive_lexemes": ["a", "child"], "negative_lexemes": ["a", "child"]}, {"tag": "insert", "positive_start": 2, "positive_end": 2, "negative_start": 2, "negative_end": 3, "positive_lexemes": [], "negative_lexemes": ["not"]}, {"tag": "equal", "positive_start": 2, "positive_end": 11, "negative_start": 3, "negative_end": 12, "positive_lexemes": ["wearing", "yellow", "is", "holding", "a", "pizza", "in", "a", "box"], "negative_lexemes": ["wearing", "yellow", "is", "holding", "a", "pizza", "in", "a", "box"]}]`
- 共同前缀：`["a", "child"]`
- 正确 contrast hull：`[]`
- 错误 contrast hull：`["not"]`
- 共同后缀：`["wearing", "yellow", "is", "holding", "a", "pizza", "in", "a", "box"]`
- Hull token 覆盖率（正/负/最大）：`[0.0, 0.045454545454545456, 0.045454545454545456]`
- 共同前缀模型 token：`[100, 6109]`
- 正确 hull 模型 token：IDs `[]`；text ""
- 错误 hull 模型 token：IDs `[1027]`；text " not"
- 第一轮/第二轮分类：`unique_alignment` / `token_mapping_problem`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；"positive_hull_not_mappable_to_token_boundaries;one_or_both_hulls_have_no_scorable_token"

### 13. `replace_relation:46`

- 负例类型/范围：`replace_relation` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A person is in a kitchen making pizzas."
- 原始正描述 2："An individual is making pizzas in a kitchen."
- 原始负描述："A person is in a kitchen cleaning up after making pizzas."
- 规范化正描述 1："a person is in a kitchen making pizzas"
- 规范化正描述 2："an individual is making pizzas in a kitchen"
- 规范化负描述："a person is in a kitchen cleaning up after making pizzas"
- 正描述 1 选择元组：`[3, 3, 1, 0.2727272727272727, 0.32142857142857145]`
- 正描述 2 选择元组：`[11, 19, 3, 0.8181818181818182, 0.7142857142857143]`
- 最终比较正描述：`positive_1` / "A person is in a kitchen making pizzas."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 6, "negative_start": 0, "negative_end": 6, "positive_lexemes": ["a", "person", "is", "in", "a", "kitchen"], "negative_lexemes": ["a", "person", "is", "in", "a", "kitchen"]}, {"tag": "insert", "positive_start": 6, "positive_end": 6, "negative_start": 6, "negative_end": 9, "positive_lexemes": [], "negative_lexemes": ["cleaning", "up", "after"]}, {"tag": "equal", "positive_start": 6, "positive_end": 8, "negative_start": 9, "negative_end": 11, "positive_lexemes": ["making", "pizzas"], "negative_lexemes": ["making", "pizzas"]}]`
- 共同前缀：`["a", "person", "is", "in", "a", "kitchen"]`
- 正确 contrast hull：`[]`
- 错误 contrast hull：`["cleaning", "up", "after"]`
- 共同后缀：`["making", "pizzas"]`
- Hull token 覆盖率（正/负/最大）：`[0.0, 0.2631578947368421, 0.2631578947368421]`
- 共同前缀模型 token：`[100, 2198, 395, 353, 299, 914, 338, 102, 2051]`
- 正确 hull 模型 token：IDs `[]`；text ""
- 错误 hull 模型 token：IDs `[3735, 325, 350, 1253, 3898]`；text " cleaning up after"
- 第一轮/第二轮分类：`unique_alignment` / `token_mapping_problem`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；"positive_hull_not_mappable_to_token_boundaries;one_or_both_hulls_have_no_scorable_token"

### 14. `replace_relation:534`

- 负例类型/范围：`replace_relation` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："Two giraffes stand together near rocks and a building."
- 原始正描述 2："Two giraffes stand near rocks and a building."
- 原始负描述："Two giraffes stand far from each other near rocks and a building."
- 规范化正描述 1："two giraffes stand together near rocks and a building"
- 规范化正描述 2："two giraffes stand near rocks and a building"
- 规范化负描述："two giraffes stand far from each other near rocks and a building"
- 正描述 1 选择元组：`[5, 5, 2, 0.3333333333333333, 0.203125]`
- 正描述 2 选择元组：`[4, 4, 1, 0.3333333333333333, 0.3125]`
- 最终比较正描述：`positive_2` / "Two giraffes stand near rocks and a building."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 3, "negative_start": 0, "negative_end": 3, "positive_lexemes": ["two", "giraffes", "stand"], "negative_lexemes": ["two", "giraffes", "stand"]}, {"tag": "insert", "positive_start": 3, "positive_end": 3, "negative_start": 3, "negative_end": 7, "positive_lexemes": [], "negative_lexemes": ["far", "from", "each", "other"]}, {"tag": "equal", "positive_start": 3, "positive_end": 8, "negative_start": 7, "negative_end": 12, "positive_lexemes": ["near", "rocks", "and", "a", "building"], "negative_lexemes": ["near", "rocks", "and", "a", "building"]}]`
- 共同前缀：`["two", "giraffes", "stand"]`
- 正确 contrast hull：`[]`
- 错误 contrast hull：`["far", "from", "each", "other"]`
- 共同后缀：`["near", "rocks", "and", "a", "building"]`
- Hull token 覆盖率（正/负/最大）：`[0.0, 0.21739130434782608, 0.21739130434782608]`
- 共同前缀模型 token：`[119, 122, 114, 492, 108, 559, 1627, 329, 2823]`
- 正确 hull 模型 token：IDs `[]`；text ""
- 错误 hull 模型 token：IDs `[341, 370, 961, 1766, 1649]`；text " far from each other"
- 第一轮/第二轮分类：`unique_alignment` / `token_mapping_problem`
- 自动判断："positive_2_selection_tuple_lexicographically_smaller"；"positive_hull_not_mappable_to_token_boundaries;one_or_both_hulls_have_no_scorable_token"

### 15. `replace_relation:630`

- 负例类型/范围：`replace_relation` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："Some zebras are on a plain of sands and grass."
- 原始正描述 2："Some zebras are on a vast expanse of sands and grass."
- 原始负描述："Some zebras are running on a plain of sands and grass."
- 规范化正描述 1："some zebras are on a plain of sands and grass"
- 规范化正描述 2："some zebras are on a vast expanse of sands and grass"
- 规范化负描述："some zebras are running on a plain of sands and grass"
- 正描述 1 选择元组：`[1, 1, 1, 0.09090909090909091, 0.1509433962264151]`
- 正描述 2 选择元组：`[4, 8, 3, 0.2727272727272727, 0.2830188679245283]`
- 最终比较正描述：`positive_1` / "Some zebras are on a plain of sands and grass."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 3, "negative_start": 0, "negative_end": 3, "positive_lexemes": ["some", "zebras", "are"], "negative_lexemes": ["some", "zebras", "are"]}, {"tag": "insert", "positive_start": 3, "positive_end": 3, "negative_start": 3, "negative_end": 4, "positive_lexemes": [], "negative_lexemes": ["running"]}, {"tag": "equal", "positive_start": 3, "positive_end": 10, "negative_start": 4, "negative_end": 11, "positive_lexemes": ["on", "a", "plain", "of", "sands", "and", "grass"], "negative_lexemes": ["on", "a", "plain", "of", "sands", "and", "grass"]}]`
- 共同前缀：`["some", "zebras", "are"]`
- 正确 contrast hull：`[]`
- 错误 contrast hull：`["running"]`
- 共同后缀：`["on", "a", "plain", "of", "sands", "and", "grass"]`
- Hull token 覆盖率（正/负/最大）：`[0.0, 0.09523809523809523, 0.09523809523809523]`
- 共同前缀模型 token：`[118, 3219, 3243, 3037, 117, 390, 732]`
- 正确 hull 模型 token：IDs `[]`；text ""
- 错误 hull 模型 token：IDs `[3161, 1795]`；text " running"
- 第一轮/第二轮分类：`unique_alignment` / `token_mapping_problem`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；"positive_hull_not_mappable_to_token_boundaries;one_or_both_hulls_have_no_scorable_token"

### 16. `replace_relation:718`

- 负例类型/范围：`replace_relation` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A barge floating down a river with the skyline in the background."
- 原始正描述 2：" With the skyline in the background, a barge is floating down a river."
- 原始负描述："A barge floating down a river with the skyline beneath it in the background."
- 规范化正描述 1："a barge floating down a river with the skyline in the background"
- 规范化正描述 2："with the skyline in the background , a barge is floating down a river"
- 规范化负描述："a barge floating down a river with the skyline beneath it in the background"
- 正描述 1 选择元组：`[2, 2, 1, 0.14285714285714285, 0.14666666666666667]`
- 正描述 2 选择元组：`[28, 28, 1, 1.0, 0.8133333333333334]`
- 最终比较正描述：`positive_1` / "A barge floating down a river with the skyline in the background."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 9, "negative_start": 0, "negative_end": 9, "positive_lexemes": ["a", "barge", "floating", "down", "a", "river", "with", "the", "skyline"], "negative_lexemes": ["a", "barge", "floating", "down", "a", "river", "with", "the", "skyline"]}, {"tag": "insert", "positive_start": 9, "positive_end": 9, "negative_start": 9, "negative_end": 11, "positive_lexemes": [], "negative_lexemes": ["beneath", "it"]}, {"tag": "equal", "positive_start": 9, "positive_end": 12, "negative_start": 11, "negative_end": 14, "positive_lexemes": ["in", "the", "background"], "negative_lexemes": ["in", "the", "background"]}]`
- 共同前缀：`["a", "barge", "floating", "down", "a", "river", "with", "the", "skyline"]`
- 正确 contrast hull：`[]`
- 错误 contrast hull：`["beneath", "it"]`
- 共同后缀：`["in", "the", "background"]`
- Hull token 覆盖率（正/负/最大）：`[0.0, 0.17391304347826086, 0.17391304347826086]`
- 共同前缀模型 token：`[100, 363, 370, 583, 5796, 1807, 4076, 299, 757, 5258, 599, 309, 3716, 3138]`
- 正确 hull 模型 token：IDs `[]`；text ""
- 错误 hull 模型 token：IDs `[363, 4975, 1831, 563]`；text " beneath it"
- 第一轮/第二轮分类：`unique_alignment` / `token_mapping_problem`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；"positive_hull_not_mappable_to_token_boundaries;one_or_both_hulls_have_no_scorable_token"

### 17. `replace_relation:782`

- 负例类型/范围：`replace_relation` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："this bathroom has pink tiles in the shower and is painted blue"
- 原始正描述 2："The shower in this bathroom has pink tiles, and the bathroom is painted blue."
- 原始负描述："This bathroom has pink tiles nowhere in the shower and is painted blue."
- 规范化正描述 1："this bathroom has pink tiles in the shower and is painted blue"
- 规范化正描述 2："the shower in this bathroom has pink tiles , and the bathroom is painted blue"
- 规范化负描述："this bathroom has pink tiles nowhere in the shower and is painted blue"
- 正描述 1 选择元组：`[1, 1, 1, 0.07692307692307693, 0.11428571428571428]`
- 正描述 2 选择元组：`[10, 22, 4, 0.4666666666666667, 0.4155844155844156]`
- 最终比较正描述：`positive_1` / "this bathroom has pink tiles in the shower and is painted blue"
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 5, "negative_start": 0, "negative_end": 5, "positive_lexemes": ["this", "bathroom", "has", "pink", "tiles"], "negative_lexemes": ["this", "bathroom", "has", "pink", "tiles"]}, {"tag": "insert", "positive_start": 5, "positive_end": 5, "negative_start": 5, "negative_end": 6, "positive_lexemes": [], "negative_lexemes": ["nowhere"]}, {"tag": "equal", "positive_start": 5, "positive_end": 12, "negative_start": 6, "negative_end": 13, "positive_lexemes": ["in", "the", "shower", "and", "is", "painted", "blue"], "negative_lexemes": ["in", "the", "shower", "and", "is", "painted", "blue"]}]`
- 共同前缀：`["this", "bathroom", "has", "pink", "tiles"]`
- 正确 contrast hull：`[]`
- 错误 contrast hull：`["nowhere"]`
- 共同后缀：`["in", "the", "shower", "and", "is", "painted", "blue"]`
- Hull token 覆盖率（正/负/最大）：`[0.0, 0.08695652173913043, 0.08695652173913043]`
- 共同前缀模型 token：`[495, 324, 363, 1831, 393, 444, 1290, 344, 3010, 297, 485, 329]`
- 正确 hull 模型 token：IDs `[]`；text ""
- 错误 hull 模型 token：IDs `[4787, 2503]`；text " nowhere"
- 第一轮/第二轮分类：`complex_edit` / `token_mapping_problem`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；"positive_hull_not_mappable_to_token_boundaries;one_or_both_hulls_have_no_scorable_token"

### 18. `replace_relation:821`

- 负例类型/范围：`replace_relation` / `{"canonical": true, "pilot": true, "formal": false, "certifying_formal": false}`
- 原始正描述 1："The group of zebras are in the field."
- 原始正描述 2："The zebras are in the field."
- 原始负描述："The group of zebras are running in the field."
- 规范化正描述 1："the group of zebras are in the field"
- 规范化正描述 2："the zebras are in the field"
- 规范化负描述："the group of zebras are running in the field"
- 正描述 1 选择元组：`[1, 1, 1, 0.1111111111111111, 0.18181818181818182]`
- 正描述 2 选择元组：`[3, 7, 2, 0.3333333333333333, 0.38636363636363635]`
- 最终比较正描述：`positive_1` / "The group of zebras are in the field."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 5, "negative_start": 0, "negative_end": 5, "positive_lexemes": ["the", "group", "of", "zebras", "are"], "negative_lexemes": ["the", "group", "of", "zebras", "are"]}, {"tag": "insert", "positive_start": 5, "positive_end": 5, "negative_start": 5, "negative_end": 6, "positive_lexemes": [], "negative_lexemes": ["running"]}, {"tag": "equal", "positive_start": 5, "positive_end": 8, "negative_start": 6, "negative_end": 9, "positive_lexemes": ["in", "the", "field"], "negative_lexemes": ["in", "the", "field"]}]`
- 共同前缀：`["the", "group", "of", "zebras", "are"]`
- 正确 contrast hull：`[]`
- 错误 contrast hull：`["running"]`
- 共同后缀：`["in", "the", "field"]`
- Hull token 覆盖率（正/负/最大）：`[0.0, 0.15384615384615385, 0.15384615384615385]`
- 共同前缀模型 token：`[4345, 4592, 354, 3243, 3037, 117, 390, 732]`
- 正确 hull 模型 token：IDs `[]`；text ""
- 错误 hull 模型 token：IDs `[3161, 1795]`；text " running"
- 第一轮/第二轮分类：`unique_alignment` / `token_mapping_problem`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；"positive_hull_not_mappable_to_token_boundaries;one_or_both_hulls_have_no_scorable_token"

### 19. `swap_object:2`

- 负例类型/范围：`swap_object` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A person prepares a pizza while a person watches."
- 原始正描述 2："A person watches as another person is preparing a pizza."
- 原始负描述："A person prepares a pizza while a person watches."
- 规范化正描述 1："a person prepares a pizza while a person watches"
- 规范化正描述 2："a person watches as another person is preparing a pizza"
- 规范化负描述："a person prepares a pizza while a person watches"
- 正描述 1 选择元组：`[0, 0, 0, 0.0, 0.0]`
- 正描述 2 选择元组：`[15, 15, 2, 0.8, 0.6363636363636364]`
- 最终比较正描述：`positive_1` / "A person prepares a pizza while a person watches."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 9, "negative_start": 0, "negative_end": 9, "positive_lexemes": ["a", "person", "prepares", "a", "pizza", "while", "a", "person", "watches"], "negative_lexemes": ["a", "person", "prepares", "a", "pizza", "while", "a", "person", "watches"]}]`
- 共同前缀：`["a", "person", "prepares", "a", "pizza", "while", "a", "person", "watches"]`
- 正确 contrast hull：`[]`
- 错误 contrast hull：`[]`
- 共同后缀：`[]`
- Hull token 覆盖率（正/负/最大）：`[0.0, 0.0, 0.0]`
- 共同前缀模型 token：`[100, 2198, 2165, 115, 5673, 299, 344, 1028, 125, 100, 3052, 299, 2198, 339, 314, 4298]`
- 正确 hull 模型 token：IDs `[]`；text ""
- 错误 hull 模型 token：IDs `[]`；text ""
- 第一轮/第二轮分类：`invalid_sample` / `surface_only_or_degenerate`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；"selected_positive_equals_negative_after_alignment_normalization"

### 20. `swap_object:8`

- 负例类型/范围：`swap_object` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A person holding a game controller with a person looking on."
- 原始正描述 2："A person is looking on while another person holds a game controller."
- 原始负描述："A person holding a game controller with a person looking on."
- 规范化正描述 1："a person holding a game controller with a person looking on"
- 规范化正描述 2："a person is looking on while another person holds a game controller"
- 规范化负描述："a person holding a game controller with a person looking on"
- 正描述 1 选择元组：`[0, 0, 0, 0.0, 0.0]`
- 正描述 2 选择元组：`[19, 19, 2, 0.8333333333333334, 0.6268656716417911]`
- 最终比较正描述：`positive_1` / "A person holding a game controller with a person looking on."
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 11, "negative_start": 0, "negative_end": 11, "positive_lexemes": ["a", "person", "holding", "a", "game", "controller", "with", "a", "person", "looking", "on"], "negative_lexemes": ["a", "person", "holding", "a", "game", "controller", "with", "a", "person", "looking", "on"]}]`
- 共同前缀：`["a", "person", "holding", "a", "game", "controller", "with", "a", "person", "looking", "on"]`
- 正确 contrast hull：`[]`
- 错误 contrast hull：`[]`
- 共同后缀：`[]`
- Hull token 覆盖率（正/负/最大）：`[0.0, 0.0, 0.0]`
- 共同前缀模型 token：`[100, 2198, 429, 2569, 350, 299, 4428, 1684, 393, 1989, 311, 599, 299, 2198, 3125, 619]`
- 正确 hull 模型 token：IDs `[]`；text ""
- 错误 hull 模型 token：IDs `[]`；text ""
- 第一轮/第二轮分类：`invalid_sample` / `surface_only_or_degenerate`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；"selected_positive_equals_negative_after_alignment_normalization"

## 表面差异被成功消除

候选 `595` 条，本节抽取 `30` 条。

### 1. `replace_attribute:242`

- 负例类型/范围：`replace_attribute` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："This boat has docked next to a wooden pier"
- 原始正描述 2："The wooden pier is adjacent to the docked boat."
- 原始负描述："This boat has docked next to a concrete pier."
- 规范化正描述 1："this boat has docked next to a wooden pier"
- 规范化正描述 2："the wooden pier is adjacent to the docked boat"
- 规范化负描述："this boat has docked next to a concrete pier"
- 正描述 1 选择元组：`[2, 2, 1, 0.1111111111111111, 0.13636363636363635]`
- 正描述 2 选择元组：`[16, 18, 2, 0.8888888888888888, 0.6956521739130435]`
- 最终比较正描述：`positive_1` / "This boat has docked next to a wooden pier"
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 7, "negative_start": 0, "negative_end": 7, "positive_lexemes": ["this", "boat", "has", "docked", "next", "to", "a"], "negative_lexemes": ["this", "boat", "has", "docked", "next", "to", "a"]}, {"tag": "replace", "positive_start": 7, "positive_end": 8, "negative_start": 7, "negative_end": 8, "positive_lexemes": ["wooden"], "negative_lexemes": ["concrete"]}, {"tag": "equal", "positive_start": 8, "positive_end": 9, "negative_start": 8, "negative_end": 9, "positive_lexemes": ["pier"], "negative_lexemes": ["pier"]}]`
- 共同前缀：`["this", "boat", "has", "docked", "next", "to", "a"]`
- 正确 contrast hull：`["wooden"]`
- 错误 contrast hull：`["concrete"]`
- 共同后缀：`["pier"]`
- Hull token 覆盖率（正/负/最大）：`[0.1875, 0.1875, 0.1875]`
- 共同前缀模型 token：`[495, 324, 1847, 314, 1290, 1041, 892, 382, 4658, 364, 299]`
- 正确 hull 模型 token：IDs `[339, 2166, 327]`；text " wooden"
- 错误 hull 模型 token：IDs `[614, 2395, 741]`；text " concrete"
- 第一轮/第二轮分类：`complex_edit` / `one_block_local`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 2. `replace_attribute:317`

- 负例类型/范围：`replace_attribute` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A dog is sitting on a neatly made bed while someone looks on. "
- 原始正描述 2："The person is observing a dog sitting on a clean made bed."
- 原始负描述："A dog is sitting on a messily made bed while someone looks on."
- 规范化正描述 1："a dog is sitting on a neatly made bed while someone looks on"
- 规范化正描述 2："the person is observing a dog sitting on a clean made bed"
- 规范化负描述："a dog is sitting on a messily made bed while someone looks on"
- 正描述 1 选择元组：`[2, 2, 1, 0.07692307692307693, 0.06557377049180328]`
- 正描述 2 选择元组：`[13, 25, 4, 0.7692307692307693, 0.7704918032786885]`
- 最终比较正描述：`positive_1` / "A dog is sitting on a neatly made bed while someone looks on. "
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 6, "negative_start": 0, "negative_end": 6, "positive_lexemes": ["a", "dog", "is", "sitting", "on", "a"], "negative_lexemes": ["a", "dog", "is", "sitting", "on", "a"]}, {"tag": "replace", "positive_start": 6, "positive_end": 7, "negative_start": 6, "negative_end": 7, "positive_lexemes": ["neatly"], "negative_lexemes": ["messily"]}, {"tag": "equal", "positive_start": 7, "positive_end": 13, "negative_start": 7, "negative_end": 13, "positive_lexemes": ["made", "bed", "while", "someone", "looks", "on"], "negative_lexemes": ["made", "bed", "while", "someone", "looks", "on"]}]`
- 共同前缀：`["a", "dog", "is", "sitting", "on", "a"]`
- 正确 contrast hull：`["neatly"]`
- 错误 contrast hull：`["messily"]`
- 共同后缀：`["made", "bed", "while", "someone", "looks", "on"]`
- Hull token 覆盖率（正/负/最大）：`[0.15789473684210525, 0.1111111111111111, 0.15789473684210525]`
- 共同前缀模型 token：`[100, 1041, 106, 395, 5305, 2912, 619, 299]`
- 正确 hull 模型 token：IDs `[730, 314, 542]`；text " neatly"
- 错误 hull 模型 token：IDs `[3202, 2738]`；text " messily"
- 第一轮/第二轮分类：`unique_alignment` / `one_block_local`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 3. `replace_attribute:435`

- 负例类型/范围：`replace_attribute` / `{"canonical": true, "pilot": true, "formal": false, "certifying_formal": false}`
- 原始正描述 1："Two long boats are sailing near a large bridge. "
- 原始正描述 2："A couple of short boats are sailing close to a large bridge."
- 原始负描述："Two short boats are sailing near a large bridge."
- 规范化正描述 1："two long boats are sailing near a large bridge"
- 规范化正描述 2："a couple of short boats are sailing close to a large bridge"
- 规范化负描述："two short boats are sailing near a large bridge"
- 正描述 1 选择元组：`[2, 2, 1, 0.1111111111111111, 0.0851063829787234]`
- 正描述 2 选择元组：`[7, 15, 4, 0.4166666666666667, 0.288135593220339]`
- 最终比较正描述：`positive_1` / "Two long boats are sailing near a large bridge. "
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 1, "negative_start": 0, "negative_end": 1, "positive_lexemes": ["two"], "negative_lexemes": ["two"]}, {"tag": "replace", "positive_start": 1, "positive_end": 2, "negative_start": 1, "negative_end": 2, "positive_lexemes": ["long"], "negative_lexemes": ["short"]}, {"tag": "equal", "positive_start": 2, "positive_end": 9, "negative_start": 2, "negative_end": 9, "positive_lexemes": ["boats", "are", "sailing", "near", "a", "large", "bridge"], "negative_lexemes": ["boats", "are", "sailing", "near", "a", "large", "bridge"]}]`
- 共同前缀：`["two"]`
- 正确 contrast hull：`["long"]`
- 错误 contrast hull：`["short"]`
- 共同后缀：`["boats", "are", "sailing", "near", "a", "large", "bridge"]`
- Hull token 覆盖率（正/负/最大）：`[0.058823529411764705, 0.058823529411764705, 0.058823529411764705]`
- 共同前缀模型 token：`[119, 122, 114]`
- 正确 hull 模型 token：IDs `[2954]`；text " long"
- 错误 hull 模型 token：IDs `[3306]`；text " short"
- 第一轮/第二轮分类：`complex_edit` / `one_block_local`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 4. `replace_attribute:437`

- 负例类型/范围：`replace_attribute` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A chocolate frosted donut on a plate with a cup of coffee and a penguin napkin holder. "
- 原始正描述 2："The donut frosted with chocolate is on the plate with a penguin napkin holder and a cup of coffee."
- 原始负描述："A vanilla frosted donut on a plate with a cup of coffee and a penguin napkin holder."
- 规范化正描述 1："a chocolate frosted donut on a plate with a cup of coffee and a penguin napkin holder"
- 规范化正描述 2："the donut frosted with chocolate is on the plate with a penguin napkin holder and a cup of coffee"
- 规范化负描述："a vanilla frosted donut on a plate with a cup of coffee and a penguin napkin holder"
- 正描述 1 选择元组：`[2, 2, 1, 0.058823529411764705, 0.08235294117647059]`
- 正描述 2 选择元组：`[22, 36, 6, 0.631578947368421, 0.6082474226804123]`
- 最终比较正描述：`positive_1` / "A chocolate frosted donut on a plate with a cup of coffee and a penguin napkin holder. "
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 1, "negative_start": 0, "negative_end": 1, "positive_lexemes": ["a"], "negative_lexemes": ["a"]}, {"tag": "replace", "positive_start": 1, "positive_end": 2, "negative_start": 1, "negative_end": 2, "positive_lexemes": ["chocolate"], "negative_lexemes": ["vanilla"]}, {"tag": "equal", "positive_start": 2, "positive_end": 17, "negative_start": 2, "negative_end": 17, "positive_lexemes": ["frosted", "donut", "on", "a", "plate", "with", "a", "cup", "of", "coffee", "and", "a", "penguin", "napkin", "holder"], "negative_lexemes": ["frosted", "donut", "on", "a", "plate", "with", "a", "cup", "of", "coffee", "and", "a", "penguin", "napkin", "holder"]}]`
- 共同前缀：`["a"]`
- 正确 contrast hull：`["chocolate"]`
- 错误 contrast hull：`["vanilla"]`
- 共同后缀：`["frosted", "donut", "on", "a", "plate", "with", "a", "cup", "of", "coffee", "and", "a", "penguin", "napkin", "holder"]`
- Hull token 覆盖率（正/负/最大）：`[0.1111111111111111, 0.1111111111111111, 0.1111111111111111]`
- 共同前缀模型 token：`[100]`
- 正确 hull 模型 token：IDs `[890, 1427, 500, 557]`；text " chocolate"
- 错误 hull 模型 token：IDs `[603, 325, 959, 100]`；text " vanilla"
- 第一轮/第二轮分类：`complex_edit` / `one_block_local`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 5. `replace_attribute:499`

- 负例类型/范围：`replace_attribute` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1：" a living room with a big table next to a book shelf "
- 原始正描述 2："The book shelf is adjacent to the large table in the living room."
- 原始负描述："A living room with a small table next to a book shelf."
- 规范化正描述 1："a living room with a big table next to a book shelf"
- 规范化正描述 2："the book shelf is adjacent to the large table in the living room"
- 规范化负描述："a living room with a small table next to a book shelf"
- 正描述 1 选择元组：`[2, 2, 1, 0.08333333333333333, 0.09433962264150944]`
- 正描述 2 选择元组：`[25, 25, 2, 1.0, 0.78125]`
- 最终比较正描述：`positive_1` / " a living room with a big table next to a book shelf "
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 5, "negative_start": 0, "negative_end": 5, "positive_lexemes": ["a", "living", "room", "with", "a"], "negative_lexemes": ["a", "living", "room", "with", "a"]}, {"tag": "replace", "positive_start": 5, "positive_end": 6, "negative_start": 5, "negative_end": 6, "positive_lexemes": ["big"], "negative_lexemes": ["small"]}, {"tag": "equal", "positive_start": 6, "positive_end": 12, "negative_start": 6, "negative_end": 12, "positive_lexemes": ["table", "next", "to", "a", "book", "shelf"], "negative_lexemes": ["table", "next", "to", "a", "book", "shelf"]}]`
- 共同前缀：`["a", "living", "room", "with", "a"]`
- 正确 contrast hull：`["big"]`
- 错误 contrast hull：`["small"]`
- 共同后缀：`["table", "next", "to", "a", "book", "shelf"]`
- Hull token 覆盖率（正/负/最大）：`[0.11764705882352941, 0.0625, 0.11764705882352941]`
- 共同前缀模型 token：`[100, 406, 4917, 1552, 444, 599, 299]`
- 正确 hull 模型 token：IDs `[363, 499]`；text " big"
- 错误 hull 模型 token：IDs `[3436]`；text " small"
- 第一轮/第二轮分类：`complex_edit` / `one_block_local`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 6. `replace_attribute:525`

- 负例类型/范围：`replace_attribute` / `{"canonical": true, "pilot": true, "formal": false, "certifying_formal": false}`
- 原始正描述 1："A large black truck in a parking lot"
- 原始正描述 2："A large truck that is black is parked in a lot."
- 原始负描述："A small black truck in a parking lot."
- 规范化正描述 1："a large black truck in a parking lot"
- 规范化正描述 2："a large truck that is black is parked in a lot"
- 规范化负描述："a small black truck in a parking lot"
- 正描述 1 选择元组：`[2, 2, 1, 0.125, 0.1388888888888889]`
- 正描述 2 选择元组：`[9, 15, 5, 0.6363636363636364, 0.5434782608695652]`
- 最终比较正描述：`positive_1` / "A large black truck in a parking lot"
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 1, "negative_start": 0, "negative_end": 1, "positive_lexemes": ["a"], "negative_lexemes": ["a"]}, {"tag": "replace", "positive_start": 1, "positive_end": 2, "negative_start": 1, "negative_end": 2, "positive_lexemes": ["large"], "negative_lexemes": ["small"]}, {"tag": "equal", "positive_start": 2, "positive_end": 8, "negative_start": 2, "negative_end": 8, "positive_lexemes": ["black", "truck", "in", "a", "parking", "lot"], "negative_lexemes": ["black", "truck", "in", "a", "parking", "lot"]}]`
- 共同前缀：`["a"]`
- 正确 contrast hull：`["large"]`
- 错误 contrast hull：`["small"]`
- 共同后缀：`["black", "truck", "in", "a", "parking", "lot"]`
- Hull token 覆盖率（正/负/最大）：`[0.07692307692307693, 0.07692307692307693, 0.07692307692307693]`
- 共同前缀模型 token：`[100]`
- 正确 hull 模型 token：IDs `[2994]`；text " large"
- 错误 hull 模型 token：IDs `[3436]`；text " small"
- 第一轮/第二轮分类：`complex_edit` / `one_block_local`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 7. `replace_attribute:535`

- 负例类型/范围：`replace_attribute` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A grassy hill side with some animals in the distance "
- 原始正描述 2："some animals in the distance on a hillside filled with grass."
- 原始负描述："A rocky hill side with some animals in the distance."
- 规范化正描述 1："a grassy hill side with some animals in the distance"
- 规范化正描述 2："some animals in the distance on a hillside filled with grass"
- 规范化负描述："a rocky hill side with some animals in the distance"
- 正描述 1 选择元组：`[2, 2, 1, 0.1, 0.07692307692307693]`
- 正描述 2 选择元组：`[21, 21, 2, 1.0, 0.7666666666666667]`
- 最终比较正描述：`positive_1` / "A grassy hill side with some animals in the distance "
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 1, "negative_start": 0, "negative_end": 1, "positive_lexemes": ["a"], "negative_lexemes": ["a"]}, {"tag": "replace", "positive_start": 1, "positive_end": 2, "negative_start": 1, "negative_end": 2, "positive_lexemes": ["grassy"], "negative_lexemes": ["rocky"]}, {"tag": "equal", "positive_start": 2, "positive_end": 10, "negative_start": 2, "negative_end": 10, "positive_lexemes": ["hill", "side", "with", "some", "animals", "in", "the", "distance"], "negative_lexemes": ["hill", "side", "with", "some", "animals", "in", "the", "distance"]}]`
- 共同前缀：`["a"]`
- 正确 contrast hull：`["grassy"]`
- 错误 contrast hull：`["rocky"]`
- 共同后缀：`["hill", "side", "with", "some", "animals", "in", "the", "distance"]`
- Hull token 覆盖率（正/负/最大）：`[0.25, 0.2, 0.25]`
- 共同前缀模型 token：`[100]`
- 正确 hull 模型 token：IDs `[492, 117, 1388, 124]`；text " grassy"
- 错误 hull 模型 token：IDs `[1552, 892, 124]`；text " rocky"
- 第一轮/第二轮分类：`complex_edit` / `one_block_local`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 8. `replace_attribute:584`

- 负例类型/范围：`replace_attribute` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A GREEN TABLE WITH A OLD RUSTY BLENDER AND A PRINTER "
- 原始正描述 2："The printer and a old rusty blender are positioned on a green table."
- 原始负描述："A GREEN TABLE WITH A OLD SHINY BLENDER AND A PRINTER."
- 规范化正描述 1："a green table with a old rusty blender and a printer"
- 规范化正描述 2："the printer and a old rusty blender are positioned on a green table"
- 规范化负描述："a green table with a old shiny blender and a printer"
- 正描述 1 选择元组：`[2, 2, 1, 0.09090909090909091, 0.07692307692307693]`
- 正描述 2 选择元组：`[16, 24, 7, 0.7692307692307693, 0.6119402985074627]`
- 最终比较正描述：`positive_1` / "A GREEN TABLE WITH A OLD RUSTY BLENDER AND A PRINTER "
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 6, "negative_start": 0, "negative_end": 6, "positive_lexemes": ["a", "green", "table", "with", "a", "old"], "negative_lexemes": ["a", "green", "table", "with", "a", "old"]}, {"tag": "replace", "positive_start": 6, "positive_end": 7, "negative_start": 6, "negative_end": 7, "positive_lexemes": ["rusty"], "negative_lexemes": ["shiny"]}, {"tag": "equal", "positive_start": 7, "positive_end": 11, "negative_start": 7, "negative_end": 11, "positive_lexemes": ["blender", "and", "a", "printer"], "negative_lexemes": ["blender", "and", "a", "printer"]}]`
- 共同前缀：`["a", "green", "table", "with", "a", "old"]`
- 正确 contrast hull：`["rusty"]`
- 错误 contrast hull：`["shiny"]`
- 共同后缀：`["blender", "and", "a", "printer"]`
- Hull token 覆盖率（正/负/最大）：`[0.2, 0.2, 0.2]`
- 共同前缀模型 token：`[100, 5921, 2630, 599, 299, 4797]`
- 正确 hull 模型 token：IDs `[757, 1076, 124]`；text " rusty"
- 错误 hull 模型 token：IDs `[1128, 301, 124]`；text " shiny"
- 第一轮/第二轮分类：`complex_edit` / `one_block_local`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 9. `replace_attribute:663`

- 负例类型/范围：`replace_attribute` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："a coin meter that has paint all over it"
- 原始正描述 2："The paint is all over the coin meter."
- 原始负描述："A coin meter that is clean all over it."
- 规范化正描述 1："a coin meter that has paint all over it"
- 规范化正描述 2："the paint is all over the coin meter"
- 规范化负描述："a coin meter that is clean all over it"
- 正描述 1 选择元组：`[4, 4, 1, 0.2222222222222222, 0.1794871794871795]`
- 正描述 2 选择元组：`[11, 17, 5, 0.8888888888888888, 0.8157894736842105]`
- 最终比较正描述：`positive_1` / "a coin meter that has paint all over it"
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 4, "negative_start": 0, "negative_end": 4, "positive_lexemes": ["a", "coin", "meter", "that"], "negative_lexemes": ["a", "coin", "meter", "that"]}, {"tag": "replace", "positive_start": 4, "positive_end": 6, "negative_start": 4, "negative_end": 6, "positive_lexemes": ["has", "paint"], "negative_lexemes": ["is", "clean"]}, {"tag": "equal", "positive_start": 6, "positive_end": 9, "negative_start": 6, "negative_end": 9, "positive_lexemes": ["all", "over", "it"], "negative_lexemes": ["all", "over", "it"]}]`
- 共同前缀：`["a", "coin", "meter", "that"]`
- 正确 contrast hull：`["has", "paint"]`
- 错误 contrast hull：`["is", "clean"]`
- 共同后缀：`["all", "over", "it"]`
- Hull token 覆盖率（正/负/最大）：`[0.25, 0.25, 0.25]`
- 共同前缀模型 token：`[100, 966, 301, 4743, 311, 591]`
- 正确 hull 模型 token：IDs `[1290, 5063, 119]`；text " has paint"
- 错误 hull 模型 token：IDs `[395, 3735, 325]`；text " is clean"
- 第一轮/第二轮分类：`complex_edit` / `one_block_local`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 10. `replace_attribute:679`

- 负例类型/范围：`replace_attribute` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："two teddy bears that are large sitting in a small garden"
- 原始正描述 2："In a small garden, there are two large teddy bears sitting."
- 原始负描述："Two teddy bears that are tiny sitting in a small garden."
- 规范化正描述 1："two teddy bears that are large sitting in a small garden"
- 规范化正描述 2："in a small garden , there are two large teddy bears sitting"
- 规范化负描述："two teddy bears that are tiny sitting in a small garden"
- 正描述 1 选择元组：`[2, 2, 1, 0.09090909090909091, 0.08928571428571429]`
- 正描述 2 选择元组：`[23, 23, 2, 1.0, 0.7457627118644068]`
- 最终比较正描述：`positive_1` / "two teddy bears that are large sitting in a small garden"
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 5, "negative_start": 0, "negative_end": 5, "positive_lexemes": ["two", "teddy", "bears", "that", "are"], "negative_lexemes": ["two", "teddy", "bears", "that", "are"]}, {"tag": "replace", "positive_start": 5, "positive_end": 6, "negative_start": 5, "negative_end": 6, "positive_lexemes": ["large"], "negative_lexemes": ["tiny"]}, {"tag": "equal", "positive_start": 6, "positive_end": 11, "negative_start": 6, "negative_end": 11, "positive_lexemes": ["sitting", "in", "a", "small", "garden"], "negative_lexemes": ["sitting", "in", "a", "small", "garden"]}]`
- 共同前缀：`["two", "teddy", "bears", "that", "are"]`
- 正确 contrast hull：`["large"]`
- 错误 contrast hull：`["tiny"]`
- 共同后缀：`["sitting", "in", "a", "small", "garden"]`
- Hull token 覆盖率（正/负/最大）：`[0.05, 0.13636363636363635, 0.13636363636363635]`
- 共同前缀模型 token：`[119, 122, 114, 297, 382, 103, 124, 600, 2546, 591, 732]`
- 正确 hull 模型 token：IDs `[2994]`；text " large"
- 错误 hull 模型 token：IDs `[297, 301, 124]`；text " tiny"
- 第一轮/第二轮分类：`complex_edit` / `one_block_local`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 11. `replace_object:1106`

- 负例类型/范围：`replace_object` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："There is a very large pizza with different toppings on it"
- 原始正描述 2："The pizza which is huge has various toppings spread out on it."
- 原始负描述："There is a very large burger with different toppings on it."
- 规范化正描述 1："there is a very large pizza with different toppings on it"
- 规范化正描述 2："the pizza which is huge has various toppings spread out on it"
- 规范化负描述："there is a very large burger with different toppings on it"
- 正描述 1 选择元组：`[2, 2, 1, 0.09090909090909091, 0.10344827586206896]`
- 正描述 2 选择元组：`[19, 19, 2, 0.8333333333333334, 0.6885245901639344]`
- 最终比较正描述：`positive_1` / "There is a very large pizza with different toppings on it"
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 5, "negative_start": 0, "negative_end": 5, "positive_lexemes": ["there", "is", "a", "very", "large"], "negative_lexemes": ["there", "is", "a", "very", "large"]}, {"tag": "replace", "positive_start": 5, "positive_end": 6, "negative_start": 5, "negative_end": 6, "positive_lexemes": ["pizza"], "negative_lexemes": ["burger"]}, {"tag": "equal", "positive_start": 6, "positive_end": 11, "negative_start": 6, "negative_end": 11, "positive_lexemes": ["with", "different", "toppings", "on", "it"], "negative_lexemes": ["with", "different", "toppings", "on", "it"]}]`
- 共同前缀：`["there", "is", "a", "very", "large"]`
- 正确 contrast hull：`["pizza"]`
- 错误 contrast hull：`["burger"]`
- 共同后缀：`["with", "different", "toppings", "on", "it"]`
- Hull token 覆盖率（正/负/最大）：`[0.23529411764705882, 0.1875, 0.23529411764705882]`
- 共同前缀模型 token：`[119, 2503, 395, 299, 4965, 2994]`
- 正确 hull 模型 token：IDs `[344, 1028, 125, 100]`；text " pizza"
- 错误 hull 模型 token：IDs `[363, 543, 4105]`；text " burger"
- 第一轮/第二轮分类：`complex_edit` / `one_block_local`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 12. `replace_object:1125`

- 负例类型/范围：`replace_object` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A man is on the court holding his racket. "
- 原始正描述 2："The man is holding his racket on the court."
- 原始负描述："A man is on the court holding his ball."
- 规范化正描述 1："a man is on the court holding his racket"
- 规范化正描述 2："the man is holding his racket on the court"
- 规范化负描述："a man is on the court holding his ball"
- 正描述 1 选择元组：`[2, 2, 1, 0.1111111111111111, 0.125]`
- 正描述 2 选择元组：`[14, 18, 2, 0.7777777777777778, 0.6904761904761905]`
- 最终比较正描述：`positive_1` / "A man is on the court holding his racket. "
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 8, "negative_start": 0, "negative_end": 8, "positive_lexemes": ["a", "man", "is", "on", "the", "court", "holding", "his"], "negative_lexemes": ["a", "man", "is", "on", "the", "court", "holding", "his"]}, {"tag": "replace", "positive_start": 8, "positive_end": 9, "negative_start": 8, "negative_end": 9, "positive_lexemes": ["racket"], "negative_lexemes": ["ball"]}]`
- 共同前缀：`["a", "man", "is", "on", "the", "court", "holding", "his"]`
- 正确 contrast hull：`["racket"]`
- 错误 contrast hull：`["ball"]`
- 共同后缀：`[]`
- Hull token 覆盖率（正/负/最大）：`[0.21428571428571427, 0.15384615384615385, 0.21428571428571427]`
- 共同前缀模型 token：`[100, 1672, 395, 619, 309, 3759, 119, 429, 2569, 350, 2049]`
- 正确 hull 模型 token：IDs `[2265, 892, 439]`；text " racket"
- 错误 hull 模型 token：IDs `[363, 1266]`；text " ball"
- 第一轮/第二轮分类：`unique_alignment` / `one_block_local`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 13. `replace_object:1156`

- 负例类型/范围：`replace_object` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："All of the cows are poking their heads out, eating some hay. "
- 原始正描述 2："The cows are positioned in such a way that their heads are poking out while they are eating some hay."
- 原始负描述："All of the goats are poking their heads out, eating some hay."
- 规范化正描述 1："all of the cows are poking their heads out , eating some hay"
- 规范化正描述 2："the cows are positioned in such a way that their heads are poking out while they are eating some hay"
- 规范化负描述："all of the goats are poking their heads out , eating some hay"
- 正描述 1 选择元组：`[2, 2, 1, 0.07692307692307693, 0.04918032786885246]`
- 正描述 2 选择元组：`[21, 27, 5, 0.7, 0.57]`
- 最终比较正描述：`positive_1` / "All of the cows are poking their heads out, eating some hay. "
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 3, "negative_start": 0, "negative_end": 3, "positive_lexemes": ["all", "of", "the"], "negative_lexemes": ["all", "of", "the"]}, {"tag": "replace", "positive_start": 3, "positive_end": 4, "negative_start": 3, "negative_end": 4, "positive_lexemes": ["cows"], "negative_lexemes": ["goats"]}, {"tag": "equal", "positive_start": 4, "positive_end": 13, "negative_start": 4, "negative_end": 13, "positive_lexemes": ["are", "poking", "their", "heads", "out", ",", "eating", "some", "hay"], "negative_lexemes": ["are", "poking", "their", "heads", "out", ",", "eating", "some", "hay"]}]`
- 共同前缀：`["all", "of", "the"]`
- 正确 contrast hull：`["cows"]`
- 错误 contrast hull：`["goats"]`
- 共同后缀：`["are", "poking", "their", "heads", "out", ",", "eating", "some", "hay"]`
- Hull token 覆盖率（正/负/最大）：`[0.10526315789473684, 0.10526315789473684, 0.10526315789473684]`
- 共同前缀模型 token：`[1266, 354, 309]`
- 正确 hull 模型 token：IDs `[317, 3032]`；text " cows"
- 错误 hull 模型 token：IDs `[2379, 4585]`；text " goats"
- 第一轮/第二轮分类：`complex_edit` / `one_block_local`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 14. `replace_object:1194`

- 负例类型/范围：`replace_object` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："a room full of colorful furniture and a tv"
- 原始正描述 2："The room is adorned with a TV and vibrant furniture."
- 原始负描述："A room full of colorful furniture and a bookshelf."
- 规范化正描述 1："a room full of colorful furniture and a tv"
- 规范化正描述 2："the room is adorned with a tv and vibrant furniture"
- 规范化负描述："a room full of colorful furniture and a bookshelf"
- 正描述 1 选择元组：`[2, 2, 1, 0.1111111111111111, 0.1836734693877551]`
- 正描述 2 选择元组：`[15, 19, 4, 0.8, 0.7843137254901961]`
- 最终比较正描述：`positive_1` / "a room full of colorful furniture and a tv"
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 8, "negative_start": 0, "negative_end": 8, "positive_lexemes": ["a", "room", "full", "of", "colorful", "furniture", "and", "a"], "negative_lexemes": ["a", "room", "full", "of", "colorful", "furniture", "and", "a"]}, {"tag": "replace", "positive_start": 8, "positive_end": 9, "negative_start": 8, "negative_end": 9, "positive_lexemes": ["tv"], "negative_lexemes": ["bookshelf"]}]`
- 共同前缀：`["a", "room", "full", "of", "colorful", "furniture", "and", "a"]`
- 正确 contrast hull：`["tv"]`
- 错误 contrast hull：`["bookshelf"]`
- 共同后缀：`[]`
- Hull token 覆盖率（正/负/最大）：`[0.13333333333333333, 0.1875, 0.1875]`
- 共同前缀模型 token：`[100, 1552, 444, 5840, 354, 4987, 1930, 341, 1262, 338, 745, 376, 299]`
- 正确 hull 模型 token：IDs `[297, 121]`；text " tv"
- 错误 hull 模型 token：IDs `[5826, 4887, 105]`；text " bookshelf"
- 第一轮/第二轮分类：`complex_edit` / `one_block_local`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 15. `replace_object:1245`

- 负例类型/范围：`replace_object` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："Plates of Pizza with silverware next to ketchup and other condiments. "
- 原始正描述 2："Plates of pizza along with the silverware, and the ketchup and other condiments are located nearby."
- 原始负描述："Plates of burgers with silverware next to ketchup and other condiments."
- 规范化正描述 1："plates of pizza with silverware next to ketchup and other condiments"
- 规范化正描述 2："plates of pizza along with the silverware , and the ketchup and other condiments are located nearby"
- 规范化负描述："plates of burgers with silverware next to ketchup and other condiments"
- 正描述 1 选择元组：`[2, 2, 1, 0.09090909090909091, 0.1]`
- 正描述 2 选择元组：`[12, 24, 6, 0.5294117647058824, 0.41414141414141414]`
- 最终比较正描述：`positive_1` / "Plates of Pizza with silverware next to ketchup and other condiments. "
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 2, "negative_start": 0, "negative_end": 2, "positive_lexemes": ["plates", "of"], "negative_lexemes": ["plates", "of"]}, {"tag": "replace", "positive_start": 2, "positive_end": 3, "negative_start": 2, "negative_end": 3, "positive_lexemes": ["pizza"], "negative_lexemes": ["burgers"]}, {"tag": "equal", "positive_start": 3, "positive_end": 11, "negative_start": 3, "negative_end": 11, "positive_lexemes": ["with", "silverware", "next", "to", "ketchup", "and", "other", "condiments"], "negative_lexemes": ["with", "silverware", "next", "to", "ketchup", "and", "other", "condiments"]}]`
- 共同前缀：`["plates", "of"]`
- 正确 contrast hull：`["pizza"]`
- 错误 contrast hull：`["burgers"]`
- 共同后缀：`["with", "silverware", "next", "to", "ketchup", "and", "other", "condiments"]`
- Hull token 覆盖率（正/负/最大）：`[0.18181818181818182, 0.18181818181818182, 0.18181818181818182]`
- 共同前缀模型 token：`[992, 1434, 354]`
- 正确 hull 模型 token：IDs `[344, 1028, 125, 100]`；text " pizza"
- 错误 hull 模型 token：IDs `[363, 543, 106, 496]`；text " burgers"
- 第一轮/第二轮分类：`complex_edit` / `one_block_local`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 16. `replace_object:1262`

- 负例类型/范围：`replace_object` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A small bathroom with a closet off to the side"
- 原始正描述 2："A compact bathroom with a closet adjacent to it."
- 原始负描述："A small bedroom with a closet off to the side."
- 规范化正描述 1："a small bathroom with a closet off to the side"
- 规范化正描述 2："a compact bathroom with a closet adjacent to it"
- 规范化负描述："a small bedroom with a closet off to the side"
- 正描述 1 选择元组：`[2, 2, 1, 0.1, 0.06521739130434782]`
- 正描述 2 选择元组：`[9, 17, 4, 0.5, 0.44680851063829785]`
- 最终比较正描述：`positive_1` / "A small bathroom with a closet off to the side"
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 2, "negative_start": 0, "negative_end": 2, "positive_lexemes": ["a", "small"], "negative_lexemes": ["a", "small"]}, {"tag": "replace", "positive_start": 2, "positive_end": 3, "negative_start": 2, "negative_end": 3, "positive_lexemes": ["bathroom"], "negative_lexemes": ["bedroom"]}, {"tag": "equal", "positive_start": 3, "positive_end": 10, "negative_start": 3, "negative_end": 10, "positive_lexemes": ["with", "a", "closet", "off", "to", "the", "side"], "negative_lexemes": ["with", "a", "closet", "off", "to", "the", "side"]}]`
- 共同前缀：`["a", "small"]`
- 正确 contrast hull：`["bathroom"]`
- 错误 contrast hull：`["bedroom"]`
- 共同后缀：`["with", "a", "closet", "off", "to", "the", "side"]`
- Hull token 覆盖率（正/负/最大）：`[0.2857142857142857, 0.2857142857142857, 0.2857142857142857]`
- 共同前缀模型 token：`[100, 3436]`
- 正确 hull 模型 token：IDs `[363, 1831, 393, 444]`；text " bathroom"
- 错误 hull 模型 token：IDs `[363, 382, 393, 444]`；text " bedroom"
- 第一轮/第二轮分类：`complex_edit` / `one_block_local`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 17. `replace_object:1328`

- 负例类型/范围：`replace_object` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："Sheep grazing in grass in the mountains "
- 原始正描述 2："Sheep are in the mountains grazing the grass."
- 原始负描述："Camels grazing in grass in the mountains."
- 规范化正描述 1："sheep grazing in grass in the mountains"
- 规范化正描述 2："sheep are in the mountains grazing the grass"
- 规范化负描述："camels grazing in grass in the mountains"
- 正描述 1 选择元组：`[2, 2, 1, 0.14285714285714285, 0.125]`
- 正描述 2 选择元组：`[11, 15, 4, 0.75, 0.6818181818181818]`
- 最终比较正描述：`positive_1` / "Sheep grazing in grass in the mountains "
- 完整 lexeme 编辑块：`[{"tag": "replace", "positive_start": 0, "positive_end": 1, "negative_start": 0, "negative_end": 1, "positive_lexemes": ["sheep"], "negative_lexemes": ["camels"]}, {"tag": "equal", "positive_start": 1, "positive_end": 7, "negative_start": 1, "negative_end": 7, "positive_lexemes": ["grazing", "in", "grass", "in", "the", "mountains"], "negative_lexemes": ["grazing", "in", "grass", "in", "the", "mountains"]}]`
- 共同前缀：`[]`
- 正确 contrast hull：`["sheep"]`
- 错误 contrast hull：`["camels"]`
- 共同后缀：`["grazing", "in", "grass", "in", "the", "mountains"]`
- Hull token 覆盖率（正/负/最大）：`[0.21428571428571427, 0.21428571428571427, 0.21428571428571427]`
- 共同前缀模型 token：`[]`
- 正确 hull 模型 token：IDs `[118, 300, 1522]`；text "sheep"
- 错误 hull 模型 token：IDs `[102, 497, 3325]`；text "camels"
- 第一轮/第二轮分类：`complex_edit` / `one_block_local`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 18. `replace_object:1369`

- 负例类型/范围：`replace_object` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："The batter, catcher and umpire during a baseball game"
- 原始正描述 2："During a baseball game, the batter, catcher, and the umpire are shown."
- 原始负描述："The pitcher, catcher and umpire during a baseball game."
- 规范化正描述 1："the batter , catcher and umpire during a baseball game"
- 规范化正描述 2："during a baseball game , the batter , catcher , and the umpire are shown"
- 规范化负描述："the pitcher , catcher and umpire during a baseball game"
- 正描述 1 选择元组：`[2, 2, 1, 0.1, 0.07272727272727272]`
- 正描述 2 选择元组：`[19, 25, 3, 0.8, 0.75]`
- 最终比较正描述：`positive_1` / "The batter, catcher and umpire during a baseball game"
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 1, "negative_start": 0, "negative_end": 1, "positive_lexemes": ["the"], "negative_lexemes": ["the"]}, {"tag": "replace", "positive_start": 1, "positive_end": 2, "negative_start": 1, "negative_end": 2, "positive_lexemes": ["batter"], "negative_lexemes": ["pitcher"]}, {"tag": "equal", "positive_start": 2, "positive_end": 10, "negative_start": 2, "negative_end": 10, "positive_lexemes": [",", "catcher", "and", "umpire", "during", "a", "baseball", "game"], "negative_lexemes": [",", "catcher", "and", "umpire", "during", "a", "baseball", "game"]}]`
- 共同前缀：`["the"]`
- 正确 contrast hull：`["batter"]`
- 错误 contrast hull：`["pitcher"]`
- 共同后缀：`[",", "catcher", "and", "umpire", "during", "a", "baseball", "game"]`
- Hull token 覆盖率（正/负/最大）：`[0.15, 0.19047619047619047, 0.19047619047619047]`
- 共同前缀模型 token：`[4345]`
- 正确 hull 模型 token：IDs `[363, 314, 887]`；text " batter"
- 错误 hull 模型 token：IDs `[344, 338, 102, 771]`；text " pitcher"
- 第一轮/第二轮分类：`complex_edit` / `one_block_local`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 19. `replace_object:1421`

- 负例类型/范围：`replace_object` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："Three sausages covered in various condiments side by side"
- 原始正描述 2："The three sausages, each covered in different condiments, are arranged next to one another."
- 原始负描述："Three sausages covered in various vegetables side by side."
- 规范化正描述 1："three sausages covered in various condiments side by side"
- 规范化正描述 2："the three sausages , each covered in different condiments , are arranged next to one another"
- 规范化负描述："three sausages covered in various vegetables side by side"
- 正描述 1 选择元组：`[2, 2, 1, 0.1111111111111111, 0.15789473684210525]`
- 正描述 2 选择元组：`[17, 25, 4, 0.75, 0.5978260869565217]`
- 最终比较正描述：`positive_1` / "Three sausages covered in various condiments side by side"
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 5, "negative_start": 0, "negative_end": 5, "positive_lexemes": ["three", "sausages", "covered", "in", "various"], "negative_lexemes": ["three", "sausages", "covered", "in", "various"]}, {"tag": "replace", "positive_start": 5, "positive_end": 6, "negative_start": 5, "negative_end": 6, "positive_lexemes": ["condiments"], "negative_lexemes": ["vegetables"]}, {"tag": "equal", "positive_start": 6, "positive_end": 9, "negative_start": 6, "negative_end": 9, "positive_lexemes": ["side", "by", "side"], "negative_lexemes": ["side", "by", "side"]}]`
- 共同前缀：`["three", "sausages", "covered", "in", "various"]`
- 正确 contrast hull：`["condiments"]`
- 错误 contrast hull：`["vegetables"]`
- 共同后缀：`["side", "by", "side"]`
- Hull token 覆盖率（正/负/最大）：`[0.1875, 0.1875, 0.1875]`
- 共同前缀模型 token：`[495, 1382, 316, 6281, 2455, 966, 478, 1837, 353, 2522]`
- 正确 hull 模型 token：IDs `[4745, 467, 1870]`；text " condiments"
- 错误 hull 模型 token：IDs `[4389, 2353, 4880]`；text " vegetables"
- 第一轮/第二轮分类：`complex_edit` / `one_block_local`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 20. `replace_object:1440`

- 负例类型/范围：`replace_object` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："some colorful carrots sitting on a table next to some other veggies"
- 原始正描述 2："The table contains some colorful carrots and other vegetables positioned on top of it."
- 原始负描述："Some colorful peaches sitting on a table next to some other veggies."
- 规范化正描述 1："some colorful carrots sitting on a table next to some other veggies"
- 规范化正描述 2："the table contains some colorful carrots and other vegetables positioned on top of it"
- 规范化负描述："some colorful peaches sitting on a table next to some other veggies"
- 正描述 1 选择元组：`[2, 2, 1, 0.08333333333333333, 0.08955223880597014]`
- 正描述 2 选择元组：`[22, 26, 3, 0.9285714285714286, 0.7058823529411765]`
- 最终比较正描述：`positive_1` / "some colorful carrots sitting on a table next to some other veggies"
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 2, "negative_start": 0, "negative_end": 2, "positive_lexemes": ["some", "colorful"], "negative_lexemes": ["some", "colorful"]}, {"tag": "replace", "positive_start": 2, "positive_end": 3, "negative_start": 2, "negative_end": 3, "positive_lexemes": ["carrots"], "negative_lexemes": ["peaches"]}, {"tag": "equal", "positive_start": 3, "positive_end": 12, "negative_start": 3, "negative_end": 12, "positive_lexemes": ["sitting", "on", "a", "table", "next", "to", "some", "other", "veggies"], "negative_lexemes": ["sitting", "on", "a", "table", "next", "to", "some", "other", "veggies"]}]`
- 共同前缀：`["some", "colorful"]`
- 正确 contrast hull：`["carrots"]`
- 错误 contrast hull：`["peaches"]`
- 共同后缀：`["sitting", "on", "a", "table", "next", "to", "some", "other", "veggies"]`
- Hull token 覆盖率（正/负/最大）：`[0.15, 0.15, 0.15]`
- 共同前缀模型 token：`[118, 3219, 4987, 1930]`
- 正确 hull 模型 token：IDs `[3751, 393, 2726]`；text " carrots"
- 错误 hull 模型 token：IDs `[2188, 1545, 2470]`；text " peaches"
- 第一轮/第二轮分类：`complex_edit` / `one_block_local`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 21. `replace_object:1532`

- 负例类型/范围：`replace_object` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："three strange looking birds walking on the grass"
- 原始正描述 2："Three birds with unusual appearances are strolling on the grass."
- 原始负描述："Three strange looking squirrels walking on the grass."
- 规范化正描述 1："three strange looking birds walking on the grass"
- 规范化正描述 2："three birds with unusual appearances are strolling on the grass"
- 规范化负描述："three strange looking squirrels walking on the grass"
- 正描述 1 选择元组：`[2, 2, 1, 0.125, 0.11538461538461539]`
- 正描述 2 选择元组：`[10, 10, 2, 0.6, 0.5238095238095238]`
- 最终比较正描述：`positive_1` / "three strange looking birds walking on the grass"
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 3, "negative_start": 0, "negative_end": 3, "positive_lexemes": ["three", "strange", "looking"], "negative_lexemes": ["three", "strange", "looking"]}, {"tag": "replace", "positive_start": 3, "positive_end": 4, "negative_start": 3, "negative_end": 4, "positive_lexemes": ["birds"], "negative_lexemes": ["squirrels"]}, {"tag": "equal", "positive_start": 4, "positive_end": 8, "negative_start": 4, "negative_end": 8, "positive_lexemes": ["walking", "on", "the", "grass"], "negative_lexemes": ["walking", "on", "the", "grass"]}]`
- 共同前缀：`["three", "strange", "looking"]`
- 正确 contrast hull：`["birds"]`
- 错误 contrast hull：`["squirrels"]`
- 共同后缀：`["walking", "on", "the", "grass"]`
- Hull token 覆盖率（正/负/最大）：`[0.13333333333333333, 0.23529411764705882, 0.23529411764705882]`
- 共同前缀模型 token：`[495, 1382, 3025, 1285, 3125]`
- 正确 hull 模型 token：IDs `[5231, 1881]`；text " birds"
- 错误 hull 模型 token：IDs `[2343, 639, 6296, 118]`；text " squirrels"
- 第一轮/第二轮分类：`complex_edit` / `one_block_local`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 22. `replace_object:433`

- 负例类型/范围：`replace_object` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："Pedestrians walking on a sidewalk by a badly tipped traffic light"
- 原始正描述 2："The traffic light is badly tipped and pedestrians are walking on a sidewalk next to it."
- 原始负描述："Cyclists riding on a sidewalk by a badly tipped traffic light."
- 规范化正描述 1："pedestrians walking on a sidewalk by a badly tipped traffic light"
- 规范化正描述 2："the traffic light is badly tipped and pedestrians are walking on a sidewalk next to it"
- 规范化负描述："cyclists riding on a sidewalk by a badly tipped traffic light"
- 正描述 1 选择元组：`[4, 4, 1, 0.18181818181818182, 0.2]`
- 正描述 2 选择元组：`[25, 27, 3, 0.9375, 0.7558139534883721]`
- 最终比较正描述：`positive_1` / "Pedestrians walking on a sidewalk by a badly tipped traffic light"
- 完整 lexeme 编辑块：`[{"tag": "replace", "positive_start": 0, "positive_end": 2, "negative_start": 0, "negative_end": 2, "positive_lexemes": ["pedestrians", "walking"], "negative_lexemes": ["cyclists", "riding"]}, {"tag": "equal", "positive_start": 2, "positive_end": 11, "negative_start": 2, "negative_end": 11, "positive_lexemes": ["on", "a", "sidewalk", "by", "a", "badly", "tipped", "traffic", "light"], "negative_lexemes": ["on", "a", "sidewalk", "by", "a", "badly", "tipped", "traffic", "light"]}]`
- 共同前缀：`[]`
- 正确 contrast hull：`["pedestrians", "walking"]`
- 错误 contrast hull：`["cyclists", "riding"]`
- 共同后缀：`["on", "a", "sidewalk", "by", "a", "badly", "tipped", "traffic", "light"]`
- Hull token 覆盖率（正/负/最大）：`[0.3333333333333333, 0.2727272727272727, 0.3333333333333333]`
- 共同前缀模型 token：`[]`
- 正确 hull 模型 token：IDs `[115, 382, 611, 809, 1106, 339, 352, 1237]`；text "pedestrians walking"
- 错误 hull 模型 token：IDs `[2863, 1110, 4638, 757, 460, 350]`；text "cyclists riding"
- 第一轮/第二轮分类：`complex_edit` / `one_block_local`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 23. `replace_object:484`

- 负例类型/范围：`replace_object` / `{"canonical": true, "pilot": true, "formal": false, "certifying_formal": false}`
- 原始正描述 1："A skillet on a stove with vegetables in it "
- 原始正描述 2："A skillet with vegetables in it is positioned on a stove."
- 原始负描述："A skillet on a stove with meat in it."
- 规范化正描述 1："a skillet on a stove with vegetables in it"
- 规范化正描述 2："a skillet with vegetables in it is positioned on a stove"
- 规范化负描述："a skillet on a stove with meat in it"
- 正描述 1 选择元组：`[2, 2, 1, 0.1111111111111111, 0.19047619047619047]`
- 正描述 2 选择元组：`[16, 16, 2, 0.8181818181818182, 0.6071428571428571]`
- 最终比较正描述：`positive_1` / "A skillet on a stove with vegetables in it "
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 6, "negative_start": 0, "negative_end": 6, "positive_lexemes": ["a", "skillet", "on", "a", "stove", "with"], "negative_lexemes": ["a", "skillet", "on", "a", "stove", "with"]}, {"tag": "replace", "positive_start": 6, "positive_end": 7, "negative_start": 6, "negative_end": 7, "positive_lexemes": ["vegetables"], "negative_lexemes": ["meat"]}, {"tag": "equal", "positive_start": 7, "positive_end": 9, "negative_start": 7, "negative_end": 9, "positive_lexemes": ["in", "it"], "negative_lexemes": ["in", "it"]}]`
- 共同前缀：`["a", "skillet", "on", "a", "stove", "with"]`
- 正确 contrast hull：`["vegetables"]`
- 错误 contrast hull：`["meat"]`
- 共同后缀：`["in", "it"]`
- Hull token 覆盖率（正/负/最大）：`[0.21428571428571427, 0.15384615384615385, 0.21428571428571427]`
- 共同前缀模型 token：`[100, 2549, 485, 3973, 619, 299, 580, 2520, 599]`
- 正确 hull 模型 token：IDs `[4389, 2353, 4880]`；text " vegetables"
- 错误 hull 模型 token：IDs `[765, 314]`；text " meat"
- 第一轮/第二轮分类：`complex_edit` / `one_block_local`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 24. `replace_relation:1214`

- 负例类型/范围：`replace_relation` / `{"canonical": true, "pilot": true, "formal": false, "certifying_formal": false}`
- 原始正描述 1："Street signs and traffic lights on a city street"
- 原始正描述 2："There are street signs and traffic lights along a city street."
- 原始负描述："Street signs and traffic lights beside a city street."
- 规范化正描述 1："street signs and traffic lights on a city street"
- 规范化正描述 2："there are street signs and traffic lights along a city street"
- 规范化负描述："street signs and traffic lights beside a city street"
- 正描述 1 选择元组：`[2, 2, 1, 0.1111111111111111, 0.11538461538461539]`
- 正描述 2 选择元组：`[4, 14, 2, 0.2727272727272727, 0.26229508196721313]`
- 最终比较正描述：`positive_1` / "Street signs and traffic lights on a city street"
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 5, "negative_start": 0, "negative_end": 5, "positive_lexemes": ["street", "signs", "and", "traffic", "lights"], "negative_lexemes": ["street", "signs", "and", "traffic", "lights"]}, {"tag": "replace", "positive_start": 5, "positive_end": 6, "negative_start": 5, "negative_end": 6, "positive_lexemes": ["on"], "negative_lexemes": ["beside"]}, {"tag": "equal", "positive_start": 6, "positive_end": 9, "negative_start": 6, "negative_end": 9, "positive_lexemes": ["a", "city", "street"], "negative_lexemes": ["a", "city", "street"]}]`
- 共同前缀：`["street", "signs", "and", "traffic", "lights"]`
- 正确 contrast hull：`["on"]`
- 错误 contrast hull：`["beside"]`
- 共同后缀：`["a", "city", "street"]`
- Hull token 覆盖率（正/负/最大）：`[0.06666666666666667, 0.17647058823529413, 0.17647058823529413]`
- 共同前缀模型 token：`[432, 306, 439, 2185, 118, 376, 1946, 5935, 2795, 118]`
- 正确 hull 模型 token：IDs `[619]`；text " on"
- 错误 hull 模型 token：IDs `[363, 329, 688]`；text " beside"
- 第一轮/第二轮分类：`complex_edit` / `one_block_local`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 25. `replace_relation:1300`

- 负例类型/范围：`replace_relation` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："a living room with a big table next to a book shelf"
- 原始正描述 2："The book shelf is adjacent to the large table in the living room."
- 原始负描述："A living room with a big table away from a book shelf."
- 规范化正描述 1："a living room with a big table next to a book shelf"
- 规范化正描述 2："the book shelf is adjacent to the large table in the living room"
- 规范化负描述："a living room with a big table away from a book shelf"
- 正描述 1 选择元组：`[4, 4, 1, 0.16666666666666666, 0.1320754716981132]`
- 正描述 2 选择元组：`[25, 25, 2, 1.0, 0.796875]`
- 最终比较正描述：`positive_1` / "a living room with a big table next to a book shelf"
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 7, "negative_start": 0, "negative_end": 7, "positive_lexemes": ["a", "living", "room", "with", "a", "big", "table"], "negative_lexemes": ["a", "living", "room", "with", "a", "big", "table"]}, {"tag": "replace", "positive_start": 7, "positive_end": 9, "negative_start": 7, "negative_end": 9, "positive_lexemes": ["next", "to"], "negative_lexemes": ["away", "from"]}, {"tag": "equal", "positive_start": 9, "positive_end": 12, "negative_start": 9, "negative_end": 12, "positive_lexemes": ["a", "book", "shelf"], "negative_lexemes": ["a", "book", "shelf"]}]`
- 共同前缀：`["a", "living", "room", "with", "a", "big", "table"]`
- 正确 contrast hull：`["next", "to"]`
- 错误 contrast hull：`["away", "from"]`
- 共同后缀：`["a", "book", "shelf"]`
- Hull token 覆盖率（正/负/最大）：`[0.11764705882352941, 0.16666666666666666, 0.16666666666666666]`
- 共同前缀模型 token：`[100, 406, 4917, 1552, 444, 599, 299, 363, 499, 2630]`
- 正确 hull 模型 token：IDs `[4658, 364]`；text " next to"
- 错误 hull 模型 token：IDs `[299, 5054, 961]`；text " away from"
- 第一轮/第二轮分类：`complex_edit` / `one_block_local`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 26. `replace_relation:1385`

- 负例类型/范围：`replace_relation` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A living room with wooden floors and furniture"
- 原始正描述 2："Furniture is located within the wooden floored living room."
- 原始负描述："A living room without wooden floors and furniture."
- 规范化正描述 1："a living room with wooden floors and furniture"
- 规范化正描述 2："furniture is located within the wooden floored living room"
- 规范化负描述："a living room without wooden floors and furniture"
- 正描述 1 选择元组：`[2, 2, 1, 0.125, 0.061224489795918366]`
- 正描述 2 选择元组：`[15, 17, 3, 0.8888888888888888, 0.6206896551724138]`
- 最终比较正描述：`positive_1` / "A living room with wooden floors and furniture"
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 3, "negative_start": 0, "negative_end": 3, "positive_lexemes": ["a", "living", "room"], "negative_lexemes": ["a", "living", "room"]}, {"tag": "replace", "positive_start": 3, "positive_end": 4, "negative_start": 3, "negative_end": 4, "positive_lexemes": ["with"], "negative_lexemes": ["without"]}, {"tag": "equal", "positive_start": 4, "positive_end": 8, "negative_start": 4, "negative_end": 8, "positive_lexemes": ["wooden", "floors", "and", "furniture"], "negative_lexemes": ["wooden", "floors", "and", "furniture"]}]`
- 共同前缀：`["a", "living", "room"]`
- 正确 contrast hull：`["with"]`
- 错误 contrast hull：`["without"]`
- 共同后缀：`["wooden", "floors", "and", "furniture"]`
- Hull token 覆盖率（正/负/最大）：`[0.0625, 0.0625, 0.0625]`
- 共同前缀模型 token：`[100, 406, 4917, 1552, 444]`
- 正确 hull 模型 token：IDs `[599]`；text " with"
- 错误 hull 模型 token：IDs `[4007]`；text " without"
- 第一轮/第二轮分类：`complex_edit` / `one_block_local`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 27. `replace_relation:337`

- 负例类型/范围：`replace_relation` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："Looking down at the spectators and players during a basketball game"
- 原始正描述 2："Observing the players and the spectators from above during a basketball game."
- 原始负描述："Looking down at the spectators and players after a basketball game."
- 规范化正描述 1："looking down at the spectators and players during a basketball game"
- 规范化正描述 2："observing the players and the spectators from above during a basketball game"
- 规范化负描述："looking down at the spectators and players after a basketball game"
- 正描述 1 选择元组：`[2, 2, 1, 0.09090909090909091, 0.08955223880597014]`
- 正描述 2 选择元组：`[13, 17, 3, 0.5833333333333334, 0.4605263157894737]`
- 最终比较正描述：`positive_1` / "Looking down at the spectators and players during a basketball game"
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 7, "negative_start": 0, "negative_end": 7, "positive_lexemes": ["looking", "down", "at", "the", "spectators", "and", "players"], "negative_lexemes": ["looking", "down", "at", "the", "spectators", "and", "players"]}, {"tag": "replace", "positive_start": 7, "positive_end": 8, "negative_start": 7, "negative_end": 8, "positive_lexemes": ["during"], "negative_lexemes": ["after"]}, {"tag": "equal", "positive_start": 8, "positive_end": 11, "negative_start": 8, "negative_end": 11, "positive_lexemes": ["a", "basketball", "game"], "negative_lexemes": ["a", "basketball", "game"]}]`
- 共同前缀：`["looking", "down", "at", "the", "spectators", "and", "players"]`
- 正确 contrast hull：`["during"]`
- 错误 contrast hull：`["after"]`
- 共同后缀：`["a", "basketball", "game"]`
- Hull token 覆盖率（正/负/最大）：`[0.047619047619047616, 0.047619047619047616, 0.047619047619047616]`
- 共同前缀模型 token：`[722, 114, 1237, 4076, 1248, 309, 946, 426, 314, 1945, 376, 2865, 496]`
- 正确 hull 模型 token：IDs `[4266]`；text " during"
- 错误 hull 模型 token：IDs `[3898]`；text " after"
- 第一轮/第二轮分类：`complex_edit` / `one_block_local`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 28. `replace_relation:434`

- 负例类型/范围：`replace_relation` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："Two adult pheasants walking slowly across a street"
- 原始正描述 2："Two adult pheasants are slowly walking across the street."
- 原始负描述："Two adult pheasants flying slowly across a street."
- 规范化正描述 1："two adult pheasants walking slowly across a street"
- 规范化正描述 2："two adult pheasants are slowly walking across the street"
- 规范化负描述："two adult pheasants flying slowly across a street"
- 正描述 1 选择元组：`[2, 2, 1, 0.125, 0.06]`
- 正描述 2 选择元组：`[5, 9, 3, 0.3333333333333333, 0.30357142857142855]`
- 最终比较正描述：`positive_1` / "Two adult pheasants walking slowly across a street"
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 3, "negative_start": 0, "negative_end": 3, "positive_lexemes": ["two", "adult", "pheasants"], "negative_lexemes": ["two", "adult", "pheasants"]}, {"tag": "replace", "positive_start": 3, "positive_end": 4, "negative_start": 3, "negative_end": 4, "positive_lexemes": ["walking"], "negative_lexemes": ["flying"]}, {"tag": "equal", "positive_start": 4, "positive_end": 8, "negative_start": 4, "negative_end": 8, "positive_lexemes": ["slowly", "across", "a", "street"], "negative_lexemes": ["slowly", "across", "a", "street"]}]`
- 共同前缀：`["two", "adult", "pheasants"]`
- 正确 contrast hull：`["walking"]`
- 错误 contrast hull：`["flying"]`
- 共同后缀：`["slowly", "across", "a", "street"]`
- Hull token 覆盖率（正/负/最大）：`[0.15789473684210525, 0.15789473684210525, 0.15789473684210525]`
- 共同前缀模型 token：`[119, 122, 114, 1200, 1005, 344, 300, 390, 5483]`
- 正确 hull 模型 token：IDs `[339, 352, 1237]`；text " walking"
- 错误 hull 模型 token：IDs `[341, 542, 350]`；text " flying"
- 第一轮/第二轮分类：`complex_edit` / `one_block_local`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 29. `replace_relation:639`

- 负例类型/范围：`replace_relation` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："A refrigerator on a patio flooded with water, beverage cans and a beer bottle. "
- 原始正描述 2："A refrigerator on a patio with a flood of water, beverage cans, and a beer bottle."
- 原始负描述："A refrigerator on a patio empty of water, beverage cans and a beer bottle."
- 规范化正描述 1："a refrigerator on a patio flooded with water , beverage cans and a beer bottle"
- 规范化正描述 2："a refrigerator on a patio with a flood of water , beverage cans , and a beer bottle"
- 规范化负描述："a refrigerator on a patio empty of water , beverage cans and a beer bottle"
- 正描述 1 选择元组：`[4, 4, 1, 0.13333333333333333, 0.14102564102564102]`
- 正描述 2 选择元组：`[5, 15, 3, 0.2222222222222222, 0.1686746987951807]`
- 最终比较正描述：`positive_1` / "A refrigerator on a patio flooded with water, beverage cans and a beer bottle. "
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 5, "negative_start": 0, "negative_end": 5, "positive_lexemes": ["a", "refrigerator", "on", "a", "patio"], "negative_lexemes": ["a", "refrigerator", "on", "a", "patio"]}, {"tag": "replace", "positive_start": 5, "positive_end": 7, "negative_start": 5, "negative_end": 7, "positive_lexemes": ["flooded", "with"], "negative_lexemes": ["empty", "of"]}, {"tag": "equal", "positive_start": 7, "positive_end": 15, "negative_start": 7, "negative_end": 15, "positive_lexemes": ["water", ",", "beverage", "cans", "and", "a", "beer", "bottle"], "negative_lexemes": ["water", ",", "beverage", "cans", "and", "a", "beer", "bottle"]}]`
- 共同前缀：`["a", "refrigerator", "on", "a", "patio"]`
- 正确 contrast hull：`["flooded", "with"]`
- 错误 contrast hull：`["empty", "of"]`
- 共同后缀：`["water", ",", "beverage", "cans", "and", "a", "beer", "bottle"]`
- Hull token 覆盖率（正/负/最大）：`[0.14285714285714285, 0.14285714285714285, 0.14285714285714285]`
- 共同前缀模型 token：`[100, 1786, 117, 499, 311, 2991, 619, 299, 4195, 3604]`
- 正确 hull 模型 token：IDs `[5796, 1318, 382, 599]`；text " flooded with"
- 错误 hull 模型 token：IDs `[1682, 875, 124, 354]`；text " empty of"
- 第一轮/第二轮分类：`ambiguous_source` / `one_block_local`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null

### 30. `replace_relation:742`

- 负例类型/范围：`replace_relation` / `{"canonical": true, "pilot": false, "formal": true, "certifying_formal": true}`
- 原始正描述 1："a bathroom with a toilet and a lot of ski boots"
- 原始正描述 2："A lot of ski boots are in a bathroom with a toilet."
- 原始负描述："A bathroom without a toilet and a lot of ski boots."
- 规范化正描述 1："a bathroom with a toilet and a lot of ski boots"
- 规范化正描述 2："a lot of ski boots are in a bathroom with a toilet"
- 规范化负描述："a bathroom without a toilet and a lot of ski boots"
- 正描述 1 选择元组：`[2, 2, 1, 0.09090909090909091, 0.06]`
- 正描述 2 选择元组：`[19, 21, 3, 0.8333333333333334, 0.74]`
- 最终比较正描述：`positive_1` / "a bathroom with a toilet and a lot of ski boots"
- 完整 lexeme 编辑块：`[{"tag": "equal", "positive_start": 0, "positive_end": 2, "negative_start": 0, "negative_end": 2, "positive_lexemes": ["a", "bathroom"], "negative_lexemes": ["a", "bathroom"]}, {"tag": "replace", "positive_start": 2, "positive_end": 3, "negative_start": 2, "negative_end": 3, "positive_lexemes": ["with"], "negative_lexemes": ["without"]}, {"tag": "equal", "positive_start": 3, "positive_end": 11, "negative_start": 3, "negative_end": 11, "positive_lexemes": ["a", "toilet", "and", "a", "lot", "of", "ski", "boots"], "negative_lexemes": ["a", "toilet", "and", "a", "lot", "of", "ski", "boots"]}]`
- 共同前缀：`["a", "bathroom"]`
- 正确 contrast hull：`["with"]`
- 错误 contrast hull：`["without"]`
- 共同后缀：`["a", "toilet", "and", "a", "lot", "of", "ski", "boots"]`
- Hull token 覆盖率（正/负/最大）：`[0.05, 0.05, 0.05]`
- 共同前缀模型 token：`[100, 363, 1831, 393, 444]`
- 正确 hull 模型 token：IDs `[599]`；text " with"
- 错误 hull 模型 token：IDs `[4007]`；text " without"
- 第一轮/第二轮分类：`complex_edit` / `one_block_local`
- 自动判断："positive_1_selection_tuple_lexicographically_smaller"；null
