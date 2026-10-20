# Schema

kb.schema.json采用JSON Schema Draft-07，约束data/kb.json总库。definitions中的各记录类型也可用于单表导入。schema中的example.invalid为标识符，验证使用本地文件。跨表引用、镜像一致性与层级规则由tools/validate.py补充检查。

v1.5新增game_scene_coverage集合、序章NBT段落、0级剧透和可选context_record_ids。迁移时使用更新后的schema与工具；原集合和ID含义保留。

v1.6新增game_material_coverage（第21个集合）、严格语音定位与发信日期结构、材料所属角色及可选关系阶段字段。game_lore扩展来信、大厅、服装、信物和招聘合同类型及各自叙事层；所有补充材料仍按16级剧透门槛处理。客户端和音频核对状态当前均约束为false，变更前需要相应证据与迁移。旧记录及ID保留；新编号中的间隔按去重过程保留。

v1.7新增game_localization_checks、材料对照引用、语音英文文本状态及server/language配对约束；对照项的三版、来源、哈希与双向链接还由check_v17.py验证。schema反例扩展为20项。

v1.8新增game_discussion_guides（第23个集合），严格约束编者导航、提纲引用与默认检索关闭；跨表引用、提纲依据集合及剧透等级由check_v18.py检查。schema反例共22项。

v1.9新增game_answer_reviews（第24集合）及metadata.maintenance。逐话索引允许1—13话，未核播放目录时长以not_reviewed/null成对保存；catalog_minutes保持正整数。回答样本引用与上下文由check_v19.py验证，语义结论由单一编者记录。schema反例25项。

v1.10新增original_question_index（第25集合）及逐话work_id；EP与MYGO前缀分别绑定对应作品，公告日期允许null。跨作品同号集数的区分、主创复述与解读分层、原作查询由check_v110.py检查。统一验证12项，schema反例29项。v1.11扩展订正版、剧中作曲范围、分作者解读与22项原作自然问法；v1.12沿用schema，扩展转载取得路径、沙槌假设隔离、集数写法归一与30项原作自然问法。

v1.13沿用schema，扩展分页来源、交涉行为／动机分层、角色发言及既有关系保留的检查；原作自然问法38项，总查询／导航发现132项。

## 当前结构与验证

主库仍有25个集合。v1.17加入original_question_index可选answer_review，保存逐句text_zh、record_ids、layer和复核方法，随导航排除事实检索。字段结构由schema约束，引用与句子分层由Python检查。当前12项统一工具、188项查询／导航发现和33项schema反例；上面的版本段落为历史扩展记录。

仓库版本由data/kb.json的metadata.version、package.json及package-lock.json根版本共同保存；tools/validate.py检查一致性。Skill展示信息独立位于agents/openai.yaml。当前数据版本及安装方式见[README](../README.md)。
