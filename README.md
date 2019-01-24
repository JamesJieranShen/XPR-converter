# XPR-converter
Simple tool to convert Vivado XPR project file into something else

# Description
This script allows to extract list of files from Vivado project and convert it to some other file format.  
This conversion may not be ideal. For example Vivado has a concept of "FileSets", which isn't present in any other tool I've encountered. Current approach to this problem is to specify manually a fileset to be extracted.
If you don't pass any fileset, `xpr_conv` will automatically pick the default "sources_1".

`xpr_conv` currently supports two tools:  
[HDL Code Checker](https://github.com/suoto/hdlcc)  
[rust_hdl](https://github.com/kraigher/rust_hdl)

I'm open to suggestions and new file formats to support.

# Usage
Just type `./xpr_conv -h` to get help.
