# 首次自然需求技术运行：待人类预算与精确放行

**REQUEST_ONLY / NOT_APPROVED / PREPARED_NOT_RELEASED。** 本文件不构成批准、canonical release或运行权限。当前不运行SUMO、不合并PR。唯一资格工作为[Issue #14](https://github.com/yuhong-zhang202/MatsterArbeit_Rampmetering/issues/14)，交付在依赖PR13的[Draft PR #15](https://github.com/yuhong-zhang202/MatsterArbeit_Rampmetering/pull/15)。

## 准确对象

- 仅首身份：`QUAL_NATURAL_ALINEA_R900_S17_01`。
- 卡：`artifacts/natural_actuator_qualification_20261015_v1/engineering/packages_v1/QUAL_NATURAL_ALINEA_R900_S17_01/card.json`。
- 卡SHA-256：`b73c678130604d1cef41dd5ecb70a79cc868084e91ae5033cc179393c25f6982`。
- 精确源摘要：`c2f00d7f66ea66e331e436248bf34d510fc8ba11a99b16792cd80e18f61055b2`，173项；可执行代码checkpoint `b6c60b927fc71a8750f5674f2cf168824b78cf05`。后续仅卡、回执和状态文档提交不改变该执行源。
- 原PR13上游：`61612bf6e240d41d2ca4be95a02429f48c9ddd54`。它的定点GitHub review必须完成并无未处理的实质阻碍；当前仍Running，不能称已完成。

## 拟批准的唯一新增范围

为`NATURAL_QUALIFICATION_20261015_V1`新增独立**总900墙钟秒**，并仅放行本卡的一次非正式技术运行。worker内限870秒、清理预留30秒计入900；启动限60秒；实时最低5,000,000,000字节自由空间，无固定输出字节门。由外层guardian管理其直接worker及经过实际身份核实的专属native同组；必须允许读取PID/PGID/SID以完成库存与清理。实际耗时、超额和未知都记录，不声称绝对无超额。

旧600秒scope已耗475.645467625秒，余124.354532375秒；旧账不重置、不转入新scope。新增预算和精确执行批准缺失时available=null，不能用旧余额启动。第二身份未准备、未释放；本次答复不能成为第二次自动运行许可。最多两次身份的上限不等于应当用完次数。

同一既有自然4050车输入，M3600/R900/U360/X180、seed17、dt1、0–4200秒、600秒起控、[1200,3000)六个300秒窗；原ALINEA参数、车型、网络、需求及速度因子不改。precision8仅测量输出。无正式效果矩阵、无换seed或失败重试、无合并。

出现合同规定的碰撞、异常制动、违规新入口、身份／人口／车尾／日志或其它安全UNKNOWN即停止并保存原始证据。普通N0/1与已知供给／接收限制不自动当执行器故障；C−N和原因不明仍如实报告，名义账准确不自动给QUALIFIED。

## 实际放行前仍须全部满足

1. PR13本轮准确616定点review完成，无未处理实质阻碍；卡／源／输入不发生漂移。
2. 本卡工程、独立数据、只读科学实际字段回执完整且SHA匹配，运行环境141项hash、Python版本、5GB实时门及实际PID观察权限再核。
3. 人类明确批准新增独立900秒预算，并明确仅对上列卡解除当前noSUMO；保留可核验直接答复，不能由AI替答或从完整目标推断。
4. 基于真实批准和精确三方回执形成当前canonical release；现有prepare记录、旧canonical或本文件均不能替代。
5. outer guardian执行前验证全部门，只有此后才分配唯一raw身份和启动一次native；失败／unknown资源不自行释放，须实际后审与结算。

当前卡执行授权false、实际观察全null；无新raw、guardian运行上下文、预算批准、精确运行批准或canonical。实际自然安全／持续服务／城市表现与资源性能均NOT_TESTED，总体NOT_QUALIFIED。用户可选择继续等待review而不批准运行；这不妨碍查看已经完成的代码与卡证据。
