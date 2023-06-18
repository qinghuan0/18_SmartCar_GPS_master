# 18_SmartCar_GPS_master
18届单车越野GPS上位机

## 功能描述

* 采集原始GPS点位
* 使用贝塞尔曲线拟合
* 计算曲线上点的曲率，过滤掉大部分直道上的点，保留弯道的点
* 速度规划

## 注意事项

* 打点时直道不需要太密集，弯道则需要密集一些的点位来或偏移一点距离来增加曲线拟合的曲率

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

