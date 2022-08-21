import asyncio
import pickle
import socket


class Client:
    def __init__(self):
        self.socket = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM,
        )
        self.socket.settimeout(5)


class Server:
    def __init__(self, table):
        self.socket = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM,
        )
        self.main_loop = asyncio.new_event_loop()
        self.players = []
        self.table = table
        self.answers = []
        self.functions = [self.key0, self.key1, self.key2]

    async def key0(self, message):
        self.table.add(message)

    async def key1(self, message):
        name = message[0]
        correct = message[1]
        self.table.change(name, correct)

    async def key2(self, message):
        ans = message[0]
        self.answers.append(ans)

    async def send_data(self, data=None, socket=None):
        # Если socket is None, то сервер отправляет всем клиентам в комнате, иначе конкретному клиенту по адресу сокета
        if socket is None:
            for user in self.players:
                await self.main_loop.sock_sendall(user, data)
        else:
            await self.main_loop.sock_sendall(socket, data)

    async def listen_socket(self, player_ip, listened_socket=None):
        if not listened_socket:
            return

        while True:
            try:
                data = await self.main_loop.sock_recv(listened_socket, 2048)
                data_decode = pickle.loads(data)
                await self.functions[data_decode['Key']](data_decode['Message'])

            except ConnectionResetError:
                print('Пользователь вышел')
                return

    async def accept_sockets(self):
        while True:
            try:
                user_socket, address = await self.main_loop.sock_accept(self.socket)
                self.players.append(user_socket)
                self.main_loop.create_task(self.listen_socket(address[0], user_socket))
            except:
                break

    async def main(self):
        await self.main_loop.create_task(self.accept_sockets())

    def start(self):
        self.main_loop.run_until_complete(self.main())
