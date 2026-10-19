# Schema

kb.schema.json采用JSON Schema Draft-07，约束data/kb.json总库。definitions中的各记录类型也可用于单表导入。schema中的example.invalid为标识符，验证使用本地文件。跨表引用、镜像一致性与层级规则由tools/validate.py补充检查。

v1.5新增game_scene_coverage集合、序章NBT段落、0级剧透和可选context_record_ids。迁移时使用更新后的schema与工具；原集合和ID含义保留。

v1.6新增game_material_coverage（第21个集合）、严格语音定位与发信日期结构、材料所属角色及可选关系阶段字段。game_lore扩展来信、大厅、服装、信物和招聘合同类型及各自叙事层；所有补充材料仍按16级剧透门槛处理。客户端和音频核对状态当前均约束为false，变更前需要相应证据与迁移。旧记录及ID保留；新编号中的间隔按去重过程保留。

v1.7新增game_localization_checks、材料对照引用、语音英文文本状态及server/language配对约束；对照项的三版、来源、哈希与双向链接还由check_v17.py验证。schema反例扩展为20项。

v1.8新增game_discussion_guides（第23个集合），严格约束编者导航、提纲引用与默认检索关闭；跨表引用、提纲依据集合及剧透等级由check_v18.py检查。schema反例共22项。

v1.9新增game_answer_reviews（第24集合）及metadata.maintenance。逐话索引允许1—13话，未核播放目录时长以not_reviewed/null成对保存；catalog_minutes保持正整数。回答样本引用与上下文由check_v19.py验证，语义结论由单一编者记录。schema反例25项。
