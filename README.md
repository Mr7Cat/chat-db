




## DB

```bash
docker run --name test-mysql -e MYSQL_ROOT_PASSWORD=123456 -p 3306:3306 -d mysql:latest

# 查看mysql状态
sudo lsof -i :3306
COMMAND     PID USER   FD   TYPE             DEVICE SIZE/OFF NODE NAME
com.docke 79903 Will   83u  IPv6 0xe6640184d0208b5b      0t0  TCP *:mysql (LISTEN)



# 连接
mysql -h 127.0.0.1 -P 3306 -u root -p

# 初始化数据
首先，列出所有可用的数据库：
SHOW DATABASES;
2. 如果你还没有创建数据库，可以创建一个新的数据库：
CREATE DATABASE IF NOT EXISTS electronics_store;
选择要使用的数据库：
USE electronics_store;


-- 创建 product 表
CREATE TABLE product (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(255),
    price DECIMAL(10, 2),
    description TEXT
);

-- 插入一些电子产品数据
INSERT INTO product (name, category, price, description) VALUES
('智能手机 A', '手机', 5999.00, '一款功能强大的智能手机'),
('笔记本电脑 B', '电脑', 8999.00, '轻薄便携的笔记本电脑'),
('平板电脑 C', '平板', 3999.00, '高清显示屏平板电脑'),
('智能手表 D', '可穿戴设备', 1999.00, '运动健康智能手表'),
('无线耳机 E', '音频', 999.00, '高保真无线耳机'),
('智能音箱 F', '智能家居', 499.00, '语音控制智能音箱'),
('游戏机 G', '游戏', 2999.00, '高性能游戏机'),
('数码相机 H', '相机', 4999.00, '专业级数码相机'),
('电视机 I', '电视', 6999.00, '4K 超高清电视'),
('显示器 J', '电脑', 1999.00, '高分辨率显示器');


--  更多数据 (可选，您可以根据需要添加更多数据)
INSERT INTO product (name, category, price, description) VALUES
('智能手机 K', '手机', 4599.00, '高性价比智能手机'),
('笔记本电脑 L', '电脑', 7999.00, '商务办公笔记本电脑'),
('平板电脑 M', '平板', 2999.00, '学生学习平板电脑'),
('智能手表 N', '可穿戴设备', 1299.00, '时尚智能手表'),
('无线耳机 O', '音频', 799.00, '降噪无线耳机');


-- 查看插入的数据
SELECT * FROM product;

mysql> SELECT * FROM product;
+----+-------------------+-----------------+---------+-----------------------------------+
| id | name              | category        | price   | description                       |
+----+-------------------+-----------------+---------+-----------------------------------+
|  1 | 智能手机 A        | 手机            | 5999.00 | 一款功能强大的智能手机            |
|  2 | 笔记本电脑 B      | 电脑            | 8999.00 | 轻薄便携的笔记本电脑              |
|  3 | 平板电脑 C        | 平板            | 3999.00 | 高清显示屏平板电脑                |
|  4 | 智能手表 D        | 可穿戴设备      | 1999.00 | 运动健康智能手表                  |
|  5 | 无线耳机 E        | 音频            |  999.00 | 高保真无线耳机                    |
|  6 | 智能音箱 F        | 智能家居        |  499.00 | 语音控制智能音箱                  |
|  7 | 游戏机 G          | 游戏            | 2999.00 | 高性能游戏机                      |
|  8 | 数码相机 H        | 相机            | 4999.00 | 专业级数码相机                    |
|  9 | 电视机 I          | 电视            | 6999.00 | 4K 超高清电视                     |
| 10 | 显示器 J          | 电脑            | 1999.00 | 高分辨率显示器                    |
| 11 | 智能手机 K        | 手机            | 4599.00 | 高性价比智能手机                  |
| 12 | 笔记本电脑 L      | 电脑            | 7999.00 | 商务办公笔记本电脑                |
| 13 | 平板电脑 M        | 平板            | 2999.00 | 学生学习平板电脑                  |
| 14 | 智能手表 N        | 可穿戴设备      | 1299.00 | 时尚智能手表                      |
| 15 | 无线耳机 O        | 音频            |  799.00 | 降噪无线耳机                      |
+----+-------------------+-----------------+---------+-----------------------------------+



```

SELECT column_name, character_set_name 
FROM information_schema.`COLUMNS` 
WHERE table_schema = 'electronics_store' 
AND table_name = 'name';



## Server

export OPENAI_API_KEY='your_openai_api_key'


export OPENAI_API_KEY='https://api.tokenfree.ai'

API 调用示例：
```bash
# 查询
curl -X POST http://localhost:5000/query \
     -H "Content-Type: application/json" \
     -d '{
         "database_name": "electronics_store",
         "prompt": "查询所有苹果产品的信息"
     }'

# 中文unicode显示问题
curl -X POST http://localhost:5000/query \
     -H "Content-Type: application/json" \
     -d '{
         "database_name": "electronics_store",
         "prompt": "查询所有电脑的信息"
     }' > response.json

python -c "import json; f = open('response.json', 'r'); data = json.load(f); print(json.dumps(data, ensure_ascii=False, indent=2)); f.close()"


# 添加
curl -X POST http://localhost:5000/add_product \
     -H "Content-Type: application/json" \
     -d '{
         "database_name": "electronics_store",
         "name": "智能手机 Y",
         "category": "手机",
         "price": 4999.00,
         "description": "一款功能强大的智能手机 Y"
     }'

# 删除
curl -X DELETE http://localhost:5000/delete_product \
-H "Content-Type: application/json" \
-d '{
    "database_name": "electronics_store",
    "id": 26
}'
```