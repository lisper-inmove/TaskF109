from functools import partial

from PyQt5.QtCore import QRunnable, QTimer

from log_config import main_logger as logger


class BatchWorker(QRunnable):
    """批量工作器，一次处理多个任务"""

    def __init__(self, task_func, task_list):
        """
        Args:
            task_func: 任务函数，接受一个参数（任务数据）
            task_list: 任务数据列表
            callback: 完成回调函数，接受结果列表
        """
        super().__init__()
        self.task_func = task_func
        self.task_list = task_list

    def run(self):
        """在线程中执行批量任务"""
        results = []
        for task_data in self.task_list:
            try:
                result = self.task_func(task_data)
                logger.info(f"Task completed: {task_data} -> {result}")
                results.append(result)
            except Exception as e:
                results.append((task_data, False, str(e)))
        logger.info("BatchWorker finished all tasks and triggered callback")
