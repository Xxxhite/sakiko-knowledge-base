# Schema

kb.schema.json采用JSON Schema Draft-07，约束data/kb.json总库。definitions中的各记录类型也可用于单表导入。schema中的example.invalid为标识符，验证使用本地文件。跨表引用、镜像一致性与层级规则由tools/validate.py补充检查。
