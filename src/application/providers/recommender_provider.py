from src.domain.interfaces.recommender import IRecommender
from src.domain.services.recommender.item_based_cf_recommender import ItemBasedCFRecommender


def get_recommender() -> IRecommender:
    return ItemBasedCFRecommender()
