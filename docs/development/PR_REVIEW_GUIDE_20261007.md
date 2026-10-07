# 开发试跑 PR 审查入口

本次仅交付已完成的D-019开发工作，供用户和Chat审查。用户明确要求本次先提交PR；没有关联Issue，没有Issue验收条件。PR使用Draft，总体交付状态为“实现完成，待审查”，不代表用户验收或正式实验授权。

## 建议阅读顺序

1. [开发总结](DEVELOPMENT_TRIAL_SUMMARY_20261007.md)：18格覆盖、分类成本、服务失败、残留与版本边界。
2. [独立数据报告V2](../../data/processed/formal_development_20261007_v1/DATA_REPORT_FIX02_FINAL_V2.md)与[最终验证回执](../../data/processed/formal_development_20261007_v1/FINAL_DELIVERY_VALIDATION_V2.json)。
3. [工程总结](../../artifacts/formal_development_20261007_v1/engineering/FIX02_FINAL_ENGINEERING_SUMMARY.md)、[16次执行台账](../../artifacts/formal_development_20261007_v1/engineering/FINAL_EXECUTION_LEDGER.json)、[最终科学审查](../../artifacts/formal_development_20261007_v1/FINAL_SCIENTIFIC_REVIEW.md)。
4. [正式实验草案v1](../正式实验设计草案v1.md)：保留为Proposed的背景材料，不是本次获批的正式协议。

## 在线与本地证据

本PR明确选择发布：6个开发源码文件、版本化输入卡片／配置／释放记录、技术修复与失败摘要、独立分析源码快照和精选检查报告、汇总CSV及PNG。保留原路径以使开发总结的主要相对链接在GitHub可打开。生成数据继续默认被`.gitignore`排除，本次仅按显式文件清单纳入审查证据，不放宽全局忽略规则。

[发布清单](../../artifacts/formal_development_20261007_v1/pr_review/PUBLISH_MANIFEST.json)记录选定文件的SHA-256；[打包核对](../../artifacts/formal_development_20261007_v1/pr_review/PACKAGING_CHECKS.json)记录历史源码快照、现有原始输出清单和关键证据的身份核验。

以下**没有新上传**：`data/raw/formal_development_20261007_v1/`约1.323 GB原始FCD、逐秒控制日志及XML；未选中的大型逐车派生内容；私人Robert邮件；MemoryCore数据、候选及恢复脚本。它们未被删除、移动或改写。

[本地证据索引](../../artifacts/formal_development_20261007_v1/pr_review/LOCAL_ONLY_EVIDENCE.json)保留路径、大小、SHA-256；16次运行的[回执](../../artifacts/formal_development_20261007_v1/receipts/)在线提供各输出文件的原始manifest。哈希和摘要使交付可追踪，但不能代替读取原始内容；Chat无法仅靠本PR重新执行完整原始数据审计。需要时由用户另行提供指定文件或授权共享。

某些历史回执包含本机绝对路径。这些是来源标识，不是可在线访问的URL。主要审查材料使用本仓库相对链接，PR正文使用固定提交永久链接。历史报告里的“待最终审查”等字样反映生成顺序；最新总体结论由最终科学审查及开发总结给出，不能改写旧签核文件来消除时间差。原`FINAL_DOCUMENT_VERIFICATION.json`仍绑定开发结束时的文档；本次新增交接文字由新的打包记录覆盖，不重写旧哈希。

## 本次验证的含义

历史仿真发生在首次交付commit之前，基于`48d3b327fee805e7f9bb6d2cc04d2fee955c242d`上的工作区源码快照。其准确版本由源码、输入、SUMO二进制和参数哈希绑定。打包时核对这些相关字节与交付index一致，不声称历史上运行过尚不存在的Git commit，也没有为了PR重新启动仿真。

历史环境记录为macOS、Python3.13项目venv、SUMO1.26.0、TraCI/sumolib1.26.0、sumoITScontrol0.1.0；Python具体patch和完整操作系统/build环境未完整锁定。绝对路径、SUMO安装和本地原始数据仍是完整复现依赖，未验证任意新电脑开箱即跑。已用卡片与输出目录不可重启；后续运行需要相应授权与新版本绑定。

## 必须保留的结论边界

- 开发覆盖完成，与服务能力合格是不同条件。12个控制运行整体`NOT_QUALIFIED`；72窗口中71失败、1通过。
- R900控制有终点残留，采用截至4200 s的完整请求群体截断成本，不能仅报告完成者。
- 修复前控制不得混入FIX02效应；严格30 s连续链阴性保留。
- 没有正式sweet spot结论，没有唯一识别全部U损失的物理回溢原因。Stage6保持既有结项状态，正式协议仍未冻结。

下一位接手：用户和Chat，审查本PR并确认未来Issue／验收条件及执行方式、评价终点等待决项。**下一步建议不构成执行授权。**
