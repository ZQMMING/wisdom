with open('engines/zhuanwang_gates.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 删掉函数里的重复import
content = content.replace(
    '''            # 1. 财星无根：地支无本气根
            cai_root = False
            cai_wx = WUXING_OF[day_wx]["财"]
            for b in branches:
                from spec.root_qi import BENQI
                if BENQI.get(b) == cai_wx:
                    cai_root = True
                    break''',
    '''            # 1. 财星无根：地支无本气根
            cai_root = False
            cai_wx = WUXING_OF[day_wx]["财"]
            for b in branches:
                if BENQI.get(b) == cai_wx:
                    cai_root = True
                    break'''
)

with open('engines/zhuanwang_gates.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done")
