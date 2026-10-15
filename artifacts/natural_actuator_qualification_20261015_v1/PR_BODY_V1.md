## 范围与依赖

Refs #14。基于 Draft PR #13 的准确 `61612bf6e240d41d2ca4be95a02429f48c9ddd54`，base必须保持 `codex/issue-12-alinea-signal-policy`。资格准备与PR13最后pending字段定点复审分别记录；本PR不合并或替代上游审查。

本PR只完成自然需求资格所需的审计、精确首卡与资源／启动保护准备，**不运行SUMO、不合并PR**。自然安全／持续服务／实际资源性能均 `NOT_TESTED`，总体 `NOT_QUALIFIED`。正式协议未填充或冻结，未更改研究目标、ALINEA公式、需求、车辆模型、seed或正式参数。

## 必要实现

- 自然4050车既有输入，seed17／dt1／0–4200秒／600起控／1200–3000六窗。新包precision8只改变测量表示；原候选及旧raw不变。
- `policy.py`／`adapter.py`／`producer.py`保持616；bridge只增加直接native Popen后、TraCI前的3行启动身份记录钩子。新bridge按新源绑定，不声称与616全部字节相同。
- 新native reader独立读取manifest、native provenance／bridge receipt、流式FCD／TLS／ACK及身份／车尾／终点、E1、4050生命周期／系统成本与城市队列观察；旧synthetic reader不重标为原生。
- C／E_scheduled／E_executed／C_selected／C_applied／N及完整命令生命周期分开，物理短放不进入调度追债。数据完整性通过不自动变为服务资格通过；未观察或截断域保留UNKNOWN／NOT_TESTED。
- 新scope共900墙钟秒仅为提案，worker内限870＋清理30包含在900内；旧475.645467625已耗／124.354532375余额只披露，禁止pool。预算缺批准时可用量null，raw或pre-raw未知预留不自动释放。
- outer guardian只管理自己创建且核实的专属worker／native同组进程，异常早退继续检查／清理；身份或EOF不完整保持UNKNOWN，不做进程名扫描。执行还需准确人类运行授权、新数字预算、三方精确审查及canonical。

## 离线证据与边界

工程四个有界方法均有最终PASS证据；不是新完整suite或native测试。首次fixture路径错误和sandbox拒绝ps的UNKNOWN保留；相同普通Python正常／超时／父进程早退三组合工具escalation后PASS1.012秒。进程组inventory权限仍是未来运行前提。

- 工程报告：`artifacts/natural_actuator_qualification_20261015_v1/engineering/implementation_v1/ENGINEERING_REPORT_V1.md`
- 58文件绑定：`b5954b752ef9c06d8f5d18ece87ab150ebe2441bcaa7961fe6a4396105f7fee6`，主代理现场逐项匹配。
- 独立数据和科学终审、准确卡与源码绑定：完成后在本段以实际回执更新；目前不预报PASS。

所有历史FAIL、STOP3、原154版本、raw及旧审计回执保留。未启动native --version、netconvert、真实TraCI或SUMO；未创建实际运行批准／canonical，未分配新raw。

## 交付文档与停止点

STATE／WORKLOG／PRB-004／最小资格方案／准备说明／README及Dashboard同步具体事实。依据与访问层次见 `artifacts/thesis_actuator_readiness_20261015_v1/LITERATURE_AND_METHOD_BASIS.md`；C−E_scheduled为有说明的工程选择，不伪称文献要求。

首卡仅 `PREPARED_NOT_RELEASED`。完成全部独立准备和审查后，停在准确新数字预算与本卡直接人工运行授权门；旧批准、最多两次身份、Reviewer回复和本PR均不授权运行。第二身份不预备，必须由首项实际实质结果支持且同一新scope余量及全部权限有效。
