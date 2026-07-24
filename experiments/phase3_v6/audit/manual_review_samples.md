# SugarCrepe++ 编辑片段自动审计抽查材料

本文件仅供后续人工审核；以下样本尚未经过人工验证。

固定随机种子：`3407`；每个分组最多抽取 `30` 条。不同分组可重复出现同一样本。

## 成功恢复

候选 `2624` 条，本节抽取 `30` 条。

### 1. `replace_attribute:125`

- 负例类型：`replace_attribute`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："A box full of matching, ridged donuts with glaze."
- 正描述 2："A box containing a collection of identical, grooved donuts that have been coated with glaze."
- 负描述："A box full of matching, smooth donuts with glaze."
- 自动来源：`positive_1` / "A box full of matching, ridged donuts with glaze."
- 正确片段："ridged"
- 错误片段："smooth"
- 正确片段 token：IDs `[757, 460, 106, 382]`；pieces `["Ġr", "id", "g", "ed"]`；decode " ridged"
- 错误片段 token：IDs `[2589, 824, 495]`；pieces `["Ġsm", "oo", "th"]`；decode " smooth"
- 自动分类：`unique_alignment`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因：null
- Token 边界提示：[]

### 2. `replace_attribute:29`

- 负例类型：`replace_attribute`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："A person riding a green motorcycle with a side car."
- 正描述 2："A person is riding a green motorcycle with a side car."
- 负描述："A person riding a purple motorcycle with a side car."
- 自动来源：`positive_1` / "A person riding a green motorcycle with a side car."
- 正确片段："green"
- 错误片段："purple"
- 正确片段 token：IDs `[5921]`；pieces `["Ġgreen"]`；decode " green"
- 错误片段 token：IDs `[3315, 833]`；pieces `["Ġpur", "ple"]`；decode " purple"
- 自动分类：`unique_alignment`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因：null
- Token 边界提示：[]

### 3. `replace_attribute:332`

- 负例类型：`replace_attribute`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："A zebra standing in a grassy field by a woods."
- 正描述 2："A zebra is standing adjacent to the woods in a grassy field."
- 负描述："A zebra standing in a rocky field by a woods."
- 自动来源：`positive_1` / "A zebra standing in a grassy field by a woods."
- 正确片段："grass"
- 错误片段："rock"
- 正确片段 token：IDs `[492, 117, 1388]`；pieces `["Ġg", "r", "ass"]`；decode " grass"
- 错误片段 token：IDs `[1552, 892]`；pieces `["Ġro", "ck"]`；decode " rock"
- 自动分类：`unique_alignment`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因：null
- Token 边界提示：[]

### 4. `replace_attribute:412`

- 负例类型：`replace_attribute`
- 阶段三范围：`pilot`；certifying formal：`False`
- 正描述 1："A person uses a laptop in an otherwise dark room."
- 正描述 2："In a room that is otherwise dark, a person uses a laptop."
- 负描述："A person uses a laptop in an otherwise bright room."
- 自动来源：`positive_1` / "A person uses a laptop in an otherwise dark room."
- 正确片段："dark"
- 错误片段："bright"
- 正确片段 token：IDs `[373, 2000]`；pieces `["Ġd", "ark"]`；decode " dark"
- 错误片段 token：IDs `[3461, 774]`；pieces `["Ġbr", "ight"]`；decode " bright"
- 自动分类：`unique_alignment`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因：null
- Token 边界提示：[]

### 5. `replace_attribute:626`

- 负例类型：`replace_attribute`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："An airplane is parked next to a domed tower."
- 正描述 2："The domed tower is positioned next to the parked airplane."
- 负描述："An airplane is parked next to a squared tower."
- 自动来源：`positive_1` / "An airplane is parked next to a domed tower."
- 正确片段："dom"
- 错误片段："squar"
- 正确片段 token：IDs `[373, 444, 382]`；pieces `["Ġd", "om", "ed"]`；decode " domed"
- 错误片段 token：IDs `[2574, 103]`；pieces `["Ġsquare", "d"]`；decode " squared"
- 自动分类：`unique_alignment`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因：null
- Token 边界提示：[]

### 6. `replace_attribute:72`

- 负例类型：`replace_attribute`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："People stand near the curb behind a lime green double-decked bus."
- 正描述 2："The lime green double-decked bus is positioned in front of the people who are standing near the curb."
- 负描述："People stand near the curb behind a lime green single-decked bus."
- 自动来源：`positive_1` / "People stand near the curb behind a lime green double-decked bus."
- 正确片段："doub"
- 错误片段："sing"
- 正确片段 token：IDs `[373, 326, 2129]`；pieces `["Ġd", "ou", "ble"]`；decode " double"
- 错误片段 token：IDs `[4486]`；pieces `["Ġsingle"]`；decode " single"
- 自动分类：`unique_alignment`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因：null
- Token 边界提示：[]

### 7. `replace_object:1010`

- 负例类型：`replace_object`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："A colorful public restroom focused on the sinks."
- 正描述 2："The sinks are the focal point of the vibrant public restroom."
- 负描述："A colorful public restroom focused on the toilet stalls."
- 自动来源：`positive_1` / "A colorful public restroom focused on the sinks."
- 正确片段："sink"
- 错误片段："toilet stall"
- 正确片段 token：IDs `[316, 301, 1275]`；pieces `["Ġs", "in", "ks"]`；decode " sinks"
- 错误片段 token：IDs `[364, 1299, 119, 580, 1266, 118]`；pieces `["Ġto", "ile", "t", "Ġst", "all", "s"]`；decode " toilet stalls"
- 自动分类：`unique_alignment`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因：null
- Token 边界提示：[]

### 8. `replace_object:1255`

- 负例类型：`replace_object`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："A black cat sits in a white bathroom sink."
- 正描述 2："A white bathroom sink contains a black cat sitting in it."
- 负描述："A black dog sits in a white bathroom sink."
- 自动来源：`positive_1` / "A black cat sits in a white bathroom sink."
- 正确片段："cat"
- 错误片段："dog"
- 正确片段 token：IDs `[3706]`；pieces `["Ġcat"]`；decode " cat"
- 错误片段 token：IDs `[1041, 106]`；pieces `["Ġdo", "g"]`；decode " dog"
- 自动分类：`unique_alignment`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因：null
- Token 边界提示：[]

### 9. `replace_object:1378`

- 负例类型：`replace_object`
- 阶段三范围：`formal`；certifying formal：`False`
- 正描述 1："Two young women are washing two motorcycles with hoses."
- 正描述 2："A couple of young women are using hoses to wash two motorcycles."
- 负描述："Two young men are washing two motorcycles with hoses."
- 自动来源：`positive_1` / "Two young women are washing two motorcycles with hoses."
- 正确片段："wo"
- 错误片段：""
- 正确片段 token：IDs `[339, 444]`；pieces `["Ġw", "om"]`；decode " wom"
- 错误片段 token：IDs `[351]`；pieces `["Ġm"]`；decode " m"
- 自动分类：`unique_alignment`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因：null
- Token 边界提示：[]

### 10. `replace_object:1437`

- 负例类型：`replace_object`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："A woman sitting looking at her phone with an iron cast woman next to her."
- 正描述 2："A female person is sitting adjacent to an iron cast woman while looking at her phone."
- 负描述："A woman sitting looking at her phone with a painting next to her."
- 自动来源：`positive_1` / "A woman sitting looking at her phone with an iron cast woman next to her."
- 正确片段："n iron cast woman"
- 错误片段：" painting"
- 正确片段 token：IDs `[346, 256, 3234, 317, 1154, 339, 444, 325]`；pieces `["Ġan", "Ġ", "iron", "Ġc", "ast", "Ġw", "om", "an"]`；decode " an iron cast woman"
- 错误片段 token：IDs `[299, 5063, 2912]`；pieces `["Ġa", "Ġpain", "ting"]`；decode " a painting"
- 自动分类：`unique_alignment`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因：null
- Token 边界提示：[]

### 11. `replace_object:1447`

- 负例类型：`replace_object`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："A corner of a rest room with a cookie and coffee."
- 正描述 2："In the corner of the rest room, there is a cookie and coffee."
- 负描述："A corner of a living room with a cookie and coffee."
- 自动来源：`positive_1` / "A corner of a rest room with a cookie and coffee."
- 正确片段："rest"
- 错误片段："living"
- 正确片段 token：IDs `[5128]`；pieces `["Ġrest"]`；decode " rest"
- 错误片段 token：IDs `[406, 4917]`；pieces `["Ġl", "iving"]`；decode " living"
- 自动分类：`unique_alignment`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因：null
- Token 边界提示：[]

### 12. `replace_object:1575`

- 负例类型：`replace_object`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："People fly kites in a large park in the middle of a city."
- 正描述 2："In a large park situated in the heart of a city, people fly kites."
- 负描述："People fly hot air balloons in a large park in the middle of a city."
- 自动来源：`positive_1` / "People fly kites in a large park in the middle of a city."
- 正确片段："kite"
- 错误片段："hot air balloon"
- 正确片段 token：IDs `[914, 338, 329]`；pieces `["Ġk", "it", "es"]`；decode " kites"
- 错误片段 token：IDs `[429, 593, 3980, 363, 352, 722, 3070]`；pieces `["Ġh", "ot", "Ġair", "Ġb", "al", "lo", "ons"]`；decode " hot air balloons"
- 自动分类：`unique_alignment`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因：null
- Token 边界提示：[]

### 13. `replace_object:193`

- 负例类型：`replace_object`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："A room with a bed, a desk, and a television."
- 正描述 2："The room contains a television, a bed and a desk."
- 负描述："A room with a bed, a desk, and a fireplace."
- 自动来源：`positive_1` / "A room with a bed, a desk, and a television."
- 正确片段："television"
- 错误片段："fireplace"
- 正确片段 token：IDs `[1047, 361, 121, 5190]`；pieces `["Ġte", "le", "v", "ision"]`；decode " television"
- 错误片段 token：IDs `[341, 1475, 4256]`；pieces `["Ġf", "ire", "place"]`；decode " fireplace"
- 自动分类：`unique_alignment`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因：null
- Token 边界提示：[]

### 14. `replace_object:253`

- 负例类型：`replace_object`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："A zebra stands in high grass in wooded area."
- 正描述 2："A zebra is positioned within a wooded area in high grass."
- 负描述："A giraffe stands in high grass in wooded area."
- 自动来源：`positive_1` / "A zebra stands in high grass in wooded area."
- 正确片段："zebra"
- 错误片段："giraffe"
- 正确片段 token：IDs `[3243, 3037, 559]`；pieces `["Ġz", "eb", "ra"]`；decode " zebra"
- 错误片段 token：IDs `[492, 108, 559, 1627, 104]`；pieces `["Ġg", "i", "ra", "ff", "e"]`；decode " giraffe"
- 自动分类：`unique_alignment`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因：null
- Token 边界提示：[]

### 15. `replace_object:363`

- 负例类型：`replace_object`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："Two vases filled with flowers on a table."
- 正描述 2："The table has two vases filled with flowers on it."
- 负描述："Two vases filled with candles on a table."
- 自动来源：`positive_1` / "Two vases filled with flowers on a table."
- 正确片段："flower"
- 错误片段："candle"
- 正确片段 token：IDs `[5652, 496]`；pieces `["Ġflow", "ers"]`；decode " flowers"
- 错误片段 token：IDs `[541, 103, 1907]`；pieces `["Ġcan", "d", "les"]`；decode " candles"
- 自动分类：`unique_alignment`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因：null
- Token 边界提示：[]

### 16. `replace_object:45`

- 负例类型：`replace_object`
- 阶段三范围：`pilot`；certifying formal：`False`
- 正描述 1："A painting of a vase with a sunflower on a table."
- 正描述 2："A vase with a sunflower is positioned on a table in a painting."
- 负描述："A sculpture of a vase with a sunflower on a table."
- 自动来源：`positive_1` / "A painting of a vase with a sunflower on a table."
- 正确片段："painting"
- 错误片段："sculpture"
- 正确片段 token：IDs `[5063, 2912]`；pieces `["Ġpain", "ting"]`；decode " painting"
- 错误片段 token：IDs `[1416, 549, 875, 745]`；pieces `["Ġsc", "ul", "pt", "ure"]`；decode " sculpture"
- 自动分类：`unique_alignment`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因：null
- Token 边界提示：[]

### 17. `replace_object:53`

- 负例类型：`replace_object`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："Two girls with a large white teddy bear."
- 正描述 2："Two girls are holding a teddy bear that is large and white."
- 负描述："Two boys with a large white teddy bear."
- 自动来源：`positive_1` / "Two girls with a large white teddy bear."
- 正确片段："girl"
- 错误片段："boy"
- 正确片段 token：IDs `[492, 639, 111, 118]`；pieces `["Ġg", "ir", "l", "s"]`；decode " girls"
- 错误片段 token：IDs `[1847, 2211]`；pieces `["Ġbo", "ys"]`；decode " boys"
- 自动分类：`unique_alignment`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因：null
- Token 边界提示：[]

### 18. `replace_object:567`

- 负例类型：`replace_object`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："A woman sitting in front of a giant pizza."
- 正描述 2："A giant pizza is in front of a woman who is sitting."
- 负描述："A man sitting in front of a giant pizza."
- 自动来源：`positive_1` / "A woman sitting in front of a giant pizza."
- 正确片段："wo"
- 错误片段：""
- 正确片段 token：IDs `[339, 444, 325]`；pieces `["Ġw", "om", "an"]`；decode " woman"
- 错误片段 token：IDs `[1672]`；pieces `["Ġman"]`；decode " man"
- 自动分类：`unique_alignment`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因：null
- Token 边界提示：[]

### 19. `replace_object:65`

- 负例类型：`replace_object`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："A man holding a tennis racquet on a court."
- 正描述 2："A man is on a court holding a tennis racquet."
- 负描述："A woman holding a tennis racquet on a court."
- 自动来源：`positive_1` / "A man holding a tennis racquet on a court."
- 正确片段：""
- 错误片段："wo"
- 正确片段 token：IDs `[1672]`；pieces `["Ġman"]`；decode " man"
- 错误片段 token：IDs `[339, 444, 325]`；pieces `["Ġw", "om", "an"]`；decode " woman"
- 自动分类：`unique_alignment`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因：null
- Token 边界提示：[]

### 20. `replace_object:805`

- 负例类型：`replace_object`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："Two bear cubs are playing on a log."
- 正描述 2："The log is positioned under two bear cubs while they are playing on it."
- 负描述："Two river otters are playing on a log."
- 自动来源：`positive_1` / "Two bear cubs are playing on a log."
- 正确片段："bear cub"
- 错误片段："river otter"
- 正确片段 token：IDs `[600, 370, 317, 1352, 118]`；pieces `["Ġbe", "ar", "Ġc", "ub", "s"]`；decode " bear cubs"
- 错误片段 token：IDs `[757, 5258, 319, 119, 4271]`；pieces `["Ġr", "iver", "Ġo", "t", "ters"]`；decode " river otters"
- 自动分类：`unique_alignment`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因：null
- Token 边界提示：[]

### 21. `replace_object:987`

- 负例类型：`replace_object`
- 阶段三范围：`pilot`；certifying formal：`False`
- 正描述 1："A boat that is sitting in the water."
- 正描述 2："The boat is positioned in the water."
- 负描述："A canoe that is sitting in the water."
- 自动来源：`positive_1` / "A boat that is sitting in the water."
- 正确片段："boat"
- 错误片段："canoe"
- 正确片段 token：IDs `[1847, 314]`；pieces `["Ġbo", "at"]`；decode " boat"
- 错误片段 token：IDs `[541, 114, 104]`；pieces `["Ġcan", "o", "e"]`；decode " canoe"
- 自动分类：`unique_alignment`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因：null
- Token 边界提示：[]

### 22. `replace_relation:1095`

- 负例类型：`replace_relation`
- 阶段三范围：`pilot`；certifying formal：`False`
- 正描述 1："Luggage is arranged in groups on a concrete platform."
- 正描述 2："The concrete platform accommodates the luggage in organized groups."
- 负描述："Luggage is arranged in groups beside a concrete platform."
- 自动来源：`positive_1` / "Luggage is arranged in groups on a concrete platform."
- 正确片段："on"
- 错误片段："beside"
- 正确片段 token：IDs `[619]`；pieces `["Ġon"]`；decode " on"
- 错误片段 token：IDs `[363, 329, 688]`；pieces `["Ġb", "es", "ide"]`；decode " beside"
- 自动分类：`unique_alignment`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因：null
- Token 边界提示：[]

### 23. `replace_relation:1187`

- 负例类型：`replace_relation`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："A person riding a snowboard down a snowy slope."
- 正描述 2："The snowboard rider glides down the snowy slope."
- 负描述："A person is falling down a snowy slope."
- 自动来源：`positive_1` / "A person riding a snowboard down a snowy slope."
- 正确片段："riding a snowboard"
- 错误片段："is falling"
- 正确片段 token：IDs `[757, 460, 350, 299, 316, 1103, 101, 114, 1433]`；pieces `["Ġr", "id", "ing", "Ġa", "Ġs", "now", "b", "o", "ard"]`；decode " riding a snowboard"
- 错误片段 token：IDs `[395, 6347, 350]`；pieces `["Ġis", "Ġfall", "ing"]`；decode " is falling"
- 自动分类：`unique_alignment`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因：null
- Token 边界提示：[]

### 24. `replace_relation:1391`

- 负例类型：`replace_relation`
- 阶段三范围：`pilot`；certifying formal：`False`
- 正描述 1："A long-haired person standing outside holding a racquet with both hands."
- 正描述 2："An individual with long hair is standing outdoors and holding a racket with both hands."
- 负描述："A long-haired person sitting outside holding a racquet with both hands."
- 自动来源：`positive_1` / "A long-haired person standing outside holding a racquet with both hands."
- 正确片段："tand"
- 错误片段："itt"
- 正确片段 token：IDs `[2823, 350]`；pieces `["Ġstand", "ing"]`；decode " standing"
- 错误片段 token：IDs `[5305, 2912]`；pieces `["Ġsit", "ting"]`；decode " sitting"
- 自动分类：`unique_alignment`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因：null
- Token 边界提示：[]

### 25. `replace_relation:148`

- 负例类型：`replace_relation`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："A group of dogs that are standing in the grass."
- 正描述 2："A pack of dogs that are standing in the grass."
- 负描述："A group of dogs that are lying in the grass."
- 自动来源：`positive_1` / "A group of dogs that are standing in the grass."
- 正确片段："stand"
- 错误片段："ly"
- 正确片段 token：IDs `[2823]`；pieces `["Ġstand"]`；decode " stand"
- 错误片段 token：IDs `[406, 124]`；pieces `["Ġl", "y"]`；decode " ly"
- 自动分类：`unique_alignment`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因：null
- Token 边界提示：[]

### 26. `replace_relation:326`

- 负例类型：`replace_relation`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："A dog is playing with a ball in the grass."
- 正描述 2："The ball is in the grass, and the dog is playing with it."
- 负描述："A dog is chasing a ball in the grass."
- 自动来源：`positive_1` / "A dog is playing with a ball in the grass."
- 正确片段："playing with"
- 错误片段："chasing"
- 正确片段 token：IDs `[2865, 350, 599]`；pieces `["Ġplay", "ing", "Ġwith"]`；decode " playing with"
- 错误片段 token：IDs `[890, 390, 350]`；pieces `["Ġch", "as", "ing"]`；decode " chasing"
- 自动分类：`unique_alignment`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因：null
- Token 边界提示：[]

### 27. `replace_relation:372`

- 负例类型：`replace_relation`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："A person is holding a spatula near slices of bread on a stove."
- 正描述 2："An individual is holding a spatula close to bread slices on the stove."
- 负描述："A person is pushing a spatula near slices of bread on a stove."
- 自动来源：`positive_1` / "A person is holding a spatula near slices of bread on a stove."
- 正确片段："hold"
- 错误片段："push"
- 正确片段 token：IDs `[429, 2569]`；pieces `["Ġh", "old"]`；decode " hold"
- 错误片段 token：IDs `[344, 4923]`；pieces `["Ġp", "ush"]`；decode " push"
- 自动分类：`unique_alignment`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因：null
- Token 边界提示：[]

### 28. `replace_relation:442`

- 负例类型：`replace_relation`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："A teddy bear sitting in front of a pile of boxes."
- 正描述 2："A teddy bear is positioned in front of a pile of boxes."
- 负描述："A teddy bear standing in front of a pile of boxes."
- 自动来源：`positive_1` / "A teddy bear sitting in front of a pile of boxes."
- 正确片段："itt"
- 错误片段："tand"
- 正确片段 token：IDs `[5305, 2912]`；pieces `["Ġsit", "ting"]`；decode " sitting"
- 错误片段 token：IDs `[2823, 350]`；pieces `["Ġstand", "ing"]`；decode " standing"
- 自动分类：`unique_alignment`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因：null
- Token 边界提示：[]

### 29. `replace_relation:712`

- 负例类型：`replace_relation`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："Some people are standing outside a building with suitcases."
- 正描述 2："Some individuals with suitcases are standing outside a building."
- 负描述："Some people are sitting outside a building with suitcases."
- 自动来源：`positive_1` / "Some people are standing outside a building with suitcases."
- 正确片段："tand"
- 错误片段："itt"
- 正确片段 token：IDs `[2823, 350]`；pieces `["Ġstand", "ing"]`；decode " standing"
- 错误片段 token：IDs `[5305, 2912]`；pieces `["Ġsit", "ting"]`；decode " sitting"
- 自动分类：`unique_alignment`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因：null
- Token 边界提示：[]

### 30. `replace_relation:952`

- 负例类型：`replace_relation`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："A hand with finger on a blender filled with liquid."
- 正描述 2："A blender filled with liquid is touched by a hand with a finger."
- 负描述："A hand with finger on a blender that is empty."
- 自动来源：`positive_1` / "A hand with finger on a blender filled with liquid."
- 正确片段："filled with liquid"
- 错误片段："that is empty"
- 正确片段 token：IDs `[2608, 2003, 599, 406, 2680, 460]`；pieces `["Ġfil", "led", "Ġwith", "Ġl", "iqu", "id"]`；decode " filled with liquid"
- 错误片段 token：IDs `[591, 395, 1682, 875, 124]`；pieces `["Ġthat", "Ġis", "Ġem", "pt", "y"]`；decode " that is empty"
- 自动分类：`unique_alignment`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因：null
- Token 边界提示：[]

## 来源不唯一

候选 `87` 条，本节抽取 `30` 条。

### 1. `replace_attribute:14`

- 负例类型：`replace_attribute`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："A small tiled bathroom stall with a black toilet seat."
- 正描述 2："A small tiled bathroom stall with a black toilet seat."
- 负描述："A small tiled bathroom stall with a white toilet seat."
- 自动来源：`None` / null
- 正确片段：""
- 错误片段：""
- 正确片段 token：IDs `[]`；pieces `[]`；decode ""
- 错误片段 token：IDs `[]`；pieces `[]`；decode ""
- 自动分类：`ambiguous_source`
- 来源规则："equal_character_and_token_distance_scores"
- 失败原因："equal_character_and_token_distance_scores"
- Token 边界提示：[]

### 2. `replace_attribute:619`

- 负例类型：`replace_attribute`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："A photo of a person and his partner on a bed"
- 正描述 2："A photo of a person along with another person on a bed."
- 负描述："A photo of three people on a bed."
- 自动来源：`None` / null
- 正确片段：""
- 错误片段：""
- 正确片段 token：IDs `[]`；pieces `[]`；decode ""
- 错误片段 token：IDs `[]`；pieces `[]`；decode ""
- 自动分类：`ambiguous_source`
- 来源规则："character_and_token_distance_rankings_conflict"
- 失败原因："character_and_token_distance_rankings_conflict"
- Token 边界提示：[]

### 3. `replace_attribute:642`

- 负例类型：`replace_attribute`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："A fire hydrant is decorated with an American flag design."
- 正描述 2："The American flag design is adorned on the fire hydrant."
- 负描述："An undecorated fire hydrant is standing on the street."
- 自动来源：`None` / null
- 正确片段：""
- 错误片段：""
- 正确片段 token：IDs `[]`；pieces `[]`；decode ""
- 错误片段 token：IDs `[]`；pieces `[]`；decode ""
- 自动分类：`ambiguous_source`
- 来源规则："character_and_token_distance_rankings_conflict"
- 失败原因："character_and_token_distance_rankings_conflict"
- Token 边界提示：[]

### 4. `replace_object:606`

- 负例类型：`replace_object`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："a woman with her luggage at a train station"
- 正描述 2："A woman with her luggage is located at a train station."
- 负描述："A man with his luggage at a train station."
- 自动来源：`None` / null
- 正确片段：""
- 错误片段：""
- 正确片段 token：IDs `[]`；pieces `[]`；decode ""
- 错误片段 token：IDs `[]`；pieces `[]`；decode ""
- 自动分类：`ambiguous_source`
- 来源规则："character_and_token_distance_rankings_conflict"
- 失败原因："character_and_token_distance_rankings_conflict"
- Token 边界提示：[]

### 5. `replace_relation:1222`

- 负例类型：`replace_relation`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："Two dishes holding a bunch of vegetables and fruit"
- 正描述 2："Two plates containing an assortment of fruits and vegetables."
- 负描述："Two dishes that are empty are on the table."
- 自动来源：`None` / null
- 正确片段：""
- 错误片段：""
- 正确片段 token：IDs `[]`；pieces `[]`；decode ""
- 错误片段 token：IDs `[]`；pieces `[]`；decode ""
- 自动分类：`ambiguous_source`
- 来源规则："character_and_token_distance_rankings_conflict"
- 失败原因："character_and_token_distance_rankings_conflict"
- Token 边界提示：[]

### 6. `replace_relation:24`

- 负例类型：`replace_relation`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："a cat that is looking out the window"
- 正描述 2："The cat is positioned in front of the window and is looking out."
- 负描述："A cat is sleeping on the window sill."
- 自动来源：`None` / null
- 正确片段：""
- 错误片段：""
- 正确片段 token：IDs `[]`；pieces `[]`；decode ""
- 错误片段 token：IDs `[]`；pieces `[]`；decode ""
- 自动分类：`ambiguous_source`
- 来源规则："character_and_token_distance_rankings_conflict"
- 失败原因："character_and_token_distance_rankings_conflict"
- Token 边界提示：[]

### 7. `replace_relation:243`

- 负例类型：`replace_relation`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："A dell inspiron laptop is sitting on a desk.."
- 正描述 2："A dell inspiron laptop is situated on a desk."
- 负描述："A dell inspiron laptop is lying on a desk."
- 自动来源：`None` / null
- 正确片段：""
- 错误片段：""
- 正确片段 token：IDs `[]`；pieces `[]`；decode ""
- 错误片段 token：IDs `[]`；pieces `[]`；decode ""
- 自动分类：`ambiguous_source`
- 来源规则："character_and_token_distance_rankings_conflict"
- 失败原因："character_and_token_distance_rankings_conflict"
- Token 边界提示：[]

### 8. `replace_relation:246`

- 负例类型：`replace_relation`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："A small boat is beached on the shore."
- 正描述 2："The small boat is resting on the shore."
- 负描述："A small boat is floating in the water."
- 自动来源：`None` / null
- 正确片段：""
- 错误片段：""
- 正确片段 token：IDs `[]`；pieces `[]`；decode ""
- 错误片段 token：IDs `[]`；pieces `[]`；decode ""
- 自动分类：`ambiguous_source`
- 来源规则："character_and_token_distance_rankings_conflict"
- 失败原因："character_and_token_distance_rankings_conflict"
- Token 边界提示：[]

### 9. `replace_relation:341`

- 负例类型：`replace_relation`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："Several surfboards standing in a row on the beach"
- 正描述 2："Several surfboards are lined up in a row on the beach."
- 负描述："Several surfboards lying in a row on the beach."
- 自动来源：`None` / null
- 正确片段：""
- 错误片段：""
- 正确片段 token：IDs `[]`；pieces `[]`；decode ""
- 错误片段 token：IDs `[]`；pieces `[]`；decode ""
- 自动分类：`ambiguous_source`
- 来源规则："character_and_token_distance_rankings_conflict"
- 失败原因："character_and_token_distance_rankings_conflict"
- Token 边界提示：[]

### 10. `replace_relation:40`

- 负例类型：`replace_relation`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："a close up of an oven with food cooking on top"
- 正描述 2："A close up of an oven with food cooking at the top."
- 负描述："A close up of an oven with food cooking inside."
- 自动来源：`None` / null
- 正确片段：""
- 错误片段：""
- 正确片段 token：IDs `[]`；pieces `[]`；decode ""
- 错误片段 token：IDs `[]`；pieces `[]`；decode ""
- 自动分类：`ambiguous_source`
- 来源规则："character_and_token_distance_rankings_conflict"
- 失败原因："character_and_token_distance_rankings_conflict"
- Token 边界提示：[]

### 11. `replace_relation:450`

- 负例类型：`replace_relation`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："A row of white toilets sitting on top of a dirt ground."
- 正描述 2："A row of white toilets sits on the dirt ground."
- 负描述："A row of white toilets embedded in a dirt ground."
- 自动来源：`None` / null
- 正确片段：""
- 错误片段：""
- 正确片段 token：IDs `[]`；pieces `[]`；decode ""
- 错误片段 token：IDs `[]`；pieces `[]`；decode ""
- 自动分类：`ambiguous_source`
- 来源规则："character_and_token_distance_rankings_conflict"
- 失败原因："character_and_token_distance_rankings_conflict"
- Token 边界提示：[]

### 12. `replace_relation:610`

- 负例类型：`replace_relation`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："Two women sit next to each other on a park bench."
- 正描述 2："Two women are seated adjacent to one another on a park bench."
- 负描述："Two women are standing across from each other in the park."
- 自动来源：`None` / null
- 正确片段：""
- 错误片段：""
- 正确片段 token：IDs `[]`；pieces `[]`；decode ""
- 错误片段 token：IDs `[]`；pieces `[]`；decode ""
- 自动分类：`ambiguous_source`
- 来源规则："character_and_token_distance_rankings_conflict"
- 失败原因："character_and_token_distance_rankings_conflict"
- Token 边界提示：[]

### 13. `replace_relation:746`

- 负例类型：`replace_relation`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："A highway filled with lots of traffic and buses."
- 正描述 2："A highway with a high volume of traffic and buses."
- 负描述："A highway empty of traffic and buses."
- 自动来源：`None` / null
- 正确片段：""
- 错误片段：""
- 正确片段 token：IDs `[]`；pieces `[]`；decode ""
- 错误片段 token：IDs `[]`；pieces `[]`；decode ""
- 自动分类：`ambiguous_source`
- 来源规则："character_and_token_distance_rankings_conflict"
- 失败原因："character_and_token_distance_rankings_conflict"
- Token 边界提示：[]

### 14. `replace_relation:932`

- 负例类型：`replace_relation`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："A young child flying a colorful kite on top of a sidewalk."
- 正描述 2："A young child flying a colorful kite atop a sidewalk."
- 负描述："A young child running with a colorful kite on a sidewalk."
- 自动来源：`None` / null
- 正确片段：""
- 错误片段：""
- 正确片段 token：IDs `[]`；pieces `[]`；decode ""
- 错误片段 token：IDs `[]`；pieces `[]`；decode ""
- 自动分类：`ambiguous_source`
- 来源规则："character_and_token_distance_rankings_conflict"
- 失败原因："character_and_token_distance_rankings_conflict"
- Token 边界提示：[]

### 15. `swap_atribute:117`

- 负例类型：`swap_atribute`
- 阶段三范围：`formal`；certifying formal：`False`
- 正描述 1："Group of people play video games at bestbuy"
- 正描述 2："At best buy, group of people are playing video games."
- 负描述："Video games play a group of people at Best Buy."
- 自动来源：`None` / null
- 正确片段：""
- 错误片段：""
- 正确片段 token：IDs `[]`；pieces `[]`；decode ""
- 错误片段 token：IDs `[]`；pieces `[]`；decode ""
- 自动分类：`ambiguous_source`
- 来源规则："character_and_token_distance_rankings_conflict"
- 失败原因："character_and_token_distance_rankings_conflict"
- Token 边界提示：[]

### 16. `swap_atribute:297`

- 负例类型：`swap_atribute`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："two teddy bear on the garden with some decorations"
- 正描述 2："The teddy bears are on the garden with some decorations."
- 负描述："Some teddy bears on the garden with two decorations."
- 自动来源：`None` / null
- 正确片段：""
- 错误片段：""
- 正确片段 token：IDs `[]`；pieces `[]`；decode ""
- 错误片段 token：IDs `[]`；pieces `[]`；decode ""
- 自动分类：`ambiguous_source`
- 来源规则："character_and_token_distance_rankings_conflict"
- 失败原因："character_and_token_distance_rankings_conflict"
- Token 边界提示：[]

### 17. `swap_atribute:303`

- 负例类型：`swap_atribute`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："A person falling asleep next to another person, who are both sitting down."
- 正描述 2："A person is sitting next to another person, both of whom are falling asleep while sitting down."
- 负描述："A person sitting down next to another person, who are both falling asleep."
- 自动来源：`None` / null
- 正确片段：""
- 错误片段：""
- 正确片段 token：IDs `[]`；pieces `[]`；decode ""
- 错误片段 token：IDs `[]`；pieces `[]`；decode ""
- 自动分类：`ambiguous_source`
- 来源规则："character_and_token_distance_rankings_conflict"
- 失败原因："character_and_token_distance_rankings_conflict"
- Token 边界提示：[]

### 18. `swap_atribute:340`

- 负例类型：`swap_atribute`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："A person with blue jersey holding a baseball bat."
- 正描述 2："A person with a blue jersey is holding a baseball bat."
- 负描述："A person with a baseball jersey holding a blue bat."
- 自动来源：`None` / null
- 正确片段：""
- 错误片段：""
- 正确片段 token：IDs `[]`；pieces `[]`；decode ""
- 错误片段 token：IDs `[]`；pieces `[]`；decode ""
- 自动分类：`ambiguous_source`
- 来源规则："character_and_token_distance_rankings_conflict"
- 失败原因："character_and_token_distance_rankings_conflict"
- Token 边界提示：[]

### 19. `swap_atribute:352`

- 负例类型：`swap_atribute`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："a white cake is by a bunch of flowers"
- 正描述 2："A white cake is positioned beside a bunch of flowers."
- 负描述："A bunch of cakes are by a white flower."
- 自动来源：`None` / null
- 正确片段：""
- 错误片段：""
- 正确片段 token：IDs `[]`；pieces `[]`；decode ""
- 错误片段 token：IDs `[]`；pieces `[]`；decode ""
- 自动分类：`ambiguous_source`
- 来源规则："character_and_token_distance_rankings_conflict"
- 失败原因："character_and_token_distance_rankings_conflict"
- Token 边界提示：[]

### 20. `swap_atribute:376`

- 负例类型：`swap_atribute`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："An old doctors office with two windows with curatins."
- 正描述 2："An old doctor's office with two windows, each with curtains."
- 负描述："A two-doored doctor's office with old windows and curtains."
- 自动来源：`None` / null
- 正确片段：""
- 错误片段：""
- 正确片段 token：IDs `[]`；pieces `[]`；decode ""
- 错误片段 token：IDs `[]`；pieces `[]`；decode ""
- 自动分类：`ambiguous_source`
- 来源规则："character_and_token_distance_rankings_conflict"
- 失败原因："character_and_token_distance_rankings_conflict"
- Token 边界提示：[]

### 21. `swap_atribute:450`

- 负例类型：`swap_atribute`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："This boat has docked next to a wooden pier"
- 正描述 2："The wooden pier is adjacent to the docked boat."
- 负描述："A wooden boat is not docked next a pier."
- 自动来源：`None` / null
- 正确片段：""
- 错误片段：""
- 正确片段 token：IDs `[]`；pieces `[]`；decode ""
- 错误片段 token：IDs `[]`；pieces `[]`；decode ""
- 自动分类：`ambiguous_source`
- 来源规则："character_and_token_distance_rankings_conflict"
- 失败原因："character_and_token_distance_rankings_conflict"
- Token 边界提示：[]

### 22. `swap_atribute:455`

- 负例类型：`swap_atribute`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："people ride their motorcycles beside some cars, passing by an empty street with stores and apartment buildings"
- 正描述 2："Some cars are beside people who are riding their motorcycles, passing by an empty street with stores and apartment buildings."
- 负描述："people do not ride their cars beside some motorcycles, passing by an empty street with stores and apartment buildings."
- 自动来源：`None` / null
- 正确片段：""
- 错误片段：""
- 正确片段 token：IDs `[]`；pieces `[]`；decode ""
- 错误片段 token：IDs `[]`；pieces `[]`；decode ""
- 自动分类：`ambiguous_source`
- 来源规则："character_and_token_distance_rankings_conflict"
- 失败原因："character_and_token_distance_rankings_conflict"
- Token 边界提示：[]

### 23. `swap_atribute:473`

- 负例类型：`swap_atribute`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："A green netted bed in a light filled bedroom."
- 正描述 2："A light-filled bedroom with a green netted bed."
- 负描述："A light filled netted bed in a green bedroom."
- 自动来源：`None` / null
- 正确片段：""
- 错误片段：""
- 正确片段 token：IDs `[]`；pieces `[]`；decode ""
- 错误片段 token：IDs `[]`；pieces `[]`；decode ""
- 自动分类：`ambiguous_source`
- 来源规则："character_and_token_distance_rankings_conflict"
- 失败原因："character_and_token_distance_rankings_conflict"
- Token 边界提示：[]

### 24. `swap_atribute:481`

- 负例类型：`swap_atribute`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："A cat is sitting on a bright orange chair."
- 正描述 2："The bright orange chair is positioned beneath the cat."
- 负描述："A bright orange cat is sitting on a chair."
- 自动来源：`None` / null
- 正确片段：""
- 错误片段：""
- 正确片段 token：IDs `[]`；pieces `[]`；decode ""
- 错误片段 token：IDs `[]`；pieces `[]`；decode ""
- 自动分类：`ambiguous_source`
- 来源规则："character_and_token_distance_rankings_conflict"
- 失败原因："character_and_token_distance_rankings_conflict"
- Token 边界提示：[]

### 25. `swap_atribute:597`

- 负例类型：`swap_atribute`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："Several middle eastern looking stickers decorate a black briefcase."
- 正描述 2："Several stickers with a Middle Eastern appearance adorn a black briefcase."
- 负描述："Several black stickers decorate a middle eastern looking briefcase."
- 自动来源：`None` / null
- 正确片段：""
- 错误片段：""
- 正确片段 token：IDs `[]`；pieces `[]`；decode ""
- 错误片段 token：IDs `[]`；pieces `[]`；decode ""
- 自动分类：`ambiguous_source`
- 来源规则："character_and_token_distance_rankings_conflict"
- 失败原因："character_and_token_distance_rankings_conflict"
- Token 边界提示：[]

### 26. `swap_atribute:652`

- 负例类型：`swap_atribute`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："Black and White cat laying down in dead leaves."
- 正描述 2："In the dead leaves lies the black and white cat."
- 负描述："Dead cat laying down in black and white leaves."
- 自动来源：`None` / null
- 正确片段：""
- 错误片段：""
- 正确片段 token：IDs `[]`；pieces `[]`；decode ""
- 错误片段 token：IDs `[]`；pieces `[]`；decode ""
- 自动分类：`ambiguous_source`
- 来源规则："character_and_token_distance_rankings_conflict"
- 失败原因："character_and_token_distance_rankings_conflict"
- Token 边界提示：[]

### 27. `swap_object:120`

- 负例类型：`swap_object`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："A light that is sitting underneath a umbrella."
- 正描述 2："The umbrella is positioned above the light."
- 负描述："An umbrella that is sitting underneath a light."
- 自动来源：`None` / null
- 正确片段：""
- 错误片段：""
- 正确片段 token：IDs `[]`；pieces `[]`；decode ""
- 错误片段 token：IDs `[]`；pieces `[]`；decode ""
- 自动分类：`ambiguous_source`
- 来源规则："character_and_token_distance_rankings_conflict"
- 失败原因："character_and_token_distance_rankings_conflict"
- Token 边界提示：[]

### 28. `swap_object:179`

- 负例类型：`swap_object`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："A person holds a carrot in their right hand with a beverage in the other."
- 正描述 2："The person holds a beverage in their left hand and a carrot in their other hand."
- 负描述："A person holds a beverage in their right hand with a carrot in the other."
- 自动来源：`None` / null
- 正确片段：""
- 错误片段：""
- 正确片段 token：IDs `[]`；pieces `[]`；decode ""
- 错误片段 token：IDs `[]`；pieces `[]`；decode ""
- 自动分类：`ambiguous_source`
- 来源规则："character_and_token_distance_rankings_conflict"
- 失败原因："character_and_token_distance_rankings_conflict"
- Token 边界提示：[]

### 29. `swap_object:64`

- 负例类型：`swap_object`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："A person holding a fork and reaching for a slice of pizza."
- 正描述 2："A person is reaching for a pizza slice while holding a fork."
- 负描述："A person holding a slice of pizza and reaching for a fork."
- 自动来源：`None` / null
- 正确片段：""
- 错误片段：""
- 正确片段 token：IDs `[]`；pieces `[]`；decode ""
- 错误片段 token：IDs `[]`；pieces `[]`；decode ""
- 自动分类：`ambiguous_source`
- 来源规则："character_and_token_distance_rankings_conflict"
- 失败原因："character_and_token_distance_rankings_conflict"
- Token 边界提示：[]

### 30. `swap_object:95`

- 负例类型：`swap_object`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："a person standing on cement lift their leg over a brief case"
- 正描述 2："A person elevates their leg over a briefcase while standing on a cement."
- 负描述："a person standing on a briefcase lifts their leg over cement."
- 自动来源：`None` / null
- 正确片段：""
- 错误片段：""
- 正确片段 token：IDs `[]`；pieces `[]`；decode ""
- 错误片段 token：IDs `[]`；pieces `[]`；decode ""
- 自动分类：`ambiguous_source`
- 来源规则："character_and_token_distance_rankings_conflict"
- 失败原因："character_and_token_distance_rankings_conflict"
- Token 边界提示：[]

## 复杂编辑

候选 `2044` 条，本节抽取 `30` 条。

### 1. `replace_attribute:339`

- 负例类型：`replace_attribute`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："a child wearing a hat is holding a pizza box with pizza inside."
- 正描述 2："A child holding a pizza box containing pizza is wearing a hat."
- 负描述："A hatless child is holding a pizza box with pizza inside."
- 自动来源：`positive_1` / "a child wearing a hat is holding a pizza box with pizza inside."
- 正确片段："a child wearing a hat"
- 错误片段："A hatless child"
- 正确片段 token：IDs `[100, 6109, 796, 370, 350, 299, 429, 314]`；pieces `["a", "Ġchild", "Ġwe", "ar", "ing", "Ġa", "Ġh", "at"]`；decode "a child wearing a hat"
- 错误片段 token：IDs `[68, 429, 314, 5062, 6109]`；pieces `["A", "Ġh", "at", "less", "Ġchild"]`；decode "A hatless child"
- 自动分类：`complex_edit`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因："non_contiguous_edit_blocks=2"
- Token 边界提示：[]

### 2. `replace_attribute:60`

- 负例类型：`replace_attribute`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："A person holding a red book in her hand while sitting on a bed. "
- 正描述 2："A person is sitting on a bed while holding a red book in her hand."
- 负描述："A person holding a blue book in her hand while sitting on a bed."
- 自动来源：`positive_1` / "A person holding a red book in her hand while sitting on a bed. "
- 正确片段："red book in her hand while sitting on a bed. "
- 错误片段："blue book in her hand while sitting on a bed."
- 正确片段 token：IDs `[5534, 2961, 353, 2833, 3319, 3052, 5305, 2912, 619, 299, 363, 382, 49, 256]`；pieces `["Ġred", "Ġbook", "Ġin", "Ġher", "Ġhand", "Ġwhile", "Ġsit", "ting", "Ġon", "Ġa", "Ġb", "ed", ".", "Ġ"]`；decode " red book in her hand while sitting on a bed. "
- 错误片段 token：IDs `[4300, 2961, 353, 2833, 3319, 3052, 5305, 2912, 619, 299, 363, 382, 49]`；pieces `["Ġblue", "Ġbook", "Ġin", "Ġher", "Ġhand", "Ġwhile", "Ġsit", "ting", "Ġon", "Ġa", "Ġb", "ed", "."]`；decode " blue book in her hand while sitting on a bed."
- 自动分类：`complex_edit`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因："obvious_rewrite_by_fixed_coverage_rule"
- Token 边界提示：[]

### 3. `replace_attribute:692`

- 负例类型：`replace_attribute`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："Display for bananas with a euro money sign"
- 正描述 2："The display for bananas along with a euro money sign."
- 负描述："Display for bananas with a dollar money sign."
- 自动来源：`positive_1` / "Display for bananas with a euro money sign"
- 正确片段："euro money sign"
- 错误片段："dollar money sign."
- 正确片段 token：IDs `[413, 5399, 351, 1634, 124, 2185]`；pieces `["Ġe", "uro", "Ġm", "one", "y", "Ġsign"]`；decode " euro money sign"
- 错误片段 token：IDs `[373, 6132, 370, 351, 1634, 124, 2185, 49]`；pieces `["Ġd", "oll", "ar", "Ġm", "one", "y", "Ġsign", "."]`；decode " dollar money sign."
- 自动分类：`complex_edit`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因："non_contiguous_edit_blocks=2"
- Token 边界提示：[]

### 4. `replace_attribute:98`

- 负例类型：`replace_attribute`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："A person in uniform riding a horse by a fence"
- 正描述 2："A person wearing uniform is riding a horse near a fence."
- 负描述："A person in casual clothes riding a horse by a fence."
- 自动来源：`positive_1` / "A person in uniform riding a horse by a fence"
- 正确片段："uniform riding a horse by a fence"
- 错误片段："casual clothes riding a horse by a fence."
- 正确片段 token：IDs `[1406, 507, 5713, 757, 460, 350, 299, 429, 336, 573, 769, 299, 341, 944]`；pieces `["Ġun", "if", "orm", "Ġr", "id", "ing", "Ġa", "Ġh", "or", "se", "Ġby", "Ġa", "Ġf", "ence"]`；decode " uniform riding a horse by a fence"
- 错误片段 token：IDs `[317, 390, 1885, 1658, 593, 2470, 757, 460, 350, 299, 429, 336, 573, 769, 299, 341, 944, 49]`；pieces `["Ġc", "as", "ual", "Ġcl", "ot", "hes", "Ġr", "id", "ing", "Ġa", "Ġh", "or", "se", "Ġby", "Ġa", "Ġf", "ence", "."]`；decode " casual clothes riding a horse by a fence."
- 自动分类：`complex_edit`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因："non_contiguous_edit_blocks=2;obvious_rewrite_by_fixed_coverage_rule"
- Token 边界提示：[]

### 5. `replace_object:1359`

- 负例类型：`replace_object`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："a tray of food on a wooden table"
- 正描述 2："A wooden table has a tray of food on it."
- 负描述："A tray of books on a wooden table."
- 自动来源：`positive_1` / "a tray of food on a wooden table"
- 正确片段："a tray of food on a wooden table"
- 错误片段："A tray of books on a wooden table."
- 正确片段 token：IDs `[100, 1946, 124, 354, 341, 2166, 619, 299, 339, 2166, 327, 2630]`；pieces `["a", "Ġtra", "y", "Ġof", "Ġf", "ood", "Ġon", "Ġa", "Ġw", "ood", "en", "Ġtable"]`；decode "a tray of food on a wooden table"
- 错误片段 token：IDs `[68, 1946, 124, 354, 5826, 619, 299, 339, 2166, 327, 2630, 49]`；pieces `["A", "Ġtra", "y", "Ġof", "Ġbooks", "Ġon", "Ġa", "Ġw", "ood", "en", "Ġtable", "."]`；decode "A tray of books on a wooden table."
- 自动分类：`complex_edit`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因："non_contiguous_edit_blocks=3;obvious_rewrite_by_fixed_coverage_rule"
- Token 边界提示：[]

### 6. `replace_object:1406`

- 负例类型：`replace_object`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："A child holds a toothbrush halfway out of their mouth while brushing their teeth."
- 正描述 2："A child is brushing their teeth, holding a toothbrush halfway out of their mouth."
- 负描述："An elderly woman holds a toothbrush halfway out of her mouth while brushing her teeth."
- 自动来源：`positive_1` / "A child holds a toothbrush halfway out of their mouth while brushing their teeth."
- 正确片段：" child holds a toothbrush halfway out of their mouth while brushing thei"
- 错误片段："n elderly woman holds a toothbrush halfway out of her mouth while brushing he"
- 正确片段 token：IDs `[68, 6109, 429, 500, 1881, 299, 364, 114, 495, 101, 117, 4923, 429, 352, 105, 5054, 1695, 354, 1635, 351, 326, 495, 3052, 3461, 4923, 350, 1635]`；pieces `["A", "Ġchild", "Ġh", "ol", "ds", "Ġa", "Ġto", "o", "th", "b", "r", "ush", "Ġh", "al", "f", "way", "Ġout", "Ġof", "Ġtheir", "Ġm", "ou", "th", "Ġwhile", "Ġbr", "ush", "ing", "Ġtheir"]`；decode "A child holds a toothbrush halfway out of their mouth while brushing their"
- 错误片段 token：IDs `[5799, 413, 674, 311, 542, 339, 444, 325, 429, 500, 1881, 299, 364, 114, 495, 101, 117, 4923, 429, 352, 105, 5054, 1695, 354, 2833, 351, 326, 495, 3052, 3461, 4923, 350, 2833]`；pieces `["An", "Ġe", "ld", "er", "ly", "Ġw", "om", "an", "Ġh", "ol", "ds", "Ġa", "Ġto", "o", "th", "b", "r", "ush", "Ġh", "al", "f", "way", "Ġout", "Ġof", "Ġher", "Ġm", "ou", "th", "Ġwhile", "Ġbr", "ush", "ing", "Ġher"]`；decode "An elderly woman holds a toothbrush halfway out of her mouth while brushing her"
- 自动分类：`complex_edit`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因："non_contiguous_edit_blocks=3;obvious_rewrite_by_fixed_coverage_rule"
- Token 边界提示：[]

### 7. `replace_object:1506`

- 负例类型：`replace_object`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："A person stands and shows his tie off."
- 正描述 2："A person stands, displaying their tie."
- 负描述："A woman stands and shows her tie off."
- 自动来源：`positive_1` / "A person stands and shows his tie off."
- 正确片段："person stands and shows his"
- 错误片段："woman stands and shows her"
- 正确片段 token：IDs `[2198, 2823, 118, 376, 1128, 3032, 2049]`；pieces `["Ġperson", "Ġstand", "s", "Ġand", "Ġsh", "ows", "Ġhis"]`；decode " person stands and shows his"
- 错误片段 token：IDs `[339, 444, 325, 2823, 118, 376, 1128, 3032, 2833]`；pieces `["Ġw", "om", "an", "Ġstand", "s", "Ġand", "Ġsh", "ows", "Ġher"]`；decode " woman stands and shows her"
- 自动分类：`complex_edit`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因："non_contiguous_edit_blocks=2"
- Token 边界提示：[]

### 8. `replace_object:1588`

- 负例类型：`replace_object`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："a surfing instructor teaches students with surfboards on a beach in front of large hotel buildings."
- 正描述 2："in front of large hotel buildings, a surfing instructor on a beach instructs students with surfboards."
- 负描述："A yoga instructor leads students with yoga mats on a beach in front of large hotel buildings."
- 自动来源：`positive_1` / "a surfing instructor teaches students with surfboards on a beach in front of large hotel buildings."
- 正确片段："a surfing instructor teaches students with surfboard"
- 错误片段："A yoga instructor leads students with yoga mat"
- 正确片段 token：IDs `[100, 3946, 105, 350, 2745, 2978, 336, 1047, 1545, 2470, 6176, 599, 3946, 105, 101, 114, 1433]`；pieces `["a", "Ġsur", "f", "ing", "Ġinst", "ruct", "or", "Ġte", "ac", "hes", "Ġstudents", "Ġwith", "Ġsur", "f", "b", "o", "ard"]`；decode "a surfing instructor teaches students with surfboard"
- 错误片段 token：IDs `[68, 385, 1172, 100, 2745, 2978, 336, 2624, 118, 6176, 599, 385, 1172, 100, 2366]`；pieces `["A", "Ġy", "og", "a", "Ġinst", "ruct", "or", "Ġlead", "s", "Ġstudents", "Ġwith", "Ġy", "og", "a", "Ġmat"]`；decode "A yoga instructor leads students with yoga mat"
- 自动分类：`complex_edit`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因："non_contiguous_edit_blocks=3"
- Token 边界提示：[]

### 9. `replace_object:640`

- 负例类型：`replace_object`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："The woman is looking at the elephant in amazement. "
- 正描述 2："The elephant is being looked at in amazement by the woman."
- 负描述："The child is looking at the elephant in amazement."
- 自动来源：`positive_1` / "The woman is looking at the elephant in amazement. "
- 正确片段："woman is looking at the elephant in amazement. "
- 错误片段："child is looking at the elephant in amazement."
- 正确片段 token：IDs `[339, 444, 325, 395, 3125, 1248, 309, 1905, 1601, 811, 353, 1746, 100, 125, 687, 425, 49, 256]`；pieces `["Ġw", "om", "an", "Ġis", "Ġlooking", "Ġat", "Ġthe", "Ġele", "ph", "ant", "Ġin", "Ġam", "a", "z", "em", "ent", ".", "Ġ"]`；decode " woman is looking at the elephant in amazement. "
- 错误片段 token：IDs `[6109, 395, 3125, 1248, 309, 1905, 1601, 811, 353, 1746, 100, 125, 687, 425, 49]`；pieces `["Ġchild", "Ġis", "Ġlooking", "Ġat", "Ġthe", "Ġele", "ph", "ant", "Ġin", "Ġam", "a", "z", "em", "ent", "."]`；decode " child is looking at the elephant in amazement."
- 自动分类：`complex_edit`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因："obvious_rewrite_by_fixed_coverage_rule"
- Token 边界提示：[]

### 10. `replace_object:823`

- 负例类型：`replace_object`
- 阶段三范围：`pilot`；certifying formal：`False`
- 正描述 1："there are three vases made of clay on a table"
- 正描述 2："The table has three vases made of clay positioned on it."
- 负描述："There are three vases made of glass on a table."
- 自动来源：`positive_1` / "there are three vases made of clay on a table"
- 正确片段："there are three vases made of clay on a table"
- 错误片段："There are three vases made of glass on a table."
- 正确片段 token：IDs `[119, 2503, 732, 3785, 603, 3164, 4303, 354, 1658, 655, 619, 299, 2630]`；pieces `["t", "here", "Ġare", "Ġthree", "Ġv", "ases", "Ġmade", "Ġof", "Ġcl", "ay", "Ġon", "Ġa", "Ġtable"]`；decode "there are three vases made of clay on a table"
- 错误片段 token：IDs `[750, 306, 732, 3785, 603, 3164, 4303, 354, 492, 111, 1388, 619, 299, 2630, 49]`；pieces `["The", "re", "Ġare", "Ġthree", "Ġv", "ases", "Ġmade", "Ġof", "Ġg", "l", "ass", "Ġon", "Ġa", "Ġtable", "."]`；decode "There are three vases made of glass on a table."
- 自动分类：`complex_edit`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因："non_contiguous_edit_blocks=3;obvious_rewrite_by_fixed_coverage_rule"
- Token 边界提示：[]

### 11. `replace_object:98`

- 负例类型：`replace_object`
- 阶段三范围：`pilot`；certifying formal：`False`
- 正描述 1："A man taking a picture of his reflection in a motorcycle mirror."
- 正描述 2："A man is taking a picture of himself as reflected by a motorcycle mirror."
- 负描述："A woman taking a picture of her reflection in a motorcycle mirror."
- 自动来源：`positive_1` / "A man taking a picture of his reflection in a motorcycle mirror."
- 正确片段："man taking a picture of his"
- 错误片段："woman taking a picture of her"
- 正确片段 token：IDs `[1672, 297, 5784, 299, 344, 2030, 745, 354, 2049]`；pieces `["Ġman", "Ġt", "aking", "Ġa", "Ġp", "ict", "ure", "Ġof", "Ġhis"]`；decode " man taking a picture of his"
- 错误片段 token：IDs `[339, 444, 325, 297, 5784, 299, 344, 2030, 745, 354, 2833]`；pieces `["Ġw", "om", "an", "Ġt", "aking", "Ġa", "Ġp", "ict", "ure", "Ġof", "Ġher"]`；decode " woman taking a picture of her"
- 自动分类：`complex_edit`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因："non_contiguous_edit_blocks=2"
- Token 边界提示：[]

### 12. `replace_relation:250`

- 负例类型：`replace_relation`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："a yellow book with a black pen on it"
- 正描述 2："A black pen rests on top of a yellow book."
- 负描述："A yellow book with a black pen next to it."
- 自动来源：`positive_1` / "a yellow book with a black pen on it"
- 正确片段："a yellow book with a black pen on it"
- 错误片段："A yellow book with a black pen next to it."
- 正确片段 token：IDs `[100, 385, 446, 1030, 2961, 599, 299, 2597, 1637, 344, 327, 619, 563]`；pieces `["a", "Ġy", "el", "low", "Ġbook", "Ġwith", "Ġa", "Ġbl", "ack", "Ġp", "en", "Ġon", "Ġit"]`；decode "a yellow book with a black pen on it"
- 错误片段 token：IDs `[68, 385, 446, 1030, 2961, 599, 299, 2597, 1637, 344, 327, 4658, 364, 563, 49]`；pieces `["A", "Ġy", "el", "low", "Ġbook", "Ġwith", "Ġa", "Ġbl", "ack", "Ġp", "en", "Ġnext", "Ġto", "Ġit", "."]`；decode "A yellow book with a black pen next to it."
- 自动分类：`complex_edit`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因："non_contiguous_edit_blocks=3;obvious_rewrite_by_fixed_coverage_rule"
- Token 边界提示：[]

### 13. `replace_relation:416`

- 负例类型：`replace_relation`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："A person holds a phone in a car with the window rolled down"
- 正描述 2："A phone is held by a person in a car with the window rolled down."
- 负描述："A person is outside a car with the window rolled down, holding a phone."
- 自动来源：`positive_1` / "A person holds a phone in a car with the window rolled down"
- 正确片段："holds a phone in a car with the window rolled down"
- 错误片段："is outside a car with the window rolled down, holding a phone."
- 正确片段 token：IDs `[429, 500, 1881, 299, 2001, 1634, 353, 299, 3751, 599, 309, 5472, 451, 1552, 111, 2003, 4076]`；pieces `["Ġh", "ol", "ds", "Ġa", "Ġph", "one", "Ġin", "Ġa", "Ġcar", "Ġwith", "Ġthe", "Ġwind", "ow", "Ġro", "l", "led", "Ġdown"]`；decode " holds a phone in a car with the window rolled down"
- 错误片段 token：IDs `[395, 1695, 118, 688, 299, 3751, 599, 309, 5472, 451, 1552, 111, 2003, 4076, 47, 429, 2569, 350, 299, 2001, 1634, 49]`；pieces `["Ġis", "Ġout", "s", "ide", "Ġa", "Ġcar", "Ġwith", "Ġthe", "Ġwind", "ow", "Ġro", "l", "led", "Ġdown", ",", "Ġh", "old", "ing", "Ġa", "Ġph", "one", "."]`；decode " is outside a car with the window rolled down, holding a phone."
- 自动分类：`complex_edit`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因："non_contiguous_edit_blocks=2;obvious_rewrite_by_fixed_coverage_rule"
- Token 边界提示：[]

### 14. `replace_relation:545`

- 负例类型：`replace_relation`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："Two adult men stands with a group of little league baseball players for a group photo"
- 正描述 2："For a group photo, two adult men stand with a group of little league baseball players."
- 负描述："Two adult men sit among a group of little league baseball players for a group photo."
- 自动来源：`positive_1` / "Two adult men stands with a group of little league baseball players for a group photo"
- 正确片段："tands with a group of little league baseball players for a group photo"
- 错误片段："it among a group of little league baseball players for a group photo."
- 正确片段 token：IDs `[2823, 118, 599, 299, 4592, 354, 406, 338, 5395, 848, 1163, 922, 4933, 101, 1266, 2865, 496, 503, 299, 4592, 2001, 593, 114]`；pieces `["Ġstand", "s", "Ġwith", "Ġa", "Ġgroup", "Ġof", "Ġl", "it", "tle", "Ġle", "ag", "ue", "Ġbase", "b", "all", "Ġplay", "ers", "Ġfor", "Ġa", "Ġgroup", "Ġph", "ot", "o"]`；decode " stands with a group of little league baseball players for a group photo"
- 错误片段 token：IDs `[5305, 1746, 1377, 299, 4592, 354, 406, 338, 5395, 848, 1163, 922, 4933, 101, 1266, 2865, 496, 503, 299, 4592, 2001, 593, 114, 49]`；pieces `["Ġsit", "Ġam", "ong", "Ġa", "Ġgroup", "Ġof", "Ġl", "it", "tle", "Ġle", "ag", "ue", "Ġbase", "b", "all", "Ġplay", "ers", "Ġfor", "Ġa", "Ġgroup", "Ġph", "ot", "o", "."]`；decode " sit among a group of little league baseball players for a group photo."
- 自动分类：`complex_edit`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因："non_contiguous_edit_blocks=2;obvious_rewrite_by_fixed_coverage_rule"
- Token 边界提示：[]

### 15. `replace_relation:741`

- 负例类型：`replace_relation`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："A person holding a phone in each hand and wearing a head set in front  of a Christmas tree."
- 正描述 2："In front of a Christmas tree, A person is holding a phone in each hand and wearing a headset."
- 负描述："A person dropping a phone in each hand and wearing a head set in front of a Christmas tree."
- 自动来源：`positive_1` / "A person holding a phone in each hand and wearing a head set in front  of a Christmas tree."
- 正确片段："holding a phone in each hand and wearing a head set in front "
- 错误片段："dropping a phone in each hand and wearing a head set in front"
- 正确片段 token：IDs `[429, 2569, 350, 299, 2001, 1634, 353, 1766, 3319, 376, 796, 370, 350, 299, 5308, 2139, 353, 341, 117, 3856, 256]`；pieces `["Ġh", "old", "ing", "Ġa", "Ġph", "one", "Ġin", "Ġeach", "Ġhand", "Ġand", "Ġwe", "ar", "ing", "Ġa", "Ġhead", "Ġset", "Ġin", "Ġf", "r", "ont", "Ġ"]`；decode " holding a phone in each hand and wearing a head set in front "
- 错误片段 token：IDs `[373, 393, 737, 350, 299, 2001, 1634, 353, 1766, 3319, 376, 796, 370, 350, 299, 5308, 2139, 353, 341, 117, 3856]`；pieces `["Ġd", "ro", "pp", "ing", "Ġa", "Ġph", "one", "Ġin", "Ġeach", "Ġhand", "Ġand", "Ġwe", "ar", "ing", "Ġa", "Ġhead", "Ġset", "Ġin", "Ġf", "r", "ont"]`；decode " dropping a phone in each hand and wearing a head set in front"
- 自动分类：`complex_edit`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因："obvious_rewrite_by_fixed_coverage_rule"
- Token 边界提示：[]

### 16. `swap_atribute:198`

- 负例类型：`swap_atribute`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："Two skateboarders trying to film a skateboard trick"
- 正描述 2："Two skateboarders are attempting to capture a skateboard trick on film."
- 负描述："A skateboarder trying to film two skateboard tricks."
- 自动来源：`positive_1` / "Two skateboarders trying to film a skateboard trick"
- 正确片段："Two skateboarders trying to film a skateboard trick"
- 错误片段："A skateboarder trying to film two skateboard tricks."
- 正确片段 token：IDs `[87, 122, 114, 2549, 557, 101, 114, 1433, 496, 3616, 364, 4552, 299, 2549, 557, 101, 114, 1433, 1144, 2437]`；pieces `["T", "w", "o", "Ġsk", "ate", "b", "o", "ard", "ers", "Ġtrying", "Ġto", "Ġfilm", "Ġa", "Ġsk", "ate", "b", "o", "ard", "Ġtr", "ick"]`；decode "Two skateboarders trying to film a skateboard trick"
- 错误片段 token：IDs `[68, 2549, 557, 101, 114, 1433, 311, 3616, 364, 4552, 2102, 2549, 557, 101, 114, 1433, 1144, 375, 1275, 49]`；pieces `["A", "Ġsk", "ate", "b", "o", "ard", "er", "Ġtrying", "Ġto", "Ġfilm", "Ġtwo", "Ġsk", "ate", "b", "o", "ard", "Ġtr", "ic", "ks", "."]`；decode "A skateboarder trying to film two skateboard tricks."
- 自动分类：`complex_edit`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因："non_contiguous_edit_blocks=3;obvious_rewrite_by_fixed_coverage_rule"
- Token 边界提示：[]

### 17. `swap_atribute:208`

- 负例类型：`swap_atribute`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："a black goat standing next to two white goats"
- 正描述 2："A black goat is positioned next to two white goats."
- 负描述："Two black goats standing next to a white goat."
- 自动来源：`positive_1` / "a black goat standing next to two white goats"
- 正确片段："a black goat standing next to two white goats"
- 错误片段："Two black goats standing next to a white goat."
- 正确片段 token：IDs `[100, 2597, 1637, 2379, 314, 2823, 350, 4658, 364, 2102, 654, 1078, 2379, 4585]`；pieces `["a", "Ġbl", "ack", "Ġgo", "at", "Ġstand", "ing", "Ġnext", "Ġto", "Ġtwo", "Ġwh", "ite", "Ġgo", "ats"]`；decode "a black goat standing next to two white goats"
- 错误片段 token：IDs `[87, 122, 114, 2597, 1637, 2379, 4585, 2823, 350, 4658, 364, 299, 654, 1078, 2379, 314, 49]`；pieces `["T", "w", "o", "Ġbl", "ack", "Ġgo", "ats", "Ġstand", "ing", "Ġnext", "Ġto", "Ġa", "Ġwh", "ite", "Ġgo", "at", "."]`；decode "Two black goats standing next to a white goat."
- 自动分类：`complex_edit`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因："non_contiguous_edit_blocks=4;word_order_change;obvious_rewrite_by_fixed_coverage_rule"
- Token 边界提示：[]

### 18. `swap_atribute:223`

- 负例类型：`swap_atribute`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："person  playing Nintendo Wii in font of business people in office"
- 正描述 2："The person is playing Nintendo Wii in front of the business people in the office."
- 负描述："Business people playing Nintendo Wii in front of a person in the office."
- 自动来源：`positive_2` / "The person is playing Nintendo Wii in front of the business people in the office."
- 正确片段："The person is playing Nintendo Wii in front of the business people"
- 错误片段："Business people playing Nintendo Wii in front of a person"
- 正确片段 token：IDs `[750, 2198, 395, 2865, 350, 1231, 806, 901, 114, 1004, 108, 108, 353, 341, 117, 3856, 354, 309, 2659, 2975]`；pieces `["The", "Ġperson", "Ġis", "Ġplay", "ing", "ĠN", "int", "end", "o", "ĠW", "i", "i", "Ġin", "Ġf", "r", "ont", "Ġof", "Ġthe", "Ġbusiness", "Ġpeople"]`；decode "The person is playing Nintendo Wii in front of the business people"
- 错误片段 token：IDs `[69, 832, 2447, 2975, 2865, 350, 1231, 806, 901, 114, 1004, 108, 108, 353, 341, 117, 3856, 354, 299, 2198]`；pieces `["B", "us", "iness", "Ġpeople", "Ġplay", "ing", "ĠN", "int", "end", "o", "ĠW", "i", "i", "Ġin", "Ġf", "r", "ont", "Ġof", "Ġa", "Ġperson"]`；decode "Business people playing Nintendo Wii in front of a person"
- 自动分类：`complex_edit`
- 来源规则："positive_2_pareto_dominates_character_and_token_distance"
- 失败原因："non_contiguous_edit_blocks=2;obvious_rewrite_by_fixed_coverage_rule"
- Token 边界提示：[]

### 19. `swap_atribute:23`

- 负例类型：`swap_atribute`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："Workers in fluorescent yellow jackets standing under a fluorescent orange umbrella."
- 正描述 2："The fluorescent orange umbrella is positioned above the workers who are standing in fluorescent yellow jackets."
- 负描述："Workers in fluorescent orange jackets standing under a fluorescent yellow umbrella."
- 自动来源：`positive_1` / "Workers in fluorescent yellow jackets standing under a fluorescent orange umbrella."
- 正确片段："yellow jackets standing under a fluorescent orange"
- 错误片段："orange jackets standing under a fluorescent yellow"
- 正确片段 token：IDs `[385, 446, 1030, 1315, 1637, 3391, 2823, 350, 1943, 299, 3687, 120, 114, 889, 5141, 522, 1285]`；pieces `["Ġy", "el", "low", "Ġj", "ack", "ets", "Ġstand", "ing", "Ġunder", "Ġa", "Ġfl", "u", "o", "res", "cent", "Ġor", "ange"]`；decode " yellow jackets standing under a fluorescent orange"
- 错误片段 token：IDs `[522, 1285, 1315, 1637, 3391, 2823, 350, 1943, 299, 3687, 120, 114, 889, 5141, 385, 446, 1030]`；pieces `["Ġor", "ange", "Ġj", "ack", "ets", "Ġstand", "ing", "Ġunder", "Ġa", "Ġfl", "u", "o", "res", "cent", "Ġy", "el", "low"]`；decode " orange jackets standing under a fluorescent yellow"
- 自动分类：`complex_edit`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因："non_contiguous_edit_blocks=2;word_order_change"
- Token 边界提示：[]

### 20. `swap_atribute:244`

- 负例类型：`swap_atribute`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："A Teddy bear sits on a floral patterned chair."
- 正描述 2："The floral patterned chair is positioned under the Teddy bear."
- 负描述："A floral patterned bear sits on a Teddy chair."
- 自动来源：`positive_2` / "The floral patterned chair is positioned under the Teddy bear."
- 正确片段："The floral patterned chair is positioned under the Teddy bea"
- 错误片段："A floral patterned bear sits on a Teddy chai"
- 正确片段 token：IDs `[750, 3687, 336, 352, 5335, 382, 890, 3709, 395, 2617, 1632, 382, 1943, 309, 527, 382, 103, 124, 600, 370]`；pieces `["The", "Ġfl", "or", "al", "Ġpattern", "ed", "Ġch", "air", "Ġis", "Ġpos", "ition", "ed", "Ġunder", "Ġthe", "ĠT", "ed", "d", "y", "Ġbe", "ar"]`；decode "The floral patterned chair is positioned under the Teddy bear"
- 错误片段 token：IDs `[68, 3687, 336, 352, 5335, 382, 600, 370, 316, 2163, 619, 299, 527, 382, 103, 124, 890, 3709]`；pieces `["A", "Ġfl", "or", "al", "Ġpattern", "ed", "Ġbe", "ar", "Ġs", "its", "Ġon", "Ġa", "ĠT", "ed", "d", "y", "Ġch", "air"]`；decode "A floral patterned bear sits on a Teddy chair"
- 自动分类：`complex_edit`
- 来源规则："positive_2_pareto_dominates_character_and_token_distance"
- 失败原因："non_contiguous_edit_blocks=3;obvious_rewrite_by_fixed_coverage_rule"
- Token 边界提示：[]

### 21. `swap_atribute:250`

- 负例类型：`swap_atribute`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："A group of different colored teddy bears sitting on top of a blue table."
- 正描述 2："A group of teddy bears of varying colors is positioned on top of a blue table."
- 负描述："A group of blue teddy bears sitting on top of a different colored table."
- 自动来源：`positive_1` / "A group of different colored teddy bears sitting on top of a blue table."
- 正确片段："different colored teddy bears sitting on top of a blue"
- 错误片段："blue teddy bears sitting on top of a different colored"
- 正确片段 token：IDs `[2301, 1683, 1239, 103, 297, 382, 103, 124, 600, 2546, 5305, 2912, 619, 2924, 354, 299, 4300]`；pieces `["Ġdifferent", "Ġcol", "ore", "d", "Ġt", "ed", "d", "y", "Ġbe", "ars", "Ġsit", "ting", "Ġon", "Ġtop", "Ġof", "Ġa", "Ġblue"]`；decode " different colored teddy bears sitting on top of a blue"
- 错误片段 token：IDs `[4300, 297, 382, 103, 124, 600, 2546, 5305, 2912, 619, 2924, 354, 299, 2301, 1683, 1239, 103]`；pieces `["Ġblue", "Ġt", "ed", "d", "y", "Ġbe", "ars", "Ġsit", "ting", "Ġon", "Ġtop", "Ġof", "Ġa", "Ġdifferent", "Ġcol", "ore", "d"]`；decode " blue teddy bears sitting on top of a different colored"
- 自动分类：`complex_edit`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因："non_contiguous_edit_blocks=2;word_order_change;obvious_rewrite_by_fixed_coverage_rule"
- Token 边界提示：[]

### 22. `swap_atribute:255`

- 负例类型：`swap_atribute`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："An elephant standing on rocks next to a wood bridge."
- 正描述 2："An elephant is positioned on rocks adjacent to a wooden bridge."
- 负描述："An elephant standing on a wood next to a rock bridge."
- 自动来源：`positive_1` / "An elephant standing on rocks next to a wood bridge."
- 正确片段："rocks next to a wood"
- 错误片段："a wood next to a rock"
- 正确片段 token：IDs `[1552, 892, 118, 4658, 364, 299, 339, 2166]`；pieces `["Ġro", "ck", "s", "Ġnext", "Ġto", "Ġa", "Ġw", "ood"]`；decode " rocks next to a wood"
- 错误片段 token：IDs `[299, 339, 2166, 4658, 364, 299, 1552, 892]`；pieces `["Ġa", "Ġw", "ood", "Ġnext", "Ġto", "Ġa", "Ġro", "ck"]`；decode " a wood next to a rock"
- 自动分类：`complex_edit`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因："non_contiguous_edit_blocks=2"
- Token 边界提示：[]

### 23. `swap_atribute:337`

- 负例类型：`swap_atribute`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："A group of young persons standing on top of a sandy beach."
- 正描述 2："A group of young persons is positioned on top of a sandy beach."
- 负描述："A group of sandy persons standing on top of a young beach."
- 自动来源：`positive_1` / "A group of young persons standing on top of a sandy beach."
- 正确片段："young persons standing on top of a sandy"
- 错误片段："sandy persons standing on top of a young"
- 正确片段 token：IDs `[401, 1685, 2198, 118, 2823, 350, 619, 2924, 354, 299, 316, 728, 124]`；pieces `["Ġyou", "ng", "Ġperson", "s", "Ġstand", "ing", "Ġon", "Ġtop", "Ġof", "Ġa", "Ġs", "and", "y"]`；decode " young persons standing on top of a sandy"
- 错误片段 token：IDs `[316, 728, 124, 2198, 118, 2823, 350, 619, 2924, 354, 299, 401, 1685]`；pieces `["Ġs", "and", "y", "Ġperson", "s", "Ġstand", "ing", "Ġon", "Ġtop", "Ġof", "Ġa", "Ġyou", "ng"]`；decode " sandy persons standing on top of a young"
- 自动分类：`complex_edit`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因："non_contiguous_edit_blocks=2;word_order_change;obvious_rewrite_by_fixed_coverage_rule"
- Token 边界提示：[]

### 24. `swap_atribute:357`

- 负例类型：`swap_atribute`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："A giraffe and two zebras in a dirt area next to fence."
- 正描述 2："In a dirt area adjacent to a fence, there is a giraffe and two zebras."
- 负描述："Two giraffes and a zebra in a dirt area next to fence."
- 自动来源：`positive_1` / "A giraffe and two zebras in a dirt area next to fence."
- 正确片段："A giraffe and two zebras"
- 错误片段："Two giraffes and a zebra"
- 正确片段 token：IDs `[68, 492, 108, 559, 1627, 104, 376, 2102, 3243, 3037, 117, 390]`；pieces `["A", "Ġg", "i", "ra", "ff", "e", "Ġand", "Ġtwo", "Ġz", "eb", "r", "as"]`；decode "A giraffe and two zebras"
- 错误片段 token：IDs `[87, 122, 114, 492, 108, 559, 1627, 329, 376, 299, 3243, 3037, 559]`；pieces `["T", "w", "o", "Ġg", "i", "ra", "ff", "es", "Ġand", "Ġa", "Ġz", "eb", "ra"]`；decode "Two giraffes and a zebra"
- 自动分类：`complex_edit`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因："non_contiguous_edit_blocks=2"
- Token 边界提示：[]

### 25. `swap_atribute:392`

- 负例类型：`swap_atribute`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："All of the cows are poking their heads out, eating some hay. "
- 正描述 2："The cows are positioned in such a way that their heads are poking out while they are eating some hay."
- 负描述："Some cows are poking their heads out, eating all of the hay."
- 自动来源：`positive_1` / "All of the cows are poking their heads out, eating some hay. "
- 正确片段："All of the cows are poking their heads out, eating some hay. "
- 错误片段："Some cows are poking their heads out, eating all of the hay."
- 正确片段 token：IDs `[68, 1989, 354, 309, 317, 3032, 732, 927, 1237, 1635, 5308, 118, 1695, 47, 413, 1807, 2104, 429, 655, 49, 256]`；pieces `["A", "ll", "Ġof", "Ġthe", "Ġc", "ows", "Ġare", "Ġpo", "king", "Ġtheir", "Ġhead", "s", "Ġout", ",", "Ġe", "ating", "Ġsome", "Ġh", "ay", ".", "Ġ"]`；decode "All of the cows are poking their heads out, eating some hay. "
- 错误片段 token：IDs `[86, 3219, 317, 3032, 732, 927, 1237, 1635, 5308, 118, 1695, 47, 413, 1807, 1650, 354, 309, 429, 655, 49]`；pieces `["S", "ome", "Ġc", "ows", "Ġare", "Ġpo", "king", "Ġtheir", "Ġhead", "s", "Ġout", ",", "Ġe", "ating", "Ġall", "Ġof", "Ġthe", "Ġh", "ay", "."]`；decode "Some cows are poking their heads out, eating all of the hay."
- 自动分类：`complex_edit`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因："non_contiguous_edit_blocks=2;word_order_change;obvious_rewrite_by_fixed_coverage_rule"
- Token 边界提示：[]

### 26. `swap_atribute:410`

- 负例类型：`swap_atribute`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："Two persons sitting on ledge looking at a cellphone."
- 正描述 2："Two persons are seated on a ledge, facing a cellphone."
- 负描述："A person sitting on a ledge looking at two cellphones."
- 自动来源：`positive_1` / "Two persons sitting on ledge looking at a cellphone."
- 正确片段："Two persons sitting on ledge looking at a cellphone"
- 错误片段："A person sitting on a ledge looking at two cellphones"
- 正确片段 token：IDs `[87, 122, 114, 2198, 118, 5305, 2912, 619, 848, 103, 583, 3125, 1248, 299, 317, 446, 823, 107, 1634]`；pieces `["T", "w", "o", "Ġperson", "s", "Ġsit", "ting", "Ġon", "Ġle", "d", "ge", "Ġlooking", "Ġat", "Ġa", "Ġc", "el", "lp", "h", "one"]`；decode "Two persons sitting on ledge looking at a cellphone"
- 错误片段 token：IDs `[68, 2198, 5305, 2912, 619, 299, 848, 103, 583, 3125, 1248, 2102, 317, 446, 823, 107, 310, 329]`；pieces `["A", "Ġperson", "Ġsit", "ting", "Ġon", "Ġa", "Ġle", "d", "ge", "Ġlooking", "Ġat", "Ġtwo", "Ġc", "el", "lp", "h", "on", "es"]`；decode "A person sitting on a ledge looking at two cellphones"
- 自动分类：`complex_edit`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因："non_contiguous_edit_blocks=3;obvious_rewrite_by_fixed_coverage_rule"
- Token 边界提示：[]

### 27. `swap_atribute:412`

- 负例类型：`swap_atribute`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："A large white bowl of many green apples."
- 正描述 2：" Many green apples in a bowl."
- 负描述："A green bowl of many large white apples."
- 自动来源：`positive_1` / "A large white bowl of many green apples."
- 正确片段："large white bowl of many green"
- 错误片段："green bowl of many large white"
- 正确片段 token：IDs `[2994, 654, 1078, 363, 451, 111, 354, 2547, 5921]`；pieces `["Ġlarge", "Ġwh", "ite", "Ġb", "ow", "l", "Ġof", "Ġmany", "Ġgreen"]`；decode " large white bowl of many green"
- 错误片段 token：IDs `[5921, 363, 451, 111, 354, 2547, 2994, 654, 1078]`；pieces `["Ġgreen", "Ġb", "ow", "l", "Ġof", "Ġmany", "Ġlarge", "Ġwh", "ite"]`；decode " green bowl of many large white"
- 自动分类：`complex_edit`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因："non_contiguous_edit_blocks=2;word_order_change"
- Token 边界提示：[]

### 28. `swap_atribute:443`

- 负例类型：`swap_atribute`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："a little black bird with a big colorful beak sitting on a branch"
- 正描述 2："A small black bird with a large, colorful beak perched on a branch."
- 负描述："a big colorful black bird with a little beak sitting on a branch"
- 自动来源：`positive_1` / "a little black bird with a big colorful beak sitting on a branch"
- 正确片段："little black bird with a big colorful"
- 错误片段："big colorful black bird with a little"
- 正确片段 token：IDs `[406, 338, 5395, 2597, 1637, 5231, 103, 599, 299, 363, 499, 4987, 1930]`；pieces `["Ġl", "it", "tle", "Ġbl", "ack", "Ġbir", "d", "Ġwith", "Ġa", "Ġb", "ig", "Ġcolor", "ful"]`；decode " little black bird with a big colorful"
- 错误片段 token：IDs `[363, 499, 4987, 1930, 2597, 1637, 5231, 103, 599, 299, 406, 338, 5395]`；pieces `["Ġb", "ig", "Ġcolor", "ful", "Ġbl", "ack", "Ġbir", "d", "Ġwith", "Ġa", "Ġl", "it", "tle"]`；decode " big colorful black bird with a little"
- 自动分类：`complex_edit`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因："non_contiguous_edit_blocks=2;word_order_change"
- Token 边界提示：[]

### 29. `swap_atribute:54`

- 负例类型：`swap_atribute`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："A little child kneeling down to pet two dogs on a leash."
- 正描述 2："A small child kneels to pet two leashed dogs."
- 负描述："Two children kneeling down to pet a little dog on a leash."
- 自动来源：`positive_1` / "A little child kneeling down to pet two dogs on a leash."
- 正确片段："A little child kneeling down to pet two dogs"
- 错误片段："Two children kneeling down to pet a little dog"
- 正确片段 token：IDs `[68, 406, 338, 5395, 6109, 914, 1763, 446, 350, 4076, 364, 344, 439, 2102, 1041, 4474]`；pieces `["A", "Ġl", "it", "tle", "Ġchild", "Ġk", "ne", "el", "ing", "Ġdown", "Ġto", "Ġp", "et", "Ġtwo", "Ġdo", "gs"]`；decode "A little child kneeling down to pet two dogs"
- 错误片段 token：IDs `[87, 122, 114, 6109, 3193, 914, 1763, 446, 350, 4076, 364, 344, 439, 299, 406, 338, 5395, 1041, 106]`；pieces `["T", "w", "o", "Ġchild", "ren", "Ġk", "ne", "el", "ing", "Ġdown", "Ġto", "Ġp", "et", "Ġa", "Ġl", "it", "tle", "Ġdo", "g"]`；decode "Two children kneeling down to pet a little dog"
- 自动分类：`complex_edit`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因："non_contiguous_edit_blocks=2;obvious_rewrite_by_fixed_coverage_rule"
- Token 边界提示：[]

### 30. `swap_object:55`

- 负例类型：`swap_object`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："A white faced clock with roman numerals surrounded by a painting."
- 正描述 2："The clock, with Roman numerals and a white face, is surrounded by a painting."
- 负描述："A painting with roman numerals surrounded by a white faced clock."
- 自动来源：`positive_1` / "A white faced clock with roman numerals surrounded by a painting."
- 正确片段："white faced clock with roman numerals surrounded by a painting"
- 错误片段："painting with roman numerals surrounded by a white faced clock"
- 正确片段 token：IDs `[654, 1078, 5875, 382, 4414, 892, 599, 256, 865, 325, 5636, 3293, 3946, 2383, 382, 769, 299, 5063, 2912]`；pieces `["Ġwh", "ite", "Ġfac", "ed", "Ġclo", "ck", "Ġwith", "Ġ", "rom", "an", "Ġnumer", "als", "Ġsur", "round", "ed", "Ġby", "Ġa", "Ġpain", "ting"]`；decode " white faced clock with roman numerals surrounded by a painting"
- 错误片段 token：IDs `[5063, 2912, 599, 256, 865, 325, 5636, 3293, 3946, 2383, 382, 769, 299, 654, 1078, 5875, 382, 4414, 892]`；pieces `["Ġpain", "ting", "Ġwith", "Ġ", "rom", "an", "Ġnumer", "als", "Ġsur", "round", "ed", "Ġby", "Ġa", "Ġwh", "ite", "Ġfac", "ed", "Ġclo", "ck"]`；decode " painting with roman numerals surrounded by a white faced clock"
- 自动分类：`complex_edit`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因："non_contiguous_edit_blocks=2;word_order_change;obvious_rewrite_by_fixed_coverage_rule"
- Token 边界提示：[]

## Tokenizer 问题

候选 `0` 条，本节抽取 `0` 条。

本类别没有可抽取样本。

## 负例类型：replace_attribute

候选 `788` 条，本节抽取 `30` 条。

### 1. `replace_attribute:100`

- 负例类型：`replace_attribute`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："A sidewalk scene with focus on a red bench."
- 正描述 2："A red bench is situated on a sidewalk."
- 负描述："A sidewalk scene with focus on a yellow bench."
- 自动来源：`positive_1` / "A sidewalk scene with focus on a red bench."
- 正确片段："red"
- 错误片段："yellow"
- 正确片段 token：IDs `[5534]`；pieces `["Ġred"]`；decode " red"
- 错误片段 token：IDs `[385, 446, 1030]`；pieces `["Ġy", "el", "low"]`；decode " yellow"
- 自动分类：`unique_alignment`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因：null
- Token 边界提示：[]

### 2. `replace_attribute:105`

- 负例类型：`replace_attribute`
- 阶段三范围：`pilot`；certifying formal：`False`
- 正描述 1："a large campaign trailer parked in a parking lot."
- 正描述 2："A huge campaign trailer is parked in a parking lot."
- 负描述："A small campaign trailer parked in a parking lot."
- 自动来源：`positive_1` / "a large campaign trailer parked in a parking lot."
- 正确片段："a large"
- 错误片段："A small"
- 正确片段 token：IDs `[100, 2994]`；pieces `["a", "Ġlarge"]`；decode "a large"
- 错误片段 token：IDs `[68, 3436]`；pieces `["A", "Ġsmall"]`；decode "A small"
- 自动分类：`unique_alignment`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因：null
- Token 边界提示：[]

### 3. `replace_attribute:117`

- 负例类型：`replace_attribute`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："Interior bathroom shot of a glass shower and white sink fixtures."
- 正描述 2："A photograph of the interior of a bathroom, featuring a glass shower and white sink fixtures."
- 负描述："Interior bathroom shot of a tiled shower and white sink fixtures."
- 自动来源：`positive_1` / "Interior bathroom shot of a glass shower and white sink fixtures."
- 正确片段："glass"
- 错误片段："tiled"
- 正确片段 token：IDs `[492, 111, 1388]`；pieces `["Ġg", "l", "ass"]`；decode " glass"
- 错误片段 token：IDs `[297, 4598]`；pieces `["Ġt", "iled"]`；decode " tiled"
- 自动分类：`unique_alignment`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因：null
- Token 边界提示：[]

### 4. `replace_attribute:13`

- 负例类型：`replace_attribute`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："A person wearing a hat while standing in front of a bathroom mirror."
- 正描述 2："A person standing in front of a bathroom mirror is wearing a hat."
- 负描述："A person removing a hat while standing in front of a bathroom mirror."
- 自动来源：`positive_1` / "A person wearing a hat while standing in front of a bathroom mirror."
- 正确片段："wear"
- 错误片段："remov"
- 正确片段 token：IDs `[796, 370, 350]`；pieces `["Ġwe", "ar", "ing"]`；decode " wearing"
- 错误片段 token：IDs `[2428, 114, 2828]`；pieces `["Ġrem", "o", "ving"]`；decode " removing"
- 自动分类：`unique_alignment`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因：null
- Token 边界提示：[]

### 5. `replace_attribute:158`

- 负例类型：`replace_attribute`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："An old blender and printer sitting on a table."
- 正描述 2："A printer and an old blender are positioned on top of the table."
- 负描述："A new blender and printer sitting on a table."
- 自动来源：`positive_1` / "An old blender and printer sitting on a table."
- 正确片段："n old"
- 错误片段：" new"
- 正确片段 token：IDs `[5799, 4797]`；pieces `["An", "Ġold"]`；decode "An old"
- 错误片段 token：IDs `[68, 1619]`；pieces `["A", "Ġnew"]`；decode "A new"
- 自动分类：`unique_alignment`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因：null
- Token 边界提示：[]

### 6. `replace_attribute:224`

- 负例类型：`replace_attribute`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："A person sitting on a wooden bench on a wall."
- 正描述 2："A person is sitting on a wooden bench that is positioned on a wall."
- 负描述："A person sitting on a stone bench on a wall."
- 自动来源：`positive_1` / "A person sitting on a wooden bench on a wall."
- 正确片段："wooden"
- 错误片段："stone"
- 正确片段 token：IDs `[339, 2166, 327]`；pieces `["Ġw", "ood", "en"]`；decode " wooden"
- 错误片段 token：IDs `[580, 1634]`；pieces `["Ġst", "one"]`；decode " stone"
- 自动分类：`unique_alignment`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因：null
- Token 边界提示：[]

### 7. `replace_attribute:230`

- 负例类型：`replace_attribute`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："A model in a blue and white dress sits for a photo. "
- 正描述 2："A person sitting in a white and blue dress is captured in a photograph."
- 负描述："A model in a red and white dress sits for a photo."
- 自动来源：`positive_1` / "A model in a blue and white dress sits for a photo. "
- 正确片段："blue and white dress sits for a photo. "
- 错误片段："red and white dress sits for a photo."
- 正确片段 token：IDs `[4300, 376, 654, 1078, 373, 1592, 316, 2163, 503, 299, 2001, 593, 114, 49, 256]`；pieces `["Ġblue", "Ġand", "Ġwh", "ite", "Ġd", "ress", "Ġs", "its", "Ġfor", "Ġa", "Ġph", "ot", "o", ".", "Ġ"]`；decode " blue and white dress sits for a photo. "
- 错误片段 token：IDs `[5534, 376, 654, 1078, 373, 1592, 316, 2163, 503, 299, 2001, 593, 114, 49]`；pieces `["Ġred", "Ġand", "Ġwh", "ite", "Ġd", "ress", "Ġs", "its", "Ġfor", "Ġa", "Ġph", "ot", "o", "."]`；decode " red and white dress sits for a photo."
- 自动分类：`complex_edit`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因："obvious_rewrite_by_fixed_coverage_rule"
- Token 边界提示：[]

### 8. `replace_attribute:251`

- 负例类型：`replace_attribute`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："A double parking meter on a pole with a bicycle rack."
- 正描述 2："A bicycle rack is positioned on a pole with a double parking meter."
- 负描述："A single parking meter on a pole with a bicycle rack."
- 自动来源：`positive_1` / "A double parking meter on a pole with a bicycle rack."
- 正确片段："doub"
- 错误片段："sing"
- 正确片段 token：IDs `[373, 326, 2129]`；pieces `["Ġd", "ou", "ble"]`；decode " double"
- 错误片段 token：IDs `[4486]`；pieces `["Ġsingle"]`；decode " single"
- 自动分类：`unique_alignment`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因：null
- Token 边界提示：[]

### 9. `replace_attribute:282`

- 负例类型：`replace_attribute`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："A person wearing a white shirt and tie standing in  a room."
- 正描述 2："A person standing in a room is wearing a white shirt along with a tie."
- 负描述："A person wearing a black shirt and tie standing in a room."
- 自动来源：`positive_1` / "A person wearing a white shirt and tie standing in  a room."
- 正确片段："white shirt and tie standing in "
- 错误片段："black shirt and tie standing in"
- 正确片段 token：IDs `[654, 1078, 1128, 4193, 376, 297, 1400, 2823, 350, 353, 256]`；pieces `["Ġwh", "ite", "Ġsh", "irt", "Ġand", "Ġt", "ie", "Ġstand", "ing", "Ġin", "Ġ"]`；decode " white shirt and tie standing in "
- 错误片段 token：IDs `[2597, 1637, 1128, 4193, 376, 297, 1400, 2823, 350, 353]`；pieces `["Ġbl", "ack", "Ġsh", "irt", "Ġand", "Ġt", "ie", "Ġstand", "ing", "Ġin"]`；decode " black shirt and tie standing in"
- 自动分类：`unique_alignment`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因：null
- Token 边界提示：[]

### 10. `replace_attribute:290`

- 负例类型：`replace_attribute`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："A train passing through wooded areas on a train track."
- 正描述 2："A train is moving on a train track through a forest."
- 负描述："A train passing through desolate areas on a train track."
- 自动来源：`positive_1` / "A train passing through wooded areas on a train track."
- 正确片段："wooded"
- 错误片段："desolate"
- 正确片段 token：IDs `[339, 2166, 382]`；pieces `["Ġw", "ood", "ed"]`；decode " wooded"
- 错误片段 token：IDs `[1453, 500, 557]`；pieces `["Ġdes", "ol", "ate"]`；decode " desolate"
- 自动分类：`unique_alignment`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因：null
- Token 边界提示：[]

### 11. `replace_attribute:299`

- 负例类型：`replace_attribute`
- 阶段三范围：`pilot`；certifying formal：`False`
- 正描述 1："A photo of a bright pink shoe on a blue and green background."
- 正描述 2："The photo of the bright pink shoe is situated on a green and blue background."
- 负描述："A photo of a dim pink shoe on a blue and green background."
- 自动来源：`positive_1` / "A photo of a bright pink shoe on a blue and green background."
- 正确片段："bright"
- 错误片段："dim"
- 正确片段 token：IDs `[3461, 774]`；pieces `["Ġbr", "ight"]`；decode " bright"
- 错误片段 token：IDs `[373, 467]`；pieces `["Ġd", "im"]`；decode " dim"
- 自动分类：`unique_alignment`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因：null
- Token 边界提示：[]

### 12. `replace_attribute:316`

- 负例类型：`replace_attribute`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："The vanity is decorated with a red flower arrangement and glass candles and perfume bottles. "
- 正描述 2："Red flower arrangement along with perfume bottles and glass candles are positioned to adorn the vanity."
- 负描述："The vanity is decorated with a yellow flower arrangement and glass candles and perfume bottles."
- 自动来源：`positive_1` / "The vanity is decorated with a red flower arrangement and glass candles and perfume bottles. "
- 正确片段："red flower arrangement and glass candles and perfume bottles. "
- 错误片段："yellow flower arrangement and glass candles and perfume bottles."
- 正确片段 token：IDs `[5534, 5652, 311, 3562, 1285, 791, 376, 492, 111, 1388, 541, 103, 1907, 376, 1613, 105, 4557, 363, 593, 119, 1907, 49, 256]`；pieces `["Ġred", "Ġflow", "er", "Ġarr", "ange", "ment", "Ġand", "Ġg", "l", "ass", "Ġcan", "d", "les", "Ġand", "Ġper", "f", "ume", "Ġb", "ot", "t", "les", ".", "Ġ"]`；decode " red flower arrangement and glass candles and perfume bottles. "
- 错误片段 token：IDs `[385, 446, 1030, 5652, 311, 3562, 1285, 791, 376, 492, 111, 1388, 541, 103, 1907, 376, 1613, 105, 4557, 363, 593, 119, 1907, 49]`；pieces `["Ġy", "el", "low", "Ġflow", "er", "Ġarr", "ange", "ment", "Ġand", "Ġg", "l", "ass", "Ġcan", "d", "les", "Ġand", "Ġper", "f", "ume", "Ġb", "ot", "t", "les", "."]`；decode " yellow flower arrangement and glass candles and perfume bottles."
- 自动分类：`complex_edit`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因："obvious_rewrite_by_fixed_coverage_rule"
- Token 边界提示：[]

### 13. `replace_attribute:345`

- 负例类型：`replace_attribute`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："an old person sitting on top of a horse next to the mountains"
- 正描述 2："An elderly person is positioned on top of a horse, which is situated close to the mountains."
- 负描述："A young person sitting on top of a horse next to the mountains."
- 自动来源：`positive_1` / "an old person sitting on top of a horse next to the mountains"
- 正确片段："an old person sitting on top of a horse next to the mountains"
- 错误片段："A young person sitting on top of a horse next to the mountains."
- 正确片段 token：IDs `[325, 4797, 2198, 5305, 2912, 619, 2924, 354, 299, 429, 336, 573, 4658, 364, 309, 5083, 118]`；pieces `["an", "Ġold", "Ġperson", "Ġsit", "ting", "Ġon", "Ġtop", "Ġof", "Ġa", "Ġh", "or", "se", "Ġnext", "Ġto", "Ġthe", "Ġmountain", "s"]`；decode "an old person sitting on top of a horse next to the mountains"
- 错误片段 token：IDs `[68, 401, 1685, 2198, 5305, 2912, 619, 2924, 354, 299, 429, 336, 573, 4658, 364, 309, 5083, 118, 49]`；pieces `["A", "Ġyou", "ng", "Ġperson", "Ġsit", "ting", "Ġon", "Ġtop", "Ġof", "Ġa", "Ġh", "or", "se", "Ġnext", "Ġto", "Ġthe", "Ġmountain", "s", "."]`；decode "A young person sitting on top of a horse next to the mountains."
- 自动分类：`complex_edit`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因："non_contiguous_edit_blocks=2;obvious_rewrite_by_fixed_coverage_rule"
- Token 边界提示：[]

### 14. `replace_attribute:376`

- 负例类型：`replace_attribute`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："A brick building with a tall clock tower beside it."
- 正描述 2："A tall clock tower stands beside a brick building."
- 负描述："A glass building with a tall clock tower beside it."
- 自动来源：`positive_1` / "A brick building with a tall clock tower beside it."
- 正确片段："brick"
- 错误片段："glass"
- 正确片段 token：IDs `[3461, 2437]`；pieces `["Ġbr", "ick"]`；decode " brick"
- 错误片段 token：IDs `[492, 111, 1388]`；pieces `["Ġg", "l", "ass"]`；decode " glass"
- 自动分类：`unique_alignment`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因：null
- Token 边界提示：[]

### 15. `replace_attribute:383`

- 负例类型：`replace_attribute`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："several jet planes flying in unison in a v formation "
- 正描述 2："Several jet planes are flying in a V formation in unison."
- 负描述："Several propeller planes flying in unison in a V formation."
- 自动来源：`positive_1` / "several jet planes flying in unison in a v formation "
- 正确片段："several jet planes flying in unison in a v formation "
- 错误片段："Several propeller planes flying in unison in a V formation."
- 正确片段 token：IDs `[573, 652, 352, 1315, 439, 4140, 329, 341, 542, 350, 353, 1406, 324, 310, 353, 299, 603, 1508, 489, 256]`；pieces `["se", "ver", "al", "Ġj", "et", "Ġplan", "es", "Ġf", "ly", "ing", "Ġin", "Ġun", "is", "on", "Ġin", "Ġa", "Ġv", "Ġform", "ation", "Ġ"]`；decode "several jet planes flying in unison in a v formation "
- 错误片段 token：IDs `[86, 1389, 352, 540, 115, 1272, 311, 4140, 329, 341, 542, 350, 353, 1406, 324, 310, 353, 299, 2299, 1508, 489, 49]`；pieces `["S", "ever", "al", "Ġpro", "p", "ell", "er", "Ġplan", "es", "Ġf", "ly", "ing", "Ġin", "Ġun", "is", "on", "Ġin", "Ġa", "ĠV", "Ġform", "ation", "."]`；decode "Several propeller planes flying in unison in a V formation."
- 自动分类：`complex_edit`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因："non_contiguous_edit_blocks=3;obvious_rewrite_by_fixed_coverage_rule"
- Token 边界提示：[]

### 16. `replace_attribute:391`

- 负例类型：`replace_attribute`
- 阶段三范围：`pilot`；certifying formal：`False`
- 正描述 1："A group of zebra standing next to each other on a dirt field."
- 正描述 2："A group of zebras are on a dirt field standing together."
- 负描述："A group of zebra standing next to each other on a grass field."
- 自动来源：`positive_1` / "A group of zebra standing next to each other on a dirt field."
- 正确片段："dirt"
- 错误片段："grass"
- 正确片段 token：IDs `[373, 4193]`；pieces `["Ġd", "irt"]`；decode " dirt"
- 错误片段 token：IDs `[492, 117, 1388]`；pieces `["Ġg", "r", "ass"]`；decode " grass"
- 自动分类：`unique_alignment`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因：null
- Token 边界提示：[]

### 17. `replace_attribute:4`

- 负例类型：`replace_attribute`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："A person leaning up against a metal rail while holding a rainbow colored umbrella."
- 正描述 2："A person is positioned against a metal rail while holding a rainbow-colored umbrella."
- 负描述："A person leaning up against a plastic rail while holding a rainbow colored umbrella."
- 自动来源：`positive_1` / "A person leaning up against a metal rail while holding a rainbow colored umbrella."
- 正确片段："metal"
- 错误片段："plastic"
- 正确片段 token：IDs `[4743, 352]`；pieces `["Ġmet", "al"]`；decode " metal"
- 错误片段 token：IDs `[1219, 1154, 375]`；pieces `["Ġpl", "ast", "ic"]`；decode " plastic"
- 自动分类：`unique_alignment`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因：null
- Token 边界提示：[]

### 18. `replace_attribute:400`

- 负例类型：`replace_attribute`
- 阶段三范围：`formal`；certifying formal：`False`
- 正描述 1："A red Dodge truck is parked near another Dodge. "
- 正描述 2："Another Dodge is parked adjacent to a red Dodge truck."
- 负描述："A black Dodge truck is parked near another Dodge."
- 自动来源：`positive_1` / "A red Dodge truck is parked near another Dodge. "
- 正确片段："red Dodge truck is parked near another Dodge. "
- 错误片段："black Dodge truck is parked near another Dodge."
- 正确片段 token：IDs `[5534, 1058, 1318, 583, 1144, 120, 892, 395, 344, 2000, 382, 730, 370, 5467, 1058, 1318, 583, 49, 256]`；pieces `["Ġred", "ĠD", "od", "ge", "Ġtr", "u", "ck", "Ġis", "Ġp", "ark", "ed", "Ġne", "ar", "Ġanother", "ĠD", "od", "ge", ".", "Ġ"]`；decode " red Dodge truck is parked near another Dodge. "
- 错误片段 token：IDs `[2597, 1637, 1058, 1318, 583, 1144, 120, 892, 395, 344, 2000, 382, 730, 370, 5467, 1058, 1318, 583, 49]`；pieces `["Ġbl", "ack", "ĠD", "od", "ge", "Ġtr", "u", "ck", "Ġis", "Ġp", "ark", "ed", "Ġne", "ar", "Ġanother", "ĠD", "od", "ge", "."]`；decode " black Dodge truck is parked near another Dodge."
- 自动分类：`complex_edit`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因："obvious_rewrite_by_fixed_coverage_rule"
- Token 边界提示：[]

### 19. `replace_attribute:436`

- 负例类型：`replace_attribute`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："Small child in green shirt holding a slice of pizza to their face. "
- 正描述 2："The little child holding a slice of pizza in front of their face is wearing a green shirt."
- 负描述："Small child in purple shirt holding a slice of pizza to their face."
- 自动来源：`positive_1` / "Small child in green shirt holding a slice of pizza to their face. "
- 正确片段："green shirt holding a slice of pizza to their face. "
- 错误片段："purple shirt holding a slice of pizza to their face."
- 正确片段 token：IDs `[5921, 1128, 4193, 429, 2569, 350, 299, 316, 111, 1126, 354, 344, 1028, 125, 100, 364, 1635, 341, 1489, 49, 256]`；pieces `["Ġgreen", "Ġsh", "irt", "Ġh", "old", "ing", "Ġa", "Ġs", "l", "ice", "Ġof", "Ġp", "iz", "z", "a", "Ġto", "Ġtheir", "Ġf", "ace", ".", "Ġ"]`；decode " green shirt holding a slice of pizza to their face. "
- 错误片段 token：IDs `[3315, 833, 1128, 4193, 429, 2569, 350, 299, 316, 111, 1126, 354, 344, 1028, 125, 100, 364, 1635, 341, 1489, 49]`；pieces `["Ġpur", "ple", "Ġsh", "irt", "Ġh", "old", "ing", "Ġa", "Ġs", "l", "ice", "Ġof", "Ġp", "iz", "z", "a", "Ġto", "Ġtheir", "Ġf", "ace", "."]`；decode " purple shirt holding a slice of pizza to their face."
- 自动分类：`complex_edit`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因："obvious_rewrite_by_fixed_coverage_rule"
- Token 边界提示：[]

### 20. `replace_attribute:482`

- 负例类型：`replace_attribute`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："A white toilet with a black seat sitting in a small stall."
- 正描述 2："A black seat is positioned on top of a white toilet, which is situated within a small stall."
- 负描述："A pink toilet with a black seat sitting in a small stall."
- 自动来源：`positive_1` / "A white toilet with a black seat sitting in a small stall."
- 正确片段："white"
- 错误片段："pink"
- 正确片段 token：IDs `[654, 1078]`；pieces `["Ġwh", "ite"]`；decode " white"
- 错误片段 token：IDs `[344, 3010]`；pieces `["Ġp", "ink"]`；decode " pink"
- 自动分类：`unique_alignment`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因：null
- Token 边界提示：[]

### 21. `replace_attribute:52`

- 负例类型：`replace_attribute`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："The orange handles of scissors are sticking out of a holder."
- 正描述 2："The orange handles of scissors are protruding from a holder."
- 负描述："The green handles of scissors are sticking out of a holder."
- 自动来源：`positive_1` / "The orange handles of scissors are sticking out of a holder."
- 正确片段："orange"
- 错误片段："green"
- 正确片段 token：IDs `[522, 1285]`；pieces `["Ġor", "ange"]`；decode " orange"
- 错误片段 token：IDs `[5921]`；pieces `["Ġgreen"]`；decode " green"
- 自动分类：`unique_alignment`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因：null
- Token 边界提示：[]

### 22. `replace_attribute:542`

- 负例类型：`replace_attribute`
- 阶段三范围：`pilot`；certifying formal：`False`
- 正描述 1："A toilet that is made of material with sparkles."
- 正描述 2："A toilet made of sparkling material."
- 负描述："A toilet that is made of plain material."
- 自动来源：`positive_2` / "A toilet made of sparkling material."
- 正确片段："made of sparkling"
- 错误片段："that is made of plain"
- 正确片段 token：IDs `[4303, 354, 1772, 2000, 4510]`；pieces `["Ġmade", "Ġof", "Ġsp", "ark", "ling"]`；decode " made of sparkling"
- 错误片段 token：IDs `[591, 395, 4303, 354, 1219, 740]`；pieces `["Ġthat", "Ġis", "Ġmade", "Ġof", "Ġpl", "ain"]`；decode " that is made of plain"
- 自动分类：`complex_edit`
- 来源规则："positive_2_pareto_dominates_character_and_token_distance"
- 失败原因："non_contiguous_edit_blocks=2"
- Token 边界提示：[]

### 23. `replace_attribute:557`

- 负例类型：`replace_attribute`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："A bathroom has yellow walls, brown floors, and a closet in it."
- 正描述 2："The closet is located within the bathroom, which has brown floors and yellow walls."
- 负描述："A bathroom has yellow walls, white floors, and a closet in it."
- 自动来源：`positive_1` / "A bathroom has yellow walls, brown floors, and a closet in it."
- 正确片段："brown"
- 错误片段："white"
- 正确片段 token：IDs `[363, 2079, 113]`；pieces `["Ġb", "row", "n"]`；decode " brown"
- 错误片段 token：IDs `[654, 1078]`；pieces `["Ġwh", "ite"]`；decode " white"
- 自动分类：`unique_alignment`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因：null
- Token 边界提示：[]

### 24. `replace_attribute:579`

- 负例类型：`replace_attribute`
- 阶段三范围：`pilot`；certifying formal：`False`
- 正描述 1："A small cow in a enclosure with straw on the floor. "
- 正描述 2："A small cow is enclosed in a straw-covered area on the floor."
- 负描述："A gigantic cow in an enclosure with straw on the floor."
- 自动来源：`positive_1` / "A small cow in a enclosure with straw on the floor. "
- 正确片段："small cow in a enclosure with straw on the floor. "
- 错误片段："gigantic cow in an enclosure with straw on the floor."
- 正确片段 token：IDs `[3436, 317, 451, 353, 299, 5867, 722, 118, 745, 599, 580, 559, 122, 619, 309, 5796, 336, 49, 256]`；pieces `["Ġsmall", "Ġc", "ow", "Ġin", "Ġa", "Ġenc", "lo", "s", "ure", "Ġwith", "Ġst", "ra", "w", "Ġon", "Ġthe", "Ġflo", "or", ".", "Ġ"]`；decode " small cow in a enclosure with straw on the floor. "
- 错误片段 token：IDs `[492, 499, 811, 375, 317, 451, 353, 346, 5867, 722, 118, 745, 599, 580, 559, 122, 619, 309, 5796, 336, 49]`；pieces `["Ġg", "ig", "ant", "ic", "Ġc", "ow", "Ġin", "Ġan", "Ġenc", "lo", "s", "ure", "Ġwith", "Ġst", "ra", "w", "Ġon", "Ġthe", "Ġflo", "or", "."]`；decode " gigantic cow in an enclosure with straw on the floor."
- 自动分类：`complex_edit`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因："non_contiguous_edit_blocks=2;obvious_rewrite_by_fixed_coverage_rule"
- Token 边界提示：[]

### 25. `replace_attribute:611`

- 负例类型：`replace_attribute`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："A black metal bench with a hat hanging on the back of it. "
- 正描述 2："A bench with a hat hanging on its back is made of metal and is black."
- 负描述："A green metal bench with a hat hanging on the back of it."
- 自动来源：`positive_1` / "A black metal bench with a hat hanging on the back of it. "
- 正确片段："black metal bench with a hat hanging on the back of it. "
- 错误片段："green metal bench with a hat hanging on the back of it."
- 正确片段 token：IDs `[2597, 1637, 4743, 352, 6141, 550, 599, 299, 429, 314, 429, 942, 350, 619, 309, 3901, 354, 563, 49, 256]`；pieces `["Ġbl", "ack", "Ġmet", "al", "Ġben", "ch", "Ġwith", "Ġa", "Ġh", "at", "Ġh", "ang", "ing", "Ġon", "Ġthe", "Ġback", "Ġof", "Ġit", ".", "Ġ"]`；decode " black metal bench with a hat hanging on the back of it. "
- 错误片段 token：IDs `[5921, 4743, 352, 6141, 550, 599, 299, 429, 314, 429, 942, 350, 619, 309, 3901, 354, 563, 49]`；pieces `["Ġgreen", "Ġmet", "al", "Ġben", "ch", "Ġwith", "Ġa", "Ġh", "at", "Ġh", "ang", "ing", "Ġon", "Ġthe", "Ġback", "Ġof", "Ġit", "."]`；decode " green metal bench with a hat hanging on the back of it."
- 自动分类：`complex_edit`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因："obvious_rewrite_by_fixed_coverage_rule"
- Token 边界提示：[]

### 26. `replace_attribute:668`

- 负例类型：`replace_attribute`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："A stop sign with a eating animals sticker on it."
- 正描述 2："A sign displaying a 'stop' symbol with a sticker of eating animals on it."
- 负描述："A stop sign with a vegetarian animals sticker on it."
- 自动来源：`positive_1` / "A stop sign with a eating animals sticker on it."
- 正确片段："eating"
- 错误片段："vegetarian"
- 正确片段 token：IDs `[413, 1807]`；pieces `["Ġe", "ating"]`；decode " eating"
- 错误片段 token：IDs `[4389, 2353, 1482, 325]`；pieces `["Ġve", "get", "ari", "an"]`；decode " vegetarian"
- 自动分类：`unique_alignment`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因：null
- Token 边界提示：[]

### 27. `replace_attribute:682`

- 负例类型：`replace_attribute`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："Two men wearing ties cross the street at night."
- 正描述 2："Two men in ties walk across the street at night."
- 负描述："Two men wearing ties cross the street in the daytime."
- 自动来源：`positive_1` / "Two men wearing ties cross the street at night."
- 正确片段："at night"
- 错误片段："in the daytime"
- 正确片段 token：IDs `[1248, 4460]`；pieces `["Ġat", "Ġnight"]`；decode " at night"
- 错误片段 token：IDs `[353, 309, 2893, 3904]`；pieces `["Ġin", "Ġthe", "Ġday", "time"]`；decode " in the daytime"
- 自动分类：`unique_alignment`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因：null
- Token 边界提示：[]

### 28. `replace_attribute:716`

- 负例类型：`replace_attribute`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："Several vehicles providing ground transportation are shown in the photo: streetcar, tourbus, classic car and family cars"
- 正描述 2："The photograph depicts vehicles used for different modes of ground transportation such as: a tourbus, a streetcar, family cars and a classic car."
- 负描述："Several vehicles providing aerial transportation are shown in the photo: helicopter, hot air balloon, small plane and glider."
- 自动来源：`positive_1` / "Several vehicles providing ground transportation are shown in the photo: streetcar, tourbus, classic car and family cars"
- 正确片段："ground transportation are shown in the photo: streetcar, tourbus, classic car and family cars"
- 错误片段："aerial transportation are shown in the photo: helicopter, hot air balloon, small plane and glider."
- 正确片段 token：IDs `[492, 2383, 1890, 1426, 489, 732, 1128, 2791, 353, 309, 2001, 593, 114, 61, 5941, 439, 102, 370, 47, 297, 1084, 101, 832, 47, 2882, 375, 3751, 376, 5879, 317, 2546]`；pieces `["Ġg", "round", "Ġtrans", "port", "ation", "Ġare", "Ġsh", "own", "Ġin", "Ġthe", "Ġph", "ot", "o", ":", "Ġstre", "et", "c", "ar", ",", "Ġt", "our", "b", "us", ",", "Ġclass", "ic", "Ġcar", "Ġand", "Ġfamily", "Ġc", "ars"]`；decode " ground transportation are shown in the photo: streetcar, tourbus, classic car and family cars"
- 错误片段 token：IDs `[299, 311, 926, 1890, 1426, 489, 732, 1128, 2791, 353, 309, 2001, 593, 114, 61, 582, 1802, 114, 875, 311, 47, 429, 593, 3980, 363, 352, 722, 310, 47, 3436, 4140, 104, 376, 492, 111, 4591, 49]`；pieces `["Ġa", "er", "ial", "Ġtrans", "port", "ation", "Ġare", "Ġsh", "own", "Ġin", "Ġthe", "Ġph", "ot", "o", ":", "Ġhe", "lic", "o", "pt", "er", ",", "Ġh", "ot", "Ġair", "Ġb", "al", "lo", "on", ",", "Ġsmall", "Ġplan", "e", "Ġand", "Ġg", "l", "ider", "."]`；decode " aerial transportation are shown in the photo: helicopter, hot air balloon, small plane and glider."
- 自动分类：`complex_edit`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因："non_contiguous_edit_blocks=5;obvious_rewrite_by_fixed_coverage_rule"
- Token 边界提示：[]

### 29. `replace_attribute:768`

- 负例类型：`replace_attribute`
- 阶段三范围：`pilot`；certifying formal：`False`
- 正描述 1："An assortment of doughnuts are arranged in a display case."
- 正描述 2："A variety of doughnuts are organized for display in a case."
- 负描述："A singular doughnut is arranged in a display case."
- 自动来源：`positive_1` / "An assortment of doughnuts are arranged in a display case."
- 正确片段："n assortment of doughnuts are"
- 错误片段：" singular doughnut is"
- 正确片段 token：IDs `[5799, 1031, 866, 791, 354, 373, 3113, 113, 501, 118, 732]`；pieces `["An", "Ġass", "ort", "ment", "Ġof", "Ġd", "ough", "n", "ut", "s", "Ġare"]`；decode "An assortment of doughnuts are"
- 错误片段 token：IDs `[68, 3634, 2055, 373, 3113, 113, 501, 395]`；pieces `["A", "Ġsing", "ular", "Ġd", "ough", "n", "ut", "Ġis"]`；decode "A singular doughnut is"
- 自动分类：`unique_alignment`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因：null
- Token 边界提示：[]

### 30. `replace_attribute:785`

- 负例类型：`replace_attribute`
- 阶段三范围：`pilot`；certifying formal：`False`
- 正描述 1："An old person reading a book on a park bench."
- 正描述 2："An elderly person is seated on a park bench while reading a book."
- 负描述："A young person reading a book on a park bench."
- 自动来源：`positive_1` / "An old person reading a book on a park bench."
- 正确片段："n old"
- 错误片段：" young"
- 正确片段 token：IDs `[5799, 4797]`；pieces `["An", "Ġold"]`；decode "An old"
- 错误片段 token：IDs `[68, 401, 1685]`；pieces `["A", "Ġyou", "ng"]`；decode "A young"
- 自动分类：`unique_alignment`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因：null
- Token 边界提示：[]

## 负例类型：replace_object

候选 `1652` 条，本节抽取 `30` 条。

### 1. `replace_object:1029`

- 负例类型：`replace_object`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："There is a plate filled with pastries next to a keyboard."
- 正描述 2："The keyboard is adjacent to a plate filled with pastries."
- 负描述："There is a basket filled with pastries next to a keyboard."
- 自动来源：`positive_1` / "There is a plate filled with pastries next to a keyboard."
- 正确片段："plate"
- 错误片段："basket"
- 正确片段 token：IDs `[1219, 557]`；pieces `["Ġpl", "ate"]`；decode " plate"
- 错误片段 token：IDs `[5207, 110, 439]`；pieces `["Ġbas", "k", "et"]`；decode " basket"
- 自动分类：`unique_alignment`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因：null
- Token 边界提示：[]

### 2. `replace_object:1111`

- 负例类型：`replace_object`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："A big brown cow walking down a sidewalk near homes."
- 正描述 2："A large brown cow is strolling along a sidewalk near residences."
- 负描述："A big brown horse walking down a sidewalk near homes."
- 自动来源：`positive_1` / "A big brown cow walking down a sidewalk near homes."
- 正确片段："cow"
- 错误片段："horse"
- 正确片段 token：IDs `[317, 451]`；pieces `["Ġc", "ow"]`；decode " cow"
- 错误片段 token：IDs `[429, 336, 573]`；pieces `["Ġh", "or", "se"]`；decode " horse"
- 自动分类：`unique_alignment`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因：null
- Token 边界提示：[]

### 3. `replace_object:1174`

- 负例类型：`replace_object`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："A pregnant woman is in bed reading a large book."
- 正描述 2："In a bed, there is a pregnant woman who is reading a large book."
- 负描述："A pregnant woman is on a sofa reading a large book."
- 自动来源：`positive_1` / "A pregnant woman is in bed reading a large book."
- 正确片段："in bed"
- 错误片段："on a sofa"
- 正确片段 token：IDs `[353, 363, 382]`；pieces `["Ġin", "Ġb", "ed"]`；decode " in bed"
- 错误片段 token：IDs `[619, 299, 1122, 105, 100]`；pieces `["Ġon", "Ġa", "Ġso", "f", "a"]`；decode " on a sofa"
- 自动分类：`unique_alignment`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因：null
- Token 边界提示：[]

### 4. `replace_object:1233`

- 负例类型：`replace_object`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："A lady is preparing pancakes in a charming white kitchen."
- 正描述 2："A woman is in a lovely white kitchen making pancakes."
- 负描述："A man is preparing pancakes in a charming white kitchen."
- 自动来源：`positive_1` / "A lady is preparing pancakes in a charming white kitchen."
- 正确片段："lady"
- 错误片段："man"
- 正确片段 token：IDs `[406, 785, 124]`；pieces `["Ġl", "ad", "y"]`；decode " lady"
- 错误片段 token：IDs `[1672]`；pieces `["Ġman"]`；decode " man"
- 自动分类：`unique_alignment`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因：null
- Token 边界提示：[]

### 5. `replace_object:1249`

- 负例类型：`replace_object`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："A bathroom with toys and books for young children.  "
- 正描述 2："The bathroom contains books and toys for young children."
- 负描述："A bathroom with toys and gadgets for young children."
- 自动来源：`positive_1` / "A bathroom with toys and books for young children.  "
- 正确片段："books for young children.  "
- 错误片段："gadgets for young children."
- 正确片段 token：IDs `[5826, 503, 401, 1685, 6109, 3193, 49, 332]`；pieces `["Ġbooks", "Ġfor", "Ġyou", "ng", "Ġchild", "ren", ".", "ĠĠ"]`；decode " books for young children.  "
- 错误片段 token：IDs `[492, 785, 2353, 118, 503, 401, 1685, 6109, 3193, 49]`；pieces `["Ġg", "ad", "get", "s", "Ġfor", "Ġyou", "ng", "Ġchild", "ren", "."]`；decode " gadgets for young children."
- 自动分类：`unique_alignment`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因：null
- Token 边界提示：[]

### 6. `replace_object:139`

- 负例类型：`replace_object`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："A small child is in the kitchen with an adult and dog."
- 正描述 2："An adult and a dog are in the kitchen with a small child."
- 负描述："A small child is in the kitchen with an adult and cat."
- 自动来源：`positive_1` / "A small child is in the kitchen with an adult and dog."
- 正确片段："dog"
- 错误片段："cat"
- 正确片段 token：IDs `[1041, 106]`；pieces `["Ġdo", "g"]`；decode " dog"
- 错误片段 token：IDs `[3706]`；pieces `["Ġcat"]`；decode " cat"
- 自动分类：`unique_alignment`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因：null
- Token 边界提示：[]

### 7. `replace_object:1458`

- 负例类型：`replace_object`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："A polar bear with his chin raised lies on a rock."
- 正描述 2："A polar bear lying on a rock with its chin lifted."
- 负描述："A lion with his chin raised lies on a rock."
- 自动来源：`positive_1` / "A polar bear with his chin raised lies on a rock."
- 正确片段："polar bear"
- 错误片段："lion"
- 正确片段 token：IDs `[3080, 370, 600, 370]`；pieces `["Ġpol", "ar", "Ġbe", "ar"]`；decode " polar bear"
- 错误片段 token：IDs `[406, 371]`；pieces `["Ġl", "ion"]`；decode " lion"
- 自动分类：`unique_alignment`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因：null
- Token 边界提示：[]

### 8. `replace_object:1562`

- 负例类型：`replace_object`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："A street lined with cones with people up and down the sidewalk."
- 正描述 2："with people walking up and down the sidewalk of a street where cones are positioned along the street."
- 负描述："A street lined with flowers with people up and down the sidewalk."
- 自动来源：`positive_1` / "A street lined with cones with people up and down the sidewalk."
- 正确片段："cone"
- 错误片段："flower"
- 正确片段 token：IDs `[614, 329]`；pieces `["Ġcon", "es"]`；decode " cones"
- 错误片段 token：IDs `[5652, 496]`；pieces `["Ġflow", "ers"]`；decode " flowers"
- 自动分类：`unique_alignment`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因：null
- Token 边界提示：[]

### 9. `replace_object:1582`

- 负例类型：`replace_object`
- 阶段三范围：`pilot`；certifying formal：`False`
- 正描述 1："Three zebras standing in a sandy desert area."
- 正描述 2："A group of three zebras are standing in a sandy desert area."
- 负描述："Three ostriches standing in a sandy desert area."
- 自动来源：`positive_1` / "Three zebras standing in a sandy desert area."
- 正确片段："zebra"
- 错误片段："ostriche"
- 正确片段 token：IDs `[3243, 3037, 117, 390]`；pieces `["Ġz", "eb", "r", "as"]`；decode " zebras"
- 错误片段 token：IDs `[319, 3040, 375, 2470]`；pieces `["Ġo", "str", "ic", "hes"]`；decode " ostriches"
- 自动分类：`unique_alignment`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因：null
- Token 边界提示：[]

### 10. `replace_object:1583`

- 负例类型：`replace_object`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："A cat is staring while sitting in a sink."
- 正描述 2："The cat is sitting in the sink while staring."
- 负描述："A goldfish is swimming in a sink."
- 自动来源：`positive_1` / "A cat is staring while sitting in a sink."
- 正确片段："cat is staring while sitt"
- 错误片段："goldfish is swimm"
- 正确片段 token：IDs `[3706, 395, 580, 370, 350, 3052, 5305, 2912]`；pieces `["Ġcat", "Ġis", "Ġst", "ar", "ing", "Ġwhile", "Ġsit", "ting"]`；decode " cat is staring while sitting"
- 错误片段 token：IDs `[5135, 105, 1689, 395, 316, 122, 467, 3005]`；pieces `["Ġgold", "f", "ish", "Ġis", "Ġs", "w", "im", "ming"]`；decode " goldfish is swimming"
- 自动分类：`complex_edit`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因："non_contiguous_edit_blocks=2"
- Token 边界提示：[]

### 11. `replace_object:163`

- 负例类型：`replace_object`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："A white sink with a black cabinet underneath it."
- 正描述 2："The black cabinet is positioned underneath the white sink."
- 负描述："A white bathtub with a black cabinet underneath it."
- 自动来源：`positive_1` / "A white sink with a black cabinet underneath it."
- 正确片段："sink"
- 错误片段："bathtub"
- 正确片段 token：IDs `[316, 3010]`；pieces `["Ġs", "ink"]`；decode " sink"
- 错误片段 token：IDs `[363, 1831, 119, 1352]`；pieces `["Ġb", "ath", "t", "ub"]`；decode " bathtub"
- 自动分类：`unique_alignment`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因：null
- Token 边界提示：[]

### 12. `replace_object:1646`

- 负例类型：`replace_object`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："A living room with a couch and chair."
- 正描述 2："A couch and chair are positioned in a living room."
- 负描述："A bedroom with a bed and dresser."
- 自动来源：`positive_1` / "A living room with a couch and chair."
- 正确片段："living room with a couch and chai"
- 错误片段："bedroom with a bed and dresse"
- 正确片段 token：IDs `[406, 4917, 1552, 444, 599, 299, 317, 326, 550, 376, 890, 3709]`；pieces `["Ġl", "iving", "Ġro", "om", "Ġwith", "Ġa", "Ġc", "ou", "ch", "Ġand", "Ġch", "air"]`；decode " living room with a couch and chair"
- 错误片段 token：IDs `[363, 382, 393, 444, 599, 299, 363, 382, 376, 373, 1592, 311]`；pieces `["Ġb", "ed", "ro", "om", "Ġwith", "Ġa", "Ġb", "ed", "Ġand", "Ġd", "ress", "er"]`；decode " bedroom with a bed and dresser"
- 自动分类：`complex_edit`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因："non_contiguous_edit_blocks=3"
- Token 边界提示：[]

### 13. `replace_object:180`

- 负例类型：`replace_object`
- 阶段三范围：`formal`；certifying formal：`False`
- 正描述 1："Two people are riding bikes through the street traffic."
- 正描述 2："Two individuals are biking through the street's traffic."
- 负描述："Two people are riding scooters through the street traffic."
- 自动来源：`positive_1` / "Two people are riding bikes through the street traffic."
- 正确片段："bike"
- 错误片段："scooter"
- 正确片段 token：IDs `[363, 3159, 329]`；pieces `["Ġb", "ik", "es"]`；decode " bikes"
- 错误片段 token：IDs `[1416, 4967, 496]`；pieces `["Ġsc", "oot", "ers"]`；decode " scooters"
- 自动分类：`unique_alignment`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因：null
- Token 边界提示：[]

### 14. `replace_object:304`

- 负例类型：`replace_object`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："A bowl holds soup with broccoli and other vegetables. "
- 正描述 2："The soup bowl contains broccoli and other vegetables."
- 负描述："A bowl holds stew with broccoli and other vegetables."
- 自动来源：`positive_1` / "A bowl holds soup with broccoli and other vegetables. "
- 正确片段："oup with broccoli and other vegetables. "
- 错误片段："tew with broccoli and other vegetables."
- 正确片段 token：IDs `[316, 326, 115, 599, 5108, 1130, 500, 108, 376, 1649, 4389, 2353, 4880, 49, 256]`；pieces `["Ġs", "ou", "p", "Ġwith", "Ġbro", "cc", "ol", "i", "Ġand", "Ġother", "Ġve", "get", "ables", ".", "Ġ"]`；decode " soup with broccoli and other vegetables. "
- 错误片段 token：IDs `[580, 3068, 599, 5108, 1130, 500, 108, 376, 1649, 4389, 2353, 4880, 49]`；pieces `["Ġst", "ew", "Ġwith", "Ġbro", "cc", "ol", "i", "Ġand", "Ġother", "Ġve", "get", "ables", "."]`；decode " stew with broccoli and other vegetables."
- 自动分类：`unique_alignment`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因：null
- Token 边界提示：[]

### 15. `replace_object:366`

- 负例类型：`replace_object`
- 阶段三范围：`pilot`；certifying formal：`False`
- 正描述 1："A man standing next to a dog on the ground."
- 正描述 2："A man is standing on the ground adjacent to a dog."
- 负描述："A woman standing next to a dog on the ground."
- 自动来源：`positive_1` / "A man standing next to a dog on the ground."
- 正确片段：""
- 错误片段："wo"
- 正确片段 token：IDs `[1672]`；pieces `["Ġman"]`；decode " man"
- 错误片段 token：IDs `[339, 444, 325]`；pieces `["Ġw", "om", "an"]`；decode " woman"
- 自动分类：`unique_alignment`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因：null
- Token 边界提示：[]

### 16. `replace_object:429`

- 负例类型：`replace_object`
- 阶段三范围：`pilot`；certifying formal：`False`
- 正描述 1："A man with graying hair looks down at a stand full of yellow bananas."
- 正描述 2："A stand full of yellow bananas is positioned below a man with graying hair who looks down at it."
- 负描述："A woman with graying hair looks down at a stand full of yellow bananas."
- 自动来源：`positive_1` / "A man with graying hair looks down at a stand full of yellow bananas."
- 正确片段：""
- 错误片段："wo"
- 正确片段 token：IDs `[1672]`；pieces `["Ġman"]`；decode " man"
- 错误片段 token：IDs `[339, 444, 325]`；pieces `["Ġw", "om", "an"]`；decode " woman"
- 自动分类：`unique_alignment`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因：null
- Token 边界提示：[]

### 17. `replace_object:466`

- 负例类型：`replace_object`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："A large group of zebras graze in the grasslands of africa"
- 正描述 2："In the grasslands of Africa, a large group of zebras graze in the grasslands."
- 负描述："A large group of giraffes graze in the grasslands of Africa."
- 自动来源：`positive_1` / "A large group of zebras graze in the grasslands of africa"
- 正确片段："zebras graze in the grasslands of africa"
- 错误片段："giraffes graze in the grasslands of Africa."
- 正确片段 token：IDs `[3243, 3037, 117, 390, 5528, 3441, 353, 309, 492, 117, 1388, 4882, 118, 354, 299, 105, 3069, 100]`；pieces `["Ġz", "eb", "r", "as", "Ġgra", "ze", "Ġin", "Ġthe", "Ġg", "r", "ass", "land", "s", "Ġof", "Ġa", "f", "ric", "a"]`；decode " zebras graze in the grasslands of africa"
- 错误片段 token：IDs `[492, 108, 559, 1627, 329, 5528, 3441, 353, 309, 492, 117, 1388, 4882, 118, 354, 529, 105, 3069, 100, 49]`；pieces `["Ġg", "i", "ra", "ff", "es", "Ġgra", "ze", "Ġin", "Ġthe", "Ġg", "r", "ass", "land", "s", "Ġof", "ĠA", "f", "ric", "a", "."]`；decode " giraffes graze in the grasslands of Africa."
- 自动分类：`complex_edit`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因："non_contiguous_edit_blocks=2"
- Token 边界提示：[]

### 18. `replace_object:480`

- 负例类型：`replace_object`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："A white plate with two slices of cheese and a whole banana unpealed."
- 正描述 2："A whole banana unpeeled and two slices of cheese are on a white plate."
- 负描述："A cutting board with two slices of cheese and a whole banana unpealed."
- 自动来源：`positive_1` / "A white plate with two slices of cheese and a whole banana unpealed."
- 正确片段："white plate"
- 错误片段："cutting board"
- 正确片段 token：IDs `[654, 1078, 1219, 557]`；pieces `["Ġwh", "ite", "Ġpl", "ate"]`；decode " white plate"
- 错误片段 token：IDs `[5431, 2912, 1847, 1433]`；pieces `["Ġcut", "ting", "Ġbo", "ard"]`；decode " cutting board"
- 自动分类：`unique_alignment`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因：null
- Token 边界提示：[]

### 19. `replace_object:511`

- 负例类型：`replace_object`
- 阶段三范围：`pilot`；certifying formal：`False`
- 正描述 1："A small sheep is standing under a wooden fence post."
- 正描述 2："There is a small sheep that is situated below a wooden fence post."
- 负描述："A small goat is standing under a wooden fence post."
- 自动来源：`positive_1` / "A small sheep is standing under a wooden fence post."
- 正确片段："sheep"
- 错误片段："goat"
- 正确片段 token：IDs `[3191, 1522]`；pieces `["Ġshe", "ep"]`；decode " sheep"
- 错误片段 token：IDs `[2379, 314]`；pieces `["Ġgo", "at"]`；decode " goat"
- 自动分类：`unique_alignment`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因：null
- Token 边界提示：[]

### 20. `replace_object:536`

- 负例类型：`replace_object`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："An older pickup truck with decorative murals painted on."
- 正描述 2："The pickup truck that is old and painted with decorative murals."
- 负描述："An older bicycle with decorative murals painted on."
- 自动来源：`positive_1` / "An older pickup truck with decorative murals painted on."
- 正确片段："pickup truck"
- 错误片段："bicycle"
- 正确片段 token：IDs `[344, 2437, 2764, 1144, 120, 892]`；pieces `["Ġp", "ick", "up", "Ġtr", "u", "ck"]`；decode " pickup truck"
- 错误片段 token：IDs `[363, 375, 124, 2945]`；pieces `["Ġb", "ic", "y", "cle"]`；decode " bicycle"
- 自动分类：`unique_alignment`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因：null
- Token 边界提示：[]

### 21. `replace_object:544`

- 负例类型：`replace_object`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："A piece of dutch chocolate cake with a fork  on a plate. "
- 正描述 2："A plate with a fork and a piece of Dutch chocolate cake."
- 负描述："A piece of dutch chocolate cake with a spoon on a plate."
- 自动来源：`positive_1` / "A piece of dutch chocolate cake with a fork  on a plate. "
- 正确片段："fork  on a plate. "
- 错误片段："spoon on a plate."
- 正确片段 token：IDs `[503, 110, 256, 619, 299, 1219, 557, 49, 256]`；pieces `["Ġfor", "k", "Ġ", "Ġon", "Ġa", "Ġpl", "ate", ".", "Ġ"]`；decode " fork  on a plate. "
- 错误片段 token：IDs `[1772, 114, 310, 619, 299, 1219, 557, 49]`；pieces `["Ġsp", "o", "on", "Ġon", "Ġa", "Ġpl", "ate", "."]`；decode " spoon on a plate."
- 自动分类：`unique_alignment`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因：null
- Token 边界提示：[]

### 22. `replace_object:548`

- 负例类型：`replace_object`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："A man skiing down a snowy hill alone."
- 正描述 2："A man alone is skiing down a hill covered with snow."
- 负描述："A woman skiing down a snowy hill alone."
- 自动来源：`positive_1` / "A man skiing down a snowy hill alone."
- 正确片段：""
- 错误片段："wo"
- 正确片段 token：IDs `[1672]`；pieces `["Ġman"]`；decode " man"
- 错误片段 token：IDs `[339, 444, 325]`；pieces `["Ġw", "om", "an"]`；decode " woman"
- 自动分类：`unique_alignment`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因：null
- Token 边界提示：[]

### 23. `replace_object:563`

- 负例类型：`replace_object`
- 阶段三范围：`pilot`；certifying formal：`False`
- 正描述 1："Two young girls in uniforms sitting closely together."
- 正描述 2："Two young girls wearing uniforms sit closely beside each other."
- 负描述："Two young girls in dresses sitting closely together."
- 自动来源：`positive_1` / "Two young girls in uniforms sitting closely together."
- 正确片段："uniform"
- 错误片段："dresse"
- 正确片段 token：IDs `[1406, 507, 5713, 118]`；pieces `["Ġun", "if", "orm", "s"]`；decode " uniforms"
- 错误片段 token：IDs `[373, 1592, 329]`；pieces `["Ġd", "ress", "es"]`；decode " dresses"
- 自动分类：`unique_alignment`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因：null
- Token 边界提示：[]

### 24. `replace_object:643`

- 负例类型：`replace_object`
- 阶段三范围：`pilot`；certifying formal：`False`
- 正描述 1："A little boy with a red baseball cap playing tennis. "
- 正描述 2："A small kid is playing tennis while wearing a red baseball cap."
- 负描述："A little boy with a red baseball cap playing basketball."
- 自动来源：`positive_1` / "A little boy with a red baseball cap playing tennis. "
- 正确片段："tennis. "
- 错误片段："basketball."
- 正确片段 token：IDs `[297, 6201, 324, 49, 256]`；pieces `["Ġt", "enn", "is", ".", "Ġ"]`；decode " tennis. "
- 错误片段 token：IDs `[5207, 110, 439, 101, 1266, 49]`；pieces `["Ġbas", "k", "et", "b", "all", "."]`；decode " basketball."
- 自动分类：`unique_alignment`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因：null
- Token 边界提示：[]

### 25. `replace_object:7`

- 负例类型：`replace_object`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："A woman wearing shorts bends over a frying pan on a stove."
- 正描述 2："The woman bends over the frying pan on a stove while wearing shorts."
- 负描述："A woman wearing shorts bends over a wok on a stove."
- 自动来源：`positive_1` / "A woman wearing shorts bends over a frying pan on a stove."
- 正确片段："frying pan"
- 错误片段："wok"
- 正确片段 token：IDs `[341, 1557, 350, 344, 325]`；pieces `["Ġf", "ry", "ing", "Ġp", "an"]`；decode " frying pan"
- 错误片段 token：IDs `[339, 4301]`；pieces `["Ġw", "ok"]`；decode " wok"
- 自动分类：`unique_alignment`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因：null
- Token 边界提示：[]

### 26. `replace_object:759`

- 负例类型：`replace_object`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："a blonde horse is standing in a field"
- 正描述 2："A horse with blonde hair is standing in a field."
- 负描述："A blonde cow is standing in a field."
- 自动来源：`None` / null
- 正确片段：""
- 错误片段：""
- 正确片段 token：IDs `[]`；pieces `[]`；decode ""
- 错误片段 token：IDs `[]`；pieces `[]`；decode ""
- 自动分类：`ambiguous_source`
- 来源规则："character_and_token_distance_rankings_conflict"
- 失败原因："character_and_token_distance_rankings_conflict"
- Token 边界提示：[]

### 27. `replace_object:841`

- 负例类型：`replace_object`
- 阶段三范围：`pilot`；certifying formal：`False`
- 正描述 1："A cat on a stool with something on its head"
- 正描述 2："The cat with something on its head is positioned on top of the stool."
- 负描述："A cat on a chair with something on its head."
- 自动来源：`positive_1` / "A cat on a stool with something on its head"
- 正确片段："stool with something on its head"
- 错误片段："chair with something on its head."
- 正确片段 token：IDs `[580, 114, 500, 599, 2798, 619, 1342, 5308]`；pieces `["Ġst", "o", "ol", "Ġwith", "Ġsomething", "Ġon", "Ġits", "Ġhead"]`；decode " stool with something on its head"
- 错误片段 token：IDs `[890, 3709, 599, 2798, 619, 1342, 5308, 49]`；pieces `["Ġch", "air", "Ġwith", "Ġsomething", "Ġon", "Ġits", "Ġhead", "."]`；decode " chair with something on its head."
- 自动分类：`complex_edit`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因："non_contiguous_edit_blocks=2"
- Token 边界提示：[]

### 28. `replace_object:961`

- 负例类型：`replace_object`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："A roasting pan full with apples, carrots, potatoes, and meat"
- 正描述 2："The roasting pan is filled with potatoes, apples, meat and carrots."
- 负描述："A roasting pan full with apples, carrots, onions, and meat."
- 自动来源：`positive_1` / "A roasting pan full with apples, carrots, potatoes, and meat"
- 正确片段："potatoes, and meat"
- 错误片段："onions, and meat."
- 正确片段 token：IDs `[4915, 314, 114, 329, 47, 376, 765, 314]`；pieces `["Ġpot", "at", "o", "es", ",", "Ġand", "Ġme", "at"]`；decode " potatoes, and meat"
- 错误片段 token：IDs `[619, 987, 47, 376, 765, 314, 49]`；pieces `["Ġon", "ions", ",", "Ġand", "Ġme", "at", "."]`；decode " onions, and meat."
- 自动分类：`complex_edit`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因："non_contiguous_edit_blocks=2"
- Token 边界提示：[]

### 29. `replace_object:992`

- 负例类型：`replace_object`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："A turboprop airplane that is in the hangar for repair. "
- 正描述 2："The turboprop airplane is for repair and is in the hangar."
- 负描述："A helicopter that is in the hangar for repair."
- 自动来源：`positive_1` / "A turboprop airplane that is in the hangar for repair. "
- 正确片段："turboprop airplane that is in the hangar for repair. "
- 错误片段："helicopter that is in the hangar for repair."
- 正确片段 token：IDs `[297, 543, 101, 1506, 5623, 3980, 992, 4875, 591, 395, 353, 309, 429, 942, 370, 503, 2956, 3709, 49, 256]`；pieces `["Ġt", "ur", "b", "op", "rop", "Ġair", "pl", "ane", "Ġthat", "Ġis", "Ġin", "Ġthe", "Ġh", "ang", "ar", "Ġfor", "Ġrep", "air", ".", "Ġ"]`；decode " turboprop airplane that is in the hangar for repair. "
- 错误片段 token：IDs `[582, 1802, 114, 875, 311, 591, 395, 353, 309, 429, 942, 370, 503, 2956, 3709, 49]`；pieces `["Ġhe", "lic", "o", "pt", "er", "Ġthat", "Ġis", "Ġin", "Ġthe", "Ġh", "ang", "ar", "Ġfor", "Ġrep", "air", "."]`；decode " helicopter that is in the hangar for repair."
- 自动分类：`complex_edit`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因："obvious_rewrite_by_fixed_coverage_rule"
- Token 边界提示：[]

### 30. `replace_object:999`

- 负例类型：`replace_object`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："A laptop computer and a desktop computer on a white desk"
- 正描述 2："The white desk has a laptop computer and a desktop computer positioned on it."
- 负描述："A tablet and a desktop computer on a white desk."
- 自动来源：`positive_1` / "A laptop computer and a desktop computer on a white desk"
- 正确片段："laptop computer and a desktop computer on a white desk"
- 错误片段："tablet and a desktop computer on a white desk."
- 正确片段 token：IDs `[3090, 875, 1506, 4818, 376, 299, 1453, 110, 119, 1506, 4818, 619, 299, 654, 1078, 1453, 110]`；pieces `["Ġla", "pt", "op", "Ġcomputer", "Ġand", "Ġa", "Ġdes", "k", "t", "op", "Ġcomputer", "Ġon", "Ġa", "Ġwh", "ite", "Ġdes", "k"]`；decode " laptop computer and a desktop computer on a white desk"
- 错误片段 token：IDs `[2630, 119, 376, 299, 1453, 110, 119, 1506, 4818, 619, 299, 654, 1078, 1453, 110, 49]`；pieces `["Ġtable", "t", "Ġand", "Ġa", "Ġdes", "k", "t", "op", "Ġcomputer", "Ġon", "Ġa", "Ġwh", "ite", "Ġdes", "k", "."]`；decode " tablet and a desktop computer on a white desk."
- 自动分类：`complex_edit`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因："non_contiguous_edit_blocks=2;obvious_rewrite_by_fixed_coverage_rule"
- Token 边界提示：[]

## 负例类型：replace_relation

候选 `1406` 条，本节抽取 `30` 条。

### 1. `replace_relation:1026`

- 负例类型：`replace_relation`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："A bunch of sheep are walking around bored."
- 正描述 2："A herd of bored sheep are roaming around."
- 负描述："A bunch of sheep are running through the field excitedly."
- 自动来源：`positive_1` / "A bunch of sheep are walking around bored."
- 正确片段："walking around bored"
- 错误片段："running through the field excitedly"
- 正确片段 token：IDs `[339, 352, 1237, 3364, 363, 1239, 103]`；pieces `["Ġw", "al", "king", "Ġaround", "Ġb", "ore", "d"]`；decode " walking around bored"
- 错误片段 token：IDs `[3161, 1795, 2309, 309, 4749, 719, 102, 2633, 542]`；pieces `["Ġrun", "ning", "Ġthrough", "Ġthe", "Ġfield", "Ġex", "c", "ited", "ly"]`；decode " running through the field excitedly"
- 自动分类：`unique_alignment`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因：null
- Token 边界提示：[]

### 2. `replace_relation:1029`

- 负例类型：`replace_relation`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："A person laying on a bathroom floor next to a toilet."
- 正描述 2："A person lies beside a toilet on the bathroom floor."
- 负描述："A person sitting on a bathroom floor next to a toilet."
- 自动来源：`positive_1` / "A person laying on a bathroom floor next to a toilet."
- 正确片段："lay"
- 错误片段："sitt"
- 正确片段 token：IDs `[406, 655, 350]`；pieces `["Ġl", "ay", "ing"]`；decode " laying"
- 错误片段 token：IDs `[5305, 2912]`；pieces `["Ġsit", "ting"]`；decode " sitting"
- 自动分类：`unique_alignment`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因：null
- Token 边界提示：[]

### 3. `replace_relation:1048`

- 负例类型：`replace_relation`
- 阶段三范围：`formal`；certifying formal：`False`
- 正描述 1："A red truck sitting on a grassy field next to other trucks."
- 正描述 2："The red truck is stationed alongside other trucks on the grassy field."
- 负描述："A red truck driving on a grassy field next to other trucks."
- 自动来源：`positive_1` / "A red truck sitting on a grassy field next to other trucks."
- 正确片段："sitt"
- 错误片段："driv"
- 正确片段 token：IDs `[5305, 2912]`；pieces `["Ġsit", "ting"]`；decode " sitting"
- 错误片段 token：IDs `[5893, 4917]`；pieces `["Ġdr", "iving"]`；decode " driving"
- 自动分类：`unique_alignment`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因：null
- Token 边界提示：[]

### 4. `replace_relation:1110`

- 负例类型：`replace_relation`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："A cat standing in front of a tv on a tv stand."
- 正描述 2："The cat stands in front of a tv which is positioned on a tv stand."
- 负描述："A cat standing in front of a tv next to a tv stand."
- 自动来源：`positive_1` / "A cat standing in front of a tv on a tv stand."
- 正确片段："on"
- 错误片段："next to"
- 正确片段 token：IDs `[619]`；pieces `["Ġon"]`；decode " on"
- 错误片段 token：IDs `[4658, 364]`；pieces `["Ġnext", "Ġto"]`；decode " next to"
- 自动分类：`unique_alignment`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因：null
- Token 边界提示：[]

### 5. `replace_relation:1168`

- 负例类型：`replace_relation`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："A group of people looking at some kind of show or exhibit"
- 正描述 2："A show or exhibit is being obeserved by a group of people."
- 负描述："A group of people ignoring some kind of show or exhibit."
- 自动来源：`positive_1` / "A group of people looking at some kind of show or exhibit"
- 正确片段："looking at some kind of show or exhibit"
- 错误片段："ignoring some kind of show or exhibit."
- 正确片段 token：IDs `[3125, 1248, 2104, 914, 916, 354, 5950, 522, 719, 107, 676, 338]`；pieces `["Ġlooking", "Ġat", "Ġsome", "Ġk", "ind", "Ġof", "Ġshow", "Ġor", "Ġex", "h", "ib", "it"]`；decode " looking at some kind of show or exhibit"
- 错误片段 token：IDs `[256, 1289, 336, 350, 2104, 914, 916, 354, 5950, 522, 719, 107, 676, 338, 49]`；pieces `["Ġ", "ign", "or", "ing", "Ġsome", "Ġk", "ind", "Ġof", "Ġshow", "Ġor", "Ġex", "h", "ib", "it", "."]`；decode " ignoring some kind of show or exhibit."
- 自动分类：`complex_edit`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因："non_contiguous_edit_blocks=2;obvious_rewrite_by_fixed_coverage_rule"
- Token 边界提示：[]

### 6. `replace_relation:1209`

- 负例类型：`replace_relation`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："A young person kneeling down while riding skis."
- 正描述 2："While riding skiis, a young person is kneeling down."
- 负描述："A young person standing upright while riding skis."
- 自动来源：`positive_1` / "A young person kneeling down while riding skis."
- 正确片段："kneeling down"
- 错误片段："standing upright"
- 正确片段 token：IDs `[914, 1763, 446, 350, 4076]`；pieces `["Ġk", "ne", "el", "ing", "Ġdown"]`；decode " kneeling down"
- 错误片段 token：IDs `[2823, 350, 1253, 4853]`；pieces `["Ġstand", "ing", "Ġup", "right"]`；decode " standing upright"
- 自动分类：`unique_alignment`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因：null
- Token 边界提示：[]

### 7. `replace_relation:128`

- 负例类型：`replace_relation`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："A cat sitting on a bench in front of a building."
- 正描述 2："A bench is in front of a building, and a cat is sitting on it."
- 负描述："A cat lying on a bench in front of a building."
- 自动来源：`positive_1` / "A cat sitting on a bench in front of a building."
- 正确片段："sitt"
- 错误片段："ly"
- 正确片段 token：IDs `[5305, 2912]`；pieces `["Ġsit", "ting"]`；decode " sitting"
- 错误片段 token：IDs `[406, 124, 350]`；pieces `["Ġl", "y", "ing"]`；decode " lying"
- 自动分类：`unique_alignment`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因：null
- Token 边界提示：[]

### 8. `replace_relation:138`

- 负例类型：`replace_relation`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："A person sitting in a chair with a cat and a laptop."
- 正描述 2："A person sits in a chair next to a laptop and a cat."
- 负描述："A person lying down in a chair with a cat and a laptop."
- 自动来源：`positive_1` / "A person sitting in a chair with a cat and a laptop."
- 正确片段："sitting"
- 错误片段："lying down"
- 正确片段 token：IDs `[5305, 2912]`；pieces `["Ġsit", "ting"]`；decode " sitting"
- 错误片段 token：IDs `[406, 124, 350, 4076]`；pieces `["Ġl", "y", "ing", "Ġdown"]`；decode " lying down"
- 自动分类：`unique_alignment`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因：null
- Token 边界提示：[]

### 9. `replace_relation:1398`

- 负例类型：`replace_relation`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："Three workers stand next to each other with their baked goods behind them."
- 正描述 2："Three employees are positioned side by side in front of their baked goods."
- 负描述："Three workers stand opposite each other with their baked goods behind them."
- 自动来源：`positive_1` / "Three workers stand next to each other with their baked goods behind them."
- 正确片段："next to"
- 错误片段："opposite"
- 正确片段 token：IDs `[4658, 364]`；pieces `["Ġnext", "Ġto"]`；decode " next to"
- 错误片段 token：IDs `[319, 737, 1312, 1078]`；pieces `["Ġo", "pp", "os", "ite"]`；decode " opposite"
- 自动分类：`unique_alignment`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因：null
- Token 边界提示：[]

### 10. `replace_relation:186`

- 负例类型：`replace_relation`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："Black cat with green eyes sitting in a bathroom sink."
- 正描述 2："Green-eyed black cat sitting in a bathroom sink."
- 负描述："A black cat with green eyes sleeping in a bathroom sink."
- 自动来源：`positive_1` / "Black cat with green eyes sitting in a bathroom sink."
- 正确片段："Black cat with green eyes sitt"
- 错误片段："A black cat with green eyes sleep"
- 正确片段 token：IDs `[69, 111, 1637, 3706, 599, 5921, 413, 124, 329, 5305, 2912]`；pieces `["B", "l", "ack", "Ġcat", "Ġwith", "Ġgreen", "Ġe", "y", "es", "Ġsit", "ting"]`；decode "Black cat with green eyes sitting"
- 错误片段 token：IDs `[68, 2597, 1637, 3706, 599, 5921, 413, 124, 329, 316, 361, 1522, 350]`；pieces `["A", "Ġbl", "ack", "Ġcat", "Ġwith", "Ġgreen", "Ġe", "y", "es", "Ġs", "le", "ep", "ing"]`；decode "A black cat with green eyes sleeping"
- 自动分类：`complex_edit`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因："non_contiguous_edit_blocks=2"
- Token 边界提示：[]

### 11. `replace_relation:202`

- 负例类型：`replace_relation`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："An elephant standing in a shaded clearing in a wooded area."
- 正描述 2："A shaded clearing in a wooded area features an elephant standing in it."
- 负描述："An elephant lying in a shaded clearing in a wooded area."
- 自动来源：`positive_1` / "An elephant standing in a shaded clearing in a wooded area."
- 正确片段："stand"
- 错误片段："ly"
- 正确片段 token：IDs `[2823]`；pieces `["Ġstand"]`；decode " stand"
- 错误片段 token：IDs `[406, 124]`；pieces `["Ġl", "y"]`；decode " ly"
- 自动分类：`unique_alignment`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因：null
- Token 边界提示：[]

### 12. `replace_relation:239`

- 负例类型：`replace_relation`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："A male baseball player wearing red and white is up to bat."
- 正描述 2："A baseball player in red and white is up to bat."
- 负描述："A male baseball player wearing red and white is running to first base."
- 自动来源：`positive_1` / "A male baseball player wearing red and white is up to bat."
- 正确片段："up to bat"
- 错误片段："running to first base"
- 正确片段 token：IDs `[1253, 364, 363, 314]`；pieces `["Ġup", "Ġto", "Ġb", "at"]`；decode " up to bat"
- 错误片段 token：IDs `[3161, 1795, 364, 1710, 4933]`；pieces `["Ġrun", "ning", "Ġto", "Ġfirst", "Ġbase"]`；decode " running to first base"
- 自动分类：`complex_edit`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因："non_contiguous_edit_blocks=2"
- Token 边界提示：[]

### 13. `replace_relation:29`

- 负例类型：`replace_relation`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："A hand holding a spraying hose to a toilet bowl in a small toilet stall."
- 正描述 2："A person holds a spraying hose near to a restroom stall's toilet bowl."
- 负描述："A hand holding a spraying hose away from a toilet bowl in a small toilet stall."
- 自动来源：`positive_1` / "A hand holding a spraying hose to a toilet bowl in a small toilet stall."
- 正确片段："to"
- 错误片段："away from"
- 正确片段 token：IDs `[364]`；pieces `["Ġto"]`；decode " to"
- 错误片段 token：IDs `[299, 5054, 961]`；pieces `["Ġa", "way", "Ġfrom"]`；decode " away from"
- 自动分类：`unique_alignment`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因：null
- Token 边界提示：[]

### 14. `replace_relation:331`

- 负例类型：`replace_relation`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："Shadows are cast onto the side of a train because of the sun."
- 正描述 2："The sun cast shadows onto the side of the train."
- 负描述："Shadows are cast over the side of a train because of the sun."
- 自动来源：`positive_1` / "Shadows are cast onto the side of a train because of the sun."
- 正确片段："nto"
- 错误片段："ver"
- 正确片段 token：IDs `[619, 2263]`；pieces `["Ġon", "to"]`；decode " onto"
- 错误片段 token：IDs `[2141]`；pieces `["Ġover"]`；decode " over"
- 自动分类：`unique_alignment`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因：null
- Token 边界提示：[]

### 15. `replace_relation:36`

- 负例类型：`replace_relation`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："A stop sign vandalized with an eating animals sticker below the word stop."
- 正描述 2："The eating animals sticker is positioned below the word stop on the stop sign that has been vandalized."
- 负描述："A stop sign vandalized with an eating animals sticker above the word stop."
- 自动来源：`positive_1` / "A stop sign vandalized with an eating animals sticker below the word stop."
- 正确片段："below"
- 错误片段："above"
- 正确片段 token：IDs `[4021, 451]`；pieces `["Ġbel", "ow"]`；decode " below"
- 错误片段 token：IDs `[6264]`；pieces `["Ġabove"]`；decode " above"
- 自动分类：`unique_alignment`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因：null
- Token 边界提示：[]

### 16. `replace_relation:405`

- 负例类型：`replace_relation`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："A little child standing in a field below a kite."
- 正描述 2："The kite is above the little child standing in a field."
- 负描述："A little child running in a field below a kite."
- 自动来源：`positive_1` / "A little child standing in a field below a kite."
- 正确片段："stand"
- 错误片段："runn"
- 正确片段 token：IDs `[2823, 350]`；pieces `["Ġstand", "ing"]`；decode " standing"
- 错误片段 token：IDs `[3161, 1795]`；pieces `["Ġrun", "ning"]`；decode " running"
- 自动分类：`unique_alignment`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因：null
- Token 边界提示：[]

### 17. `replace_relation:430`

- 负例类型：`replace_relation`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："The plane is parked at the gate at the airport terminal."
- 正描述 2："The airport terminal gate is where the plane is parked."
- 负描述："The plane is departing from the gate at the airport terminal."
- 自动来源：`positive_1` / "The plane is parked at the gate at the airport terminal."
- 正确片段："parked at"
- 错误片段："departing from"
- 正确片段 token：IDs `[344, 2000, 382, 1248]`；pieces `["Ġp", "ark", "ed", "Ġat"]`；decode " parked at"
- 错误片段 token：IDs `[2486, 913, 350, 961]`；pieces `["Ġdep", "art", "ing", "Ġfrom"]`；decode " departing from"
- 自动分类：`unique_alignment`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因：null
- Token 边界提示：[]

### 18. `replace_relation:431`

- 负例类型：`replace_relation`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："A person on a skateboard is coming up a ramp."
- 正描述 2："A skateboarder is coming up a ramp."
- 负描述："A person near a skateboard is coming up a ramp."
- 自动来源：`positive_1` / "A person on a skateboard is coming up a ramp."
- 正确片段："on"
- 错误片段："near"
- 正确片段 token：IDs `[619]`；pieces `["Ġon"]`；decode " on"
- 错误片段 token：IDs `[730, 370]`；pieces `["Ġne", "ar"]`；decode " near"
- 自动分类：`unique_alignment`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因：null
- Token 边界提示：[]

### 19. `replace_relation:457`

- 负例类型：`replace_relation`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："A child wearing yellow is holding a pizza in a box."
- 正描述 2："A child in a yellow outfit is holding a pizza in a box."
- 负描述："A child not wearing yellow is holding a pizza in a box."
- 自动来源：`positive_1` / "A child wearing yellow is holding a pizza in a box."
- 正确片段：""
- 错误片段："not "
- 正确片段 token：IDs `[]`；pieces `[]`；decode ""
- 错误片段 token：IDs `[1027]`；pieces `["Ġnot"]`；decode " not"
- 自动分类：`unique_alignment`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因：null
- Token 边界提示：[]

### 20. `replace_relation:54`

- 负例类型：`replace_relation`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："A sign on a sidewalk has a teddy bear on it."
- 正描述 2："The teddy bear is on a sign located on a sidewalk."
- 负描述："A sign beside a sidewalk has a teddy bear on it."
- 自动来源：`positive_1` / "A sign on a sidewalk has a teddy bear on it."
- 正确片段："on"
- 错误片段："beside"
- 正确片段 token：IDs `[619]`；pieces `["Ġon"]`；decode " on"
- 错误片段 token：IDs `[363, 329, 688]`；pieces `["Ġb", "es", "ide"]`；decode " beside"
- 自动分类：`unique_alignment`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因：null
- Token 边界提示：[]

### 21. `replace_relation:616`

- 负例类型：`replace_relation`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："A person wearing a hat while standing in front of a bathroom mirror."
- 正描述 2："A person wearing a hat is standing in front of a bathroom mirror."
- 负描述："A person holding a hat while standing in front of a bathroom mirror."
- 自动来源：`positive_1` / "A person wearing a hat while standing in front of a bathroom mirror."
- 正确片段："wear"
- 错误片段："hold"
- 正确片段 token：IDs `[796, 370]`；pieces `["Ġwe", "ar"]`；decode " wear"
- 错误片段 token：IDs `[429, 2569]`；pieces `["Ġh", "old"]`；decode " hold"
- 自动分类：`unique_alignment`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因：null
- Token 边界提示：[]

### 22. `replace_relation:643`

- 负例类型：`replace_relation`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："a cat laying on top of a chair in the living room"
- 正描述 2："The cat is positioned on top of the chair in the living room."
- 负描述："A cat laying next to a chair in the living room."
- 自动来源：`positive_1` / "a cat laying on top of a chair in the living room"
- 正确片段："a cat laying on top of a chair in the living room"
- 错误片段："A cat laying next to a chair in the living room."
- 正确片段 token：IDs `[100, 3706, 406, 655, 350, 619, 2924, 354, 299, 890, 3709, 353, 309, 406, 4917, 1552, 444]`；pieces `["a", "Ġcat", "Ġl", "ay", "ing", "Ġon", "Ġtop", "Ġof", "Ġa", "Ġch", "air", "Ġin", "Ġthe", "Ġl", "iving", "Ġro", "om"]`；decode "a cat laying on top of a chair in the living room"
- 错误片段 token：IDs `[68, 3706, 406, 655, 350, 4658, 364, 299, 890, 3709, 353, 309, 406, 4917, 1552, 444, 49]`；pieces `["A", "Ġcat", "Ġl", "ay", "ing", "Ġnext", "Ġto", "Ġa", "Ġch", "air", "Ġin", "Ġthe", "Ġl", "iving", "Ġro", "om", "."]`；decode "A cat laying next to a chair in the living room."
- 自动分类：`complex_edit`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因："non_contiguous_edit_blocks=3;obvious_rewrite_by_fixed_coverage_rule"
- Token 边界提示：[]

### 23. `replace_relation:665`

- 负例类型：`replace_relation`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："a dirty fridge standing in the middle of a patio"
- 正描述 2："The patio has a dirty fridge standing in its center."
- 负描述："A dirty fridge leaning against the wall on the patio."
- 自动来源：`positive_1` / "a dirty fridge standing in the middle of a patio"
- 正确片段："a dirty fridge standing in the middle of a patio"
- 错误片段："A dirty fridge leaning against the wall on the patio."
- 正确片段 token：IDs `[100, 373, 639, 3915, 341, 117, 460, 583, 2823, 350, 353, 309, 351, 5032, 361, 354, 299, 4195, 3604]`；pieces `["a", "Ġd", "ir", "ty", "Ġf", "r", "id", "ge", "Ġstand", "ing", "Ġin", "Ġthe", "Ġm", "idd", "le", "Ġof", "Ġa", "Ġpat", "io"]`；decode "a dirty fridge standing in the middle of a patio"
- 错误片段 token：IDs `[68, 373, 639, 3915, 341, 117, 460, 583, 848, 325, 350, 6113, 432, 309, 339, 1266, 619, 309, 4195, 3604, 49]`；pieces `["A", "Ġd", "ir", "ty", "Ġf", "r", "id", "ge", "Ġle", "an", "ing", "Ġagain", "st", "Ġthe", "Ġw", "all", "Ġon", "Ġthe", "Ġpat", "io", "."]`；decode "A dirty fridge leaning against the wall on the patio."
- 自动分类：`complex_edit`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因："non_contiguous_edit_blocks=4;obvious_rewrite_by_fixed_coverage_rule"
- Token 边界提示：[]

### 24. `replace_relation:707`

- 负例类型：`replace_relation`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："A person standing at a kitchen counter with a child and a dog is behind them."
- 正描述 2："At a kitchen counter, a person is standing with a child and a dog is behind them."
- 负描述："A person sitting at a kitchen counter with a child and a dog is behind them."
- 自动来源：`positive_1` / "A person standing at a kitchen counter with a child and a dog is behind them."
- 正确片段："tand"
- 错误片段："itt"
- 正确片段 token：IDs `[2823, 350]`；pieces `["Ġstand", "ing"]`；decode " standing"
- 错误片段 token：IDs `[5305, 2912]`；pieces `["Ġsit", "ting"]`；decode " sitting"
- 自动分类：`unique_alignment`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因：null
- Token 边界提示：[]

### 25. `replace_relation:717`

- 负例类型：`replace_relation`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："Four bananas in a bunch with brown dots"
- 正描述 2："A cluster of four bananas with brown spots."
- 负描述："Four bananas separate from each other with brown dots."
- 自动来源：`positive_1` / "Four bananas in a bunch with brown dots"
- 正确片段："in a bunch with brown dots"
- 错误片段："separate from each other with brown dots."
- 正确片段 token：IDs `[353, 299, 363, 651, 550, 599, 363, 2079, 113, 373, 593, 118]`；pieces `["Ġin", "Ġa", "Ġb", "un", "ch", "Ġwith", "Ġb", "row", "n", "Ġd", "ot", "s"]`；decode " in a bunch with brown dots"
- 错误片段 token：IDs `[762, 4671, 557, 961, 1766, 1649, 599, 363, 2079, 113, 373, 593, 118, 49]`；pieces `["Ġse", "par", "ate", "Ġfrom", "Ġeach", "Ġother", "Ġwith", "Ġb", "row", "n", "Ġd", "ot", "s", "."]`；decode " separate from each other with brown dots."
- 自动分类：`complex_edit`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因："non_contiguous_edit_blocks=2"
- Token 边界提示：[]

### 26. `replace_relation:782`

- 负例类型：`replace_relation`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："this bathroom has pink tiles in the shower and is painted blue"
- 正描述 2："The shower in this bathroom has pink tiles, and the bathroom is painted blue."
- 负描述："This bathroom has pink tiles nowhere in the shower and is painted blue."
- 自动来源：`positive_1` / "this bathroom has pink tiles in the shower and is painted blue"
- 正确片段："this bathroom has pink tiles in the shower and is painted blue"
- 错误片段："This bathroom has pink tiles nowhere in the shower and is painted blue."
- 正确片段 token：IDs `[495, 324, 363, 1831, 393, 444, 1290, 344, 3010, 297, 485, 329, 353, 309, 1128, 2257, 376, 395, 5063, 4587, 4300]`；pieces `["th", "is", "Ġb", "ath", "ro", "om", "Ġhas", "Ġp", "ink", "Ġt", "il", "es", "Ġin", "Ġthe", "Ġsh", "ower", "Ġand", "Ġis", "Ġpain", "ted", "Ġblue"]`；decode "this bathroom has pink tiles in the shower and is painted blue"
- 错误片段 token：IDs `[2224, 363, 1831, 393, 444, 1290, 344, 3010, 297, 485, 329, 4787, 2503, 353, 309, 1128, 2257, 376, 395, 5063, 4587, 4300, 49]`；pieces `["This", "Ġb", "ath", "ro", "om", "Ġhas", "Ġp", "ink", "Ġt", "il", "es", "Ġnow", "here", "Ġin", "Ġthe", "Ġsh", "ower", "Ġand", "Ġis", "Ġpain", "ted", "Ġblue", "."]`；decode "This bathroom has pink tiles nowhere in the shower and is painted blue."
- 自动分类：`complex_edit`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因："non_contiguous_edit_blocks=3;obvious_rewrite_by_fixed_coverage_rule"
- Token 边界提示：[]

### 27. `replace_relation:799`

- 负例类型：`replace_relation`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："Two people bump their cell phones together at a party"
- 正描述 2："Cell phones of two people are being bumped togather at a party."
- 负描述："Two people swap their cell phones together at a party."
- 自动来源：`positive_1` / "Two people bump their cell phones together at a party"
- 正确片段："bump their cell phones together at a party"
- 错误片段："swap their cell phones together at a party."
- 正确片段 token：IDs `[363, 457, 115, 1635, 317, 1272, 2001, 310, 329, 5169, 1248, 299, 1609, 124]`；pieces `["Ġb", "um", "p", "Ġtheir", "Ġc", "ell", "Ġph", "on", "es", "Ġtogether", "Ġat", "Ġa", "Ġpart", "y"]`；decode " bump their cell phones together at a party"
- 错误片段 token：IDs `[316, 122, 1175, 1635, 317, 1272, 2001, 310, 329, 5169, 1248, 299, 1609, 124, 49]`；pieces `["Ġs", "w", "ap", "Ġtheir", "Ġc", "ell", "Ġph", "on", "es", "Ġtogether", "Ġat", "Ġa", "Ġpart", "y", "."]`；decode " swap their cell phones together at a party."
- 自动分类：`complex_edit`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因："non_contiguous_edit_blocks=2;obvious_rewrite_by_fixed_coverage_rule"
- Token 边界提示：[]

### 28. `replace_relation:851`

- 负例类型：`replace_relation`
- 阶段三范围：`pilot`；certifying formal：`False`
- 正描述 1："a huge suitcase with a bunch of stickers on it"
- 正描述 2："A large suitcase with numerous stickers adorning its surface."
- 负描述："A huge suitcase without any stickers on it."
- 自动来源：`positive_1` / "a huge suitcase with a bunch of stickers on it"
- 正确片段："a huge suitcase with a bunch of stickers on it"
- 错误片段："A huge suitcase without any stickers on it."
- 正确片段 token：IDs `[100, 429, 120, 583, 855, 338, 4220, 599, 299, 363, 651, 550, 354, 580, 2437, 496, 619, 563]`；pieces `["a", "Ġh", "u", "ge", "Ġsu", "it", "case", "Ġwith", "Ġa", "Ġb", "un", "ch", "Ġof", "Ġst", "ick", "ers", "Ġon", "Ġit"]`；decode "a huge suitcase with a bunch of stickers on it"
- 错误片段 token：IDs `[68, 429, 120, 583, 855, 338, 4220, 4007, 1149, 580, 2437, 496, 619, 563, 49]`；pieces `["A", "Ġh", "u", "ge", "Ġsu", "it", "case", "Ġwithout", "Ġany", "Ġst", "ick", "ers", "Ġon", "Ġit", "."]`；decode "A huge suitcase without any stickers on it."
- 自动分类：`complex_edit`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因："non_contiguous_edit_blocks=3;obvious_rewrite_by_fixed_coverage_rule"
- Token 边界提示：[]

### 29. `replace_relation:861`

- 负例类型：`replace_relation`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："A person holding a camera is taking a picture."
- 正描述 2："A picture is being taken by a person holding a camera."
- 负描述："A person putting away a camera."
- 自动来源：`None` / null
- 正确片段：""
- 错误片段：""
- 正确片段 token：IDs `[]`；pieces `[]`；decode ""
- 错误片段 token：IDs `[]`；pieces `[]`；decode ""
- 自动分类：`ambiguous_source`
- 来源规则："character_and_token_distance_rankings_conflict"
- 失败原因："character_and_token_distance_rankings_conflict"
- Token 边界提示：[]

### 30. `replace_relation:90`

- 负例类型：`replace_relation`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："A pizza is shown with various toppings on it."
- 正描述 2："The various toppings are on top of the pizza."
- 负描述："A pizza is being enjoyed by people with various toppings on it."
- 自动来源：`positive_1` / "A pizza is shown with various toppings on it."
- 正确片段："shown"
- 错误片段："being enjoyed by people"
- 正确片段 token：IDs `[1128, 2791]`；pieces `["Ġsh", "own"]`；decode " shown"
- 错误片段 token：IDs `[4016, 1057, 109, 4117, 382, 769, 2975]`；pieces `["Ġbeing", "Ġen", "j", "oy", "ed", "Ġby", "Ġpeople"]`；decode " being enjoyed by people"
- 自动分类：`unique_alignment`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因：null
- Token 边界提示：[]

## 负例类型：swap_atribute

候选 `666` 条，本节抽取 `30` 条。

### 1. `swap_atribute:124`

- 负例类型：`swap_atribute`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："Two persons waiting at a bench next to a street."
- 正描述 2："Two persons are sitting on a bench next to a street."
- 负描述："A person waiting at a bench next to two streets."
- 自动来源：`positive_1` / "Two persons waiting at a bench next to a street."
- 正确片段："Two persons waiting at a bench next to a street"
- 错误片段："A person waiting at a bench next to two streets"
- 正确片段 token：IDs `[87, 122, 114, 2198, 118, 339, 100, 5945, 1248, 299, 6141, 550, 4658, 364, 299, 5941, 439]`；pieces `["T", "w", "o", "Ġperson", "s", "Ġw", "a", "iting", "Ġat", "Ġa", "Ġben", "ch", "Ġnext", "Ġto", "Ġa", "Ġstre", "et"]`；decode "Two persons waiting at a bench next to a street"
- 错误片段 token：IDs `[68, 2198, 339, 100, 5945, 1248, 299, 6141, 550, 4658, 364, 2102, 5941, 3391]`；pieces `["A", "Ġperson", "Ġw", "a", "iting", "Ġat", "Ġa", "Ġben", "ch", "Ġnext", "Ġto", "Ġtwo", "Ġstre", "ets"]`；decode "A person waiting at a bench next to two streets"
- 自动分类：`complex_edit`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因："non_contiguous_edit_blocks=2;obvious_rewrite_by_fixed_coverage_rule"
- Token 边界提示：[]

### 2. `swap_atribute:140`

- 负例类型：`swap_atribute`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："Four picture collage of a snowboarder wearing a red jacket and brown pants going down a snowy mountain side."
- 正描述 2："collage of four pictures of a snowboarder wearing a red jacket and brown pants descending a snowy mountain slope."
- 负描述："Four picture collage of a snowboarder wearing a brown jacket and red pants going down a snowy mountain side."
- 自动来源：`positive_1` / "Four picture collage of a snowboarder wearing a red jacket and brown pants going down a snowy mountain side."
- 正确片段："red jacket and brown"
- 错误片段："brown jacket and red"
- 正确片段 token：IDs `[5534, 1315, 1637, 439, 376, 363, 2079, 113]`；pieces `["Ġred", "Ġj", "ack", "et", "Ġand", "Ġb", "row", "n"]`；decode " red jacket and brown"
- 错误片段 token：IDs `[363, 2079, 113, 1315, 1637, 439, 376, 5534]`；pieces `["Ġb", "row", "n", "Ġj", "ack", "et", "Ġand", "Ġred"]`；decode " brown jacket and red"
- 自动分类：`complex_edit`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因："non_contiguous_edit_blocks=2;word_order_change"
- Token 边界提示：[]

### 3. `swap_atribute:22`

- 负例类型：`swap_atribute`
- 阶段三范围：`pilot`；certifying formal：`False`
- 正描述 1："A person is sitting with two young children at a table"
- 正描述 2："A person is seated at a table with two young children."
- 负描述："Two persons with a young child at a table."
- 自动来源：`positive_1` / "A person is sitting with two young children at a table"
- 正确片段："A person is sitting with two young children at a table"
- 错误片段："Two persons with a young child at a table."
- 正确片段 token：IDs `[68, 2198, 395, 5305, 2912, 599, 2102, 401, 1685, 6109, 3193, 1248, 299, 2630]`；pieces `["A", "Ġperson", "Ġis", "Ġsit", "ting", "Ġwith", "Ġtwo", "Ġyou", "ng", "Ġchild", "ren", "Ġat", "Ġa", "Ġtable"]`；decode "A person is sitting with two young children at a table"
- 错误片段 token：IDs `[87, 122, 114, 2198, 118, 599, 299, 401, 1685, 6109, 1248, 299, 2630, 49]`；pieces `["T", "w", "o", "Ġperson", "s", "Ġwith", "Ġa", "Ġyou", "ng", "Ġchild", "Ġat", "Ġa", "Ġtable", "."]`；decode "Two persons with a young child at a table."
- 自动分类：`complex_edit`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因："non_contiguous_edit_blocks=4;obvious_rewrite_by_fixed_coverage_rule"
- Token 边界提示：[]

### 4. `swap_atribute:227`

- 负例类型：`swap_atribute`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："There is a fire hydrant next to a red sign"
- 正描述 2："The red sign is adjacent to the fire hydrant."
- 负描述："There is a red hydrant next to a fire sign."
- 自动来源：`positive_1` / "There is a fire hydrant next to a red sign"
- 正确片段："fire hydrant next to a red sign"
- 错误片段："red hydrant next to a fire sign."
- 正确片段 token：IDs `[341, 1475, 5548, 103, 117, 811, 4658, 364, 299, 5534, 2185]`；pieces `["Ġf", "ire", "Ġhy", "d", "r", "ant", "Ġnext", "Ġto", "Ġa", "Ġred", "Ġsign"]`；decode " fire hydrant next to a red sign"
- 错误片段 token：IDs `[5534, 5548, 103, 117, 811, 4658, 364, 299, 341, 1475, 2185, 49]`；pieces `["Ġred", "Ġhy", "d", "r", "ant", "Ġnext", "Ġto", "Ġa", "Ġf", "ire", "Ġsign", "."]`；decode " red hydrant next to a fire sign."
- 自动分类：`complex_edit`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因："non_contiguous_edit_blocks=3;word_order_change"
- Token 边界提示：[]

### 5. `swap_atribute:265`

- 负例类型：`swap_atribute`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："A marble table with white plate holding a pizza."
- 正描述 2："A white plate with a pizza is positioned on a marble table."
- 负描述："A white table with marble plate holding a pizza."
- 自动来源：`positive_1` / "A marble table with white plate holding a pizza."
- 正确片段："marble table with whit"
- 错误片段："white table with marbl"
- 正确片段 token：IDs `[4852, 2129, 2630, 599, 654, 1078]`；pieces `["Ġmar", "ble", "Ġtable", "Ġwith", "Ġwh", "ite"]`；decode " marble table with white"
- 错误片段 token：IDs `[654, 1078, 2630, 599, 4852, 2129]`；pieces `["Ġwh", "ite", "Ġtable", "Ġwith", "Ġmar", "ble"]`；decode " white table with marble"
- 自动分类：`complex_edit`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因："non_contiguous_edit_blocks=2"
- Token 边界提示：[]

### 6. `swap_atribute:276`

- 负例类型：`swap_atribute`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："A box of six pastries containing two chocolate doughnuts, one strawberry, one glaze, and two glazed crullers."
- 正描述 2："A box of six pastries, including two chocolate doughnuts, one strawberry, one glaze, and two glazed crullers."
- 负描述："A box of six pastries containing two strawberry doughnuts, one chocolate, one glaze, and two glazed crullers."
- 自动来源：`positive_1` / "A box of six pastries containing two chocolate doughnuts, one strawberry, one glaze, and two glazed crullers."
- 正确片段："chocolate doughnuts, one strawberry"
- 错误片段："strawberry doughnuts, one chocolate"
- 正确片段 token：IDs `[890, 1427, 500, 557, 373, 3113, 113, 501, 118, 47, 1623, 580, 559, 122, 2009, 1557]`；pieces `["Ġch", "oc", "ol", "ate", "Ġd", "ough", "n", "ut", "s", ",", "Ġone", "Ġst", "ra", "w", "ber", "ry"]`；decode " chocolate doughnuts, one strawberry"
- 错误片段 token：IDs `[580, 559, 122, 2009, 1557, 373, 3113, 113, 501, 118, 47, 1623, 890, 1427, 500, 557]`；pieces `["Ġst", "ra", "w", "ber", "ry", "Ġd", "ough", "n", "ut", "s", ",", "Ġone", "Ġch", "oc", "ol", "ate"]`；decode " strawberry doughnuts, one chocolate"
- 自动分类：`complex_edit`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因："non_contiguous_edit_blocks=2;word_order_change"
- Token 边界提示：[]

### 7. `swap_atribute:282`

- 负例类型：`swap_atribute`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："A large dog tied to a yellow fire hydrant.\n"
- 正描述 2："A yellow fire hydrant has a large dog tied to it."
- 负描述："A yellow dog tied to a large fire hydrant."
- 自动来源：`positive_1` / "A large dog tied to a yellow fire hydrant.\n"
- 正确片段："large dog tied to a yellow fire hydrant.\n"
- 错误片段："yellow dog tied to a large fire hydrant."
- 正确片段 token：IDs `[2994, 1041, 106, 297, 3267, 364, 299, 385, 446, 1030, 341, 1475, 5548, 103, 117, 811, 49, 234]`；pieces `["Ġlarge", "Ġdo", "g", "Ġt", "ied", "Ġto", "Ġa", "Ġy", "el", "low", "Ġf", "ire", "Ġhy", "d", "r", "ant", ".", "Ċ"]`；decode " large dog tied to a yellow fire hydrant.\n"
- 错误片段 token：IDs `[385, 446, 1030, 1041, 106, 297, 3267, 364, 299, 2994, 341, 1475, 5548, 103, 117, 811, 49]`；pieces `["Ġy", "el", "low", "Ġdo", "g", "Ġt", "ied", "Ġto", "Ġa", "Ġlarge", "Ġf", "ire", "Ġhy", "d", "r", "ant", "."]`；decode " yellow dog tied to a large fire hydrant."
- 自动分类：`complex_edit`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因："non_contiguous_edit_blocks=2;word_order_change;obvious_rewrite_by_fixed_coverage_rule"
- Token 边界提示：[]

### 8. `swap_atribute:288`

- 负例类型：`swap_atribute`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："a bathroom with black walls and a toilet with a silver toilet seat"
- 正描述 2："The bathroom has black walls and a toilet with a silver toilet seat."
- 负描述："a bathroom with a silver walls and a toilet with a black toilet seat."
- 自动来源：`positive_1` / "a bathroom with black walls and a toilet with a silver toilet seat"
- 正确片段："black walls and a toilet with a silver toilet seat"
- 错误片段："a silver walls and a toilet with a black toilet seat."
- 正确片段 token：IDs `[2597, 1637, 339, 1266, 118, 376, 299, 364, 1299, 119, 599, 299, 4663, 652, 364, 1299, 119, 762, 314]`；pieces `["Ġbl", "ack", "Ġw", "all", "s", "Ġand", "Ġa", "Ġto", "ile", "t", "Ġwith", "Ġa", "Ġsil", "ver", "Ġto", "ile", "t", "Ġse", "at"]`；decode " black walls and a toilet with a silver toilet seat"
- 错误片段 token：IDs `[299, 4663, 652, 339, 1266, 118, 376, 299, 364, 1299, 119, 599, 299, 2597, 1637, 364, 1299, 119, 762, 314, 49]`；pieces `["Ġa", "Ġsil", "ver", "Ġw", "all", "s", "Ġand", "Ġa", "Ġto", "ile", "t", "Ġwith", "Ġa", "Ġbl", "ack", "Ġto", "ile", "t", "Ġse", "at", "."]`；decode " a silver walls and a toilet with a black toilet seat."
- 自动分类：`complex_edit`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因："non_contiguous_edit_blocks=3;obvious_rewrite_by_fixed_coverage_rule"
- Token 边界提示：[]

### 9. `swap_atribute:317`

- 负例类型：`swap_atribute`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："A blue pot of tomato sauce with a wooden ladle."
- 正描述 2："A wooden ladle is positioned inside a blue pot of tomato sauce."
- 负描述："A wooden pot of tomato sauce with a blue ladle."
- 自动来源：`positive_1` / "A blue pot of tomato sauce with a wooden ladle."
- 正确片段："blue pot of tomato sauce with a wooden"
- 错误片段："wooden pot of tomato sauce with a blue"
- 正确片段 token：IDs `[4300, 4915, 354, 364, 2728, 114, 316, 1900, 473, 599, 299, 339, 2166, 327]`；pieces `["Ġblue", "Ġpot", "Ġof", "Ġto", "mat", "o", "Ġs", "au", "ce", "Ġwith", "Ġa", "Ġw", "ood", "en"]`；decode " blue pot of tomato sauce with a wooden"
- 错误片段 token：IDs `[339, 2166, 327, 4915, 354, 364, 2728, 114, 316, 1900, 473, 599, 299, 4300]`；pieces `["Ġw", "ood", "en", "Ġpot", "Ġof", "Ġto", "mat", "o", "Ġs", "au", "ce", "Ġwith", "Ġa", "Ġblue"]`；decode " wooden pot of tomato sauce with a blue"
- 自动分类：`complex_edit`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因："non_contiguous_edit_blocks=2;word_order_change;obvious_rewrite_by_fixed_coverage_rule"
- Token 边界提示：[]

### 10. `swap_atribute:372`

- 负例类型：`swap_atribute`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："A little child holding a baseball bat on grass."
- 正描述 2："A baseball bat is being held by a little child."
- 负描述："A baseball child holding a little bat on grass."
- 自动来源：`positive_1` / "A little child holding a baseball bat on grass."
- 正确片段："little child holding a baseball"
- 错误片段："baseball child holding a little"
- 正确片段 token：IDs `[406, 338, 5395, 6109, 429, 2569, 350, 299, 4933, 101, 1266]`；pieces `["Ġl", "it", "tle", "Ġchild", "Ġh", "old", "ing", "Ġa", "Ġbase", "b", "all"]`；decode " little child holding a baseball"
- 错误片段 token：IDs `[4933, 101, 1266, 6109, 429, 2569, 350, 299, 406, 338, 5395]`；pieces `["Ġbase", "b", "all", "Ġchild", "Ġh", "old", "ing", "Ġa", "Ġl", "it", "tle"]`；decode " baseball child holding a little"
- 自动分类：`complex_edit`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因："non_contiguous_edit_blocks=2;word_order_change"
- Token 边界提示：[]

### 11. `swap_atribute:379`

- 负例类型：`swap_atribute`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："A street sign with flags on it and a building in the background."
- 正描述 2："A building with a street sign and flags in the background."
- 负描述："A building sign with flags on it and a street in the background."
- 自动来源：`positive_1` / "A street sign with flags on it and a building in the background."
- 正确片段："street sign with flags on it and a building"
- 错误片段："building sign with flags on it and a street"
- 正确片段 token：IDs `[5941, 439, 2185, 599, 3687, 1163, 118, 619, 563, 376, 299, 6331, 350]`；pieces `["Ġstre", "et", "Ġsign", "Ġwith", "Ġfl", "ag", "s", "Ġon", "Ġit", "Ġand", "Ġa", "Ġbuild", "ing"]`；decode " street sign with flags on it and a building"
- 错误片段 token：IDs `[6331, 350, 2185, 599, 3687, 1163, 118, 619, 563, 376, 299, 5941, 439]`；pieces `["Ġbuild", "ing", "Ġsign", "Ġwith", "Ġfl", "ag", "s", "Ġon", "Ġit", "Ġand", "Ġa", "Ġstre", "et"]`；decode " building sign with flags on it and a street"
- 自动分类：`complex_edit`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因："non_contiguous_edit_blocks=2;word_order_change;obvious_rewrite_by_fixed_coverage_rule"
- Token 边界提示：[]

### 12. `swap_atribute:389`

- 负例类型：`swap_atribute`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："A child asleep on a large bed under a mosquito net"
- 正描述 2："A mosquito net is positioned above a large bed where a child is sleeping."
- 负描述："A child asleep on a mosquito bed under a large net."
- 自动来源：`positive_1` / "A child asleep on a large bed under a mosquito net"
- 正确片段："large bed under a mosquito net"
- 错误片段："mosquito bed under a large net."
- 正确片段 token：IDs `[2994, 363, 382, 1943, 299, 621, 118, 537, 338, 114, 399, 439]`；pieces `["Ġlarge", "Ġb", "ed", "Ġunder", "Ġa", "Ġmo", "s", "qu", "it", "o", "Ġn", "et"]`；decode " large bed under a mosquito net"
- 错误片段 token：IDs `[621, 118, 537, 338, 114, 363, 382, 1943, 299, 2994, 399, 439, 49]`；pieces `["Ġmo", "s", "qu", "it", "o", "Ġb", "ed", "Ġunder", "Ġa", "Ġlarge", "Ġn", "et", "."]`；decode " mosquito bed under a large net."
- 自动分类：`complex_edit`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因："non_contiguous_edit_blocks=3;word_order_change"
- Token 边界提示：[]

### 13. `swap_atribute:397`

- 负例类型：`swap_atribute`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："A white bowl of green granny smith apples."
- 正描述 2：" Green granny smith apples in a white bowl."
- 负描述："A green bowl of white granny smith apples."
- 自动来源：`positive_1` / "A white bowl of green granny smith apples."
- 正确片段："white bowl of green"
- 错误片段："green bowl of white"
- 正确片段 token：IDs `[654, 1078, 363, 451, 111, 354, 5921]`；pieces `["Ġwh", "ite", "Ġb", "ow", "l", "Ġof", "Ġgreen"]`；decode " white bowl of green"
- 错误片段 token：IDs `[5921, 363, 451, 111, 354, 654, 1078]`；pieces `["Ġgreen", "Ġb", "ow", "l", "Ġof", "Ġwh", "ite"]`；decode " green bowl of white"
- 自动分类：`complex_edit`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因："non_contiguous_edit_blocks=2;word_order_change"
- Token 边界提示：[]

### 14. `swap_atribute:410`

- 负例类型：`swap_atribute`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："Two persons sitting on ledge looking at a cellphone."
- 正描述 2："Two persons are seated on a ledge, facing a cellphone."
- 负描述："A person sitting on a ledge looking at two cellphones."
- 自动来源：`positive_1` / "Two persons sitting on ledge looking at a cellphone."
- 正确片段："Two persons sitting on ledge looking at a cellphone"
- 错误片段："A person sitting on a ledge looking at two cellphones"
- 正确片段 token：IDs `[87, 122, 114, 2198, 118, 5305, 2912, 619, 848, 103, 583, 3125, 1248, 299, 317, 446, 823, 107, 1634]`；pieces `["T", "w", "o", "Ġperson", "s", "Ġsit", "ting", "Ġon", "Ġle", "d", "ge", "Ġlooking", "Ġat", "Ġa", "Ġc", "el", "lp", "h", "one"]`；decode "Two persons sitting on ledge looking at a cellphone"
- 错误片段 token：IDs `[68, 2198, 5305, 2912, 619, 299, 848, 103, 583, 3125, 1248, 2102, 317, 446, 823, 107, 310, 329]`；pieces `["A", "Ġperson", "Ġsit", "ting", "Ġon", "Ġa", "Ġle", "d", "ge", "Ġlooking", "Ġat", "Ġtwo", "Ġc", "el", "lp", "h", "on", "es"]`；decode "A person sitting on a ledge looking at two cellphones"
- 自动分类：`complex_edit`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因："non_contiguous_edit_blocks=3;obvious_rewrite_by_fixed_coverage_rule"
- Token 边界提示：[]

### 15. `swap_atribute:424`

- 负例类型：`swap_atribute`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："An Apple desktop computer system is turned on with a monitor, keyboard, mouse, two speakers, and other peripherals."
- 正描述 2："Complete with a monitor, keyboard, mouse, a pair of speakers, and various other peripherals, an apple computer is being turned on."
- 负描述："An Apple desktop computer system is turned on with two monitors, keyboard, mouse, a speaker, and other peripherals."
- 自动来源：`positive_1` / "An Apple desktop computer system is turned on with a monitor, keyboard, mouse, two speakers, and other peripherals."
- 正确片段："a monitor, keyboard, mouse, two speakers"
- 错误片段："two monitors, keyboard, mouse, a speaker"
- 正确片段 token：IDs `[299, 4036, 338, 336, 47, 3311, 101, 114, 1433, 47, 351, 6325, 47, 2102, 946, 1660, 496]`；pieces `["Ġa", "Ġmon", "it", "or", ",", "Ġkey", "b", "o", "ard", ",", "Ġm", "ouse", ",", "Ġtwo", "Ġspe", "ak", "ers"]`；decode " a monitor, keyboard, mouse, two speakers"
- 错误片段 token：IDs `[2102, 4036, 338, 1945, 47, 3311, 101, 114, 1433, 47, 351, 6325, 47, 299, 946, 1660, 311]`；pieces `["Ġtwo", "Ġmon", "it", "ors", ",", "Ġkey", "b", "o", "ard", ",", "Ġm", "ouse", ",", "Ġa", "Ġspe", "ak", "er"]`；decode " two monitors, keyboard, mouse, a speaker"
- 自动分类：`complex_edit`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因："non_contiguous_edit_blocks=2"
- Token 边界提示：[]

### 16. `swap_atribute:426`

- 负例类型：`swap_atribute`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："A bathroom with a white tub and white cabinets has a black pattern on the floor."
- 正描述 2："A white tub and white cabinets, and a black pattern on the floor are featured in a bathroom."
- 负描述："A bathroom with a black tub and black cabinets has a white pattern on the floor."
- 自动来源：`positive_1` / "A bathroom with a white tub and white cabinets has a black pattern on the floor."
- 正确片段："white tub and white cabinets has a black"
- 错误片段："black tub and black cabinets has a white"
- 正确片段 token：IDs `[654, 1078, 297, 1352, 376, 654, 1078, 317, 572, 301, 3391, 1290, 299, 2597, 1637]`；pieces `["Ġwh", "ite", "Ġt", "ub", "Ġand", "Ġwh", "ite", "Ġc", "ab", "in", "ets", "Ġhas", "Ġa", "Ġbl", "ack"]`；decode " white tub and white cabinets has a black"
- 错误片段 token：IDs `[2597, 1637, 297, 1352, 376, 2597, 1637, 317, 572, 301, 3391, 1290, 299, 654, 1078]`；pieces `["Ġbl", "ack", "Ġt", "ub", "Ġand", "Ġbl", "ack", "Ġc", "ab", "in", "ets", "Ġhas", "Ġa", "Ġwh", "ite"]`；decode " black tub and black cabinets has a white"
- 自动分类：`complex_edit`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因："non_contiguous_edit_blocks=3;obvious_rewrite_by_fixed_coverage_rule"
- Token 边界提示：[]

### 17. `swap_atribute:427`

- 负例类型：`swap_atribute`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："An office view shows cubicles and overhead lights in the background, and to the front ,  a serious looking person with a beard, vest and colorful tie. "
- 正描述 2："In the foreground of the office view, a serious-looking person with a beard, vest, and colorful tie is visible, while cubicles and overhead lights can be seen in the background."
- 负描述："An office view shows cubicles and overhead lights in the background, and to the front, a colorful looking person with a beard, vest and serious tie."
- 自动来源：`positive_1` / "An office view shows cubicles and overhead lights in the background, and to the front ,  a serious looking person with a beard, vest and colorful tie. "
- 正确片段：" ,  a serious looking person with a beard, vest and colorful tie. "
- 错误片段：", a colorful looking person with a beard, vest and serious tie."
- 正确片段 token：IDs `[256, 47, 256, 299, 1319, 3635, 3125, 2198, 599, 299, 600, 1433, 47, 603, 611, 376, 4987, 1930, 297, 1400, 49, 256]`；pieces `["Ġ", ",", "Ġ", "Ġa", "Ġser", "ious", "Ġlooking", "Ġperson", "Ġwith", "Ġa", "Ġbe", "ard", ",", "Ġv", "est", "Ġand", "Ġcolor", "ful", "Ġt", "ie", ".", "Ġ"]`；decode " ,  a serious looking person with a beard, vest and colorful tie. "
- 错误片段 token：IDs `[47, 299, 4987, 1930, 3125, 2198, 599, 299, 600, 1433, 47, 603, 611, 376, 1319, 3635, 297, 1400, 49]`；pieces `[",", "Ġa", "Ġcolor", "ful", "Ġlooking", "Ġperson", "Ġwith", "Ġa", "Ġbe", "ard", ",", "Ġv", "est", "Ġand", "Ġser", "ious", "Ġt", "ie", "."]`；decode ", a colorful looking person with a beard, vest and serious tie."
- 自动分类：`complex_edit`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因："non_contiguous_edit_blocks=2;word_order_change"
- Token 边界提示：[]

### 18. `swap_atribute:430`

- 负例类型：`swap_atribute`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："A bunch of birds flying around a couple of waves near the ocean."
- 正描述 2："A group of birds flying above a pair of waves near the ocean."
- 负描述："A couple of birds flying around a bunch of waves near the ocean."
- 自动来源：`positive_1` / "A bunch of birds flying around a couple of waves near the ocean."
- 正确片段："bunch of birds flying around a couple"
- 错误片段："couple of birds flying around a bunch"
- 正确片段 token：IDs `[363, 651, 550, 354, 5231, 1881, 341, 542, 350, 3364, 299, 317, 326, 833]`；pieces `["Ġb", "un", "ch", "Ġof", "Ġbir", "ds", "Ġf", "ly", "ing", "Ġaround", "Ġa", "Ġc", "ou", "ple"]`；decode " bunch of birds flying around a couple"
- 错误片段 token：IDs `[317, 326, 833, 354, 5231, 1881, 341, 542, 350, 3364, 299, 363, 651, 550]`；pieces `["Ġc", "ou", "ple", "Ġof", "Ġbir", "ds", "Ġf", "ly", "ing", "Ġaround", "Ġa", "Ġb", "un", "ch"]`；decode " couple of birds flying around a bunch"
- 自动分类：`complex_edit`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因："non_contiguous_edit_blocks=2;word_order_change"
- Token 边界提示：[]

### 19. `swap_atribute:444`

- 负例类型：`swap_atribute`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："Two babies sitting on their potties in the bathroom."
- 正描述 2："In the bathroom, two babies are seated on their potties."
- 负描述："Their baby is sitting on two potties in the bathroom."
- 自动来源：`positive_1` / "Two babies sitting on their potties in the bathroom."
- 正确片段："wo babies sitting on their"
- 错误片段："heir baby is sitting on two"
- 正确片段 token：IDs `[87, 122, 114, 363, 572, 925, 5305, 2912, 619, 1635]`；pieces `["T", "w", "o", "Ġb", "ab", "ies", "Ġsit", "ting", "Ġon", "Ġtheir"]`；decode "Two babies sitting on their"
- 错误片段 token：IDs `[750, 639, 363, 572, 124, 395, 5305, 2912, 619, 2102]`；pieces `["The", "ir", "Ġb", "ab", "y", "Ġis", "Ġsit", "ting", "Ġon", "Ġtwo"]`；decode "Their baby is sitting on two"
- 自动分类：`complex_edit`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因："non_contiguous_edit_blocks=2"
- Token 边界提示：[]

### 20. `swap_atribute:471`

- 负例类型：`swap_atribute`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："Several white birds standing in a puddle in a parking lot."
- 正描述 2："In a parking lot, several white birds are standing in a puddle "
- 负描述："Several birds standing in a white puddle in a parking lot."
- 自动来源：`positive_1` / "Several white birds standing in a puddle in a parking lot."
- 正确片段："white birds standing in a"
- 错误片段："birds standing in a white"
- 正确片段 token：IDs `[654, 1078, 5231, 1881, 2823, 350, 353, 299]`；pieces `["Ġwh", "ite", "Ġbir", "ds", "Ġstand", "ing", "Ġin", "Ġa"]`；decode " white birds standing in a"
- 错误片段 token：IDs `[5231, 1881, 2823, 350, 353, 299, 654, 1078]`；pieces `["Ġbir", "ds", "Ġstand", "ing", "Ġin", "Ġa", "Ġwh", "ite"]`；decode " birds standing in a white"
- 自动分类：`complex_edit`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因："non_contiguous_edit_blocks=2;word_order_change"
- Token 边界提示：[]

### 21. `swap_atribute:504`

- 负例类型：`swap_atribute`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："A red stop sign with a green street sign posted above it."
- 正描述 2："A green street sign is positioned above a red stop sign."
- 负描述："A green stop sign with a red street sign posted above it."
- 自动来源：`positive_1` / "A red stop sign with a green street sign posted above it."
- 正确片段："red stop sign with a green"
- 错误片段："green stop sign with a red"
- 正确片段 token：IDs `[5534, 580, 1506, 2185, 599, 299, 5921]`；pieces `["Ġred", "Ġst", "op", "Ġsign", "Ġwith", "Ġa", "Ġgreen"]`；decode " red stop sign with a green"
- 错误片段 token：IDs `[5921, 580, 1506, 2185, 599, 299, 5534]`；pieces `["Ġgreen", "Ġst", "op", "Ġsign", "Ġwith", "Ġa", "Ġred"]`；decode " green stop sign with a red"
- 自动分类：`complex_edit`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因："non_contiguous_edit_blocks=2;word_order_change"
- Token 边界提示：[]

### 22. `swap_atribute:512`

- 负例类型：`swap_atribute`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："A blue shelving unit has a vase and metal cups on it."
- 正描述 2："A vase and metal cups lies on the blue shelving unit."
- 负描述："A metal shelving unit has a vase and blue cups on it."
- 自动来源：`positive_1` / "A blue shelving unit has a vase and metal cups on it."
- 正确片段："blue shelving unit has a vase and metal"
- 错误片段："metal shelving unit has a vase and blue"
- 正确片段 token：IDs `[4300, 3191, 111, 2828, 1406, 338, 1290, 299, 603, 812, 376, 4743, 352]`；pieces `["Ġblue", "Ġshe", "l", "ving", "Ġun", "it", "Ġhas", "Ġa", "Ġv", "ase", "Ġand", "Ġmet", "al"]`；decode " blue shelving unit has a vase and metal"
- 错误片段 token：IDs `[4743, 352, 3191, 111, 2828, 1406, 338, 1290, 299, 603, 812, 376, 4300]`；pieces `["Ġmet", "al", "Ġshe", "l", "ving", "Ġun", "it", "Ġhas", "Ġa", "Ġv", "ase", "Ġand", "Ġblue"]`；decode " metal shelving unit has a vase and blue"
- 自动分类：`complex_edit`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因："non_contiguous_edit_blocks=2;word_order_change;obvious_rewrite_by_fixed_coverage_rule"
- Token 边界提示：[]

### 23. `swap_atribute:518`

- 负例类型：`swap_atribute`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："A parasailer in the distance with two surfers in the foreground."
- 正描述 2："In the distance, there is a parasailer, and in the foreground, there are two surfers."
- 负描述："Two parasailers in the distance with a surfer in the foreground."
- 自动来源：`positive_1` / "A parasailer in the distance with two surfers in the foreground."
- 正确片段："A parasailer in the distance with two surfers"
- 错误片段："Two parasailers in the distance with a surfer"
- 正确片段 token：IDs `[68, 2655, 390, 1348, 311, 353, 309, 6163, 599, 2102, 3946, 105, 496]`；pieces `["A", "Ġpar", "as", "ail", "er", "Ġin", "Ġthe", "Ġdistance", "Ġwith", "Ġtwo", "Ġsur", "f", "ers"]`；decode "A parasailer in the distance with two surfers"
- 错误片段 token：IDs `[87, 122, 114, 2655, 390, 1348, 496, 353, 309, 6163, 599, 299, 3946, 105, 311]`；pieces `["T", "w", "o", "Ġpar", "as", "ail", "ers", "Ġin", "Ġthe", "Ġdistance", "Ġwith", "Ġa", "Ġsur", "f", "er"]`；decode "Two parasailers in the distance with a surfer"
- 自动分类：`complex_edit`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因："non_contiguous_edit_blocks=2;obvious_rewrite_by_fixed_coverage_rule"
- Token 边界提示：[]

### 24. `swap_atribute:527`

- 负例类型：`swap_atribute`
- 阶段三范围：`formal`；certifying formal：`False`
- 正描述 1："The colorful umbrella sits in front of the lavender building."
- 正描述 2："The lavender building is positioned behind the colorful umbrella."
- 负描述："The lavender umbrella sits in front of the colorful building."
- 自动来源：`positive_1` / "The colorful umbrella sits in front of the lavender building."
- 正确片段："colorful umbrella sits in front of the lavender"
- 错误片段："lavender umbrella sits in front of the colorful"
- 正确片段 token：IDs `[4987, 1930, 256, 714, 306, 1989, 100, 316, 2163, 353, 341, 117, 3856, 354, 309, 406, 1113, 6207]`；pieces `["Ġcolor", "ful", "Ġ", "umb", "re", "ll", "a", "Ġs", "its", "Ġin", "Ġf", "r", "ont", "Ġof", "Ġthe", "Ġl", "av", "ender"]`；decode " colorful umbrella sits in front of the lavender"
- 错误片段 token：IDs `[406, 1113, 6207, 256, 714, 306, 1989, 100, 316, 2163, 353, 341, 117, 3856, 354, 309, 4987, 1930]`；pieces `["Ġl", "av", "ender", "Ġ", "umb", "re", "ll", "a", "Ġs", "its", "Ġin", "Ġf", "r", "ont", "Ġof", "Ġthe", "Ġcolor", "ful"]`；decode " lavender umbrella sits in front of the colorful"
- 自动分类：`complex_edit`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因："non_contiguous_edit_blocks=2;word_order_change;obvious_rewrite_by_fixed_coverage_rule"
- Token 边界提示：[]

### 25. `swap_atribute:631`

- 负例类型：`swap_atribute`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："A group of people standing around a sidewalk together."
- 正描述 2："A group of people are gathered around a sidewalk together."
- 负描述："people standing alone on different sidewalks."
- 自动来源：`positive_1` / "A group of people standing around a sidewalk together."
- 正确片段："A group of people standing around a sidewalk together"
- 错误片段："people standing alone on different sidewalks"
- 正确片段 token：IDs `[68, 4592, 354, 2975, 2823, 350, 3364, 299, 5046, 122, 5864, 5169]`；pieces `["A", "Ġgroup", "Ġof", "Ġpeople", "Ġstand", "ing", "Ġaround", "Ġa", "Ġside", "w", "alk", "Ġtogether"]`；decode "A group of people standing around a sidewalk together"
- 错误片段 token：IDs `[653, 2643, 2823, 350, 789, 1634, 619, 2301, 5046, 122, 352, 1275]`；pieces `["pe", "ople", "Ġstand", "ing", "Ġal", "one", "Ġon", "Ġdifferent", "Ġside", "w", "al", "ks"]`；decode "people standing alone on different sidewalks"
- 自动分类：`complex_edit`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因："non_contiguous_edit_blocks=2;obvious_rewrite_by_fixed_coverage_rule"
- Token 边界提示：[]

### 26. `swap_atribute:644`

- 负例类型：`swap_atribute`
- 阶段三范围：`formal`；certifying formal：`False`
- 正描述 1："A person helping a child stand on a skateboard."
- 正描述 2："A child is being helped by a person to stand on a skateboard."
- 负描述："A person on a skateboard stands helping a child."
- 自动来源：`positive_1` / "A person helping a child stand on a skateboard."
- 正确片段："helping a child stand on a skateboar"
- 错误片段："on a skateboard stands helping a chil"
- 正确片段 token：IDs `[843, 350, 299, 6109, 2823, 619, 299, 2549, 557, 101, 114, 1433]`；pieces `["Ġhelp", "ing", "Ġa", "Ġchild", "Ġstand", "Ġon", "Ġa", "Ġsk", "ate", "b", "o", "ard"]`；decode " helping a child stand on a skateboard"
- 错误片段 token：IDs `[619, 299, 2549, 557, 101, 114, 1433, 2823, 118, 843, 350, 299, 6109]`；pieces `["Ġon", "Ġa", "Ġsk", "ate", "b", "o", "ard", "Ġstand", "s", "Ġhelp", "ing", "Ġa", "Ġchild"]`；decode " on a skateboard stands helping a child"
- 自动分类：`complex_edit`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因："non_contiguous_edit_blocks=2"
- Token 边界提示：[]

### 27. `swap_atribute:648`

- 负例类型：`swap_atribute`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："The train engine is followed by a line of open cars."
- 正描述 2："The line of open cars is led by the train engine."
- 负描述："The open engine is followed by a line of train cars."
- 自动来源：`positive_1` / "The train engine is followed by a line of open cars."
- 正确片段："train engine is followed by a line of ope"
- 错误片段："open engine is followed by a line of trai"
- 正确片段 token：IDs `[1946, 301, 3136, 1016, 395, 1502, 382, 769, 299, 2909, 354, 5102]`；pieces `["Ġtra", "in", "Ġeng", "ine", "Ġis", "Ġfollow", "ed", "Ġby", "Ġa", "Ġline", "Ġof", "Ġopen"]`；decode " train engine is followed by a line of open"
- 错误片段 token：IDs `[5102, 3136, 1016, 395, 1502, 382, 769, 299, 2909, 354, 1946, 301]`；pieces `["Ġopen", "Ġeng", "ine", "Ġis", "Ġfollow", "ed", "Ġby", "Ġa", "Ġline", "Ġof", "Ġtra", "in"]`；decode " open engine is followed by a line of train"
- 自动分类：`complex_edit`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因："non_contiguous_edit_blocks=2;obvious_rewrite_by_fixed_coverage_rule"
- Token 边界提示：[]

### 28. `swap_atribute:67`

- 负例类型：`swap_atribute`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："A person in a yellow shirt is about to catch a white frisbee."
- 正描述 2："A white frisbee is about to be caught by a person in a yellow shirt."
- 负描述："A person in a white shirt is about to catch a yellow frisbee."
- 自动来源：`positive_1` / "A person in a yellow shirt is about to catch a white frisbee."
- 正确片段："yellow shirt is about to catch a white"
- 错误片段："white shirt is about to catch a yellow"
- 正确片段 token：IDs `[385, 446, 1030, 1128, 4193, 395, 1196, 364, 3706, 550, 299, 654, 1078]`；pieces `["Ġy", "el", "low", "Ġsh", "irt", "Ġis", "Ġabout", "Ġto", "Ġcat", "ch", "Ġa", "Ġwh", "ite"]`；decode " yellow shirt is about to catch a white"
- 错误片段 token：IDs `[654, 1078, 1128, 4193, 395, 1196, 364, 3706, 550, 299, 385, 446, 1030]`；pieces `["Ġwh", "ite", "Ġsh", "irt", "Ġis", "Ġabout", "Ġto", "Ġcat", "ch", "Ġa", "Ġy", "el", "low"]`；decode " white shirt is about to catch a yellow"
- 自动分类：`complex_edit`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因："non_contiguous_edit_blocks=2;word_order_change;obvious_rewrite_by_fixed_coverage_rule"
- Token 边界提示：[]

### 29. `swap_atribute:95`

- 负例类型：`swap_atribute`
- 阶段三范围：`pilot`；certifying formal：`False`
- 正描述 1："The toilet is covered in sparkles with a red object in front of it."
- 正描述 2："The red object is positioned in front of the toilet, which is covered in sparkles."
- 负描述："The toilet has a red cover with a sparkly object in front of it."
- 自动来源：`positive_1` / "The toilet is covered in sparkles with a red object in front of it."
- 正确片段："is covered in sparkles with a red"
- 错误片段："has a red cover with a sparkly"
- 正确片段 token：IDs `[395, 966, 478, 1837, 353, 1772, 2000, 1907, 599, 299, 5534]`；pieces `["Ġis", "Ġco", "ve", "red", "Ġin", "Ġsp", "ark", "les", "Ġwith", "Ġa", "Ġred"]`；decode " is covered in sparkles with a red"
- 错误片段 token：IDs `[1290, 299, 5534, 966, 652, 599, 299, 1772, 2000, 542]`；pieces `["Ġhas", "Ġa", "Ġred", "Ġco", "ver", "Ġwith", "Ġa", "Ġsp", "ark", "ly"]`；decode " has a red cover with a sparkly"
- 自动分类：`complex_edit`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因："non_contiguous_edit_blocks=2"
- Token 边界提示：[]

### 30. `swap_atribute:99`

- 负例类型：`swap_atribute`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："A person watching two elephants behind a wire fence."
- 正描述 2："An individual observes two elephants from behind a wire fence."
- 负描述："Two people watching an elephant behind a wire fence."
- 自动来源：`positive_1` / "A person watching two elephants behind a wire fence."
- 正确片段："A person watching two elephants"
- 错误片段："Two people watching an elephant"
- 正确片段 token：IDs `[68, 2198, 339, 6131, 350, 2102, 1905, 1601, 5483]`；pieces `["A", "Ġperson", "Ġw", "atch", "ing", "Ġtwo", "Ġele", "ph", "ants"]`；decode "A person watching two elephants"
- 错误片段 token：IDs `[87, 122, 114, 2975, 339, 6131, 350, 346, 1905, 1601, 811]`；pieces `["T", "w", "o", "Ġpeople", "Ġw", "atch", "ing", "Ġan", "Ġele", "ph", "ant"]`；decode "Two people watching an elephant"
- 自动分类：`complex_edit`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因："non_contiguous_edit_blocks=2"
- Token 边界提示：[]

## 负例类型：swap_object

候选 `245` 条，本节抽取 `30` 条。

### 1. `swap_object:10`

- 负例类型：`swap_object`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："A person in a green shirt stands by a child holding a piece of cake on a plate."
- 正描述 2："a child holding a plate with a piece of cake is positioned next to a standing person wearing a green shirt."
- 负描述："A child in a green shirt stands by a person holding a piece of cake on a plate."
- 自动来源：`positive_1` / "A person in a green shirt stands by a child holding a piece of cake on a plate."
- 正确片段："person in a green shirt stands by a child"
- 错误片段："child in a green shirt stands by a person"
- 正确片段 token：IDs `[2198, 353, 299, 5921, 1128, 4193, 2823, 118, 769, 299, 6109]`；pieces `["Ġperson", "Ġin", "Ġa", "Ġgreen", "Ġsh", "irt", "Ġstand", "s", "Ġby", "Ġa", "Ġchild"]`；decode " person in a green shirt stands by a child"
- 错误片段 token：IDs `[6109, 353, 299, 5921, 1128, 4193, 2823, 118, 769, 299, 2198]`；pieces `["Ġchild", "Ġin", "Ġa", "Ġgreen", "Ġsh", "irt", "Ġstand", "s", "Ġby", "Ġa", "Ġperson"]`；decode " child in a green shirt stands by a person"
- 自动分类：`complex_edit`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因："non_contiguous_edit_blocks=2;word_order_change;obvious_rewrite_by_fixed_coverage_rule"
- Token 边界提示：[]

### 2. `swap_object:108`

- 负例类型：`swap_object`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："A person on a motorcycle driving past a group of people behind a fence."
- 正描述 2："A person is driving a motorcycle past a group of individuals who are behind a fence."
- 负描述："A group of people on motorcycles driving past a person behind a fence."
- 自动来源：`positive_1` / "A person on a motorcycle driving past a group of people behind a fence."
- 正确片段："person on a motorcycle driving past a group of people"
- 错误片段："group of people on motorcycles driving past a person"
- 正确片段 token：IDs `[2198, 619, 299, 351, 593, 336, 2863, 2945, 5893, 4917, 344, 1154, 299, 4592, 354, 2975]`；pieces `["Ġperson", "Ġon", "Ġa", "Ġm", "ot", "or", "cy", "cle", "Ġdr", "iving", "Ġp", "ast", "Ġa", "Ġgroup", "Ġof", "Ġpeople"]`；decode " person on a motorcycle driving past a group of people"
- 错误片段 token：IDs `[4592, 354, 2975, 619, 351, 593, 336, 2863, 1110, 329, 5893, 4917, 344, 1154, 299, 2198]`；pieces `["Ġgroup", "Ġof", "Ġpeople", "Ġon", "Ġm", "ot", "or", "cy", "cl", "es", "Ġdr", "iving", "Ġp", "ast", "Ġa", "Ġperson"]`；decode " group of people on motorcycles driving past a person"
- 自动分类：`complex_edit`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因："non_contiguous_edit_blocks=3;obvious_rewrite_by_fixed_coverage_rule"
- Token 边界提示：[]

### 3. `swap_object:113`

- 负例类型：`swap_object`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："Donuts in a box and a type of meat on a plate."
- 正描述 2："a type of meat is on a plate along with donuts in a box."
- 负描述："A type of meat in a box and donuts on a plate."
- 自动来源：`positive_2` / "a type of meat is on a plate along with donuts in a box."
- 正确片段："a type of meat is on a plate along with donuts in a box"
- 错误片段："A type of meat in a box and donuts on a plate"
- 正确片段 token：IDs `[100, 3217, 354, 765, 314, 395, 619, 299, 1219, 557, 5782, 599, 2207, 501, 118, 353, 299, 1847, 123]`；pieces `["a", "Ġtype", "Ġof", "Ġme", "at", "Ġis", "Ġon", "Ġa", "Ġpl", "ate", "Ġalong", "Ġwith", "Ġdon", "ut", "s", "Ġin", "Ġa", "Ġbo", "x"]`；decode "a type of meat is on a plate along with donuts in a box"
- 错误片段 token：IDs `[68, 3217, 354, 765, 314, 353, 299, 1847, 123, 376, 2207, 501, 118, 619, 299, 1219, 557]`；pieces `["A", "Ġtype", "Ġof", "Ġme", "at", "Ġin", "Ġa", "Ġbo", "x", "Ġand", "Ġdon", "ut", "s", "Ġon", "Ġa", "Ġpl", "ate"]`；decode "A type of meat in a box and donuts on a plate"
- 自动分类：`complex_edit`
- 来源规则："positive_2_pareto_dominates_character_and_token_distance"
- 失败原因："non_contiguous_edit_blocks=3;obvious_rewrite_by_fixed_coverage_rule"
- Token 边界提示：[]

### 4. `swap_object:117`

- 负例类型：`swap_object`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："A small pizza with olives is placed on a stack of plates."
- 正描述 2："A small pizza topped with olives is placed on top of a stack of plates."
- 负描述："A stack of plates with olives is placed on a small pizza."
- 自动来源：`positive_1` / "A small pizza with olives is placed on a stack of plates."
- 正确片段："mall pizza with olives is placed on a stack of plates"
- 错误片段："tack of plates with olives is placed on a small pizza"
- 正确片段 token：IDs `[3436, 344, 1028, 125, 100, 599, 319, 111, 3541, 395, 1219, 1545, 382, 619, 299, 580, 1637, 354, 1219, 1434]`；pieces `["Ġsmall", "Ġp", "iz", "z", "a", "Ġwith", "Ġo", "l", "ives", "Ġis", "Ġpl", "ac", "ed", "Ġon", "Ġa", "Ġst", "ack", "Ġof", "Ġpl", "ates"]`；decode " small pizza with olives is placed on a stack of plates"
- 错误片段 token：IDs `[580, 1637, 354, 1219, 1434, 599, 319, 111, 3541, 395, 1219, 1545, 382, 619, 299, 3436, 344, 1028, 125, 100]`；pieces `["Ġst", "ack", "Ġof", "Ġpl", "ates", "Ġwith", "Ġo", "l", "ives", "Ġis", "Ġpl", "ac", "ed", "Ġon", "Ġa", "Ġsmall", "Ġp", "iz", "z", "a"]`；decode " stack of plates with olives is placed on a small pizza"
- 自动分类：`complex_edit`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因："non_contiguous_edit_blocks=2;obvious_rewrite_by_fixed_coverage_rule"
- Token 边界提示：[]

### 5. `swap_object:129`

- 负例类型：`swap_object`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："A street light in front of a colorful train on a bridge."
- 正描述 2："A colorful train is on a bridge with a street light in front of it."
- 负描述："A colorful train in front of a street light on a bridge."
- 自动来源：`None` / null
- 正确片段：""
- 错误片段：""
- 正确片段 token：IDs `[]`；pieces `[]`；decode ""
- 错误片段 token：IDs `[]`；pieces `[]`；decode ""
- 自动分类：`ambiguous_source`
- 来源规则："character_and_token_distance_rankings_conflict"
- 失败原因："character_and_token_distance_rankings_conflict"
- Token 边界提示：[]

### 6. `swap_object:133`

- 负例类型：`swap_object`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："A person sitting in front of the Eiffel tower near pigeons."
- 正描述 2："A person is surrounded by pigeons while sitting in front of the Eiffel tower, ."
- 负描述："Pigeons sitting in front of the Eiffel tower near a person."
- 自动来源：`positive_1` / "A person sitting in front of the Eiffel tower near pigeons."
- 正确片段："A person sitting in front of the Eiffel tower near pigeons"
- 错误片段："Pigeons sitting in front of the Eiffel tower near a person"
- 正确片段 token：IDs `[68, 2198, 5305, 2912, 353, 341, 117, 3856, 354, 309, 957, 507, 105, 446, 364, 122, 311, 730, 370, 344, 499, 104, 3070]`；pieces `["A", "Ġperson", "Ġsit", "ting", "Ġin", "Ġf", "r", "ont", "Ġof", "Ġthe", "ĠE", "if", "f", "el", "Ġto", "w", "er", "Ġne", "ar", "Ġp", "ig", "e", "ons"]`；decode "A person sitting in front of the Eiffel tower near pigeons"
- 错误片段 token：IDs `[83, 499, 104, 3070, 5305, 2912, 353, 341, 117, 3856, 354, 309, 957, 507, 105, 446, 364, 122, 311, 730, 370, 299, 2198]`；pieces `["P", "ig", "e", "ons", "Ġsit", "ting", "Ġin", "Ġf", "r", "ont", "Ġof", "Ġthe", "ĠE", "if", "f", "el", "Ġto", "w", "er", "Ġne", "ar", "Ġa", "Ġperson"]`；decode "Pigeons sitting in front of the Eiffel tower near a person"
- 自动分类：`complex_edit`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因："non_contiguous_edit_blocks=2;word_order_change;obvious_rewrite_by_fixed_coverage_rule"
- Token 边界提示：[]

### 7. `swap_object:134`

- 负例类型：`swap_object`
- 阶段三范围：`pilot`；certifying formal：`False`
- 正描述 1："A pizza sitting on top of a pizza box covered in cheese."
- 正描述 2："A pizza is positioned on top of a pizza box that is covered in cheese."
- 负描述："A pizza box sitting on top of a pizza covered in cheese."
- 自动来源：`positive_1` / "A pizza sitting on top of a pizza box covered in cheese."
- 正确片段："sitting on top of a pizza box"
- 错误片段："box sitting on top of a pizza"
- 正确片段 token：IDs `[5305, 2912, 619, 2924, 354, 299, 344, 1028, 125, 100, 1847, 123]`；pieces `["Ġsit", "ting", "Ġon", "Ġtop", "Ġof", "Ġa", "Ġp", "iz", "z", "a", "Ġbo", "x"]`；decode " sitting on top of a pizza box"
- 错误片段 token：IDs `[1847, 123, 5305, 2912, 619, 2924, 354, 299, 344, 1028, 125, 100]`；pieces `["Ġbo", "x", "Ġsit", "ting", "Ġon", "Ġtop", "Ġof", "Ġa", "Ġp", "iz", "z", "a"]`；decode " box sitting on top of a pizza"
- 自动分类：`complex_edit`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因："non_contiguous_edit_blocks=2;word_order_change"
- Token 边界提示：[]

### 8. `swap_object:140`

- 负例类型：`swap_object`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："Half an eclair on a plate and a coffee mug on wooden table."
- 正描述 2："A coffee mug is on a wooden table and half of an eclair are positioned on a plate."
- 负描述："A coffee mug on a plate and half an eclair on wooden table."
- 自动来源：`positive_2` / "A coffee mug is on a wooden table and half of an eclair are positioned on a plate."
- 正确片段："is on a wooden table and half of an eclair are positioned on a plat"
- 错误片段："on a plate and half an eclair on wooden tabl"
- 正确片段 token：IDs `[395, 619, 299, 339, 2166, 327, 2630, 376, 429, 352, 105, 354, 346, 413, 1110, 3709, 732, 2617, 1632, 382, 619, 299, 1219, 557]`；pieces `["Ġis", "Ġon", "Ġa", "Ġw", "ood", "en", "Ġtable", "Ġand", "Ġh", "al", "f", "Ġof", "Ġan", "Ġe", "cl", "air", "Ġare", "Ġpos", "ition", "ed", "Ġon", "Ġa", "Ġpl", "ate"]`；decode " is on a wooden table and half of an eclair are positioned on a plate"
- 错误片段 token：IDs `[619, 299, 1219, 557, 376, 429, 352, 105, 346, 413, 1110, 3709, 619, 339, 2166, 327, 2630]`；pieces `["Ġon", "Ġa", "Ġpl", "ate", "Ġand", "Ġh", "al", "f", "Ġan", "Ġe", "cl", "air", "Ġon", "Ġw", "ood", "en", "Ġtable"]`；decode " on a plate and half an eclair on wooden table"
- 自动分类：`complex_edit`
- 来源规则："positive_2_pareto_dominates_character_and_token_distance"
- 失败原因："non_contiguous_edit_blocks=2;obvious_rewrite_by_fixed_coverage_rule"
- Token 边界提示：[]

### 9. `swap_object:144`

- 负例类型：`swap_object`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："A close up of a sandwich with a drink in the back."
- 正描述 2："A close-up photograph of a sandwich with a drink visible in the background."
- 负描述："A close up of a drink with a sandwich in the back."
- 自动来源：`positive_1` / "A close up of a sandwich with a drink in the back."
- 正确片段："sandwich with a drink"
- 错误片段："drink with a sandwich"
- 正确片段 token：IDs `[316, 728, 122, 948, 599, 299, 5893, 3010]`；pieces `["Ġs", "and", "w", "ich", "Ġwith", "Ġa", "Ġdr", "ink"]`；decode " sandwich with a drink"
- 错误片段 token：IDs `[5893, 3010, 599, 299, 316, 728, 122, 948]`；pieces `["Ġdr", "ink", "Ġwith", "Ġa", "Ġs", "and", "w", "ich"]`；decode " drink with a sandwich"
- 自动分类：`complex_edit`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因："non_contiguous_edit_blocks=2;word_order_change"
- Token 边界提示：[]

### 10. `swap_object:146`

- 负例类型：`swap_object`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："A school bus in the street behind other cars."
- 正描述 2："A school bus is positioned behind other cars on the street."
- 负描述："Other cars in the street behind a school bus."
- 自动来源：`positive_1` / "A school bus in the street behind other cars."
- 正确片段："A school bus in the street behind other car"
- 错误片段："Other cars in the street behind a school bu"
- 正确片段 token：IDs `[68, 316, 4165, 500, 2499, 353, 309, 5941, 439, 5237, 916, 1649, 317, 2546]`；pieces `["A", "Ġs", "cho", "ol", "Ġbus", "Ġin", "Ġthe", "Ġstre", "et", "Ġbeh", "ind", "Ġother", "Ġc", "ars"]`；decode "A school bus in the street behind other cars"
- 错误片段 token：IDs `[82, 1187, 317, 2546, 353, 309, 5941, 439, 5237, 916, 299, 316, 4165, 500, 2499]`；pieces `["O", "ther", "Ġc", "ars", "Ġin", "Ġthe", "Ġstre", "et", "Ġbeh", "ind", "Ġa", "Ġs", "cho", "ol", "Ġbus"]`；decode "Other cars in the street behind a school bus"
- 自动分类：`complex_edit`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因："non_contiguous_edit_blocks=2;obvious_rewrite_by_fixed_coverage_rule"
- Token 边界提示：[]

### 11. `swap_object:163`

- 负例类型：`swap_object`
- 阶段三范围：`pilot`；certifying formal：`False`
- 正描述 1："There is a banana on a beach chair with a small umbrella"
- 正描述 2："The small umbrella is positioned on a beach chair with a banana."
- 负描述："There is a small umbrella on a beach chair with a banana."
- 自动来源：`positive_2` / "The small umbrella is positioned on a beach chair with a banana."
- 正确片段：" small umbrella is positioned"
- 错误片段："re is a small umbrella"
- 正确片段 token：IDs `[3436, 256, 714, 306, 1989, 100, 395, 2617, 1632, 382]`；pieces `["Ġsmall", "Ġ", "umb", "re", "ll", "a", "Ġis", "Ġpos", "ition", "ed"]`；decode " small umbrella is positioned"
- 错误片段 token：IDs `[306, 395, 299, 3436, 256, 714, 306, 1989, 100]`；pieces `["re", "Ġis", "Ġa", "Ġsmall", "Ġ", "umb", "re", "ll", "a"]`；decode "re is a small umbrella"
- 自动分类：`complex_edit`
- 来源规则："positive_2_pareto_dominates_character_and_token_distance"
- 失败原因："non_contiguous_edit_blocks=2"
- Token 边界提示：[]

### 12. `swap_object:177`

- 负例类型：`swap_object`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："A person is in the ocean waves near their surfboard with a dog on it."
- 正描述 2："The person is near their surfboard in the ocean waves with a dog positioned on it."
- 负描述："A dog is in the ocean waves near its surfboard with a person on it."
- 自动来源：`positive_1` / "A person is in the ocean waves near their surfboard with a dog on it."
- 正确片段："person is in the ocean waves near their surfboard with a dog"
- 错误片段："dog is in the ocean waves near its surfboard with a person"
- 正确片段 token：IDs `[2198, 395, 353, 309, 319, 473, 325, 339, 3923, 730, 370, 1635, 3946, 105, 101, 114, 1433, 599, 299, 1041, 106]`；pieces `["Ġperson", "Ġis", "Ġin", "Ġthe", "Ġo", "ce", "an", "Ġw", "aves", "Ġne", "ar", "Ġtheir", "Ġsur", "f", "b", "o", "ard", "Ġwith", "Ġa", "Ġdo", "g"]`；decode " person is in the ocean waves near their surfboard with a dog"
- 错误片段 token：IDs `[1041, 106, 395, 353, 309, 319, 473, 325, 339, 3923, 730, 370, 1342, 3946, 105, 101, 114, 1433, 599, 299, 2198]`；pieces `["Ġdo", "g", "Ġis", "Ġin", "Ġthe", "Ġo", "ce", "an", "Ġw", "aves", "Ġne", "ar", "Ġits", "Ġsur", "f", "b", "o", "ard", "Ġwith", "Ġa", "Ġperson"]`；decode " dog is in the ocean waves near its surfboard with a person"
- 自动分类：`complex_edit`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因："non_contiguous_edit_blocks=3;obvious_rewrite_by_fixed_coverage_rule"
- Token 边界提示：[]

### 13. `swap_object:186`

- 负例类型：`swap_object`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："A table topped with a cake covered in berries next to a plate of sandwiches."
- 正描述 2："A cake covered in berries is positioned adjacent to a plate of sandwiches on top of a table."
- 负描述："A table topped with a plate of sandwiches covered in berries next to a cake."
- 自动来源：`positive_1` / "A table topped with a cake covered in berries next to a plate of sandwiches."
- 正确片段："cake covered in berries next to a plate of sandwiches"
- 错误片段："plate of sandwiches covered in berries next to a cake"
- 正确片段 token：IDs `[317, 2434, 966, 478, 1837, 353, 363, 311, 3603, 4658, 364, 299, 1219, 557, 354, 316, 728, 122, 375, 2470]`；pieces `["Ġc", "ake", "Ġco", "ve", "red", "Ġin", "Ġb", "er", "ries", "Ġnext", "Ġto", "Ġa", "Ġpl", "ate", "Ġof", "Ġs", "and", "w", "ic", "hes"]`；decode " cake covered in berries next to a plate of sandwiches"
- 错误片段 token：IDs `[1219, 557, 354, 316, 728, 122, 375, 2470, 966, 478, 1837, 353, 363, 311, 3603, 4658, 364, 299, 317, 2434]`；pieces `["Ġpl", "ate", "Ġof", "Ġs", "and", "w", "ic", "hes", "Ġco", "ve", "red", "Ġin", "Ġb", "er", "ries", "Ġnext", "Ġto", "Ġa", "Ġc", "ake"]`；decode " plate of sandwiches covered in berries next to a cake"
- 自动分类：`complex_edit`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因："non_contiguous_edit_blocks=2;word_order_change;obvious_rewrite_by_fixed_coverage_rule"
- Token 边界提示：[]

### 14. `swap_object:207`

- 负例类型：`swap_object`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："A dog rests on a bed in a bedroom where one person is also sitting."
- 正描述 2："A person is sitting where a dog also rests on a bed in a bedroom."
- 负描述："One person rests on a bed in a bedroom where a dog is also sitting."
- 自动来源：`positive_1` / "A dog rests on a bed in a bedroom where one person is also sitting."
- 正确片段："A dog rests on a bed in a bedroom where one person"
- 错误片段："One person rests on a bed in a bedroom where a dog"
- 正确片段 token：IDs `[68, 1041, 106, 5128, 118, 619, 299, 363, 382, 353, 299, 363, 382, 393, 444, 1828, 1623, 2198]`；pieces `["A", "Ġdo", "g", "Ġrest", "s", "Ġon", "Ġa", "Ġb", "ed", "Ġin", "Ġa", "Ġb", "ed", "ro", "om", "Ġwhere", "Ġone", "Ġperson"]`；decode "A dog rests on a bed in a bedroom where one person"
- 错误片段 token：IDs `[82, 1763, 2198, 5128, 118, 619, 299, 363, 382, 353, 299, 363, 382, 393, 444, 1828, 299, 1041, 106]`；pieces `["O", "ne", "Ġperson", "Ġrest", "s", "Ġon", "Ġa", "Ġb", "ed", "Ġin", "Ġa", "Ġb", "ed", "ro", "om", "Ġwhere", "Ġa", "Ġdo", "g"]`；decode "One person rests on a bed in a bedroom where a dog"
- 自动分类：`complex_edit`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因："non_contiguous_edit_blocks=2;word_order_change;obvious_rewrite_by_fixed_coverage_rule"
- Token 边界提示：[]

### 15. `swap_object:209`

- 负例类型：`swap_object`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："A person is holding a baby who is wrapped in a towel and holding a toothbrush"
- 正描述 2："The baby, who is wrapped in a towel and holding a toothbrush, is being held by a person."
- 负描述："A person is holding a toothbrush while the baby wrapped in a towel looks on."
- 自动来源：`positive_1` / "A person is holding a baby who is wrapped in a towel and holding a toothbrush"
- 正确片段："baby who is wrapped in a towel and holding a toothbrush"
- 错误片段："toothbrush while the baby wrapped in a towel looks on."
- 正确片段 token：IDs `[363, 572, 124, 2109, 395, 339, 559, 737, 382, 353, 299, 364, 122, 446, 376, 429, 2569, 350, 299, 364, 114, 495, 101, 117, 4923]`；pieces `["Ġb", "ab", "y", "Ġwho", "Ġis", "Ġw", "ra", "pp", "ed", "Ġin", "Ġa", "Ġto", "w", "el", "Ġand", "Ġh", "old", "ing", "Ġa", "Ġto", "o", "th", "b", "r", "ush"]`；decode " baby who is wrapped in a towel and holding a toothbrush"
- 错误片段 token：IDs `[364, 114, 495, 101, 117, 4923, 3052, 309, 363, 572, 124, 339, 559, 737, 382, 353, 299, 364, 122, 446, 1853, 1275, 619, 49]`；pieces `["Ġto", "o", "th", "b", "r", "ush", "Ġwhile", "Ġthe", "Ġb", "ab", "y", "Ġw", "ra", "pp", "ed", "Ġin", "Ġa", "Ġto", "w", "el", "Ġloo", "ks", "Ġon", "."]`；decode " toothbrush while the baby wrapped in a towel looks on."
- 自动分类：`complex_edit`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因："non_contiguous_edit_blocks=3;obvious_rewrite_by_fixed_coverage_rule"
- Token 边界提示：[]

### 16. `swap_object:220`

- 负例类型：`swap_object`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："A sign with the word pub sits on a wall and underneath it on a table is a blender and three bottles of variety of alcohol and some flavoring."
- 正描述 2："A pub sign is mounted on a wall, and below it on a table are three bottles of different types of alcohol, a blender and some flavorings."
- 负描述："A sign with the word pub sits on a table and underneath it on a wall is a blender and three bottles of variety of alcohol and some flavoring."
- 自动来源：`positive_1` / "A sign with the word pub sits on a wall and underneath it on a table is a blender and three bottles of variety of alcohol and some flavoring."
- 正确片段："wall and underneath it on a table"
- 错误片段："table and underneath it on a wall"
- 正确片段 token：IDs `[339, 1266, 376, 1943, 1763, 1831, 563, 619, 299, 2630]`；pieces `["Ġw", "all", "Ġand", "Ġunder", "ne", "ath", "Ġit", "Ġon", "Ġa", "Ġtable"]`；decode " wall and underneath it on a table"
- 错误片段 token：IDs `[2630, 376, 1943, 1763, 1831, 563, 619, 299, 339, 1266]`；pieces `["Ġtable", "Ġand", "Ġunder", "ne", "ath", "Ġit", "Ġon", "Ġa", "Ġw", "all"]`；decode " table and underneath it on a wall"
- 自动分类：`complex_edit`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因："non_contiguous_edit_blocks=2;word_order_change"
- Token 边界提示：[]

### 17. `swap_object:23`

- 负例类型：`swap_object`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："a person holding a surf board in a body of water."
- 正描述 2："A person is in a body of water holding a surfboard."
- 负描述："A surf board holding a person in a body of water."
- 自动来源：`positive_1` / "a person holding a surf board in a body of water."
- 正确片段："a person holding a surf board"
- 错误片段："A surf board holding a person"
- 正确片段 token：IDs `[100, 2198, 429, 2569, 350, 299, 3946, 105, 1847, 1433]`；pieces `["a", "Ġperson", "Ġh", "old", "ing", "Ġa", "Ġsur", "f", "Ġbo", "ard"]`；decode "a person holding a surf board"
- 错误片段 token：IDs `[68, 3946, 105, 1847, 1433, 429, 2569, 350, 299, 2198]`；pieces `["A", "Ġsur", "f", "Ġbo", "ard", "Ġh", "old", "ing", "Ġa", "Ġperson"]`；decode "A surf board holding a person"
- 自动分类：`complex_edit`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因："non_contiguous_edit_blocks=2;word_order_change"
- Token 边界提示：[]

### 18. `swap_object:231`

- 负例类型：`swap_object`
- 阶段三范围：`pilot`；certifying formal：`False`
- 正描述 1："A truck is shown with another car in the back of it."
- 正描述 2："TAnother car is positioned behind the truck in the image."
- 负描述："Another car is shown with a truck in the back of it."
- 自动来源：`positive_1` / "A truck is shown with another car in the back of it."
- 正确片段：" truck is shown with another car"
- 错误片段："nother car is shown with a truck"
- 正确片段 token：IDs `[68, 1144, 120, 892, 395, 1128, 2791, 599, 5467, 3751]`；pieces `["A", "Ġtr", "u", "ck", "Ġis", "Ġsh", "own", "Ġwith", "Ġanother", "Ġcar"]`；decode "A truck is shown with another car"
- 错误片段 token：IDs `[5799, 3861, 3751, 395, 1128, 2791, 599, 299, 1144, 120, 892]`；pieces `["An", "other", "Ġcar", "Ġis", "Ġsh", "own", "Ġwith", "Ġa", "Ġtr", "u", "ck"]`；decode "Another car is shown with a truck"
- 自动分类：`complex_edit`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因："non_contiguous_edit_blocks=2"
- Token 边界提示：[]

### 19. `swap_object:244`

- 负例类型：`swap_object`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："The woman in the diner and the man looking into the window are making eye contact."
- 正描述 2："The man in the window is facing the woman in the diner, and they are making eye contact."
- 负描述："The man in the diner and the woman looking into the window are making eye contact."
- 自动来源：`positive_1` / "The woman in the diner and the man looking into the window are making eye contact."
- 正确片段："woman in the diner and the "
- 错误片段："man in the diner and the wo"
- 正确片段 token：IDs `[339, 444, 325, 353, 309, 373, 301, 311, 376, 309, 1672]`；pieces `["Ġw", "om", "an", "Ġin", "Ġthe", "Ġd", "in", "er", "Ġand", "Ġthe", "Ġman"]`；decode " woman in the diner and the man"
- 错误片段 token：IDs `[1672, 353, 309, 373, 301, 311, 376, 309, 339, 444, 325]`；pieces `["Ġman", "Ġin", "Ġthe", "Ġd", "in", "er", "Ġand", "Ġthe", "Ġw", "om", "an"]`；decode " man in the diner and the woman"
- 自动分类：`complex_edit`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因："non_contiguous_edit_blocks=2"
- Token 边界提示：[]

### 20. `swap_object:29`

- 负例类型：`swap_object`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："A person pats an elephant as a couple people watch."
- 正描述 2：" a couple of people are observing an elephant being patted by a person."
- 负描述："A couple people pat an elephant as a person watches."
- 自动来源：`None` / null
- 正确片段：""
- 错误片段：""
- 正确片段 token：IDs `[]`；pieces `[]`；decode ""
- 错误片段 token：IDs `[]`；pieces `[]`；decode ""
- 自动分类：`ambiguous_source`
- 来源规则："character_and_token_distance_rankings_conflict"
- 失败原因："character_and_token_distance_rankings_conflict"
- Token 边界提示：[]

### 21. `swap_object:39`

- 负例类型：`swap_object`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："A dog is sitting on a neatly made bed while someone looks on. "
- 正描述 2："The person is observing a dog sitting on a clean and made bed."
- 负描述："Someone is sitting on a neatly made bed while a dog looks on."
- 自动来源：`positive_1` / "A dog is sitting on a neatly made bed while someone looks on. "
- 正确片段："A dog is sitting on a neatly made bed while someone looks on. "
- 错误片段："Someone is sitting on a neatly made bed while a dog looks on."
- 正确片段 token：IDs `[68, 1041, 106, 395, 5305, 2912, 619, 299, 730, 314, 542, 4303, 363, 382, 3052, 4779, 1853, 1275, 619, 49, 256]`；pieces `["A", "Ġdo", "g", "Ġis", "Ġsit", "ting", "Ġon", "Ġa", "Ġne", "at", "ly", "Ġmade", "Ġb", "ed", "Ġwhile", "Ġsomeone", "Ġloo", "ks", "Ġon", ".", "Ġ"]`；decode "A dog is sitting on a neatly made bed while someone looks on. "
- 错误片段 token：IDs `[86, 3219, 1634, 395, 5305, 2912, 619, 299, 730, 314, 542, 4303, 363, 382, 3052, 299, 1041, 106, 1853, 1275, 619, 49]`；pieces `["S", "ome", "one", "Ġis", "Ġsit", "ting", "Ġon", "Ġa", "Ġne", "at", "ly", "Ġmade", "Ġb", "ed", "Ġwhile", "Ġa", "Ġdo", "g", "Ġloo", "ks", "Ġon", "."]`；decode "Someone is sitting on a neatly made bed while a dog looks on."
- 自动分类：`complex_edit`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因："non_contiguous_edit_blocks=2;word_order_change;obvious_rewrite_by_fixed_coverage_rule"
- Token 边界提示：[]

### 22. `swap_object:42`

- 负例类型：`swap_object`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："A black and white photograph of a stuffed teddy bear wearing a shirt that reads handle with care and a small stuffed sheep."
- 正描述 2："A monochrome photo of a small stuffed sheep along with a stuffed teddy bear wearing a shirt that reads handle with care."
- 负描述："A black and white photograph of a small stuffed sheep wearing a shirt that reads handle with care and a stuffed teddy bear."
- 自动来源：`positive_1` / "A black and white photograph of a stuffed teddy bear wearing a shirt that reads handle with care and a small stuffed sheep."
- 正确片段："tuffed teddy bear wearing a shirt that reads handle with care and a small stuffed sheep"
- 错误片段："mall stuffed sheep wearing a shirt that reads handle with care and a stuffed teddy bear"
- 正确片段 token：IDs `[580, 120, 1627, 382, 297, 382, 103, 124, 600, 370, 796, 370, 350, 299, 1128, 4193, 591, 3094, 118, 3319, 361, 599, 317, 1093, 376, 299, 3436, 580, 120, 1627, 382, 3191, 1522]`；pieces `["Ġst", "u", "ff", "ed", "Ġt", "ed", "d", "y", "Ġbe", "ar", "Ġwe", "ar", "ing", "Ġa", "Ġsh", "irt", "Ġthat", "Ġread", "s", "Ġhand", "le", "Ġwith", "Ġc", "are", "Ġand", "Ġa", "Ġsmall", "Ġst", "u", "ff", "ed", "Ġshe", "ep"]`；decode " stuffed teddy bear wearing a shirt that reads handle with care and a small stuffed sheep"
- 错误片段 token：IDs `[3436, 580, 120, 1627, 382, 3191, 1522, 796, 370, 350, 299, 1128, 4193, 591, 3094, 118, 3319, 361, 599, 317, 1093, 376, 299, 580, 120, 1627, 382, 297, 382, 103, 124, 600, 370]`；pieces `["Ġsmall", "Ġst", "u", "ff", "ed", "Ġshe", "ep", "Ġwe", "ar", "ing", "Ġa", "Ġsh", "irt", "Ġthat", "Ġread", "s", "Ġhand", "le", "Ġwith", "Ġc", "are", "Ġand", "Ġa", "Ġst", "u", "ff", "ed", "Ġt", "ed", "d", "y", "Ġbe", "ar"]`；decode " small stuffed sheep wearing a shirt that reads handle with care and a stuffed teddy bear"
- 自动分类：`complex_edit`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因："non_contiguous_edit_blocks=4;obvious_rewrite_by_fixed_coverage_rule"
- Token 边界提示：[]

### 23. `swap_object:47`

- 负例类型：`swap_object`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："Several kites sit on the ground, with a few people in the background."
- 正描述 2："with a few people in the background, several kites are visible on the ground."
- 负描述："Several people sit on the ground, with a few kites in the background."
- 自动来源：`positive_1` / "Several kites sit on the ground, with a few people in the background."
- 正确片段："kites sit on the ground, with a few people"
- 错误片段："people sit on the ground, with a few kites"
- 正确片段 token：IDs `[914, 338, 329, 5305, 619, 309, 492, 2383, 47, 599, 299, 4654, 2975]`；pieces `["Ġk", "it", "es", "Ġsit", "Ġon", "Ġthe", "Ġg", "round", ",", "Ġwith", "Ġa", "Ġfew", "Ġpeople"]`；decode " kites sit on the ground, with a few people"
- 错误片段 token：IDs `[2975, 5305, 619, 309, 492, 2383, 47, 599, 299, 4654, 914, 338, 329]`；pieces `["Ġpeople", "Ġsit", "Ġon", "Ġthe", "Ġg", "round", ",", "Ġwith", "Ġa", "Ġfew", "Ġk", "it", "es"]`；decode " people sit on the ground, with a few kites"
- 自动分类：`complex_edit`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因："non_contiguous_edit_blocks=2;word_order_change;obvious_rewrite_by_fixed_coverage_rule"
- Token 边界提示：[]

### 24. `swap_object:72`

- 负例类型：`swap_object`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："A thick crust cut pizza on a plate with wine by its side."
- 正描述 2："A pizza with a thick crust is sliced and placed on a plate, and wine is positioned beside it."
- 负描述："A glass of wine on a plate with a thick crust cut pizza by its side."
- 自动来源：`positive_1` / "A thick crust cut pizza on a plate with wine by its side."
- 正确片段："thick crust cut pizza on a plate with wine"
- 错误片段："glass of wine on a plate with a thick crust cut pizza"
- 正确片段 token：IDs `[445, 2437, 5347, 1076, 5431, 344, 1028, 125, 100, 619, 299, 1219, 557, 599, 339, 1016]`；pieces `["Ġth", "ick", "Ġcr", "ust", "Ġcut", "Ġp", "iz", "z", "a", "Ġon", "Ġa", "Ġpl", "ate", "Ġwith", "Ġw", "ine"]`；decode " thick crust cut pizza on a plate with wine"
- 错误片段 token：IDs `[492, 111, 1388, 354, 339, 1016, 619, 299, 1219, 557, 599, 299, 445, 2437, 5347, 1076, 5431, 344, 1028, 125, 100]`；pieces `["Ġg", "l", "ass", "Ġof", "Ġw", "ine", "Ġon", "Ġa", "Ġpl", "ate", "Ġwith", "Ġa", "Ġth", "ick", "Ġcr", "ust", "Ġcut", "Ġp", "iz", "z", "a"]`；decode " glass of wine on a plate with a thick crust cut pizza"
- 自动分类：`complex_edit`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因："non_contiguous_edit_blocks=2;obvious_rewrite_by_fixed_coverage_rule"
- Token 边界提示：[]

### 25. `swap_object:76`

- 负例类型：`swap_object`
- 阶段三范围：`formal`；certifying formal：`False`
- 正描述 1："Three people on packed snow trail, two skiing, one walking."
- 正描述 2："Three individuals are on a packed snow trail with two of them skiing and the third one walking."
- 负描述："Three people on packed snow trail, one skiing, two walking."
- 自动来源：`positive_1` / "Three people on packed snow trail, two skiing, one walking."
- 正确片段："two skiing, one"
- 错误片段："one skiing, two"
- 正确片段 token：IDs `[2102, 2549, 108, 350, 47, 1623]`；pieces `["Ġtwo", "Ġsk", "i", "ing", ",", "Ġone"]`；decode " two skiing, one"
- 错误片段 token：IDs `[1623, 2549, 108, 350, 47, 2102]`；pieces `["Ġone", "Ġsk", "i", "ing", ",", "Ġtwo"]`；decode " one skiing, two"
- 自动分类：`complex_edit`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因："non_contiguous_edit_blocks=2;word_order_change"
- Token 边界提示：[]

### 26. `swap_object:78`

- 负例类型：`swap_object`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："A traffic light on a metal pole by a tree."
- 正描述 2："A traffic light is placed on a metal pole adjacent to a tree."
- 负描述："A traffic light on a tree by a metal pole."
- 自动来源：`positive_1` / "A traffic light on a metal pole by a tree."
- 正确片段："metal pole by a tre"
- 错误片段："tree by a metal pol"
- 正确片段 token：IDs `[4743, 352, 927, 361, 769, 299, 297, 1382]`；pieces `["Ġmet", "al", "Ġpo", "le", "Ġby", "Ġa", "Ġt", "ree"]`；decode " metal pole by a tree"
- 错误片段 token：IDs `[297, 1382, 769, 299, 4743, 352, 927, 361]`；pieces `["Ġt", "ree", "Ġby", "Ġa", "Ġmet", "al", "Ġpo", "le"]`；decode " tree by a metal pole"
- 自动分类：`complex_edit`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因："non_contiguous_edit_blocks=2"
- Token 边界提示：[]

### 27. `swap_object:85`

- 负例类型：`swap_object`
- 阶段三范围：`formal`；certifying formal：`False`
- 正描述 1："A picture of a bathroom with a fern plant near the sink and a photo of a city above the toilet. "
- 正描述 2："A photograph of a bathroom featuring a sink with a fern plant nearby, and a depiction of a city situated above the toilet."
- 负描述："A picture of a bathroom with a photo of a city near the sink and a fern plant above the toilet."
- 自动来源：`positive_1` / "A picture of a bathroom with a fern plant near the sink and a photo of a city above the toilet. "
- 正确片段："fern plant near the sink and a photo of a city above the toilet. "
- 错误片段："photo of a city near the sink and a fern plant above the toilet."
- 正确片段 token：IDs `[341, 2107, 1219, 811, 730, 370, 309, 316, 3010, 376, 299, 2001, 593, 114, 354, 299, 3972, 6264, 309, 364, 1299, 119, 49, 256]`；pieces `["Ġf", "ern", "Ġpl", "ant", "Ġne", "ar", "Ġthe", "Ġs", "ink", "Ġand", "Ġa", "Ġph", "ot", "o", "Ġof", "Ġa", "Ġcity", "Ġabove", "Ġthe", "Ġto", "ile", "t", ".", "Ġ"]`；decode " fern plant near the sink and a photo of a city above the toilet. "
- 错误片段 token：IDs `[2001, 593, 114, 354, 299, 3972, 730, 370, 309, 316, 3010, 376, 299, 341, 2107, 1219, 811, 6264, 309, 364, 1299, 119, 49]`；pieces `["Ġph", "ot", "o", "Ġof", "Ġa", "Ġcity", "Ġne", "ar", "Ġthe", "Ġs", "ink", "Ġand", "Ġa", "Ġf", "ern", "Ġpl", "ant", "Ġabove", "Ġthe", "Ġto", "ile", "t", "."]`；decode " photo of a city near the sink and a fern plant above the toilet."
- 自动分类：`complex_edit`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因："non_contiguous_edit_blocks=2;word_order_change;obvious_rewrite_by_fixed_coverage_rule"
- Token 边界提示：[]

### 28. `swap_object:86`

- 负例类型：`swap_object`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："A train at the station with no passengers around."
- 正描述 2："At the station, there is a train with no passengers nearby."
- 负描述："Passengers at the station with no train around."
- 自动来源：`positive_1` / "A train at the station with no passengers around."
- 正确片段："A train at the station with no passengers"
- 错误片段："Passengers at the station with no train"
- 正确片段 token：IDs `[68, 1946, 301, 1248, 309, 580, 489, 599, 2396, 3241, 1979, 496]`；pieces `["A", "Ġtra", "in", "Ġat", "Ġthe", "Ġst", "ation", "Ġwith", "Ġno", "Ġpass", "eng", "ers"]`；decode "A train at the station with no passengers"
- 错误片段 token：IDs `[83, 1388, 1979, 496, 1248, 309, 580, 489, 599, 2396, 1946, 301]`；pieces `["P", "ass", "eng", "ers", "Ġat", "Ġthe", "Ġst", "ation", "Ġwith", "Ġno", "Ġtra", "in"]`；decode "Passengers at the station with no train"
- 自动分类：`complex_edit`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因："non_contiguous_edit_blocks=2;obvious_rewrite_by_fixed_coverage_rule"
- Token 边界提示：[]

### 29. `swap_object:91`

- 负例类型：`swap_object`
- 阶段三范围：`pilot`；certifying formal：`False`
- 正描述 1："An adult standing behind a little child while holding an umbrella."
- 正描述 2："An adult holding an umbrella stands behind a little child."
- 负描述："A little child standing behind an adult while holding an umbrella."
- 自动来源：`positive_1` / "An adult standing behind a little child while holding an umbrella."
- 正确片段："n adult standing behind a little child"
- 错误片段：" little child standing behind an adult"
- 正确片段 token：IDs `[5799, 1200, 1005, 2823, 350, 5237, 916, 299, 406, 338, 5395, 6109]`；pieces `["An", "Ġad", "ult", "Ġstand", "ing", "Ġbeh", "ind", "Ġa", "Ġl", "it", "tle", "Ġchild"]`；decode "An adult standing behind a little child"
- 错误片段 token：IDs `[68, 406, 338, 5395, 6109, 2823, 350, 5237, 916, 346, 1200, 1005]`；pieces `["A", "Ġl", "it", "tle", "Ġchild", "Ġstand", "ing", "Ġbeh", "ind", "Ġan", "Ġad", "ult"]`；decode "A little child standing behind an adult"
- 自动分类：`complex_edit`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因："non_contiguous_edit_blocks=2"
- Token 边界提示：[]

### 30. `swap_object:98`

- 负例类型：`swap_object`
- 阶段三范围：`formal`；certifying formal：`True`
- 正描述 1："A person stands on a fishing boat as the tide rolls in from the shore on a desolate beach."
- 正描述 2："The tide comes in from the shore on an empty beach with a person on a fishing boat."
- 负描述："A person stands on the shore as the tide rolls in from a fishing boat on a desolate beach."
- 自动来源：`positive_1` / "A person stands on a fishing boat as the tide rolls in from the shore on a desolate beach."
- 正确片段："a fishing boat as the tide rolls in from the shore"
- 错误片段："the shore as the tide rolls in from a fishing boat"
- 正确片段 token：IDs `[299, 341, 1689, 350, 1847, 314, 523, 309, 297, 688, 1552, 1989, 118, 353, 961, 309, 1128, 1239]`；pieces `["Ġa", "Ġf", "ish", "ing", "Ġbo", "at", "Ġas", "Ġthe", "Ġt", "ide", "Ġro", "ll", "s", "Ġin", "Ġfrom", "Ġthe", "Ġsh", "ore"]`；decode " a fishing boat as the tide rolls in from the shore"
- 错误片段 token：IDs `[309, 1128, 1239, 523, 309, 297, 688, 1552, 1989, 118, 353, 961, 299, 341, 1689, 350, 1847, 314]`；pieces `["Ġthe", "Ġsh", "ore", "Ġas", "Ġthe", "Ġt", "ide", "Ġro", "ll", "s", "Ġin", "Ġfrom", "Ġa", "Ġf", "ish", "ing", "Ġbo", "at"]`；decode " the shore as the tide rolls in from a fishing boat"
- 自动分类：`complex_edit`
- 来源规则："positive_1_pareto_dominates_character_and_token_distance"
- 失败原因："non_contiguous_edit_blocks=2;word_order_change;obvious_rewrite_by_fixed_coverage_rule"
- Token 边界提示：[]
