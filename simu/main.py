import argparse
import signal
import sys
import threading
import time
from typing import Any, Dict, List

from config import Config
from server import TCPServer
from udp_server import UDPServer
from utils.logger import setup_logger


class MultiPortServerManager:
    """多端口服务器管理器"""

    def __init__(self, config: Config = None):
        self.config = config or Config()
        self.servers: Dict[int, TCPServer] = {}
        self.running = False
        self.logger = setup_logger("server_manager")

    def start_servers(self, ports: List[int], host: str = "0.0.0.0"):
        """启动多个端口的服务器"""
        if self.running:
            self.logger.warning("服务器管理器已在运行中")
            return

        self.running = True

        for port in ports:
            try:
                server = TCPServer(host=host, port=port, config=self.config)
                server.start()
                self.servers[port] = server
                self.logger.info(f"已启动服务器: {host}:{port}")
            except Exception as e:
                self.logger.error(f"启动服务器 {host}:{port} 失败: {e}")

        self.logger.info(f"已启动 {len(self.servers)} 个服务器实例")

    def stop_servers(self):
        """停止所有服务器"""
        for port, server in self.servers.items():
            try:
                server.stop()
                self.logger.info(f"已停止服务器: {server.host}:{port}")
            except Exception as e:
                self.logger.error(f"停止服务器 {port} 失败: {e}")

        self.servers.clear()
        self.running = False
        self.logger.info("所有服务器已停止")

    def get_stats(self) -> Dict:
        """获取所有服务器的统计信息"""
        stats = {
            "total_servers": len(self.servers),
            "running": self.running,
            "servers": {}
        }

        for port, server in self.servers.items():
            stats["servers"][port] = server.get_server_stats()

        return stats


def custom_message_handler(message: Any, client_address: tuple) -> Dict:
    """
    自定义消息处理器示例

    Args:
        message: 接收到的消息
        client_address: 客户端地址

    Returns:
        Dict: 响应数据
    """
    # 这里可以实现自定义的业务逻辑
    import time

    response = {
        "status": "success",
        "timestamp": time.time(),
        "server_response": f"收到来自 {client_address} 的消息",
        "original_message": message,
        "processed": True,
        "echo_count": len(str(message)) if isinstance(message, str) else 1
    }

    return response


def print_stats(manager: MultiPortServerManager, interval: int = 10):
    """定期打印统计信息"""
    while manager.running:
        try:
            stats = manager.get_stats()

            print("\n" + "=" * 60)
            print(f"服务器统计信息 ({time.strftime('%Y-%m-%d %H:%M:%S')})")
            print("=" * 60)

            print(f"运行中的服务器: {stats['total_servers']}")

            for port, server_stats in stats["servers"].items():
                print(f"\n端口 {port}:")
                print(f"  运行时间: {server_stats['uptime']:.1f} 秒")
                print(f"  总连接数: {server_stats['total_connections']}")
                print(f"  当前连接: {server_stats['current_connections']}")
                print(f"  最大并发: {server_stats['max_concurrent_connections']}")

            print("=" * 60 + "\n")

            time.sleep(interval)

        except Exception as e:
            print(f"获取统计信息失败: {e}")
            time.sleep(interval)


def signal_handler(signum, frame):
    """信号处理函数"""
    print("\n收到停止信号，正在关闭服务器...")
    sys.exit(0)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="TCP/UDP 服务器仿真工具")
    parser.add_argument("-p",
                        "--ports",
                        nargs="+",
                        type=int,
                        default=[9999],
                        help="监听的端口列表 (默认: 9999)")
    parser.add_argument("--host", default="0.0.0.0", help="监听地址 (默认: 0.0.0.0)")
    parser.add_argument("--protocol",
                        choices=["tcp", "udp", "both"],
                        default="tcp",
                        help="协议类型 (默认: tcp)")
    parser.add_argument("--config", help="配置文件路径")
    parser.add_argument("--stats-interval",
                        type=int,
                        default=10,
                        help="统计信息打印间隔 (秒，默认: 10)")
    parser.add_argument("--custom-handler",
                        action="store_true",
                        help="使用自定义消息处理器")

    args = parser.parse_args()

    # 设置信号处理
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # 加载配置
    config = Config(args.config)

    # 创建服务器管理器
    manager = MultiPortServerManager(config)

    # 启动服务器
    print(f"启动TCP服务器...")
    print(f"监听地址: {args.host}")
    print(f"监听端口: {args.ports}")
    print(f"配置文件: {args.config or '使用默认配置'}")
    print(f"统计间隔: {args.stats_interval}秒")
    print(f"自定义处理器: {'是' if args.custom_handler else '否'}")
    print("-" * 50)

    try:
        # 启动服务器
        manager.start_servers(args.ports, args.host)

        # 设置自定义消息处理器
        if args.custom_handler:
            for server in manager.servers.values():
                server.set_message_callback(custom_message_handler)
            print("✓ 已启用自定义消息处理器")

        # 启动统计信息线程
        if args.stats_interval > 0:
            stats_thread = threading.Thread(target=print_stats,
                                            args=(manager,
                                                  args.stats_interval),
                                            daemon=True)
            stats_thread.start()

        # 保持主线程运行
        print("\n服务器正在运行，按 Ctrl+C 停止...")

        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n正在停止服务器...")
    except Exception as e:
        print(f"运行错误: {e}")
    finally:
        manager.stop_servers()


if __name__ == "__main__":
    main()
