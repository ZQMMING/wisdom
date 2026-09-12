"""Verify Sydney timezone test case for R-04 independent verification"""
from datetime import datetime
from zoneinfo import ZoneInfo

sydney = ZoneInfo('Australia/Sydney')
bjt = ZoneInfo('Asia/Shanghai')

# To be post-lichun in Sydney (19:26:53+11 = 16:26:53 BJT)
post_lichun_sydney = datetime(2024, 2, 4, 19, 27, 0, tzinfo=sydney)
print(f"Sydney post-lichun: {post_lichun_sydney}")
print(f"BJT equivalent: {post_lichun_sydney.astimezone(bjt)}")

# To be pre-lichun in Sydney (19:26:52+11 = 16:26:52 BJT)
pre_lichun_sydney = datetime(2024, 2, 4, 19, 26, 52, tzinfo=sydney)
print(f"Sydney pre-lichun: {pre_lichun_sydney}")
print(f"BJT equivalent: {pre_lichun_sydney.astimezone(bjt)}")
