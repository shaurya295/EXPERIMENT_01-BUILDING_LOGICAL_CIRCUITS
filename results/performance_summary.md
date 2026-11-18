# Performance Summary

| Circuit | AND | OR | NOT | XOR/XNOR | NAND | NOR | Total gates | Logic depth |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| F1 – original SOP | 4 | 1 | 4 | – | – | – | **9** | **3** |
| F1 – simplified POS  (A+C)(B+D)(A'+B'+C'+D') | 1 | 2 | – | – | 1 | – | **4** | **2** |
| F2 – original POS | 1 | 3 | 4 | – | – | – | **8** | **3** |
| F2 – NAND-only implementation | – | – | – | – | 9 | – | **9** | **4** |
| F3 – original nested-complement circuit | 1 | 2 | – | – | 1 | 2 | **6** | **3** |
| F3 – NAND/NOR implementation of (A+B+C)(A'+C'+D') | – | – | – | – | 1 | 3 | **4** | **3** |
| F4 – XOR / XNOR implementation | 2 | 1 | 1 | 3 | – | – | **7** | **3** |
| F4 – basic-gate (AND/OR/NOT) implementation  A'B + AB'CD + AB'C'D' | 3 | 1 | 4 | – | – | – | **8** | **3** |
| F5 – five-input SOP (already minimal) | 4 | 1 | 4 | – | – | – | **9** | **3** |
| F6 – six-input mixed logic | 3 | 3 | 1 | 1 | – | 1 | **9** | **3** |
| F7 – NAND-NOR hybrid implementation | – | – | – | – | 4 | 2 | **6** | **3** |
| F7 – simplified  A'BC' + B'C'D'  (NOR-only) | – | – | – | – | – | 5 | **5** | **4** |
| F8 – six-input advanced combinational logic | 4 | 1 | – | 2 | – | 2 | **9** | **3** |

All circuits verified against their Boolean equations for every input combination (0 mismatches).
