import pandas as pd
import numpy as np
import re

df=pd.read_csv('招聘信息.csv', encoding='utf-8-sig')
def parse_news(news):
    if pd.isnull(news) or not isinstance(news, str):
        return None, None, None
    news = news.strip()
    if "面议" in news or "元/天" in news:
        return None, None, None
    match = re.search(r"([\d.]+)\s*-\s*([\d.]+)", news)
    if match:
        low, high = float(match.group(1)), float(match.group(2))
        if '万' in news:
            low, high = low * 10000, high * 10000
        is_author = '·' in news and '薪' in news
        if is_author:
            months = re.search(r"·(\d+)薪", news)
            if months:
                m = int(months.group(1))
                low, high = low / m * 12, high / m * 12
        return low, high, is_author
    match = re.search(r"([\d.]+)", news)
    if match:
        val = float(match.group(1))
        is_author = '·' in news and '薪' in news
        if '万' in news:
            val *= 10000
        if is_author:
            months = re.search(r"·(\d+)薪", news)
            if months:
                m = int(months.group(1))
                val = val / m * 12
        return val, val, is_author
    return None, None, None
df[['最低薪资','最高薪资','is_author']]=df["job_news"].apply(
    lambda x: pd.Series(parse_news(x))
)
df['平均薪资']=(df["最低薪资"]+df["最高薪资"])/2
def parse_experience(exp):
    if pd.isna(exp) or not isinstance(exp,str):
        return None,None,None
    exp=exp.strip()
    if '不限' in exp:
        return 0,None
    if "以下" in exp:
        match=re.search(r"([\d.]+)",exp)
        if match:
            val=int(match.group(1))
            return val,val
    march=re.search(r"([\d.]+)\s*-\s*([\d.]+)",exp)
    if march:
        return int(march.group(1)),int(march.group(2))
    match = re.search(r"([\d.]+)", exp)
    if match:
        val = int(match.group(1))
        return val, val
    return None,None
df[["最低经验","最高经验"]]=df["job_ex"].apply(
    lambda x: pd.Series(parse_experience(x))
)
def job_compay_size(size):
    if pd.isna(size) or not isinstance(size,str):
        return None
    size=size.strip()
    march=re.search(r"([\d.]+)\s*-\s*([\d.]+)",size)
    if march:
        return (int(march.group(1))+int(march.group(2)))/2
    match =re.search(r"([\d.]+)",size)
    if match:
        if '以下' in size:
            return int(match.group(1))/2
        elif '以上' in size:
            return int(match.group(1))*1.5
        return int(match.group(1))
    return None
df["公司规模"]=df["c_num"].apply(job_compay_size)
edu_list={
    '不限':0,'大专':1,'本科':2,'硕士':3,'博士':4,'学历不限':5
}
df["学历要求"]=df['job_edu'].map(edu_list)
def spile_city(city):
    if pd.isna(city) or not isinstance(city,str):
        return None,None,None
    part=city.split('·')
    if len(part)==3:
        return part[0],part[1],part[2]
    elif len(part)==2:
        return part[0],part[1],None
    else:
        return part[0],None,None
df[["城市","区","街道"]]=df["job_city"].apply(
    lambda x: pd.Series(spile_city(x))
)
def classly_job(job_name):
    if pd.isna(job_name) or not isinstance(job_name,str):
        return "其他"
    job_name=job_name.lower()
    if '爬虫' in job_name or '采集' in job_name:
        return '爬虫/采集'
    elif '数据开发' in job_name or '大数据' in job_name or '数据工程' in job_name:
        return '数据开发'
    elif '后端' in job_name or '全栈' in job_name:
        return '后端/全栈'
    elif 'ai' in job_name or '智能体' in job_name or '大模型' in job_name:
        return 'AI/智能体'
    elif '测试' in job_name:
        return '测试'
    else:
        return '其他'
df["岗位划分"]=df["job_name"].apply(classly_job)
def news_graud(avg):
    if pd.isna(avg):
        return None
    if avg < 10000:
        return ("10k以下")
    elif avg<20000:
        return ("10k-20k")
    elif avg<30000:
        return ("20k-30k")
    elif avg<40000:
        return ("30k-40k")
    else:
        return ("40k以上")
df["薪资等级"]=df["平均薪资"].apply(news_graud)
df=df.drop_duplicates(subset=["job_name","job_company","job_city"],keep="first")
df=df[~((df["平均薪资"]>1000000)|(df["平均薪资"]<1000)|(df["平均薪资"].isna()))]
columns_to_keep = [
    'job_name', '岗位划分', '最低薪资', '最高薪资', '平均薪资',
    '薪资等级', '最低经验', '最高经验', 'job_edu', '学历要求',
    '城市', '区', '街道', 'job_company', '公司规模'
]
existing_columns = [col for col in columns_to_keep if col in df.columns]
df[columns_to_keep].to_csv('cleaned.csv', index=False, encoding='utf-8-sig')