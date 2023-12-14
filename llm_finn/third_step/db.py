def get_kakao_sync_data(*args):
    print(args)
    path = "data/kakao_sync.txt"
    with open(path, "r") as fin:
        return fin.read()


def get_kakao_channel_data(*args):
    print(args)
    path = "data/kakao_channel.txt"
    with open(path, "r") as fin:
        return fin.read()


def get_kakao_social_data(*args):
    print(args)
    path = "data/kakao_social.txt"
    with open(path, "r") as fin:
        return fin.read()
