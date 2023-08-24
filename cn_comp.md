# VCDMate

Fast and Effective VCD file compressor and decompressor (Academic Version V1.0)

#### Author:

Yuyang Xie (xyy18@mails.tsinghua.edu.cn)
Numbda, CST Department, Tsinghua University.  

Lingjie Li (li-lj18@mails.tsinghua.edu.cn)
Numbda, CST Department, Tsinghua University.  

2021

#### Supervisor:

Wenjian Yu (yu-wj@tsinghua.edu.cn)
Numbda, CST Department, Tsinghua University.  

#### Executable: 

"VCDMate" has been compiled by g++ version 9.4.0 under Ubuntu Linux Workstation release 16.04.12.

#### compress and decompress program:

Compress and decompress directly compress VCD files and decompress compressed files.

`./bin/compress <vcd file> <compressed file> [-lib <secondary compression method>] [-m <compression strategy>]  `

`./bin/decompress <compressed file> <decompressed file> [-lib <secondary compression method>] [-m <compression strategy>]  `

The syntax:

-lib: represents the selection parameter of the secondary compression method, -lib 2 represents the selected Bzip2 for secondary compression, -lib 1 represents the selection of Gzip for compression, the Gzip compression rate is lower, but the speed is faster, -lib 0 represents Write files directly with fwrite, with the lowest compression rate.

-m: represents the selection parameter of the compression strategy, -m 0 indicates that the first compression strategy is selected, and -m 1 indicates that the second compression strategy is selected. The experimental test -m 0 and -m 1 have little difference in the compression ratio and operating efficiency of the test example, so usually choose -m 0.

Example:

`./bin/compress ../data/test.vcd ../data/test.comp -lib 2 -m 0`

`./bin/decompress ../data/test.comp ../data/test.decomp -lib 2 -m 0`

#### Reference: 

[1]谢雨洋, 李凌劼, 喻文健. 面向集成电路逻辑仿真的高效数字波形压缩方法[J]. 计算机辅助设计与图形学学报, 2021(011):033.
