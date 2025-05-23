gcc -fPIC -shared -o mrm.so mrmMainFunctions.c mrmFunctions.c -l ws2_32  //// windows
cc -fPIC -shared -o mrm.so mrmMainFunctions.c mrmFunctions.c //// linux

Compile and generate the mrm.so for radar controls. the file must be put in project/radar/mrm.so
Must recompile for any changes on the c code ofc.
