from flask import Flask, request, jsonify
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from openai import OpenAI
import os
from dotenv import load_dotenv
from sqlalchemy.exc import SQLAlchemyError
import re

# 加载.env文件中的环境变量
load_dotenv()

app = Flask(__name__)

# 数据库连接配置
DATABASE_URL = os.getenv('DATABASE_URL', 'mysql+pymysql://root:123456@localhost:3306')

# OpenAI API密钥配置
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
OPENAI_API_BASE = os.getenv('OPENAI_API_BASE')

print(OPENAI_API_KEY)
print(OPENAI_API_BASE)
print(DATABASE_URL)

if not OPENAI_API_KEY:
    raise ValueError("请在.env文件中设置OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_API_BASE )



app = Flask(__name__)


def get_database_schema(database_name):
    """
    获取数据库的表结构和字段信息
    """
    # engine = create_engine(f'{DATABASE_URL}/{database_name}?charset=utf8mb4')
    engine = create_engine(f'{DATABASE_URL}/{database_name}')
    
    # 查询数据库中的所有表
    with engine.connect() as connection:
        tables_query = text("""
            SELECT TABLE_NAME, COLUMN_NAME, DATA_TYPE 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = :db_name
        """)
        
        result = connection.execute(tables_query, {'db_name': database_name})
        
        # 组织表结构信息
        schema_info = {}
        for row in result:
            table_name = row[0]
            column_name = row[1]
            column_type = row[2]
            
            if table_name not in schema_info:
                schema_info[table_name] = []
            
            schema_info[table_name].append({
                'column_name': column_name,
                'column_type': column_type
            })
    
    return schema_info

def generate_sql_query(database_name, prompt, schema_info):
    """
    使用 OpenAI 生成 SQL 查询
    """
    system_prompt = f"""你是一个专业的SQL查询助手。数据库 {database_name} 的架构如下：\n"""
    for table, columns in schema_info.items():
        system_prompt += f"表 {table}:\n"
        for column in columns:
            system_prompt += f"- {column['column_name']} ({column['column_type']})\n"
    
       # 构建系统提示词，包含数据库架构信息
    system_prompt += """
    请根据用户的自然语言需求，生成准确的SQL查询语句。
    如果用户请求中包含关键词例如 “包含”、“模糊”、“大概”、“类似” 等，请使用 `LIKE` 运算符进行模糊匹配。
    模糊匹配需要使用 `%` 通配符。例如，要查找 `name` 字段中包含 "手机" 的商品，可以使用 `WHERE name LIKE '%手机%'`。
    """  # 更新了system prompt，明确指出如何进行模糊查询
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ]
        )
        
        # 提取生成的 SQL 查询
        # print(response)
        sql_query = response.choices[0].message.content
         # 去除 markdown 代码块标识符
        sql_query = sql_query.replace("```sql", "").replace("```", "").strip()
        # 使用正则表达式提取 SQL 查询 (保持不变)
        match = re.search(r"```sql\n(.*?)\n```", sql_query, re.DOTALL)
        if match:
            sql_query = match.group(1).strip()
        else:
            sql_query = sql_query.strip()
        return sql_query
    
    except Exception as e:
        return f"生成 SQL 查询时出错: {str(e)}"

def execute_sql_query(database_name, sql_query):
    """
    执行 SQL 查询并返回结果
    """
    engine = create_engine(f'{DATABASE_URL}/{database_name}')
    
    try:
        with engine.connect() as connection:
            result = connection.execute(text(sql_query))
            columns = result.keys()
            results = [dict(zip(columns, row)) for row in result.fetchall()]
            return results
    except SQLAlchemyError as e:
        return f"执行SQL查询时出错: {str(e)}"
    except Exception as e:
        return f"未知错误: {str(e)}"

@app.route('/add_product', methods=['POST'])
def add_product():
    """
    API 接口：增加产品数据
    """
    # 获取请求参数
    data = request.json
    name = data.get('name')
    category = data.get('category')
    price = data.get('price')
    description = data.get('description')
    database_name = data.get('database_name')

    if not database_name or not name or not category or not price or not description:
        return jsonify({
            'error': '缺少必要参数：database_name, name, category, price 或 description'
        }), 400

    try:
        # 创建数据库连接
        # engine = create_engine(f'{DATABASE_URL}/{database_name}?charset=utf8mb4')
        engine = create_engine(f'{DATABASE_URL}/{database_name}')

        # 构建 SQL 插入语句
        insert_statement = text("""
            INSERT INTO product (name, category, price, description)
            VALUES (:name, :category, :price, :description)
        """)
        
        # 确定price是字符串以便于SQLAlchemy传递
        price = f"{price:.2f}"

        with engine.connect() as connection:
            result = connection.execute(insert_statement, {
                'name': name,
                'category': category,
                'price': price,
                'description': description
            })
            # 提交后结果才会入库
            connection.commit()
        # 获取最后插入行的 ID
        inserted_id = result.lastrowid
        print(f"Inserted ID: {inserted_id}")
        return jsonify({
            'message': '产品成功添加',
            'inserted_id': inserted_id
        }), 201

    except SQLAlchemyError as e:
        print(f"SQLAlchemy Error: {str(e)}")
        return jsonify({
            'error': f"添加产品时出错: {str(e)}"
        }), 500
    except Exception as e:
        return jsonify({
            'error': f"未知错误: {str(e)}"
        }), 500
        
@app.route('/query', methods=['POST'])
def database_query():
    """
    API 接口：数据库查询
    """
    # 获取请求参数
    data = request.json
    database_name = data.get('database_name')
    prompt = data.get('prompt')
    
    if not database_name or not prompt:
        return jsonify({
            'error': '缺少必要参数：database_name 或 prompt'
        }), 400
    
    try:
        # 获取数据库架构
        schema_info = get_database_schema(database_name)
        
        # 生成 SQL 查询
        sql_query = generate_sql_query(database_name, prompt, schema_info)
        print(sql_query)
        # 执行 SQL 查询
        query_results = execute_sql_query(database_name, sql_query)
        print(f"query_results = {query_results}")
        return jsonify({
            'sql_query': sql_query,
            'results': query_results
        })
    
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)