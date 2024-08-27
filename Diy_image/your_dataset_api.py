# 工具包
#https://azure.microsoft.com/en-us/try/cognitive-services/
from requests import exceptions
import argparse
import requests
import cv2
import os

# 输入参数
ap = argparse.ArgumentParser()
ap.add_argument("-q", "--query", required=True,
	help="search query to search Bing Image API for")
ap.add_argument("-o", "--output", required=True,
	help="path to output directory of images")
args = vars(ap.parse_args())

# 网页里面的那个key
# 最大的数量
# 每一个请求页面的数量
API_KEY = "8c8e68cfba8d47bc92a61805e05ec9b1"
MAX_RESULTS = 250
GROUP_SIZE = 50

# API URL
URL = "https://api.cognitive.microsoft.com/bing/v7.0/images/search"

# 下载过程肯定有各种错误，暂时不用管
EXCEPTIONS = set([IOError, FileNotFoundError,
	exceptions.RequestException, exceptions.HTTPError,
	exceptions.ConnectionError, exceptions.Timeout])

# 要发送的信息
term = args["query"]
headers = {"Ocp-Apim-Subscription-Key" : API_KEY}
params = {"q": term, "offset": 0, "count": GROUP_SIZE}

# 执行查找
print("[INFO] searching Bing API for '{}'".format(term))
search = requests.get(URL, headers=headers, params=params)
search.raise_for_status()

# 把结果抓下来
results = search.json()
estNumResults = min(results["totalEstimatedMatches"], MAX_RESULTS)
print("[INFO] {} total results for '{}'".format(estNumResults,
	term))

# 初始化下载个数
total = 0

# 循环去抓
for offset in range(0, estNumResults, GROUP_SIZE):
	print("[INFO] making request for group {}-{} of {}...".format(
		offset, offset + GROUP_SIZE, estNumResults))
	params["offset"] = offset
	search = requests.get(URL, headers=headers, params=params)
	search.raise_for_status()
	results = search.json()
	print("[INFO] saving images for group {}-{} of {}...".format(
		offset, offset + GROUP_SIZE, estNumResults))

	# loop over the results
	for v in results["value"]:
		# 下载图片
		try:
			print("[INFO] fetching: {}".format(v["contentUrl"]))
			r = requests.get(v["contentUrl"], timeout=30)
			# 存储位置
			ext = v["contentUrl"][v["contentUrl"].rfind("."):]
			p = os.path.sep.join([args["output"], "{}{}".format(
				str(total).zfill(8), ext)])
			# 写下来
			f = open(p, "wb")
			f.write(r.content)
			f.close()

		# 如果报错了，跳过
		except Exception as e:

			if type(e) in EXCEPTIONS:
				print("[INFO] skipping: {}".format(v["contentUrl"]))
				continue

		#如果下载的东西读不了，那就删了
		image = cv2.imread(p)

		if image is None:
			print("[INFO] deleting: {}".format(p))
			os.remove(p)
			continue

		total += 1