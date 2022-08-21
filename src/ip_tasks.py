import ipaddress
import random


def task1():
    ip = str(random.randint(1, 255)) + '.' + str(random.randint(1, 255)) + '.' + str(
        random.randint(1, 255)) + '.' + str(random.randint(1, 255))
    mask = str(random.randint(8, 30))
    int1 = ipaddress.ip_interface(ip + '/' + mask)
    ans = str(int1.network)
    data = ['1', ip, str(int1.netmask), '_', '_', '_', '_', '_', '_', '_', ans.split('/')[0]]
    return data


def task2():
    ip = str(random.randint(1, 255)) + '.' + str(random.randint(1, 255)) + '.' + str(
        random.randint(1, 255)) + '.' + str(random.randint(1, 255))
    mask = str(random.randint(8, 30))
    int1 = ipaddress.ip_interface(ip + '/' + mask)
    tmp = ipaddress.ip_address(str(int1.network).split('/')[0])
    tmp2 = ipaddress.ip_address(ip)
    ans = int(tmp2) - int(tmp)
    data = ['2', ip, str(int1.netmask), '_', '_', '_', '_', '_', '_', '_', str(ans)]
    return data


def task3():
    mask = str(random.randint(8, 30))
    int1 = ipaddress.ip_interface('0.0.0.0' + '/' + mask)
    maska_str = str(int1.netmask)
    maska = [format(int(x), '08b') for x in maska_str.split('.')]
    maska = ''.join(maska)
    index_mask = maska.find('0')
    num = 2 ** (len(maska[index_mask:])) - 2
    return ["3", '_', maska_str, '_', '_', '_', '_', '_', '_', '_', str(num)]


def task4():
    ip = str(random.randint(1, 255)) + '.' + str(random.randint(1, 255)) + '.' + str(
        random.randint(1, 255)) + '.' + str(random.randint(1, 255))
    mask = str(random.randint(4, 30))
    int1 = ipaddress.ip_interface(ip + '/' + mask)

    return ["4", '_', '_', str(int1), '_', '_', '_', '_', '_', '_', str(int1.netmask)]


def task5():
    ip = str(random.randint(150, 255)) + '.' + str(random.randint(50, 255)) + '.' + str(
        0) + '.' + str(0)
    bits_subnet = 0
    bits_hosts = 0
    num_subnet = 0
    num_hosts = 0
    while (bits_subnet + bits_hosts) != 16:
        num_subnet = random.randint(12, 4096)
        num_hosts = random.randint(12, 4096)
        bits_subnet = len(str(bin(num_subnet - 1))[2:])
        bits_hosts = len(str(bin(num_hosts + 1))[2:])
    mask = 16 + bits_subnet
    int1 = ipaddress.ip_interface(ip + '/' + str(mask))
    ans = str(int1.netmask)
    return ["5", '_', '_', '_', ip, num_subnet, num_hosts, '_', '_', '_', ans]


def task6():
    ip1 = ipaddress.ip_address(
        str(random.randint(1, 255)) + '.' + str(random.randint(1, 255)) + '.' + str(random.randint(1, 255)) + '.' + '0')
    net1 = ipaddress.ip_network(str(ip1) + '/' + '24')
    subnet1_size = random.randint(63, 120)
    subnet2_size = random.randint(20, 62)
    subnet3_size = random.randint(5, 19)

    subnet1 = list(net1.subnets())[0]
    subnet1_begin = list(subnet1.hosts())[0]
    subnet1_end = subnet1.broadcast_address - 1

    subs_list = list(list(net1.subnets())[1].subnets(prefixlen_diff=7 - len(str(bin(subnet2_size + 1))[2:])))
    subnet2 = subs_list[0]
    subnet2_begin = list(subnet2.hosts())[0]
    subnet2_end = subnet2.broadcast_address - 1

    subnet3 = list(subs_list[1].subnets(prefixlen_diff=len(str(bin(subnet2_size + 1))[2:]) - len(str(bin(subnet3_size + 1))[2:])))[0]
    subnet3_begin = list(subnet3.hosts())[0]
    subnet3_end = subnet3.broadcast_address - 1

    return ["6", '_', '_', '_', '_', '_', '_', str(net1), [subnet1_size, subnet2_size, subnet3_size], '_', [
            [str(subnet1.network_address), str(subnet1.broadcast_address), str(subnet1_begin), str(subnet1_end), str(subnet1.netmask)],
            [str(subnet2.network_address), str(subnet2.broadcast_address), str(subnet2_begin), str(subnet2_end), str(subnet2.netmask)],
            [str(subnet3.network_address), str(subnet3.broadcast_address), str(subnet3_begin), str(subnet3_end), str(subnet3.netmask)]
            ]]


def task7():
    ip1 = ipaddress.ip_address(
        str(random.randint(1, 255)) + '.' + str(random.randint(1, 255)) + '.' + str(random.randint(1, 250)) + '.' + '0')
    ip2 = ip1 + 256
    ip3 = ip1 + 256 * 2
    ip4 = ip1 + 256 * 3
    bits = len(str(bin(int(ip1) ^ int(ip4)))[2:])
    mask = 32 - bits
    int1 = ipaddress.ip_interface(str(ip1) + '/' + str(mask))
    return ["7", '_', '_', '_', '_', '_', '_', '_', '_', [str(ip1), str(ip2), str(ip3), str(ip4)], str(int1.netmask)]



