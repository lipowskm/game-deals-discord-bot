from sqlalchemy import BigInteger, Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from database.base import Base


class Guild(Base):
    id = Column('id', Integer, primary_key=True)
    discord_id = Column('discord_id', BigInteger, unique=True)
    category = relationship('Category', uselist=False, back_populates='guild', cascade="all,delete")
    channels = relationship('Channel', cascade="all,delete")
    name = Column('name', String(length=100))
    auto = Column('auto', Boolean)
    time = Column('time', Integer)


class Category(Base):
    id = Column('id', Integer, primary_key=True)
    discord_id = Column('discord_id', BigInteger, unique=True)
    guild_id = Column(Integer, ForeignKey('guild.id', ondelete='CASCADE'))
    guild_discord_id = Column(BigInteger, ForeignKey('guild.discord_id', ondelete='CASCADE'))
    name = Column('name', String(length=100))
    guild = relationship("Guild", back_populates='category', cascade="all,delete")
    channels = relationship('Channel', cascade="all,delete")


class Channel(Base):
    id = Column('id', Integer, primary_key=True)
    discord_id = Column('discord_id', BigInteger, unique=True)
    guild_id = Column(Integer, ForeignKey('guild.id', ondelete='CASCADE'))
    guild_discord_id = Column(BigInteger, ForeignKey('guild.discord_id', ondelete='CASCADE'))
    category_id = Column(Integer, ForeignKey('category.id', ondelete='CASCADE'))
    category_discord_id = Column(BigInteger, ForeignKey('category.discord_id', ondelete='CASCADE'))
    name = Column('name', String(length=100))
    min_retail_price = Column(Integer)
    max_retail_price = Column(Integer)
    store = Column(String(length=20))
