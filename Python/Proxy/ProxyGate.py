import requests
import subprocess

# cmd = "kill -9 $(lsof -ti:9050)"
# returned_value = subprocess.call(cmd, shell=True)  # returns the exit code in unix
# print('lsof value:', returned_value)

# cmd = "tor"
# p1 = subprocess.Popen(cmd, shell=True)  # returns the exit code in unix
# print('tor value:', p1)

url1 = "http://icanhazip.com/"
# url2 = "http://naver.com"
url2 = "https://search.shopping.naver.com/product/84500857369"

proxies = {
    "http": "socks5://127.0.0.1:9050",
    "https": "socks5://127.0.0.1:9050",
}

res = requests.get(url1, proxies=proxies)
print(res.text)
res = requests.get(url2, proxies=proxies)
print(res.text)

# p1.terminate()
