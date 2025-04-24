from micropython import const
from typing import TYPE_CHECKING

from storage import device
from trezor import io, wire
from trezor.crypto.hashlib import blake2s
from trezor.messages import LabelAck, LabelRequest, Success

import ujson as json

if TYPE_CHECKING:
    from trezor.messages import LabelUpload

# 常量定义
REQUEST_CHUNK_SIZE = const(16 * 1024)

async def label_upload(ctx: wire.Context, msg: LabelUpload) -> Success:
    print("## label_upload")
    # 获取参数
    data_length = msg.data_length
    passphrase_enabled = msg.passphrase_enabled
    
    # 检查初始数据块
    if msg.initial_chunk and len(msg.initial_chunk) > REQUEST_CHUNK_SIZE:
        raise wire.DataError("Initial chunk too large")
    
    # 准备文件路径
    label_path = "1:/res/label.json"
    
    try:
        # 收集所有数据块到一个字节数组
        all_data = bytearray()
        data_left = data_length
        offset = 0
        
        # 如果有初始数据块，先添加到数据数组
        if msg.initial_chunk:
            all_data.extend(msg.initial_chunk)
            offset += len(msg.initial_chunk)
            data_left -= len(msg.initial_chunk)
        
        # 循环请求剩余的数据块
        while data_left > 0:
            # 计算当前请求的数据块大小
            chunk_size = min(REQUEST_CHUNK_SIZE, data_left)
            
            # 发送请求获取下一个数据块
            request = LabelRequest(data_length=chunk_size, offset=offset)
            ack: LabelAck = await ctx.call(request, LabelAck)
            
            # 验证数据完整性（保留原有的哈希校验）
            if ack.hash is not None:
                digest = blake2s(ack.data_chunk).digest()
                if digest != ack.hash:
                    raise wire.DataError("Data digest is inconsistent")
            
            # 添加数据块到数据数组
            all_data.extend(ack.data_chunk)
            
            # 更新偏移量和剩余数据量
            data_size = len(ack.data_chunk)
            offset += data_size
            data_left -= data_size
            
            # 检查接收到的数据块大小
            if data_size != chunk_size:
                raise wire.DataError("Received data chunk size mismatch")
        
        # 将收集到的数据转换为JSON
        try:
            # 将字节数据解码为UTF-8字符串
            data_str = all_data.decode("utf-8")
            
            # 解析为JSON以验证格式
            json_data = json.loads(data_str)
            
            # 将JSON重新格式化为字符串
            formatted_json = json.dumps(json_data)
            
        except UnicodeError:
            raise wire.DataError("Label data is not valid UTF-8")
        except Exception as e:
            raise wire.DataError(f"Invalid JSON format: {e}")
        
        # 写入格式化后的JSON到文件
        with io.fatfs.open(label_path, "w") as f:
            f.write(formatted_json)
            # 强制刷新到磁盘
            f.sync()
        
        # 返回成功消息
        print("## label_upload success")
        return Success(message="Label uploaded successfully")
    
    except BaseException as e:
        # 处理异常
        raise wire.FirmwareError(f"Failed to write label with error: {e}")
