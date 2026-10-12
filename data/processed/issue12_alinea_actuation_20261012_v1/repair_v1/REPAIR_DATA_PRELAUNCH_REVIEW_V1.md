# Issue12唯一dispatch修复：独立数据受影响预启动核查

2026-10-12。结论：PASS仅离线修复交付，支持科学审查**精确FIX01 R300**是否GO；R900仍条件预备、未放行。Context已刷新AGENTS／STATE／DECISIONS／协议0B／WORKLOG，Issue12技术准备中；首DIAG01一次失败保留，3启动上限已用1。Stage6既有结项、A1 UNRESOLVED、Candidate A NOT_QUALIFIED不变。

独立工程V2清单逐文件SHA全部匹配，FIX01卡9f914d8b…／BOUNDARY01卡60750bf6…及sources／prepared／inherited哈希一致；旧三卡字节不变，原prefix16文件绑定与data reader V3不变。adapter／policy与原105清单SHA一致；新影响限bridge dispatch、active identity/cap及相应CLI／回归。两fresh raw parent均不存在，实际只有原DIAG01 reservation；没有把已消费身份重新放行。

代码只在已绑定actual-red ACK、program/phase/state正确、整秒剩余red与周期终点相加相等时直接调用官方setPhaseDuration。先fsync写ATTEMPTED，再调用并完整readback time/program/phase/r/nextSwitch==cycleend；API异常或readback不符保留FAILED_STOP后抛出，不继续。保持原最低total red、动态checkpoint、缓存setter失效、未覆盖危险／未知STOP与既有guard。记录schema足以让后续实际data审计逐次对照API／readback／TLS；prepared和fake PASS不能证native setter已经成功。

读取工程真实旧source组合FAIL／新source一项method PASS（完整三fake周期、API异常和readback负例）以及保留的PYTHONPATH import失败；本审查没有复跑fake或旧套件。首DIAG01冻结prefix数据与1271末步PASS支持技术原因调查，不替代新FIX01完整周期／最少red2／动态checkpoint及新terminal审计。

新profile拒绝historical release，未知raw allocation或已分配≥3即拒绝；只active FIX300／BOUNDARY900。R600按总启动预算SKIPPED。R300／R900是固定服务指令，qRamp都900、ALINEA=null，不能当新需求样本或正式控制效果。此核查未创建canonical权限、release或raw，未运行SUMO／prepare／environment。

建议科学精确FIX300预启动门；实际运行后仍独立FCD/TLS/ACK完整72s率链、dynamic red请求日志、终点BEGIN precision8／舍入、WAIT/yellow/EOF／供给及unfinished核账。新UNKNOWN／危险须STOP，不能以兼容修复把E等同N或声称资格。900必须等待修后实际运行三方门后才决定，剩余启动不自动授权。
