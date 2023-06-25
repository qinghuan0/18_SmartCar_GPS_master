# 18_SmartCar_GPS_master
18届单车越野GPS上位机

## 功能描述

* 采集原始GPS点位
* 使用贝塞尔曲线拟合
* 过滤掉直道上的点，保留弯道的点
* 速度规划
* 点位调整

## 使用方法
1.首先运行point_write.py文件，将GPS原始点位保存至.txt文件中

2.运行GPS_system.py文件，输入存储GPS原始点位的文件名称

3.首先展示原始点位图

4.关闭即可弹出交互窗口

5.选择开始拟合

6.若出现点位不正，关闭窗口选择调整轨迹，调整控制点位置，后关闭窗口，点击开始拟合重新开始

7.若调整不当可选择轨迹复位重新开始调整，若调整完毕可选择输出代码，该选项将会在当前目录生成.txt文件

## 注意事项

* 在make_curve函数中可调整各个点位区间代表的任务阶段，根据实际情况修改
* 同样在make_curve函数中可以修改不同任务阶段的小车速度

## 通讯协议

    void Float_to_Byte(float f,unsigned char byte[])
    {
        FloatLongType fl;
        fl.fdata=f;
        byte[0]=(unsigned char)fl.ldata;
        byte[1]=(unsigned char)(fl.ldata>>8);
        byte[2]=(unsigned char)(fl.ldata>>16);
        byte[3]=(unsigned char)(fl.ldata>>24);
    }
    void send_gps_data(float lat,float lon)//第一个参数是纬度，第二个是经度
    {
    //发送帧头
    uart_write_string(UART_2, "1");

    //发送纬度
    Float_to_Byte(lat,byte);
    uart_write_buffer(UART_2,byte,4);//UART_2

    uart_write_string(UART_2, "2");

    //发送经度
    Float_to_Byte(lon,byte);
    uart_write_buffer(UART_2,byte,4);//UART_2

    //发送帧尾
    uart_write_string(UART_2, "3");

#### 最后发送“4”代表结束

### 代码示例

    void qudian(void)
    {
        int bezier_point = 0;
    
        flash_read_my(lati_1,lati,pointsum);
        flash_read1_my(longi_1,longi,pointsum);
    
    #if 1 //置1采集完数据之后，按复位将GPS原始数据上传至上位机，接着置0使用处理后的点。
        for(int count=0;count<pointsum;count++)
            {
                GPS_get_latitude[count]=lati[count];   //纬度
                GPS_get_longitude[count]=longi[count];   //经度
                send_gps_data(lati[count],longi[count]);
            }
            uart_write_string(UART_2, "4");
    
    #else
        if(sizeof(la_bezier)/sizeof(la_bezier[0]) < sizeof(lo_bezier)/sizeof(lo_bezier[0])) bezier_point = sizeof(la_bezier)/sizeof(la_bezier[0]);
        else bezier_point = sizeof(lo_bezier)/sizeof(lo_bezier[0]);
        for(int k=0;k<bezier_point;k++)
        {
            GPS_get_latitude[k]=la_bezier[k];
            GPS_get_longitude[k]=lo_bezier[k];
            send_gps_data(GPS_get_latitude[k],GPS_get_longitude[k]);       //发送经纬度到上位机
        }
        uart_write_string(UART_2, "4"); //上位机结束标志
    #endif

        found_already = 1;
    }

