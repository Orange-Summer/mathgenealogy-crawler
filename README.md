# 数学家数字族谱的可视化系统-爬虫(mathgenealogy-crawler)

爬取[数学谱系工程网站](https://mathgenealogy.org/)的数学家信息。

main.py 中第 10 行 advisorId 为 data/advisor.csv 中的默认主键，没有实际意义，只是表示条目数，是连续不中断的。而 data/mathematician.csv 中因为直接用数学家的 id 代替了主键，所以可能不连续，id 也不代表着一共有多少条记录。

main.py 中第 149 行 range 表示爬取的数学家的 id 范围，id 指在数学谱系工程网站中该数学家页面 url 中的 id，例如 `https://mathgenealogy.org/id.php?id=102812`。

最后爬取得到的数据在 data 文件夹中，mathematician.csv 中是数学家的信息，advisor.csv 中是数学家之间的指导关系，其中 pid 为学生 id，aid 为导师 id，一个学生可能有多个导师。

爬取代码中为了防止一次请求失败导致运行中断，使用了 retrying 包，第 37 行中`stop_max_attempt_number`为运行停止前重新尝试的最大次数，`wait_random_min`和`wait_random_max`为两次重试之间等待时长范围，从中随机取一个数以毫秒为单位等待之后再重试。
