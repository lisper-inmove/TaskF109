# UDP 服务器支持设计文档

**日期：** 2026-02-28
**状态：** 已批准
**作者：** Claude Code

## 概述

为仿真服务器添加 UDP 协议支持，使其能够处理来自客户端的 UDP 数据包。客户端已经实现了 UDP 传输层（UDPTransport），现在需要在服务器端添加相应的支持。

## 背景

当前系统架构：
- **客户端：** 已实现 TCP 和 UDP 传输策略（TransportStrategy 模式）
- **服务器端：** 仅支持 TCP 协议（TCPServer）
- **协议：** 使用 ByteStreamProtocol（长度头 + 数据）

## 设计目标

1. 为仿真服务器添加 UDP 支持
2. 保持与现有 TCP 服务器架构的一致性
3. 复用现有的协议处理逻辑
4. 支持同时运行 TCP 和 UDP 服务器

## 方案选择

### 评估的方案

**方案 A：独立 UDPServer 类（已选择）**
- 创建独立的 UDPServer 类，与 TCPServer 平行
- 使用单个 UDP socket 接收所有客户端的数据包
- 优点：架构清晰、实现简单、易于维护

**方案 B：统一 Server 抽象**
- 创建 ServerStrategy 抽象基类
- 缺点：需要重构现有代码，增加复杂度

**方案 C：混合模式服务器**
- 使用 select/epoll 统一处理
- 缺点：实现复杂，过度设计

### 最终选择：方案 A

理由：与现有架构一致，实现简单，满足需求，易于测试和维护。

## 架构设计

### 文件结构

```
simu/
├── server.py          # 现有的 TCPServer
├── udp_server.py      # 新增：UDPServer 类
├── main.py            # 修改：支持 --protocol 参数
├── protocol.py        # 复用：消息打包/解包
├── config.py          # 现有配置
└── client_handler.py  # TCP 客户端处理器（UDP 不需要）
```

### 核心组件

#### 1. UDPServer 类

**接口设计：**
```python
class UDPServer:
    def __init__(self, host: str, port: int, config: Config)
    def start(self) -> None
    def stop(self) -> None
    def set_message_callback(self, callback: Callable) -> None
    def get_server_stats(self) -> Dict
```

**实现要点：**
- 创建 UDP socket (SOCK_DGRAM)
- 在独立线程中运行主循环
- 使用 recvfrom() 接收数据包（获取发送方地址）
- 使用 sendto() 发送响应到发送方
- 单线程处理所有客户端（UDP 无连接特性）

**与 TCPServer 的差异：**
- 无需 accept() 和 listen()
- 无需 ClientHandler（每个数据包独立处理）
- 使用 recvfrom()/sendto() 而非 recv()/send()

#### 2. MultiPortServerManager 集成

**修改内容：**
- servers 字典存储 (protocol, server) 元组
- 支持同一端口同时运行 TCP 和 UDP
- 统计信息区分协议类型

#### 3. main.py 命令行参数

**新增参数：**
```bash
--protocol {tcp,udp,both}  # 协议类型选择
```

**使用示例：**
```bash
# 仅 TCP
python main.py --ports 9999 --protocol tcp

# 仅 UDP
python main.py --ports 9999 --protocol udp

# 同时运行
python main.py --ports 9999 --protocol both
```

## 数据流设计

### UDP 通信流程

1. **客户端发送：**
   ```
   客户端数据 → ByteStreamProtocol.pack() → UDP socket.sendto()
   ```

2. **服务器处理：**
   ```
   recvfrom() → 获取数据包和发送方地址
        ↓
   ByteStreamProtocol.unpack() → 解析数据
        ↓
   message_callback() → 生成响应
        ↓
   ByteStreamProtocol.pack() → 打包响应
        ↓
   sendto(发送方地址) → 发送响应
   ```

3. **客户端接收：**
   ```
   UDP socket.recvfrom() → ByteStreamProtocol.unpack() → 处理响应
   ```

### 协议兼容性

- 复用现有的 ByteStreamProtocol（长度头 + 数据）
- TCP 和 UDP 使用相同的消息格式
- 客户端和服务器端协议保持一致

## 错误处理

### Socket 错误

1. **绑定失败：**
   - 端口被占用或权限不足
   - 处理：记录错误并抛出异常

2. **接收超时：**
   - 使用 settimeout() 避免阻塞
   - 处理：继续循环，不中断服务

3. **发送失败：**
   - 目标不可达
   - 处理：记录警告，继续处理下一个包

### 协议解析错误

1. **数据包格式错误：**
   - 处理：记录警告，丢弃该包

2. **解包失败：**
   - 处理：发送错误响应（如果可能）

### 回调函数异常

- 捕获所有异常，记录错误
- 返回默认错误响应
- 避免服务器崩溃

## 测试策略

### 集成测试（推荐）

1. 启动 UDP 服务器
2. 使用客户端 UDPTransport 发送测试数据包
3. 验证服务器正确接收和响应
4. 测试多客户端并发

### 验证要点

- UDP 服务器正常启动和停止
- 接收和响应数据包
- 心跳机制正常工作
- 统计信息准确
- 错误处理正确

### 手动测试

```bash
# 启动 UDP 服务器
python main.py --ports 9999 --protocol udp

# 使用客户端连接（在 GUI 中选择 UDP）
python client/main.py
```

## 实现清单

### 新增文件

- [ ] `simu/udp_server.py` - UDPServer 类实现

### 修改文件

- [ ] `simu/main.py` - 添加 --protocol 参数支持
- [ ] `simu/main.py` - MultiPortServerManager 支持 UDP

### 测试

- [ ] 单元测试（可选）
- [ ] 集成测试
- [ ] 手动测试验证

## 性能考虑

- UDP 单线程处理，适合高频小数据包
- 如需处理大量并发，可后续优化为线程池
- 当前设计优先考虑简单性和可维护性

## 后续优化建议

1. 添加 UDP 客户端会话跟踪（基于 IP:Port）
2. 实现 UDP 可靠性机制（ACK 确认）
3. 性能优化：线程池或异步 I/O
4. 添加更详细的统计信息（每客户端统计）

## 总结

本设计采用独立 UDPServer 类的方案，与现有 TCPServer 架构保持一致。通过复用 ByteStreamProtocol 和统一的消息处理接口，实现了简洁高效的 UDP 支持。设计考虑了错误处理、性能和可维护性，满足当前需求并为未来扩展留有空间。
