# users/throttling.py（DRF内置功能，无需额外安装）
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle

# 登录用户限流类（对应settings里的user规则）
class UserApiThrottle(UserRateThrottle):
    scope = 'user'  # 必须和settings里的DEFAULT_THROTTLE_RATES.key一致

# 匿名用户限流类（对应settings里的anon规则）
class AnonApiThrottle(AnonRateThrottle):
    scope = 'anon'  # 必须和settings里的DEFAULT_THROTTLE_RATES.key一致