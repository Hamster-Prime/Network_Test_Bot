import asyncio
import time
import logging

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def check_authorization(user_id: int, authorized_users: list) -> bool:
    return user_id in authorized_users

def check_is_admin(user_id: int, admin_users: list) -> bool:
    return user_id in admin_users

async def schedule_delete_message(context, chat_id: int, message_id: int, delay: int = 10):
    await asyncio.sleep(delay)
    try:
        await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
    except Exception as e:
        logging.error(f"删除消息 {message_id} 失败: {e}")

async def progress_spinner(context, chat_id: int, message_id: int, base_text: str, done_event: asyncio.Event):
    spinner_states = [".", "..", "...", "...."]
    i = 0
    while not done_event.is_set():
        spinner = spinner_states[i % len(spinner_states)]
        try:
            await context.bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=f"{base_text}{spinner}",
                parse_mode="HTML"
            )
        except Exception as e:
            logging.error(f"更新进度消息失败: {e}")
        await asyncio.sleep(1)
        i += 1

def retry_operation(func, *args, retries=3, delay=2, **kwargs):
    """
    执行一个操作，如果失败则进行重试
    
    参数:
        func: 要执行的函数
        *args: 函数的位置参数
        retries: 重试次数，默认为3
        delay: 重试之间的延迟（秒），默认为2
        **kwargs: 函数的关键字参数
        
    返回:
        函数的执行结果或异常信息
    """
    last_exception = None
    
    for attempt in range(retries):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            last_exception = e
            logging.warning(f"操作失败 (尝试 {attempt+1}/{retries}): {str(e)}")
            if attempt < retries - 1:  # 如果不是最后一次尝试
                time.sleep(delay)
                # 每次重试增加延迟时间
                delay *= 1.5
    
    return f"操作失败，已重试{retries}次: {str(last_exception)}"
