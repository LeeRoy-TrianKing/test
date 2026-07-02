# from pyais.encode import encode_dict
#
# # === 在这里填写你想要的字段值 ===
# data = {
#     'type': 1,                # 消息类型 1（A类位置报告）
#     'repeat': 0,              # 重复指示
#     'mmsi': '412345678',      # 9位 MMSI
#     'status': 0,              # 航海状态
#     'rot': 0,                 # 转弯率
#     'sog': 12.5,              # 对地航速（节）
#     'accuracy': 0,            # 位置精度
#     'lon': 121.4737,          # 经度（度）
#     'lat': 31.2304,           # 纬度（度）
#     'cog': 135.5,             # 对地航向（度）
#     'heading': 136,           # 真实航向（度）
#     'second': 30,             # UTC 秒
#     'raim': 0,                # RAIM 标志
# }
#
# # === 生成 AIVDM（他船）===
# nmea_sentences = encode_dict(data, radio_channel="B", talker_id="AI", sentence_type="VDM")
# for s in nmea_sentences:
#     print(s)
#
# # === 生成 AIVDO（本船）===
# nmea_sentences = encode_dict(data, radio_channel="B", talker_id="AI", sentence_type="VDO")
# for s in nmea_sentences:
#     print(s)

from pyais.encode import encode_dict

# === 在这里填写消息类型 5 的字段值 ===
data_type5 = {
    'type': 5,                  # 消息类型 5（A类静态和航次数据）
    'repeat': 0,                # 重复指示
    'mmsi': '412345678',        # 9位 MMSI
    'ais_version': 0,           # AIS版本 (0=ITU-R M.1371-3)
    'imo': 9123456,             # IMO编号 (0=不可用，例如 9123456)
    'callsign': 'ABCD123',      # 呼号 (最多7字符，不足补@或空格)
    'shipname': 'MY TEST VESSEL', # 船名 (最多20字符)
    'shiptype': 70,             # 船舶类型代码 (70=货船, 30=渔船, 50=引航船等)
    'to_bow': 100,              # 参考点到船首距离 (单位：米)
    'to_stern': 50,             # 参考点到船尾距离 (单位：米)
    'to_port': 20,              # 参考点到左舷距离 (单位：米)
    'to_starboard': 10,         # 参考点到右舷距离 (单位：米)
    'epfd': 1,                  # 定位设备类型 (1=GPS)
    'month': 5,                 # ETA 月份 (1-12, 0=不可用)
    'day': 20,                  # ETA 日 (1-31, 0=不可用)
    'hour': 14,                 # ETA 小时 (0-23, 24=不可用)
    'minute': 30,               # ETA 分钟 (0-59, 60=不可用)
    'draught': 8.5,             # 最大吃水 (单位：米，步长0.1，如8.5表示8.5米)
    'destination': 'SHANGHAI',  # 目的地 (最多20字符)
}

# === 生成 AIVDM（他船）===
print("=== Type 5 AIVDM（他船）===")
nmea_sentences_vdm = encode_dict(data_type5, radio_channel="B", talker_id="AI", sentence_type="VDM")
for s in nmea_sentences_vdm:
    print(s)

