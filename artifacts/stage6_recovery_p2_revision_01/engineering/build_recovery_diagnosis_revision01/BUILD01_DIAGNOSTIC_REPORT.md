# BUILD01 timeout 只读诊断

**结论：已找到与 BUILD01 PID/时间匹配的 sandbox 拒绝事件，超时根因仍未证实。推荐一次保持网络输入不变、经工具权限审核的 BUILD02 环境诊断构建。** 本阶段没有启动新的 netconvert；不开展 SUMO/TraCI/GUI。

| 项目 | 证据与结论 | 置信度 |
|---|---|---|
| 原终态 | PID21722，30.032025833秒后SIGTERM，returncode−15，stdout/stderr均0B，无network文件；后来PID不存在 | High |
| 新系统证据 | 21:32:26.899947+0200出现该PID `deny(1) sysctl-read kern.bootargs`；相距started约0.476秒 | High |
| 因果解释 | 日志证明拒绝发生，不能证明该拒绝使进程停滞；没有当时的调用栈/CPU/syscall记录 | Unknown |
| 二进制/依赖 | 原SHA不变，arm64；7个直接非系统动态库存在可读；主程序无xattr记录 | High，限静态事实 |
| 输入 | 五份原输入逐字hash一致；原178项离线/XSD检查回执绑定不变；实际编译语义仍未验证 | High，限离线范围 |
| 下一尝试能否成功 | 尚未知，不能据此保证 | Unknown |

原 `log show` 在sandbox内返回“Cannot run while sandboxed”。随后通过工具提供的 `require_escalated` 权限审核，限定45秒窗口和PID/二进制名称，只读导出系统日志。原始导出、完整查询、窗口、时区、SHA及PID对应关系见 `diagnostic_findings.json`、`readonly_commands.json` 和 `scoped_system_log_unsandboxed.json`。没有关闭系统保护、改系统设置或修改二进制。

下一尝试只改变执行环境、独立输出身份和verbose诊断。所有节点、lane、connection、TLS和源config字节保持不变；通过明确CLI output-file覆盖隔离BUILD02输出。新wrapper差异、19/19假进程测试、卡片和有限预算分别在本目录；当前卡未激活，等待独立审查。用户“排查原因，尝试直到成功”作为持续授权依据，不伪造用户对后来生成的卡SHA逐字批准。

BUILD02在进程仍存活时建议做一次有界启动栈采样，失败也必须保留；若成功则转入compiled只读核验，不再为证明根因重复构建。若仍超时且没有新证据，则停止重复尝试并报告具体阻碍。即使构建成功，也不证明specific_obstacle解决。

详细操作、精确命令和sandbox escalation边界见 `BUILD02_EXECUTION_CONTRACT.md` 与 `BUILD02_request_card.json`。本轮未改原卡、BUILD01资料、原始数据、科学设计或protocol。项目状态/工作日志由父代理更新。
