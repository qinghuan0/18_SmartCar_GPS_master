# 18_SmartCar_GPS_master
18届单车越野GPS上位机

![image](https://github.com/qinghuan0/18_SmartCar_GPS_master/blob/main/example.jpg?raw=true)

## 功能描述

* 一键规划路径
* 速度规划
* 蓝牙收发

## 使用方法
1. 首先运行text_operation.py文件，将GPS原始点位保存至.txt文件中
#####
2. 运行GPS_master.py文件，输入存储GPS原始点位的文件名称
#####
3. 展示路径规划
#####
4. 关闭即可弹出交互窗口
#####
5. 若出现点位不正，关闭窗口选择调整轨迹，拖动点位调整位置，后关闭窗口，点击开始拟合重新开始
#####
6. 若调整不当可选择轨迹复位重新开始调整，若调整完毕可选择输出代码，该选项将会在当前目录生成.txt文件

## 注意事项

* 速度调整在fusion.py开头宏定义
* 打点时仅需打起点、掉头点、终点、锥桶、坡道起点终点，其中起点、终点、坡道起点终点和掉头点打普通点，其它打特殊点
* 使用输出代码方法需要复制粘贴到对应数组重新烧录程序
* 使用蓝牙传输则不需要重新烧录程序，但需要接收完之后将经纬度数组以及速度规划数组存flash，方便重复使用

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

### 蓝牙解算

    void uart_rx_interrupt_handle(void)  //蓝牙接收
    {
        double lo_rec[500]; //蓝牙接收的数据
        double la_rec[500];
        int speed_rec[500];
        int flg_num = 0; // 串口数据接收标志
        uint8 dat_rec ;
        int rec_num = 0;
        double data_double = 0;
        int data_int = 0;
        float lo_width = 100;
        float la_width = 10;
        int speed_width = 10;
        
        int lo_long = 9;
        int la_long = 8;
        int sdat_long = 2;
        int pass_flg = 0;
    
        dat_rec = uart_read_byte(UART_2);
    
        if (dat_rec == '*')
        {
            flg_num++;
            rec_num = 0;
            data_double = 0;
            data_int = 0;
            lo_width = 100;
             la_width = 10;
             speed_width = 10;
             lo_long = 9;
             la_long = 8;
             sdat_long = 2;
             pass_flg = 1;
        }
        else if (dat_rec == ',')
        {
            if (flg_num == 1)
            {
                lo_rec[rec_num] = data_double;
                data_double = 0;
            }
            else if (flg_num == 2)
            {
                la_rec[rec_num] = data_double;
                data_double = 0;
            }
            else if (flg_num == 3)
            {
                speed_rec[rec_num] = data_int;
                data_int = 0;
            }
            lo_width = 100;
            la_width = 10;
            speed_width = 10;
            lo_long = 9;
            la_long = 8;
            sdat_long = 2;
            rec_num++;
        }
    
        if(dat_rec >= '0' && dat_rec <= '9')pass_flg = 0;
        else pass_flg = 1;
    
        if (flg_num == 1 && pass_flg == 0 && lo_long > 0)
        {
            data_double += ((int)dat_rec-'0') * lo_width;
            lo_width /= 10;
            lo_long--;
        }
        if (flg_num == 2 && pass_flg == 0 && la_long>0)
        {
            data_double += ((int)dat_rec-'0') * la_width;
            la_width /= 10;
            la_long--;
        }
        if (flg_num == 3 && pass_flg == 0 && sdat_long>0)
        {
            data_int += ((int)dat_rec-'0') * speed_width;
            speed_width /= 10;
            sdat_long--;
        }
    }

