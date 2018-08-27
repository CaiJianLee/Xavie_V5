ZYNQ平台的一些调试小工具，灵活运用可以延长生命！^-^

** 更详细的使用方法请自行搜索 **

* i2cdetect
检测ZYNQ板的I2C总线及I2C设备地址
./i2cdetect -l         #查看ZYNQ板总线信息
./i2cdetect -y -r 0    #查看0总线上的I2C设备地址
./i2cdetect -y -r 1    #查看1总线上的I2C设备地址

* i2cdump
导出I2C设备中的所有寄存器值
./i2cdump -f -y 1 0x20        #查看1总线上的地址为0x20的设备的所有寄存器值

* i2cget
读取单个寄存器值
./i2cget -f -y 1 0x20 0x77    #获取1总线上的地址为0x20的设备的0x77寄存器值

* i2cset
设置单个寄存器值
./i2cset -f -y 1 0x20 0x77 0xab  #设置1总线上的地址为0x20的设备的0x77寄存器值为0xab

* spitest
SPI testing utility
./spitest -v        #show tx buffer

*sgbspd
本地调试设备驱动的模拟器应用程序，具体使用方法参考虚拟机上调试设备驱动操作文档
./sgbspd


* i2cdetect.py
检测ZYNQ板的I2C总线及I2C设备地址
python i2cdetect.py -h			#help infomation
python i2cdetect.py <i2c_name>		#search i2c devices
