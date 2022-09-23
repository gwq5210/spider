## 配置

```sh
filebrowser -d /etc/filebrowser/filebrowser.db config init
filebrowser -d /etc/filebrowser/filebrowser.db config set --address 0.0.0.0
filebrowser -d /etc/filebrowser/filebrowser.db config set --port 9090
filebrowser -d /etc/filebrowser/filebrowser.db config set --cert /etc/ssl/gwq5210.com/gwq5210.com_bundle.crt
filebrowser -d /etc/filebrowser/filebrowser.db config set --key /etc/ssl/gwq5210.com/gwq5210.com.key
filebrowser -d /etc/filebrowser/filebrowser.db config set --log /var/log/filebrowser/filebrowser.log
filebrowser -d /etc/filebrowser/filebrowser.db config set --root /var/www/gwq5210.com/files
filebrowser -d /etc/filebrowser/filebrowser.db config set --locale zh-cn
# filebrowser -d /etc/filebrowser/filebrowser.db users add root password --perm.admin
```

其中的root和password分别是用户名和密码，根据自己的需求更改。

有关更多配置的选项，可以参考官方文档：https://docs.filebrowser.xyz/

配置修改好以后，就可以启动 File Browser 了，使用-d参数指定配置数据库路径。示例：

```sh
filebrowser -c /etc/filebrowser/filebrowser.json
```

启动成功就可以使用浏览器访问 File Browser 了
