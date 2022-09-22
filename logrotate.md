# 使用logrotate完成日志自动切分并轮转

部署网络应用时，会对请求进行日志保存，用于数据统计分析以及故障排除，但对于高并发请求的服务器，日志文件会迅速增长，快速的消耗磁盘空间，同时，分析一个大文件来排查问题也会非常慢。因此，我们通常需要将日志按照天级别进行存储，并对过旧的日志进行压缩转存或删除，方便节省磁盘空间和进行脚本分析。

当我第一次有这种需求的时候，最先想到的是crontab脚本定时执行日志清理脚本。就是先编写一个cleanLog.sh，然后让crontab定期的来执行它。这个方法可行，但是比较麻烦费事，此时一个Linux内置的工具就比较有用了：logrotate。

## logrotate: Linux日志文件总管

logrotate（日志轮转工具）可以自动对日志文件提供截断、压缩以及轮转的功能。

logrotate工具默认安装在linux机器上，全局命令在/usr/sbin/logrotate，另外还包含两个配置文件：

```sh
// 全局配置文件，存储的为公用的默认配置项
/etc/logrotate.conf
// 子项配置文件夹，该文件夹下提供一些系统级别的日志配置，你的自定义配置也需要配置在这里
/etc/logrotate.d/
```

这个工具能做到自动执行的功能，其实还是依赖于crontab工具，只不过这些设定系统自动完成了，我们可以查看crontab系统级别的日运行脚本：

```sh
$ vim /etc/cron.daily/logrotate
#!/bin/sh

/usr/sbin/logrotate /etc/logrotate.conf >/dev/null 2>&1
EXITVALUE=$?
if [ $EXITVALUE != 0 ]; then
    /usr/bin/logger -t logrotate "ALERT exited abnormally with [$EXITVALUE]"
fi
exit 0
```

可以看到在crontab的日级别配置文件目录下有一个logrotate子项，它会每天执行logrotate命令，调用的配置为/etc/logrotate.conf。

在实际执行中，logrotate命令会先读取/etc/logrotate.conf的配置作为默认项，然后再依次读取/etc/logrotate.d/目录下的各文件配置来覆盖默认项，并执行日志轮转功能。

## logrotate命令

```sh
语法：logrotate [OPTION...] <configfile>
参数说明：
-d, --debug ：debug模式，测试配置文件是否有错误。
-f, --force ：强制转储文件。
-m, --mail=command ：压缩日志后，发送日志到指定邮箱。
-s, --state=statefile ：使用指定的状态文件。
-v, --verbose ：显示转储过程。
```

## logrotate使用

假设我们现在有一个日志文件存储在/home/work/log/nginx.access.log，需要对其每日进行切分为新旧两个日志文件，并删除7天前的旧日志。

首先我们创建新的日志轮转配置：

```sh
$vim /etc/logrotate.d/nginxAccessLog
# 指定需要轮转处理的日志文件
/home/work/log/nginx.access.log {
    # 日志文件轮转周期，可用值为: daily/weekly/yearly
    daily
    # 新日志文件的权限
    create 0664 work work
    # 轮转次数，即最多存储7个归档日志，会删除最久的归档日志
    rotate 7
    # 以当前日期作为命名格式
    dateext
    # 轮循结束后，已归档日志使用gzip进行压缩
    compress
    # 与compress共用，最近的一次归档不要压缩
    delaycompress
    # 忽略错误信息
    missingok
    # 日志文件为空，轮循不会继续执行
    notifempty
    # 当日志文件大于指定大小时，才继续执行，单位为bytes（默认）/k/M/G
    size = 100M
    # 将日志文件转储后执行的命令，以endscript结尾，命令需要单独成行
    postrotate
        # 重启nginx日志服务，写入到新的文件中去，否则会依然写入重命名后的文件中
        /bin/kill -USR1 `cat /home/work/run/nginx.pid 2> /dev/null` 2> /dev/null || true
        # 默认logrotate会以root身份运行，如果想要以其他身份执行一个命令，可以这样使用：
        #su - work -c '/home/work/odp/webserver/loadnginx.sh restart'
    endscript
}
```

在使用前，我们先演练一下，也就是debug模式，此时，不用实际轮循，而是模拟并输出，使用强制执行是因为还没到轮循周期：

```sh
$logrotate -d -f /etc/logrotate.d/nginxAccessLog 
reading config file /etc/logrotate.d/nginxAccessLog
reading config info for /home/work/log/nginx.access.log

Handling 1 logs

rotating pattern: /home/work/log/nginx.access.log forced from command line (7 rotations)
empty log files are rotated, old logs are removed
considering log /home/work/log/nginx.access.log
  log needs rotating
rotating log /home/work/log/nginx.access.log, log->rotateCount is 7
dateext suffix '-20190228'
glob pattern '-[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]'
glob finding old rotated logs failed
renaming /home/work/log/nginx.access.log to /home/work/log/nginx.access.log-20190228
creating new /home/work/log/nginx.access.log mode = 0664 uid = 500 gid = 501
running postrotate script
running script with arg /home/work/log/nginx.access.log: "
        /bin/kill -USR1 `cat /home/work/run/nginx.pid 2> /dev/null` 2> /dev/null || true
"
```

可以看到整个执行流程，以及没有什么报错信息，此时我们直接继续执行：

```sh
$logrotate -f /etc/logrotate.d/nginxAccessLog
$ll /home/work/lnmp/log/                      
-rw-r--r-- 1 work work          0 Feb 28 13:40 nginx.access.log
-rw-r--r-- 1 work work    5379846 Feb 28 13:37 nginx.access.log-20190228
```

可以看到我们已经对日志进行了切分，最新的日志文件大小为0。以后系统就会对该日志进行自动的轮转管理。

## 多文件配置

我们可以为一个配置区块指定多个文件，支持通配符，多个文件之间用空格分割：

```sh
/home/work/log/nginx.access.log /home/work/log/nginx.error.log /home/work/log/mysql.*.log {
    ...
}
也可以在一个配置文件中指定多个区块：

/home/work/log/nginx.access.log {
    ...
}
/home/work/log/nginx.error.log {
    ...
}
```

## 参考资料

- Linux日志文件总管——logrotate：https://linux.cn/article-4126...
- logrotate-(8) manual page：https://linuxconfig.org/logro...
- 运维中的日志切割操作梳理：https://www.cnblogs.com/kevin...
- Linux logrotate 命令教程日志分割: https://www.gubo.org/linux-rotate-logs-with-logrotate-utility/