from pydantic_settings import BaseSettings


class Constant(BaseSettings):
    # 返回值
    RESP_200: str = "success"
    RESP_VALIDATION_ERROR: str = "参数校验错误"
    RESP_SERVER_ERROR: str = "服务器错误"
    TOKEN_NOT_MATCH: str = "Token校验失败"
    
    # 服务状态
    CLIENT_VERIFY_ERROR: str = "客户端验证时出现了一个错误"
    CLIENT_VERIFY_FAIL: str = "客户端验证失败"
    TOPIC_TYPE_VERIFY_ERROR: str = "TOPIC类型验证失败：无效的类型"
    TOPIC_SELECT_ERROR: str = "服务器内部错误：TOPIC选择失败"
    
    # 权限
    ROLE_ADMIN_DESCRIPTION: str = "系统管理员，管理所有数据"
    ROLE_USER_DESCRIPTION: str = "系统用户，查看自己用户数据"
    ROLE_GUEST_DESCRIPTION: str = "访客，查看公开数据"
    # 用户
    USER_NOT_ENOUGH_PERMISSION: str = "当前用户权限不足"
    USER_NOT_ACTIVE: str = "当前账户已暂停使用"
    USER_INCORRECT_PASSWORD: str = "用户名或密码错误"
    USER_EXISTS: str = "用户名已存在"
    USER_NOT_EXISTS: str = "用户不存在"
    # file 文件
    FILE_USER_NOT_PERMISSION: str = "该用户无法删除该文件"
    FILE_NOT_EXISTS: str = "文件不存在"
    # task 任务
    TASK_NOT_EXISTS: str = "任务不存在"
    TASK_USER_NOT_PERMISSION: str = "该用户无法删除该任务"
    DELETE_TASK_FILE_FAIL: str = "删除任务文件失败"
    TASK_RUNNING: str = "任务正在运行中"
    INFERENCE_RESULT_NOT_EXISTS: str = "推理结果不存在"
    DELETE_INFERENCE_RESULT_FILE_FAIL: str = "删除推理结果文件失败"


CONSTANT = Constant()
