# -*- coding: utf-8 -*-
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Text, Integer, DateTime, Boolean
from sqlalchemy import create_engine
from sqlalchemy.dialects.mysql import LONGTEXT
Base = declarative_base()
mysql_client = create_engine(
    "mysql+mysqlconnector://root:123456@127.0.0.1:3306/products?charset=utf8",
    encoding="utf-8",
)
mysql_client_remote = create_engine(
    "mysql+mysqlconnector://root:password@192.168.1.166:3306/crawls?charset=utf8",
    encoding="utf-8",
)

class JingDong(Base):
    __tablename__ = "jingdong"
    id = Column(Integer, autoincrement=True, primary_key=True)
    productName = Column(String(256), index=True)
    shop = Column(String(128), index=True)
    price = Column(String(128))
    commentTag = Column(String(256))
    popular = Column(String(64))
    rate = Column(String(16))
    image = Column(String(512))
    productUrl = Column(String(256))
    goodCommentCount = Column(String(16))
    poorCommentCount = Column(String(16))
    generalCommentCount = Column(String(16))
    totalCommentCount = Column(String(16))
    defaultGoodCommentCount = Column(String(16))
    vedioCommentCount = Column(String(16))
    afterCommentCount = Column(String(16))
    category = Column(String(20))


class MeiTuanShop(Base):
    __tablename__ = "meiTuanShop"
    id = Column(Integer, autoincrement=True, primary_key=True)
    shop = Column(String(128), index=True)
    phone = Column(String(66))
    address = Column(String(512))
    score = Column(String(32))
    url = Column(String(512))
    openTime = Column(String(226))


class EnterpriseCq(Base):
    __tablename__ = "enterprise"
    id = Column(Integer, autoincrement=True, primary_key=True)
    enterpriseName = Column(String(128), index=True)
    address = Column(String(528))
    socialCreditCode = Column(String(128))
    area = Column(String(64))
    registerDate = Column(String(32))
    businessScope = Column(String(1222))
    legalRepresentative = Column(String(64))
    registeredFunds = Column(String(64))
    enterpriseType = Column(String(128))


class GoverNews(Base):
    __tablename__ = "govermentnews"
    id = Column(Integer, autoincrement=True, primary_key=True)
    title = Column(String(888))
    publishDate = Column(String(24))
    about = Column(String(128))
    url = Column(String(128))
    content = Column(LONGTEXT)


class WaiMai(Base):
    __tablename__ = "meituanwaimai"
    id = Column(Integer, autoincrement=True, primary_key=True)
    shop = Column(String(200), index=True)
    openTime = Column(String(256))
    address = Column(String(512))
    about = Column(String(888))
    score = Column(String(32))
    url = Column(String(128), index=True)
    geoArea = Column(String(20))


class XieCheng(Base):
    __tablename__ = "xiechenghotel"
    id = Column(Integer, autoincrement=True, primary_key=True)
    hotelName = Column(String(200))
    address = Column(String(200))
    price = Column(String(12))
    score = Column(String(10))
    url = Column(String(128), index=True)


class DZDianPing(Base):
    __tablename__ = "dazhongdianping"
    id = Column(Integer, autoincrement=True, primary_key=True)
    shop = Column(String(200))
    address = Column(String(200))
    area = Column(String(20))
    score = Column(String(10))
    url = Column(String(128), index=True)
    phone = Column(String(66))
    openTime = Column(String(66))


class TuNiu(Base):
    __tablename__ = "tuniu"
    id = Column(Integer, autoincrement=True, primary_key=True)
    shop = Column(String(200))
    address = Column(String(200))
    area = Column(String(128))
    phone = Column(String(66))
    district = Column(String(20))
    score = Column(String(10))
    url = Column(String(128), index=True)
    price = Column(String(10))
    decorateYear = Column(String(10))


class ShunQi(Base):
    __tablename__ = "shunqi"
    id = Column(Integer, autoincrement=True, primary_key=True)
    enterpriseName = Column(String(128), index=True)
    address = Column(String(228))
    products = Column(String(528))
    area = Column(String(32))
    representative = Column(String(12))
    establishedTime = Column(String(22))
    url = Column(String(66), index=True)
    postCodes = Column(String(10))
    businessCode = Column(String(20))
    fax = Column(String(32))
    registeredFunds = Column(String(64))
    phone = Column(String(48))
    fixedPhone = Column(String(36))
    operateStatus = Column(String(20))
    about = Column(LONGTEXT)
    others = Column(LONGTEXT)


class WGQY(Base):
    __tablename__ = "wanguoqiye"
    id = Column(Integer, autoincrement=True, primary_key=True)
    enterpriseName = Column(String(64), index=True)
    primaryBusiness = Column(String(128))
    phone = Column(String(64))
    url = Column(String(48))
    establishedTime = Column(String(22))
    registeredFunds = Column(String(64))
    category = Column(String(128))
    about = Column(LONGTEXT)


Base.metadata.create_all(mysql_client)
Base.metadata.create_all(mysql_client_remote)
