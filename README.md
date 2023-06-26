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

6.若出现点位不正，关闭窗口选择调整轨迹，拖动点位调整位置，后关闭窗口，点击开始拟合重新开始

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

#### 发送“4”代表开始发送标志点位
#### 最后发送“5”表示结束

### 代码示例

    if(sw3_status==0)
    {
         flash_read_page_to_buffer(0, 9);
         for(int i=0;i<250;i++)
          {
             if(flash_union_buffer[i].int16_type>=0&&flash_union_buffer[i].int16_type<30)
              {
                  velocity[i] = flash_union_buffer[i].int16_type;
                  last_p++;
              }
             else velocity[i]=5;
          }
         flash_read_my(lati_1,lati,pointsum);
         flash_read1_my(longi_1,longi,pointsum);
         for(int count=0;count<pointsum;count++)
         {
              GPS_get_latitude[count]=lati[count];   //纬度
              GPS_get_longitude[count]=longi[count];   //经度
              send_gps_data(lati[count],longi[count]);
          }
         uart_write_string(UART_2, "4");

         Cone_barrel_flash_read_my(Cone_barrel_lati_1,Cone_barrel_lati,Cone_barrelsum);
         Cone_barrel_flash_read1_my(Cone_barrel_longi_1,Cone_barrel_longi,Cone_barrelsum);
         for(int count=0;count<Cone_barrelsum;count++)
         {
             send_gps_data(Cone_barrel_lati[count],Cone_barrel_longi[count]);
         }
         uart_write_string(UART_2, "5");

    }

