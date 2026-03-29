# throttling.py
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle

# 针对登录用户的限流：每天最多100次请求
class UserApiThrottle(UserRateThrottle):
    rate = '100/day'  # 可改：比如 '5/minute'（每分钟5次）、'200/hour'（每小时200次）

# 针对匿名用户的限流：每天最多50次请求
class AnonApiThrottle(AnonRateThrottle):
    rate = '50/day'