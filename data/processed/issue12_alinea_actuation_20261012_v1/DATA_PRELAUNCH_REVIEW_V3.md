# Issue12 data-reader Minor修复 V3

仅修复科学预审指出的V2入口消费漏洞：V2末尾只核ID，已计入ID的额外窗口外记录可能漏检。V3按每条记录索引消费且要求整数BEGIN／END=BEGIN+1；重复、未绑定时间、窗口外／空观测附入口、同ID额外记录均UNKNOWN。原C/E/N和arrival BEGIN／precision8规则不变，runtime／卡片／guard未改。

实际命令：`python3 data/processed/issue12_alinea_actuation_20261012_v1/test_data_V3.py`；3个methods PASS，0.001s。其中新增1项组合fixture覆盖同ID窗口外、无time、重复和错误END；不扩大工程或仿真测试矩阵。V1/V2源码、日志、receipt及V2绑定9文件哈希不变，先前局限仍可追踪。

结论：PASS限离线reader修复，不代表native结果。首R300尚待冻结实际raw、独立FCD/TLS/ACK重建入口、72s率链、末步arrived／before-only／tripinfo、WAIT/yellow/logEOF以及供给与队列核对；任何缺测UNKNOWN保留前缀并阻后续。无SUMO、prepare、release或权限变更。V2审查其余边界保持，V3作为后续数据reader。
