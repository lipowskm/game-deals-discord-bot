from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, BigInteger
from sqlalchemy.orm import relationship

from database.base import Base


class Guild(Base):
    id = Column('id', Integer, primary_key=True)
    discord_id = Column('discord_id', BigInteger, unique=True)
    category = relationship('Category', uselist=False, back_populates='guild')
    channels = relationship('Channel')
    name = Column('name', String(length=100))
    auto = Column('auto', Boolean)
    time = Column('time', Integer)


class Category(Base):
    id = Column('id', Integer, primary_key=True)
    discord_id = Column('discord_id', BigInteger, unique=True)
    guild_id = Column(Integer, ForeignKey('guild.id'))
    guild_discord_id = Column(BigInteger, ForeignKey('guild.discord_id'))
    name = Column('name', String(length=100))
    guild = relationship("Guild", back_populates='category')
    channels = relationship('Channel')


class Channel(Base):
    id = Column('id', Integer, primary_key=True)
    discord_id = Column('discord_id', BigInteger, unique=True)
    guild_id = Column(Integer, ForeignKey('guild.id'))
    guild_discord_id = Column(BigInteger, ForeignKey('guild.discord_id'))
    category_id = Column(Integer, ForeignKey('category.id'))
    category_discord_id = Column(BigInteger, ForeignKey('category.discord_id'))
    name = Column('name', String(length=100))
    min_retail_price = Column(Integer)
    max_retail_price = Column(Integer)
    store = Column(String(length=20))
