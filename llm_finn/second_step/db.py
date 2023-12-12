def get_kakao_sink_data(*args):
    print(args)
    path = "data/kakao_sink.txt"
    with open(path, "r") as fin:
        return fin.read()

