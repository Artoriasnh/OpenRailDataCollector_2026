def read_SOP(file_path):
    f = open(file_path)
    lines = f.readlines()
    f.close()

    sop = {}
    byte = {}
    bit = '0'
    for i in range(0, len(lines)):
        lines[i] = lines[i].replace('\t', '')
        if i % 8 == 0:
            bit = lines[i][0:len(str(i // 8))]
            byte = {}
        byte[lines[i][6]] = lines[i][12:].replace("\n", "").replace(' ','')
        sop[bit] = byte
    return sop

def get_container(file_path):
    f = open(file_path)
    lines = f.readlines()
    f.close()

    state_container = {}
    byte = {}
    bit = '0'
    count = 1
    for i in range(0, len(lines)):
        lines[i] = lines[i].replace("\t", "")
        if i % 8 == 0:
            bit = lines[i][0:len(str(i // 8))]
            byte = {}
        signal = lines[i][12:].replace("\n", "").replace(' ','')
        if signal == '':
            signal = 'null_' + bit + '_' + str(count)
            count = count + 1
        byte[signal] = ''
        state_container[bit] = byte
    return state_container

def get_address_update_state_container(file_path):
    #只包含address 初始状态为0 说明这个address还没有被更新过 当0->1说明被更新过，当所有address的状态被更新为1，则说明，全部的初始化完成。
    f = open(file_path)
    lines = f.readlines()
    f.close()
    address_update_state_container = {}
    byte = {}
    bit = "0"
    for i in range(0, len(lines)):
        lines[i] = lines[i].replace("\t", "")
        if i % 8 == 0:
            bit = lines[i][0:len(str(i // 8))]
            byte = 0
        address_update_state_container[bit] = byte
    return address_update_state_container



if __name__ == '__main__':
    sop = read_SOP("C:/Users/NH/Desktop/TRT1.DY2_2.SOP")
    state_container = get_container("C:/Users/NH/Desktop/TRT1.DY2_2.SOP")
    address_update_state_container = get_address_update_state_container("C:/Users/NH/Desktop/TRT1.DY2_2.SOP")
    print(sop)
    # with open('DY_SOP.py', 'a+') as f:
    #     f.seek(0)
    #     f.write('DY_SOP = ')
    #     print(sop, file=f)
    # print(state_container)
    # with open('DY_state_container.py', 'a+') as f:
    #     f.seek(0)
    #     f.write('DY_state_container = ')
    #     print(state_container, file=f)
    # print(address_update_state_container)
    # with open('DY_address_update_state_container.py', 'a+') as f:
    #     f.seek(0)
    #     f.write('DY_address_update_state_container = ')
    #     print(address_update_state_container, file=f)




