# BUILD02 编译网络工程核验

**结果：PASS_STATIC_COMPILED_ONLY。155项通过、0项失败、4类运行期事项尚不可评价。未释放SUMO。** 置信度High，限静态XML、文件绑定和进程/字节核账。

## 进程与完整账目

BUILD02的PID24060及其进程组均已不存在；限定该目录的lsof检查没有报告打开句柄。原wrapper记录returncode0、4.657082667秒。最终六个文件共 **21,096字节**，等于wrapper记录的17,609字节加其自身3,487字节receipt；每个已有输出哈希与wrapper一致，审计前后无变化。

父代理首次检查时PID已经不存在，因此没有启动sample；没有sample文件或部分文件，也没有sample写进程需要等待。**首次检查相对于t+2的准确时点未记录，不能声称恰在2秒跳过。** 这是诊断时点偏差，须供独立review评估。不得补采样、虚构栈或将本次成功严格归因于特定sysctl拒绝。

network.net.xml：12,244字节，SHA-256 `e47b0f94521414e55d0e5337b87204dc38d98a0a3a7c5466f2a5883f80b52710`。XML根net，本地net_file.xsd离线验证通过。stderr为空，stdout完整保留并记录Success。旧BUILD01资料和五个网络源输入全部保持哈希一致。

## 核心编译门

| 项目 | 实际编译结果 | 结论 |
|---|---|---|
| 辅助车道可用长度 | 294.51m，设计范围280–300m | PASS |
| 下游主线长度 | 两lane均496m，严格大于400m；尾段96m | PASS |
| 三个合流入口 | M0→section1、M1→section2、R0→section0；三个request foes/response均000 | PASS |
| 辅助lane0终点 | 无outgoing；R必须实际安全左换道后继续 | PASS静态设计；实际换道未知 |
| M连续通道 | section1→down0、section2→down1；两条through lane几何对齐 | PASS |
| 右侧许可 | section1 changeRight=authority，passenger不能从该lane右入aux0 | PASS静态权限 |
| R/M几何 | R入口及via在M中心线右侧/下方，三入口不相交 | PASS |
| 城市共享、分流、cross与TLS | shape/length/speed、连接、junction/request和45Gr/3yr/9rG/3ry相同 | PASS |
| ramp_storage/ramp_mid | 储存lane204.49m、mid内部lane81.98m；既有几何不变 | PASS |
| E1/E2与域 | 五套模板各9E1+2E2；所有位置可容纳，不需裁剪；storage endPos可解析为204.49 | PASS静态适配；尚未实体化/实际加载 |

城市lane的width由旧文件省略变为显式3.20。审计按本机sumolib解析器的缺省3.2规范化后比较；没有宣称新旧XML字节相同。原几何shape、长度等保持一致。

额外记录：netconvert自动给merge_section_0输出`acceleration="1"`，原plain XML未手工设置；该编译属性保留，运行期含义尚未测试。生成注释的时区后缀与wrapper UTC epoch背景不一致；运行时点采用wrapper记录，不用XML注释推断精确时间。

## 路径、观察域与局限

M主指标域含上游1200m至lane尾198.38m、入口内部3.11m、section294.51m、末端内部8m、下游200m，合计 **704m**。两M通道一致；M全走廊纵向lane长度合计2200m。

从shared出口到辅助lane终点的R专用路径分量为113.08+204.49+81.98+99.07+3.11+294.51= **796.24m**；shared本身238.8m。它们是纵向几何之和，不能直接转换为车辆储存容量或实际换道轨迹长度。新旧指标不能因名称类似就视为等价。

四类NOT_EVALUABLE为实际E1/E2加载与17-role输出、M真实p100/aux0使用、R真实安全换道/通过、以及specific_obstacle/两侧交通表现。它们需要之后独立获批的SUMO技术smoke/验证。本轮只读取网络和模板，未实体化运行包、修改compiled XML或运行任何交通工具。

原revision01审计保留；revision02只纠正R_route的说明字段匹配名称，全部155项通过结果不变。最终closeout、逐项检查、lane/connection映射和域分量均在本目录。等待独立数据/科学复核。
