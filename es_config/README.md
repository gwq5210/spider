## elasticsearch创建密码

- `elasticsearch.yml`配置中启用配置项`xpack.security.enabled`

```sh
xpack.security.enabled: true
```

- 创建密码

```sh
sudo ./bin/elasticsearch-setup-passwords interactive
```

- 访问elasticsearch

```sh
curl -u user:password 'http://localhost:9200'
curl 'http://user:password@localhost:9200'
```

## elasticsearch启用https

- 修改配置项，添加证书和私钥

```sh
xpack.security.http.ssl.enabled: true
xpack.security.http.ssl.certificate: /path/to/name.cert
xpack.security.http.ssl.key: /path/to/name.key
```

## kibana配置elasticsearch用户密码

- 使用kibana-keystore保存用户密码

```sh
sudo ./bin/kibana-keystore create
sudo ./bin/kibana-keystore add elasticsearch.username # 输入elasticsearch用户名
sudo ./bin/kibana-keystore add elasticsearch.password # 输入elasticsearch密码
```

## kibana启用https

- 修改配置项，添加证书和私钥

```sh
server.ssl.enabled: true
server.ssl.certificate: /path/to/name.cert
server.ssl.key: /path/to/name.key
```

## 调整kibana和elasticsearch的jvm内存占用
