import factory
from faker import Factory as FakerFactory
from pytest_factoryboy import register

from src.resources.article.model import Article, SavedArticle
from src.resources.user.model import UserInfo

faker = FakerFactory.create()


@register
class UserInfoFactory(factory.Factory):
    class Meta:
        model = UserInfo

    id = factory.LazyAttribute(lambda x: str(faker.uuid4()))
    user_name = factory.LazyAttribute(faker.first_name)
    email_id = factory.LazyAttribute(faker.safe_email())


@register
class ArticleFactory(factory.Factory):
    class Meta:
        model = Article

    id = factory.LazyAttribute(lambda x: str(faker.uuid4()))
    user_id = factory.LazyAttribute(lambda o: o.user_info.id)
    article_link = factory.LazyAttribute(faker.text)
    image_link = factory.LazyAttribute(faker.text)
    category = factory.LazyAttribute(faker.text)
    website_name = factory.LazyAttribute(faker.text)


@register
class SavedArticleFactory(factory.Factory):
    class Meta:
        model = SavedArticle

    id = factory.LazyAttribute(lambda x: str(faker.uuid4()))
    user_id = factory.LazyAttribute(lambda o: o.user_info.id)
    article_id = factory.LazyAttribute(lambda o: o.article.id)
