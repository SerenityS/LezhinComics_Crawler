# LezhinComics_Crawler

> ### 주의사항
>
> 이 툴을 이용하여 다운로드한 파일을 무단배포 시 **법적 제재**를 받을 수 있으며,
>
> 그에 대한 책임은 이 툴을 사용한 **본인**에게 있습니다.



### 설명

* 로그인 & 만화 고유 ID로 간단하게 전 화를 다운받을 수 있는 툴이다.



### 결과물

* 만화 제목 폴더에 모든 화수의 압축된 만화 파일이 저장됨.



### Requirements

```python
python3

bs4
requests
tqdm
```



### 사용법

![](https://raw.githubusercontent.com/SerenityS/LezhinComics_Crawler/master/example/example.gif)



### 구현 방법

> 레진코믹스 로그인 → 토큰 획득 → 만화 고유 넘버 및 에피소드 고유 넘버 획득 → 이미지 다운로드

##### 

* 로그인

로그인은 타 사이트들에 비해 굉장히 쉬운데, 로그인 제출 링크로 계정 정보를 form에 담아 POST 해주면 간단히 로그인된다.

```https://www.lezhin.com/ko/login/submit```

```
redirect: 
username: id
password: pw
```



각 만화의 메인화면인 ```https://www.lezhin.com/ko/comic/c_id```의 HTML Elements를 보면 무작위 정수로 이루어진 해당 만화의 고유 넘버와 각 에피소드의 고유 넘버, Access Token(로그인 된 경우)을 가지고 있는 Script들이 있다.

또한 성인만화는 로그인 된 경우에만 해당 만화의 메인화면에 접속이 가능하다. 그렇기에 이 툴에선 로그인을 구현하였다.



* Access Token

```html
<script>
    __LZ_CONFIG__ = _.merge(window.__LZ_CONFIG__, {
        apiUrl: 'api.lezhin.com',
	...
    token: 'Access Token',
    ...
</script>
```

* 만화 고유 넘버(c_num)

```html
    <script>
        window.sp('trackUnstructEvent', {
            schema: 'iglu:lz/view_item_list/jsonschema/1-0-0',
            data: {
                item_type: 'comic_episode',
                category: 'episode_list',
                parent_id: '만화 고유 넘버'
            }
        });
    </script>
```

* 에피소드 고유 넘버(e_num)

```json
{"name":"화수","display":{"title":"제목","type":"g","displayName":"화수","artistComment":""},"properties":{"expired":false,"notForSale":false},"coin":0,"point":0,"badge":"u","updatedAt":int,"freedAt":int,"seq":1,"publishedAt":int,"id":에피소드 고유 넘버}
```



이렇게 획득한 세가지 정보를 토대로 레진코믹스 API에 접근할 수 있다.



* 에피소드 정보

```http://cdn.lezhin.com/episodes/(c_id)/(int).json?access_token=(token)```

```json
c_id = sparrow

{"episodeId":"sparrow/1","seq":1,"comicId":"sparrow","name":"1","displayName":"01","title":"1화","artists":"birdstarcoal/yunamul","description":"","cover":"","banner":"","social":"","cut":14,"page":0,"type":"","coin":3,"point":0,"created":1548674840000,"updated":1548674903269,"publishDate":"","free":true,"freeDate":"","up":false,"dDay":0,"artistComment":"","direction":"","published":1549033200000,"freed":1549033200000}
```

이 API를 통해 제목, 필요 코인 및 컷 수를 알아낼 수 있는데, 이때 1화는 14개의 이미지 파일로 만들어져 있음을 인지할 수 있다.



```http://cdn.lezhin.com/episodes/(c_id)?access_token=(token)```

위의 API를 통해서는 해당 만화의 **모든 에피소드**의 정보를 획득할 수 있다.



* 이미지 다운로드

```https://cdn.lezhin.com/v2/comics/(c_num)/episodes/(e_num)/contents/scrolls/(cut).webp?access_token=(token)```

위에서 얻은 정보들을 종합하여 이미지를 다운로드 할 수 있다.

만약 컷 수가 14라면 1~14까지 14개의 webp를 다운로드 해야 하는 것이다.

또한 webp를 jpg로 치환하여 jpg 이미지를 다운로드 할 수 있지만 webp가 jpg보다 평균적으로 30% 정도 가볍다.



##### 다운로드 후 파일 처리

처음에는 모든 컷을 모아 하나의 파일로 제작했지만 heigh가 65000px을 넘는 경우가 허다해 저장이 되지 않았다.

PNG로 저장하면 되긴 하는데 파일 용량이 30MB가 넘고 잘 열리지도 않았다.

그래서 그냥 압축했다...



## Issue



## TODO

