# 问题与解决经验索引

这是项目问题记录的唯一目录入口，归档原问题、依据、处理效果和剩余限制。它不替代Issue任务、PROJECT_STATE现状、DECISIONS批准记录或原始实验报告；原证据保留原路径。历史问题的新进展追加到相应记录时须保留版本／证据边界，不拆分每条Reviewer表示缺陷凑数量。

归档日期2026-10-12；依据[Issue #12](https://github.com/yuhong-zhang202/MatsterArbeit_Rampmetering/issues/12)。以下严重程度是本索引的影响分级，不是GitHub Reviewer P等级。OPEN=问题仍待处理；MITIGATED=限定范围缓解；CLOSED=指定技术子问题结束；NO-GO=指定路线的有界否定建议，不代表物理不可能或用户新科研决定。

| ID／问题 | 日期／阶段 | 影响 | 状态 | 根因边界／处理 | Issue／PR及原证据 | 阻塞正式实验？ |
|---|---|---|---|---|---|---|
| [PRB-001：FIX02服务跟踪](PRB-001_FIX02_SERVICE_TRACKING.md) | 10-07开发 | 高 | OPEN | 缺额确认；唯一因果贡献未识别；保留71/72 FAIL | Issue2／PR3；开发总结与逐窗口表 | 是：实际服务资格未获证明 |
| [PRB-002：STOP3／A1证明缺口](PRB-002_STOP3_A1_PROOF_GAP.md) | 10-08～11技术／离线 | 高 | NO-GO，限定当前接口证明路线建议 | 旧guard可重现；原生未来联合状态证明不足 | Issue4/6/8/10；PR5/7/9/11；A07与A1报告 | 完整A1路线无资格；不证明原生控制不可用 |
| [PRB-003：receiver WAIT／预算](PRB-003_RECEIVER_WAIT_AND_BUDGET.md) | 10-12独立诊断 | 中 | MITIGATED；预算子问题CLOSED | 假设推进与实际等待分清；300/360完成、420/480跳过 | 原W300／WAIT／预算原报告；Issue12 | 本局部问题缓解，安全覆盖和服务限制仍在 |
| [PRB-004：名义双车放行](PRB-004_NOMINAL_TWO_CAR_DISCHARGE.md) | 10-12原因分析/Issue12诊断 | 高 | MITIGATED，限定技术点 | G4/FIX300及短packet900实测双车；全域/长期未资格 | 六周期数据／原因报告；Issue12 | 是：旧E6/N3保留；300/900局部改善不等于300–900资格 |

本次仅回填四个独立问题；预算按Issue要求并入接收恢复记录，覆盖五类必需历史事项。没有迁移开发报告、原始数据或历史日志；未发现现有独立问题记录需移动。本轮政策选择和有界实际诊断见Issue12交付报告；三方GO交付不代替用户验收。当前Candidate A NOT_QUALIFIED、A1 UNRESOLVED、Stage6既有结项和空／未冻结正式协议保持。

旧WAIT完整raw仍在独立工作区；Issue12新raw在主目录data/raw/issue12_alinea_actuation_20261012_v1/。GitHub交付仅紧凑摘要、精确源/input/raw清单与哈希，完整raw仅本地，canonical权限不上传。Issue／PR用于任务和依赖身份。下一步建议不构成执行授权。
