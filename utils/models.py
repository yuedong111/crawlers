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
    url = Column(String(512), index=True)
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
    url = Column(String(128), index=True)
    content = Column(LONGTEXT)


class WaiMai(Base):
    __tablename__ = "meituanwaimai"
    id = Column(Integer, autoincrement=True, primary_key=True)
    shop = Column(String(200), index=True)
    openTime = Column(String(256))
    address = Column(String(512))
    about = Column(String(999))
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


class DZDianPingCQ(Base):
    __tablename__ = "dazhongdianping"
    id = Column(Integer, autoincrement=True, primary_key=True)
    shop = Column(String(200))
    address = Column(String(200))
    area = Column(String(20))
    score = Column(String(10))
    url = Column(String(128), index=True)
    phone = Column(String(66))
    openTime = Column(String(66))


class DZDianPing(Base):
    __tablename__ = "dianping"
    id = Column(Integer, autoincrement=True, primary_key=True)
    shop = Column(String(200))
    address = Column(String(200))
    area = Column(String(20))
    locate = Column(String(32))
    score = Column(String(10))
    url = Column(String(128), index=True)
    phone = Column(String(66))
    openTime = Column(String(66))
    cateUrl = Column(String(256))


class TuNiuAll(Base):
    __tablename__ = "tuniuquanguo"
    id = Column(Integer, autoincrement=True, primary_key=True)
    shop = Column(String(200))
    address = Column(String(200))
    city = Column(String(12))
    area = Column(String(128))
    phone = Column(String(66))
    district = Column(String(20))
    score = Column(String(10))
    url = Column(String(128), index=True)
    price = Column(String(10))
    decorateYear = Column(String(10))


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
    representative = Column(String(40))
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
    enterpriseName = Column(String(100), index=True)
    address = Column(String(256))
    primaryBusiness = Column(String(128))
    phone = Column(String(128))
    url = Column(String(80), index=True)
    establishedTime = Column(String(22))
    registeredFunds = Column(String(64))
    location = Column(String(36))
    category = Column(String(188))
    about = Column(LONGTEXT)


class BFZYCQ(Base):
    __tablename__ = "bafangziyuanchongqing"
    id = Column(Integer, autoincrement=True, primary_key=True)
    enterpriseName = Column(String(128), index=True)
    address = Column(String(228))
    area = Column(String(32))
    phone = Column(String(48))
    representative = Column(String(40))
    establishedTime = Column(String(22))
    url = Column(String(66), index=True)
    registeredFunds = Column(String(64))
    updateTime = Column(String(22))
    about = Column(LONGTEXT)
    others = Column(LONGTEXT)


class BFZY(Base):
    __tablename__ = "bafangziyuan"
    id = Column(Integer, autoincrement=True, primary_key=True)
    enterpriseName = Column(String(128), index=True)
    address = Column(String(228))
    area = Column(String(32))
    locate = Column(String(16))
    phone = Column(String(48))
    representative = Column(String(88))
    establishedTime = Column(String(22))
    url = Column(String(66), index=True)
    registeredFunds = Column(String(64))
    updateTime = Column(String(22))
    about = Column(LONGTEXT)
    others = Column(LONGTEXT)


class SouLeWang(Base):
    __tablename__ = "51sole"
    id = Column(Integer, autoincrement=True, primary_key=True)
    enterpriseName = Column(String(128), index=True)
    address = Column(String(228))
    phone = Column(String(128))
    representative = Column(String(40))
    contact = Column(String(30))
    products = Column(String(256))
    enterpriseType = Column(String(32))
    url = Column(String(66), index=True)
    industry = Column(String(66))
    postCodes = Column(String(10))
    category = Column(String(48))
    businessModel = Column(String(24))
    siteUrl = Column(String(88))
    location = Column(String(32))
    registerDate = Column(String(64))
    registeredFunds = Column(String(64))
    companyScale = Column(String(28))
    annualTurnover = Column(String(66))


class QYLu(Base):
    __tablename__ = "qiyelu"
    id = Column(Integer, autoincrement=True, primary_key=True)
    enterpriseName = Column(String(128), index=True)
    address = Column(String(228))
    location = Column(String(66))
    phone = Column(String(188))
    representative = Column(String(40))
    contact = Column(String(30))
    products = Column(String(256))
    enterpriseType = Column(String(32))
    url = Column(String(66), index=True)
    industry = Column(String(66))
    category = Column(String(48))
    businessModel = Column(String(24))
    markets = Column(String(88))
    about = Column(LONGTEXT)
    establishedTime = Column(String(64))
    registeredFunds = Column(String(64))
    companyScale = Column(String(66))
    others = Column(LONGTEXT)


class HuangYe(Base):
    __tablename__ = "huangye88"
    id = Column(Integer, autoincrement=True, primary_key=True)
    enterpriseName = Column(String(128), index=True)
    address = Column(String(228))
    postCodes = Column(String(12))
    phone = Column(String(188))
    representative = Column(String(40))
    contact = Column(String(30))
    registeredFunds = Column(String(64))
    location = Column(String(66))
    products = Column(String(256))
    enterpriseType = Column(String(32))
    url = Column(String(66), index=True)
    industry = Column(String(66))
    category = Column(String(48))
    businessModel = Column(String(24))
    status = Column(String(12))
    customers = Column(String(66))
    establishedTime = Column(String(64))
    businessScope = Column(String(666))
    about = Column(LONGTEXT)


class CnTrade(Base):
    __tablename__ = "cntrade"
    id = Column(Integer, autoincrement=True, primary_key=True)
    enterpriseName = Column(String(128), index=True)
    address = Column(String(228))
    postCodes = Column(String(12))
    phoneimg = Column(String(512))
    contact = Column(String(30))
    registerDate = Column(String(20))
    registeredFunds = Column(String(64))
    location = Column(String(66))
    companyScale = Column(String(66))
    url = Column(String(66), index=True)
    products = Column(String(256))
    enterpriseType = Column(String(32))
    siteUrl = Column(String(256))
    industry = Column(String(256))
    category = Column(String(48))
    businessModel = Column(String(24))
    businessScope = Column(String(666))
    about = Column(LONGTEXT)


class MetalInc(Base):
    __tablename__ = "metalinc"
    id = Column(Integer, autoincrement=True, primary_key=True)
    enterpriseName = Column(String(128), index=True)
    address = Column(String(228))
    contact = Column(String(30))
    phone = Column(String(188))
    registerDate = Column(String(20))
    registeredFunds = Column(String(64))
    location = Column(String(66))
    companyScale = Column(String(66))
    url = Column(String(66), index=True)
    products = Column(String(256))
    enterpriseType = Column(String(66))
    industry = Column(String(256))
    businessModel = Column(String(24))
    businessScope = Column(String(666))
    about = Column(LONGTEXT)


Base.metadata.create_all(mysql_client)
Base.metadata.create_all(mysql_client_remote)

