class DataOperate():

    def int_2_list(self,int_data,list_len):
        list_out = []
        for i in range (0,list_len):
            list_out.append(int_data%256)
            int_data = int_data >> 8
        return list_out     
      
    def list_2_int(self,list_in):
        data_out = 0
        for i in range(0,len(list_in)):
            data_out = data_out + list_in[i]*pow(2,8*i)
        if(list_in[len(list_in)-1] > 127):
            data_out = data_out - pow(2,len(list_in)*8)
        return data_out    
    
    def cyclic_shift(self,shift_direction,shift_data,data_bits,shift_bits):
        if(shift_bits > data_bits):
            print('Error:    shift bits set error')
            return False
        if(shift_direction == 'L'):
            shift_data = (shift_data >> (data_bits-shift_bits)) | (shift_data << shift_bits)
            shift_data = shift_data % pow(2,data_bits)
            return shift_data
        elif(shift_direction == 'R'):
            shift_data = (shift_data << (data_bits-shift_bits)) | (shift_data >> shift_bits)
            shift_data = shift_data % pow(2,data_bits)
            return shift_data
        else:
            print('Error:    shift direction set error')
            return False
    