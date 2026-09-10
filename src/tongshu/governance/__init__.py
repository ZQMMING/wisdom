"""governance — 治理基础设施包（G0-1 Evidence Index / G0-2 Resolved Provenance）。

与 classic_evidence/（各经证据代理）、corpus/（检索层）并列的治理层模块。
归属：跨引擎基础设施，不属于任何单一 engine 的修改面（单 commit 纪律内新增）。

红线（BZ-FNDR-15.11/15.12 锁定）：
  - 本包只产出身份/可见性/provenance 解析，不改 G1、不动 evidence 资源文件、
    不产生任何 SHIJIAN event method。
"""
