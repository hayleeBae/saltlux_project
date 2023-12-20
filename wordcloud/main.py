from sqlalchemy import create_engine, Column, Integer, String, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from collections import Counter
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import json

# MySQL 데이터베이스 설정
DATABASE_URL = "mysql+pymysql://user:password@localhost/dbname"
Base = declarative_base()

class GroupedTopNouns(Base):
    __tablename__ = "grouped_top_nouns"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    top_nouns_json = Column(String)

# 데이터베이스 연결 엔진 생성
engine = create_engine(DATABASE_URL)
Base.metadata.create_all(bind=engine)

# 데이터베이스 세션 생성
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# FastAPI 엔드포인트 - 홈 페이지
@app.get("/")
def read_home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

# FastAPI 엔드포인트 - 결과 페이지
@app.post("/result")
def show_result(request: Request, hospital_name: str = Form(...)):
    db = SessionLocal()
    
    # 데이터베이스에서 그룹화된 명사 데이터 가져오기
    db_data = db.query(GroupedTopNouns).filter(GroupedTopNouns.name == hospital_name).first()
    
    if not db_data:
        print(f"No data available for {hospital_name}")
        return templates.TemplateResponse("home.html", {"request": request, "message": f"No data available for {hospital_name}"})
    
    top_nouns = json.loads(db_data.top_nouns_json)
    
    # 워드클라우드 생성
    wc = WordCloud(background_color='white', font_path='./NanumBarunGothic.ttf')
    wc.generate_from_frequencies(top_nouns)
    
    # 결과 저장
    message = f"Results for {hospital_name}"
    
    # 워드클라우드 표시
    plt.figure(figsize=(10, 6))
    plt.imshow(wc, interpolation='bilinear')
    plt.axis("off")
    plt.title(f"Word Cloud for {hospital_name}")
    plt.show()
    
    return templates.TemplateResponse("home.html", {"request": request, "message": message})
